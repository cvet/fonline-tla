# Project documentation audit — 2026-10-24

Project-only refresh in `H:/fonline-tla-2`; Engine source/instructions were read
as dependencies and left unchanged. Baseline project HEAD:
`952f5d6b23db3e05ce274d27348061d3f00db6d3`; committed Engine pin and Engine HEAD:
`57424cb5d2ac132b1fa8ba83e353d07cb6ca75e0`. Both trees started clean on `master`.
No staging, commit, push, branch movement or publication is part of this task.

## Coverage and method

The original inventory contains **22 tracked project Markdown files**, including
root/tool/hidden instruction files. Final coverage includes all **31** current
project documents, including eight new owner/reference/history pages and this
report. Engine Markdown and generated/ignored build/package/cache trees are
outside this project's corpus. Linked Engine targets were checked for existence
and modeled anchors, not re-audited as an Engine documentation project.

Read current task/CMake/workflow/config owners, generator/config, harness,
script-quality and nullable validators, relevant scripts/native declarations,
and the neighboring `H:/lf-22` instruction/maintenance structure. Reused its
bounded readability scanner. TLA retains AS, its language rules and source owners;
LF's Managed C# gameplay, four-edition localization, Authoring/Ops and tracker
procedures were not imported as TLA policy.

Private evidence is in ignored `Workspace/instruction-audit-20261024/`:
`docs-before.json`, `before/`, `docs-final.json`, `readability-before.json`,
`readability-final.json`, `links-before.json`, `links-final.json`,
`agents-preservation.json`, `extraction-ledger.json`, `session-inventory.json`,
`session-coverage.json` and `log-finding-context.json`. Raw private session text
is not copied into maintained docs. These artifacts describe this workstation;
they are not required to execute the maintained project workflow later.

## Corrections against current owners

| Prior contradiction/staleness | Current result and evidence owner |
| --- | --- |
| README, Nullability and ScriptStyle prescribed removed Sync/Async | [Scripts](../Scripts.md#single-threaded-logic-and-lifetime); `TLA.fomain` has SingleThreadedLogic=True, scripts no longer own that Sync module. Old recipes remain explicitly historical. |
| Refactoring demanded English comments while AGENTS/ScriptStyle required Russian | Current language agrees; ScriptStyle retains Russian, native/general docs English. |
| ScriptStyle claimed no script harness | Existing `Scripts/Testing.fos` and `Scripts/Tests/`, exact launch/filter/COMPLETE rules in [BuildAndLaunch](../BuildAndLaunch.md#local-runtime-and-tests). |
| “One trailing blank line” contradicted the actual script validator | Exactly one EOL terminator, no extra blank line; C++ keeps Engine's own convention. |
| Generated GUI path and old Engine core directories drifted | `InterfaceEditor.cfg` selects `Scripts/Generated`; both metadata/script packs explicitly include project `Scripts/Core/`. |
| Generated GUI fixes alternated between mandatory regeneration and no hand edits | [ContentWorkflow](../ContentWorkflow.md#gui-generation) retains the narrow paired-source/output exception and original regeneration conditions. |
| SourceExt/ContentMigration and a project ACM decoder were described as current | [NativeExtensions](../NativeExtensions.md) follows actual AddEngineSources; ACM is the selected optional Engine importer. A stale config comment is explicitly identified, without changing runtime configuration. |
| Old native assert spellings and loose pointer/noexcept advice | Current Engine checklist is required explicitly; project guide explains actual binding and cleanup boundaries. |
| Nullability said script-to-script runtime null enforcement was absent | Current Engine compiler/interpreter has `asBC_RefCpyChk`; the project now links the reusable contract. |
| Verify/CI were described as identical; building tests implied running them | Exact local chain vs current CI jobs are separated. CI lacks the script harness; native execution and terminal script evidence are explicit. |
| LocalTest was called empty and “persistent server” could imply persistent storage | LocalTest sets LoginTimeout=0; default Memory retains data within one process only. Restart tests require isolated persistent storage. |
| Campaign proposal mixed planned files/jobs with implemented guarantees | [ReanimationPlan](../ReanimationPlan.md) names missing catalog/batch/SOAK infrastructure and routes to the complete old proposal. No campaign acceptance is invented. |
| Frozen test counts, protocol version and setting-consumer line links looked current | Counts are dated; no fixed protocol number in current guidance. Historical settings evidence locations are code, not misleading live line links. |
| Unavailable memory reference and XML tool residue in ScriptStyle | Replaced by explicit repository rules; closing tool tags removed. |

## AGENTS preservation and extraction

The private ledger retains **165 original blocks** (including headings, examples
and table rows), concrete owner destinations and **37 exception/example controls**.
Codex compared applicable requirements, conditions and exceptions with the owner
text; automated text/link checks are supporting evidence, not semantic proof.
Obsolete descriptions were deliberately corrected against source, rather than
silently dropped or copied into a second conflicting guide.

| Original AGENTS subject | Owner of retained detail |
| --- | --- |
| Project layout, backend, sides, state, module lifecycle and globals | [Scripts](../Scripts.md), [Systems](../Systems.md), [ScriptStyle](../ScriptStyle.md) |
| Stacking, sounds, day tint, options and their regression routes | [Scripts adapters](../Scripts.md#project-adapters-that-must-not-be-bypassed) |
| Nullable locals/casts/components/Chosen and handler parity | [Nullability](../Nullability.md) |
| Build/task chain, startup, logs, CI and warnings | [BuildAndLaunch](../BuildAndLaunch.md) |
| Engine update integration and old/new revision comparison | [DocumentationMaintenance](../DocumentationMaintenance.md#engine-submodule-updates) |
| Native source roles, annotations, pointers, invariants, profiling and EOF | [NativeExtensions](../NativeExtensions.md), explicit Engine reading route |
| Authored inputs, packs, generated outputs, GUI code keys and paired fixes | [ContentWorkflow](../ContentWorkflow.md) |
| Localization, secure channel and secret/pin issuance | [ContentWorkflow configuration](../ContentWorkflow.md#configuration-and-secure-channel) |
| Formatter/quality validator modes and current check scope | [ScriptStyle](../ScriptStyle.md), [ScriptQuality](../../Tools/ScriptQuality/README.md), [NullableEstimate](../../Tools/NullableEstimate/README.md) |
| Authority, language, preservation and final report | [AGENTS](../../AGENTS.md), [DocumentationMaintenance](../DocumentationMaintenance.md) |

The full earlier campaign body is preserved with only relative-link rebasing,
title replacement and EOF normalization. AI protocol, historical runs/fixes and
old roadmap bodies are retained with recorded extraction checks; original entry
anchors route to their new owners. Current references do not require reading the
entire historical record at startup.

## Local session evidence

Parsed **1,000 local JSONL files / 98,480 records**, with **zero parse errors**:
six Codex files (root VS Code sessions plus one child) and 994 Claude files
(one project conversation plus workflow/subagent/journal records). The current
audit session was excluded from historical findings. VS Code workspace mappings
were inventoried; `H:/fonline-tla` has the same repository remote and supplied
older project evidence. No local Claude conversation for `fonline-tla-2` was
found, so that absence was not replaced by a claim of fresh Claude testing.

Human corrections were distinguished from instruction snapshots, continuation
summaries, worker prompts, notifications and duplicate deliveries; search hits
were reviewed with surrounding assistant exchanges. This is a **local project
history** audit, not a remote-machine or fleet-wide log audit. Remote VS Code
workspace metadata does not establish access to remote session contents.

Sanitized findings (record numbers identify private source evidence):

| Evidence | Clarified working rule |
| --- | --- |
| Claude `3225b340-6376-4531-bf95-74331ada8e2f`, records 14466/14511; Codex `01a16924-3d54-7e01-9c2c-0ca670361085`:1087 | Engine-only branch instructions must not move project commits; keep requested source branches instead of generic review branch churn. |
| Codex `01a16a1c-c4c9-7811-97ba-3410adef1776`:902 | Ordinary Engine update keeps the owner's master branch, rather than leaving detached HEAD. |
| Codex `01a130b5-c3a6-77c3-980f-627303354c6a`:2903/5422/9327/13962 | Match adjacent naming/member order and semantic blank-line grouping. The later withdrawn spelling correction is not generalized into a universal abbreviation rule. |
| Same Codex session:4154 | Inspect throwing cleanup calls before noexcept; a passing review/build does not prove exception safety. |
| Claude conversation:5064/6073 | Reject disputed cosmetic restructuring; demonstrate the responsibility/bug and add a regression that distinguishes the old wrong behavior. |
| Claude conversation:7506/8350/11394 | Preserve the chosen single-threaded AS architecture; do not reintroduce removed Sync/Async or infer C# adoption from Engine capability. |
| Claude conversation:17768/20050; current GUI/animation owners | Player-visible rendering/input needs ordinary visible interaction after migrations. Startup/harness/static bridge discovery alone cannot qualify it. |
| Codex `01a130b5-c3a6-77c3-980f-627303354c6a`:27529/28100 | User changes to index/Engine revision during verification must be preserved; re-anchor evidence to the final revision. |
| Claude conversation:2872/3032 | Explain findings and examples plainly in Russian while preserving the repository's source/document language conventions. |

These are durable conclusions from the examined evidence, not a frequency estimate
or permission to repeat historical commits, migrations or publication actions.

## Quality inventory

Follow-up: the owner selected `Docs/Plans/` for maintained project plans.
Five plans were relocated, their relative links and the index were rebased,
and the instruction rule now takes precedence over generic workflow defaults.
The table below reflects the current paths and metrics; original audit evidence
and the relocation verification remain in ignored task artifacts.

Raw UTF-8 byte counts below describe before/final files. Approximate word counts
exclude modeled code spans/blocks; they are not model tokens. All current guides
fit the review thresholds in [DocumentationMaintenance](../DocumentationMaintenance.md#scope-size-and-readability-checks).
Large historical records/reference tables have explicit role exceptions and
section routes; their complete evidence is retained rather than truncated to an
arbitrary startup budget.

| Document | Before bytes | Final bytes | Approx. words | Disposition |
| --- | ---: | ---: | ---: | --- |
| `.github/copilot-instructions.md` | 59 | 59 | 6 | Minimal pointer; H1 exemption |
| `AGENTS.md` | 24434 | 9037 | 1067 | Startup entry; detail moved to owners |
| `CLAUDE.md` | 12 | 12 | 2 | Minimal import; H1 exemption |
| `Docs/AiControl.md` | 61128 | 22728 | 2160 | Current launch/MCP/playtest guide; protocol and history extracted |
| `Docs/AiControlProtocol.md` | new | 18379 | 1732 | Protocol/command reference; complete body, prose wrapped |
| `Docs/Animation.md` | 2686 | 2686 | 292 | Focused reference; unchanged |
| `Docs/AuditPlan.md` | 16311 | 16599 | 2149 | Dated queue; snapshot boundary clarified |
| `Docs/BuildAndLaunch.md` | new | 10544 | 1123 | Canonical tasks, validation, runtime, CI and packages |
| `Docs/ContentWorkflow.md` | new | 5919 | 638 | Canonical inputs, GUI generation, localization/config |
| `Docs/DocumentationMaintenance.md` | new | 10168 | 1343 | Ownership, quality, discovery, log audit, Engine integration |
| `Docs/EngineSettingsAudit.md` | 54385 | 42204 | 1763 | Historical table; justified size exception and group routes |
| `Docs/History/AiControl-2026.md` | new | 24384 | 2607 | Dated runs/fixes/roadmap; size exception if above trigger |
| `Docs/History/ReanimationPlan-2026.md` | new | 70123 | 7504 | Complete old proposal; justified historical size exception |
| `Docs/History/Refactoring-2026.md` | 101463 | 103396 | 12764 | Complete journal; justified historical size exception and section map |
| `Docs/NativeExtensions.md` | new | 5167 | 532 | Current CMake/source owners and Engine native reading route |
| `Docs/README.md` | 3772 | 4420 | 433 | Complete docs map; no embedded subsystem reference bodies |
| `Docs/ReanimationPlan.md` | 69132 | 7462 | 882 | Current proposal entry; existing vs planned tools explicit |
| `Docs/Refactoring.md` | 13895 | 14512 | 1718 | Dated rounds/decisions; language/H1/authority corrected |
| `Docs/ScriptStyle.md` | 19504 | 20314 | 1147 | Coherent Russian style guide; current harness, EOF and sync policy |
| `Docs/Scripts.md` | new | 8322 | 920 | Canonical AS state/side/dispatch/adapters |
| `Docs/Systems.md` | 8452 | 8819 | 899 | Routing map; counts labeled as snapshot, source paths corrected |
| `Docs/Plans/2026-10-14-project-owned-engine-policy.md` | 13728 | 14089 | 1682 | Historical assignment; scope/authorization notice and prose wrapping |
| `Docs/Plans/2026-10-16-engine-settings-audit.md` | 5722 | 6091 | 770 | Historical assignment; scope/authorization notice and prose wrapping |
| `Docs/Plans/2026-10-20-resource-manager.md` | 6586 | 6953 | 870 | Historical assignment; scope/authorization notice and prose wrapping |
| `Docs/Plans/2026-10-21-engine-update-publication.md` | 7718 | 8077 | 1047 | Historical assignment; scope/authorization notice and prose wrapping |
| `Docs/Plans/2026-10-22-sprite-frame-offsets.md` | 1952 | 2307 | 302 | Historical assignment; scope/authorization notice and prose wrapping |
| `Nullability.md` | 15115 | 6967 | 727 | Current TLA boundary/validators; obsolete Sync/runtime claims corrected |
| `README.md` | 29966 | 8438 | 808 | Human entry; duplicate catalogs removed |
| `Tools/NullableEstimate/README.md` | 1595 | 1593 | 146 | Focused tool guide; explicit Python 3 and wrapped prose |
| `Tools/ScriptQuality/README.md` | 3464 | 3464 | 272 | Focused validator/ratchet guide; unchanged |
| `Docs/History/DocumentationAudit-2026-10-24.md` | new | final manifest | final manifest | This dated audit; included in final scan |

## Verification and limits

- Full final manifest checked for UTF-8, one H1 (except the two minimal wrappers),
  heading-level jumps, open fences, long ordinary prose lines/paragraphs and
  role-based size exceptions. No unresolved structural findings remain.
- Baseline link inventory found **11 errors**. Final modeled local links/anchors
  have **zero errors**; external URLs are classified without claiming remote
  availability. The bounded scanners' parser limitations are retained in JSON.
- Link-helper tests and independent wrong-state controls cover exact corpus,
  Unicode/duplicate/explicit anchors, missing paths/headings, code exclusion,
  line bounds, escape rejection and UTF-8 CLI. Final test suite: **21 passed**.
- Clause/exception controls and full-body extraction checks pass. Exact task,
  config, generator, validator and harness claims were checked against source.
- `git diff --check`, final status/index and root/Engine revision checks are the
  final repository gates. No native build, bake, GUI, performance or platform
  qualification was run for this documentation-only change.

Fresh-session instruction loading remains a separate client check: file sizes,
valid links and a guide read in this session do not prove that every future
Codex/Claude profile will load or follow the same instruction chain. Historical
Engine-settings consumer claims and campaign-wide completion remain historical
or unverified, as labeled in their owning pages.
