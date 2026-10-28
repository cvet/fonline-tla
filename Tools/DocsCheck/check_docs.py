#!/usr/bin/env python3
"""Audit project Markdown: local inline links, anchors, UTF-8 and headings.

Checks every Markdown file known to git in this repository (tracked plus new
untracked, non-ignored files; the Engine submodule is a separate corpus). For
each file: strict UTF-8, no replacement characters, exactly one H1 (one-line
import wrappers are exempt), no heading-level jumps, and every local inline
link resolves to an existing file with an existing GitHub-style anchor.
Headings and links inside backtick or tilde fenced code blocks are ignored; an
unclosed fence is reported. This is an inline-link/ATX-heading subset, not a
full Markdown renderer. Exit code 0 = clean, 1 = findings. `--selftest` runs
detector fixtures in an isolated temporary directory.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import unquote

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Minimal one-line instruction import wrappers intentionally have no H1.
H1_EXEMPT = {"CLAUDE.md", ".github/copilot-instructions.md"}

FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
FENCE_CLOSE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*$", re.MULTILINE)
LINK_RE = re.compile(
    r"\[[^\]]*\]\(\s*(<[^>\n]+>|[^)\s]+)(?:\s+(?:\"[^\"\n]*\"|'[^'\n]*'))?\s*\)"
)
INLINE_CODE_RE = re.compile(r"(`+)(.+?)\1")


def tracked_markdown(root: Path) -> list[Path]:
    # Tracked files plus new (untracked, non-ignored) Markdown so that freshly
    # authored docs are audited before they are committed. A tracked path that
    # no longer exists in the working tree (a staged deletion) is skipped.
    out = subprocess.run(
        ["git", "ls-files", "-z", "--others", "--exclude-standard", "--cached", "*.md"],
        cwd=root,
        capture_output=True,
        check=True,
    )
    paths = {root / name for name in out.stdout.decode("utf-8").split("\0") if name}
    return sorted(path for path in paths if path.is_file())


def scan_markdown(text: str) -> tuple[list[tuple[int, str]], str, Optional[int]]:
    """Return headings, prose with fences blanked, and unclosed-fence line."""
    headings: list[tuple[int, str]] = []
    prose: list[str] = []
    fence: Optional[tuple[str, int]] = None
    opened_at: Optional[int] = None
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    for number, line in enumerate(normalized.split("\n"), 1):
        if fence is not None:
            close = FENCE_CLOSE_RE.match(line)
            if close and close.group(1)[0] == fence[0] and len(close.group(1)) >= fence[1]:
                fence = None
            prose.append("")
            continue
        opening = FENCE_OPEN_RE.match(line)
        info = opening.group(2) if opening else ""
        if opening and not (opening.group(1)[0] == "`" and "`" in info):
            fence = (opening.group(1)[0], len(opening.group(1)))
            opened_at = number
            prose.append("")
            continue
        prose.append(line)
        heading = HEADING_RE.match(line)
        if heading:
            headings.append((len(heading.group(1)), heading.group(2)))
    return headings, "\n".join(prose), opened_at if fence is not None else None


def github_anchor(heading: str) -> str:
    plain = INLINE_CODE_RE.sub(r"\2", heading)
    lowered = plain.strip().lower()
    cleaned = re.sub(r"[^\w\s-]", "", lowered, flags=re.UNICODE)
    return re.sub(r"\s", "-", cleaned)


def heading_anchors(headings: list[tuple[int, str]]) -> set[str]:
    used: set[str] = set()
    for _, body in headings:
        base = github_anchor(body)
        anchor = base
        suffix = 1
        while anchor in used:
            anchor = f"{base}-{suffix}"
            suffix += 1
        used.add(anchor)
    return used


def file_anchors(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    headings, _, _ = scan_markdown(text)
    return heading_anchors(headings)


def check_file(path: Path, root: Path) -> list[str]:
    findings: list[str] = []
    rel = path.relative_to(root).as_posix()
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [f"{rel}: not valid UTF-8 ({exc})"]
    if "\ufffd" in text:
        findings.append(f"{rel}: replacement character present")

    headings, prose, unclosed = scan_markdown(text)
    if unclosed is not None:
        findings.append(f"{rel}: unclosed fence opened at line {unclosed}")
    h1_count = sum(1 for level, _ in headings if level == 1)
    if rel not in H1_EXEMPT and h1_count != 1:
        findings.append(f"{rel}: expected exactly one H1, found {h1_count}")
    previous = 1
    for level, _ in headings:
        if level > previous + 1:
            findings.append(f"{rel}: heading level jump {previous} -> {level}")
        previous = level

    anchors = heading_anchors(headings)
    for target in LINK_RE.findall(prose):
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        target_path, separator, raw_fragment = target.partition("#")
        target_path = unquote(target_path)
        fragment = unquote(raw_fragment) if separator else ""
        if not target_path:
            if fragment and fragment not in anchors:
                findings.append(f"{rel}: broken same-file anchor #{fragment}")
            continue
        resolved = (path.parent / target_path).resolve()
        if not resolved.exists():
            findings.append(f"{rel}: broken link {target}")
            continue
        if fragment and resolved.is_file() and resolved.suffix.lower() == ".md":
            if fragment not in file_anchors(resolved):
                findings.append(f"{rel}: anchor #{fragment} not found in {target_path}")
    return findings


def selftest() -> int:
    failures = 0
    quests = (
        "# Quests\n\n## Card format\n\n## Repeated\n\n## Repeated\n\n"
        "~~~markdown\n## Hidden example\n~~~\n"
    )
    cases = {
        "clean document": (
            "# Fixture\n\nSee [Quests](Quests.md#card-format), "
            "[repeated](Quests.md#repeated-1), and [root](../README.md).\n\n"
            "## Use `API` here\n\n[code anchor](#use-api-here)\n",
            [],
        ),
        "broken file link": ("# Fixture\n\n[x](Missing.md)\n", ["broken link"]),
        "broken target anchor": (
            "# Fixture\n\n[x](Quests.md#no-such-anchor)\n",
            ["anchor #no-such-anchor not found"],
        ),
        "broken same-file anchor": (
            "# Fixture\n\n[x](#no-such-heading)\n",
            ["broken same-file anchor"],
        ),
        "fenced target heading": (
            "# Fixture\n\n[x](Quests.md#hidden-example)\n",
            ["anchor #hidden-example not found"],
        ),
        "heading jump": ("# Fixture\n\n### Jump\n", ["heading level jump"]),
        "tilde fence": ("# Fixture\n\n~~~text\n[x](Missing.md)\n~~~\n", []),
        "unclosed fence": (
            "# Fixture\n\n```text\n[x](Missing.md)\n",
            ["unclosed fence"],
        ),
    }
    with tempfile.TemporaryDirectory(prefix="docscheck-selftest-") as tmp:
        root = Path(tmp)
        (root / "Docs").mkdir()
        (root / "README.md").write_text("# Fixture root\n", encoding="utf-8")
        (root / "Docs" / "Quests.md").write_text(quests, encoding="utf-8")
        fixture = root / "Docs" / "Selftest.md"
        for name, (content, expected) in cases.items():
            fixture.write_text(content, encoding="utf-8")
            findings = check_file(fixture, root)
            for needle in expected:
                if not any(needle in finding for finding in findings):
                    print(f"selftest MISS [{name}]: expected '{needle}' in {findings}")
                    failures += 1
            for finding in findings:
                if not any(needle in finding for needle in expected):
                    print(f"selftest EXTRA [{name}]: {finding}")
                    failures += 1
        fixture.write_bytes(b"# Bad\xff\xfeUTF8\n")
        findings = check_file(fixture, root)
        if not any("not valid UTF-8" in finding for finding in findings):
            print("selftest MISS [utf8]: invalid UTF-8 not flagged")
            failures += 1
    print("selftest:", "OK" if failures == 0 else f"{failures} failure(s)")
    return 0 if failures == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true", help="verify the detector on fixtures")
    args = parser.parse_args()
    if args.selftest:
        return selftest()

    files = tracked_markdown(PROJECT_ROOT)
    findings: list[str] = []
    for path in files:
        findings.extend(check_file(path, PROJECT_ROOT))
    for finding in findings:
        print(finding)
    print(f"checked {len(files)} Markdown files: {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
