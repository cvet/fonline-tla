# FOnline: The Life After

[![Build](https://github.com/cvet/fonline-tla/workflows/build/badge.svg)](https://github.com/cvet/fonline-tla/actions)
[![Last commit](https://img.shields.io/github/last-commit/cvet/fonline-tla.svg)](https://github.com/cvet/fonline-tla/commits/master)
[![License](https://img.shields.io/github/license/cvet/fonline-tla.svg)](LICENSE)
[![Site](https://img.shields.io/badge/site-tla.fonline.ru-blue.svg)](https://tla.fonline.ru)

**FOnline: The Life After** (TLA) is a multiplayer post-apocalyptic isometric RPG built on the reusable [FOnline engine](https://github.com/cvet/fonline). It is a large, playable game project with a persistent world, Fallout-style hex maps, quests, dialogs, critters, items, factions, world-map encounters, client UI, editor tooling, and cross-platform build automation.

The repository is split into a pinned engine submodule plus TLA-specific game content:

- `Engine/` is the reusable FOnline engine, consumed as a git submodule.
- `Scripts/*.fos` contains AngelScript gameplay and client/server behavior.
- `SourceExt/*` contains TLA-native C++ extension hooks and exported script methods.
- `Maps/`, `Dialogs/`, `Critters/`, `Items/`, `Texts/`, `Gui/`, and `Resources/` contain authored game data and assets.
- `TLA.fomain` is the main game configuration, resource baking definition, and subconfig registry.

This README is the human-facing project overview. If you are an AI coding agent, read [AGENTS.md](AGENTS.md) before changing files.

## Contents

- [Quick Links](#quick-links)
- [Project Snapshot](#project-snapshot)
- [Playing](#playing)
- [Building From Source](#building-from-source)
- [Running A Local Shard](#running-a-local-shard)
- [Common Build Targets](#common-build-targets)
- [VS Code Workflow](#vs-code-workflow)
- [Repository Layout](#repository-layout)
- [Content Pipeline](#content-pipeline)
- [Gameplay Scripting](#gameplay-scripting)
- [Native Extensions](#native-extensions)
- [Configuration](#configuration)
- [Verification Guide](#verification-guide)
- [Troubleshooting](#troubleshooting)
- [CI And Packaging](#ci-and-packaging)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Quick Links

| Resource | Link |
| -------- | ---- |
| Website | <https://tla.fonline.ru> |
| Repository | <https://github.com/cvet/fonline-tla> |
| Releases | <https://github.com/cvet/fonline-tla/releases> |
| Engine repository | <https://github.com/cvet/fonline> |
| TLA scripting API | <https://tla.fonline.ru/SCRIPTING_API> |
| Engine public API | [Engine/PUBLIC_API.md](Engine/PUBLIC_API.md) |
| Engine tutorial | [Engine/TUTORIAL.md](Engine/TUTORIAL.md) |
| Maintainer contact | <cvet@tut.by> |

## Project Snapshot

The repository contains a full game corpus, not only a code sample. Current authored inputs include:

| Content | Source files |
| ------- | ------------ |
| AngelScript modules (`Scripts/**/*.fos`) | 260 |
| Dialog packs (`Dialogs/*.fodlg`) | 884 |
| Maps (`Maps/*.fomap`) | 275 |
| Location protos (`Maps/*.foloc`) | 136 |
| Critter protos (`Critters/*.focr`) | 635 |
| Item/proto files (`Items/*.foitem`, `Items/*.fopro`) | 4,688 |
| GUI screens (`Gui/*.fogui`) | 32 |
| Localized text packs (`Texts/*.fotxt`) | 12 |

Important project characteristics:

- Client and server are built from source together with the engine.
- Gameplay is implemented primarily in AngelScript.
- TLA uses hexagonal Fallout-style map geometry (`FO_GEOMETRY HEXAGONAL`, 32x16 hexes).
- The default client language is English; resources are baked for Russian and English (`russ engl`).
- Baked resources, caches, logs, and binaries are generated locally and are not the authoritative source of game content.
- The engine submodule is actively shared with other FOnline projects. Treat it as upstream unless a task explicitly requires an engine change.

## Playing

Tagged releases publish long-lived downloadable packages on the [GitHub Releases](https://github.com/cvet/fonline-tla/releases) page:

- `TLA-Client.zip` - client package for connecting to a configured server.
- `TLA-Server.zip` - server package with baked resources for hosting a shard.
- `TLA-Dev.zip` - development package with multiple Windows tools.

On Windows, unpack the client package and run `TLA_Client.exe`. The project website is [tla.fonline.ru](https://tla.fonline.ru).

Short-lived CI artifacts are also produced by GitHub Actions for branches and pull requests, but release archives are the stable distribution channel.

## Building From Source

Building from source is the normal workflow for development, modding, local shards, engine updates, and platforms not covered by release archives.

### Prerequisites

Minimum common tools:

- Git with submodule support.
- CMake 3.22 or newer.
- Python 3 for generation and formatting scripts.
- A C++ toolchain for your host or target platform.

Supported configure presets are defined in [CMakePresets.json](CMakePresets.json):

| Preset | Platform/toolchain |
| ------ | ------------------ |
| `auto` | Host-driven default, outputs to `Build/Auto`. This is what local tasks use. |
| `msvc2022` | Visual Studio 2022. |
| `msvc2026` | Visual Studio 2026. |
| `clang-cl` | Visual Studio 2022 generator with ClangCL. |
| `clang-cl-2026` | Visual Studio 2026 generator with ClangCL. |
| `clang` | Clang + Ninja Multi-Config on non-Windows hosts. |
| `gcc` | GCC + Ninja Multi-Config on Linux. |
| `xcode` | Xcode generator on macOS. |
| `emscripten` | Web build; requires `EMSDK`. |
| `android-ndk-arm32` | Android armeabi-v7a; requires `NDK_ROOT`. |
| `android-ndk-arm64` | Android arm64-v8a; requires `NDK_ROOT`. |
| `android-ndk-x86` | Android x86; requires `NDK_ROOT`. |

The engine also ships workspace preparation scripts and a broader dependency matrix in [Engine/BuildTools/README.md](Engine/BuildTools/README.md).

### Clone

Use a recursive clone so the engine submodule is present:

```sh
git clone --recursive https://github.com/cvet/fonline-tla.git
cd fonline-tla
```

If the repository was cloned without submodules:

```sh
git submodule update --init --recursive
```

### Configure

For the default local setup:

```sh
cmake --preset auto
```

For an explicit toolchain, choose a preset:

```sh
cmake --preset msvc2022
cmake --preset clang
cmake --preset gcc
```

### Build The Usual Development Targets

The default local build directory is `Build/Auto`; the standard configuration is `RelWithDebInfo`.

```sh
cmake --build Build/Auto --config RelWithDebInfo --target BakeResources
cmake --build Build/Auto --config RelWithDebInfo --target TLA_Server
cmake --build Build/Auto --config RelWithDebInfo --target TLA_Client
```

Built applications are emitted under `Binaries/`, with platform-specific directories such as:

- `Binaries/Server-Windows-win64/`
- `Binaries/Client-Windows-win64/`
- `Binaries/Server-Linux-x64/`
- `Binaries/Client-Linux-x64/`
- `Binaries/Tests-Windows-win64/`
- `Binaries/Tests-Linux-x64/`

## Running A Local Shard

The `LocalTest` subconfig is the intended local development profile. It keeps the client on `localhost` and uses the default project port (`4008`); at the moment it intentionally has no overrides beyond the base config.

Build and bake first:

```sh
cmake --build Build/Auto --config RelWithDebInfo --target BakeResources
cmake --build Build/Auto --config RelWithDebInfo --target TLA_ServerHeadless
cmake --build Build/Auto --config RelWithDebInfo --target TLA_Client
```

Run a Windows server:

```powershell
.\Binaries\Server-Windows-win64\TLA_ServerHeadless.exe --ApplySubConfig LocalTest
```

Run a Linux server:

```sh
./Binaries/Server-Linux-x64/TLA_ServerHeadless --ApplySubConfig LocalTest
```

A successful server startup reaches:

```text
Start server complete!
```

Then start the matching client binary from `Binaries/Client-*`.

For GUI server debugging instead of headless startup, use `TLA_Server` with the same `--ApplySubConfig LocalTest` argument.

## Common Build Targets

| Target | Purpose |
| ------ | ------- |
| `BakeResources` | Incrementally bake scripts, configs, text, dialogs, protos, maps, images, effects, and raw resources. Run after content changes. |
| `ForceBakeResources` | Rebuild baked output while ignoring the incremental cache. Use when cache state is suspicious. |
| `CompileAngelScript` | Fast AngelScript compile/API check without a full native rebuild. |
| `TLA_Server` | GUI-capable game server. Useful for local development. |
| `TLA_ServerHeadless` | Headless game server. Useful for production-like and CI startup checks. |
| `TLA_Client` | Game client. |
| `TLA_Mapper` | Map editing application. |
| `TLA_Editor` | Content/editor application. |
| `TLA_Baker` | Standalone resource baker. |
| `TLA_ASCompiler` | Standalone AngelScript compiler/static checker. |
| `TLA_UnitTests` | Engine unit tests built in this project context. |

Useful command forms:

```sh
cmake --build Build/Auto --config RelWithDebInfo --target CompileAngelScript
cmake --build Build/Auto --config RelWithDebInfo --target TLA_ServerHeadless
cmake --build Build/Auto --config RelWithDebInfo --target TLA_UnitTests
```

## VS Code Workflow

The authoritative local workflow is encoded in [.vscode/tasks.json](.vscode/tasks.json). The most important tasks are:

| Task | Use it when |
| ---- | ----------- |
| `Bake Resources` | You changed `Scripts/`, `Dialogs/`, `Maps/`, `Items/`, `Critters/`, `Texts/`, `Gui/`, `Resources/`, or `TLA.fomain`. |
| `Force Bake Resources` | Incremental baking may be stale. |
| `Compile AngelScript` | You need a quick script syntax/API check. |
| `Build :: TLA_Server` | You changed server-side native code or need a GUI server. |
| `Build :: TLA_ServerHeadless` | You need a production-like server binary. |
| `Build :: TLA_Client` | You changed client native code, GUI, input, rendering, or presentation behavior. |
| `Build :: TLA_Mapper` | You changed mapper-facing code/content. |
| `Build :: TLA_Editor` | You changed editor-facing code/content. |
| `Build :: TLA_Baker` | You changed resource baking code. |
| `Build :: TLA_ASCompiler` | You changed script compiler-facing code. |
| `Build :: TLA_UnitTests` | You changed native engine-facing behavior that is covered by tests. |
| `Prepare :: TLA_*` | Bake resources and then build the selected target. |
| `Launch :: TLA_Server [windows]` / `[linux]` | Prepare and run the local GUI server with `LocalTest`. |
| `Launch :: TLA_UnitTests [windows]` / `[linux]` | Prepare and run unit tests. |
| `Generate :: GuiScreens.fos` | Regenerate script bindings from `Gui/*.fogui`. |
| `Generate :: Version` | Update `VERSION` through `Tools/GenerateVersion/generate_version.py`. |
| `Format :: Scripts` | Format AngelScript, native extensions, and GUI definitions. |
| `Format :: Prototypes` | Format authored prototype files. |
| `Format :: Main Config` | Format `TLA.fomain`. |
| `Format :: All` | Run all formatting tasks. |

Debug launch configurations are in [.vscode/launch.json](.vscode/launch.json). They include Windows and Linux server launches, headless server launches, unit-test launches, and `Attach :: FOS` for the AngelScript debugger extension.

## Repository Layout

| Path | Role |
| ---- | ---- |
| [Engine/](Engine) | Pinned FOnline engine submodule. Keep game behavior outside this directory unless an engine change is explicitly intended. |
| [Scripts/](Scripts) | AngelScript gameplay, AI, dialogs, quests, combat, world-map logic, GUI behavior, and server/client hooks. |
| [Scripts/Json/](Scripts/Json) | JSON helpers used by script code. |
| [Scripts/Content.fos](Scripts/Content.fos) | Generated content declarations. Do not hand-edit. |
| [Scripts/GuiScreens.fos](Scripts/GuiScreens.fos) | Generated GUI screen bindings. Update through `Gui/*.fogui` and the Python generator. |
| [Scripts/GuiScreensExt.fos](Scripts/GuiScreensExt.fos) | Hand-written companion logic for generated GUI screens. |
| [SourceExt/](SourceExt) | Project-local C++ extension layer registered from [CMakeLists.txt](CMakeLists.txt). |
| [SourceExt/SHA/](SourceExt/SHA) | Small bundled SHA library used by common extension helpers. |
| [Gui/](Gui) | GUI screen definitions (`*.fogui`) and the default GUI scheme. |
| [Dialogs/](Dialogs) | Dialog packs (`*.fodlg`) consumed by the baker and runtime dialog support. |
| [Maps/](Maps) | Maps (`*.fomap`) and locations (`*.foloc`). |
| [Critters/](Critters) | Critter prototypes (`*.focr`). |
| [Items/](Items) | Item and prototype data (`*.foitem`, `*.fopro`). |
| [Texts/](Texts) | English and Russian text packs (`*.fotxt`). |
| [Resources/](Resources) | Image, sound, video, raw data, mapper resources, and legacy data packs. |
| [Tools/](Tools) | Formatter, GUI generator, version generator, dialog editor, and helper scripts. |
| [TLA.fomain](TLA.fomain) | Main configuration, subconfigs, bake languages, and resource pack definitions. |
| [CMakeLists.txt](CMakeLists.txt) | TLA build options, native extension registration, package definitions, and generation stage order. |
| [CMakePresets.json](CMakePresets.json) | Configure/build preset matrix. |
| [.vscode/tasks.json](.vscode/tasks.json) | Canonical local build/generate/format tasks. |
| [.github/workflows/build.yml](.github/workflows/build.yml) | CI, package, and release workflow. |
| [AGENTS.md](AGENTS.md) | Maintainer and AI-agent working rules. |
| [CLAUDE.md](CLAUDE.md) | Pointer to `AGENTS.md`. |
| [Binaries/](Binaries) | Generated binaries. |
| [Baking/](Baking) | Generated baked output. |
| [Cache/](Cache) | Generated bake cache. |
| [Build/](Build) | Generated build directories. |
| [TLA-Dev/](TLA-Dev) | Local package/output tree. |

Generated output directories are useful for debugging, but authored changes should be made in the source directories above.

## Content Pipeline

TLA uses the FOnline baking pipeline. Authored data is transformed into runtime-ready resources before server/client startup.

High-level flow:

```text
Gui/*.fogui
  -> Tools/InterfaceEditor/generate_gui_screens.py
  -> Scripts/GuiScreens.fos

Scripts + Texts + Dialogs + Maps + Critters + Items + Resources + TLA.fomain
  -> BakeResources / ForceBakeResources
  -> Baking/ + resource packs
  -> Binaries/* consume baked data at runtime
```

The resource packs are defined in [TLA.fomain](TLA.fomain). The major packs are:

| Pack | Inputs | Purpose |
| ---- | ------ | ------- |
| `Metadata` | `Scripts`, engine core scripts | Metadata generation. |
| `Configs` | Project configuration | Server-only baked config data. |
| `Scripts` | `Scripts`, `Scripts/Json`, engine AngelScript core scripts | Gameplay script bytecode/data. |
| `Embedded` | Engine embedded resources | Engine images/effects/raw resources. |
| `Core` | Engine core and embedded resources | Shared engine resources. |
| `Texts` | `Texts`, `Maps`, `Critters`, `Items`, `Dialogs` | Text packs, proto text, dialog text. |
| `CommonData` | `Resources/CommonData` | Shared raw data. |
| `ServerData` | `Resources/ServerData`, `Dialogs` | Server-only dialogs/images/raw data. |
| `FOnline` | `Resources/FOnline` | Client image resources. |
| `FOArt` | `Resources/DataPacks/fo_art*.zip` | Client legacy art resources. |
| `FOSound` | `Resources/DataPacks/fo_sound.zip` | Client sound resources. |
| `Music` | `Resources/FOnlineMusic` | Client music resources. |
| `Video` | `Resources/FOnlineVideo` | Client video resources. |
| `Mapper` | `Resources/Mapper` | Mapper-only resources. |
| `Protos` | `Maps`, `Critters`, `Items` | Proto baking. |
| `Maps` | `Maps` | Map baking. |

### Generated Files

Do not hand-edit these unless the owning source is updated too:

- `Scripts/Content.fos` - generated/baked content declarations.
- `Scripts/GuiScreens.fos` - generated from `Gui/*.fogui`.
- `VERSION` - generated by `Tools/GenerateVersion/generate_version.py`.
- `Baking/`, `Cache/`, `Binaries/`, `Build/`, `TLA-Dev/` - generated outputs.

### GUI Screen Generation

GUI definitions live in `Gui/*.fogui`. Embedded AngelScript can appear inside `.fogui` JSON fields such as callbacks, screen code, global mouse handlers, draw handlers, class fields, and global scope blocks.

The supported generator is:

```sh
py -3 Tools/InterfaceEditor/generate_gui_screens.py --project-root .
```

On Linux:

```sh
python3 Tools/InterfaceEditor/generate_gui_screens.py --project-root .
```

Use the `Generate :: GuiScreens.fos` VS Code task for the same operation.

Do not use `Tools/InterfaceEditor/InterfaceEditor.exe -SilentGenerate` for this project. Its generated layout is not compatible with TLA.

## Gameplay Scripting

Gameplay code is AngelScript (`*.fos`) with FOnline project conventions:

- Each script file declares a namespace matching the file name, for example `Scripts/Combat.fos` uses `namespace Combat`.
- There are no `#include` directives; the baker sees all `.fos` files.
- Cross-module calls use explicit namespaces, for example `Dialog::...` or `Worldmap::...`.
- Server-authoritative behavior belongs under `#if SERVER`.
- Client-only input, UI, and presentation behavior belongs under `#if CLIENT`.
- Mapper-specific logic belongs under `#if MAPPER`.
- Startup functions use `[[ModuleInit]]` and subscribe to events from there.
- Event handlers return `void` for implicit continuation or `EventResult` for explicit chain control.
- `[[TimeEvent]]` and remote callbacks that run on worker threads must be marked `[[Async]]` before using async helpers, and must lock the entity cover they touch. For map-visible critter work, use `Sync::LockCritterWithMap(cr)` before reading or mutating critter/map state.
- Nullable handles are explicit: use `T?` when an engine call or dictionary lookup can return `null`, then narrow before dereferencing.
- Generated component accessors are guarded by `Has<Component>` flags such as `HasRadio` or `HasDialogContext`; do not probe component accessors with `== null`.
- Dialog answer links used by `.fodlg` files, such as `Answer Barter`, require globally visible `///@ Enum DialogAnswerLink ...` metadata so the dialog baker can resolve them.
- TLA assumes a hex grid. Prefer engine/game helpers such as distance, direction, tracing, and pathing APIs over ad hoc rectangular math.

Common script areas:

| Area | Typical files |
| ---- | ------------- |
| Combat and critter state | `Combat.fos`, `CritterState.fos`, `CritterActions.fos`, `CritterTypes.fos` |
| Dialog and quest behavior | `Dialog*.fos`, quest/location-specific scripts |
| World map and encounters | `Worldmap.fos`, `GlobalMap*.fos`, `Encounter*.fos` |
| Client UI and input | `ClientMain.fos`, `GuiScreensExt.fos`, `DropMenuHandler.fos`, screen-specific files |
| Items and inventory | `Item*.fos`, `Inventory*.fos`, `ClientItems.fos` |
| Tools and mapper behavior | `MapperMain.fos`, mapper-facing helpers |

When changing public script names, event signatures, dialog demands/results, proto names, or generated content IDs, search the content tree for references. Script changes often have consumers in dialogs, text packs, maps, item/critter protos, and GUI callbacks.

## Native Extensions

TLA adds a small native extension layer in [SourceExt/](SourceExt). The files are registered through `AddEngineSources(...)` in [CMakeLists.txt](CMakeLists.txt):

| File | Role |
| ---- | ---- |
| `CommonExtension.cpp` | Shared helpers, including SHA methods exposed to scripts. |
| `ContentMigration.cpp` | TLA-specific content/data migrations. |
| `Dialogs.h` / `Dialogs.cpp` | Runtime dialog support. |
| `ServerExtension.cpp` | Server hooks, image checks, dialog plumbing, visibility hooks, critter busy/free stubs. |
| `ClientExtension.cpp` | Client `Game.FormatTags` and client critter busy/free stubs. |
| `BakerExtension.cpp` | Baker lifecycle extension hook. |
| `DialogBaker.h` / `DialogBaker.cpp` | Dialog bake support. |
| `SHA/*` | Bundled SHA implementation linked as a static third-party library. |

Engine annotations drive binding/codegen:

- `///@ EngineHook` marks lifecycle or behavior hooks with engine-defined names/signatures.
- `///@ ExportMethod` exposes native C++ methods into AngelScript.

If you add or remove native extension files, update the relevant `AddEngineSources(...)` block under `COMMON`, `SERVER`, `CLIENT`, or `BAKER`.

## Configuration

[TLA.fomain](TLA.fomain) is the main runtime and bake configuration.

Important defaults:

| Setting | Value |
| ------- | ----- |
| `Common.GameName` | `FOnline: The Life After` |
| `Common.GameVersion` | `$FILE{VERSION}` |
| `Baking.BakeLanguages` | `russ engl` |
| `Baking.BakeOutput` | `Baking` |
| `Baking.ClientResources` | `Resources` |
| `Baking.ServerResources` | `ServerResources` |
| `Baking.CacheResources` | `Cache` |
| `Client.Language` | `engl` |
| `ClientNetwork.ServerHost` | `localhost` |
| `Network.ServerPort` | `4008` |
| `Server.DbStorage` | `Memory` |
| `Geometry.MapHexagonal` | `True` |
| `WorldTime.StartYear` | `2040` |
| `WorldTime.Multiplier` | `20` |

Subconfigs:

| Subconfig | Purpose |
| --------- | ------- |
| `Unpackaged` | Development-oriented unpackaged startup. Disables music, adds artificial lag, enables render debug, and adjusts timeout/debug settings. |
| `LocalTest` | Local development shard used by launch tasks. Currently empty, so it keeps the base localhost/default-port settings. |
| `PublicGame` | Public-game profile with a public port and server UI collapse behavior. |

Apply a subconfig at runtime with:

```sh
TLA_ServerHeadless --ApplySubConfig LocalTest
```

## Verification Guide

Use the narrowest verification that covers the changed surface:

| Change type | Recommended checks |
| ----------- | ------------------ |
| AngelScript only | `Compile AngelScript`, then `Bake Resources` if the script participates in baked content. |
| Dialogs, texts, maps, protos, resources | `Bake Resources`; inspect baker logs on failure. |
| GUI definitions | Update `Gui/*.fogui`, regenerate `Scripts/GuiScreens.fos`, then `Bake Resources` and build/run the client if behavior changed. |
| Server gameplay behavior | `Bake Resources`, `Build :: TLA_ServerHeadless`, then start with `LocalTest` if startup/runtime matters. |
| Client UI/input/presentation | `Bake Resources`, `Build :: TLA_Client`, then run against a local server. |
| Native server extension | Build the narrowest affected server target; run `TLA_UnitTests` if covered by engine tests. |
| Native client extension | Build `TLA_Client`; add server/client runtime smoke tests if the change crosses the network boundary. |
| Baker/dialog bake support | Build `TLA_Baker`, then `Bake Resources` or `Force Bake Resources`. |
| Engine submodule update | Bake resources, build server and client, compare `H:/lf-30` for migration patterns, run unit tests when relevant, and smoke-test server startup. |

Baseline broad verification:

```sh
cmake --build Build/Auto --config RelWithDebInfo --target BakeResources
cmake --build Build/Auto --config RelWithDebInfo --target TLA_Server
cmake --build Build/Auto --config RelWithDebInfo --target TLA_Client
cmake --build Build/Auto --config RelWithDebInfo --target TLA_UnitTests
```

For runtime startup:

```sh
cmake --build Build/Auto --config RelWithDebInfo --target TLA_ServerHeadless
.\Binaries\Server-Windows-win64\TLA_ServerHeadless.exe --ApplySubConfig LocalTest
```

## Troubleshooting

Start at the boundary that failed, then inspect the first relevant log.

| Symptom | First command | Logs to inspect |
| ------- | ------------- | --------------- |
| Script syntax/API error | `Compile AngelScript` | `TLA_ASCompiler.log`, `Build/_errors.txt` |
| Bake/content/dialog/map/text error | `Bake Resources` | `TLA_Baker.log`, `TLA_BakerLib.log`, `Build/_bake.log`, `Build/_errors.txt` |
| Native compile/link error | Build the narrowest `TLA_*` target | Compiler output, then target logs if startup fails |
| Server startup/runtime issue | `Build :: TLA_ServerHeadless`, then run with `LocalTest` | `TLA_ServerHeadless.log`, `TLA_Server.log` |
| Client presentation/input issue | `Build :: TLA_Client`, then run client/server pair | `TLA_Client.log` |
| Mapper issue | `Build :: TLA_Mapper` | `TLA_Mapper.log` |
| Engine regression | Inspect `Engine` commits and compare `H:/lf-30` if needed | Unit-test output, engine logs |

Common local log files in the repository root:

- `TLA_Server.log`
- `TLA_ServerHeadless.log`
- `TLA_Client.log`
- `TLA_Baker.log`
- `TLA_BakerLib.log`
- `TLA_ASCompiler.log`
- `TLA_Mapper.log`
- `TLA_UnitTests.log`
- `Build/_bake.log`
- `Build/_errors.txt`

## CI And Packaging

GitHub Actions are defined in [.github/workflows/build.yml](.github/workflows/build.yml). The workflow runs on pushes and pull requests to `master`.

CI jobs:

| Job | What it does |
| --- | ------------ |
| `check-formatting` | Runs clang-format 20 over `Scripts` and `SourceExt` (excluding `SourceExt/SHA`). |
| `unit-tests` | Prepares the Linux workspace and runs engine unit tests. |
| `compile-scripts` | Runs `CompileAngelScript` through the engine toolset. |
| `bake-resources` | Runs `BakeResources` and uploads baked output for packaging. |
| `windows-build` | Builds Windows client/server/editor/mapper/baker targets, including profiling variants. |
| `linux-build` | Builds Linux client/server/editor/mapper, Android client variants, and Web client. |
| `macos-build` | Builds macOS and iOS clients. |
| `package` | Combines baked output and binaries into `TLA-Dev`, `TLA-Test`, and the short-lived `TLA-Release` artifact. |
| `release` | Runs after packaging on every workflow run. On `push` to `master` it publishes the GitHub release; otherwise it performs the same metadata/artifact preflight as a dry-run and writes the planned release to the log and job summary. |

Package definitions live in [CMakeLists.txt](CMakeLists.txt):

| Package | Contents |
| ------- | -------- |
| `Dev` | Windows win64 server, client, mapper, editor, baker for `LocalTest`. |
| `Test` | Windows win64 profiling client and server for `LocalTest`. |
| `LinuxTest` | Linux x64 client, server, editor, mapper for `LocalTest`. |

Successful `master` builds publish a versioned GitHub release from the repository `VERSION` file. The release job fails if `VERSION` is not `X.Y.Z` or if the matching `vX.Y.Z` tag already exists, so `VERSION` must be bumped before publishing another release.

Non-release runs execute the release job in dry-run mode. Dry-run mode downloads the same `TLA-Release` artifact, validates `VERSION`, computes the release tag and previous tag, verifies the three zip assets, prints their sizes and SHA-256 hashes, and records the release plan in the workflow summary without creating a tag or GitHub release.

Published release assets:

- `TLA-Dev.zip`
- `TLA-Server.zip`
- `TLA-Client.zip`

## Documentation

Project documents:

- [AGENTS.md](AGENTS.md) - repository practices for maintainers and AI agents.
- [README.md](README.md) - this project overview.
- [CLAUDE.md](CLAUDE.md) - compatibility pointer to `AGENTS.md`.

Engine documents:

- [Engine/README.md](Engine/README.md) - engine overview.
- [Engine/PUBLIC_API.md](Engine/PUBLIC_API.md) - public C++ and build-tool API.
- [Engine/TUTORIAL.md](Engine/TUTORIAL.md) - engine tutorial.
- [Engine/BuildTools/README.md](Engine/BuildTools/README.md) - workspace preparation, packaging, Android workflow, and toolset details.
- [TLA scripting API](https://tla.fonline.ru/SCRIPTING_API) - generated scripting API for this project.

## Contributing

Pull requests against `master` are welcome. Please keep changes focused and verify the surface you touched.

Before opening a pull request:

1. Format relevant files:

   ```sh
   py -3 Tools/Formatter/format_project.py scripts
   py -3 Tools/Formatter/format_project.py prototypes
   py -3 Tools/Formatter/format_project.py fomain
   ```

   Or use the VS Code `Format :: *` tasks.

2. Run script/content checks where relevant:

   ```sh
   cmake --build Build/Auto --config RelWithDebInfo --target CompileAngelScript
   cmake --build Build/Auto --config RelWithDebInfo --target BakeResources
   ```

3. Build affected binaries:

   ```sh
   cmake --build Build/Auto --config RelWithDebInfo --target TLA_Server
   cmake --build Build/Auto --config RelWithDebInfo --target TLA_Client
   ```

4. Run unit tests for native engine-facing changes:

   ```sh
   cmake --build Build/Auto --config RelWithDebInfo --target TLA_UnitTests
   ```

5. Smoke-test local startup when runtime behavior changed:

   ```sh
   .\Binaries\Server-Windows-win64\TLA_ServerHeadless.exe --ApplySubConfig LocalTest
   ```

Contribution notes:

- Keep `Engine/` submodule bumps isolated and intentional.
- Do not hand-edit generated files unless the owning source is updated in the same change.
- Keep player-facing text pack structure intact and update both English/Russian surfaces when the surrounding content expects both.
- Add new native files to `CMakeLists.txt`.
- Prefer project-local script/content changes over engine changes when behavior is TLA-specific.
- Do not commit generated cache/build output.

## License

The source code is distributed under the [MIT License](LICENSE).

The repository also contains bundled third-party engine dependencies and legacy game data packs used by the FOnline content pipeline. Review the relevant upstream licenses and asset rights before redistributing derived packages.
