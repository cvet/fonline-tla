# Engine 2026.1.106 integration plan

**Goal:** Adopt the fetched Engine update (2026.1.98-dev → 2026.1.106-dev) and
verify TLA's existing behavior without project regressions.

**Architecture:** Keep the project on `master` and fast-forward the Engine's
`master` to the fetched upstream tip. Retain project configuration unless a
build, bake or migration note requires a change, force a complete bake and run
the full local integration chain.

**Requirements:** [integration procedure](../DocumentationMaintenance.md#engine-submodule-updates),
[verification route](../BuildAndLaunch.md#select-verification-by-the-change), and
[configuration owner](../ContentWorkflow.md#configuration-and-secure-channel).

## Constraints and review focus

- No staging, commits, publication or project branch movement; the gitlink bump
  stays uncommitted for owner review. Preserve all other local work.
- Preserve Memory, single-threaded logic, AngelScript and `TLA.fomain` pack
  layout unless an incoming change requires otherwise.
- Keep consumers away from bake/build writers. Running `Forcanum_Baker.exe` and
  `LF_Baker.exe` belong to sibling projects (other paths); no TLA process ran.
- Require warning-free builds and bake, terminal native/script results, and
  clean task-owned process exits.

## Baseline and incoming range

Project: `78193bd9`; `master`, clean. Engine HEAD and committed gitlink:
`ac37c9d217b314b3f3a1f567f67be535cfe15cac` (`2026.1.98-dev`).
Fetched target: `3d56c1f3f99914527b7a8911480743267d5452e2` (`2026.1.106-dev`).

Complete incoming range (oldest first), per-commit version in brackets:

1. `8dd3fa35f7` [99] Code refactoring (#231): native refactoring merge — checked
   arithmetic deduces from equal operand types (`checked_mul<int64_t>(a, b)` no
   longer compiles), `FileReader::Get*` consuming readers renamed `Read*`,
   record member operations moved to free functions, braced initialization.
2. `9d838ea0ab` [99] refactor follow-up (6 files).
3. `1ad91af999` [100] native guard initialization (`OutBufAccessor`/`InBufAccessor`
   direct construction), Vulkan in-flight slots in `array`, updater fixtures.
4. `20998dd3e8` [101] API contract; `ImageImport::FrameCollection::Dirs` becomes
   `array`; additive `Game.SimulateTouchScroll`. API inventory 2593 symbols.
5. `82ac7d57fe`, `7348efd742`, `2a24c54275`, `72c1be91a0` [102] large-map work.
6. `0bd0702354` [103] reverts 5 as unreviewed — net sources of [101].
7. `28b3a9b22a` [104], `4375450b39` [105], `3d56c1f3f9` [106]: test/fixture and
   inventory expectation fixes only.

Engine notes: `MigrationRule Version` 0.0.86 and Managed ABI 9 unchanged; no
persisted-data or wire change. Rebuild every native role, regenerate metadata
and rebake together.

## Project consumer analysis (baseline)

- `rg` over `SourceExt` and `Scripts` for `checked_*<`, consuming `FileReader`
  names, `FrameCollection`/`.Dirs`, buffer accessors, `GetLightData`/`SetLight`:
  no hits. Compiler remains the proof for record-to-free-function moves.

## Steps and acceptance

- [x] Inspect both repositories, fetch upstream, read changelog/migrations.
- [x] Fast-forward Engine `master` to `3d56c1f3f9`.
- [x] Reconfigure (`cmake --preset auto`), build all native targets warning-free.
- [x] Force a complete bake; warning-free.
- [x] Execute `Verify :: All` leaves; inspect COMPLETE counts, exit codes and
  runtime exceptions.
- [x] Review final diff, configuration preservation, docs impact; record
  results and qualification limits.

## Verification record

Evidence root: ignored `Workspace/engine-update-20261104/`.

Engine advanced `ac37c9d217 → 3d56c1f3f9` (fast-forward, clean). Committed and
index pins remain `ac37c9d217`; working-tree gitlink is the new revision,
intentionally unstaged.

`cmake --preset auto`: exit 0, no warnings. `ForceBakeResources`: exit 0
(14:32–14:48), "Baking complete!", no warnings. Builds (RelWithDebInfo), each
exit 0 with no compiler warnings: `TLA_Server`, `TLA_ServerHeadless`,
`TLA_Client`, `TLA_Mapper`, `TLA_ASCompiler`, `TLA_UnitTests`. No project source,
config or script change was needed: the record-to-free-function, `checked_*`,
reader-rename and buffer-accessor migrations do not touch `SourceExt`.

Executed checks:

- `TLA_UnitTests.exe`: exit 0, "All tests passed (747463 assertions in 809 test
  cases)". The logged `GlobalSettingsGroup_Android_GradleDependency` AngelScript
  error comes from an expected-failure case inside the passing suite.
- `TLA_ServerHeadless.exe --ApplySubConfig LocalTest --Testing.Enabled True`:
  exit 0, `COMPLETE: 128 passed, 0 failed, 0 skipped (of 128)`, clean shutdown.
- Script quality ratchet (no new violations), nullable markers `--check`,
  nullable validator test, placement and coverage, `pytest Tools` (220 passed,
  89 subtests), `Format :: Scripts/Prototypes/Main Config`: all exit 0; the
  formatters changed nothing.
- `git diff --check` clean; Engine worktree clean.

Resulting diff: `Engine` gitlink `ac37c9d217 → 3d56c1f3f9` (working tree only;
committed and index pins remain `ac37c9d217`) and `VERSION` `0.3.18 → 0.3.19`
(bake-generated, as in earlier Engine updates), plus this plan.

Qualification limits: Windows x64 MSVC only; no GUI/visual player route, Linux
build or restart-persistence run was performed. `Verify :: All` leaves were run
individually (same commands, same order apart from the earlier forced bake).
