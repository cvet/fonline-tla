# World and travel

Locations, map entrances and transfers, global-map groups, the worldmap
encounter engine, and vehicles. Map/city preview screens are covered by
[Systems](Systems.md); location protos and map files as content are
[ContentWorkflow](ContentWorkflow.md). Verified against revision `e2b5b90b0`
(static analysis).

## Locations — [Scripts/Location.fos](../Scripts/Location.fos)

Locations are created from `.foloc` protos (`Location::CreateLocation(protoId,
wpos, critters?, props?)` builds `MapProtos` from the proto and optionally
marks the location known to the given critters). Every location runs a
1-second **garbage collector** time event: `AutoGarbage` locations whose
every map passes `CheckMapForGarbage` are destroyed. Players, NPCs marked
`IsGeck`, NPC GECK-item carriers and NPCs satisfying
`!IsNoHome && HomeMapId != map.Id` prevent collection. An NPC at its home
map does not by itself prevent collection. The check for a GECK *item on the map*
is a commented-out breadcrumb pending `Item::IsGeck` work. Personal
(quest/event) locations set `AutoGarbage/Hidden` explicitly. The player's
known-location list (`KnownLocations` → `KnownLocProtoId` on change) is what
the global-map UI offers; [Scripts/GlobalMapLocations.fos](../Scripts/GlobalMapLocations.fos)
syncs it to the client on every change and on global-map entry.

## Entrances and transfers — [Scripts/Entrance.fos](../Scripts/Entrance.fos)

Map "entries" are `Entrance` grid static items whose `Grid_ToMapEntry` names
an entry (numeric strings are the convention: `"0"` arrival, `"242"` the
replication entry, city exits, event entries `"33".."36"`). API:
`ParseEntries`, `GetEntry(map, name, skip)`, `GetEntryFreeHex` (entry hex,
then neighbors honoring hex parity, otherwise false),
`MapGetAllEntries`, and `CritterTransferToMapEntry` (random entry of that
name → `cr.TransferToMap`). Whole-*group* transfers go through
`GlobalmapGroup::GroupToLoc/GroupToMap`. Leaving to the global map is
`cr.TransferToGlobal()` (exit grids, scripts, the NoPvp escape RPC).

## Global-map groups — [Scripts/GlobalmapGroup.fos](../Scripts/GlobalmapGroup.fos)

- A group is keyed by `GlobalMapTripId` in the script pool
  `AllGlobalGroups`; members join/leave via engine events
  `OnGlobalMapCritterIn/Out` with snapshot-checked mutation. When the leader
  leaves, **leadership passes to the highest-Charisma member**; the last
  member out destroys the group. Movement checks stop oversized groups when
  their size exceeds `leader.Charisma + leader.PerkMagneticPersonality`.
  `GlobalMap.GlobalMapGroupMaxCount` is declared/configured as 6, but no
  consumer of that setting was found in the traced sources.
- Movement: each member has an idle event; only the leader calls `GroupMove`.
  Script `ProcessGroup` calls `GlobalProcess(processType, …)` unless the
  critter's `OnGlobalMapProcess` event overrides the step:
  per move step: `speedPix = speed · GlobalMapMoveTime/1000`, straight-line
  integration toward the target, zone-based encounter checks (below), and
  parking checks (`CheckForLocationWithoutParking`). Group members render on
  the client global map (`GlobalMap.ShowGroups`).
- Entering a location: `GroupToLoc(rule, locId, entrance)` checks knowledge,
  radius, capacity and entrance events, resolves the selected pair in
  `loc.MapEntrances`, then calls `GroupToMap`. Pedestrians use that entry;
  cars use the dedicated car/car-critter entries. Encounter invitations are
  a separate flow. Rule changes and follow/invite commands flow
  through `ProcessGlobalMapCommandImpl` (client RPC → leader authority).
- The world is 28×30 zones of 50 world units (`GlobalMap.*` settings; the
  same constants are mirrored in `Worldmap::ZONE_COUNT_*`).

## Encounter engine — [Scripts/Worldmap.fos](../Scripts/Worldmap.fos)

The largest content system (~11.5k lines, almost entirely data). Structure:

- `CZone` per ground/water cell: difficulty, terrain, per-daypart encounter
  chance (morning/afternoon/night), and a `CEncounterTable` reference.
- `CEncounterTable`: candidate **location protos** (the encounter map pool)
  plus `CEncounter` entries — each with a `Chance`, a text `StrNum`
  (GlobalMap text pack: "You ran into …"), optional `IsSpecial`,
  group selections with ratio ranges (`AddGroup(group, ratioMin, ratioMax)`),
  inter-group `Actions` (`Fighting` — spawned sides start hostile to each
  other), and `CCheck` conditions (skills/properties/time).
- `CEncounterGroup`: a spawn formation — `TeamNum`, `Position` (formation
  index), `Spacing`, `Distance`, and objects (critter pids, items, attached
  init scripts — this is where `AiPattern::*Init` behavior patterns attach).
- `WorldmapInit` (server start) builds all tables/zones via `SetZone`/
  `AddEncounter` — the bulk of the file. Special one-shot encounters are
  gated by per-critter `SpecialEncounter*` counters (declared as quest-like
  `Max = 1..3` properties, `Worldmap.fos:17-43`).
- **Flow**: `GlobalProcess` periodically calls `Worldmap::FindEncounter`,
  which rolls the zone's daypart chance and picks a passing encounter.
  `CreateFoundedEncounter` records an ungenerated descriptor
  (`IsGenerated=false`, `LocationId=ZERO_IDENT`); it does not reserve a map.
  `InviteToEncounter(group, car, descriptor, combatMode, …)` creates the
  location/formations lazily through `GenerateEncounter` and returns the
  map/entry. Outdoorsman and movement type (including water/flying) affect
  whether the invitation asks for a choice or forces entry. Car-owner
  replication reuses the same entry (`Replication.fos:256`), as do caravans
  and slaver hunts. `Worldmap::TestEncounter` is a QA hook to force an
  encounter by its StrNum.

## Vehicles — [Scripts/Car.fos](../Scripts/Car.fos)

Cars are `ItemType::Car` items: energy cells work for either engine, while
the listed alcoholic fuels additionally require `CarIsBioEngine` (octane
acts as fuel density); lock/key checks
(`CarIsNoLockpick`), skill inspection/repair (repair skill reduces
`Deterioration` measured against `Car_MaxDeterioration`), and taking the car
to the global map (`cr.TransferToGlobal()` moves the car with the group;
`Car_MovementType` selects movement speed/relief). Car ownership interacts
with death/replication (see [PlayerLifecycle](PlayerLifecycle.md)) — the
replicator handles cars before choosing the player/NPC respawn branch,
attempting to transfer the dead car owner into an empty encounter or destroying
the cars on failure. `GetCarCost` currently uses a placeholder world-count of 10
(migration TODO).

## Caravans: disabled

[Scripts/Caravan.fos](../Scripts/Caravan.fos) is a complete escort-caravan
system (scheduled routes between towns with leader NPCs, hired guards,
worldmap travel with encounters, cab loot, guard quest success/failure
accounting; route constants `CARAVAN_*` at the top). **Its initialization is
commented out** in `Main.fos` with a route-setup null-reference warning.
Ordinary startup therefore does not start the scheduled caravan system.
Its dialogs/properties and individually callable handlers still exist;
their presence does not prove that escorts run or that every handler is
unreachable. Reactivation requires a separate gameplay task.

## Verification

Static source trace at the revision above; `Scripts/Tests/Test_Worldmap.fos`
is the regression owner for the encounter data plumbing. Travel changes
need a real global-map round trip (solo + group + car) and an encounter
accept/decline in a client; zone/table edits are pure data — re-run the
suite and one forced encounter (`TestEncounter` under the QA hook rules in
[AiControl](AiControl.md)) before shipping.
