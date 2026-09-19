# FOnline: The Life After - Agent Instructions

Project front door for AI maintainers working on **FOnline: The Life After** (TLA). Read this before changing anything. Keep this file as the single source for agent-facing repository practices; `CLAUDE.md` and `.github/copilot-instructions.md` intentionally point here.

## What This Project Is

- TLA is a multiplayer game built on top of the reusable **fonline-engine** submodule in `Engine/`.
- The split is engine plus game:
  - `Engine/` - upstream engine submodule. Treat as external unless the task explicitly requires an engine change.
  - `Scripts/*.fos` - AngelScript gameplay, dialogs, quests, AI, GUI behavior, and server/client hooks. Hand-written gameplay code sits at the top level; `Scripts/Generated/` holds generated files, `Scripts/Tests/` the harness suites, `Scripts/Json/` the JSON helpers, `Scripts/Core/` the utility library (`Gui`, `Math`, `Time`, `Color`, `Sprite`, `Tween`, ...) that the engine used to bundle and that TLA owns since the engine went backend-neutral. Every script directory must be listed in the `InputDirs` of the `Metadata` and `Scripts` resource packs in `TLA.fomain` — baking does not recurse.
  - `SourceExt/*.cpp` / `SourceExt/*.h` - project-local native C++ extensions registered from `CMakeLists.txt`.
  - `Critters/`, `Items/`, `Maps/`, `Dialogs/`, `Gui/`, `Texts/`, `Resources/` - authored game content and assets.
  - `TLA.fomain` - master engine/game config and `[SubConfig]` profiles.
  - `CMakeLists.txt` / `CMakePresets.json` - build glue. Default local preset is `auto` into `Build/Auto`.
- TLA scripts are AngelScript only. The engine also offers a managed (C#) backend; it stays off (`FO_MANAGED_SCRIPTING OFF` in `CMakeLists.txt`), and the `ManagedScript.*` settings the engine requires regardless are left empty in `TLA.fomain`.
- The user usually converses in Russian; answer the user in Russian unless asked otherwise.
- **Script comment language is Russian** (owner decision 2026-06-20, reversing the prior English-only rule). In `Scripts/*.fos`: code comments and the per-file header block (see [Docs/ScriptStyle.md](Docs/ScriptStyle.md)) are written in Russian, and existing English comments are translated to Russian as files are touched. **Exception:** serialized/contract names stay English — `///@ Property/Enum/Setting/Event/RemoteCall`, proto ids, text-pack keys, and identifiers (renaming them risks save/network/content migration). Agent-facing markdown (`AGENTS.md`, most of `Docs/`) and native C++ (`SourceExt/`) remain English; player-facing text follows the existing localized pack structure.
- Text packs are baked for `russ engl`; `Client.Language = engl` in the default config. When editing player-facing text, preserve the existing pack structure and update both language surfaces when the nearby content expects that.

## Repository Orientation

- `Engine/` - pinned fonline-engine submodule. Do not edit in place for game behavior; advance the SHA in coordinated chunks.
- `Scripts/Content.fos` - generated/baked content declarations. Do not hand-edit.
- `Scripts/Generated/GuiScreens.fos` - generated screen bindings. Source of truth: `Gui/*.fogui` plus `Tools/InterfaceEditor/generate_gui_screens.py`. Do not hand-edit unless you also update the owning `.fogui` code as described below.
- `Scripts/GuiScreensExt.fos` - hand-written companion to `GuiScreens.fos`; non-generated GUI logic lives here.
- `Scripts/Sounds.fos` - play sounds through `Sounds::Play(name)`, not `Game.PlaySound`: the engine plays only an exact resource path, and `Sounds` maps TLA's names (any-case paths, bare Fallout names such as `LEVELUP.ACM`, `NAME_1..NAME_N` series) onto the baked paths.
- `Gui/*.fogui` - GUI definitions and embedded screen script code.
- `SourceExt/CommonExtension.cpp` - SHA helpers shared by client/server.
- `SourceExt/ServerExtension.cpp` - server image checks, dialog plumbing, visibility hooks, critter busy/free stubs.
- `SourceExt/ClientExtension.cpp` / `SourceExt/ClientExtension.h` - `Game.FormatTags`, client critter busy/free stubs, `ClientInitHook` + `ClientExtData` (holds the AI control bridge state and embedded-client index).
- `SourceExt/ClientAiBridge.cpp` - localhost TCP line protocol for the AI control bridge (client-side test/automation). Pairs with `Scripts/AiControl.fos` and `Tools/AiControlMcp/`. See [Docs/AiControl.md](Docs/AiControl.md).
- `SourceExt/BakerExtension.cpp`, `SourceExt/DialogBaker.*`, `SourceExt/Dialogs.*` - dialog bake/runtime support; `SetupBakersHook` also registers the ACM loader with the engine's `AudioBaker`.
- `SourceExt/AcmDecoder.*` - Fallout ACM decoder (a bit-exact port of the unpacker the engine dropped in #211) and `LoadAcmAudio`, the `AudioBaker` loader: every `.acm` is baked to Ogg Vorbis like any other sound, effects as mono and `sound/music/` as stereo, the way Fallout played them. Covered by `SourceExt/TestAcmDecoder.cpp`.
- `SourceExt/ContentMigration.cpp` - TLA-specific content/data migrations.
- `SourceExt/SHA/` - bundled SHA implementation wrapped as a static library.
- `Tools/Formatter/format_project.py` and `FormatSource.bat` - formatting entry points. VS Code tasks use the Python formatter.
- `Tools/InterfaceEditor/generate_gui_screens.py` - supported GUI screen generator.
- Build/runtime logs are written to repo root: `TLA_Server.log`, `TLA_ServerHeadless.log`, `TLA_Client.log`, `TLA_Baker.log`, `TLA_ASCompiler.log`, `TLA_Mapper.log`, `Build/_bake.log`, `Build/_errors.txt`.
- Built binaries land under `Binaries/`; baked output lives in `Baking/`; cache in `Cache/`; resource trees in `Resources/`.

Adding or removing a native extension file requires updating the relevant `AddEngineSources(...)` block in `CMakeLists.txt` under `COMMON`, `SERVER`, `CLIENT`, or `BAKER`.

## Build And Verify

VS Code tasks in `.vscode/tasks.json` are the authoritative workflow. The same commands can be run directly from the terminal.

Warnings are treated as failures. Keep script compilation, resource baking, native builds, tests, and smoke runs at zero warnings; fix new or existing warnings instead of hand-waving them in the handoff.

| Task | When to use |
| ---- | ----------- |
| `Verify :: All` | The full pre-handoff chain: bake, build every target, engine unit tests, script harness, validators, formatters. Run this instead of reassembling the steps by hand; CI runs the same chain. |
| `Bake Resources` | After edits in `Scripts/`, `Dialogs/`, `Maps/`, `Items/`, `Critters/`, `Texts/`, `Gui/`, or `TLA.fomain`. |
| `Force Bake Resources` | When incremental baking may be stale. Use sparingly. |
| `Compile AngelScript` | Fast script syntax/API check. |
| `Build :: TLA_Server`, `Build :: TLA_ServerHeadless`, `Build :: TLA_Client`, `Build :: TLA_Mapper`, `Build :: TLA_Baker`, `Build :: TLA_ASCompiler`, `Build :: TLA_UnitTests` | Build one target in `Build/Auto`, `RelWithDebInfo`. |
| `Prepare :: TLA_*` | `Bake Resources` plus the corresponding build target. |
| `Launch :: TLA_Server [windows]` / `[linux]` | Build, bake, then run the server with `LocalTest`. |
| `Launch :: TLA_UnitTests [windows]` / `[linux]` | Build, bake, then run engine unit tests. |
| `Generate :: GuiScreens.fos` | Regenerate `Scripts/Generated/GuiScreens.fos` from `Gui/*.fogui`. |
| `Generate :: Version` | Update `VERSION` via `Tools/GenerateVersion/generate_version.py`; do not hand-edit `VERSION`. |
| `Format :: Scripts`, `Format :: Prototypes`, `Format :: Main Config`, `Format :: All` | Format the relevant authored files. |
| `Test :: Python Tools` | The tooling test suites under `Tools/` (script/content quality, nullable, AI control bridge). |

Typical command equivalents:

```bash
cmake --build Build/Auto --config RelWithDebInfo --target BakeResources
cmake --build Build/Auto --config RelWithDebInfo --target TLA_Server
cmake --build Build/Auto --config RelWithDebInfo --target TLA_Client
```

Baseline verification after an engine bump or broad script/content change:

1. `Bake Resources`
2. `Build :: TLA_Server`
3. `Build :: TLA_Client`
4. If runtime startup matters, run `TLA_ServerHeadless` or `Launch :: TLA_Server [windows]` and confirm startup reaches `"Start server complete!"`.

For native engine-facing changes, also build/run `TLA_UnitTests` when the touched surface is covered by engine tests.

## Engine Update Workflow

The engine moves frequently. Handle submodule bumps deliberately:

1. Inspect `Engine` status and recent upstream commits first.
2. Prefer fast-forwarding `Engine` at coherent upstream boundaries instead of a large blind jump.
3. After each bump: `Bake Resources` -> build affected targets -> fix script/config/native fallout.
4. Cross-check `H:/lf-30` when upstream renames or signatures shift. It is the nearest migration reference and often has the pattern already.
5. Do not commit, stage, or push unless the user explicitly asks. The user reviews and commits changes themselves.

Typical breakage points after a bump:

- New engine settings required in `TLA.fomain`.
- `///@ EngineHook` rename or signature change in `SourceExt/*Extension.cpp`.
- AngelScript core type/API changes (`hstring`, `any`, `ident_t`, `mpos`/`mdir`, collection APIs).
- Stricter AngelScript nullability and component access (`T?`, `Has<Component>`, no component `== null` probes).
- Logging or stack-trace API changes.
- New init-path guards such as `if (IsTestingInProgress) return;`.
- Baker/CMake API changes around `AddEngineSources(...)`, `AddDirSource(...)`, or generated metadata.

## Engine Vs Game Boundary

Before adding behavior, pick the narrowest correct layer:

1. Gameplay rules, quests, dialogs, AI, GUI behavior -> AngelScript in `Scripts/` or authored content.
2. Project-specific native bridge or helper -> `SourceExt/`, wired through `CMakeLists.txt`.
3. Reusable engine capability -> `Engine/` only when the change belongs to every game using the engine.
4. Runtime/build configuration -> `TLA.fomain` or a `[SubConfig]`.

When a serialized contract changes (properties, save data, network-visible data, generated content IDs), check whether `///@ MigrationRule` metadata or a config/version bump is required.

## Native Extensions

Native exports use engine annotations:

- `///@ EngineHook` - lifecycle or behavior hook. Name/signature are dictated by engine codegen.
- `///@ ExportMethod` - binds C++ functions into AngelScript. The first argument is the receiver (`ServerEngine*`, `ClientEngine*`, `BaseEngine*`, `Critter*`, `CritterView*`, etc.). The AngelScript name comes from the `Server_` / `Client_` / `Common_` suffix mapping, e.g. `Server_Game_LoadImage` -> `Game.LoadImage` on server.

Native C++ conventions:

- Match existing engine/source style before introducing a new pattern.
- Use `FO_SCRIPT_API` on exported methods/hooks.
- For non-trivial engine/native functions, follow nearby stack-trace practice (`FO_STACK_TRACE_ENTRY()` or `FO_NO_STACK_TRACE_ENTRY()`), especially in engine-facing hooks.
- Prefer `FO_RUNTIME_ASSERT` / `FO_RUNTIME_ASSERT_STR` for invariants over silent fallbacks.
- Use fixed-width engine aliases (`int32_t`, `uint32_t`, `float32_t`, `size_t`, etc.) where the surrounding code does.
- Use `numeric_cast` for numeric conversions when narrowing/widening matters.
- Use pointers for `Entity`-derived objects unless the existing API requires references.
- Use file-local `static` helpers; avoid introducing hidden mutable static state.
- Add `const`/`noexcept` when they express the real contract, not mechanically.
- Keep edited source files ending with exactly one trailing blank line.

## AngelScript Conventions

- Each `.fos` file declares a namespace matching its filename (`CritterActions.fos` -> `namespace CritterActions`).
- There are no `#include` directives; baking sees all `.fos` files. Cross-module calls use `Namespace::Function()`.
- Use `#if SERVER`, `#if CLIENT`, and `#if MAPPER` carefully. Side-specific bugs are often missing or stray guards.
- Keep authoritative gameplay state changes on the server. Client scripts should focus on UI, input, presentation, and client-only probes.
- **A module you touch leaves the mutable-globals allowlist, or says why it stays.**
  `AngelScript.MutableGlobalsAllowedNamespaces` in `TLA.fomain` lists 77 namespaces — it was meant to mark
  exceptions and now covers nearly the whole project, which is also what makes those modules hard to test in
  isolation. Do not sweep the list; when a module is opened for any other reason, either move its mutable
  state behind the module (a parameter, an accessor, per-entity storage) and drop the namespace, or add one
  line to the module header saying what the global state is and why it has to be global.
- Mark startup functions with `[[ModuleInit]]`; subscribe to events from `ModuleInit()`. Attribute-marked functions are called by their attribute system; move reusable logic into plain helpers instead of calling attribute entrypoints directly.
- **Scripts take no entity cover, and the server runs single-threaded.** `Server.SingleThreadedLogic = True`
  pins the engine to one worker, so a script may read and mutate any entity it can reach without
  synchronizing first. The script-side `Sync` module and the `[[Async]]` markers that propagated from
  `Game.Sync` were removed with it — do not reintroduce either.
- **The multithreaded configuration is not supported by the current scripts.** Turning
  `Server.SingleThreadedLogic` off still passes the harness (72/72), because the resulting
  `Entity access without sync` throws are recoverable at the job frontier — but it logs 794 of them and
  stops 253 time events by exception. `Server.WorkerThreads` therefore has no effect. Restoring the
  multithreaded mode means restoring entity cover across the scripts, which is a project of its own.
- Event handlers return `void` for implicit continue or `EventResult` for explicit `ContinueChain` / `StopChain`.
- Do not pass inputs by `const &`. Use plain `&` only for genuine out/inout value-type parameters.
- Treat `?` as the source contract for nullable handles. If a dictionary lookup or engine call can return `null`, bind it to a nullable local (`T?`) before narrowing it.
- The AngelScript compiler enforces nullability at compile time ("strong nullable"): it warns on redundant null comparisons, dereference of an un-narrowed `T?`, and a redundant `?` on a non-null initializer. Fix these — narrow `T?` locals with `if (x == null) return;` / `if (x != null)` / ternary / `&&`-`||` short-circuits, use `cast<T?>(x)` (not `cast<T>(x)`) when a downcast may fail and you test for `null`, and guard the throwing `Game.Chosen` accessor with `HasChosen` rather than `Chosen == null`. See [Nullability.md](Nullability.md) for the full rules.
- Component properties are guarded by generated `Has<Component>` flags. Check `item.HasRadio`, `cr.HasDialogContext`, etc. before using the component accessor; do not compare the component accessor itself with `null`.
- Use explicit time helpers (`Time::Milliseconds`, `Time::Seconds`, `Time::Asap`) for game timing where available.
- Prefer engine/game geometry helpers such as `Game.GetDistance()`, `Game.GetDirection()`, pathing, and tracing APIs instead of inventing rectangular-grid math. TLA uses hex-grid assumptions.
- Do not mask invariant failures with broad defensive fallbacks. Assert or fail loudly when an expected value is absent.
- Add server-side `Game.Log(...)` lines only when they materially help diagnose positive and negative flows.
- Script changes often affect authored assets: dialogs, text packs, item/critter/map prototypes, GUI callbacks. Check references when changing public symbols or behavior.
- Special dialog answer links such as `Answer Barter` / `Answer Attack` must have globally visible `///@ Enum DialogAnswerLink ...` metadata, typically near the dialog contract in `Scripts/Dialogs.fos`, so the dialog baker can resolve them.
- Keep edited `.fos` files ending with exactly one trailing blank line.

## Content Pipeline

Authored inputs:

```text
Scripts/*.fos, Scripts/Core/*.fos, Scripts/Generated/*.fos, Scripts/Json/*.fos, Scripts/Tests/*.fos
Critters/*.focr, Items/*.foitem, Maps/*.fomap
Dialogs/*.fodlg, Gui/*.fogui, Texts/*.fotxt
Resources/*
```

Pipeline:

```text
Gui/*.fogui
  -> Tools/InterfaceEditor/generate_gui_screens.py
  -> Scripts/Generated/GuiScreens.fos

Authored sources + generated script files
  -> BakeResources / ForceBakeResources
  -> baked configs, scripts, protos, maps, dialogs, text, resource packs
  -> Binaries/ consume baked output
```

A file can bake successfully and still be semantically wrong. Debug content by starting from the consumer: combat code for combat data, dialog code for `.fodlg` demand/result failures, GUI code for `.fogui` callbacks, and so on.

## GuiScreens.fos Pitfall

`Scripts/Generated/GuiScreens.fos` is generated **only** by `Tools/InterfaceEditor/generate_gui_screens.py`. The VS Code task `Generate :: GuiScreens.fos` is already wired to that script.

Do not use the legacy `Tools/InterfaceEditor/InterfaceEditor.exe -SilentGenerate` path for TLA generation; it emits an incompatible layout for this project.

AngelScript embedded in screens lives in the `.fogui` JSON: `OnGlobalMouseDown`, `OnLMouseClick`, `GlobalScope`, `ClassFields`, `OnDraw`, callbacks listed in `CALLBACK_METHODS`, plus `CODE_KEYS` in the generator. If you fix behavior inside generated screen code:

1. Find the owning `.fogui` file.
2. Apply the same edit there.
3. Apply the same edit to `Scripts/Generated/GuiScreens.fos` if the baked project needs the fix immediately.
4. Regenerate only when screen identity or non-code `.fogui` properties change, or when you intentionally want to refresh generated output.

## Formatting And Generated Files

- Use `Format :: Scripts`, `Format :: Prototypes`, `Format :: Main Config`, or `Format :: All` before handing off when touched files need formatting.
- `FormatSource.bat` is a smaller formatter path for `Scripts/`, `SourceExt/*`, and `Gui/*.fogui`.
- `Tools/ScriptQuality/validate_scripts.py` is a quality *validator* (reports only; not a formatter) for `Scripts/*.fos`: banner tags, magic text-pack ids, hand-rolled-util calls, redundant bool returns, commented-out code, `namespace`==filename, `#if` balance, component `== null` probes, unsafe location access from `ItemTrigger` callbacks, and trailing blank lines. (The former `cyrillic-comment` check was retired 2026-06-20 — script comments are Russian now; see [Docs/ScriptStyle.md](Docs/ScriptStyle.md).) Run `Analyze :: Script Quality` for a summary; `--ratchet` fails only on new violations vs `Tools/ScriptQuality/baseline.json`; `--fix` applies the few safe autofixes. See `Tools/NullableEstimate/validate_nullable.py` for the complementary script `?` and native `ptr<T>`/`nptr<T>` ABI checks.
- Do not hand-edit generated files: `Scripts/Content.fos`, generated `Scripts/Generated/GuiScreens.fos` without the matching `.fogui` update, baked output under `Baking/`, cache files under `Cache/`, or generated `VERSION`.
- Local working trees such as `TLA-Dev/`, `Baking/`, `Cache/`, and build folders are outputs/debug state, not canonical authored inputs.

## Debugging

Pick the boundary before reaching for a heavy interactive session:

| Symptom | Start with |
| ------- | ---------- |
| Script compile error | `Compile AngelScript`, then inspect `TLA_ASCompiler.log` / `Build/_errors.txt`. |
| Content, dialog, map, or text bake error | `Bake Resources`, then inspect `TLA_Baker.log`, `TLA_BakerLib.log`, `Build/_bake.log`, `Build/_errors.txt`. |
| Native compile/link error | Build the narrowest `TLA_*` target and inspect the first compiler error. |
| Server startup/runtime issue | `Build :: TLA_ServerHeadless` or `Launch :: TLA_Server [windows]`, then inspect `TLA_ServerHeadless.log` / `TLA_Server.log`. |
| Client presentation/input issue | `Build :: TLA_Client`, run the client/server pair, then inspect `TLA_Client.log`. |
| Engine regression | Check `Engine` upstream commits, compare `H:/lf-30`, then run/build `TLA_UnitTests` when applicable. |

## Commit Policy

- Do not run `git commit`, `git add`, `git push`, or destructive git commands unless the user explicitly asks.
- The worktree may contain user changes. Never revert or overwrite changes you did not make.
- If unrelated files are dirty, leave them alone. If touched files contain user changes, read them and work with them.
- Summarize changed files, verification, and any residual risk at the end of the task.

## Quick Reference

- `Docs/README.md` - documentation index.
- `Docs/Systems.md` - map of the gameplay systems: what they are, where they live, what covers them.
- `Docs/AuditPlan.md` - the current improvement queue with the measurement behind each item.
- `README.md` - repo-root overview.
- `Docs/AiControl.md` - AI control bridge (client-side TCP test/automation) + the `Tools/AiControlMcp/` MCP adapter for observing/controlling a real client to test mechanics and quests.
- `Docs/Refactoring.md` - Scripts/*.fos refactoring plan, phases, and running status.
- `TLA.fomain` - main config and subconfigs (`LocalTest`, `PublicGame`, resource baking subconfigs).
- `.vscode/tasks.json` - authoritative build/generate/format/launch tasks.
- `.vscode/launch.json` - debugger launch profiles when present.
- `CMakeLists.txt` - target wiring and native extension roles.
- `.github/workflows/` - CI definitions.
- `H:/lf-30/AGENTS.md` - reference project on the same engine; copy only generic, non-project-specific practices.
