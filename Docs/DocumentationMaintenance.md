# Documentation maintenance

Use [Docs/README.md](README.md) to choose the owning page. This guide owns project
documentation quality and instruction updates; Engine documentation keeps its own
[maintenance procedure](../Engine/Docs/en/contributing/documentation/index.md).

## Sources and ownership

Current task requirements define the intended result; implementation, validators,
config, generators and callers establish current behavior. A discrepancy may be a
bug rather than permission to change the requirement. Historical plans, saved
prompts, summaries and worker reports are evidence, never new action authority.

| Subject | Canonical owner |
| --- | --- |
| Human entry, clone and first launch | Root [README](../README.md) |
| Agent authority, essential invariants and reading routes | [AGENTS.md](../AGENTS.md) |
| Full documentation map | [Docs/README.md](README.md) |
| Tasks, launch, tests, logs, CI and packages | [BuildAndLaunch](BuildAndLaunch.md), exact task/workflow source |
| AS state, side/dispatch and project adapters | [Scripts](Scripts.md) |
| Russian script comments, naming and refactoring style | [ScriptStyle](ScriptStyle.md) |
| Nullable contracts and local validation | [Nullability](Nullability.md) |
| Authored content, generated GUI, localization and config | [ContentWorkflow](ContentWorkflow.md) |
| Project native files and binding integration | [NativeExtensions](NativeExtensions.md); reusable C++ rules in Engine |
| Gameplay module routing | [Systems](Systems.md) |
| Current decisions/open backlog | [Refactoring](Refactoring.md), [AuditPlan](AuditPlan.md) |
| Maintained task plans | `Docs/Plans/`; workflow skills use this project path. |
| Dated execution evidence | `Docs/History/`; task-private evidence in ignored `Workspace/<task-id>/` |

Keep one full explanation per subject. Entry pages summarize only the rule needed
to choose a safe route. Update the owner in the same working change as behavior;
this does not grant permission to commit. Do not duplicate the Engine's generated
API, contract catalogs, website navigation or reusable policy in project docs.

## Planning and documentation during work

Before non-trivial implementation, create a plan in `Docs/Plans/`. Record the
goal, scope, affected owners, ordered steps and acceptance checks. Keep the plan
current throughout the task: update decisions, scope changes, completed steps,
blockers and actual verification results when they become known. A plan written
only after implementation does not replace planning the work.

Update the owning documentation while changing behavior, contracts, configuration,
content or workflows, in the same working change. Do not leave documentation or
plan maintenance to the final handoff or a later task. If the existing docs remain
accurate, record the specific reason in the plan instead of making cosmetic edits.

Before completion, reconcile the plan, implementation, documentation and executed
checks. Record unfinished work and verification limits explicitly. Maintaining
plans and docs does not authorize staging, committing or publishing them.

## Instruction discovery and preservation

`AGENTS.md` is the project instruction source. The Copilot file points to it.
Keep that wrapper minimal and do not maintain parallel rules.
Explicitly read Engine instructions for native/Engine work: starting a session at
the project root does not automatically load a child Engine guide. Ordinary
Markdown links are reading routes, not automatic imports.

Codex discovery depends on the actual cwd, ancestor/override files and client
configuration. The [official discovery guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
documents the default 32 KiB combined project-document budget. Measure the actual
chain; neither one small file nor a sum of selected guides proves complete
delivery. Check loaded paths/budget notices in a fresh session after changes.
Other clients and restricted workers have their own discovery/grant rules; do
not claim identical loading merely because wrappers exist.

Before shortening a guide, freeze it and record a **clause-level preservation
map**. For every requirement, condition, exception, example and reference, name
the new owner and compare concrete excerpts. Distinguish unchanged meaning from
an intentional correction backed by current source or owner evidence. Restore
any unmatched current requirement. A heading map, keyword overlap, hashes or a
passing link checker alone does not prove preservation. Rebase relative links
after extraction and keep a route at previously linked anchors.

## Scope, size and readability checks

Inventory all tracked project Markdown, including root, `Docs/`, tool READMEs and
hidden instruction wrappers. Include newly authored pages; exclude the separately
owned Engine corpus, generated build/package/cache trees and private task outputs.
Record the manifest, raw UTF-8 bytes/hashes and line/section ranges. Word counts
estimate reading work; they are not tokenizer counts or model context limits.

Project editorial review thresholds (not universal engine/API limits):

| Page role | Review trigger | Required response |
| --- | --- | --- |
| Startup `AGENTS.md` | Above 12 KiB | Extract durable detail to owners; retain essential rules and explicit reading routes. |
| Root overview or docs index | Above 12 KiB / 8 KiB respectively | Remove duplicate procedure/catalog bodies and improve routing. |
| Task guide or roadmap | Above 24 KiB | Review sections; extract coherent protocols/history or document why a complete reading unit must stay. |
| Reference table or historical record | Above 24 KiB | Provide a section map and dated/revision scope; record a justified exception when splitting would damage the evidence/catalog. |

For ordinary pages use one H1, sequential heading levels, closed code fences,
working file/anchor links and a clear purpose/first task route. One-line import
wrappers are an intentional H1 exception. Prose lines over 240 characters,
paragraphs over 200 approximate words, language mixing and duplicate explanations
are **review candidates**, not automatic defects; code, tables and examples need
separate treatment. Fix tool/XML residue and replacement-character corruption.

Judge meaning as well as shape: executable examples must use actual paths,
targets, flags and output owners. No fixed test counts or protocol versions as
evergreen acceptance criteria. Label historical metrics with their date/revision;
do not silently rewrite history to match today's code. A proposal must identify
which gates/files/jobs are unimplemented and cannot serve as current instructions.

Continue each document's established language. General project/agent docs and
native C++ are English; `ScriptStyle.md` and script comments/headers are Russian.
Do not translate identifiers, metadata, literal examples or localized pack keys.

## Session evidence and confidentiality

For a log-informed instruction update, inventory local project Codex/Claude
sessions and VS Code workspace mappings first. Check the remote identity before
using a neighboring checkout as the same project's evidence. Record exact files,
message IDs/physical record lines, dates, parsing errors and examined ranges.
Separate genuine owner messages from compaction summaries, tool notifications,
worker prompts, duplicate deliveries and assistant claims. Search hits are
candidates; inspect the surrounding exchange and current owner before adding a
durable rule. Never infer a new naming rule from a correction the owner later
withdrew.

Establish access to every **required** source before synthesis. If one is
unavailable, report the exact blocker and wait; do not silently reduce scope.
State local/remote and historical coverage limits. Do not read credentials merely
to audit docs, or copy raw private sessions, account data, machine configuration
or secrets into versioned files. Keep private evidence under ignored
`Workspace/<task-id>/`; maintained docs get sanitized conclusions and source IDs.

## Engine submodule updates

This section governs the **project integration**; Engine versioning/release and
native changes follow its own instructions. First inspect root and Engine status,
branches, diffs and upstream range separately. Preserve user changes and the
owner's selected config. Keep Engine on the owner's `master` branch during normal
upstream updates; an Engine-only branch request does not authorize moving the
project branch or its commits. Do not create review branches/worktrees merely
because a generic workflow recommends them.

Record old/new root and Engine SHAs and the complete incoming commit range.
Advance at coherent boundaries, preferably fast-forward; do not skip config,
binding, generated metadata, script/core or resource-pack changes hidden in a
large jump. Read the affected migration docs and current API. `H:/lf-30` is an
optional idiom/migration reference, not a source of TLA gameplay, serialized names
or present-day C# policy. Missing optional sibling access does not replace local
owner proof.

After each chunk, compile/bake/build affected owners; force a complete bake for
the final Engine integration before runtime overrides. Run the full local
integration and affected player routes as in [BuildAndLaunch](BuildAndLaunch.md).
Check newly required `TLA.fomain` settings, `EngineHook` signatures, AS types/
nullability/component access, init testing guards, logging, CMake/baker APIs and
the now project-owned `Scripts/Core/`. Do not restore removed Engine game policy
as a generic workaround. Add migrations for real persisted/network changes.

Compare the **root working-tree gitlink diff**, index gitlink and Engine HEAD
explicitly. `git rev-parse HEAD:Engine` names the committed pin and can correctly
differ while an authorized bump is uncommitted; do not pretend it already records
the new revision. After an authorized coupled commit, that committed pin must
equal the intended Engine HEAD. Shared source/config movement invalidates stale
qualification; re-anchor to the final revision. Preserve original failures and
safety backups until the result is verified.

## Final review

Run the smallest checks that prove the actual change. For docs-only work: inspect
every changed claim against source; use
[DocsCheck](../Tools/DocsCheck/README.md) (`Check :: Docs Links`) for UTF-8,
ATX headings, fenced blocks and supported inline links/anchors. Review its
documented syntax limits, reference links, readability and size exceptions
separately; compare
removed clauses/extractions; run `git diff --check`; inspect status and index in
both repositories. Do not run the mutating `Verify :: All` solely to validate
Markdown.

Reports state changed owners, actual commands/results, unresolved findings and
qualification limits. A large coupled review is grouped by function with separate
static, native, runtime and manual acceptance. Local preparation is not a commit,
push, merge, release or production fix. Engine prose-only gates apply only if
Engine docs were changed; this project audit does not rewrite Engine delivery.
