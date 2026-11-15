# Engine 2026.1.118 integration plan

**Goal:** Adopt the fetched Engine update `de3dfb6c8c` (2026.1.115-dev) →
`7d134df5f8` (2026.1.118-dev) and restore the failing CI run `42489693470`.

**Architecture:** Keep the project on `master`, fast-forward the Engine
submodule's `master` to the fetched tip, regenerate the root version, force a
complete bake and run the full local `Verify :: All` chain. The incoming range
contains the Engine-side fix for the Linux/clang build error that failed two CI
jobs; no project-side workaround is added.

**Requirements:** [integration procedure](../DocumentationMaintenance.md#engine-submodule-updates),
[verification route](../BuildAndLaunch.md#select-verification-by-the-change).

## Constraints and review focus

- The owner asked to fix the failing GitHub Actions run `42489693470`, so
  committing and pushing the verified Engine bump to `master` is in scope.
  Nothing else is committed; the pushed tree is exactly the verified tree.
- Preserve Memory storage, `Server.SingleThreadedLogic=True`, AngelScript and
  the `TLA.fomain` layout.
- No bake writer overlaps a consumer; check process ownership first.
- Require warning-free builds and bake, terminal native/script results.

## Baseline, incoming range and CI evidence

Project: `59e32f720` (pushed; `origin/master` equal), `master`, clean,
`VERSION` 0.3.22. Engine HEAD and committed gitlink: `de3dfb6c8c`
(`2026.1.115-dev`). Fetched target: `7d134df5f8` (`2026.1.118-dev`).

CI run `42489693470` (push `59e32f720`): `unit-tests` and
`linux-build (linux server Release)` failed; every other job passed. Both
failures are the same clang diagnostic while compiling
`SourceExt/ServerExtension.cpp`: `Engine/Source/Server/EntityManager.h:146:91:
error: use of undeclared identifier '_registryLock'`. MSVC ignores the
thread-safety attribute, so Windows jobs stayed green.

Incoming range (oldest first):

1. `c5101d149a` [116] fix the Linux server build: declare
   `EntityManager::ReserveRegistrationId()` with a leading return type so clang
   parses `FO_TSA_EXCLUDES(_registryLock)` after the class is complete; shorten
   the `StaticMap` and `PathFindingCost` comments to the two-line limit.
2. `af8fa774d8` [117] align the Engine release-safety documentation test with
   the parameterized `ResolveSettingValue()` baking mode. Engine test-only
   change; no Engine behavior change.
3. `7d134df5f8` [118] resolve hex boundary pixels in exact integer arithmetic
   in `GeometryHelper::GetHexPosCoord()` for hexagonal geometry.

Migration records: `115 → 116 → 117 → 118`, all without project migration. No
API, property, serialization, network, Managed ABI or resource-schema change;
`MigrationRule Version` is unchanged. Rebuild native roles; a pixel exactly on
a hex boundary may resolve to a different adjacent cell than before, now the
same at every map distance.

## Project consumer analysis

- TLA builds with hexagonal geometry: `CMakeLists.txt:29` sets
  `FO_GEOMETRY HEXAGONAL`, and `TLA.fomain` supplies the matching
  `Geometry.MapHex*` dimensions. Commit `7d134df5f8` therefore changes the
  active `if constexpr (HEXAGONAL_GEOMETRY)` branch of `GetHexPosCoord()`.
  TLA maps are small, while the old double rounding diverged only for pixels
  millions of pixels from the origin; the new integer arithmetic is exact and
  the Engine section `GetHexPosCoord far out on a large map resolves pixels
  like near the origin` runs inside `TLA_UnitTests`.
- `EntityManager` is Engine server code; no `SourceExt` file references
  `_registryLock`, `ReserveRegistrationId()` or the changed declaration. The
  header is included through `SourceExt/ServerExtension.cpp` only.
- `af8fa774d8` touches `Engine/BuildTools/tests/`, which the project CI does
  not run; no project consumer.
- No scripts or authored content depend on the changed Engine surfaces.

## Steps and acceptance

- [x] Fast-forward the Engine submodule `master` to `7d134df5f8`; verify the
  worktree is clean and the root working-tree gitlink names the new revision.
- [x] Regenerate `VERSION` with `Generate :: Version` (0.3.22 → 0.3.23).
- [x] `cmake --preset auto`; build Server, ServerHeadless, Client, Mapper,
  ASCompiler and UnitTests warning-free.
- [x] Force a complete bake; warning-free.
- [x] Execute `TLA_UnitTests.exe`; expect a full pass.
- [x] Execute the AngelScript harness under `LocalTest`; record `COMPLETE`
  counts and exit code.
- [x] Run the script-quality ratchet, nullable chain, `pytest Tools` and
  `Format :: All`; formatters must change nothing.
- [x] Review the final diff; commit the Engine gitlink, `VERSION` and this plan;
  push to `origin/master`.
- [x] Watch the pushed CI run to green and record it below.
- [x] Record actual results and qualification limits.

## Verification record

Evidence root: ignored `Workspace/engine-update-20261109/`.

Engine advanced `de3dfb6c8c → 7d134df5f8` (fast-forward on `master`); the
worktree is clean and the root working-tree gitlink names the new revision.
`VERSION` was generated as 0.3.23.

- `cmake --preset auto`: exit 0.
- Server, ServerHeadless, Client, Mapper, ASCompiler, UnitTests: exit 0, no
  warnings.
- `ForceBakeResources`: exit 0, "Baking complete!", no warnings; 550 map files
  baked.
- `TLA_UnitTests.exe`: exit 0, `test cases: 845 | 841 passed | 4 skipped`,
  `assertions: 1326942 | 1326942 passed`. The hex geometry test and its
  `far out on a large map` section are part of the run; the case count is
  unchanged because the incoming range adds no new test case.
- `TLA_ServerHeadless.exe --ApplySubConfig LocalTest --Testing.Enabled True`:
  exit 0, `COMPLETE: 128 passed, 0 failed, 0 skipped (of 128)`, clean startup
  and shutdown.
- Script-quality ratchet: exit 0, no new violations. Nullable markers (0 files
  changed), validator tests, placement and coverage: exit 0. `pytest Tools`:
  220 passed, 89 subtests. The three formatters: exit 0 and changed no files.

CI run `42659073265` (push `6af83c982`, the commit containing this plan's
first revision): `success`, 21 jobs green, `release` skipped as expected for a
push event. The two jobs that failed in run `42489693470` now pass:
`unit-tests` (28m38s, builds and runs the project native tests on Linux) and
`linux-build (linux server Release)` (13m56s). `validate`, `quality-gates`,
`compile-scripts`, `bake-resources`, every Windows/Linux/macOS/Android/web
build and `package` also pass.

Qualification limits: local verification is Windows x64 MSVC only; the
Linux/clang failure is fixed by Engine `c5101d149a` and proven by CI. No GUI or
restart-persistence run; hex boundary resolution at million-pixel distances
does not occur on TLA's map sizes and is covered by the Engine native test
instead. Local `TLA_UnitTests` runs the project test configuration; CI repeats
that route on Linux.
