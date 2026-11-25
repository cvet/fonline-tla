# Engine 2026.1.135 integration plan

**Goal:** Adopt the fetched Engine update `66fc22770d` (2026.1.133-dev) →
`eac3369a51` (2026.1.135-dev).

**Architecture:** Keep the project on `master`, fast-forward the Engine
submodule's `master` to the fetched tip, regenerate the root version, force a
complete bake and run the full local `Verify :: All` chain.

**Requirements:** [integration procedure](../DocumentationMaintenance.md#engine-submodule-updates),
[verification route](../BuildAndLaunch.md#select-verification-by-the-change).

## Constraints and review focus

- The owner asked to support the Engine update and then to commit the project.
  The commit is local (Engine gitlink, `VERSION`, `TLA.fomain`, this plan); no
  push was authorized.
- Preserve Memory storage, `Server.SingleThreadedLogic=True`, AngelScript and
  the `TLA.fomain` layout.
- No bake writer overlaps a consumer; check process ownership first.
- Require warning-free builds and bake, terminal native/script results.

## Baseline and incoming range

Project: `3ae34e45` (`origin/master` equal), `master`, clean, `VERSION`
0.3.25. Engine HEAD and committed gitlink: `66fc22770d` (`2026.1.133-dev`).
Fetched target: `eac3369a51` (`2026.1.135-dev`).

Incoming range (oldest first):

1. `52be20b000` [134] compare pointers with `NULL` explicitly in vendored
   libmongoc (`mongoc-handshake.c`, `mongoc-oidc-cache.c`) so MSVC 19.52 no
   longer stops with `C4047`; drop terminal periods of nine comments in
   `BuildTools` and the script test harness example; qualify two helper calls
   in `Test_ClientServerIntegration.cpp`.
2. `06c5ca2891` [135] `Test_AiControlListener.cpp` stops brace-initializing
   `nlohmann::json` from a response (which wrapped it in an array); native
   safety audit CLI help alignment and regenerated helper CLI reference.
3. `eac3369a51` `Test_ConfigBaker.cpp` passes the `**/*.fos` include pattern
   as a format argument. Test-only; no version bump.

Migration records: `133 → 134 → 135`, both "no migration". No API, property,
serialization, network, Managed ABI or resource-schema change.

## Project consumer analysis

- **Required `TLA.fomain` setting.** The baker rejects a main config that does
  not list every server setting (`Uninitialized server setting
  ServerNetwork.MaxPropertyDataSize`). The setting (Engine changelog
  2026.1.133-dev, default `65536`) was introduced before this range; the first
  force bake on the new Engine failed on it. Decision: add
  `ServerNetwork.MaxPropertyDataSize = 65536` after `MaxRemoteCallPayloadSize`,
  the Engine default, so behavior is unchanged.

- libmongoc is Engine-vendored; TLA uses Memory storage locally, but the
  server targets still compile the driver, so the MSVC fix affects the local
  Windows build route.
- The `Test_*` changes are compiled into `TLA_UnitTests` and run there.
- `BuildTools` comment/CLI changes: the project runs
  `check_native_source_layout.py` (`Analyze :: Native Source Layout`) and
  packaging through `package.py`; only comments and help formatting changed.
- `TLA.fomain` uses `IncludePatterns = *`; unaffected by the test change.
- No scripts, `SourceExt` or authored content depend on the changed surfaces.

## Steps and acceptance

- [x] Fast-forward the Engine submodule `master` to `eac3369a51`; worktree clean,
  root working-tree gitlink names the new revision.
- [x] Regenerate `VERSION` with `Generate :: Version` (0.3.25 → 0.3.26).
- [x] Add the missing `ServerNetwork.MaxPropertyDataSize` to `TLA.fomain`.
- [x] `cmake --preset auto`; build Server, ServerHeadless, Client, Mapper,
  ASCompiler and UnitTests warning-free.
- [x] Force a complete bake; warning-free.
- [ ] Execute `TLA_UnitTests.exe` to a full pass (see qualification: open).
- [x] Execute the AngelScript harness under `LocalTest`.
- [x] Run the script-quality ratchet, nullable chain, native source layout,
  Engine script checks, `pytest Tools` and the formatters.
- [x] Review the diff and record actual results and qualification limits.

## Verification record

Evidence root: ignored `Workspace/engine-update-20261125/`.

Engine advanced `66fc22770d → eac3369a51` (fast-forward on `master`); `VERSION`
generated as 0.3.26.

- `cmake --preset auto`: exit 0. Server, ServerHeadless, Client, Mapper,
  ASCompiler, UnitTests: exit 0, 0 warnings each.
- `ForceBakeResources`: first run failed on the missing setting above (exit 1,
  kept as `force-bake.log`); after the `TLA.fomain` fix exit 0, "Baking
  complete!", 550 map files, no warnings.
- `TLA_ServerHeadless.exe --ApplySubConfig LocalTest --Testing.Enabled True`:
  exit 0, `COMPLETE: 133 passed, 0 failed, 0 skipped (of 133)`.
- Script-quality ratchet, nullable markers/validator/placement/coverage, native
  source layout, Engine script checks: exit 0, no new findings. `pytest Tools`:
  220 passed, 89 subtests. The three formatters: exit 0, changed no files.
- `TLA_UnitTests.exe` is **not green**. Run 1: 891 cases, 886 passed, 1 failed,
  4 skipped (exit 42): `Threading / PreciseSleepReachesItsDeadlineForLongerWaits`
  and `CoarseSleepLandsWithinHalfAMillisecond` measured 28 ms and 18 ms against
  8 ms and 6 ms limits. Run 2 (rerun of the full suite): 885 passed, 2 failed:
  the same two `Threading` checks (64 ms, 51 ms) plus
  `ServerEngineWritesHealthFile` (health file not written within its 2 s wait).
  `Threading*` alone passed three times and once more later. During the
  reruns the host CPU stayed at 100 % because of other `cl.exe`/`VBCSCompiler`
  builds that are not part of this task, and `ServerEngineWritesHealthFile`
  also failed when run alone under that load. None of the failing test files
  changed in this Engine range, which only touches `Test_AiControlListener`,
  `Test_ClientServerIntegration` and `Test_ConfigBaker`. Cause attributed to
  host load, not proven: a rerun on an idle host is still required.

Qualification limits: local verification is Windows x64 MSVC only; no GUI or
restart-persistence run; the native unit-test result above is open; CI has not
run for this commit.
