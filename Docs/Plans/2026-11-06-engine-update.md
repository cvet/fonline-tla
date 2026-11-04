# Engine 2026.1.111 integration plan

**Goal:** Adopt the fetched Engine update (2026.1.109-dev → 2026.1.111-dev) and
verify TLA's existing behavior, including the unit-test build that
2026.1.109-dev could not compile.

**Architecture:** Keep the project on `master`, fast-forward the Engine's
`master` to the fetched tip, retain project configuration unless a build, bake
or migration note requires a change, force a complete bake and run the full
local integration chain.

**Requirements:** [integration procedure](../DocumentationMaintenance.md#engine-submodule-updates),
[verification route](../BuildAndLaunch.md#select-verification-by-the-change), and
[configuration owner](../ContentWorkflow.md#configuration-and-secure-channel).

## Constraints and review focus

- No staging, commits, publication or project branch movement; the gitlink bump
  stays uncommitted for owner review. Preserve all other local work.
- Preserve Memory, single-threaded logic, AngelScript and `TLA.fomain` layout.
- No bake writer overlaps a consumer; no TLA process was running at the start.
- Require warning-free builds and bake, terminal native/script results, and
  clean task-owned process exits.

## Baseline and incoming range

Project: `5b2f96e4` (the owner folded the previous integration, `TLA.fomain`
`Common.*` migration and `Engine` pin `9e096e8f6f`, into this commit; unpushed);
`master`, clean. Engine HEAD and committed gitlink: `9e096e8f6f`
(`2026.1.109-dev`). Fetched target: `6ea95ac28d` (`2026.1.111-dev`).

Incoming range (oldest first):

1. `b055b5da22` [110] large-map tests built for 16-bit map coordinates (fixes the
   `LF_UnitTests`/`TLA_UnitTests` compile failure recorded in the previous plan);
   server static-map cache keys a pending read by its shared promise.
2. `6ea95ac28d` [111] precise map geometry and scene depth far from the map
   origin: `GeometryHelper::GetHexMapDepth(..., originY)`,
   `SpriteManager::DrawSprites` takes the depth origin row, exact
   `GetHexPosCoord`, integer `GetLineDirAngle`, light-ray and scroll fixes,
   `ModelInstance` rotation, item flight end point, SPARK bounds step count
   (rebake to refresh particle bounds). `Settings.inc` comment-only change.

Engine notes: no API, settings, wire, `MigrationRule Version`, Managed ABI,
saved-data or resource-schema change. Rebuild every native role and rebake.

## Project consumer analysis (baseline)

- `rg` over `SourceExt` for `DrawSprites|GetHexMapDepth|GetHexPosCoord|
  GetLineDirAngle|MovingContext|TraceLightLine`: no hits.

## Steps and acceptance

- [x] Inspect both repositories, fetch upstream, read changelog.
- [x] Fast-forward Engine `master` to `6ea95ac28d`.
- [x] Reconfigure, build all native targets (including `TLA_UnitTests` on the
  pristine tip) warning-free.
- [x] Force a complete bake; warning-free.
- [x] Execute `Verify :: All` leaves; inspect COMPLETE counts, exit codes and
  runtime exceptions.
- [x] Review final diff, record results and qualification limits.

## Verification record

Evidence root: ignored `Workspace/engine-update-20261106/`.

Engine advanced `9e096e8f6f → 6ea95ac28d` (fast-forward, worktree clean).
Committed and index pins remain `9e096e8f6f`; the working-tree gitlink is the
new revision, intentionally unstaged. No project source, config or script change
was needed.

- `cmake --preset auto`: exit 0, no warnings.
- `TLA_Server`, `TLA_ServerHeadless`, `TLA_Client`, `TLA_Mapper`,
  `TLA_ASCompiler`, `TLA_UnitTests` (pristine tip, no workaround): each exit 0,
  no compiler warnings.
- `ForceBakeResources`: exit 0, "Baking complete!", no warnings.
- `TLA_UnitTests.exe`: exit 0, `test cases: 836 | 832 passed | 4 skipped`,
  `assertions: 1326739 | 1326739 passed` (skips are the wide-coordinate cases).
- `TLA_ServerHeadless.exe --ApplySubConfig LocalTest --Testing.Enabled True`:
  exit 0, `COMPLETE: 128 passed, 0 failed, 0 skipped (of 128)`.
- Script quality ratchet (no new violations), nullable markers `--check`,
  nullable validator test, placement and coverage, `pytest Tools` (220 passed,
  89 subtests), `Format :: Scripts/Prototypes/Main Config`: all exit 0; the
  formatters changed nothing. `git diff --check` clean. No TLA process left.

Resulting diff: `Engine` gitlink `9e096e8f6f → 6ea95ac28d` (working tree only)
plus this plan; `VERSION` stays `0.3.19`.

Qualification limits: Windows x64 MSVC only; no GUI/visual player route, Linux
build or restart-persistence run. Rendering depth, hex picking and light-ray
changes (changelog [111]) affect the client map view and were not checked
visually; the TLA map size is small, so the precision fixes are not expected to
change visible behavior. `Verify :: All` leaves were run individually after one
forced bake.
