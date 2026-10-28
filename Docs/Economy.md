# Economy

Barter pricing, the caps currency, NPC traders, the FixBoy crafting system,
skill and paid repair. Items/stacking contracts are [Items](Items.md);
replication money is covered with the death flow in
[PlayerLifecycle](PlayerLifecycle.md). Source baseline: project `a213c7abe`,
Engine `28c84c5d9d`; static review on 2026-10-29.

## Barter — [Scripts/Barter.fos](../Scripts/Barter.fos)

Barter is a guarded container session, not a transfer type (see
[Items](Items.md#containers-and-transfers)) — this is what stops a client
from simply "taking" NPC goods.

- **Coefficient**: `k = Clamp(npcSkillBarter − playerSkillBarter, 5, 95)`
  (`Barter.fos`); the NPC's skill comes from `Parameters`
  (`BarterCoefficient` = `SkillBarter`). No karma/reputation input anywhere
  in the chain.
- **Prices**: player sells at `cost·(100−k)/100`, buys at
  `cost·(100+k)/100` (min 1 for positive base Cost; nonpositive Cost yields
  0 and the offer rejects that item). Master Trader removes the buy markup
  only. A deal is accepted iff `sellCost ≥ buyCost` and `sellCost > 0`.
- **Session**: `StartNpcBarter` (from the dialog `Answer Barter` link)
  refuses `IsNoBarter` NPCs, sends the trader's inventory, and sets
  `TransferType = CritBarter` with a fresh `TransferSession`. The client
  mirrors pricing for display only.
- **`ProcessBarterNpcOffer`** (server RPC via `Scripts/ClientItems.fos`)
  re-validates everything: session identity, list shape (≤ 512, no duplicate
  ids), both alive, same map, within `Dialog.TalkDistance`, then recomputes
  `k` server-side and both totals from real inventory (`OnItemCheckMove`
  per item), rejects overweight results, and fires `Game.OnItemsBarter` —
  whose global handler in `Main.fos` enforces **caps-only traders**
  (`IsBarterOnlyCash`: sale side may contain only `bottle_caps`) and the
  per-NPC proto white lists of [Scripts/LimitedBarter.fos](../Scripts/LimitedBarter.fos).
  Items then move both directions through `ItemMovement::MoveItem`.
- Regression owner: `Scripts/Tests/Test_Barter.fos`.

## Currency

`bottle_caps` is the only general currency — an ordinary stackable item
valued by `Cost` in barter. Scripted caps flows: gambling (`Casino`, `Poker`
with `WinKoef` prize multipliers, `Roulette`, `NukeMachine`), the
replication-terminal account (`ReplicationMoney`, 1:1 with physical caps;
player-to-player transfers while both online), the bank vault entry fee
(100 caps), NPC repair, caravan/job/quest rewards, and loot faucets
(caravans, event caches, player-base bags). `kokoweef_mine_scrip` exists as
an item but has **no redemption consumer** — a collectible, not a currency.

## NPC traders — [Scripts/Trader.fos](../Scripts/Trader.fos)

Trader stock and skills come from `Resources/ServerData/TraderTable.json`
(79 entries: dialog id, refresh hours, barter skill, goods list); matching
is by `DialogId` after `TraderInit` (or a wrapper) is actually called.
A dialog binding alone does not install restocking behavior.
`TraderInit` (used as map `InitScript`, e.g. Whiskey Bob) sets `BagId = 0`
(no random loot bag), talk distance 5, `MaxTalkers 6`, `IsNoDrop/IsNoSteal/
IsNoLoot`, and the table's `SkillBarter` (which drives the barter
coefficient). `CashTraderInit` additionally makes the trader caps-only.
Restock (`UpdateItems` time event): items in the Inventory slot are destroyed and
recreated from the table, **deteriorable goods spawn with random 5–25%
wear** (`Repair::SetDeterioration(item, Random(5, 25))` — stock is never
mint), and the next refresh is `hours·Random(50,150)%`. Dead traders retry
after their replication timeout.

## Crafting — [Scripts/FixBoy.fos](../Scripts/FixBoy.fos)

Recipes live in `Resources/ServerData/CraftRecipes.json` (95 entries at this
revision), loaded at server start; each entry: `out` (+`count`), `exp`,
`resources` and `tools` lists of `{pid, count, flag}` — a `flag = 1` marks
"another alternative follows", so consecutive flagged entries form an OR
group (any one satisfies and is consumed), `onView`/`onCraft` gates
(`{prop, value}` restricted to SPECIAL/skill names), and an optional
`script` hook (fixed whitelist: `AnyRounds`, `PowerArmor`, `ChitinArmor`,
…). **Tools are required but never consumed; resources are consumed.**
Crafted items are created by `ItemStacks::AddItem` — always mint
(deterioration 0). Experience comes from the JSON `exp` field; the loader's
missing-field default is 0 (it explicitly supplies this value, bypassing
the constructor's 50 default). `Player.FixBoyDefaultExperience` in [TLA.fomain](../TLA.fomain) is a
legacy declaration with **no consumer**.

`Rpc_CraftItem` (`[[ServerRemoteCall]]`, `FixBoy.fos`) is the only entry:
state `FixboyList` builds the visible list (view-gated; each entry carries a
craftability flag), the detail view, or executes `CraftedItem` at
`FixboyButton`. `CraftedItem` checks `CheckOnCraft` and resources/tools on
the server before consuming and granting; `OnView` is a list-visibility
gate and is not re-run by that execution path. The client only renders.

Workbench-bound recipes add: knowledge gating by a per-character critter
property, proximity (`GetStaticItemsInRadius`, default radius 5) to a
specific scenery proto (lathe, ammo press, Shi/Hub benches, stove…),
per-map **charges** shared by identical benches
(`FixBoyWorkBenchCharges/Timeout` map properties keyed by scenery pid;
default refill timeout `GameDays(17 − Luck)`), paper recipes
(`ByRecipe` — the recipe item is destroyed on craft), and the
`AdvancedCraft` luck upgrade path (e.g. chitin armor MK-II: thresholds
15/10/5 by Luck tier against `Random(0,100) < chance`, hence chance/101,
not exact percentages). That upgrade requires more than 3 `metal_trash`
and consumes 2 only on success.

## Repair services

- **Skill repair** (own items) is part of [Items](Items.md#deterioration-and-repair)
  (`Repair::TryRepairItem`): tools +25/+50, broken penalties, +40/+20 XP,
  failure damages the item.
- **Paid NPC repair** — [Scripts/Repairer.fos](../Scripts/Repairer.fos):
  dialog-driven, item must be in hand, NPC capability flags
  (`CanRepairWeapons/Armor[+Special]` with rare-item lists). Cost for a
  fully worn item: `Clamp(0.95·Cost·npcSkillBarter·wear% /
  (playerSkillBarter·99), 0.05·Cost, 0.95·Cost)`; repair time
  `(3h − npcSkillRepair·3h/300)·wear%/99` game hours. `TakeForRepair`
  **destroys the physical item** and records `RepairCompleteTime`/pid on
  the player; after the deadline the NPC re-creates a brand-new item
  (`ItemStacks::AddItem`, weapons unloaded) — full condition by
  construction. Wear-to-price coupling (`Repair::SetItemCost`: 100% wear →
  Cost/3, >75% → 2·Cost/3) is why damaged loot sells cheaper.
- The **replication trader** is not a shop: a free starter-gear faucet
  (6 h/24 h cooldowns, quality rolls `Random(0, Luck) + Speech/10`,
  deliberately trash wear/flags) — see [PlayerLifecycle](PlayerLifecycle.md).

## Town "supply"

[Scripts/TownSupply.fos](../Scripts/TownSupply.fos) is law enforcement, not
goods: killing an eligible humanoid NPC in a city with a player killer
(`Main::CritterDead`, `IsValidForSupply`; no peaceful-state check) schedules a bounty-hunter
hit squad after `Random(5, 60)` game minutes (up to 10 offline-aware
retries); squad size `Level/10 + 1` (max 10), spawned from
`BountyHunter_1..10` protos with sniper/slayer/terminator perks, attacking
the offender and leaving/self-destructing afterwards.

## Changing economy values safely

Prices are `Cost` fields on item protos (serialized contract); barter
formulas live in `Barter.fos` with a client mirror; recipe data changes are
`CraftRecipes.json` edits + server restart (loaded once at `Game.OnInit`);
trader stock is `TraderTable.json` + `TraderInit`. Verify with
`Test_Barter`, then a real barter/craft round-trip in a client
([BuildAndLaunch](BuildAndLaunch.md#local-runtime-and-tests)); JSON edits
additionally deserve a bake check since `ServerData` is a packed input.
