# Project and Engine update

**Goal:** Update TLA and Engine from their tracked upstream branches, preserve
all local work and owner settings, and validate the resulting integration.

## Baseline and scope

- Project master `ad0815441087c03fe4885e98b4713145d1bd11d6` already equals the
  freshly fetched `origin/master`; no project commits are incoming.
- Engine master `00c3c4cf5207ec7080179e4c9d455221ff1149d4` can fast-forward eight
  commits to `a015f258b6e4cfe1c35e53f5439d7d6bf438276d` (`2026.1.78-dev`).
- Both worktrees contain earlier local integration/optional-filter work. Exact
  patches, file copies and hashes are retained in `Workspace/update-20261028/`.
  Keep `Baking.FilterResources=False` and no TLA resource-root catalog.
- The root committed/index Engine pin remains `4588149fa4e4493ed6dddfea0a2fdf65d17c1f3e`.
  Initial implementation authority excluded stage/commit/push. The owner's later
  explicit commit request authorizes the local commit handoff below; push remains
  outside scope. Keep both branches on master; preserve Authoring.
- H initially had less than 1 GB free. Archive/verify permanent worker evidence and move
  task-owned generated readback copies off H before compilation, retaining byte
  manifests, original source, logs, snapshots and archive payloads.

## Steps

- [x] Inspect both repositories, fetch upstream and freeze the dirty baselines.
- [x] Preserve history/evidence and free sufficient space from owned outputs.
- [x] Preserve Engine local work in a named safety stash; fast-forward Engine;
  reconcile local native changes and source-owned/generated documentation.
- [x] Review all incoming behavior: movement compatibility `0.0.82`, runtime
  settings, 2D/model importer fixes, archive lookup, Unity/WinAPI build changes and
  additive map query. Adapt actual TLA consumers only where necessary.
- [x] Rebase the unpublished optional-filter version/migration record onto the
  published Engine tip, retaining all incoming notes and both new API symbols.
- [x] Configure; compile/bake matching resources; build all required roles and
  execute the sequential Verify All checks. Keep failures and reruns separate.
- [x] Verify affected runtime paths and final revisions, indexes and local
  settings; retain safety backups until all applicable checks are reconciled.

## Decisions and acceptance

Git integration and coupled metadata/version contracts remain coordinator-owned.
Routine remaining implementation may be delegated only after its source/fixture
and independent acceptance contracts are qualified; deterministic regeneration
and tiny conflict hunks remain local.

The project has no incoming history to merge. Engine changes must retain the
optional filter's default-off semantics, preserve runtime marker `0.0.82`, keep
both the upstream map API and local filter setting in the strict native inventory,
and regenerate projections from their owners. Preserve project config and asset
semantics. Distinguish Windows/AS/2D functional checks from other platforms,
performance, packaging and ordinary GUI acceptance.

## Actual verification

- Engine master fast-forwarded to `a015f258b6e4cfe1c35e53f5439d7d6bf438276d`;
  root master already current. Both indexes remain untouched. Named safety stash
  and exact dirty-source snapshots remain available.
- Retained 12,521 generated readback files (5,759,410,564 bytes) on C with full
  source/destination SHA-256 verification. Launcher archive and cleanup-root
  verification passed before the exact owned directory was removed from H.
- Local filter source restored/merged without index changes. Published ledger
  records and changelog entries are retained; unpublished notes now describe
  `2026.1.79-dev` based on published `78`, runtime `0.0.82`, Managed ABI `9`.
  Native API inventory contains 2,587 symbols (both additive APIs retained).
- Incoming resource-pack/rendering/model importer edits are Unity identifier
  collision fixes and comment changes, not new resource/image semantics. The
  movement send-clock fix and additive map query are covered by native tests.
  TLA's existing callers need no migration for these additions; Managed remains
  disabled and Unity remains opt-in/off. Runtime-owned settings extraction affects
  Engine example generators, not TLA's explicitly owned configuration.
- CMake auto configure passed. Aggregate contract diff against exact Engine HEAD
  passes across 17 domains: two changes, one reviewed disposition, none missing.
  Documentation preparation passed: 315 normative snippets, 185 external parser
  checks, 4,985 current translations, 28 AI retrieval tasks / 67 checks.
- Sequential `Verify :: All` and full documentation validation completed.
- WinAPI generator regressions exposed an upstream fixture defect on CRLF
  checkouts. Exact LF/CRLF source copies prove the same generator passes LF but
  receives malformed CR-CR-LF from the CRLF fixture's raw literal plus Replace.
  Normalize the shared header-fixture body to LF before explicit CRLF conversion;
  retain the generator's real LF and CRLF continuation checks and rerun both
  source-EOL controls. Original failure and controls remain under Workspace.
- WinAPI fixture correction passes the complete generator regressions from both
  LF and CRLF source copies. No generator-production behavior changed.
- Full bake automatically forced all packs after the baking configuration hash
  changed, finishing in 2m02s after compilation. All 18,703 files in 19 physical
  pack directories exactly match the identity-bound manifest. Default / False /
  True / incremental / restored-False resource-pipeline checks pass with real
  AngelScript bytecode, `.foinfo`, native archive readback and two negative controls.
- All required roles built without compiler/baker warnings. Focused Engine
  tests: 110 passed / 78 subtests; documentation validator,
  API-diff and contract-diff tests: 67 passed / 3 subtests. Final documentation
  preparation and 413-page validation pass after the CRLF fix/current notes.
- Ordinary Start Game server reaches `Start server complete` using Memory DB.
  A standalone Direct3D client registers a fresh synthetic character through the
  normal server path; normal movement reaches `(87,29)` from `(84,29)` on `repl1`.
  Inventory activation and native world/inventory frames were inspected, with
  correct visible world, character and stats; no QA setup used.
- Windows UI helper timed out on discovery twice and after its one kernel reset.
  No further Windows inputs were issued. Native bridge/API checks above remain
  separate from Windows UI qualification. Exact task-owned client/server PIDs
  were force-cleaned before the script harness; clean GUI shutdown is unverified.
  The initial private smoke event-reader defect (wrapper not unwrapped) and its
  corrected run are retained separately; it was not a product failure.
- `Verify :: All` exited 0 with its terminal `VERIFY_ALL_COMPLETE` marker: native
  tests 708 cases / 745,400 assertions; AngelScript harness COMPLETE 114 passed,
  zero failed/skipped; script-quality ratchet reports no new violations; all four
  nullable checks pass; Python Tools 156 passed / 82 subtests. Scripts/GUI (378
  inputs), main config and prototypes (1,755 inputs) formatting changed zero files.
- Final version and exact-HEAD aggregate-contract checks pass. Published EN/RU
  `78` and earlier changelog bodies are byte-equivalent after newline normalization.
  All 61 baseline project source files remain byte-identical; both branches remain
  master, both indexes are empty, and neither repository has unmerged paths.
  Engine HEAD equals fetched origin/master; the root committed/index gitlink remains
  unchanged and the working gitlink points at the updated Engine with local edits.
- Qualification is Windows x64 / independent translation units / AngelScript /
  2D Direct3D / Memory DB. No publication, commit, remote CI, other-platform build,
  Managed/3D runtime, Unity native build, performance, restart-persistence or clean
  ordinary GUI shutdown acceptance is claimed. Safety stash/source snapshots,
  original failures, corrected runs and retained output manifests are preserved.

## Authorized commit handoff

The owner subsequently requested committing the completed work. Commit the reviewed
Engine changes first as `2026.1.79-dev`, then commit TLA's integration, authored
resource migration, tests, documentation and the resulting Engine gitlink. Keep
both commits local and retain safety snapshots/stash. Existing native/runtime
results above qualify the tested source before commit; creating commits changes
revision identities, so existing binaries/bakes are not represented as rebuilt
against the new commit hashes. Recheck source preservation, version/contract
validation, staged diff and final gitlink/clean-worktree consistency.

Engine commit: `28c84c5d9d21f5a33b2122977314383842dfe414` (`2026.1.79-dev`),
31 reviewed files. Pre-commit version and aggregate-contract checks pass against
`a015f258b6e4cfe1c35e53f5439d7d6bf438276d`; documentation validation passes for
413 Markdown entries. Native source-layout/module checks pass. The TLA commit
records this exact Engine revision with the reviewed project changes and plans.
