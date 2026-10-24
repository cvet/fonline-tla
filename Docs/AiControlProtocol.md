# AI control protocol and commands

Detailed TLA bridge reference. Start at [AiControl](AiControl.md) for configuration,
launch, MCP tools, screenshots and acceptance. The implementation owners are
`SourceExt/ClientAiBridge.cpp` and `Scripts/AiControl.fos`; check current dispatch
and observation code before extending this table. Privileged QA commands require
`AiControl.AllowQaCommands=True` on the relevant sides and are test setup, not
ordinary player acceptance.

Routes: [wire protocol](#native-bridge-protocol), [observation](#observation-schemaversion-1),
[events](#events), [commands](#commands), [QA setup](#qa-setup-commands-test-only),
[environment queries](#environment-queries).

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

The bridge serves one connection at a time; the next adapter is accepted once the current one
closes. A connection that fails (a read or write error, typically a client that went away before its
response was written) is closed and reported as `lastError` in `status`, and the bridge keeps
listening. A request whose handling throws is answered with error `-32603` instead. Only a failure
to open the listener stops the bridge.

If `AiControl.Token` is non-empty, call `auth` first on every connection. The MCP adapter does this
automatically when `TLA_AI_TOKEN` / `--token` is supplied.

## Observation (schemaVersion 1)

Top-level keys: `schemaVersion`, `seq`, `clientIndex`, `connected`, `hasMap`, `hasChosen`, `account`,
`screen`, `mouse`, `chosen`, `map`, `critters`, `mapItems`, `inventory`, `quests`, `dialog`,
`availableActions`.

Consumers must branch on `connected`, `hasMap`, `hasChosen` instead of assuming a current player/map/chosen.

QA map teleport makes the selected location persistent, including its maps and contents, so a private
database restart can restore the controlled character's complete entity graph.

- `chosen`: id, name, hexX/Y, level, currentHp, maxHp, experience, currentAp, actionPoints, isAlive,
  inCombat (`TimeoutBattle` active), inSneakMode, isMoving, walkSpeed, movingSpeed, movingEndX/Y.
  Movement speed and endpoint come from the active engine movement context; without a context they
  are `0` and `-1/-1`. These fields let GUI tests confirm a stopped character, a newly issued route
  and the actual walk/run speed.
- `mouse`: x, y and `cursor` — the current `CursorType` (`Default` 0 = action, `Move` 1, `UseItem` 2, `UseWeapon` 3,
  `UseSkill` 4, `Hand` 5); the right button cycles it in game.
- `map`: id, protoId, width, height.
- `critters`: visible critters from `CurMap.GetCritters(CritterFindType::Any)` (chosen excluded): id,
  protoId, name, hexX/Y, isAlive, inCombat, isNoTalk, effective talkDistance, dialogId. The
  `protoId` + `dialogId` pair lets quest tools distinguish authored NPC roles that happen to share a dialog;
  `isNoTalk` and `talkDistance` explain silent client/server talk precondition failures.
- In QA-enabled runs, an ordinary `talk_to` attempt also emits `talk_diagnostic`: the server reports
  life/control/no-talk/map/distance/mutual-visibility checks and whether the normal dialog context actually
  started. This is observational only; it calls the same `StartDialog`/`Dialogs::RunDialog` path and does not
  bypass distance, visibility, demands, or synchronization.
- `mapItems`: visible map items tracked from `OnItemMapIn` / `OnItemMapOut`: id, protoId, hexX/Y, count,
  stackability, ownership, cost/weight, use/pick-up capabilities, and `visualFeedback.timerCapable`.
- `inventory`: `Chosen.GetItems()`: the same real item metadata plus slot. Both item arrays also expose the
  TLA door/container contract (`hasDoor`, `hasContainer`, `hasLocker`, `canOpen`, `opened`, lock/jam/broken/
  no-open state, and `isGag`). Runners must select candidates from these fields instead of guessing safety
  from a proto name or accepting an unchecked explicit id.
- `barter`: active barter snapshot with `traderId`, transfer `session`, server-synchronized pricing metadata
  (`coefficient`, `masterTrader`, `playerOfferTotal`, `traderOfferTotal`), plus `playerInventory`,
  `playerOffer`, `traderInventory`, and `traderOffer` item arrays (`id`, `protoId`, `count`);
  `active=false` outside Barter.
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
| `use_item` | `itemId`, optional exactly one `targetId`/`auxId`, optional `stringArg` (`timer:<seconds>`) | `Tla::ChosenUseItem` on self, one critter, or one item. Timer mode is self-only and accepts only the canonical range `timer:1` through `timer:599` (no sign, whitespace, leading zeroes, target, or trailing text). |
| `use_skill` | `stringArg` (skill `CritterProperty` name, e.g. `SkillFirstAid`/`SkillLockpick`/`SkillRepair`), optional `targetId`/`itemId`/`x`/`y`; static scenery also requires `sceneryProtoId` | `CurPlayer.ServerCall.UseSkill`. With no target it applies to the chosen (self-heal etc.); scenery proto and hex are transported separately. |
| `reload` | `itemId`, `auxId` (ammo) | `CurPlayer.ServerCall.ReloadWeapon` |
| `unload` | `itemId` | `Tla::ChosenUnloadWeapon` |
| `move_item` | `itemId`, `intArg` (slot) | `CurPlayer.ServerCall.MoveInvItem` |
| `drop_item` | `itemId`, `intArg` (count) | `CurPlayer.ServerCall.DropInvItem` |
| `operate_container` | `itemId`, `intArg` (bit0 take, bit1 all, `>>2` count) | `CurPlayer.ServerCall.OperateContainer` (loot/container grid: take items) |
| `craft` | `intArg` (craft id) | `CurPlayer.ServerCall.Rpc_CraftItem(FixboyButton, id, 0)` — runs a FixBoy recipe (server checks skill/materials/tools, consumes resources, grants the item) |
| `toggle_sneak` | `append` | `Tla::ChosenSneak` — **sneak is stubbed in TLA**, returns `sneak_not_implemented_in_game` |
| `dialog_answer` | `intArg` (answer index; special links: `0xF1`=close, `0xF2`=barter) | `CurPlayer.ServerCall.SpeechAnswer` |
| `close_dialog` | none | Semantically close the active dialog with `SpeechAnswer(0xF1)` |
| `say` | `stringArg`, `intArg` (`SayType`) | `CurPlayer.ServerCall.ReceiveChosenSay` |
| `barter_transfer` | `itemId`, `stringArg` source, positive `intArg` count | Move a stack between `player_inventory`/`player_offer` or `trader_inventory`/`trader_offer` in the active Barter UI |
| `barter_offer` | none | Submit the assembled active barter offer through the normal client/server path |
| `barter_return_dialog` | none | Return from active NPC barter to its dialog through the current validated transfer session |
| `clear_actions` | none | Clear queued client actions |
| `close_screen` / `show_screen` / `hide_screen` | `stringArg` (`GuiScreen` name) | GUI screen control |
| `show_context_screen` | `stringArg` (`Aim`, `Use`, `Timer`, `Split`, or `SkillBox`), real item/target ids as required | Open a contextual screen with its normal `OnShow` parameter contract after validating the observed target, item ownership, stack, and timer/use capabilities. |
| `ui_answer` | `intArg` (index) or `stringArg` (`answer_N`/`level_N`); `auxId` is the expected DialogBox session | Answer a semantic DialogBox/elevator prompt. DialogBox requires the session from the same observation and rejects a missing/stale session; elevator answers reject a DialogBox session. |
| `save_screenshot` | `stringArg` (path) | `Game.SaveScreenshot` (framebuffer readback) |
| `set_resolution` | `x`, `y` | `Game.SetResolution` |
| `toggle_fullscreen` | none | `Game.ToggleFullscreen` |
| `set_mouse_pos` | `screenX`, `screenY` | `Game.SetForcedMousePos` |
| `mouse_click` | `screenX`, `screenY`, `intArg` (`MouseButton`) | `Game.SimulateMouseClick` |
| `key_press` | `intArg` (`KeyCode`), `stringArg` | `Game.SimulateKeyboardPress` |
| `mouse_down` / `mouse_up` | `screenX`, `screenY`, `intArg` (`MouseButton`) | `Game.SimulateMouseDown` / `Game.SimulateMouseUp`: hold a button across frames (the action-cursor menu opens on a held left button) |
| `mouse_move` | `screenX`, `screenY` | `Game.SimulateMouseMove`: a relative move, as a drag while a button is held; a pinned `set_mouse_pos` stays pinned |
| `key_down` / `key_up` | `intArg` (`KeyCode`), `stringArg` | `Input::KeyDown` / `Input::KeyUp`: hold a key (Shift shows the step count on the move cursor); the engine simulates key presses only as press-and-release |
| `environment_query` | `intArg` (queryId), `screenX`/`screenY` (from-hex, `-1` = chosen), `x`/`y` (to-hex), `stringArg` (options) | Client geometry/path query; publishes an `environment_query_result` event by `queryId`. |

Commands not yet supported in TLA return `unsupported:<type>` and `success=false`.

### QA setup commands (test-only)

Gated by `AiControl.AllowQaCommands = True` (off by default, checked on both client and server). They route
through server RemoteCalls that move the player's controlled critter; they are a test-harness setup surface,
not normal player abilities. Use them to reach content for mechanics/quest runs.

| Type | Main params | Behavior |
|------|-------------|----------|
| `qa_teleport_hex` | `x`, `y` | Same-map reposition (`Critter.TransferToHex`); the engine snaps to the nearest movable hex. Useful to reach otherwise-blocked spots. |
| `qa_teleport_map` | `stringArg` (`locationPid` or `locationPid/mapProto`), optional `x`/`y` | Teleport to a content map. The client validates both proto ids and sends them as separate known `hstring` values; the server resolves the requested map inside that location, creates a valid unloaded location when needed, and uses entry `"0"` when no hex is given. Unknown targets fail as `unknown_map_target` without a server exception. |
| `qa_teleport_global` | none | `Critter.TransferToGlobal`. Note: a no-op from the `repl1` replication/limbo start map (it has no global coordinates); use `qa_teleport_map` to reach content. |
| `qa_set_prop` | `stringArg` (CritterProperty name), `intArg` (value), optional `x` request id | Set an int CRITTER property (`cr.SetAsInt`) — reputation/loyalty values, a prior quest stage, `CurrentHp`, limb-damage flags, etc. A successful script-side write publishes `qa_prop_set` (`{prop, value, requestId}`); a missing/delayed matching event is retried by the caller. |
| `qa_set_game_prop` | `stringArg` (GameProperty name), `intArg` (value) | Set an int GAME property (`Game.SetAsInt`) — world/quest flags that live on the game singleton, not the critter (e.g. `DenVirginIsAway`). Many dialog demands gate on these, so `qa_set_prop` alone can't satisfy them. |
| `qa_give_item` | `stringArg` (item proto), `intArg` (count) | Give an item (`cr.AddItem`) — for quest items the giver doesn't hand out, or starting gear. |
| `qa_get_prop` | `stringArg` (CritterProperty name), optional `intArg` request id | Authoritative SERVER-side read of an int critter property. The server reads `cr.GetAsInt` and calls the client back (`AiControlReceiveQaProp`), which publishes a `qa_prop_value` event (`{prop, value, requestId}`). Needed because ~1/3 of quest flags are `Server`-scope (not `OwnerSync`) and therefore never appear in the client observation's `quests` — the only way to verify them is this round-trip. |
| `qa_get_text` | `stringArg` (dialog id), `intArg` (string number) | Resolve a numbered NPC floating-text via `MsgStr::DialogTextKey` and return it in the command message (`text=<…>`). Debug tool for the numbered-text fix below; empty means the string isn't authored for that dialog. |
| `qa_get_text_pack` | `intArg` (numeric id) | Resolve a row from the baked general `Text` pack for the client's active language via `TextPackKey(TextPackName::Text, …)` and return it as `text=<…>`. This verifies the runtime localization surface rather than only the authored `.fotxt` file. |
| `qa_format_tags` | `stringArg` (text with tags) | Run a raw string through `Game.FormatTags` (resolves `@text`/`@arg`/`@sex`/… client-side) and return the result (`result=<…>`). Used to verify the three-token `@text Dialogs <dialogName> <key>@` path end-to-end. |
| `qa_show_dialog_box` | none | Request a real server-backed `AskFollowGlobalGroupRuler` DialogBox with two answers for semantic/session and screenshot tests. The typed MCP wrapper is `tla_qa_show_dialog_box`; `answer_1` is the safe no-op choice. |

`qa_get_prop` is asynchronous: the value arrives as a `qa_prop_value` event, not in the command's own
completion message. Snapshot the event cursor (max `seq`), send `qa_get_prop` with a non-zero request id, then
poll `events` for the `qa_prop_value` whose `prop` and `requestId` both match. The correlation is required under
load because a delayed response to an earlier read may arrive after the new cursor. `tla_quest_runner.py`'s
`read_quest` does exactly this — it reads the client observation first (fast, for `OwnerSync` quests) and falls
back to a correlated `qa_get_prop` when the property is absent client-side (`Server`-scope quests such as
`KlamVaccination`).

`qa_set_prop` has the same correlation requirement, with the request id transported in `x` because `intArg`
already carries the property value. `tla_quest_runner.py` waits for a matching `qa_prop_set` event and resends
the command when no matching acknowledgement arrives. The acknowledgement is sent only after `SetAsInt`.
Entity locking remains an explicit `Game.Sync` cover in the `[[Async]]` script callback; no called engine
function performs implicit synchronization.

`qa_teleport_map` accepts `locationPid/mapProto` (e.g. `vault_city/vcity_courtyard`) to land on a specific
sub-map of a multi-map location. The split is intentional: a synthetic combined `hstring` is not part of baked
metadata and would be rejected by engine inbound validation. `qa_set_prop` / `qa_give_item` are the
prerequisite-setup surface for quests gated by
reputation, faction loyalty, prior quest state, or required items — set those up, then run the quest's normal
dialog flow.

`qa_teleport_map` is the practical way to put a test character on a real content map (e.g.
`qa_teleport_map arroyo` lands on the `arroyo` village map with its real NPCs). A freshly created location instance is
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
