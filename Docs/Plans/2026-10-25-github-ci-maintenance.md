# GitHub native unit-test job maintenance

## Scope and decision

The user requested GitHub maintenance and excluded private repositories. This plan covers only the public TLA unit-test CI job and its owning guide. Preserve project HEAD baseline `3465ebccb62d97c4f0c79dee53b8f4dc90688c9d` and Engine pin `af0770a5ef98ef31fa57c448f27ed4ce3fa86ee4`; no runtime, script, content, version, Engine or release changes.

The existing job calls Engine's standalone validation scaffold. That scaffold omits required `FO_APP_ICON`, so [the observed CI run](https://github.com/cvet/fonline-tla/actions/runs/40136318484) aborts before tests. TLA already declares `Resources/TLA.ico`, enables `FO_UNIT_TESTS`, registers `SourceExt/TestDialogs.cpp`, and exposes `RunUnitTests`.

Use the pinned Engine's existing project build entry point: `Engine/BuildTools/build.sh linux unit-tests Release`. Its verified `configure_build` uses `FO_PROJECT_ROOT`, and `resolve_configure_build_dir` produces `Workspace/build-linux-unit-tests-Release`. Execute that configuration's `RunUnitTests` target with two build workers. Keep the existing dependency preparation.

## Files

- `.github/workflows/build.yml`: replace standalone validation with project test build and execution.
- `Docs/BuildAndLaunch.md`: document the project-native CI route and frozen Engine behavior.
- This plan: preserve verification and residual limits.
- Logs and qualification helpers: ignored `Workspace/github-maintenance/`.

## Acceptance and progress

- [x] Read public project AGENTS.md, build owner, workflow, presets, CMake source, and pinned Engine CLI/directory owners. Pinned/current Engine instruction blobs match.
- [x] Establish source-backed RED: failing CI stops at missing icon in generic scaffold; actual TLA CMake has its own required icon.
- [x] Implement the two existing CLI calls without changing Engine or project options.
- [x] Exercise the affected Linux route in the available Ubuntu WSL environment using an isolated exact-revision source snapshot; retain compile/runtime results and any missing prerequisite.
- [x] Check YAML, diff, required job dependencies and root/Engine revision equality.
- [x] Update this plan with actual results and retain a reviewable local patch. No staging, commit, push, merge or publication.

## Actual verification

- Ubuntu WSL2, Clang 20.1.2: the exact proposed project build route completed with exit 0 and no compiler warnings. No new system packages were required.
- The generated `RunUnitTests` target completed with exit 0: 651 test cases and 735018 assertions passed.
- The linked `TLA_UnitTests` binary also executed `Dialog*`: all four project cases and 20 assertions passed, proving admission of the registered dialog source.
- The Linux snapshot has the same project/Engine revisions as this worktree. Workflow and build-guide SHA256 values match across snapshots. Engine is clean and the project gitlink remains `af0770a5ef98ef31fa57c448f27ed4ce3fa86ee4`.
- YAML parsing, generated path, package job dependency and `git diff --check` passed. Only the workflow, owning guide and this plan changed; staging is empty.
- Logs: ignored `Workspace/github-maintenance/tla-linux-project-build.log`, `tla-linux-project-tests.log`, `tla-linux-unit-tests-full.log` and `tla-linux-dialog-tests.log`.
- A complete local patch/source bundle is retained outside the repository with baseline, exact-file hashes and patch-application proof.

Local Linux success does not establish a remote GitHub Actions result or the complete platform matrix. No gameplay, visual, performance or release qualification is claimed. The original missing-icon CI failure remains separate evidence; no failed native attempts were replaced by the passing run.
