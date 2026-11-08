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

- [ ] Fast-forward the Engine submodule `master` to `de3dfb6c8c`; verify the
  worktree is clean and the root working-tree gitlink names the new revision.
- [ ] Regenerate `VERSION` with `Generate :: Version` (0.3.21 → 0.3.22).
- [ ] `cmake --preset auto`; build Server, ServerHeadless, Client, Mapper,
  ASCompiler and UnitTests warning-free.
- [ ] Force a complete bake; warning-free.
- [ ] Execute `TLA_UnitTests.exe`; expect a full pass and the two new tests.
- [ ] Execute the AngelScript harness under `LocalTest`; record `COMPLETE`
  counts and exit code.
- [ ] Run the script-quality ratchet, nullable chain, `pytest Tools` and
  `Format :: All`; formatters must change nothing.
- [ ] Review the final diff; record actual results and qualification limits.

## Verification record

To be filled after the chain runs.
