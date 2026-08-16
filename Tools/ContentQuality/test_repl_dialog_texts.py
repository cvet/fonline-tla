from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DIALOG_ROOT = PROJECT_ROOT / "Dialogs"
SPEECH_RE = re.compile(r"^Speech\s+(.+?)(?:\s+#.*)?$")
ANSWER_RE = re.compile(r"^\s+Answer\s+(.+?)(?:\s+#.*)?$")
TEXT_RE = re.compile(r"^\{([^}]+)\}\{\}\{(.*)\}$", re.MULTILINE)


def dialog_text_references(source: str) -> set[str]:
    dialog = source.split("[Dialog]", 1)[1].split("[Text russ]", 1)[0]
    references: set[str] = set()
    speech: str | None = None

    for line in dialog.splitlines():
        speech_match = SPEECH_RE.match(line)
        if speech_match:
            speech = speech_match.group(1).strip()
            references.add(f"Speech {speech}")
            continue

        answer_match = ANSWER_RE.match(line)
        if answer_match and speech is not None:
            references.add(f"Speech {speech} Answer {answer_match.group(1).strip()}")

    # Speech 1 is the invisible pre-dialog node. Its answers are routing metadata and are intentionally
    # allowed to contain a whitespace placeholder in the legacy replication dialogs.
    return {key for key in references if key != "Speech 1" and not key.startswith("Speech 1 Answer ")}


def language_texts(source: str, language: str) -> dict[str, str]:
    block = source.split(f"[Text {language}]", 1)[1]
    if language == "russ":
        block = block.split("[Text engl]", 1)[0]
    return dict(TEXT_RE.findall(block))


class ReplicationDialogTextContractTests(unittest.TestCase):
    def test_reachable_replication_dialog_text_is_authored_in_both_languages(self) -> None:
        dialog_paths = sorted(DIALOG_ROOT.glob("repl_*.fodlg"))
        self.assertEqual(len(dialog_paths), 17)

        problems: list[str] = []
        for path in dialog_paths:
            source = path.read_text(encoding="utf-8-sig")
            references = dialog_text_references(source)
            for language in ("russ", "engl"):
                texts = language_texts(source, language)
                for key in sorted(references):
                    if key not in texts:
                        problems.append(f"{path.name}:{language}:{key}:missing")
                    elif not texts[key].strip():
                        problems.append(f"{path.name}:{language}:{key}:empty")

        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
