#!/usr/bin/env python3
"""Extract a lossless quest answer index and chain summaries from dialogs.

Only the exact `[Dialog]` section of every `Dialogs/*.fodlg` is read (see
Docs/Dialogs.md); `[Text ...]`, `[Comment]` blocks and speech-level `Script`
commands are ignored. Full-line `//` comments and inline `#` preceded by
whitespace are stripped, matching the native helper; quotes do not escape
that `#` boundary. Command names are case-insensitive.

`quest_transitions.tsv` is an answer index, not an evaluated transition graph:
one row per (quest property, dialog, speech, answer) that touches a
`Group = Quests` property. `quest_demands`/`quest_results` keep every raw
Property payload for that property in source order; every other payload,
including other quest properties and `Or`/`NoRecheck` controls, stays in
`other_demands`/`other_results`. No `from`/`to` destination is inferred.

`quest_chains.tsv` aggregates the PipBoy city, dialogs and map-file families
(prefix before the first `_`) of their map bindings. The family is an
approximation only; it is not a city or runtime-reachability proof.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DIALOGS_DIR = PROJECT_ROOT / "Dialogs"
SCRIPTS_DIR = PROJECT_ROOT / "Scripts"
TEXTS_DIR = PROJECT_ROOT / "Texts"

SECTION_RE = re.compile(r"^\s*\[(?P<name>[^\]]+)\]\s*$")
COMMAND_RE = re.compile(r"^\s*(?P<command>Speech|Answer|Demand|Result)\b(?P<rest>.*)$", re.IGNORECASE)
PROP_RE = re.compile(
    r"^(?:NoRecheck\s+)?Property\s+(?:Player|Npc)\s+(?P<prop>\w+)\b", re.IGNORECASE
)
QUEST_DECL_RE = re.compile(
    r"^///@\s+Property\s+Critter\s+\w+\s+\S+\s+(?P<name>\w+)\b(?P<rest>.*)$"
)
GROUP_RE = re.compile(r"\bGroup\s*=\s*(?P<group>\w+)")
QNAME_RE = re.compile(r"^\{CritterProperty::(?P<prop>\w+)\}\{QName\}\{(?P<city>[^}]*)\}", re.MULTILINE)
DIALOG_ID_RE = re.compile(r"^\s*DialogId\s*=\s*(?P<name>\w+)\s*$", re.MULTILINE)


def strip_inline_comment(line: str) -> str:
    """Match IsDialogCommentOrEmpty and StripInlineDialogComment."""
    if line.lstrip().startswith("//"):
        return ""
    for index, char in enumerate(line):
        if char == "#" and (index == 0 or line[index - 1] in " \t\r\n\f\v"):
            return line[:index]
    return line


def quest_props() -> set[str]:
    props: set[str] = set()
    for path in sorted(SCRIPTS_DIR.glob("*.fos")):
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            match = QUEST_DECL_RE.match(line.strip())
            if not match:
                continue
            group = GROUP_RE.search(match.group("rest").split("//", 1)[0])
            if group and group.group("group") == "Quests":
                props.add(match.group("name"))
    return props


def parse_dialog(text: str) -> list[tuple[str, str, list[str], list[str]]]:
    """Return [(speech, answer_label, demand_payloads, result_payloads), ...]."""
    entries: list[tuple[str, str, list[str], list[str]]] = []
    current_speech = ""
    current_answer = ""
    in_dialog = False
    for raw_line in text.splitlines():
        line = strip_inline_comment(raw_line)
        stripped = line.strip()
        if not stripped:
            continue
        section = SECTION_RE.match(stripped)
        if section:
            in_dialog = section.group("name") == "Dialog"
            continue
        if not in_dialog:
            continue
        command = COMMAND_RE.match(line)
        if not command:
            continue
        name = command.group("command").lower()
        rest = command.group("rest").strip()
        if name == "speech":
            current_speech, current_answer = (rest.split() or [""])[0], ""
        elif name == "answer":
            current_answer = (rest.split() or [""])[0]
            entries.append((current_speech, current_answer, [], []))
        elif entries and current_answer and rest:
            entries[-1][2 if name == "demand" else 3].append(rest)
    return entries


def map_bindings_by_dialog() -> dict[str, set[str]]:
    bindings: dict[str, set[str]] = defaultdict(set)
    for path in sorted((PROJECT_ROOT / "Maps").glob("*.fomap")):
        for name in DIALOG_ID_RE.findall(path.read_text(encoding="utf-8-sig")):
            bindings[name].add(path.name)
    return bindings


def qname_cities() -> dict[str, str]:
    text = (TEXTS_DIR / "Quest.russ.fotxt").read_text(encoding="utf-8-sig")
    return {match.group("prop"): match.group("city") for match in QNAME_RE.finditer(text)}


def sort_key(entry: tuple[str, str, list[str], list[str]]) -> tuple[int, str]:
    speech = entry[0]
    return (int(speech) if speech.isdigit() else 10**6, speech)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()

    props = quest_props()
    cities = qname_cities()
    map_bindings = map_bindings_by_dialog()

    transition_rows = [[
        "property", "dialog", "speech", "answer", "quest_demands", "quest_results", "other_demands", "other_results"
    ]]
    usage: dict[str, set[str]] = defaultdict(set)

    for path in sorted(DIALOGS_DIR.glob("*.fodlg")):
        text = path.read_text(encoding="utf-8-sig")
        for speech, answer, demands, results in sorted(parse_dialog(text), key=sort_key):
            demand_items = []
            result_items = []
            for payload in demands:
                match = PROP_RE.match(payload)
                demand_items.append((match.group("prop") if match and match.group("prop") in props else None, payload))
            for payload in results:
                match = PROP_RE.match(payload)
                result_items.append((match.group("prop") if match and match.group("prop") in props else None, payload))
            touched = sorted({prop for prop, _ in demand_items + result_items if prop})
            if not touched:
                continue
            for prop in touched:
                usage[prop].add(path.stem)
                transition_rows.append([
                    prop, path.stem, speech, answer,
                    "; ".join(payload for owner, payload in demand_items if owner == prop) or "-",
                    "; ".join(payload for owner, payload in result_items if owner == prop) or "-",
                    "; ".join(payload for owner, payload in demand_items if owner != prop) or "-",
                    "; ".join(payload for owner, payload in result_items if owner != prop) or "-",
                ])

    chain_rows = [["property", "qname_city", "dialogs", "bound_map_families", "cross_location"]]
    for prop in sorted(usage):
        dialogs = sorted(usage[prop])
        families = sorted({
            name.split("_", 1)[0].removesuffix(".fomap")
            for dialog in dialogs for name in map_bindings.get(dialog, set())
        })
        chain_rows.append([
            prop, cities.get(prop, "?"), ",".join(dialogs), ",".join(families) or "-",
            "yes" if len(families) > 1 else "no",
        ])

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, rows in (("quest_transitions.tsv", transition_rows), ("quest_chains.tsv", chain_rows)):
        with (args.output_dir / filename).open("w", encoding="utf-8", newline="") as stream:
            csv.writer(stream, delimiter="\t", lineterminator="\n").writerows(rows)
    print(f"{len(transition_rows) - 1} transitions, {len(chain_rows) - 1} quest chains -> {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
