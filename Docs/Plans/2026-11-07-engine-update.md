# Engine 2026.1.114 integration and CI repair plan

**Goal:** Adopt the fetched Engine update (2026.1.111-dev → 2026.1.114-dev) and
repair the failing GitHub Actions `build` workflow.

> Addendum: after the first pass at `320c982767` (2026.1.113-dev), upstream added
> `a5cb6d1880` [114] — custom entity types register `ExplicitlyPersistent`;
> `MigrationRule Version` 0.0.87 → 0.0.88; every custom type's later property
> indices shift by one (no stored-data conversion). TLA declares no custom
> entity types (`rg ExportEntity|CustomHolder` over `Scripts`, `SourceExt`: no
> hits). The Engine was fast-forwarded to `a5cb6d1880` and the whole chain
> re-run; see "Verification record (final, 2026.1.114)" at the end.

**Architecture:** Keep the project on `master`, fast-forward the Engine's
`master` to the fetched tip, force a complete bake and run the full local
integration chain. For CI, identify the failing job from the public run data,
reproduce it on Linux (WSL) and fix the owning cause.

**Requirements:** [integration procedure](../DocumentationMaintenance.md#engine-submodule-updates),
[verification route](../BuildAndLaunch.md#select-verification-by-the-change).

## Constraints and review focus

- No staging, commits, publication or project branch movement; the gitlink bump
  stays uncommitted for owner review. Preserve all other local work.
- Preserve Memory, single-threaded logic, AngelScript and `TLA.fomain` layout.
- No bake writer overlaps a consumer; check process ownership first.
- Require warning-free builds and bake, terminal native/script results.

## Baseline and incoming range

Project: `2d59e858` (pushed; `origin/master` equal); `master`, clean. Engine
HEAD and committed gitlink: `6ea95ac28d` (`2026.1.111-dev`). Fetched target:
`320c982767` (`2026.1.113-dev`).

Incoming range (oldest first):

1. `4c6ef97d2d` [112] flat map sprites order by sub-layer before row. Rebuild
   client/Mapper; flat decals with non-zero `DrawOrderSubLayer` may paint in a
   different order.
2. `8b32281d50` [112] per-file license headers replaced by a short SPDX header
   (656 files; no behavior change).
3. `320c982767` [113] holder restore indexes equal held entities that have
   records. `MakePersistent(bool)` needs cover of the holder; the read-only
   `Map.ItemIds`/`Critter.ItemIds`/`Item.InnerItemIds`/`Map.CritterIds`/
   `Location.MapIds` and holder-entry `<Entry>Ids` no longer list temporary
   entities. Rebuild server/baker, rebake scripts.

## Project consumer analysis (baseline)

- `Scripts`: `MakePersistent` at `PlayerRegistration.fos:446` (`cr`) and
  `AiControl.fos:2284` (`loc`); no use of the `*Ids` properties or
  `DrawOrderSubLayer` in scripts or `SourceExt`. `SingleThreadedLogic=True`, so
  scripts take no explicit cover.

## GitHub Actions analysis

Public API only (no `gh`, no log access):

- Run `42215392759` (push `2d59e858`, Engine `6ea95ac28d`): only `unit-tests`
  failed (after ~28 min, i.e. at the build/run step, exit code 1); 21 other jobs
  succeeded, `package`/`release` skipped.
- Run `41661414278` (push `78193bd9`): six jobs failed, all in the
  `prepare-workspace.sh` step and all different from the next run, i.e.
  infrastructure flakiness, not a project defect.

## Steps and acceptance

- [x] Inspect both repositories, fetch upstream, read changelog.
- [x] Fast-forward Engine `master` to `320c982767`.
- [ ] Reproduce `unit-tests` on Linux and identify the cause. **Blocked:** no
  log access (see below).
- [x] Reconfigure, build all native targets warning-free (Windows).
- [x] Force a complete bake; warning-free.
- [x] Execute `Verify :: All` leaves.
- [x] Review final diff, record results and qualification limits.

## CI finding

The TLA `unit-tests` job builds and runs the Engine's own test suite
(`build.sh linux unit-tests Release` + `RunUnitTests`). Engine's own CI
(`cvet/fonline`, public check-run data) shows the same job family failing
since `8b1a9d5547` (2026.1.107-dev): `validate.sh unit-tests`, the four
sanitizer variants, wide-coordinate, unity build and coverage, on every push
through `320c982767` (2026.1.113-dev); the last green Engine push is
`3d56c1f3f9`. All Linux/Windows/macOS/Android/Web builds are green. So the TLA
`unit-tests` failure is the Engine's Linux test failure, not a TLA config or
script defect, and the Engine bump to 2026.1.113-dev does not clear it. Public
API exposes only "Process completed with exit code 1" annotations; job logs need
authentication, and WSL here has Python 3.10 (`buildtools.py` needs 3.11+) and
no passwordless `sudo`, so the failing test name is unknown.

## Verification record

Evidence root: ignored `Workspace/engine-update-20261107/`.

Engine advanced `6ea95ac28d → 320c982767` (fast-forward, worktree clean).
Committed and index pins remain `6ea95ac28d`; the working-tree gitlink is the
new revision, intentionally unstaged. No project source, config or script change
was needed: the two `MakePersistent` calls run under `SingleThreadedLogic`
without explicit cover, and no script or `SourceExt` code reads the
`*Ids` properties or `DrawOrderSubLayer`.

- `cmake --preset auto`: exit 0; all six native targets: exit 0; no warnings.
- `ForceBakeResources`: exit 0, "Baking complete!", no warnings.
- `TLA_UnitTests.exe`: exit 0, `test cases: 843 | 839 passed | 4 skipped`,
  `assertions: 1326901 | 1326901 passed`.
- `TLA_ServerHeadless.exe --ApplySubConfig LocalTest --Testing.Enabled True`:
  exit 0, `COMPLETE: 128 passed, 0 failed, 0 skipped (of 128)`.
- Script quality ratchet, nullable markers/validator/placement, `pytest Tools`
  (220 passed, 89 subtests), `Format :: Scripts/Prototypes/Main Config`: all
  exit 0; formatters changed nothing. `git diff --check` clean.

Qualification limits: Windows x64 MSVC only; no Linux run, GUI/visual route or
restart-persistence run. The flat-sprite order change (changelog [112]) was not
checked visually.

## CI root cause (supersedes "CI finding" above)

With the job log of run `42215392759` (`unit-tests`, TLA `2d59e858`, Engine
`6ea95ac28d`) the failure is a **compile error**, not a failing test: Linux
clang rejects `Engine/Source/Tests/Test_PathFinding.cpp` (lines 2246 and 2250
of that revision; 2212 now):

```
error: variable 'MAP_SIZE' cannot be implicitly captured in a lambda with no
capture-default specified
  input.CheckHex = [&check_calls, &is_blocked, local](mpos hex) -> HexBlockResult {
```

`MAP_SIZE` is a function-local `constexpr msize` that the lambda odr-uses
(member calls `is_valid_pos`/`from_raw_pos`); MSVC accepts it, clang does not.
The error exists in the Engine since 2026.1.107-dev's large-map test and is also
why Engine's own `validate.sh unit-tests` family failed. The link and test run
never started, so Linux test results beyond this are still unknown.

Prepared fix (uncommitted in the Engine worktree, one line, saved as
`Workspace/engine-update-20261107b/engine-linux-clang-capture-fix.patch`):
add `MAP_SIZE` to the capture list of that lambda. It must be committed in the
Engine repository (with its own version/changelog rules) to reach CI; the TLA
gitlink then has to be bumped to that commit.

## Verification record (final, 2026.1.114)

Evidence root: ignored `Workspace/engine-update-20261107b/`.

Engine advanced to `a5cb6d1880` (2026.1.114-dev, fast-forward). Committed and
index pins remain `6ea95ac28d`; the working-tree gitlink is the new revision.
The Engine worktree carries the one-line test fix above.

- Configure and all six native targets: exit 0, no warnings (the unit tests
  built with the fix applied).
- `ForceBakeResources`: exit 0, "Baking complete!", no warnings.
- `TLA_UnitTests.exe`: exit 0, `843 | 839 passed | 4 skipped`,
  `assertions: 1326916 | 1326916 passed`.
- `TLA_ServerHeadless.exe --ApplySubConfig LocalTest --Testing.Enabled True`:
  exit 0, `COMPLETE: 128 passed, 0 failed, 0 skipped (of 128)`.
- Script ratchet, nullable checks, `pytest Tools` (220 passed, 89 subtests),
  three formatters (0 changed): all exit 0. `git diff --check` clean.
- The compile error cannot occur on Windows, so the fix is verified here only
  as non-regressing; its effect on Linux is confirmed by the log, not by a run.

Qualification limits: Windows x64 MSVC only; no Linux build or run, no GUI or
restart-persistence run.
