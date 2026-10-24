# FOnline: The Life After

[![Build](https://github.com/cvet/fonline-tla/workflows/build/badge.svg)](https://github.com/cvet/fonline-tla/actions)
[![License](https://img.shields.io/github/license/cvet/fonline-tla.svg)](LICENSE)
[![Site](https://img.shields.io/badge/site-tla.fonline.ru-blue.svg)](https://tla.fonline.ru)

**FOnline: The Life After** (TLA) is a multiplayer post-apocalyptic isometric RPG
built on the reusable [FOnline engine](https://github.com/cvet/fonline). The game
contains a persistent-world design, Fallout-style hex maps, quests, dialogs,
combat, trade, crafting, world-map encounters and client/editor tooling.

This is the human-facing entry point. AI maintainers read [AGENTS.md](AGENTS.md)
before changing files. The complete [documentation index](Docs/README.md) routes
to current procedures, references and dated plans.

## Play

Download the client from [Releases](https://github.com/cvet/fonline-tla/releases)
and run `TLA_Client.exe` on Windows. Bundles include `TLA-Client.zip`,
`TLA-Server.zip` and the Windows development package `TLA-Dev.zip`. Large bundles
may be split into `.zip.partNN`; concatenate **all** ordered parts before
extracting. [Package details](Docs/BuildAndLaunch.md#ci-packages-and-release)
explain assembly and release preflight. Branch/PR CI artifacts are temporary.

Project site: [tla.fonline.ru](https://tla.fonline.ru); repository:
[cvet/fonline-tla](https://github.com/cvet/fonline-tla); project scripting API:
[SCRIPTING_API](https://tla.fonline.ru/SCRIPTING_API); maintainer: <cvet@tut.by>.

## Build from source

Install Git, Python 3, CMake compatible with the checked-in presets and a C++
toolchain. Engine's [workspace setup](Engine/BuildTools/README.md) owns dependency
preparation; [CMakePresets.json](CMakePresets.json) lists host/target requirements.
`auto` is the default local preset, with output in `Build/Auto`.

```sh
git clone --recurse-submodules https://github.com/cvet/fonline-tla.git
cd fonline-tla
cmake --preset auto
cmake --build Build/Auto --config RelWithDebInfo --target BakeResources
cmake --build Build/Auto --config RelWithDebInfo --target TLA_ServerHeadless
cmake --build Build/Auto --config RelWithDebInfo --target TLA_Client
```

For an existing non-recursive checkout, initialize Engine explicitly with
`git submodule update --init --recursive Engine`. Let cloning finish before
opening IDE Git automation against the destination. An interrupted clone should
be inspected before deleting downloaded objects or restarting into the same path.

Presets also cover MSVC 2022/2026, ClangCL, Clang, GCC, Xcode, Emscripten and
Android NDK. A configure preset or build matrix entry does not prove runtime
qualification for that platform. TLA selects AngelScript and 2D hex geometry;
Managed C# scripting and 3D are disabled by the project's default options.

## Run a local shard

From the repository root on Windows:

```powershell
.\Binaries\Server-Windows-win64\TLA_ServerHeadless.exe --ApplySubConfig LocalTest
```

Wait for `Start server complete!`, then run the matching client:

```powershell
.\Binaries\Client-Windows-win64\TLA_Client.exe --ApplySubConfig LocalTest
```

On Linux use `Binaries/Server-Linux-x64/TLA_ServerHeadless` and
`Binaries/Client-Linux-x64/TLA_Client`. For a GUI server use `TLA_Server` with the
same subconfig. `LocalTest` keeps the base localhost/port `4008` configuration
and disables the login timeout. The default DB is **Memory**: it survives client
reconnects, not a server restart. Restart tests need an explicitly selected
persistent provider and isolated storage.

The default client language is English; resources bake `russ engl`. Every network
connection uses a Noise channel. The base development key pair is intentionally
public for local use; `PublicGame` requires its host-owned secret and an issued
client pin. [Configuration and secure channel](Docs/ContentWorkflow.md#configuration-and-secure-channel)
describe that boundary. Preserve owner-selected defaults when testing.

## Develop and verify

Use [.vscode/tasks.json](.vscode/tasks.json) for exact local task names and
[launch.json](.vscode/launch.json) for debug profiles. [BuildAndLaunch](Docs/BuildAndLaunch.md)
owns build/launch/test commands, failure logs, process cleanup, platform limits
and CI/package behavior. Important entry tasks:

| Task | Use |
| --- | --- |
| `Compile AngelScript` | Script syntax/API checks. |
| `Bake Resources` / `Force Bake Resources` | Update resources / deliberately rebuild stale or incompatible output. |
| `Build :: TLA_*` / `Prepare :: TLA_*` | Build an application / bake and build. |
| `Launch :: TLA_Tests [windows]` | Run the project gameplay script harness. |
| `Launch :: TLA_UnitTests [windows]` / `[linux]` | Build and execute native tests. |
| `Generate :: GuiScreens.fos` | Generate GUI bindings from `.fogui`. |
| `Format :: All` | Format authored inputs; review any changes before final checks. |
| `Verify :: All` | Full local integration chain, including validators and tooling tests. |

Compiler/baker/build warnings are failures. Use focused checks while editing and
the full chain for broad integration. A compiled test executable is not a test
run, and a headless startup is not GUI/gameplay acceptance. Verify the ordinary
player action and persistence where relevant. CI uses its own jobs; it does not
yet run the script gameplay harness. Do not infer a release from a local pass.

## Repository and ownership

| Path | Owner/purpose |
| --- | --- |
| `Engine/` | Pinned reusable engine submodule; [Engine entry](Engine/README.md), [docs](Engine/Docs/en/index.md). |
| `Scripts/*.fos` | Hand-written AngelScript gameplay; [Systems](Docs/Systems.md) maps domains and entrypoints. |
| `Scripts/Core/`, `Json/`, `Tests/` | Project utility library, JSON helpers and harness suites. |
| `Scripts/Content.fos` | Generated content declarations. |
| `Scripts/Generated/GuiScreens.fos` | Generated screen bindings; source is `Gui/*.fogui` plus the Python generator. |
| `Scripts/GuiScreensExt.fos` | Hand-written GUI companion. |
| `SourceExt/` | Project C++ hooks, dialog baker/runtime, SHA and client automation bridge; [NativeExtensions](Docs/NativeExtensions.md). |
| `Gui/`, `Dialogs/`, `Maps/`, `Critters/`, `Items/`, `Texts/`, `Resources/` | Authored content and assets; [ContentWorkflow](Docs/ContentWorkflow.md). |
| `TLA.fomain` | Runtime/bake config, subconfigs and resource packs. |
| `CMakeLists.txt`, `CMakePresets.json` | Build options, source roles, packages and toolchains. |
| `Tools/` | Supported formatters, generators, validators and AI-control/playtest tools. |
| `Binaries/`, `Baking/`, `Cache/`, `Build/`, `TLA-Dev/` | Generated/debug outputs; never canonical authored inputs. |
| `Workspace/<task-id>/` | Ignored task-specific evidence and intermediates. |

The content route is `.fogui` → `Scripts/Generated/GuiScreens.fos`, then authored
inputs plus generated scripts → bake → matching applications. Script directories
must be listed explicitly in **both** metadata and script packs; baking does not
recurse. Detailed [generation rules](Docs/ContentWorkflow.md#gui-generation)
include the narrow paired-source exception. Never patch generated content,
baked/cache output or `VERSION` in place of its owner.

## Contribute

Keep changes focused and send PRs against `master`. Game policy belongs to TLA;
generic capability belongs to Engine. Read [Scripts](Docs/Scripts.md), Russian
[ScriptStyle](Docs/ScriptStyle.md) and [Nullability](Nullability.md) before script
changes. Do not copy another game's serialized names or migrate TLA to C# merely
because its engine supports that backend. Keep expected English/Russian content
surfaces together and register new native files in CMake.

Update owning docs with behavior and use the checks in
[BuildAndLaunch](Docs/BuildAndLaunch.md#select-verification-by-the-change).
Engine updates follow [revision reconciliation](Docs/DocumentationMaintenance.md#engine-submodule-updates).
Maintainer/agent Git action authority is defined in [AGENTS.md](AGENTS.md).

## License

Source code uses the [MIT License](LICENSE). The repository also contains
third-party dependencies and game data packs; check their licenses and asset
rights before redistributing derived packages.
