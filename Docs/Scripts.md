# AngelScript ownership and gameplay contracts

TLA remains **AngelScript**. `CMakeLists.txt` enables `FO_ANGELSCRIPT_SCRIPTING` and
disables Managed scripting. The required `ManagedScript.*` config placeholders
do not authorize a C# migration. Use [Systems](Systems.md) to find a domain,
[ScriptStyle](ScriptStyle.md) for Russian source style and [Nullability](Nullability.md)
for project boundary checks. The reusable compiler/attribute baseline belongs to
[Engine's AngelScript guide](../Engine/Docs/en/how-to/scripting/style-and-refactoring.md).

## Modules, sides and dispatch

Hand-written modules live at the top of `Scripts/`; `Core/` is the **project-owned**
utility library (`Gui`, `Math`, `Time`, `Color`, `Sprite`, `Tween`, etc.), `Json/`
contains JSON helpers, `Tests/` the harness suites and `Generated/` GUI bindings.
Every directory must occur in both `Metadata` and `Scripts` resource-pack
`InputDirs` in [TLA.fomain](../TLA.fomain): baking does not recurse.

Each authored `.fos` normally declares the matching namespace; retain the
validator's explicit `ColorExt.fos` → `Color` exception. There are no hand-written
`#include` graphs. Cross-module calls use `Namespace::Function()`. Use `#if SERVER`,
`#if CLIENT`, `#if MAPPER`; all side macros are defined, so `#ifdef SERVER` does
not select only server code. Compile every affected side.

Keep authoritative gameplay mutations on the server; client code owns input,
presentation, UI and client-only probes. Mark startup with `[[ModuleInit]]` and
subscribe to events there. Attribute-dispatched functions are entrypoints, not
ordinary helpers: extract a plain function for shared direct calls. The explicit
`Test_` direct-call allowlist is test policy, not a gameplay precedent.

Event handlers return `void` for implicit continuation or `EventResult` for an
explicit `ContinueChain`/`StopChain`. Check polarity against the consumer and
intended behavior; a duplicated ternary arm can compile successfully. Use plain
value parameters for inputs; `&` is for genuine value-type out/inout arguments,
not `const &` inputs. Use `Time::Milliseconds`, `Time::Seconds`, `Time::Asap` and
the engine distance/direction/path/trace helpers for TLA's hex grid.

## Single-threaded logic and lifetime

`Server.SingleThreadedLogic=True` is the supported gameplay configuration.
Scripts take no explicit entity cover; do not reintroduce the removed `Sync`
module or `[[Async]]` markers. `Server.WorkerThreads` does not select multiple
logic workers while this mode is enabled. This is project policy, not a reusable
Engine default. Native lifetime/concurrency still follows
[the Engine contract](../Engine/Docs/en/how-to/scripting/lifecycle-and-concurrency.md).

Turning the mode off is a separate migration, not a smoke-test variant. The
2026-09-02 audit recorded 72/72 harness passes alongside 794 access-without-sync
exceptions and 253 time events stopped by exceptions. Those are **historical
diagnostics**, not current suite counts; they explain why PASS totals alone are
insufficient. Restore entity-cover correctness across callers before claiming
multithreaded support.

Single-threaded execution does not remove synchronous callback effects: an
event or explicit destroy can invalidate an entity. Read the actual dispatcher,
callers and ownership boundary when retaining entities across callbacks or waits;
do not add blanket destroyed/null guards that hide a violated invariant.

Time events remain registered through final callback completion, including a
client callback suspended by `Yield`. Repeat delays start after that completion.
`CountTimeEvent(callbackOrId)` includes executing records; retain that default
for singleton guards, active-status checks and cancellation. Use the optional
`true` argument only when intentionally counting pending records while allowing
one independently queued one-shot alongside the executing callback. See the
[Engine timer contract](../Engine/Docs/en/how-to/scripting/lifecycle-and-concurrency.md).

## Mutable state and settings

When touching a namespace in `AngelScript.MutableGlobalsAllowedNamespaces`, either
move mutable state behind its proper owner (parameter/accessor/per-entity state)
and remove that namespace, or put one line in the module header identifying the
global state and why its lifetime must be global. Do not sweep the entire list
or copy a historical namespace count into policy. Settings source is the config.

Engine settings are immutable at runtime. Session state belongs to its subsystem:
`Game.Get/SetMusicVolume`, `Game.Get/SetSoundVolume`, `Game.IsFullscreen`,
`Game.Is/SetAlwaysOnTop`, `ScreenSize`, `CurrentLanguage`, `Map.SetManualScroll`,
`Map.Get/SetVisibleLayers`. Project `///@ Setting` values retain their declared
writability. Session toggles live in their owner (`InputHandler`); choices that
survive restart go through `UserOptions::Save`. Its local config keys must be
`Group.Name`; saved `LocalSettings.focfg` values apply at the next start.

## Project adapters that must not be bypassed

| Owner | Contract |
| --- | --- |
| [ItemStacks.fos](../Scripts/ItemStacks.fos) | Owns `Count`, stacking, merging, splitting and count-aware moves/destruction. Use `ItemStacks::AddItem/CountItem/DestroyItem/MoveItem/SplitItem`; the Engine treats items as single instances. |
| [Sounds.fos](../Scripts/Sounds.fos) | Use `Sounds::Play(name)`. It resolves case-insensitive paths, bare Fallout names such as `LEVELUP.ACM` and `NAME_1..NAME_N` series to baked exact resource paths; `Game.PlaySound` alone does not. |
| [DayColor.fos](../Scripts/DayColor.fos) | Client and Mapper push the day/night tint each frame through `Map.SetDayColors`. The Engine no longer evaluates the old DayColor input curves. Missing submission leaves the white default and overexposes roofs/unlit sprites. |
| [FalloutAnimation.fos](../Scripts/FalloutAnimation.fos) | Owns Fallout filename rules, poses and animation splices; generic frame data/rendering stays in Engine. See [Animation](Animation.md). |
| [GuiScreensExt.fos](../Scripts/GuiScreensExt.fos) | Hand-written companion logic. Embedded screen code belongs in `.fogui`; [generation contract](ContentWorkflow.md#gui-generation). |

Do not use `Critter.AddItem`, `Map.AddItem`, `Item.AddItem`, `Game.MoveItem`,
count-taking `Game.DestroyItem` or `Item.Clone(count)` as substitutes for the
stack adapter. Its regression owner is `Scripts/Tests/Test_ItemStacks.fos`;
day tint is covered by `Scripts/Tests/Test_DayColor.fos`. Add server `Game.Log`
only where it diagnoses meaningful positive/negative behavior.

## Contracts and tests

Map previews are owned by `Scripts/MapPreview.fos`: `Player.ViewMapArea` uses an
inclusive hex radius with live subject updates. Global-map previews retain the
controlled critter; local quest cameras temporarily `Player.SwitchCritter(null)`
and restore the same critter without moving it. TownView returns through
`Player.ReturnFromViewMap` or `Player.SwitchCritter`; city entry repeats normal
server access checks. Preview state is runtime-only on Player; disappearing maps
return the player automatically. Use rebuilt client/server outputs and matching
rebaked metadata/effects; do not carry an old fixed protocol number as policy.

Use `T?` for legitimately absent values and narrow locally; use generated
`Has<Component>` flags before component access and `HasChosen` before `Game.Chosen`.
The complete project spelling/validator workflow is [Nullability](Nullability.md).

Script symbols can be consumed by dialogs, maps, item/critter prototypes, GUI and
text packs. Search those consumers before changing public names or behavior.
Properties, proto IDs, text keys and network/save identities are serialized
contracts; evaluate `///@ MigrationRule` and config/version implications before
changing them. Relocation without renaming is not automatically a persistence
migration, but it still requires matching metadata and a force bake after property
layout changes. Never use a successful bake as semantic acceptance.

Special dialog links such as `Answer Barter` and `Answer Attack` need globally
visible `///@ Enum DialogAnswerLink ...` metadata, normally in `Scripts/Dialogs.fos`,
so the dialog baker can resolve them.

The script harness already exists: `Scripts/Testing.fos` plus `Scripts/Tests/`.
Add focused regressions for changed behavior, using real fixture/content shapes
and an assertion that distinguishes the original wrong result. Test setup must
clean up its entities and report leaks. Prove gameplay through the normal player
path when that is the requested result; injected QA state only proves the path
starting from that state. Commands and acceptance markers:
[BuildAndLaunch](BuildAndLaunch.md#local-runtime-and-tests).
