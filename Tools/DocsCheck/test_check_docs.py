from __future__ import annotations

import importlib.util
import io
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

CHECKER = Path(__file__).resolve().with_name("check_docs.py")
_spec = importlib.util.spec_from_file_location("check_docs_under_test", CHECKER)
assert _spec is not None and _spec.loader is not None
check_docs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_docs)


class DocsCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory(prefix="docscheck-test-")
        self.addCleanup(self._temp.cleanup)
        self.root = Path(self._temp.name)
        (self.root / "Docs").mkdir()
        (self.root / "README.md").write_text("# Root fixture\n", encoding="utf-8")
        (self.root / "Docs" / "Quests.md").write_text(
            "# Quests\n\n## Card format\n\n## Repeated\n\n## Repeated\n",
            encoding="utf-8",
        )
        self.review = self.root / "Docs" / "Review.md"

    def check(self, content: str) -> list[str]:
        self.review.write_text(content, encoding="utf-8")
        return check_docs.check_file(self.review, self.root)

    def test_valid_local_links_and_decoded_anchor(self) -> None:
        (self.root / "Docs" / "Guide Page.md").write_text(
            "# Guide\n\n## Café area\n", encoding="utf-8"
        )
        findings = self.check(
            "# Review\n\n"
            "[quests](Quests.md#card-format)\n"
            "[repeat](Quests.md#repeated-1)\n"
            "[guide](Guide%20Page.md#caf%C3%A9-area)\n"
            "[root](../README.md)\n"
            "[self](#review)\n\n"
            "## Use `API` here\n\n"
            "[code anchor](#use-api-here)\n"
        )
        self.assertEqual([], findings)

    def test_missing_file_and_missing_anchor(self) -> None:
        findings = self.check(
            "# Review\n\n[file](Missing.md)\n[anchor](Quests.md#counter-format)\n"
        )
        self.assertEqual(2, len(findings))
        joined = "\n".join(findings)
        self.assertIn("broken link Missing.md", joined)
        self.assertIn("anchor #counter-format not found in Quests.md", joined)

    def test_duplicate_heading_anchor_uses_suffix(self) -> None:
        findings = self.check("# Review\n\n[second](Quests.md#repeated-1)\n")
        self.assertEqual([], findings)

    def test_headings_inside_fences_are_not_anchors(self) -> None:
        (self.root / "Docs" / "Examples.md").write_text(
            "# Examples\n\n```markdown\n## Hidden heading\n```\n",
            encoding="utf-8",
        )
        findings = self.check(
            "# Review\n\n"
            "~~~text\n## Hidden heading\n~~~\n\n"
            "[target](Examples.md#hidden-heading)\n"
            "[same file](#hidden-heading)\n"
        )
        self.assertEqual(2, len(findings))
        joined = "\n".join(findings)
        self.assertIn("anchor #hidden-heading not found in Examples.md", joined)
        self.assertIn("broken same-file anchor #hidden-heading", joined)

    def test_tilde_fenced_link_is_ignored(self) -> None:
        findings = self.check(
            "# Review\n\n~~~text\n[gone](Missing.md)\n~~~\n"
        )
        self.assertEqual([], findings)

    def test_shorter_backtick_fence_does_not_close(self) -> None:
        findings = self.check(
            "# Review\n\n"
            "````markdown\n"
            "```text\n"
            "[gone](Missing.md)\n"
            "```\n"
            "````\n"
        )
        self.assertEqual([], findings)

    def test_unclosed_fence_is_reported(self) -> None:
        findings = self.check("# Review\n\n```text\n[gone](Missing.md)\n")
        self.assertEqual(1, len(findings))
        self.assertIn("unclosed fence", findings[0])

    def test_invalid_utf8_and_replacement_character(self) -> None:
        self.review.write_bytes(b"# Review\n\ntext \xff\n")
        findings = check_docs.check_file(self.review, self.root)
        self.assertEqual(1, len(findings))
        self.assertIn("not valid UTF-8", findings[0])

        findings = self.check("# Review\n\ntext \ufffd\n")
        self.assertEqual(1, len(findings))
        self.assertIn("replacement character", findings[0])

    def test_h1_count_and_heading_level_jump(self) -> None:
        findings = self.check("# One\n\n# Two\n\n### Deep\n")
        joined = "\n".join(findings)
        self.assertIn("expected exactly one H1, found 2", joined)
        self.assertIn("heading level jump 1 -> 3", joined)

    def test_git_discovery_includes_untracked_and_skips_ignored_and_deleted(self) -> None:
        repo = self.root / "repo"
        repo.mkdir()

        def git(*args: str) -> None:
            subprocess.run(
                ["git", *args],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

        git("init", "--quiet")
        (repo / "tracked.md").write_text("# Tracked\n", encoding="utf-8")
        (repo / "untracked.md").write_text("# New\n", encoding="utf-8")
        unicode_name = "\u0413\u0430\u0439\u0434.md"
        (repo / unicode_name).write_text("# Guide\n", encoding="utf-8")
        (repo / "ignored.md").write_text("# Ignored\n", encoding="utf-8")
        (repo / "deleted.md").write_text("# Deleted\n", encoding="utf-8")
        (repo / ".gitignore").write_text("ignored.md\n", encoding="utf-8")
        git("add", ".gitignore", "tracked.md", "deleted.md", unicode_name)
        (repo / "deleted.md").unlink()

        found = {
            path.relative_to(repo).as_posix()
            for path in check_docs.tracked_markdown(repo)
        }
        self.assertEqual({"tracked.md", "untracked.md", unicode_name}, found)

    def test_selftest_preserves_sentinel_and_cleans_temporary_files(self) -> None:
        sentinel = self.root / "Docs" / "DocsCheckSelftest.md"
        sentinel_bytes = b"owner sentinel\r\nkeep exactly\x00\n"
        sentinel.write_bytes(sentinel_bytes)
        (self.root / "Docs" / "Quests.md").write_text(
            "# Quests\n\nNo expected anchors live here.\n", encoding="utf-8"
        )
        before = {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }

        scratch = tempfile.TemporaryDirectory(prefix="docscheck-selftest-scratch-")
        self.addCleanup(scratch.cleanup)
        output = io.StringIO()
        with mock.patch.object(check_docs, "PROJECT_ROOT", self.root), mock.patch.object(
            tempfile, "tempdir", scratch.name
        ):
            with redirect_stdout(output):
                exit_code = check_docs.selftest()

        self.assertEqual(0, exit_code)
        self.assertIn("selftest: OK", output.getvalue())
        self.assertEqual(sentinel_bytes, sentinel.read_bytes())
        after = {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(before, after)
        self.assertEqual([], list(Path(scratch.name).iterdir()))


if __name__ == "__main__":
    unittest.main()
