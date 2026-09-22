# Game Systems

The map of TLA's own gameplay code — what the systems are, where they live, what they talk to, and what
covers them. The engine's equivalent is `Engine/Docs/Architecture.md`; this file is the layer above it.

Read this before opening a `.fos`. Every module also carries a Russian header block describing itself, so
this map deliberately does not repeat those: it gives the shape, and the headers give the detail.

## How the code is wired

- **No includes.** Baking sees every `.fos`; cross-module calls are `Namespace::Function()`. A file's
  namespace always equals its filename. Hand-written gameplay code is at the top of `Scripts/`;
  `Generated/`, `Tests/` and `Json/` are separate, and every directory is listed in `TLA.fomain`.
- **Three dispatchers, many subsystems.** `Main` (server), `ClientMain` (client) and `MapperMain` (mapper)
  subscribe to engine events in `ModuleInit` and delegate. Almost nothing else subscribes to world events
  directly; a subsystem exposes functions and its own narrow events instead.
- **The server is authoritative.** The client queues intent and renders; every state change that matters is
  a `[[ServerRemoteCall]]` landing in a server module.
- **One thread.** Since `Server.SingleThreadedLogic` was turned on, game logic runs on a single worker and
  scripts take no entity cover. See the constraint note in [../AGENTS.md](../AGENTS.md).

## The path of one player action

The most useful thing to trace first, because six systems appear in it in order:

1. **Input.** `ClientMain` turns a click into an intent and hands it to `ChosenActions`.
2. **Queue.** `ChosenActions` (client side) holds the action queue, regenerates action points, and sends
   the intent on as a remote call.
3. **Arrival.** `ChosenActions` (server side) receives it and validates the preconditions.
4. **Execution.** `CritterActions` spends AP and performs the real-time act — pick up, move item, use skill,
   reload, attack.
5. **Rules.** `Combat` resolves an attack: hit chance, damage, criticals; `Parameters` supplies every
   derived stat it reads.
6. **Reply.** The result travels back as a broadcast and `ClientMain` animates it via `Animation`.

## Systems

`S` = server, `C` = client, `M` = mapper. "Covered" names the harness suite, when one exists.

### World, travel and locations

| Module | Side | Lines | Entry point | Covered |
| ------ | ---- | ----: | ----------- | ------- |
| `Worldmap` | S | 11 587 | `WorldmapInit` builds the encounter tables | `Test_Worldmap` |
| `GlobalmapGroup` | S/C | 1 745 | `ModuleInit`; `GlobalProcess`, `GroupMove` | — |
| `GlobalMapLocations` | S/C | 220 | `ModuleInit`; known-location list per critter | — |
| `Location` | S | 338 | `ModuleInit`; creation, garbage collection | — |
| `Entrance` | S | 353 | `CritterTransferToMapEntry` | — |

Random encounters are the heaviest system in the project and are almost entirely table data; see item 1 in
[AuditPlan.md](AuditPlan.md).

### Combat and critter rules

| Module | Side | Lines | Entry point | Covered |
| ------ | ---- | ----: | ----------- | ------- |
| `Combat` | S | 3 217 | `CombatAttack`, `ApplyDamage` | — |
| `Parameters` | S/C | 1 626 | `ModuleInit` registers property getters/setters | `Test_Parameters` |
| `CritterActions` | S | 1 054 | called by `ChosenActions`; `ProcessAp` | `Test_CritterActions` |
| `CritterState` | S | 260 | `ModuleInit`; alive/knockout/dead transitions | — |
| `NpcPlanes` | S | 1 461 | `ModuleInit`; `ProcessAi` on critter idle | `Test_NpcPlanes` |
| `Animation` | C | 1 248 | `ModuleInit`; `ProcessTactics` | — |

`Combat` is the largest uncovered system and holds two of the project's longest functions — items 2 and 7
in the plan point at the same module from different sides.

### Player intent and lifecycle

| Module | Side | Lines | Entry point | Covered |
| ------ | ---- | ----: | ----------- | ------- |
| `ChosenActions` | S/C | 1 343 | `ModuleInit`; `ChosenProcess` | — |
| `Main` | S | 1 584 | `ModuleInit` — the server event dispatcher | — |
| `ClientMain` | C | 1 734 | `ModuleInit` — the client event dispatcher | — |
| `PlayerRegistration` | S/C | 560 | `ModuleInit`; login and registration | `Test_PlayerRegistration` |
| `Replication` | S | 519 | death, respawn, permanent death | — |

### Interaction

| Module | Side | Lines | Entry point | Covered |
| ------ | ---- | ----: | ----------- | ------- |
| `Dialogs` | S/C | 951 | `RunDialog`, `SpeechAnswer`, `CloseDialog` | — |
| `Dialog` | S | 1 293 | `DialogDemand` / `DialogResult` handlers | — |
| `NpcDialog` | S | 376 | per-NPC dialog helpers | — |
| `Barter` | S | 404 | `ProcessBarterNpcOffer` | `Test_Barter` |
| `FixBoy` | S/C | 1 548 | `InitFixBoy` builds the recipes; `Rpc_CraftItem` | — |
| `ClientItems` | S/C | 649 | `ModuleInit`; inventory and container UI | `Test_ClientItems` |
| `Item` / `ItemMovement` | S | 244 / 312 | doors, holodisks, deferred destroy, moves | — |

`Dialogs` is the engine-facing core (contexts, demands, results); `Dialog` is the library of authored
demand/result handlers that content calls by name. Content lives in `Dialogs/*.fodlg`.

### Infrastructure

| Module | Side | Lines | Entry point | Covered |
| ------ | ---- | ----: | ----------- | ------- |
| `Tla` | S/C | 670 | shared enums, action codes, small helpers | — |
| `Stdlib` | S | 404 | string and array helpers | `Test_Stdlib` |
| `Messaging` / `MsgStr` | S/C | 450 / 1 176 | player-facing text and text-pack keys | — |
| `Testing` | S | 298 | the script harness; `Testing.Enabled` turns it on | — |
| `AiControl` | S/C | 2 307 | the automation bridge; see [AiControl.md](AiControl.md) | — |
| `MapperMain` | M | 1 824 | `ModuleInit`; editor tabs and tools | — |

## Where the content lives

| Kind | Path | Count | Convention |
| ---- | ---- | ----: | ---------- |
| Dialogs | `Dialogs/*.fodlg` | 859 | location prefix — `arroyo_`, `den_`, `ncr_`, `vc_`, `nr_`, `sf_`, `redd_`, `klam_`, `bh_` |
| Items | `Items/*.foitem` | 813 | plus `Items/Static/` (3 848 scenery), `Custom/`, `Explode/`, `Flying/` |
| Critters | `Critters/*.focr` | 531 | |
| Maps | `Maps/*.fomap` | 275 | |
| Texts | `Texts/*.{russ,engl}.fotxt` | 6 packs | parity guarded by `Tools/ContentQuality` |
| GUI | `Gui/*.fogui` | 32 screens | generates `Scripts/GuiScreens.fos` |

Location and quest scripts follow the same prefixes as the dialogs — `MapModoc.fos`, `NcrPoliceman.fos`,
`KlamCowboy.fos` — 91 modules in all. They are content, not systems: each one drives one place.

## Where to start reading

- Changing a rule (damage, skills, AP): `Parameters` first, then `Combat` or `CritterActions`.
- Changing what a player can do: `ChosenActions` on both sides, then `CritterActions`.
- Adding to a place: find the location module by prefix, and its dialogs by the same prefix.
- Adding an NPC behaviour: `NpcPlanes`, then the pattern modules (`Pattern*`).
- Adding a check or effect callable from a dialog: `Dialog`, which is the authored handler library.
- Verifying anything: the `Verify :: All` task; see the table in [../AGENTS.md](../AGENTS.md).
