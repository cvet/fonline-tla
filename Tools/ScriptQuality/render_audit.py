#!/usr/bin/env python3
"""Ingest module-audit workflow output into a durable per-module store and
render markdown tickets + a consolidated summary.

The script refactoring audit runs as background sub-agent workflows that
return JSON (per-module bugs / quality issues / refactor plans, with
adversarial bug verifications). Those results live only in temporary task
output files. This tool persists each module's result under
`Build/_audit/json/<group>.json` (the source of truth) and regenerates
`Build/_audit/<group>.md` tickets and `Build/_audit/_SUMMARY.md` from the
full accumulated store, so audit batches add up across runs.

`Build/` is build/output state (not committed), so the audit store is
local working state, regenerable at any time.

Usage:
  python Tools/ScriptQuality/render_audit.py <workflow_output.json> [more.json ...]
  python Tools/ScriptQuality/render_audit.py            # just regenerate from store
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "Build" / "_audit"
JSON_DIR = AUDIT_DIR / "json"

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "not-a-bug": 4}


def load_modules(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "result" in data:
        data = data["result"]
    if isinstance(data, dict):
        return data.get("modules", [])
    return []


def ingest(paths: list[Path]) -> int:
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    n = 0
    for p in paths:
        for m in load_modules(p):
            group = m.get("group") or (m.get("analysis", {}) or {}).get("group")
            if not group:
                continue
            (JSON_DIR / f"{group}.json").write_text(
                json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
            n += 1
    return n


def verdict_for(bug: dict, verifications: list[dict]) -> dict | None:
    for v in verifications:
        vb = v.get("bug", {})
        if vb.get("title") == bug.get("title") and vb.get("file") == bug.get("file"):
            return v.get("verdict")
    return None


def short(text: str, n: int = 500) -> str:
    text = (text or "").strip().replace("\n", " ")
    return text if len(text) <= n else text[:n] + " …"


def render_module_md(m: dict) -> str:
    analysis = m.get("analysis", m)
    group = m.get("group") or analysis.get("group", "?")
    verifs = m.get("verifications", [])
    out = [f"# Audit: {group}", ""]

    files = analysis.get("files", [])
    if files:
        out += ["## Files", "", "| file | sides | quality | effort | lf-30 |", "| --- | --- | --- | --- | --- |"]
        for f in files:
            name = f.get("file", "").split("/")[-1]
            out.append(f"| {name} | {f.get('sides','')} | {f.get('qualityScore','')} | {f.get('effort','')} | {'yes' if f.get('hasLfCounterpart') else ''} |")
            out.append("")  # purpose line below
        out += [""]
        out += ["### Purpose", ""]
        for f in files:
            out.append(f"- **{f.get('file','').split('/')[-1]}** — {f.get('purpose','')}")
        out += [""]

    bugs = sorted(analysis.get("bugs", []), key=lambda b: SEV_ORDER.get(b.get("severity"), 9))
    if bugs:
        out += ["## Bugs", ""]
        for b in bugs:
            v = verdict_for(b, verifs)
            tag = b.get("severity", "?")
            if v is not None:
                if v.get("isReal"):
                    tag = f"{tag} → VERIFIED {v.get('correctedSeverity', '')} ({v.get('confidence','')})"
                else:
                    tag = f"{tag} → REFUTED ({v.get('correctedSeverity','not-a-bug')})"
            loc = b.get("file", "").split("/")[-1]
            line = b.get("line", "")
            out.append(f"### [{tag}] {b.get('title','')}  — `{loc}:{line}`")
            out.append("")
            out.append(short(b.get("detail", ""), 900))
            if b.get("suspectedIntent"):
                out.append(f"- **Intent:** {short(b['suspectedIntent'], 400)}")
            if b.get("fixSketch"):
                out.append(f"- **Fix:** {short(b['fixSketch'], 500)}")
            if v is not None:
                out.append(f"- **Verdict:** {short(v.get('reasoning',''), 700)}")
            out.append("")

    qi = analysis.get("qualityIssues", [])
    if qi:
        out += ["## Quality issues", ""]
        for q in qi:
            loc = (q.get("file", "") or "").split("/")[-1]
            out.append(f"- **[{q.get('category','')}]** {('`'+loc+'` ') if loc else ''}{short(q.get('detail',''),400)}")
            out.append(f"  - → {short(q.get('recommendation',''),300)}")
        out += [""]

    rp = analysis.get("refactorPlan", [])
    if rp:
        out += ["## Refactor plan", ""]
        for i, step in enumerate(rp, 1):
            out.append(f"{i}. {step}")
        out += [""]

    risks = analysis.get("risks", [])
    if risks:
        out += ["## Risks", ""]
        for r in risks:
            out.append(f"- {r}")
        out += [""]
    return "\n".join(out) + "\n"


def regenerate() -> None:
    modules = []
    for jf in sorted(JSON_DIR.glob("*.json")):
        modules.append(json.loads(jf.read_text(encoding="utf-8")))
        (AUDIT_DIR / f"{jf.stem}.md").write_text(render_module_md(modules[-1]), encoding="utf-8")

    # Consolidated summary
    lines = ["# Audit Summary", "", f"Modules audited: {len(modules)}", ""]
    # Per-group table
    lines += ["| group | files | bugs | verified-real | refuted |", "| --- | --- | --- | --- | --- |"]
    grand_real = []
    for m in modules:
        a = m.get("analysis", m)
        group = m.get("group") or a.get("group", "?")
        verifs = m.get("verifications", [])
        bugs = a.get("bugs", [])
        real = refuted = 0
        for b in bugs:
            v = verdict_for(b, verifs)
            if v is None:
                continue
            if v.get("isReal"):
                real += 1
                grand_real.append((group, b, v))
            else:
                refuted += 1
        lines.append(f"| {group} | {len(a.get('files',[]))} | {len(bugs)} | {real} | {refuted} |")
    lines += [""]

    lines += ["## Verified real bugs (by severity)", ""]
    grand_real.sort(key=lambda t: SEV_ORDER.get((t[2].get("correctedSeverity") or t[1].get("severity")), 9))
    for group, b, v in grand_real:
        sev = v.get("correctedSeverity") or b.get("severity")
        loc = b.get("file", "").split("/")[-1]
        lines.append(f"- **{sev}** [{group}] `{loc}:{b.get('line','')}` — {b.get('title','')}")
    lines += [""]

    (AUDIT_DIR / "_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def console_summary() -> None:
    modules = [json.loads(jf.read_text(encoding="utf-8")) for jf in sorted(JSON_DIR.glob("*.json"))]
    print(f"Audit store: {len(modules)} module(s) in {JSON_DIR.relative_to(ROOT)}")
    print(f"{'group':22s} {'files':>5s} {'bugs':>5s} {'real':>5s} {'refut':>6s} {'qual':>5s}")
    print("-" * 56)
    for m in modules:
        a = m.get("analysis", m)
        group = m.get("group") or a.get("group", "?")
        verifs = m.get("verifications", [])
        bugs = a.get("bugs", [])
        real = sum(1 for b in bugs if (verdict_for(b, verifs) or {}).get("isReal"))
        refuted = sum(1 for b in bugs if (verdict_for(b, verifs) and not verdict_for(b, verifs).get("isReal")))
        print(f"{group:22s} {len(a.get('files',[])):5d} {len(bugs):5d} {real:5d} {refuted:6d} {len(a.get('qualityIssues',[])):5d}")


def main() -> int:
    paths = [Path(p) for p in sys.argv[1:]]
    if paths:
        n = ingest(paths)
        print(f"Ingested {n} module result(s)")
    regenerate()
    console_summary()
    print(f"\nWrote tickets + _SUMMARY.md to {AUDIT_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
