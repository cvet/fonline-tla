# Items and inventory

Item prototypes, the stacking adapter, equipment slots, containers, item
movement, and deterioration/repair. Combat consumption of these contracts is
[Combat](Combat.md); the workflow rules for authored inputs are
[ContentWorkflow](ContentWorkflow.md). Verified against revision `e2b5b90b0`
(static analysis).

## The stacking adapter — [Scripts/ItemStacks.fos](../Scripts/ItemStacks.fos)

The engine treats every item as a single instance; **all** count semantics
are project-owned in `ItemStacks` (`Count` is a `PublicSync Persistent`
property; new items default to 1 in `OnItemInit`, which runs at
`EventPriority::Highest` so later init handlers always see ≥ 1 unit).

| Rule | Detail |
| --- | --- |
| On a critter | Stackable units of one proto merge into one stack — the first item of that proto in any slot (`FindStack(Critter, pid)` at `ItemStacks.fos:35`). Non-stackable items stay separate. |
| In a container | Stackable units merge per *stack section* (`FindStack(Item, pid, stackId)` at `:42`); an empty section matches any. `Tla::RootContainerStack()` (`any()`) is the root section used by containers. |
| On a map hex | Stacks never merge: a stackable proto becomes exactly one instance carrying the full count; non-stackable become up to `Critter.MaxAddUnstackableItems` (10) instances (`AddItem(Map, ...)` at `:144`). |

API (server): `AddItem` (critter/container/hex targets, optional initial
property dict), `CountItem`, `DestroyItem` (whole/partial by count/by pid),
`MoveItem` (critter/container-section/hex targets; stackable moves merge into
an existing stack or move a `SplitItem` piece), `SplitItem` (stackable only,
`0 < count < Count`, returns a detached copy), `Merge` (target gains count,
source destroyed if emptied). Return values differ by overload: critter adds
return the last created instance, hex adds the first — both are placement
facts, not identity guarantees. The client has its own `CountItem` duplicate
and a local-only `CloneItem` for offer previews (`Scripts/ItemStacks.fos:307-329`).

Bypassing the adapter with `Critter.AddItem`/`Map.AddItem`/count-taking
destroys is a contract violation — see
[Scripts](Scripts.md#project-adapters-that-must-not-be-bypassed). Regression
owner: `Scripts/Tests/Test_ItemStacks.fos`.

## Equipment slots

`CritterItemSlot` is engine `Inventory = 0`, `Main = 1`, `Outside = 255`,
extended by `Scripts/GameEnums.fos:420-421` with `Secondary = 2`,
`Armor = 3`. [TLA.fomain](../TLA.fomain) `Critter.CritterSlot*` vectors index
by slot value: all four slots enabled; `SendData = True False True True`
(the **Main hand item is not synced as data** — clients see it through
actions/hand protos); `MultiItem = True False False False` (only Inventory
holds several items).

`CritterItem::GetActive(cr, slot)` (`Scripts/CritterItem.fos:9-26`) never
returns null for combat-relevant slots: an empty Armor slot yields the
`default_armor` proto, empty weapon slots the `default_weapon` proto
(`Items/Custom/`, marked "used in engine"). This is why combat code can call
`WeaponHelpers` on an unarmed critter.

Slot-move rules (`ItemMovement::OnCritterCheckMoveItem`,
`Scripts/ItemMovement.fos:41-88`): dropping is always allowed; **Main** weapon
must match the critter model's `Weapon_StateAnim` capability; **Armor** only
accepts `ItemType::Armor` from Inventory and never when `IsNoArmor`; custom
slots above Armor only accept an item already in that slot. Equipping armor
recomputes the critter model (`Armor_CrTypeMale/Female` + `aa.frm`, with the
long-haired male jumpsuit special case) and sets `CurrentArmorPerk`
(`ItemMovement.fos:94-143`). Ground pickup fills a weapon only when
`Weapon_MaxAmmoCount > 0 && AmmoCount == 0`; a configured `AmmoPid`
is retained, with `Weapon_DefaultAmmoPid` used only when the pid is empty.
The free swap is Main↔Secondary
(`CritterActions::MoveInvItem` costs 0 AP, everything else
`Movement.RtApCostMoveItemInventory`).

## Containers and transfers

Container capacity is `Container_Volume` in the same abstract units as item
`Volume`; `CritterActions::CanPutItemsInContainer` (`Scripts/CritterActions.fos:439`)
sums existing root-section stacks plus the moving batch in saturation-safe
int64 math. Cycles are prevented (`WouldCreateContainerCycle`, depth 256).
The unified server operation is `CritterActions::OperateContainer`
(`Scripts/CritterActions.fos:494`), driven by the critter's active
`TransferType`/`TransferContainerId`/`TransferSession`; it re-validates
container existence, openness (`Container_Changeble`/`Opened`), distance
(including multihex), visibility (`IsNoLoot`/`IsNoSteal` filtering), weight
limits (`Parameters::CritterGetItemsWeightLimited` vs `CarryWeight`, int64
saturating), cycles, volume, and only then spends AP and moves through
`ItemMovement`. Stale client ids/counts return a fresh authoritative snapshot
instead of an exception. NPC barter is deliberately **not** a transfer type —
it must go through `Barter::ProcessBarterNpcOffer` (see [Economy](Economy.md)).

Doors and lockable containers live in [Scripts/Lockers.fos](../Scripts/Lockers.fos):
`LockerId`/`LockerComplexity` (keys are `ItemType::Key` items with matching
`LockerId`, or the bio "keys" `CritterFingersDoorId`/`EyesDoorId`, or
`KnownLockerId` on the critter), `Opened` toggling passability flags
(`SwitchLocker`), lockpicking roll
`Clamp(SkillLockpick + toolBonus − LockerComplexity, 0, 95)` vs
`Random(1,100)` — `lockpicks` +25 / `exp_lockpick_set` +50, each consumed at
1/31 per use; success opens and grants 50 XP; `TimeoutSkLockpick` (2 real
minutes) paces attempts. `ShowContainer` opens the transfer UI for players —
for NPC looters it simply moves everything out.

## Deterioration and repair

Module: [Scripts/Repair.fos](../Scripts/Repair.fos).

Internal wear `Deterioration` is in hundredths of a percent
(`Tla::MaxDeterioration = 10000` = 100%); `Tla::MaxBrokens = 10`. Wear
sources: weapon use `(+MaxSkillValue − skill)/3` per attack, armor
`((100−DR)·rounds + dmg)/3` per hit taken, pre-worn NPC/trader gear
(`EncounterNpc`, `Trader`, `PatternCommon`, …). `DeteriorateItem` clamps at
100% → `IsBroken`, severity roll by `BrokenCount`; after `MaxBrokens` breaks
(or a high roll) the item becomes `BrokenNotresc` (unrepairable).

Repair skill (`Main::CritterUseSkill` → `Repair::TryRepairItem`, target must
be own inventory item, `Deteriorable`): tool bonus `multi_tool` +25 /
`super_tool_kit` +50 (1/31 consume chance); broken-item repair penalty by
severity (−25/−75/−100) and `− BrokenCount·50/MaxBrokens`, clamp 6..95;
success zeroes wear, clears broken state, +40 XP; failure increments
`BrokenCount`. Servicing an unbroken item: `BrokenService` −25 and the same
count penalty; success sets `BrokenService` and reduces wear by
`repair·MaxDeterioration/100` (an `oil_can` in hand resets to 0, consumed),
+20 XP; **failure damages the item by 20%** wear. Cost tiers
(`SetItemCost`): 100% wear → `Cost/3`, >75% → `2·Cost/3`. Both paths end
with the skill timeout (`GameTime::RepairTimeout`) and a cost refresh.

## Item scripts and spawning

- Dynamic items get behavior by `SetupScript(...)` init functions:
  doors (`Item.fos`: auto-close from `Val3` seconds, dialog doors running
  `Dialogs::RunDialog`), holodisks (copy `Val0` to `HolodiskNum` then detach
  the script), guarded doors/containers (`Val1` = guard NPC role — warnings
  then `NpcPlanes::AddAttackPlane` on the third attempt), deferred destroy
  (`SetDestroyItem` hours). Static scenery uses `StaticScript` dispatched
  through `Game.CallStaticItemFunction` in the skill pipeline (37 maps use
  `Scenery::Dialog` alone).
- [Scripts/RespawnItem.fos](../Scripts/RespawnItem.fos): self-restoring map
  items — modes same-hex / into a map NPC / into a map container / near
  entrance N; optional no-pick gating by a critter var.
- [Scripts/EncounterItems.fos](../Scripts/EncounterItems.fos): wilderness
  encounter loot — a ~100-row table (pid, encounter terrain type, count
  min/max, chance, hex class) consumed by `GenerateItems`, spawn count
  influenced by the group's *minimum Luck* (`Random(0, Clamp(minLuck, 3, 8))`).
  This is not a strict cap: the loop stops only after the selected-entry
  count exceeds that sampled value.
- [Scripts/NpcBags.fos](../Scripts/NpcBags.fos): NPC random inventory from
  `BagsConfig.json` by `BagId`, nested child bags, refreshed every
  `Item.BagRefreshTime` (60 real minutes).

## `.foitem` format and families

INI-like `[ProtoItem]` sections; `$Name` fixes the proto id (becomes
`Content::Item::<name>`), `$Parent = <names>` resolves parents recursively
from the loaded catalog, in the written parent-list order. A parent need
not precede its child in the file. Repeated inheritance paths are governed
by `Baking.AllowRepeatedProtoParents`; cycles remain errors.
`$Text russ/engl [Desc]` embed localized name/description (baked by the
`ProtoText` baker into client text packs). Representative contracts:

- Weapon (`Items/_10mm_pistol.foitem`): per-use-slot indexed props
  (`Weapon_Skill_0..2`, `Weapon_DmgMin/Max_0`, `Weapon_MaxDist_0`,
  `Weapon_Round_0`, `Weapon_ApCost_0`, `Weapon_Aim_0`, …; `Weapon_ActiveUses`
  counts live slots), `Weapon_Caliber`/`DefaultAmmoPid`/`MaxAmmoCount`,
  `Weapon_CriticalFailture` selects the critical-miss table row,
  `Weapon_StateAnim` gates equipping by critter model, `Deteriorable`.
- Armor (`Items/combat_armor.foitem`): `Armor_AC`, `Armor_Perk`,
  `Armor_DR*/DT*` per damage type (these feed the virtual DR/DT properties —
  see [Character](Character.md)), `Armor_CrTypeMale/Female` model bases.
- Ammo (`Items/_10mm_jhp.foitem`): `Ammo_AcMod` modifies the to-hit AC term,
  while `Ammo_DrMod` modifies damage resistance;
  `Ammo_DmgMult/DmgDiv` (damage multipliers), proto-level `Count` seeds new
  stacks.
- Misc/container: `Stackable`, `Cost`, `Weight` (grams by convention),
  `Volume`, `IsCanPickUp/IsCanUse/IsCanUseOnSmth/IsCanOpen`,
  `Container_Volume`, `GroundLevel` (which hex-container transfer type opens).

Families at the source baseline: `Items/` root — 813 files/813 sections;
`Items/Static/` — 3848 files/7386 `[ProtoItem]` sections
(`generic_*`, `wall_*` families, heavily `$Parent`-derived);
`Items/Custom/` — 15 files/45 sections for project system protos
(`default_weapon`, `default_armor`, `Trigger`, `ExitGrid`, `Block`, …);
`Items/Explode/` — 5 explosion effect protos; `Items/Flying/` — 7 projectile
effect protos (both consumed by `Combat::CommenceExplosion`/`RunFlyEffect`).

## Changing items safely

Proto ids, `Content::Item::*` names and property names are serialized
contracts. Adding a proto: create the `.foitem`, reference
`Content::Item::<name>` after a bake; check `Tools/ContentQuality` text
parity expectations. Changing stacking/equip rules touches
`ItemStacks`/`ItemMovement` plus their consumers listed above — run
`Test_ItemStacks` and the container actions in `Test_CritterActions`, then
exercise pickup/container/barter paths in a client (see
[BuildAndLaunch](BuildAndLaunch.md#local-runtime-and-tests)).
