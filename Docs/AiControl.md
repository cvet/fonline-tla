# AI Control Bridge (TLA)

The AI control bridge lets an external tool (an MCP host / model) observe and control a real TLA
client over a localhost TCP socket. One bridge connection controls one client.
Ordinary actions use server-validated gameplay RPCs (cooldowns, visibility, range,
ownership and dialog state). Explicitly gated `qa_*` commands can directly mutate
server state for fixtures; enable them only for isolated tests and distinguish
injected setup from ordinary player acceptance.

The native bridge and script layer are maintained by TLA. The port originated in
a sibling project; that origin does not prove continued byte identity or current
runtime qualification. It covers observation, player-control commands, login and
dialogs. Historical runs are separated below from current procedures. Higher-level features that depend on systems TLA does not yet expose
the same way (roster, admin prep, factions, overwatch, global-map interests, the advisory/agent-runtime
layer, content-specific playtest runners) are added incrementally — see the roadmap at the end.

Reading routes: [launch](#running-it-locally), [validation](#validation),
[MCP/screenshots](#mcp-adapter), [playtest runners](#playtest-runner),
[protocol/command reference](AiControlProtocol.md),
[historical verification](History/AiControl-2026.md).

## Architecture

Two layers:

- `Scripts/AiControl.fos` (CLIENT) builds structured observation snapshots, records client-side events,
  and executes semantic commands through normal player-control paths (`ChosenActions`, `CurPlayer.ServerCall`).
- `SourceExt/ClientAiBridge.cpp` (CLIENT) exposes a localhost TCP line protocol (one JSON object per line).
  It is enabled per client and stores its state in `ClientExtData` (`SourceExt/ClientExtension.h`), which is
  allocated in the `ClientInitHook` engine hook.

`Tools/AiControlMcp/ai_control_mcp.py` wraps that TCP protocol as a stdio MCP server for model hosts. The
embedded-client index used for multi-client port spacing comes from `Game.GetEmbeddedClientIndex()`
(`SourceExt/ClientExtension.cpp`).

Normal gameplay requests remain server-validated. QA mutation endpoints have
their own explicit test-only authority and do not establish normal prerequisites.

## Configuration

Declared in `Scripts/AiControl.fos` (`///@ Setting Client ...`) with defaults in `TLA.fomain`:

| Setting | Default | Purpose |
|---------|---------|---------|
| `AiControl.Enabled` | `False` | Start the client TCP bridge when the client boots (`Game.OnStart`) |
| `AiControl.Host` | `127.0.0.1` | Bind address for the TCP listener |
| `AiControl.Port` | `43011` | TCP port used by external adapters |
| `AiControl.PortStride` | `1` | Port spacing for embedded multi-client launches: client index N binds `Port + (N-1)*PortStride` |
| `AiControl.Token` | empty | Optional shared token required before non-auth bridge calls |
| `AiControl.MaxQueuedCommands` | `64` | Back-pressure limit for queued commands |
| `AiControl.MaxEvents` | `512` | Ring-buffer size for the client event history |
| `AiControl.ObservationInterval` | `250` | Milliseconds between observation snapshots |
| `AiControl.MaxObservedEntities` | `80` | Per-snapshot cap for visible critters / map items / inventory |
| `AiControl.SkipRosterOnLogin` | `False` | Reserved (roster not ported in v1) |
| `AiControl.ProfileObservationThresholdMs` | `0` | Reserved (profiling not ported in v1) |
| `AiControl.CaptureRawInputEvents` | `False` | Reserved (raw input capture not ported in v1) |
| `AiControl.AllowQaCommands` | `False` | Gate (Common, read on client+server) for the `qa_*` setup/fixture commands. Keep off outside test harnesses. |

Keep the listener on loopback. It binds the local client as a remotely controllable process if exposed.

## Native bridge protocol

Moved to [Native bridge protocol](AiControlProtocol.md#native-bridge-protocol).

## Observation (schemaVersion 1)

Moved to [Observation (schemaVersion 1)](AiControlProtocol.md#observation-schemaversion-1).

## Events

Moved to [Events](AiControlProtocol.md#events).

## Commands

Moved to [Commands](AiControlProtocol.md#commands).

### QA setup commands (test-only)

Moved to [QA setup commands (test-only)](AiControlProtocol.md#qa-setup-commands-test-only).

### Environment queries

Moved to [Environment queries](AiControlProtocol.md#environment-queries).

## MCP adapter

`Tools/AiControlMcp/ai_control_mcp.py` is a dependency-free stdio MCP adapter (ported from the sibling
project, renamed to the `tla_` / `TLA_AI_*` / `tla://` namespace). Supporting modules:
`ai_control_runner.py` (stdio MCP client + command/observation/launch/log helpers), `ai_control_advisory.py`,
`ai_control_guides.py`, `ai_control_launch.py` (launch manifest from `TLA.fomain` + `.vscode/tasks.json`),
`ai_control_protocol.py`. `smoke_ai_control_mcp.py` is the smoke runner.

Environment variables: `TLA_AI_HOST` (`127.0.0.1`), `TLA_AI_PORT` (`43011`), `TLA_AI_TOKEN` (empty),
`TLA_AI_TIMEOUT` (`3`), `TLA_WORKSPACE_ROOT` (adapter grandparent).

Core MCP tools include `tla_ping`, `tla_status`, `tla_observe`, `tla_step`, `tla_sync`, `tla_events`,
`tla_next_events`, `tla_act`, `tla_clear_actions`, the typed command tools (`tla_move_to_hex`, `tla_talk_to`,
`tla_attack_entity`, `tla_pick_item`, `tla_use_item`, `tla_use_skill`, `tla_craft`, `tla_barter_transfer`,
`tla_barter_offer`, `tla_barter_return_dialog`, `tla_close_dialog`, `tla_show_context_screen`,
`tla_ui_answer`, `tla_qa_show_dialog_box`, ...), launch tools
(`tla_launch*`, `tla_processes`, `tla_logs`), and the static schema/guide resources. Many advisory/agent
tools were carried over from the sibling project and still assume sibling-project content; treat them as
provisional until adapted to TLA content.

TLA observations expose map positions as flat `hexX` / `hexY` fields. The navigation adapter normalizes those
fields to its generic `hex: {x, y}` shape for the chosen critter, visible critters, and map items before planning.
The current TLA bridge implements `path`, but not the sibling project's `tactical_path` query. `tla_nav_plan` and
`tla_find_safe_step` therefore fall back to `path` only when the bridge explicitly reports
`unknown_environment_query` or `unsupported_environment_query`; the result records `queryFallback`, while every
other environment-query failure is returned unchanged.

### Verified engine screenshots

`tla_save_screenshot` captures the composed render target (world plus GUI). Use a standalone graphical client for
visual regression runs: the embedded headless client produced structurally valid TGA files whose framebuffer was
entirely black in the verified Windows setup. The headless mode remains useful for non-visual bridge/gameplay
automation. The tool always waits for its own `command_completed`; callers do not need to set
`waitForCompletion`. Before capture it optionally waits `settleMs` (250 ms by default), removes an old target,
and confines the optional `.tga` path to `TLA_WORKSPACE_ROOT`. With no path it writes a timestamped file under
`Workspace/AiControlScreenshots/`.

The MCP capture result is a verification record, not just an acknowledgement: absolute and workspace-relative paths,
existence/byte size, dimensions, pixel depth, SHA-256, TGA payload boundaries, sampled color/luminance metrics,
`blankLike`, command completion, and `verified`. `verified=true` means command completion succeeded, the new file
is an uncompressed 24/32-bit true-color TGA with a complete payload, and the sampled frame is not blank-like.
Bad input (wrong extension or a path escape) is MCP `-32602`; command/file/format/blank failures are returned as
`verified=false` with a structured `failure.stage` and `failure.message`. This generic check proves that a frame
was produced, not that a particular window rendered its controls; the audit runners add content-specific ROI
oracles below.

For deterministic screen audits, direct `tla_show_screen` is safe only for parameterless screens in the right
game state:

| Audit path | Screens | Notes |
|------------|---------|-------|
| Direct show/capture/hide while in game | `Options`, `Inventory`, `Character`, `PipBoy`, `FixBoy`, `Menu`, `Credits` | No required `params`; inventory/character/PDA/crafting still need a chosen critter for meaningful content |
| Open through the real mechanic, then capture | `Dialog`, `Barter`, `PickUp`, `Split`, `Aim`, `Radio`, `Timer`, `Use`, `SkillBox`, `Elevator`, `TownView`, `GmTown`, `Say`, `SayExtended`, `DialogBox`, `InputBox` | Their screen code consumes a target/item/location/dialog context; direct show can assert or render invalid state |
| State-owned roots | `Login`, `Registration`, `Game`, `GlobalMap`, `Wait` | Reach these through connection, registration, map transfer, or wait state rather than stacking them over gameplay |

The standalone audit runner uses the shared MCP client, waits for show/hide completion, checks that each screen
became active, and applies a content oracle: controls for Options, stats for Inventory/Character, PipBoy body,
FixBoy recipes, Menu buttons, and Credits text. Unknown screens are not marked verified unless the diagnostic
`--allow-generic` opt-in is supplied. The runner writes a JSON manifest:

```bash
python Tools/AiControlMcp/tla_gui_screenshot_test.py
python Tools/AiControlMcp/tla_gui_screenshot_test.py --screens Options,Inventory,PipBoy \
  --output-dir Workspace/AiControlScreenshots/gui-smoke
```

`tla_context_gui_playtest.py` covers nine parameterized windows: `SkillBox`, `Aim`, `Split`, `Timer`,
`Use`, `PickUp`, `Radio`, `Elevator`, and `DialogBox`. It selects real observed items/targets using the
capability metadata above, opens the first five through `tla_show_context_screen`, opens PickUp and Radio
through their normal mechanics, captures Elevator when already active or enters it through an authored trigger
hex, and obtains DialogBox from `tla_qa_show_dialog_box`. Each capture has a window-specific ROI oracle.
The `Aim` oracle checks its authored green labels rather than the gold text used by several other windows.
DialogBox is closed with `tla_ui_answer` using `expectedSession`; a delayed answer cannot act on a replacement
prompt. Its semantic buttons also expose safety metadata: `answer_0` is `role=confirm`, `dangerous=true`, while
`answer_1` is the safe `role=cancel` choice. Agents must not treat an unlabelled first button as a harmless default.

The default run captures every context that is available in the current world state. `--require-all` turns a
missing prerequisite into failure. Elevator needs a known real trigger unless it is already active:

```bash
python Tools/AiControlMcp/tla_context_gui_playtest.py \
  --output-dir Workspace/AiControlScreenshots/context-gui
# First use tla_qa_teleport_map with mariposa/mariposa_level1.
python Tools/AiControlMcp/tla_context_gui_playtest.py --screens Elevator \
  --elevator-trigger-hex 101 43 --require-all
```

A live standalone-client run passed the eight Arroyo contexts available there plus the Mariposa Elevator run
(**9/9** total). Timer was also verified beyond pixels: `timer:599` consumed one inventory dynamite and created
one `active_dynamite`. The elevator exposed `level_1` through `level_3`; answering `level_2` through
`tla_ui_answer` transferred the chosen from `mariposa_level1` to `mariposa_level2`.

The runner deliberately does not bypass item safety: Split needs an owned stack, Timer an owned timer-capable
item, Use an owned `canUseOnSmth` item and a real target, PickUp a visible safe unlocked container, and Radio
an owned radio. Prepare those prerequisites through ordinary gameplay or gated QA setup commands.

`tla_barter_playtest.py` covers the contextual `Dialog` → NPC `Barter` → `Dialog` lifecycle through MCP
tools. It requires an in-game chosen critter and `AiControl.AllowQaCommands=True`; the runner grants caps,
teleports to the requested trader, verifies pricing/session metadata and a completed offer refresh, captures all
three UI states, and requires the assembled Barter frame to contain all four item panels, both totals, and the
header display. It closes the dialog and writes `report.json` alongside the verified TGA files:

```bash
python Tools/AiControlMcp/tla_barter_playtest.py --map arroyo --npc-dialog-id arroyo_doc --hex 77 103 \
  --output Workspace/AiControlBarterPlaytests/arroyo-doc
# Add --hex X Y when the trader is not visible from the map entry.
```

Use `tla_window_screenshot` only when the OS window itself matters (window chrome, presentation under a specific
desktop compositor, or a renderer diagnostic); it is Windows-only and is not the canonical composed-frame check.

> NOTE: The adapter's launch orchestration reads TLA subconfigs (`Unpackaged`, `LocalTest`, `PublicGame`).
> TLA does not use the sibling project's scene system, so `startupScenes` is empty. For now, launch the
> game manually (below) and point the adapter at the running bridge.

## Running it locally

Build once: `Build :: TLA_Client` (compiles the native bridge) and `Bake Resources`.

### Recommended: persistent server + windowed client

This is the robust setup for interactive testing — the server stays up regardless of client login state.

```bash
# 1) Persistent headless server (no embedded client), stays up:
cmake --build Build/Auto --config RelWithDebInfo --target TLA_ServerHeadless
./Binaries/Server-Windows-win64/TLA_ServerHeadless.exe --ApplySubConfig LocalTest    # wait for "Start server complete!"

# 2) A client that hosts the bridge on 127.0.0.1:43011 (windowed; D3D11 works over RDP):
./Binaries/Client-Windows-win64/TLA_Client.exe --ApplySubConfig LocalTest --AiControl.Enabled True
```

Then drive it: connect to the bridge, send `register` (a fresh character spawns and enters the game), and
poll `observe` until `hasChosen` / `hasMap` are true. On the same persistent server (in-memory DB) a name
can be registered once; use `login` to re-enter an existing character after a client relaunch.

### One-shot headless (embedded client)

```bash
./Binaries/Server-Windows-win64/TLA_ServerHeadless.exe \
    --ApplySubConfig LocalTest --AiControl.Enabled True --Server.AutoStartClientOnServer 1
```

The embedded headless client boots, fires `Game.OnStart`, and starts the bridge. This mode is **one-shot**:
the headless app quits when its embedded client disconnects (e.g. a failed/finished login), so it is best
for a single scripted run, not long iterative sessions. Use the persistent-server setup above for those.

## Validation

1. `Build :: TLA_Client` — native bridge compiles/links (rebuilds the generated script API for the new
   `///@ ExportMethod` / `///@ EngineHook`). For headless smoke also build `TLA_ServerHeadless`.
2. `Compile AngelScript` (or `Bake Resources`) — `Scripts/AiControl.fos` sees the generated client exports.
3. `python Tools/AiControlMcp/smoke_ai_control_mcp.py --static-only` — schema/tool/resource/prompt discovery.
4. `python -m unittest Tools/AiControlMcp/test_ai_control_screenshot.py` — path confinement, raw TGA validation,
   blank-like detection, event metadata, and typed command payload checks.
5. Launch a client with `AiControl.Enabled = True` (above), then
   `python Tools/AiControlMcp/smoke_ai_control_mcp.py` — `tla_ping`, `tla_status`, `tla_observe`, the event
   cursor, and one harmless `tla_clear_actions` round-trip.
6. With an in-game chosen critter, run `python Tools/AiControlMcp/tla_gui_screenshot_test.py` and inspect its
   manifest plus TGA files. Run `python Tools/AiControlMcp/tla_context_gui_playtest.py` for the nine contextual
   windows; use `--require-all` only after preparing every real item/map prerequisite.

## Playtest runner

`Tools/AiControlMcp/tla_mechanics_playtest.py` is a self-contained (no MCP adapter needed) reachability-aware
mechanics run over the bridge: it logs in (or `--register`), summarizes the observation, reachability-probes
visible critters/items with `environment_query path`, navigates to the nearest reachable targets, attempts a
talk, and writes a JSON report (`--report`). Run it against a client started as above:

```bash
python Tools/AiControlMcp/tla_mechanics_playtest.py --name TestBot1 --register --report Workspace/run.json
# run on a real content map (needs AiControl.AllowQaCommands=True on server+client):
python Tools/AiControlMcp/tla_mechanics_playtest.py --register --teleport-map arroyo --report Workspace/arroyo.json
```

`Tools/AiControlMcp/tla_quest_runner.py` runs a **full quest cycle** (accept → travel → turn in) end-to-end,
asserting the quest property advances at each stage. Quest specs are data-driven (`QUESTS` dict). Four are
verified across three towns and three shapes: `cassidy_letter` (Arroyo → Vault City delivery),
`arroyo_mynoc_oil` (accept + turn-in on one giver), `den_smitty_robot` (Den: accept → repair the Mr. Handy at
a workbench → report, skill + item gated, four stages) and `klam_vaccination` (Klamath: accept → vaccinate
sub-task → report, a `Server`-scope quest flag verified via `qa_get_prop`). Needs `AiControl.AllowQaCommands=True`
and a Russian client (`--Client.Language russ`) so dialog text matches the Russian answer keywords.

```bash
python Tools/AiControlMcp/tla_quest_runner.py --list
python Tools/AiControlMcp/tla_quest_runner.py --quest cassidy_letter --name QuestCassidy1 --register \
  --require-exercised --report Workspace/cassidy.json
python Tools/AiControlMcp/tla_quest_runner.py --quest klam_vaccination --name QuestKlam1 --register \
  --require-exercised --report Workspace/klam.json
```

The same runner can discover localized answer paths before a quest spec is authored. `--trace-dialog`
replays bounded paths against a visible NPC, reads the requested quest flag through the asynchronous
server-authoritative `qa_get_prop` round-trip, and emits the answers that increase it. Candidates are ranked by
stage advance and include the full visible `node_path` plus stable Russian keyword substrings:

```bash
python Tools/AiControlMcp/tla_quest_runner.py --trace-dialog --map arroyo \
  --npc CassidyStage4 --dialog arroyo_cassidy --flag ArroyoCassidyLetter \
  --npc-hex 82 113 --name TraceCass --register --trace-max-candidates 1 \
  --report Build/_artifacts/trace-dialog/cassidy.json
```

Run the server with `--ServerNetwork.InactivityDisconnectTime 0` for a long trace. Use a disposable QA
character: the runner restores the requested flag in `finally`, but arbitrary authored side effects such as
items, dialog cooldowns, and other properties cannot be rolled back generically. `--setup-json` accepts either
a JSON array or a path/`@path` to an array using the same `prop` / `game_prop` / `item` entries as quest specs.
The traversal is bounded by `--trace-max-depth` (12), `--trace-max-paths` (96),
`--trace-max-candidates` (8), and an internal `--trace-max-seconds` wall-clock budget (180). It uses
priority-guided replay, tolerates one-shot first-meeting roots and randomized greeting/exit text, retries a
missing or delayed `qa_get_prop` response under async load, and correlates delayed replies by request id.
Property setup/reset uses the correlated `qa_prop_set` acknowledgement and resends an unacknowledged write;
confirmed same-map teleports and `talk_to` actions are retried as well. First-time Debug
    map loads get a 90-second observed transition window, configurable with `--map-timeout`; success still requires
    observing the requested `map.protoId`. Reports expose `truncated`, `time_limit_reached`,
`branch_errors`, `flag_restored`, and `restore_error` explicitly.

A spec stage can carry a `setup` list — `{"prop"|"game_prop"|"item": name, "value"|"count": n}` — applied
after the teleport and before talking, to satisfy a giver's prerequisite demands (an attribute like
`Intellect`, a `CurrentHp`, a GAME flag, or a required inventory item). The dialog navigator auto-advances
single-answer intros, never bails out on an exit-like answer while a fresh one remains, and remembers chosen
answers across re-opens so each re-open explores a new branch — which is what makes a topic-tree giver like
Mynoc reachable without hand-coding the exact path. Current specs use monotonic stage targets: a completed
character reports `already_satisfied=true` instead of wandering an obsolete dialog branch. Use
`--require-exercised` for regression runs that must verify at least one real state transition.

## Verified end-to-end (2026-07-11)

Moved to [Verified end-to-end (2026-07-11)](History/AiControl-2026.md#verified-end-to-end-2026-07-11).

### Dialog trace seeds (2026-08-08)

Moved to [Dialog trace seeds (2026-08-08)](History/AiControl-2026.md#dialog-trace-seeds-2026-08-08).

### Mechanics beyond dialog (verified 2026-06-21)

Moved to [Mechanics beyond dialog (verified 2026-06-21)](History/AiControl-2026.md#mechanics-beyond-dialog-verified-2026-06-21).

### Adding more quests (what still needs care)

Moved to [Adding more quests (what still needs care)](History/AiControl-2026.md#adding-more-quests-what-still-needs-care).

## Fixed: empty dialog text (key mismatch)

Moved to [Fixed: empty dialog text (key mismatch)](History/AiControl-2026.md#fixed-empty-dialog-text-key-mismatch).

### Fixed: empty NPC floating text (numbered dialog strings)

Moved to [Fixed: empty NPC floating text (numbered dialog strings)](History/AiControl-2026.md#fixed-empty-npc-floating-text-numbered-dialog-strings).

### Fixed: empty dialog text in `@text` format tags (poker / roulette / banker / NPC names)

Moved to [Fixed: empty dialog text in `@text` format tags (poker / roulette / banker / NPC names)](History/AiControl-2026.md#fixed-empty-dialog-text-in-text-format-tags-poker--roulette--banker--npc-names).

### Fixed: empty proto-name `@text` tags (critter / item / location names)

Moved to [Fixed: empty proto-name `@text` tags (critter / item / location names)](History/AiControl-2026.md#fixed-empty-proto-name-text-tags-critter--item--location-names).

## Roadmap (next)

The earlier roadmap and its completed-work narrative are preserved in
[the historical record](History/AiControl-2026.md#roadmap-next). Re-evaluate
remaining world-map/quest observation, content playtests and UI affordances
against current dispatch and fixtures before scheduling them. An old roadmap
entry or historical pass is not proof that a feature is present or qualified.
