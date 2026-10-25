# Build, launch and verification

Read [AGENTS.md](../AGENTS.md) for authority and scope. Exact local commands live in
[tasks.json](../.vscode/tasks.json), toolchains in [CMakePresets.json](../CMakePresets.json),
target wiring in [CMakeLists.txt](../CMakeLists.txt). Verify names before use.

## Configure and build

Use Git with the Engine submodule, a working Python 3, CMake that understands the
checked-in presets, and the selected C++ toolchain. The project's CMake minimum
alone does not establish support for the newer preset schema. Engine dependency
setup is documented in [BuildTools](../Engine/BuildTools/README.md).

On Windows verify `py -3 --version`; on other hosts verify `python3 --version`.
Do not assume an executable named `python` is the intended interpreter. Use UTF-8
for Cyrillic source, logs and reports. Initialize Engine explicitly:

```sh
git submodule update --init --recursive Engine
cmake --preset auto
cmake --build Build/Auto --config RelWithDebInfo --target BakeResources
cmake --build Build/Auto --config RelWithDebInfo --target TLA_Server
cmake --build Build/Auto --config RelWithDebInfo --target TLA_Client
```

Other presets cover MSVC 2022/2026, ClangCL, Clang, GCC, Xcode, Emscripten and
Android NDK; their conditions and environment variables are in the preset file.
`auto` uses `Build/Auto`. Binaries are under `Binaries/<role>-<platform>-<arch>/`;
baked data is in `Baking/`, cache in `Cache/`. These are outputs, as are package
trees such as `TLA-Dev/`, not canonical authored inputs.

FOnline Tools runs the workspace's VS Code tasks. Every direct bake, script
compile and native build task first runs `Configure :: Auto` from the workspace
root (`cmake --preset auto`). Prepare and launch tasks inherit that prerequisite,
so they also work before the first configuration or after removing `Build/Auto`.
Configuration errors stop the dependent task. Direct terminal commands still
require the explicit configure step shown above.

| VS Code task | Purpose |
| --- | --- |
| `Configure :: Auto` | Configure `Build/Auto` with the `auto` preset; prerequisite of all CMake build tasks. |
| `Bake Resources` / `Force Bake Resources` | Incremental bake / deliberately ignore incremental state. See [content workflow](ContentWorkflow.md). |
| `Compile AngelScript` | Fast script syntax/API check; CMake target `CompileAngelScript`. |
| `Build :: TLA_*` | Build the named target: Server, ServerHeadless, Client, Mapper, Baker, ASCompiler or UnitTests. Verify the task exists; a CMake target need not have a VS Code task. |
| `Prepare :: TLA_*` | Bake, then build the selected application. |
| `Launch :: TLA_Server [windows]` / `[linux]` | Prepare and run the GUI server with `LocalTest`. |
| `Launch :: TLA_UnitTests [windows]` / `[linux]` | Prepare, then execute native tests. Building the executable alone does not run them. |
| `Launch :: TLA_Tests [windows]` | Prepare ServerHeadless, then run the AngelScript harness with `Testing.Enabled=True`. |
| `Generate :: GuiScreens.fos` | Python GUI generator; [ownership and regeneration](ContentWorkflow.md#gui-generation). |
| `Generate :: Version` | `Tools/GenerateVersion/generate_version.py`; never hand-edit `VERSION`. |
| `Format :: Scripts` | Project formatter for scripts, SourceExt and embedded `.fogui` code. |
| `Format :: Prototypes` / `Format :: Main Config` / `Format :: All` | Format the selected authored inputs. |
| `Analyze :: Script Quality (Ratchet)` | No new violations against the existing baseline. |
| `Analyze :: Nullable All` | Script markers, focused validator tests, ABI/handler parity and coverage. |
| `Test :: Python Tools` | `py -3 -m pytest Tools -q`. |
| `Verify :: All` | Sequential full local integration chain below. |

## Select verification by the change

Compiler, baker and native build warnings are failures. Fix their owner; do not
suppress diagnostics or raise a baseline to obtain a pass. Script-quality
heuristics have an existing backlog governed by their [ratchet](../Tools/ScriptQuality/README.md);
that is distinct from compiler warnings.

| Change | Required route |
| --- | --- |
| Documentation/instructions only | Verify claims against source; inventory links/anchors, structure, size and preservation; `git diff --check`. No native build/bake solely for prose. |
| Script or content | Compile affected Server/Client/Mapper roles, bake, owning validators and behavioral tests; build affected applications. |
| Server behavior | Above plus ServerHeadless startup to `Start server complete!`, clean logs and focused gameplay assertions. |
| GUI/input/rendering | Owning `.fogui` and generated output, compile/bake/client build, ordinary visible interaction; bridge/static tests alone do not prove it. |
| Native/binding/baker | Affected targets, build **and run** `TLA_UnitTests` when covered, owning contract/nullable tests; bake after baker/input changes. |
| Engine bump or broad integration | `Verify :: All`, matching client/server resources, startup and affected ordinary player paths. |
| Packaging/platform/CI | Exercise the real affected package/runner/platform; do not extrapolate Windows evidence. |

`Verify :: All` currently runs bake; builds Server, ServerHeadless, Client, Mapper,
ASCompiler and UnitTests; executes native tests and the script harness; runs the
script-quality ratchet, nullable chain, Python tools and `Format :: All`.
It does not itself exercise ordinary GUI play or every package/platform, and is a
VS Code task, not a CMake target. If its final formatting changes source, inspect
the diff and repeat affected checks on the formatted result.

CI in [build.yml](../.github/workflows/build.yml) has separate jobs for validation,
quality gates, native tests, script compilation, baking, platform builds, packages
and release. It is **not** the same chain: the script gameplay harness is not wired
into CI. Local success does not prove a remote CI run succeeded.

## Local runtime and tests

The base config uses localhost, port `4008`, English client text and **Memory**
storage. `LocalTest` additionally sets `ServerNetwork.LoginTimeout=0`; it is not an
empty profile. `Unpackaged` adds development overrides (music, artificial lag,
render debug and timeouts). Inspect [TLA.fomain](../TLA.fomain) rather than copying
all defaults into another reference.

```powershell
.\Binaries\Server-Windows-win64\TLA_ServerHeadless.exe --ApplySubConfig LocalTest
.\Binaries\Client-Windows-win64\TLA_Client.exe --ApplySubConfig LocalTest
```

On Linux use the corresponding `Binaries/Server-Linux-x64/` and
`Binaries/Client-Linux-x64/` executables. Run from the repository root. Debug
profiles are in [launch.json](../.vscode/launch.json), including `Attach :: FOS`.
For iterative automation use a persistent **process** plus a separate windowed
client as described in [AiControl](AiControl.md#running-it-locally). Memory DB
contents survive client reconnects but disappear when the server exits.

For restart/persistence validation, select an enabled persistent provider and an
isolated writable DB/cache/log root under `Workspace/<task-id>/`; verify actual
stored state and ordinary login after restart. Never silently change the owner's
default `Server.DbStorage` or transport settings to make a test convenient.
The Noise key/pin and `PublicGame` requirements are in
[ContentWorkflow](ContentWorkflow.md#configuration-and-secure-channel).

The harness owner is [Scripts/Testing.fos](../Scripts/Testing.fos), with suites in
`Scripts/Tests/`. Run all suites through the launch task, or add
`--Testing.Enabled True --Testing.Filter <SuiteOrTestSubstring>` to ServerHeadless.
`Testing.Filter` is a substring of `Suite.Name`, not a regex. Read the terminal
`[Testing] COMPLETE: ...` counts, expected exercised tests, failures/skips/timeouts,
exit code and runtime diagnostics. A partial PASS list or a no-match filter is
not a successful behavioral check. See [AiControl validation](AiControl.md#validation)
for MCP/static/screenshot and quest routes.

## Process ownership and evidence

Do not overlap baking with another writer or a runtime consuming that bake. Check
executable path, command line, output roots and ownership before stopping anything.
Never kill all processes by image name or delete a lock merely because it exists.
Stop only the task-owned tree, wait for exit and verify cleanup. Reusable bake
ownership: [Engine baking](../Engine/Docs/en/explanation/content-pipeline/baking.md).

A normal GUI smoke ends through the application's close/quit path with exit code
0. Forced termination is cleanup, not clean-session acceptance. Retain the original
failed run when a controlled rerun passes; record the changed condition and exact
source revision. Separate focused/full-suite, runtime, persistence, performance,
platform and publication evidence. Startup alone does not prove a quest, cursor,
animation or rendering path. Never lower a check to hide a timing-sensitive failure.

## Diagnose at the failing boundary

| Symptom | Start with | Evidence |
| --- | --- | --- |
| Script syntax/API | `Compile AngelScript` | `TLA_ASCompiler.log`, `Build/_errors.txt` |
| Bake/dialog/map/proto/text | `Bake Resources` | `TLA_Baker.log`, `TLA_BakerLib.log`, `Build/_bake.log`, `Build/_errors.txt` |
| Native compile/link | Narrowest affected target | First compiler/linker error and full target output |
| Server startup | ServerHeadless with `LocalTest` | `TLA_ServerHeadless.log`, `TLA_Server.log` |
| Client presentation/input | Matching server and client | `TLA_Client.log`, fresh screenshots and visible action |
| Mapper | Build/run Mapper | `TLA_Mapper.log` |
| Native regression | Current Engine range and tests | `TLA_UnitTests.log`, original failure and controlled rerun |

Default logs are written at repository root; explicit isolated runtime roots can
redirect them. Save task-specific copies and reports under `Workspace/<task-id>/`.

## CI packages and release

`DefinePackage` in CMake owns the combinations: `Dev` contains Windows win64
server/client/mapper and BakerLib; `Test` profiling client/server; `LinuxTest`
Linux x64 client/server/mapper. Do not list Editor as a shipped payload merely
because `FO_BUILD_EDITOR` is enabled.

The workflow collects baked output and binaries into `TLA-Dev`, `TLA-Test` and
`TLA-Release` artifacts. Release bundles are `TLA-Dev.zip`, `TLA-Server.zip` and
`TLA-Client.zip`; oversized archives become `.zip.partNN` and must be concatenated
in order before extraction. On Linux/macOS use `cat TLA-Server.zip.part* >
TLA-Server.zip`; on Windows use `copy /b` with the explicitly ordered part list.

Releases are published only by a manual run. In GitHub, open **Actions** > **build** >
**Run workflow**, select `master`, and run it. The workflow must be present on the
repository's default branch before the **Run workflow** control is available; the
selected ref supplies the revision that runs. Automatic `push` and `pull_request`
runs execute all checks, platform builds and packaging, and upload their CI
artifacts. Only the release job is skipped; publishing a GitHub release is manual.

A manual run on `master` validates `VERSION` as `X.Y.Z`, rejects an existing
`vX.Y.Z` tag, and publishes only after all checks pass, including the quality gates.
Manual runs on other refs build and package but perform the existing dry-run
preflight: an existing tag is reported without publishing, asset sizes/hashes are
recorded and no tag or release is created. Use the version generator and inspect
its result; preparing a package or version does not authorize publication.
