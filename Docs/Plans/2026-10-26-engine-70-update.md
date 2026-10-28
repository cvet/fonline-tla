# Engine 2026.1.70 integration plan

The resource-root catalog approach recorded below was superseded by the owner's
request to disable package filtering by default and in TLA. Current changes and
verification are tracked in [optional resource filtering](2026-10-26-optional-resource-filter.md).
Historical validation below retains its original scope and results.

**Goal:** Support current Engine master in TLA with matching assets, metadata and
binaries, preserving gameplay and owner-selected settings.

**Architecture:** Review all nine incoming commits, resolve TLA compatibility at
the owning source, migrate authored FOFRM inputs, and verify the real project.
Codex owns contracts, native integration, review and runtime verification. A
bounded DeepSeek assignment will migrate the homogeneous authored image corpus
after its semantics and independent checks are qualified.

**Tech stack:** CMake, C++, AngelScript, FOFRM, Python 3, Windows x64.

**Spec:** The owner's maintenance request, [integration procedure](../DocumentationMaintenance.md#engine-submodule-updates),
[build procedure](../BuildAndLaunch.md), and Engine's incoming changelog migrations.

## Constraints and review focus

- Initial project: `ad0815441`; initial Engine and committed/index gitlink:
  `4588149fa4e4493ed6dddfea0a2fdf65d17c1f3e` (`2026.1.62-dev`).
- Target: `4dc5c55f59240f45e0e2d9f9f2564261b3ffa471` (`2026.1.70-dev`).
- Both worktrees and indexes initially clean; retain both `master` branches.
- Preserve AngelScript, single-threaded logic, storage and transport settings.
- No staging, commits, pushes, publication or deployment.
- Private evidence: `Workspace/engine-70-20261026/`.
- Preserve FOFRM frame order, offsets and effective legacy timing; consumed image
  dependencies must remain reachable through their public wrapper resources.
- Check typed time consumers, native hooks, prototype identifiers, RPC completion,
  resource root declarations and source/archive overlay behavior.
- Full bake must precede consumers; normal GUI shutdown and original failures
  remain separate from cleanup, reruns and performance qualification.

## Tasks and acceptance

- [x] Inspect root/Engine state; fetch upstream and read the complete incoming
      commit list and migration notes (nine commits, 2026.1.63 through 70).
- [x] Fast-forward Engine master; inspect changed owners and all TLA consumers.
- [x] Qualify old/new FOFRM semantics and independent wrong-state controls;
      delegate and review the complete 51-file loose authored migration.
- [x] Adapt any additional verified API/resource consumers and update owning docs.
- [ ] Configure, force bake, then run every current `Verify :: All` leaf command;
      retain command exits, terminal test counts and diagnostics.
- [ ] Run ordinary visible client/server login, movement and affected resource
      interactions, then close normally and verify exit/cleanup.
- [ ] Review final diff/settings/indices, reconcile all gitlinks, update results
      and report remaining qualification limits.

## Execution decisions and results

The authorized update stays in this checkout. Project-specific instructions
override generic skill suggestions for extra worktrees, commits and plan approval.
No project consumer of the renamed sprite-duration or typed moving-context/fog
interval APIs was found in the initial focused search; final build checks remain
required. The loose authored resource corpus contains 51 legacy FOFRM descriptors.

Engine advanced to the exact target. The first native baker build exposed removed
`BakingContext` fields in `SourceExt/DialogBaker.cpp`; it now uses `CheckOutput`
and the owning accessors. `CheckOutput` must run even without an incremental
checker, because it also registers outputs for resource usage and reports.

The 51-file delegated migration passed the independent complete-corpus semantic
comparison and frozen BOM/EOL/terminal-newline checks without corrections. Native
bake/runtime acceptance remains in progress. The first full bake rejected five
missing explicit settings. TLA now declares `Common.NonInteractive=False` and the
four upstream RPC watchdog/admission defaults. Existing setting values are intact.
The first direct PowerShell launch split an unquoted dotted single-dash option;
the repeat passes quoted arguments and confirms `Force rebuild all resources`.

Resource selection will retain explicit dynamic families through a project-owned
`FixedType` resource array: complete Fallout/project art and editor catalogs,
fonts, all sound/music/video, mapper assets, and opaque common/server data.
Map/prototype resource fields remain the native collector's responsibility.
This deliberately conservative catalog preserves dynamically addressed content;
narrowing it for package-size optimization is outside this maintenance task.

The final forced bake passed on Engine 70 with the new settings, migrated images
and resource roots. All 12 root catalogs (17,194 entries) match the frozen complete
native output inventory. The official packaging manifest loader accepts the
matching markers; every explicit entry is selected in its source pack and every
selected output exists. The real negative control was the preceding successful
bake: `CommonData/CritterTypes.json` was absent from its selection and is present
after declaring the roots. No source guessing or export-all fallback was added
to Engine. TLA's explicit catalog preserves its previous resource availability.
Owning guidance is updated in `ContentWorkflow.md` and `NativeExtensions.md`.

The original full native execution exposed two upstream `Test_BakerSetup.cpp`
fixtures that invoke `ProtoBaker` without AngelScript bytecode. The exception is
`Resource pack must contain exactly one script bytecode file for this engine side`.
The production project bake has its script pack and passes. A narrow local Engine
test correction now prepares real empty server bytecode with the existing
`AngelScriptBaker` before those two prototype bakes, guarded by the backend flag.
No production native behavior, public contract or compatibility marker changes.
The original full run completed with 703/705 cases and 745272/745274 assertions;
exit 42 records exactly those two fixture failures. The first correction used an
empty AS namespace, which the real compiler correctly rejected as an empty module;
that intermediate failure is retained. A nonexecuted stub gives it valid bytecode.
The focused resource-usage run then passed all four cases / 26 assertions, exit 0,
with no compiler warnings. The complete native rerun remains required. Engine
remains at the fetched master commit with this uncommitted
test-only correction; no Engine master commit/version increment is being made.

The final verification resumes at leaf 9 after rebuilding UnitTests. Leaves 1-7
from the first chain are reused: their production sources/configuration/resources
are unchanged by the test-only correction. Leaf 8 is replaced by the fresh unit
build. Native tests and leaves 10-19 execute again/on the final source as applicable.
This avoids another unrelated full resource bake for a native fixture change.

The consumed-image reference search found one direct reference, the invisible
blocker's `art/items/blank.png`. The actual full-bake output is current sprite v3
and byte-identical to `blank.fofrm`, so its valid resource name is preserved.

The corrected full native run passed 705 cases / 745285 assertions, exit 0.
The first script harness then failed before test execution: `Main.GenerateWorld`
used `PackSynchronizedTime(2246, ...)` to initialize the clock, while `MapTime`
interprets the value as elapsed real milliseconds from `WorldTime.StartYear` and
multiplies it by 20. The newly checked time constructor exposed that pre-existing
overflow. Fresh-world initialization now computes the calendar delta from the
configured epoch and divides it by the multiplier before constructing `synctime`.
The authored initial date (2246-10-30 01:00), epoch (2040-10-30) and multiplier (20)
retain their intended values. Existing persisted clocks are not rewritten; old
persistent worlds require a separately qualified migration, outside the current
Memory-provider validation. The original runtime failure remains recorded.

Evidence limit: a continuation reused the first harness stdout filename. Its
observed exit and verbatim exception/stack excerpt remain in the private
`clock-original-failure.txt`; the complete first stdout is unavailable. Subsequent
runner continuations use separate output directories. The post-fix focused
`game_time` harness completed 3 passed / 0 failed / 110 skipped, exit 0. A new
fresh-world calendar regression is being added to the complete harness.

The complete post-fix script harness passed 114/114 with zero failures/skips and
exit 0. Quality, nullable and Python checks passed (156 Python tests, 82 subtests).
All formatter leaves completed; the script formatter only reflowed the new
`Test_GameTime.FreshWorldCalendar` assertions. Final application rebuild/bake and
the focused four-case clock suite qualify that formatted source before GUI smoke.

## Follow-up: interrupted Engine rebase

The owner requested conflict resolution after committing the local fixture patch
as `adde27d5e8` and starting a rebase onto `00c3c4cf52` (Engine 2026.1.72-dev).
Only `Source/Tests/Test_BakerSetup.cpp` is unmerged. Upstream already prepares real
bytecode in both affected fixtures through `BakerTests::AddBakedScriptBytecode`,
including all three script roles and output assertions. The local server-only
helper is therefore redundant. Preserve the upstream file exactly, retain the
original local commit in a private prerequisite-bound bundle, and finish the
existing rebase by dropping this duplicated patch. Preserve project edits/index.
This conflict resolution does not renew the Engine 70 runtime qualification for
the newer Engine revision; no new native behavior is introduced by the resolution.

Resolution completed: the resolved blob is exactly upstream
`8cb6afec7a4e6b794564b39d7066e1e965b87d30`. The existing rebase finished by skipping
the redundant local patch; Engine master is now
`00c3c4cf5207ec7080179e4c9d455221ff1149d4`, matching origin/master, with a clean
worktree/index. The private bundle containing `adde27d5e8` and its original parent
prerequisite was verified before resolution. Both repositories have no unmerged
entries; diff checks and the Engine native test-source layout check pass. The
project index and its existing Engine pin remain unchanged. No new commit or push
was made; native/runtime tests were not rerun for this exact-upstream resolution.

## Follow-up: FixedType file extension

The owner requires `.foinfo` for authored `FixedType` instances. Rename the 12
resource catalogs from `.fopro` to `.foinfo` without changing their bytes, names or
resource arrays. Add `foinfo` to `Baking.ProtoFileExtensions`, retain the existing
`Protos` input directory, and update the owning guide and current private helpers.
Verify complete rename coverage, exact byte preservation and effective baker
dispatch. Existing project/Engine changes and the project index remain intact.

All 12 catalogs now use `.foinfo`; their SHA-256 values match the private snapshot
made before renaming. The guide and current regeneration/check helpers use the new
extension. No old catalog filenames remain. The prototype baker filters by the
configured extension list, which now contains `foinfo` once; the `Protos` input
directory is retained. The project prototype formatter also includes `foinfo` in
its supported extensions so the existing formatting task discovers these inputs.

Validation uses the existing Engine 70 Baker in an isolated output/cache/writable
root under `Workspace/fixedtype-foinfo-20261026/`, because the earlier GUI client
and server remain open. The relevant native baker sources are unchanged between
Engine 70 and current Engine 72; this content check does not qualify a rebuilt
Engine 72 executable. The first invocation had PowerShell-tokenized dotted option
names, wrote eight config outputs in the ordinary `Baking/` tree and was stopped
before completion. Its original log and exit are preserved separately. The retry
passes a quoted argument array; its startup log confirms all isolated paths.
The ordinary output tree therefore still needs a fresh coherent bake before a
future launch; it is not the accepted output of this follow-up.

The isolated full bake completed in 2m47s with exit 0 and no warnings/errors.
`check_resource_sets.py` against that exact output verified all 12 catalogs and
17,194 unchanged root entries, every selected file on disk, fresh build/config
manifest markers, and the existing opaque-data negative control. The formatter's
configured discovery includes all 12 `.foinfo` inputs; its focused `--check` passes
with zero changes. Final project/Engine diff checks pass, neither repository has
unmerged entries, Engine remains clean at `00c3c4cf52`, and the project index is
unchanged. No application was closed and no commit or push was made.
