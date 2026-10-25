# FOnline Tools build bootstrap plan

**Goal:** Make project bake/build/launch tasks work when `Build/Auto` has not
been configured, including a fresh checkout or a locally removed build tree.

**Architecture:** FOnline Tools invokes the workspace's existing VS Code tasks.
Add one workspace-root `cmake --preset auto` task and make every direct CMake
build task depend on it. Existing prepare/launch chains inherit the prerequisite.
Keep the current targets, configurations, output paths and Engine revision.

**Owners:** `.vscode/tasks.json`, `CMakePresets.json`, `CMakeLists.txt`,
`Docs/BuildAndLaunch.md`; FOnline Tools task dispatch in
`Engine/BuildTools/fonline-tools/src/extension.ts` is inspected, not modified.

## Constraints and review focus

- Stay on project/Engine `master`; preserve all existing changes and settings.
- Do not stage, commit, publish, install extensions or move the Engine gitlink.
- Configure from the workspace root, including when VS Code's active file changes.
- Cover direct bake, force bake, script compile and native build entry points;
  retain Debug/RelWithDebInfo arguments and existing prepare/launch ordering.
- A configuration failure must stop dependent tasks through VS Code dependencies.
- Do not overlap bake consumers/writers. Keep private evidence under
  `Workspace/fonline-tools-bootstrap-20261025/`.
- This is a predetermined task-configuration edit; Codex applies and checks the
  bounded transform directly. No additional worker or private validator framework
  is needed for the remaining small change.

## Steps and acceptance

- [x] Inspect checkout, root/Engine revisions, tasks, preset, dispatch and docs.
  Both repositories initially clean on `master`; committed Engine pin equals
  Engine HEAD `4588149fa4e4493ed6dddfea0a2fdf65d17c1f3e`.
- [x] Establish cause: the whole `Build/` tree and `Binaries/` are absent;
  all 12 direct build tasks invoke `cmake --build` without configuring first.
- [x] Save the original failing command and task configuration.
- [x] Add `Configure :: Auto`, wire the 12 direct build tasks, update owning docs.
- [x] Check JSON, dependency resolution/cycles, unchanged build arguments and
  inherited configure ordering for prepare/start/launch tasks.
- [x] Run configuration and the original `BakeResources` command to completion;
  inspect diagnostics, then build `TLA_Server` as required by `Start Game`.
- [x] Run the exact `Start Game [sort:1]` command with `LocalTest` after its
  prerequisites and inspect actual startup. The owner explicitly requested this
  end-to-end entry point, rather than stopping at `Configure :: Auto`.
- [x] Review final diff, documentation, index and root/Engine revisions; record
  actual checks and any limitations below.

## Verification results

- Original command reproduced `Build/Auto is not a directory` before changes.
- JSON parsed; all dependency labels resolve without cycles. All 12 direct build
  tasks configure first. Removing only the added task/dependencies produces the
  exact original JSON structure; existing launch/build arguments are preserved.
- The actual VS Code FOnline Tools menu displays `Configure` > `Auto` without an
  extension reload. Computer Use was stopped with Escape; no further UI actions
  are planned in this turn.
- Initial `cmake --preset auto` passed with exit 0, Visual Studio 18 2026/MSVC;
  configuration took 489.4 s and generation 26.9 s. No configure diagnostics.
- The original `BakeResources` command passed with exit 0; terminal
  `Baking complete!`, including Scripts, Protos and Maps. No compiler/bake
  diagnostics were found. Baker's resource work took 65 seconds, after the
  initial native dependency build.
- Repeated configure passed (6.9 s configure, 5.0 s generate). The native
  `TLA_Server` build passed with exit 0, including its BakerLib runtime copy.
  Completed configure/bake/server-build logs contain no warnings/errors.
- The exact command read from `Start Game [sort:1]` was launched with `LocalTest`,
  repository-root cwd and no runtime overrides. PID 38844 has a responding visible
  `Server` window and owns TCP port 4008. The fresh log reached
  `Start server complete!` at 13:53:10 local time; stderr is empty and no runtime
  warnings/errors were found. The window is intentionally left open for the owner.
- `git diff --check` passed in both repositories; index is unchanged. Root remains
  `4d29844824072376670b9195cfab139c85e71436`, Engine remains on `master` at its
  matching committed gitlink. Engine and `TLA.fomain` are unchanged. Only tasks,
  this plan and the owning build guide were edited; no staging/commit/publication.
- Qualification covers task dependencies, actual configure/bake/server build and
  the exact Start Game command's successful server startup. Player login/gameplay
  and a clean shutdown were not exercised; the server remains running for use.
- Owner clarification: acceptance must cover `Start Game`; a successful configure
  alone is not acceptance. No separate standalone client build is required by
  that task, whose server links the embedded client runtime.
- Private evidence: `Workspace/fonline-tools-bootstrap-20261025/`.
