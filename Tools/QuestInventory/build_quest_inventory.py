#!/usr/bin/env python3
"""Build the quest registry TSV from authored sources.

A quest is a critter property declared with `Group = Quests` (see
Docs/Quests.md). The `Quest` and `Max` tags are independent and optional, in
either order. This tool cross-references every declaration with:

- dialogs that branch on the property (actual Demand/Result lines in `[Dialog]`);
- where those dialogs are referenced: map/critter instances (`DialogId = ...`),
  runtime assignments (`DialogId = Content::Dialog::...`) or other exact
  `Content::Dialog::NAME` textual references, excluding generated
  Scripts/Content.fos;
- top-level scripts referencing the property (excluding its declaring module);
- Quest text-pack coverage: numeric state entries plus `QName`/`QDesc` in both
  `Quest.russ.fotxt` and `Quest.engl.fotxt` (the city grouping shown in PipBoy).

Output: Tools/QuestInventory/quests_inventory.tsv (deterministic, LF).
Binding evidence is textual, not an AngelScript compiler or activation proof:
a reference in disabled code still appears. `bound-reference` therefore does
not prove runtime reachability.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import re
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "Scripts"
DIALOGS_DIR = PROJECT_ROOT / "Dialogs"
TEXTS_DIR = PROJECT_ROOT / "Texts"

DECL_RE = re.compile(
    r"^///@\s+Property\s+Critter\s+\w+\s+(?P<type>\S+)\s+(?P<name>\w+)\b(?P<rest>.*)$"
)
TAG_RE = re.compile(r"\b(?P<key>Group|Quest|Max)\s*=\s*(?P<value>[-\w]+)")
DIALOG_PROP_RE = re.compile(
    r"^(?:NoRecheck\s+)?Property\s+(?:Player|Npc)\s+(?P<prop>\w+)\b", re.IGNORECASE
)
DIALOG_ID_RE = re.compile(r"^\s*DialogId\s*=\s*(?P<name>\w+)\s*$", re.MULTILINE)
RUNTIME_DIALOG_RE = re.compile(r"\bDialogId\s*=\s*Content::Dialog::(?P<name>\w+)")
CONTENT_DIALOG_RE = re.compile(r"\bContent::Dialog::(?P<name>\w+)")
QUEST_TEXT_RE = re.compile(
    r"^\{CritterProperty::(?P<prop>\w+)\}\{(?P<key>[^}]*)\}\{(?P<value>[^}]*)\}", re.MULTILINE
)
# Identifier reference with ASCII-only boundaries: Cyrillic comment text around a
# name is not a word boundary, but still counts as a source reference.
SCRIPT_REF_RE = r"(?<![A-Za-z0-9_]){prop}(?![A-Za-z0-9_])"


def _load_parse_dialog():
    """Load the bounded sibling dialog parser without a circular import."""
    path = Path(__file__).with_name("build_quest_transitions.py")
    spec = importlib.util.spec_from_file_location("_quest_dialog_parser", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_dialog


parse_dialog = _load_parse_dialog()


def quest_declarations() -> list[dict[str, str]]:
    rows = []
    for path in sorted(SCRIPTS_DIR.glob("*.fos")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            match = DECL_RE.match(line.strip())
            if not match:
                continue
            tags = {
                tag.group("key"): tag.group("value")
                for tag in TAG_RE.finditer(match.group("rest").split("//", 1)[0])
            }
            if tags.get("Group") != "Quests":
                continue
            rows.append(
                {
                    "property": match.group("name"),
                    "quest_tag": tags.get("Quest", ""),
                    "max_tag": tags.get("Max", ""),
                    "type": match.group("type"),
                    "declared_in": f"{path.name}:{lineno}",
                }
            )
    unique = {row["property"]: row for row in rows}
    return [unique[key] for key in sorted(unique)]


def dialog_usage() -> dict[str, set[str]]:
    usage: dict[str, set[str]] = defaultdict(set)
    for path in sorted(DIALOGS_DIR.glob("*.fodlg")):
        for _speech, _answer, demands, results in parse_dialog(path.read_text(encoding="utf-8-sig")):
            for payload in demands + results:
                match = DIALOG_PROP_RE.match(payload)
                if match:
                    usage[match.group("prop")].add(path.stem)
    return usage


def dialog_bindings() -> dict[str, set[str]]:
    bindings: dict[str, set[str]] = defaultdict(set)
    for directory, suffix, prefix in (
        (PROJECT_ROOT / "Maps", "*.fomap", "map:"),
        (PROJECT_ROOT / "Critters", "*.focr", "proto:"),
    ):
        for path in sorted(directory.glob(suffix)):
            for name in DIALOG_ID_RE.findall(path.read_text(encoding="utf-8-sig")):
                bindings[name].add(f"{prefix}{path.name}")
    for path in sorted(SCRIPTS_DIR.glob("*.fos")):
        if path.name == "Content.fos":
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            runtime_names = set()
            for match in RUNTIME_DIALOG_RE.finditer(line):
                bindings[match.group("name")].add(f"runtime:{path.name}:{lineno}")
                runtime_names.add(match.start("name"))
            for match in CONTENT_DIALOG_RE.finditer(line):
                if match.start("name") not in runtime_names:
                    bindings[match.group("name")].add(f"script-ref:{path.name}")
    return bindings


def _empty_text_entry() -> dict[str, object]:
    return {"states": 0, "qname": "", "qname_langs": set(), "qdesc_langs": set(), "has_qname_qdesc": False}


def quest_texts() -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = defaultdict(_empty_text_entry)
    for language in ("russ", "engl"):
        text = (TEXTS_DIR / f"Quest.{language}.fotxt").read_text(encoding="utf-8-sig")
        for match in QUEST_TEXT_RE.finditer(text):
            prop, key = match.group("prop"), match.group("key")
            entry = result[prop]
            if key == "QName":
                entry["qname_langs"].add(language)
                if language == "russ" and not entry["qname"]:
                    entry["qname"] = match.group("value")
            elif key == "QDesc":
                entry["qdesc_langs"].add(language)
            elif key.isdigit() and language == "russ":
                entry["states"] = int(entry["states"]) + 1
    for entry in result.values():
        entry["has_qname_qdesc"] = (
            {"russ", "engl"} <= entry["qname_langs"] and {"russ", "engl"} <= entry["qdesc_langs"]
        )
    return result


def script_usage(declarations: list[dict[str, str]]) -> dict[str, set[str]]:
    wanted = {row["property"] for row in declarations}
    usage: dict[str, set[str]] = defaultdict(set)
    for path in sorted(SCRIPTS_DIR.glob("*.fos")):
        text = path.read_text(encoding="utf-8-sig")
        for prop in wanted:
            if re.search(SCRIPT_REF_RE.format(prop=re.escape(prop)), text):
                usage[prop].add(path.name)
    return usage


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path.resolve())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "quests_inventory.tsv")
    args = parser.parse_args()

    declarations = quest_declarations()
    dialogs = dialog_usage()
    bindings = dialog_bindings()
    texts = quest_texts()
    scripts = script_usage(declarations)

    header = [
        "property", "quest_tag", "max_tag", "type", "declared_in",
        "qname_city", "dialogs_using", "scripts_using",
        "state_texts_russ", "has_qname_qdesc", "bindings_of_user_dialogs", "reachability",
    ]
    lines = [header]
    for row in declarations:
        prop = row["property"]
        prop_dialogs = sorted(dialogs.get(prop, set()))
        decl_file = row["declared_in"].split(":")[0]
        prop_scripts = sorted(scripts.get(prop, set()) - {decl_file})
        ev = sorted({b for d in prop_dialogs for b in bindings.get(d, set())})
        entry = texts.get(prop, _empty_text_entry())
        if ev:
            reach = "bound-reference"
        elif prop_dialogs:
            reach = "unbound"
        elif prop_scripts:
            reach = "script-only"
        else:
            reach = "no-dialog"
        lines.append([
            prop, row["quest_tag"], row["max_tag"], row["type"], row["declared_in"],
            str(entry["qname"]),
            ",".join(prop_dialogs) if prop_dialogs else "-",
            ",".join(prop_scripts) if prop_scripts else "-",
            str(entry["states"]),
            "yes" if entry["has_qname_qdesc"] else "no",
            ";".join(ev) if ev else "none",
            reach,
        ])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        csv.writer(stream, delimiter="\t", lineterminator="\n").writerows(lines)
    reach_counts: dict[str, int] = defaultdict(int)
    for line in lines[1:]:
        reach_counts[line[-1]] += 1
    print(f"{len(declarations)} quest properties -> {_display_path(args.output)}")
    for key in sorted(reach_counts):
        print(f"  {key}: {reach_counts[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
