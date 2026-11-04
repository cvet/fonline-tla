# Engine 2026.1.109 integration plan

**Goal:** Adopt the fetched Engine update (2026.1.106-dev → 2026.1.109-dev) and
migrate `TLA.fomain` to the new zero-based settings model without project
regressions.

**Architecture:** Keep the project on `master` and fast-forward the Engine's
`master` to the fetched upstream tip. Migrate the retired `Baking.*` directory
settings to `Common.*`, force a complete bake and run the full local
integration chain.

**Requirements:** [integration procedure](../DocumentationMaintenance.md#engine-submodule-updates),
[verification route](../BuildAndLaunch.md#select-verification-by-the-change), and
[configuration owner](../ContentWorkflow.md#configuration-and-secure-channel).

## Constraints and review focus

- No staging, commits, publication or project branch movement; the gitlink bump
  stays uncommitted for owner review. Preserve all other local work.
- Preserve Memory, single-threaded logic, AngelScript and `TLA.fomain` pack
  layout unless an incoming change requires otherwise.
- Do not overlap bake writers and consumers; check process ownership first.
- Require warning-free builds and bake, terminal native/script results, and
  clean task-owned process exits.

## Baseline and incoming range

Project: `b11f4e84`; `master`; working tree had `VERSION` `0.3.19 → 0.3.20`
(bake-generated, not mine). Engine HEAD and committed gitlink:
`3d56c1f3f99914527b7a8911480743267d5452e2` (`2026.1.106-dev`).
Fetched target: `9e096e8f6f` (`2026.1.109-dev`).

Incoming range (oldest first):

1. `8b1a9d5547` [107] Initialize packaged settings from one zero-based profile.
   `Setup*` vs `Apply*` split; startup applies authored config without
   `Settings.inc` defaults; typed zeros are omitted from baked profiles;
   metadata Setting records hold name/type only (file version 6);
   `MigrationRule Version` 0.0.86 → 0.0.87; retired `Baking.ResourcesDir`,
   `Baking.CacheResources`, `Baking.PlatformBinaries`, `Baking.ClientResources`,
   `Baking.ServerResources` replaced by `Common.ResourcesPath`,
   `Common.CachePath`, `Common.PlatformBinariesPath`; the old keys are rejected.
2. `90061a40d4` [108] test fixture repairs only.
3. `9e096e8f6f` [109] Large map streaming (#232): chunked grid, client field
   light, lazy server map content, `Map.LoadRuntimeStaticItems` family,
   `Game.LoadStaticMap(s)`; no settings/wire/ABI change. Native consumers:
   `MapView::GetLightData`/`SetLight` removed.

## Project consumer analysis

- `TLA.fomain` authors the four retired `Baking.*` directory keys (lines 74–77):
  must move to `Common.*`.
- Docs referencing the old names: `Docs/EngineSettingsAudit.md`.
- To check: `SourceExt` for `GetLightData|SetLight\(`, grid subclasses.

## Steps and acceptance

- [x] Fast-forward Engine `master` to `9e096e8f6f`.
- [x] Migrate `TLA.fomain` directory settings.
- [x] Reconfigure, build all native targets warning-free.
  **Exception:** `TLA_UnitTests` does not compile on the pristine Engine tip.
- [x] Force a complete bake; warning-free.
- [x] Execute `Verify :: All` leaves; inspect COMPLETE counts, exit codes and
  runtime exceptions.
- [x] Docs: `ContentWorkflow.md` configuration paragraph. `EngineSettingsAudit.md`
  is a dated historical snapshot and is left unchanged.
- [x] Review final diff, record results and qualification limits.

## Verification record

Evidence root: ignored `Workspace/engine-update-20261105/`.

Engine advanced `3d56c1f3f9 → 9e096e8f6f` (fast-forward). Committed and index
pins remain `3d56c1f3f9`; the working-tree gitlink is the new revision,
intentionally unstaged.

Project change: `TLA.fomain` drops `Baking.ServerResources`,
`Baking.ClientResources`, `Baking.PlatformBinaries`, `Baking.CacheResources` and
adds `Common.ResourcesPath = Resources`, `Common.PlatformBinariesPath =
PlatformBinaries`, `Common.CachePath = Cache` (same values; the old
`ServerResources` split is replaced by the server packs at the resource root).
The authored config was already complete: the bake raised no completeness error.
No `SourceExt`/script change was needed (no `GetLightData`/`SetLight`/grid hits).

Results:

- `cmake --preset auto`: exit 0, no warnings.
- `TLA_Server`, `TLA_ServerHeadless`, `TLA_Client`, `TLA_Mapper`,
  `TLA_ASCompiler`: exit 0, no warnings.
- `ForceBakeResources`: exit 0, "Baking complete!" (9m27s), no warnings.
- `TLA_ServerHeadless.exe --ApplySubConfig LocalTest --Testing.Enabled True`:
  exit 0, `COMPLETE: 128 passed, 0 failed, 0 skipped (of 128)`, clean shutdown.
- Script quality ratchet (no new violations), nullable markers `--check`,
  nullable validator test, placement and coverage, `pytest Tools` (220 passed,
  89 subtests), `Format :: Scripts/Prototypes/Main Config`: all exit 0; the
  formatters changed nothing.
- `git diff --check` clean.

**Engine defect (blocker for a pristine unit-test build).** With the project's
default 16-bit map coordinates (`FO_MAP_WIDE_COORDS` OFF), the upstream tests
`Engine/Source/Tests/Test_LineTracer.cpp` (lines 198, 243, 308) and
`Test_PathFinding.cpp` (1443, 2226) fail with MSVC C2398 (narrowing
`128000 → mcoord_t`): `if constexpr` outside a template does not discard the
branch, and `msize {128000, 128000}` is compiled anyway. To still measure the
rest, I applied a temporary `static_cast<mcoord_t>(128000)` workaround in those
two Engine test files (saved as
`Workspace/engine-update-20261105/engine-test-narrowing-workaround.patch`) and
then reverted it; the Engine worktree is clean. With the workaround,
`TLA_UnitTests` built warning-free and `TLA_UnitTests.exe` exited 0:
`test cases: 834 | 832 passed | 2 skipped`, `assertions: 1324291 | 1324291
passed` (the two skips are the wide-coordinate cases). The pristine tip must be
fixed upstream (or built with `FO_MAP_WIDE_COORDS`, which changes the map
coordinate contract and is not done here). The `TLA_UnitTests.exe` on disk was
linked from the workaround build; a rebuild on the pristine tip fails until fixed.

Qualification limits: Windows x64 MSVC only; no GUI/visual player route, Linux
build or restart-persistence run. The new runtime map-content API
(`Map.LoadRuntimeStaticItems`, `Game.LoadStaticMap`) is unused by TLA. Lazy
server map loading means a damaged baked map is now reported at first use, not
at startup. `Verify :: All` leaves were run individually after one forced bake.
