# Engine 2026.1.115 integration plan

**Goal:** Adopt the fetched Engine update `0d1a56de63` (2026.1.114-dev) →
`de3dfb6c8c` (2026.1.115-dev) and keep the project's local integration green.

**Architecture:** Keep the project on `master`, fast-forward the Engine
submodule's `master` to the fetched tip, regenerate the root version, force a
complete bake and run the full local `Verify :: All` chain.

**Requirements:** [integration procedure](../DocumentationMaintenance.md#engine-submodule-updates),
[verification route](../BuildAndLaunch.md#select-verification-by-the-change).

## Constraints and review focus

- No staging, commits, publication or project branch movement; the gitlink bump
  and version bump stay uncommitted for owner review. Preserve all other local
  work.
- Preserve Memory storage, `Server.SingleThreadedLogic=True`, AngelScript and the
  `TLA.fomain` layout.
- No bake writer overlaps a consumer; check process ownership first.
- Require warning-free builds and bake, terminal native/script results.

## Baseline and incoming range

Project: `33fcb8506` (pushed; `origin/master` equal), `master`, clean,
`VERSION` 0.3.21. Engine HEAD and committed gitlink: `0d1a56de63`
(`2026.1.114-dev`). Fetched target: `de3dfb6c8c` (`2026.1.115-dev`).

Incoming range (oldest first):

1. `de3dfb6c8c` [115] stop server freezes from lock-order inversions with the
   Game lock. A fresh entity id is now reserved before the registry lock is
   taken; the id-range bound is persisted under the Game lock without the
   registry; `FlushExactEntityId()` takes the Game lock first. `Player::
   Send_LoginSuccess()` / `Send_InitData()` encode global values through
   `CaptureGlobalVars()` before the connection lock. New tests:
   `ServerEntityIdReserveWaitsForGameLockOutsideRegistry`,
   `PlayerGlobalVarsAreCapturedBeforeTheConnectionIsTaken`.

Migration record: baseline `0d1a56de63` → `2026.1.115-dev`, no project
migration required; entity ids stay unique and monotonic, stored documents,
property ids, network messages, Managed ABI, resource schemas and the
`MigrationRule Version` marker are unchanged. `Server.EntityIdReserveBatch` must
be positive; TLA sets 1000 (`TLA.fomain:417`).

## Project consumer analysis

- `Scripts/GlobalmapGroup.fos` takes `Game.Lock()`/`Game.Unlock()` around its
  script-owned global group maps (5 scopes). The Engine fix changes native lock
  ordering only, under `SingleThreadedLogic=True`; no script change is required.
- No `SourceExt` code uses `EntityManager` registration, id-bound, connection
  send or capture APIs.
- The server role must be rebuilt; all roles rebuild as part of the chain.

## Steps and acceptance

- [x] Fast-forward the Engine submodule `master` to `de3dfb6c8c`; verify the
  worktree is clean and the root working-tree gitlink names the new revision.
- [x] Regenerate `VERSION` with `Generate :: Version` (0.3.21 → 0.3.22).
- [x] `cmake --preset auto`; build Server, ServerHeadless, Client, Mapper,
  ASCompiler and UnitTests warning-free.
- [x] Force a complete bake; warning-free.
- [x] Execute `TLA_UnitTests.exe`; expect a full pass and the two new tests.
- [x] Execute the AngelScript harness under `LocalTest`; record `COMPLETE`
  counts and exit code.
- [x] Run the script-quality ratchet, nullable chain, `pytest Tools` and
  `Format :: All`; formatters must change nothing.
- [x] Review the final diff; record actual results and qualification limits.

## Verification record

Evidence root: ignored `Workspace/engine-update-20261108/`.

Engine advanced `0d1a56de63 → de3dfb6c8c` (fast-forward). The local `master`
branch had been left 22 commits behind the detached pin; it now matches
`origin/master`. The Engine worktree is clean.

The root gitlink, `VERSION` 0.3.22 and this plan were committed and pushed by
the owner as `8ba3c0b14` after the checks below ran; the committed tree is the
verified tree (formatters changed nothing, so only those three paths differ
from the baseline).

- `cmake --preset auto`: exit 0.
- Server, ServerHeadless, Client, Mapper, ASCompiler, UnitTests: exit 0, no
  warnings.
- `ForceBakeResources`: exit 0, "Baking complete!", no warnings; 550 map files
  baked.
- `TLA_UnitTests.exe`: exit 0, `test cases: 845 | 841 passed | 4 skipped`,
  `assertions: 1326950 | 1326950 passed`. The two incoming lock-order tests do
  not print on success; the case count rose from the previous 843 by exactly
  two.
- `TLA_ServerHeadless.exe --ApplySubConfig LocalTest --Testing.Enabled True`:
  exit 0, `COMPLETE: 128 passed, 0 failed, 0 skipped (of 128)`.
- Script-quality ratchet, nullable markers/validator/placement/coverage,
  `pytest Tools` (220 passed, 89 subtests), the three formatters (0 changed):
  exit 0. `git diff --check` clean.

Qualification limits: Windows x64 MSVC only; no Linux build or run, no GUI or
restart-persistence run. The lock-order fix is proven by the Engine's native
tests; TLA runs `Server.SingleThreadedLogic=True`, so the concurrent scenario
itself is not reproduced in the project runtime.
