# FOnline: The Life After

[![Build](https://github.com/cvet/fonline-tla/workflows/build/badge.svg)](https://github.com/cvet/fonline-tla/actions)
[![Last commit](https://img.shields.io/github/last-commit/cvet/fonline-tla.svg)](https://github.com/cvet/fonline-tla/commits/master)
[![License](https://img.shields.io/github/license/cvet/fonline-tla.svg)](LICENSE)
[![Site](https://img.shields.io/badge/site-tla.fonline.ru-blue.svg)](https://tla.fonline.ru)

A massively multiplayer post-apocalyptic isometric RPG set in the *Fallout* universe. Players survive on a shared persistent world with hundreds of locations carried over from the classic *Fallout* / *Fallout 2* art and lore, extended with original maps, quests, and factions.

The game is built on the [FOnline engine](https://github.com/cvet/fonline) (consumed as a git submodule). Gameplay is implemented in AngelScript, with a small native C++ layer for performance-critical hooks and integration glue.

- Website: [tla.fonline.ru](https://tla.fonline.ru)
- Repository: [github.com/cvet/fonline-tla](https://github.com/cvet/fonline-tla)
- Engine: [github.com/cvet/fonline](https://github.com/cvet/fonline)
- Contact: <cvet@tut.by>

## Project scope

A snapshot of what ships with the repository:

| Content | Count |
| ------- | ----- |
| Maps (`*.fomap`) | 400+ |
| Dialog packs (`*.fodlg`) | 850+ |
| Critter protos (`*.focr`) | 530+ |
| Item protos (`*.foitem`) | 800+ |
| AngelScript files (`Scripts/*.fos`) | 260+ |
| Localizations | English, Russian |

## Playing

Pre-built clients and servers are produced by CI on every push to `master` and attached to tagged releases. Grab the latest binaries from the [GitHub Releases](https://github.com/cvet/fonline-tla/releases) page; on Windows, run `TLA_Client.exe` from the unpacked `TLA-Client` archive. The official live shard is configured at [tla.fonline.ru](https://tla.fonline.ru).

If you want to host your own shard, the `TLA-Server` archive contains a self-contained server with baked resources — no extra dependencies required.

## Building from source

Building from source is required for development, modding, and platform targets that are not covered by release artifacts.

### Prerequisites

- **CMake 3.22+** and Git (the engine is a submodule, so a recursive clone is mandatory).
- A toolchain for your target platform — at least one of:
  - Windows: Visual Studio 2022 (17) or Visual Studio 2026 (18), optionally with the ClangCL toolset.
  - Linux: Clang or GCC + Ninja.
  - macOS: Xcode.
  - Web: Emscripten SDK (via the `EMSDK` env var).
  - Android: NDK (via the `NDK_ROOT` env var).
- See [Engine/README.md](Engine/README.md) for the full engine-side toolchain matrix.

### Clone and build

```sh
git clone --recursive https://github.com/cvet/fonline-tla.git
cd fonline-tla
cmake -S . -B Build/Auto --preset auto
cmake --build Build/Auto --config RelWithDebInfo --target BakeResources
cmake --build Build/Auto --config RelWithDebInfo --target TLA_Server
cmake --build Build/Auto --config RelWithDebInfo --target TLA_Client
```

Built executables land in [`Binaries/`](Binaries). A successful smoke test is launching `TLA_ServerHeadless` from `Binaries/` and seeing `Start server complete!` in the log.

### Presets

[`CMakePresets.json`](CMakePresets.json) ships an `auto` preset (host-driven defaults, used by the VSCode tasks) plus per-toolchain configure presets and a large matrix of build presets covering Release, Debug, profiling (`Profiling_Total` / `Profiling_OnDemand`), and sanitizer configurations (Address, Memory, Undefined, Thread, DataFlow, and combinations).

Configure presets: `auto`, `msvc2022`, `msvc2026`, `clang-cl`, `clang-cl-2026`, `clang`, `gcc`, `xcode`, `emscripten`, `android-ndk-arm32`, `android-ndk-arm64`, `android-ndk-x86`.

### Build targets

| Target | Purpose |
| ------ | ------- |
| `BakeResources` | Bake all content (scripts, dialogs, images, protos, maps, texts). Run after content changes. |
| `ForceBakeResources` | Same as above but ignores cache. |
| `TLA_Server` | Game server with embedded GUI and dev tooling. |
| `TLA_ServerHeadless` | Headless server — primary target for production and CI. |
| `TLA_Client` | Game client. |
| `TLA_Mapper` | Map editor. |
| `TLA_Editor` | Content editor. |
| `TLA_Baker` | Standalone resource baker. |
| `TLA_ASCompiler` | AngelScript compiler / static checker. |
| `TLA_UnitTests` | Engine and content unit tests. |
| `CompileAngelScript` | Recompile gameplay scripts only. |

### VSCode integration

The same workflow is exposed as VSCode tasks in [.vscode/tasks.json](.vscode/tasks.json): `BakeResources`, `Build TLA_*`, `Prepare TLA_*` (bake + build), `Format Scripts`, and `Generate GuiScreens.fos`. The `Prepare TLA_*` tasks are the recommended end-to-end verification steps.

### Continuous integration

[`.github/workflows/build.yml`](.github/workflows/build.yml) runs on every push and pull request to `master`. It checks formatting, compiles AngelScript, bakes resources, runs unit tests, and produces binaries for:

- Windows (x86, x64) — client, server, editor, mapper, baker, plus profiling builds.
- Linux (x64) — client, server, editor, mapper.
- macOS — client.
- iOS — client.
- Android (armeabi-v7a, arm64-v8a) — client.
- Web (Emscripten) — client.

Tagged builds publish `TLA-Dev`, `TLA-Server`, and `TLA-Client` archives as release assets.

## Repository layout

| Path | Role |
| ---- | ---- |
| [`Engine/`](Engine) | Pinned [FOnline engine](https://github.com/cvet/fonline) submodule. Treated as upstream — do not edit in place. |
| [`Scripts/`](Scripts) | AngelScript gameplay code (`*.fos`): combat, dialogs, quests, AI, UI behavior, world events. Flat layout with `Json/` as the only nested folder. |
| [`SourceExt/`](SourceExt) | Native C++ extensions hooked into the engine via `///@ EngineHook` and `///@ ExportMethod` annotations, wired through `AddEngineSources(...)` in [`CMakeLists.txt`](CMakeLists.txt). |
| [`Gui/`](Gui) | Interface definitions (`*.fogui`) and the default GUI scheme. |
| [`Maps/`](Maps) | Maps (`*.fomap`) and location metadata (`*.foloc`). |
| [`Critters/`](Critters) | Critter protos (`*.focr`). |
| [`Items/`](Items) | Item protos (`*.foitem`, `*.fopro`). |
| [`Dialogs/`](Dialogs) | Dialog packs (`*.fodlg`). |
| [`Texts/`](Texts) | Localized text packs (`*.fotxt`). Bake languages: `russ`, `engl`. |
| [`Resources/`](Resources) | Image, audio, video, and packed art assets (including original *Fallout* data packs). |
| [`Tools/`](Tools) | Auxiliary tooling: `clang-format-20.exe`, the GUI script generator, dialog editor. |
| [`Binaries/`](Binaries) | Built executables. |
| [`Build/`](Build) | Local build directories (one per preset). |
| [`Cache/`](Cache), [`Baking/`](Baking) | Caches and baked output produced by `BakeResources`. |
| [`TLA.fomain`](TLA.fomain) | Main configuration: resource packs, baking rules, server defaults, sub-configs. |
| [`VERSION`](VERSION) | Game version string used at bake time. |

## Scripting

Gameplay logic is written in AngelScript with FOnline preprocessor extensions:

- `*.fos` files in [`Scripts/`](Scripts) hold the bulk of the game.
- [`Scripts/GuiScreens.fos`](Scripts/GuiScreens.fos) is **generated** from `Gui/*.fogui` by the Python tool [`Tools/InterfaceEditor/generate_gui_screens.py`](Tools/InterfaceEditor/generate_gui_screens.py). Regenerate it through the `Generate GuiScreens.fos` VSCode task after changing screen identity. Do not hand-edit the generated file. The hand-written companion is [`Scripts/GuiScreensExt.fos`](Scripts/GuiScreensExt.fos).
- The `InterfaceEditor.exe` binary in the same folder also has a `-SilentGenerate` mode, but its output layout is incompatible — always use the Python generator.
- Native extensions in [`SourceExt/`](SourceExt) expose additional methods to AngelScript (`///@ ExportMethod`) and hook engine lifecycle events (`///@ EngineHook`).
- Run [`FormatSource.bat`](FormatSource.bat) (or the `Format Scripts` VSCode task) before submitting changes; it formats `Scripts/*.fos`, `Scripts/Json/*.fos`, `SourceExt/*.cpp`, `SourceExt/*.h`, and `Gui/*.fogui` with the bundled clang-format-20.

## Documentation

- [CLAUDE.md](CLAUDE.md) — repository tour and working notes (build workflow, native extensions, engine update process, conventions).
- [Engine/README.md](Engine/README.md) — engine-side overview.
- [Engine/PUBLIC_API.md](Engine/PUBLIC_API.md) — engine public C++ / scripting API reference.
- [Engine/TUTORIAL.md](Engine/TUTORIAL.md) — engine tutorial.

## Contributing

Contributions are welcome via pull requests against `master`. Please:

1. Format your changes (`Format Scripts` task or `FormatSource.bat`) — CI will reject unformatted code.
2. Confirm the unit tests and AngelScript compile pass locally (`TLA_UnitTests`, `CompileAngelScript`).
3. Bake resources (`BakeResources`) and smoke-test `TLA_ServerHeadless` for changes that touch content.
4. Keep engine-submodule bumps in their own focused commits, aligned with upstream PR boundaries.

## License

[MIT](LICENSE).
