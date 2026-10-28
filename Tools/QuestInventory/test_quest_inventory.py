#!/usr/bin/env python3
"""Regression tests for the quest inventory and transition generators."""
from __future__ import annotations

import contextlib
import csv
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
INVENTORY_HEADER = "property\tquest_tag\tmax_tag\ttype\tdeclared_in\tqname_city\tdialogs_using\tscripts_using\tstate_texts_russ\thas_qname_qdesc\tbindings_of_user_dialogs\treachability".split("\t")
TRANSITION_HEADER = "property\tdialog\tspeech\tanswer\tquest_demands\tquest_results\tother_demands\tother_results".split("\t")
DECLARATIONS = """\
///@ Property Critter Common uint8 Complete Mutable Persistent Max = 5 Group = Quests Quest = 10
///@ Property Critter Common uint8 Unbound Mutable Persistent Quest = 11 Group = Quests
///@ Property Critter Common uint8 ScriptOnly Mutable Persistent Group = Quests Max = 7
///@ Property Critter Common uint8 PackDescOnly Mutable Persistent Group = Quests
///@ Property Critter Common uint8 PackEnglName Mutable Persistent Group = Quests
///@ Property Critter Common uint8 SomeQuest Mutable Persistent Group = Quests Quest = 13
///@ Property Critter Common uint8 CompleteCounter Mutable Persistent Group = Other Quest = 99
///@ Property Critter Common uint8 ControlQuest Mutable Persistent Group = Quests
"""
BOUND_DIALOG = """\
[Comment]
Demand Property Player Complete == 99
[Dialog]
Speech 1 # inline comment
  ANSWER 2
    demand Property Player Complete == 1
    Demand NoRecheck Property Player ControlQuest == 2
    Demand Or
    Demand NoRecheck Or
    RESULT Property Player Complete = 2
    result Property Npc Complete += 3
    Result Script Dialog::SetUniqTo "a#b//c"
  Answer 3 # trailing comment
    Demand Property Player SomeQuestCounter == 1
[Text russ]
Demand Property Player PackDescOnly == 99
"""
UNBOUND_DIALOG = """\
[Dialog]
Speech 2
  Answer 4
    Demand Property Player Unbound != 4
"""
RUSS_TEXTS = """\
{CritterProperty::Complete}{QName}{Арройо}
{CritterProperty::Complete}{QDesc}{Описание}
{CritterProperty::Complete}{0}{Шаг ноль}
{CritterProperty::Complete}{1}{Шаг один}
{CritterProperty::PackEnglName}{QName}{Англ}
{CritterProperty::PackEnglName}{QDesc}{Описание}
{CritterProperty::PackDescOnly}{QDesc}{Только описание}
"""
ENGL_TEXTS = """\
{CritterProperty::Complete}{QName}{Arroyo}
{CritterProperty::Complete}{QDesc}{Description}
{CritterProperty::Complete}{7}{Ignored}
{CritterProperty::PackDescOnly}{QDesc}{Description only}
{CritterProperty::PackEnglName}{QDesc}{Missing name}
"""
USER_SCRIPT = """\
// textual reference fixtures
int SomeQuestCounter;
#if 0
cc.DialogId = Content::Dialog::bound;
Content::Dialog::bound;
#endif
FooDialog::bound;
SomeQuestCounter;
Content::Dialog::boundExtra;
int ScriptOnly;
"""
def _load(stem: str):
    spec = importlib.util.spec_from_file_location(f"quest_test_{stem}", HERE / f"{stem}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

inventory = _load("build_quest_inventory")
transitions = _load("build_quest_transitions")

def run_main(module, argv: list[str]) -> int:
    with mock.patch.object(sys, "argv", ["tool", *argv]), contextlib.redirect_stdout(io.StringIO()):
        return module.main()

def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))

@contextlib.contextmanager
def fixture():
    with tempfile.TemporaryDirectory(prefix="quest-fixture-") as tmp:
        root = Path(tmp)
        for name in ("Scripts", "Dialogs", "Texts", "Maps"):
            (root / name).mkdir()
        files = {
            "Scripts/CritterProps.fos": DECLARATIONS,
            "Scripts/User.fos": USER_SCRIPT,
            "Dialogs/bound.fodlg": BOUND_DIALOG,
            "Dialogs/unbound.fodlg": UNBOUND_DIALOG,
            "Texts/Quest.russ.fotxt": RUSS_TEXTS,
            "Texts/Quest.engl.fotxt": ENGL_TEXTS,
            "Maps/town_map.fomap": "DialogId = bound\n",
        }
        for relative, content in files.items():
            (root / relative).write_text(content, encoding="utf-8", newline="\n")
        with mock.patch.multiple(
            inventory, PROJECT_ROOT=root, SCRIPTS_DIR=root / "Scripts",
            DIALOGS_DIR=root / "Dialogs", TEXTS_DIR=root / "Texts"
        ), mock.patch.multiple(
            transitions, PROJECT_ROOT=root, SCRIPTS_DIR=root / "Scripts",
            DIALOGS_DIR=root / "Dialogs", TEXTS_DIR=root / "Texts"
        ):
            yield root
        gone = root
    assert not gone.exists()

class TestQuestTools(unittest.TestCase):
    def test_transitions_real_cassidy_is_lossless_and_stable(self):
        with tempfile.TemporaryDirectory(prefix="quest-real-out-") as tmp:
            out = Path(tmp)
            run_main(transitions, ["--output-dir", str(out)])
            first = (out / "quest_transitions.tsv").read_bytes()
            run_main(transitions, ["--output-dir", str(out)])
            self.assertEqual(first, (out / "quest_transitions.tsv").read_bytes())
            self.assertTrue(first.endswith(b"\n") and not first.endswith(b"\n\n"))
            self.assertFalse(b"\r" in first or first.startswith(b"\xef\xbb\xbf"))
            rows = {(r["property"], r["dialog"], r["speech"], r["answer"]): r
                    for r in read_tsv(out / "quest_transitions.tsv")}
            range_row = rows[("ArroyoCassidyLetter", "arroyo_cassidy", "1", "20")]
            self.assertEqual(list(range_row), TRANSITION_HEADER)
            self.assertEqual(
                (range_row["quest_demands"], range_row["other_demands"]),
                ("Property Player ArroyoCassidyLetter >= 1; "
                 "Property Player ArroyoCassidyLetter <= 2",
                 "Property Player Intellect > 3; Script Dialog::IsNameMemPlayerNpc"),
            )
            joint = rows[("ArroyoCassidyLetter", "arroyo_cassidy", "20", "21")]
            self.assertEqual(
                (joint["quest_demands"], joint["quest_results"], joint["other_demands"]),
                ("Property Player ArroyoCassidyLetter == 2",
                 "Property Player ArroyoCassidyLetter = 3",
                 "Property Player VCCindyLetter == 2; Item Player letter_to_cassidy > 0"),
            )
            self.assertEqual(
                joint["other_results"],
                "Property Player VCCindyLetter = 3; Item Player letter_to_cassidy -= 1; "
                "Property Player Experience += 2000; Property Player Karma += 15; "
                "Script Dialog::SetUniqTo 44640; Item Player bottle_caps += 1500",
            )
            cindy = rows[("VCCindyLetter", "arroyo_cassidy", "20", "21")]
            self.assertEqual(
                (cindy["quest_demands"], cindy["other_demands"]),
                ("Property Player VCCindyLetter == 2",
                 "Property Player ArroyoCassidyLetter == 2; Item Player letter_to_cassidy > 0"),
            )

    def test_transitions_synthetic_keeps_controls_comments_and_text_out(self):
        with fixture(), tempfile.TemporaryDirectory(prefix="quest-synthetic-out-") as tmp:
            out = Path(tmp)
            run_main(transitions, ["--output-dir", str(out)])
            rows = {(r["property"], r["dialog"], r["speech"], r["answer"]): r
                    for r in read_tsv(out / "quest_transitions.tsv")}
            complete = rows[("Complete", "bound", "1", "2")]
            self.assertEqual(
                (complete["quest_demands"], complete["quest_results"]),
                ("Property Player Complete == 1",
                 "Property Player Complete = 2; Property Npc Complete += 3"),
            )
            self.assertEqual(
                (complete["other_demands"], complete["other_results"]),
                ("NoRecheck Property Player ControlQuest == 2; Or; NoRecheck Or",
                 'Script Dialog::SetUniqTo "a#b//c"'),
            )
            control = rows[("ControlQuest", "bound", "1", "2")]
            self.assertEqual(
                (control["quest_demands"], control["other_demands"]),
                ("NoRecheck Property Player ControlQuest == 2",
                 "Property Player Complete == 1; Or; NoRecheck Or"),
            )
            self.assertFalse({
                ("SomeQuest", "bound", "1", "3"), ("PackDescOnly", "bound", "1", "3"),
            } & set(rows))
            self.assertFalse({"from_demand", "to_state"} & set(complete))
            chains = {r["property"]: r for r in read_tsv(out / "quest_chains.tsv")}
            self.assertEqual(
                (chains["Complete"]["qname_city"], chains["Complete"]["bound_map_families"]),
                ("Арройо", "town"),
            )

    def test_inventory_group_tags_flags_evidence_and_classifications(self):
        with fixture():
            declarations = {row["property"]: row for row in inventory.quest_declarations()}
            expected = {"Complete": ("10", "5"), "ScriptOnly": ("", "7"), "Unbound": ("11", "")}
            for prop, tags in expected.items():
                self.assertEqual((declarations[prop]["quest_tag"], declarations[prop]["max_tag"]), tags)
            texts = inventory.quest_texts()
            self.assertEqual(
                [texts[p]["has_qname_qdesc"] for p in ("Complete", "PackDescOnly", "PackEnglName")],
                [True, False, False],
            )
            self.assertEqual((texts["Complete"]["qname"], texts["Complete"]["states"]), ("Арройо", 2))
            usage = inventory.dialog_usage()
            self.assertEqual(usage["SomeQuestCounter"], {"bound"})
            self.assertFalse({"bound"} & (usage.get("SomeQuest", set()) | usage.get("PackDescOnly", set())))
            self.assertEqual(
                inventory.dialog_bindings()["bound"],
                {"map:town_map.fomap", "runtime:User.fos:4", "script-ref:User.fos"},
            )
            scripts = inventory.script_usage(inventory.quest_declarations())
            self.assertEqual(("User.fos" in scripts["ScriptOnly"],
                              "User.fos" in scripts.get("SomeQuest", set())), (True, False))
            with tempfile.TemporaryDirectory(prefix="quest-inventory-out-") as tmp:
                output = Path(tmp) / "nested" / "quests.tsv"
                run_main(inventory, ["--output", str(output)])
                first = output.read_bytes()
                run_main(inventory, ["--output", str(output)])
                self.assertEqual(first, output.read_bytes())
                self.assertTrue(first.endswith(b"\n") and not first.endswith(b"\n\n"))
                self.assertFalse(b"\r" in first or first.startswith(b"\xef\xbb\xbf"))
                rows = {row["property"]: row for row in read_tsv(output)}
                complete = rows["Complete"]
                self.assertEqual(list(complete), INVENTORY_HEADER)
                self.assertEqual(
                    (complete["quest_tag"], complete["max_tag"], complete["type"],
                     complete["qname_city"], complete["state_texts_russ"],
                     complete["dialogs_using"], complete["scripts_using"]),
                    ("10", "5", "uint8", "Арройо", "2", "bound", "-"),
                )
                self.assertEqual(
                    (complete["has_qname_qdesc"], complete["bindings_of_user_dialogs"],
                     complete["reachability"]),
                    ("yes", "map:town_map.fomap;runtime:User.fos:4;script-ref:User.fos",
                     "bound-reference"),
                )
                for prop, reach in {"Unbound": "unbound", "ScriptOnly": "script-only",
                                    "SomeQuest": "no-dialog"}.items():
                    self.assertEqual(rows[prop]["reachability"], reach)
                self.assertEqual(rows["ScriptOnly"]["scripts_using"], "User.fos")
                self.assertEqual(
                    (rows["PackDescOnly"]["has_qname_qdesc"], rows["PackDescOnly"]["dialogs_using"],
                     rows["PackEnglName"]["has_qname_qdesc"],
                     rows["SomeQuest"]["dialogs_using"], rows["SomeQuest"]["scripts_using"]),
                    ("no", "-", "no", "-", "-"),
                )
                self.assertNotIn("CompleteCounter", rows)

    def test_native_inline_comment_boundary(self):
        text = (
            "[Dialog]\nSpeech 1\nAnswer 2 # discarded\n"
            "Demand Property Player Complete == 1 # discarded\n"
            "// Full-line comment\n"
            "Result Script Ns::Func http://host/tag#part\n"
            'Result Script Ns::Func "a # native strips here"\n'
        )
        self.assertEqual(transitions.parse_dialog(text), [(
            "1", "2", ["Property Player Complete == 1"],
            ["Script Ns::Func http://host/tag#part", 'Script Ns::Func "a'],
        )])

    def test_tsv_preserves_payload_tabs_and_quotes(self):
        with fixture() as root, tempfile.TemporaryDirectory(prefix="quest-tab-out-") as tmp:
            (root / "Dialogs/bound.fodlg").write_text(
                '[Dialog]\nSpeech 1\nAnswer 2\n'
                'Demand Property\tPlayer Complete >= 1\n'
                'Result Script Ns::Func "quoted"\n', encoding="utf-8")
            run_main(transitions, ["--output-dir", tmp])
            rows = read_tsv(Path(tmp) / "quest_transitions.tsv")
            self.assertEqual(len(rows), 2)
            row = next(row for row in rows if row["property"] == "Complete")
            self.assertEqual(row["quest_demands"], "Property\tPlayer Complete >= 1")
            self.assertEqual(row["other_results"], 'Script Ns::Func "quoted"')
            self.assertNotIn(None, row)

if __name__ == "__main__":
    unittest.main()
