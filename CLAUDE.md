# CLAUDE.md

FOnline: The Life After (TLA) — multiplayer game built on top of the **fonline-engine** submodule (`Engine/`). Gameplay is written in AngelScript (`Scripts/*.fos`), native extensions in C++ (`Scripts/Extension/*.cpp`), GUI in `Gui/*.fogui`. A single CMake build wires everything above the engine in via `AddEngineSource(...)` in `CMakeLists.txt`.

## Repo orientation

- `Engine/` — pinned fonline-engine submodule. Treat as upstream: do not edit in place; advance the SHA in coordinated chunks.
- `Scripts/*.fos` — AngelScript: gameplay, dialogs, quests, AI. The folder is flat (only `Json/` and `Extension/` subfolders).
- `Scripts/Extension/*.cpp` — native C++ extensions. Each file is listed at the top of `CMakeLists.txt` via `AddEngineSource(<scope> path)`, where scope is `COMMON` / `SERVER` / `CLIENT` / `BAKER`.
- `Scripts/GuiScreens.fos` — **generated** screen bindings. Source of truth: the Python generator (see below). Do not hand-edit.
- `Scripts/GuiScreensExt.fos` — hand-written companion to `GuiScreens.fos`; everything that is not generated lives here.
- `Gui/*.fogui` — GUI definitions. Edited by hand. Changes that affect screen identity require regenerating `GuiScreens.fos`.
- `TLA.fomain` — main config (resource packs, baking, server defaults, sub-configs).
- `CMakeLists.txt` / `CMakePresets.json` — build glue. Default working preset is `auto` → `Build/Auto`, configuration `RelWithDebInfo`.
- `Tools/InterfaceEditor/generate_gui_screens.py` — generator for `GuiScreens.fos`. **Do not invoke `InterfaceEditor.exe` to generate it** — the .exe lives in the same folder but emits an incompatible layout (see below).
- `FormatSource.bat` — formats `Scripts/*.fos`, `Scripts/Json/*.fos`, `Scripts/Extension/*.cpp`, `Gui/*.fogui` via `Tools/clang-format-20.exe`.

## Build and verify

VSCode tasks in [.vscode/tasks.json](.vscode/tasks.json) drive the build.

| Task | When to use |
| ---- | ----------- |
| `BakeResources` | After edits in `Scripts/`, `Dialogs/`, `Maps/`, `Items/`, `Critters/`, `Texts/`, `Gui/`. |
| `Build TLA_Server` / `TLA_ServerHeadless` / `TLA_Client` / `TLA_Baker` / `TLA_ASCompiler` / `TLA_UnitTests` | Build a single target (`Build/Auto`, `RelWithDebInfo`). |
| `Prepare TLA_*` | `BakeResources` + the corresponding build target. Use these for end-to-end verification. |
| `Format Scripts` | Runs `FormatSource.bat`. |
| `Generate GuiScreens.fos` | Regenerates `Scripts/GuiScreens.fos` via the Python script. Run after `Gui/*.fogui` changes that affect the set or names of screens. |

Baseline verification after an engine bump or a large script change: `BakeResources` → `Build TLA_Server` → `Build TLA_Client`. A smoke run of `TLA_ServerHeadless` from `Binaries/` should reach the line `"Start server complete!"`.

Build environment (Windows, primary): Visual Studio 18 Insiders 2026 + the CMake `auto` preset (Ninja Multi-Config). VSCode tasks effectively run `cmake --build Build/Auto --config RelWithDebInfo --target <T>`.

## Native extensions

Each `.cpp` in `Scripts/Extension/` exports to the engine through two annotation styles:

- `///@ EngineHook` — lifecycle entry point. Name and signature are dictated by the engine; upstream renames/signature changes propagate here. The current key hook is `ServerInitHook(ServerEngine*)` in [Scripts/Extension/ServerExtension.cpp](Scripts/Extension/ServerExtension.cpp) (server-side init, dialog manager allocation).
- `///@ ExportMethod` — binds a C++ function into AngelScript. The first argument is the receiver (`ServerEngine*`, `ClientEngine*`, `Critter*`, `CritterView*`, `BaseEngine*`); the AngelScript name comes from the suffix after `Server_` / `Client_` / `Common_` (e.g. `Server_Game_LoadImage` → `Game.LoadImage` on the server, `Common_Game_Sha1` → available on both client and server).

File breakdown:

- [CommonExtension.cpp](Scripts/Extension/CommonExtension.cpp) — sha1 / sha2 (used by both client and server).
- [ServerExtension.cpp](Scripts/Extension/ServerExtension.cpp) — image loading for server-side checks, dialog plumbing (`Server_Game_GetDialogPack`, `Server_Game_RunSpeechScript`, `Server_Game_DialogScriptDemand/Result`), `Critter.IsFree/IsBusy/Wait` stubs.
- [ClientExtension.cpp](Scripts/Extension/ClientExtension.cpp) — `Game.FormatTags` (dialog text expansion: `$lex` → `@lex …@`, `@sex@` / `|m|f|`, `@rnd@`, `@text@`, `@script@`, `#` → newline), `Critter.IsFree/IsBusy/Wait` stubs.
- [BakerExtension.cpp](Scripts/Extension/BakerExtension.cpp) + [DialogBaker.cpp](Scripts/Extension/DialogBaker.cpp) — dialog handling at bake time.
- [Dialogs.cpp](Scripts/Extension/Dialogs.cpp) / [Dialogs.h](Scripts/Extension/Dialogs.h) — runtime dialog manager.
- [ContentMigration.cpp](Scripts/Extension/ContentMigration.cpp) — content/data migrations. **TLA-specific; not present in lf-7.**

Adding or removing a file here requires updating the corresponding `AddEngineSource(...)` line in `CMakeLists.txt`.

## Engine update workflow

The engine lives in its own repo and moves frequently. Workflow:

1. **Incremental, at PR boundaries.** Never advance the submodule in one large jump. After each chunk: bake → build the affected targets → fix script / extension fallout → confirm green.
2. **Cross-check with lf-7.** A reference repo on the same engine lives at `H:/lf-7` (same owner; usually receives migrations a step ahead of TLA). On upstream renames or signature changes, check there first and copy the pattern unless there is a TLA-specific reason to diverge.
3. **Do not commit between steps.** The user reviews and commits themselves (see "Commit policy").

Typical breakage points after a bump:

- `///@ EngineHook` rename or signature change → fix in `Scripts/Extension/*Extension.cpp`.
- AngelScript core type changes (`hstring`, `any`, `mdir` / `mpos`, `ident_t`) → ripple through `.fos` files.
- `LogFunc` or logging API signature drift.
- New mandatory guards such as `if (IsTestingInProgress) return;` in init paths.

## GuiScreens.fos generation — pitfall

`Scripts/GuiScreens.fos` is generated **only** by [Tools/InterfaceEditor/generate_gui_screens.py](Tools/InterfaceEditor/generate_gui_screens.py). The `Generate GuiScreens.fos` task in `.vscode/tasks.json` is already wired to it.

The same folder also contains a legacy binary, `InterfaceEditor.exe -SilentGenerate`, with its own (incompatible) generation logic. Invoking it produces a `GuiScreens.fos` that does not compile against TLA's scripts (mismatched namespaces, screen types, etc.). **Do not call it for regeneration.**

## Conventions

- **Formatting.** Before committing, or whenever files look untidy, run the `Format Scripts` task. It covers `.fos`, the extension `.cpp` files, and `.fogui`.
- **Commit policy.** The user commits everything themselves. Do not run `git commit` / `git add` / `git push` unless explicitly asked. After a task: summarize what changed and stop.
- **Repository language.** Repository content is English (code, comments, docs including this file). The user converses in Russian; keep replies in Russian unless asked otherwise, but do not put Russian into committed files.

## Where to look when debugging

- Build/runtime logs are written to the repo root: `TLA_Server.log`, `TLA_ServerHeadless.log`, `TLA_Client.log`, `TLA_Baker.log`, `TLA_ASCompiler.log`, `TLA_Mapper.log`, plus `Build/_bake.log` and `Build/_errors.txt`.
- Built binaries land in `Binaries/`.
- Cache lives in `Cache/`; baked output in `Baking/`; client/server resource trees in `Resources/`.
