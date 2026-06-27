# AI Control Bridge (TLA)

The AI control bridge lets an external tool (an MCP host / model) observe and control a real TLA
client over a localhost TCP socket, without giving server/admin powers. One bridge connection controls
one client; commands become ordinary client actions and are still validated server-side through the
normal RPC flow (cooldowns, visibility, range, item ownership, dialog state).

This is a **foundation port** adapted from the sibling project (`H:/lf-29`). The native bridge is shared
verbatim; the script layer (`Scripts/AiControl.fos`) was rewritten against TLA's own client API. It covers
observation, events, the core player-control commands, register/login, and dialog observation, all verified
end-to-end against a running client. Higher-level features that depend on systems TLA does not yet expose
the same way (roster, admin prep, factions, overwatch, global-map interests, the advisory/agent-runtime
layer, content-specific playtest runners) are added incrementally — see the roadmap at the end.

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

The server still validates every resulting gameplay request normally; the bridge is not a server-authority bypass.

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
| `AiControl.AllowQaCommands` | `False` | Gate (Common, read on client+server) for the `qa_teleport_*` test commands. Keep off outside test harnesses. |

Keep the listener on loopback. It binds the local client as a remotely controllable process if exposed.

## Native bridge protocol

`ClientAiBridge.cpp` listens for newline-delimited JSON-RPC-like messages. Request shape:

```json
{"jsonrpc":"2.0","id":1,"method":"observe","params":{}}
```

| Method | Params | Result |
|--------|--------|--------|
| `auth` | `{ "token": "..." }` | `{ "authorized": true/false }` |
| `ping` | `{}` | `{ "ok": true }` |
| `status` | `{}` | Queue sizes, host/port, observation sequence, last native error |
| `observe` | `{}` | Latest structured observation snapshot |
| `events` | `{ "afterSeq": 0, "limit": 100 }` | Client events after a sequence number |
| `act` | command object | Enqueues a command for the next client loop |

If `AiControl.Token` is non-empty, call `auth` first on every connection. The MCP adapter does this
automatically when `TLA_AI_TOKEN` / `--token` is supplied.

## Observation (schemaVersion 1)

Top-level keys: `schemaVersion`, `seq`, `clientIndex`, `connected`, `hasMap`, `hasChosen`, `account`,
`screen`, `mouse`, `chosen`, `map`, `critters`, `mapItems`, `inventory`, `quests`, `dialog`,
`availableActions`.

Consumers must branch on `connected`, `hasMap`, `hasChosen` instead of assuming a current player/map/chosen.

- `chosen`: id, name, hexX/Y, level, currentHp, maxHp, experience, currentAp, actionPoints, isAlive,
  inCombat (`TimeoutBattle` active), inSneakMode.
- `map`: id, protoId, width, height.
- `critters`: visible critters from `CurMap.GetCritters(CritterFindType::Any)` (chosen excluded): id,
  name, hexX/Y, isAlive, inCombat, dialogId.
- `mapItems`: visible map items tracked from `OnItemMapIn` / `OnItemMapOut`: id, protoId, hexX/Y, count.
- `inventory`: `Chosen.GetItems()`: id, protoId, count, slot.
- `quests`: active quests of the chosen. TLA models quests as per-quest `uint8` critter properties in the
  `Quests` group (value = stage, 0 = not started), not a `QuestProgress` array — so this lists the non-zero
  quest properties as `{ name, value }`. (Resolved quest titles/objective text are a later addition.)
- `screen`: active screen name, `modalActive` (`Gui::IsModalScreenActive()`), and the active-screen list.
- `dialog`: `{ active, dialogId, talkerId, text, answers }`. Captured from `Dialogs.fos::ReceiveDialogContext`
  (the data source, before the screen `params` dict is consumed by `Gui::ShowScreen`) via
  `AiControl::SetDialogState` / `ClearDialogState`. Drive dialogs by answer index with `dialog_answer`.
  `text`/`answers` carry the resolved speech/answer strings (see the dialog text-key fix note below).
- `availableActions`: the list of supported command types (richer affordance hints are adapter-side).

## Events

Pushed for client lifecycle/world changes: `bridge_started` / `bridge_stopped`, `connecting` /
`connecting_failed` / `connected` / `disconnected`, `login_success`, `info_message`, `input_lost`,
`map_load` / `map_unload`, `critter_in` / `critter_out`, `item_map_in` / `item_map_out`,
`item_inv_in` / `item_inv_out`, `receive_items`, `screen_change`, `console_message`, and the native
`command_completed`. The native bridge also emits `runtime_exception` events when the engine log shows
script exceptions, assertions, or fatal/error markers.

The event buffer is in-memory only. Keep the latest `seq` from `events` and ask for events after it.

## Commands

Queued through `act`, consumed by the client loop, routed through normal player intent:

| Type | Main params | Behavior |
|------|-------------|----------|
| `register` | optional `stringArg` (name) | Register a fresh character and enter the game through `PlayerRegistration` (default name `TestBot<clientIndex>`; builds a valid SPECIAL/skills/traits set). Drives the normal `Game.Connect` + `RegisterNewPlayer` path without `TryExit`. |
| `login` | optional `stringArg` (name) | Log in an existing character through `LoginExistingPlayer`. |
| `move_to_hex` | `x`, `y`, optional `intArg` (cut distance), `append` | `Tla::ChosenMove` |
| `talk_to` | `targetId`, `append` | `Tla::ChosenTalkNpc` |
| `loot_critter` | `targetId`, `append` | `Tla::ChosenPickCrit` |
| `attack_entity` | `targetId`, `intArg` (mode) | `CurPlayer.ServerCall.Attack` |
| `pick_item` | `itemId`, `append` | `Tla::ChosenPickItem` (proto/hex resolved from the item) |
| `pick_hex` | `x`, `y`, `append` | Pick a visible map item at the hex |
| `use_item` | `itemId`, optional `targetId`, `intArg` (timer) | `Tla::ChosenUseItem` (self or target critter) |
| `use_skill` | `stringArg` (skill `CritterProperty` name, e.g. `SkillFirstAid`/`SkillLockpick`/`SkillRepair`), optional `targetId`/`itemId`/`x`/`y` | `CurPlayer.ServerCall.UseSkill`. With no target it applies to the chosen (self-heal etc.). |
| `reload` | `itemId`, `auxId` (ammo) | `CurPlayer.ServerCall.ReloadWeapon` |
| `unload` | `itemId` | `Tla::ChosenUnloadWeapon` |
| `move_item` | `itemId`, `intArg` (slot) | `CurPlayer.ServerCall.MoveInvItem` |
| `drop_item` | `itemId`, `intArg` (count) | `CurPlayer.ServerCall.DropInvItem` |
| `operate_container` | `itemId`, `intArg` (bit0 take, bit1 all, `>>2` count) | `CurPlayer.ServerCall.OperateContainer` (loot/container grid: take items) |
| `craft` | `intArg` (craft id) | `CurPlayer.ServerCall.Rpc_CraftItem(FixboyButton, id, 0)` — runs a FixBoy recipe (server checks skill/materials/tools, consumes resources, grants the item) |
| `toggle_sneak` | `append` | `Tla::ChosenSneak` — **sneak is stubbed in TLA**, returns `sneak_not_implemented_in_game` |
| `dialog_answer` | `intArg` (answer index; `0xF2`=continue/close) | `CurPlayer.ServerCall.SpeechAnswer` |
| `say` | `stringArg`, `intArg` (`SayType`) | `CurPlayer.ServerCall.ReceiveChosenSay` |
| `clear_actions` | none | Clear queued client actions |
| `close_screen` / `show_screen` / `hide_screen` | `stringArg` (`GuiScreen` name) | GUI screen control |
| `save_screenshot` | `stringArg` (path) | `Game.SaveScreenshot` (framebuffer readback) |
| `set_resolution` | `x`, `y` | `Game.SetResolution` |
| `toggle_fullscreen` | none | `Game.ToggleFullscreen` |
| `set_mouse_pos` | `screenX`, `screenY` | `Game.SetForcedMousePos` |
| `mouse_click` | `screenX`, `screenY`, `intArg` (`MouseButton`) | `Game.SimulateMouseClick` |
| `key_press` | `intArg` (`KeyCode`), `stringArg` | `Game.SimulateKeyboardPress` |
| `environment_query` | `intArg` (queryId), `screenX`/`screenY` (from-hex, `-1` = chosen), `x`/`y` (to-hex), `stringArg` (options) | Client geometry/path query; publishes an `environment_query_result` event by `queryId`. |

Commands not yet supported in TLA return `unsupported:<type>` and `success=false`.

### QA setup commands (test-only)

Gated by `AiControl.AllowQaCommands = True` (off by default, checked on both client and server). They route
through server RemoteCalls that move the player's controlled critter; they are a test-harness setup surface,
not normal player abilities. Use them to reach content for mechanics/quest runs.

| Type | Main params | Behavior |
|------|-------------|----------|
| `qa_teleport_hex` | `x`, `y` | Same-map reposition (`Critter.TransferToHex`); the engine snaps to the nearest movable hex. Useful to reach otherwise-blocked spots. |
| `qa_teleport_map` | `stringArg` (map/location proto), optional `x`/`y` | Teleport to a content map. Resolves `Game.GetMap` → `Game.GetLocation` → and, if the static location is not yet instantiated, `Location::CreateLocation` a fresh instance; then transfers to the location's map whose `ProtoId` matches the requested pid (so `arroyo` lands on the `arroyo` village map with its quest-givers), else its first map (`"0"` entry when no hex given). |
| `qa_teleport_global` | none | `Critter.TransferToGlobal`. Note: a no-op from the `repl1` replication/limbo start map (it has no global coordinates); use `qa_teleport_map` to reach content. |
| `qa_set_prop` | `stringArg` (CritterProperty name), `intArg` (value) | Set an int CRITTER property (`cr.SetAsInt`) — reputation/loyalty values, a prior quest stage, `CurrentHp`, limb-damage flags, etc. |
| `qa_set_game_prop` | `stringArg` (GameProperty name), `intArg` (value) | Set an int GAME property (`Game.SetAsInt`) — world/quest flags that live on the game singleton, not the critter (e.g. `DenVirginIsAway`). Many dialog demands gate on these, so `qa_set_prop` alone can't satisfy them. |
| `qa_give_item` | `stringArg` (item proto), `intArg` (count) | Give an item (`cr.AddItem`) — for quest items the giver doesn't hand out, or starting gear. |
| `qa_get_prop` | `stringArg` (CritterProperty name) | Authoritative SERVER-side read of an int critter property. The server reads `cr.GetAsInt` and calls the client back (`AiControlReceiveQaProp`), which publishes a `qa_prop_value` event (`{prop, value}`). Needed because ~1/3 of quest flags are `Server`-scope (not `OwnerSync`) and therefore never appear in the client observation's `quests` — the only way to verify them is this round-trip. |
| `qa_get_text` | `stringArg` (dialog id), `intArg` (string number) | Resolve a numbered NPC floating-text via `MsgStr::DialogTextKey` and return it in the command message (`text=<…>`). Debug tool for the numbered-text fix below; empty means the string isn't authored for that dialog. |
| `qa_format_tags` | `stringArg` (text with tags) | Run a raw string through `Game.FormatTags` (resolves `@text`/`@arg`/`@sex`/… client-side) and return the result (`result=<…>`). Used to verify the three-token `@text Dialogs <dialogName> <key>@` path end-to-end. |

`qa_get_prop` is asynchronous: the value arrives as a `qa_prop_value` event, not in the command's own
completion message. Snapshot the event cursor (max `seq`), send `qa_get_prop`, then poll `events` for the
`qa_prop_value` whose `prop` matches. `tla_quest_runner.py`'s `read_quest` does exactly this — it reads the
client observation first (fast, for `OwnerSync` quests) and falls back to `qa_get_prop` when the property is
absent client-side (`Server`-scope quests such as `KlamVaccination`).

`qa_teleport_map` accepts `locationPid/mapProto` (e.g. `vault_city/vcity`) to land on a specific sub-map of a
multi-map location. `qa_set_prop` / `qa_give_item` are the prerequisite-setup surface for quests gated by
reputation, faction loyalty, prior quest state, or required items — set those up, then run the quest's normal
dialog flow.

`qa_teleport_map` is the practical way to put a test character on a real content map (e.g.
`qa_teleport_map arroyo` lands on `arroyo_bridge` with its real NPCs). A freshly created location instance is
a sandbox copy of the proto's maps/NPCs — good for exercising map mechanics/dialogs, but not tied to the
canonical world location's quest state.

### Environment queries

`environment_query` runs advisory geometry/path checks against the currently replicated map and publishes
an `environment_query_result` event matched by `queryId`. Options are `"kind;name=value;..."`:

- `path` — reachability from a hex (or the chosen) to a target hex: `reachable`, `pathLength`,
  `directDistance`, `fromMovable`/`toMovable`, and `directions`/`pathHexes`. Use it to skip unreachable
  targets before issuing `move_to_hex` / `talk_to` / `pick_item`.
- `obstacles` — scan a radius (`radius=`, `maxResults=`) around a center hex and list non-movable /
  non-shootable / occupied hexes.
- `trace` — trace a line toward a target (`maxDistance=`, `angle=`) and report where it stops and whether it
  reached the target.

The adapter wraps these as `tla_env_path` / `tla_env_obstacles` / `tla_env_trace`.

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
`tla_attack_entity`, `tla_pick_item`, `tla_use_item`, `tla_say`, `tla_dialog_answer`, ...), launch tools
(`tla_launch*`, `tla_processes`, `tla_logs`), and the static schema/guide resources. Many advisory/agent
tools were carried over from the sibling project and still assume sibling-project content; treat them as
provisional until adapted to TLA content.

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
4. Launch a client with `AiControl.Enabled = True` (above), then
   `python Tools/AiControlMcp/smoke_ai_control_mcp.py` — `tla_ping`, `tla_status`, `tla_observe`, the event
   cursor, and one harmless `tla_clear_actions` round-trip.

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
python Tools/AiControlMcp/tla_quest_runner.py --quest cassidy_letter --report Workspace/cassidy.json
python Tools/AiControlMcp/tla_quest_runner.py --quest klam_vaccination --report Workspace/klam.json
```

A spec stage can carry a `setup` list — `{"prop"|"game_prop"|"item": name, "value"|"count": n}` — applied
after the teleport and before talking, to satisfy a giver's prerequisite demands (an attribute like
`Intellect`, a `CurrentHp`, a GAME flag, or a required inventory item). The dialog navigator auto-advances
single-answer intros, never bails out on an exit-like answer while a fresh one remains, and remembers chosen
answers across re-opens so each re-open explores a new branch — which is what makes a topic-tree giver like
Mynoc reachable without hand-coding the exact path.

## Verified end-to-end (2026-06-21)

- `register` / `login` drive the real TLA auth path; a character spawns and `observe` populates
  `chosen` / `map` / `critters` / `mapItems` / `quests`.
- `move_to_hex` moves the chosen to the exact target hex; `pick_item` / `talk_to` auto-walk to their target;
  `say`, `attack_entity`, `dialog_answer` are accepted and processed; dialogs open and advance by answer index.
- Dialog observation captures `dialogId` / `talkerId` / answer structure (see the dialog note above on empty
  text for start-map `repl_*` dialogs).
- `environment_query path` correctly reports reachable vs unreachable target hexes (`reachable` /
  `pathLength`); `obstacles` lists blocked hexes — used by the playtest runner to pick reachable targets.
- `qa_teleport_hex` repositions on the current map; `qa_teleport_map arroyo` reaches a real content map
  (`arroyo_bridge`) with its real NPCs, where `tla_mechanics_playtest.py --teleport-map arroyo` probes 12/12
  reachable targets and opens a real content dialog (`arroyo_laumer`).
- After the dialog text-key fix, a real quest dialog is read and navigated end-to-end: the agent walked the
  Savinelli caravan-escort dialog on `arroyo_bridge` through 5 readable speeches, choosing meaningful answers.
- A real quest is **accepted with an observable state change**: on the `arroyo` village map the agent talked
  to Cassidy, asked for work, read the offer ("отнеси письмо в Город-Убежище для Синди"), answered "Да,
  конечно", and `observation.quests` then shows `CritterProperty::ArroyoCassidyLetter = 1`, with the
  `letter_to_sindy` item added to inventory. (Caravan-escort quests, by contrast, are correctly time-gated —
  they only accept near departure.)
- **A full quest cycle completes end-to-end** across two cities via teleport: after accepting the Cassidy
  letter at Arroyo, the agent `qa_teleport_map vault_city` → `vcity_courtyard`, reaches Cindy (`vc_cindy` at
  hex `65,55`), reads her dialog ("От Кэссиди?! ... Давай его скорей сюда!"), answers "Вот оно, держи.", and
  the quest advances to `CritterProperty::ArroyoCassidyLetter = 2` with the `letter_to_sindy` item consumed.
  (The `CreateLocation` sandbox instance DOES spawn the map-placed quest NPCs; an earlier "missing Cindy"
  reading was a wrong-hex lookup. After `qa_teleport_hex` on a large map, nudge a couple of hexes and
  re-`observe` to let the client sync nearby critters.)
- The whole cycle is reproducible through `tla_quest_runner.py --quest cassidy_letter` (`ok: true`,
  `ArroyoCassidyLetter` 0 → 1 → 2). `qa_teleport_map` sets `AutoGarbage=false` on the instances it creates
  (and recreates a destroyed one) so a content location persists across runner stages/runs.
- **A second full quest cycle** runs on a single giver: `tla_quest_runner.py --quest arroyo_mynoc_oil`
  (`ok: true`, `ArroyoMynocOil` 0 → 1 → 2) — accept "Я принесу тебе смазку" (gated on `Intellect > 3`, set via
  stage `setup`) then hand in the `oil_can` ("У меня есть маслёнка", item granted via `setup`). This exercises
  the robust navigator (Mynoc's accept lives several topic-tree hops deep behind a first-meeting intro).
- **A third and fourth full quest cycle** broaden the shapes and towns: `den_smitty_robot` (`DenSmittyFixit`
  1 → 2 → 3 → 4 — accept at Smitty, repair his Mr. Handy at the workbench gated on `SkillRepair` + three
  items, report back) and `klam_vaccination` (`KlamVaccination` 0 → 1 → 2 in Klamath — accept Hish's syringe
  task, the three per-brahmin sub-task flags supplied via `setup`, then report). `KlamVaccination` is a
  `Server`-scope flag (not `OwnerSync`), so it is verified through the `qa_get_prop` round-trip, not the client
  observation.
- The QA-setup commands are verified: `qa_set_prop Experience 5000` / `qa_set_prop ArroyoCassidyLetter 1`
  change the observed property; `qa_give_item stimpak 3` / `qa_give_item letter_to_sindy` add the items;
  `qa_get_prop KlamVaccination` reads back a `Server`-scope flag the observation can't see. These unblock and
  verify quests with prerequisites: some givers gate their dialog on faction loyalty or a prior quest stage
  (Arroyo's Todd needs `Dialog::CheckLoyality`), which a fresh QA character lacks — set the prerequisite first,
  then run the quest.
- **Fixed an event-buffer flood:** `OnInputLost` fired every frame while the client window was unfocused (the
  normal state for an automated/headless client), pushing `input_lost` until it evicted real events
  (`command_completed`, `qa_prop_value`) from the bounded event ring. It is now gated behind
  `AiControl.CaptureRawInputEvents` (off by default), so automation runs see a clean event stream.
- `smoke_ai_control_mcp.py` (static and live) and `tla_mechanics_playtest.py` pass.

### Mechanics beyond dialog (verified 2026-06-21)

A battery of non-dialog gameplay mechanics was driven end-to-end on a real client, each with an observable
state change in `chosen` / `inventory` / `mapItems`:

- **Skill use (self first-aid).** `qa_set_prop SkillFirstAid 200` → `qa_set_prop CurrentHp 6` →
  `use_skill SkillFirstAid` (no target ⇒ applied to self); `chosen.currentHp` went 6 → 33.
- **Item use / healing.** `qa_set_prop CurrentHp 5` → `qa_give_item stimpak` → `use_item <stimpak id>`;
  `chosen.currentHp` went 5 → 18 (the stimpak healed the character).
- **Combat / kill.** `qa_give_item super_sledge` → `move_item <weapon id>` to slot `CritterItemSlot::Main`
  (= 1; `Inventory` 0, `Main` 1, `Secondary` 2, `Armor` 3) to equip it → locate a `mob_brahmin` (passive,
  spawns on the Arroyo maps) → `attack_entity` (`mode` 0), re-issued each AP cycle while polling the target's
  `isAlive`; the brahmin died and `chosen.experience` went 0 → 80. Boost damage first with
  `qa_set_prop SkillMeleeWeapons 250` / `qa_set_prop StrengthBase 10`. Attack maps to
  `CurPlayer.ServerCall.Attack(targetId, mode)`.
- **Weapon reload.** `qa_give_item _10mm_pistol` + `qa_give_item _10mm_ap 30` → `move_item` the pistol to the
  `Main` slot → `reload <pistol id>` (accepted).
- **Equip / inventory move.** `move_item <id> <slot>` — verified round-tripping a `_10mm_pistol` through
  `Main` (1) → `Secondary` (2) → `Inventory` (0) with the observed `inventory[].slot` matching each request.
- **Drop.** `drop_item <id>` puts the item on the ground (it appears in `mapItems`). (Ground re-pickup was
  timing-flaky in the batch.)
- **Crafting (FixBoy).** `qa_set_prop SkillOutdoorsman 120` → `qa_give_item brahmin_skin 3` / `pocket_lint` /
  `rope` / `knife` → `craft 1` (recipe id 1 = `leather_armor`); the armour appeared in `inventory` and the
  resources were consumed (`brahmin_skin` 3 → 1). The server checks the recipe's skill/material/tool demands
  and only crafts when they pass.
- **Barter.** Teleport next to a merchant (Arroyo `arroyo_cassidy` at `(82,113)`), `talk_to`, then pick the
  barter answer ("Может, поторгуем?"); `chosen`'s active `screen` becomes `GuiScreen::Barter`. The barter
  answer is the engine `Answer Barter` link, which routes through `Barter::StartNpcBarter`.
- **Loot / container grid.** Kill a critter, then `loot_critter <id>` opens `GuiScreen::PickUp` and
  `operate_container` (`intArg=3` = take + all) pulls its inventory. Verified on a `mob_brahmin` corpse.
- **Global-map travel does NOT work from a sandbox map (and corrupts transfer state).** `qa_teleport_global`
  (`TransferToGlobal`) is a no-op from the `qa_teleport_map` sandbox instances (they carry no valid worldmap
  position), and after calling it the character's hex transfers stop applying (a stuck transfer state) — a
  fresh character recovers. Real global-map travel needs canonical world/town state, not a `CreateLocation`
  sandbox; treat `qa_teleport_global` as unsupported there. Sleeping/rest is likewise not a general mechanic
  in TLA (only mining has a `STR_NEED_REST` gate).
- **Sneak is NOT implemented in TLA.** `toggle_sneak` never changes `chosen.inSneakMode`, because the game
  itself stubs it: the `Tla::ChosenSneak` action body has its `Game.CustomCall(...)` commented out
  (`ChosenActions.fos`) and the `UseSneak` RemoteCall is disabled (commented `///` not `///@`, body inside
  `/* */`). The bridge now returns `sneak_not_implemented_in_game` instead of silently queuing a no-op — a
  game-content gap, not a bridge defect.

### Adding more quests (what still needs care)

The upgraded navigator (auto-advance intros, strong exit-avoidance, seen-tracking across re-opens) handles
both a simple giver (Cassidy) and a deep topic-tree giver (Mynoc). What remains per-quest is mostly *getting
the right answers to appear*, via stage `setup` and the right client language:

- **Localization.** The default client runs `Client.Language = engl`, so any NPC that *has* an English
  translation shows English answers and the Russian `prefer` keywords never match. **Run the client with
  `--Client.Language russ`** (the specs are written from the `.fodlg` `[Text russ]` source).
- **Prerequisite demands.** A quest answer can be hidden behind a critter property (`Intellect`, `CurrentHp`
  for Doc's `IsToHeal`), an inventory item (Mynoc's `oil_can`), or a GAME flag — supply them with stage
  `setup` (`qa_set_prop` for critter props, `qa_set_game_prop` for game props, `qa_give_item` for items).
- **Non-quest flags.** Some "quest-like" props are not in `CritterPropertyGroup::Quests`, so they never appear
  in `observation.quests` (Arroyo `ArroyoDocHealing` is a `Server` flag, `Max = 2`). Pick targets that *are*
  `Group = Quests` if you want to assert progress from the observation.
- **Known content-side snags** (need a fix in the content/baker, not the runner): Arroyo's Todd never opens a
  dialog at all (a guard, not a loyalty gate — default `npc.Loyality.get(cr.Id, 5)` = 5 passes his `@! 1`);
  Den Mom's "Virginia" accept answer stays hidden even after `qa_set_game_prop DenVirginIsAway 0`, because the
  demand is written `Demand Property Player DenVirginIsAway` against a property declared `Property Game` — a
  scope mismatch the baker resolves to a value the answer can't satisfy.

The `QUESTS` dict ships three verified flows plus a `NOTE` documenting these knobs:

- `cassidy_letter` — accept at Arroyo, deliver across town to Vault City (`ArroyoCassidyLetter` 0 → 1 → 2).
- `arroyo_mynoc_oil` — accept + turn-in at one giver, gated by `Intellect` and an `oil_can` item
  (`ArroyoMynocOil` 0 → 1 → 2).
- `den_smitty_robot` — four stages in one town: accept at Smitty → examine the Mr. Handy robot (needs
  `SkillRepair > 59`) → repair it (needs `pump_parts` + `oil_can` + `super_tool_kit`) → report back
  (`DenSmittyFixit` 1 → 2 → 3 → 4). Shows a quest gated by both a skill and inventory items, all supplied via
  stage `setup`.

Adding a quest is: pick a `Group = Quests` target, give each stage its `setup`, and run once against a Russian
client to confirm.

## Fixed: empty dialog text (key mismatch)

Surfacing dialog `text`/`answers` via the bridge exposed a real game bug: all dialog speech/answer strings
resolved empty. Root cause — a text-pack key mismatch between the baker and the runtime lookup. The
`DialogBaker` stores each dialog text under a 4-part key `FromParts("Dialogs", <dialogName>, <textKey>, ...)`
(it includes the dialog name), but `Dialogs.fos` looked it up with only the text key
(`TextPackKey(TextPackName::Dialogs, "" + textId)`), so the keys never matched and `Game.GetText` returned
empty for every dialog (a normal player saw the same).

Fix (in `Scripts/Dialogs.fos`): build the lookup with the dialog id as the first key part —
`TextPackKey(TextPackName::Dialogs, dialogId, textId)` in `ReceiveDialogContext` (screen text + answers) and
the answerless `Say`/`Info` path. Verified: `arroyo_laumer` now reads its real Russian quest dialog and the
agent navigates it answer-by-answer.

### Fixed: empty NPC floating text (numbered dialog strings)

The same class of bug hit the **numbered** dialog strings — the lines NPCs say on their head in combat/ambient
(`Messaging::Say`/`SayOnHead`/`Info`), keyed by `MsgStr::DialogTextId(dialogId, num)`. `DialogBaker` stores
these under `[Dialogs, <dialogName>, <100000000 + num>]` (the authored key base `100000000` is shared by every
dialog; the dialog name disambiguates), but the call sites looked them up as
`TextPackKey(TextPackName::Dialogs, "" + MsgStr::DialogTextId(dialogId, num))`, which is wrong **twice**: it
omits the dialog name, and `DialogTextId = dialogId.uhash + 12000 + num` no longer reproduces the baked key
(the 64-bit `uhash` overflows to a garbage number). So all of these floating lines were empty.

Fix: a single helper `MsgStr::DialogTextKey(dialogId, num)` →
`TextPackKey(TextPackName::Dialogs, dialogId, "" + (100000000 + num))`, and the **101** call sites across 26
files (`TextPackKey(TextPackName::Dialogs, "" + (MsgStr::DialogTextId(EXPR, N)))` → `DialogTextKey(EXPR, N)`)
were migrated to it. Verified through the `qa_get_text` debug command (resolves `MsgStr::DialogTextKey` for a
given dialog id + number): `klam_aldo` 1/2/3 ("Не могу к доске подобраться…", …), `all_poker` 0 ("Ваши карты:"),
`bh_phil` 200 — all now return their real text.

### Fixed: empty dialog text in `@text` format tags (poker / roulette / banker / NPC names)

The other consumer of the numbered dialog strings is the `@text Dialogs <id>@` **format tag** — built
server-side (poker card names, roulette, the replication-banker "spy" descriptors) and resolved client-side by
`Game.FormatTags` so each player sees their own language. The tag carried a single id
(`MsgStr::DialogTextId(...)`), so — like the `Say`/`Info` path — it omitted the dialog name and used the wrong
number; all of it rendered empty. NPC names via `@text Dialogs <MsgStr::NpcNameDlgTextId(dlg)>@` were broken
the same way (the name is stored under the string key `"Name"`).

Fix, in two parts:
- **Engine** (`SourceExt/ClientExtension.cpp::FormatTags`): the `@text` tag now also accepts a three-token form
  `@text <pack> <subkey> <key>@` → `FromPack(pack, subkey, key)` (a second key). The two-token form is
  unchanged, so every existing tag keeps its behaviour.
- **Script**: two helpers — `MsgStr::DialogTextTag(dialogId, num)` → `@text Dialogs <dialogId> <100000000+num>@`
  and `MsgStr::NpcNameTag(dialogId)` → `@text Dialogs <dialogId> Name@` — and **157** sites migrated to them
  (146 numbered-text across `Dialog.fos`/`Poker.fos`/`Roulette.fos`, 11 NPC-name across 8 files).

Verified end-to-end with the `qa_format_tags` debug command (runs a raw string through `Game.FormatTags`):
`@text Dialogs klam_aldo 100000001@` → "Не могу к доске подобраться…", `@text Dialogs all_raider Name@` →
"Рейдер", `@text Dialogs all_poker 100000000@` → "Ваши карты:", and the same tag embedded mid-sentence
resolves in place. (Requires a native `TLA_Client` rebuild for the `FormatTags` change.)

### Fixed: empty proto-name `@text` tags (critter / item / location names)

`@text Critters/Item/Locations <id>@` (NPC, item and location names in a handful of messages) were broken
differently. The engine `ProtoTextBaker` stores a proto's localized `$Text <lang>` name under
`[<pack>, <protoId>]` — i.e. the **proto id string itself is the key**, and the pack names are `Critters`,
`Items` (plural!) and `Locations`. The call sites instead passed a number (`pid.uhash` via
`NpcProtoNameTextId`/`ItemNameTextId`/`LocNameTextId`) and, for items, the wrong pack name `Item` (singular) —
so all of it missed and rendered empty.

Fix: helpers `MsgStr::NpcProtoNameTag(pid)` → `@text Critters <pid>@`, `MsgStr::ItemNameTag(item)` /
`ProtoItemNameTag(pid)` → `@text Items <pid>@`, `MsgStr::LocNameTag(pid)` → `@text Locations <pid>@`, with the
**15** sites (across `Behemoth`/`Caravan`/`FighterQuest`/`GameEventCaches`/`NcrPostman`/`Repairer`/`Resources`/
`Traveller`) migrated to them. These are plain two-token tags (no engine change needed beyond the three-token
support already added). Verified via `qa_format_tags`: `@text Critters Algernon@` → "Алжернон",
`@text Items _10mm_ap@` → "10 мм ББ", `@text Locations klamath@` → "Кламат", and embedded in a sentence.

## Roadmap (next)

- A content-driven quest runner on top of `qa_teleport_map` (accept → travel → turn in) covering more quests;
  the Cassidy letter cycle above is the reference flow.
- The proto-text long tail is **done** (full key scheme verified — name `[Pack, protoId]`, desc
  `[Pack, protoId, "Desc"]`, numbered `[Pack, protoId, "<rawN>"]`). Item names/descriptions in look/examine
  (`ItemNameKey`/`ItemInfoKey`, 9 sites in `ClientMain.fos`); all 16 worldmap/crafting GUI sites — location
  name/desc/map/entrance/picture + crafting item names (`LocNameKey`/`LocInfoKey`/`LocPicKey`/`LocLabelPicKey`/
  `LocMapNameKey`/`LocEntranceNameKey`/`LocEntrancePicx|yKey`/`ProtoItemNameKey`) edited in the `.fogui` source
  and regenerated into `GuiScreens.fos`. The old single-key resolvers (`GetItemText`/`GetLocationText`/
  `GetCritterText`/`HasLocationText`) are now unused and were removed. Also fixed the `AddDialogStr`/STR-const
  system: the replication-bank terminal + roulette messages were empty because `AddDialogStr(int msg)` did a
  single-key lookup of a `DialogTextId` number — the RemoteCall is now `AddDialogStr(hstring dialogId, int
  strNum, …)` → `DialogTextKey`, the STR constants became plain string numbers, and `DialogBarman.fos`'s
  malformed `text Dialogs/Locations` tags (missing the leading `@`) were corrected. Verified
  (`@text Dialogs repl_terminal 100000000@` → "Ошибка. Пожалуйста обратитесь…"). The only `DialogTextId`
  remnants left are vestigial (commented-out poker `// Todo: SayMsg` consts + one Caravan debug log).
- Global-map observation + travel/enter — for canonical world state and travel-only mechanics (random
  encounters, party travel). Quest accept/turn-in itself already works via `qa_teleport_map` (the sandbox
  instance spawns the map-placed quest NPCs).
- Resolved quest titles/objective text in `quests` (and faction, skills/abilities observation).
- Richer screen/affordance surfaces (barter, container/loot grids, registration customization).
- Content-driven playtest runners per quest/mechanic on top of `qa_teleport_map`; optionally adapt more of the
  ported advisory/agent-runtime adapter layer.
