# Player lifecycle

Account registration and login, character creation, death, replication
(respawn), the replicator services, and Purgatory. Combat's death/knockout
transitions are [Combat](Combat.md); registration GUI screens are
[ContentWorkflow](ContentWorkflow.md) territory. Verified against revision
`e2b5b90b0` (static analysis).

## Registration and login

Entry module: [Scripts/PlayerRegistration.fos](../Scripts/PlayerRegistration.fos).

- Player names resolve through the DB collection `PlayerNames`
  (`{_Name, CritterId}` reservation → `{PlayerId}` on first login). The
  server-side registration contract (`RegisterNewPlayer` RPC) validates:
  the props set must equal `Game.RegProperties` exactly (7 SPECIAL `*Base`,
  `TagSkill1..3`, all traits, `Age`, `Gender`); each SPECIAL 1..10 and the
  **sum must equal `Player.StartSpecialPoints` (40)**; tag skills must be
  members of `CritterPropertyGroup::Skills`. Name rules
  (`Parameters::CheckPlayerName`): 4–12 chars, only
  `Account.ValidNameLetters*` alphabets, no Latin/Cyrillic mixing, ≥70%
  letters, no double/edge spaces. The **tag-skill count (3) is enforced
  client-side only**.
- Creation: `Game.CreateCritter(Content::Critter::Player, …)` + name
  reservation + `MakePersistent(true)` (without it, a map unload would
  clear the implicit persistent flag and delete the DB document) →
  `Main::PlacePlayerAfterInitialization` → rollback destroys critter and
  reservation on any failure. `MainCritterId` must be set before
  `Game.LoginPlayerToNewRecord`.
- Existing login (`LoginExistingPlayer`): resolves the stored
  `MainCritterId`, loads the critter, reuses a live instance on re-login
  races (unload rollback otherwise). The password is cached client-side but
  not sent by these RPCs. The traced project and Engine admission path does
  not validate it; encrypted transport does not establish password authentication.
- `Main::PlayerLogin` checks `player.Id` in `Replication::PermanentDeath`
  when `Combat.PermanentDeath > 0` (0 = disabled by default), while the
  death path records `cr.Id`. Different player/critter IDs make the intended
  refusal unreliable; this discrepancy needs a separate gameplay fix. Login
  timeouts are engine settings (`ServerNetwork.LoginTimeout`, 0 in dev
  subconfigs).

## Init — `Main::CritterInit` (`Scripts/Main.fos:902`)

First-time player setup: ≤2 traits, gender clamp, age 14–80 (default 25),
SPECIAL clamps and budget re-check (a mismatched sum resets to all 5s),
`EmpResistanceBase = 500`, holodisk #42, default skin models,
`Parameters::CritterGenerate(props)` (derived stats, skill bases +20 per
tag, `MaxLifeBase += 15`, full HP/AP), and the player economy seed:
`ReplicationCost = 100`, `ReplicationMoney = 0`, `ReplicationCount = 0`,
`TeamId = 1`. **No starting items** — starter gear is the replication
trader's free set (below). Non-first-time inits apply migrations (e.g.
`FastShot → IsNoAim`). The per-second `CritterIdle` heartbeat (also the AP
regeneration and replication driver — see [Combat](Combat.md#action-points))
starts here.

## Death — `Main::CritterDead` (`Scripts/Main.fos:1160`)

1. Hand slots are moved into inventory so the corpse is fully lootable.
2. Inventory + hand items are **dropped on the ground** only when the death
   animation is `DeadPulseDust`/`DeadExplode` (energy/explosive deaths) and
   `Tla::CanCritterDropItemsOnDead` (`!IsNoSteal && !IsNoDrop`) — armor is
   kept; `IsGag` items are destroyed, `Hidden` items kept.
3. Mob-specific loot (gecko pelts need the skinning perk, scorpion tails…),
   karma adjustments for player kills by victim team, child-killer karma,
   and the town-supply bounty hook (see [Economy](Economy.md#town-supply)).
4. `Replication::SetReplicationTime` schedules the respawn; NPC planes are
   dropped; a `DeadDrawNoFlatten` corpse gets an invisible blocker item
   (removed on respawn).
5. Witness/map events fire (`map.OnCritterDead` drives Purgatory scoring).

## Replication — [Scripts/Replication.fos](../Scripts/Replication.fos)

Timer: `ReplicationTime < 0` = never (spawned-dead NPCs); `0` = default —
**player 3 minutes, NPC Random(90, 120) minutes**; the `CritterIdle`
heartbeat calls `ReplicateCritter` when the timeout expires (works while
the player is offline too).

`ReplicateCritter` branch order:

1. **Any car owner**, before the player/NPC split: with a global trip,
   attempt an empty encounter and transfer only the dead owner there. With
   no trip, or on failed transfer, destroy the cars. Remain dead and retry
   in 1 real minute.
2. **Custom target** (`NextReplicationMap` set — the Purgatory entry):
   select that map/entry; skip the account debit in the common player tail.
3. **Hell**: `ReplicationMoney < 0` → respawn on `HellMapPid`
   (`Content::Map::repl1` today; a TODO keeps the real hell map
   `repl_hell` out of play). Only death outside a hell map increments
   `HellVisits` and triggers the first-visit video/permanent-death threshold.
   Exceeding that threshold records the critter ID and disconnects; see the
   player/critter ID mismatch above before assuming a login ban.
4. **Normal**: nearest replicator map (`repl1..4` by world distance;
   `replication_4` is excluded while the replicator-station event flag is
   active). Missing maps or blocked entries retry in 1 real minute.
5. **Common player tail** after selecting custom/hell/normal destination:
   if `CanCritterDropItemsOnDead`, inspect all owned items, including armor;
   destroy `IsGag`, retain `Hidden`, drop the rest on the source map (or
   destroy the drop-list when no source map exists). This differs from the
   death-animation drop rules. Recheck the target entry after item callbacks.
   Debit `ReplicationCost` and grant a flower (+radio when resulting balance
   is at least 100) only for `!customReplMap && !dieMapIsHell`, independently
   of the chosen destination. Increment count for every non-custom replicate;
   otherwise clear the custom map/entry. With `HellMapPid=repl1`, even the
   normal replicator may count as hell: infer charges from the source-map
   predicate rather than a universal "first free respawn" sequence.
6. **Revival**: `CritterState::ToAlive`, full HP/AP, limb/eye damage
   cleared, poison/radiation cleared, drug effects cleared **except in
   hell** (players stay drugged there), all timeouts zeroed except karma
   voting.

NPC branch: planes/enemy stack cleared; global-map NPCs are destroyed,
map NPCs respawn on the same hex (neighbor search honoring hex parity).

## Replicator services

- **Terminal** ([Scripts/ReplicationTerminal.fos](../Scripts/ReplicationTerminal.fos)):
  the `ReplicationMoney` account — deposit/withdraw caps 1:1, player-to-
  player transfers (target must be online), text-input dialog state machine.
- **Bank** ([Scripts/ReplicationBank.fos](../Scripts/ReplicationBank.fos)):
  paid item storage — 100 caps entry fee, one player per 2-minute session,
  per-player hidden container stacks (`Tla::MakeContainerStack(playerId)`),
  guards attack thieves/explosive carriers and eject overstayers.
- **Trader** ([Scripts/ReplicationTrader.fos](../Scripts/ReplicationTrader.fos)):
  free starter-gear faucet (6 h since a *different* player's claim / 24 h
  same player; quality `Random(0, Luck) + Speech/10`, deliberately worn and
  sometimes flagged-broken gear; `GiveAnything` needs Speech > 90).

## Purgatory — [Scripts/Purgatory.fos](../Scripts/Purgatory.fos)

Purgatory implements a four-stage team PvP event ("The Trial"). Its monthly
schedule is declared in `GameEvent.fos`, but ordinary startup comments out
`DeclareEvents` and `CheckAllGameEvents`; that schedule is dormant.
The declared sequence is prepare (radio announcements, "Executor" recruiters in every city)
→ begin (+1 game day, teams of invitees, round-robin waves) → fight
(+5 min, doors open, hired NPC lines aggro) → finish (+2 game days).
**Joining is implemented as death**: all items move into the team
container, `CritterState::ToDead` runs, and `NextReplicationMap/Entry` is
set so the player re-enters through the ordinary replication pipeline
(cost refunded on arrival). Scoring per kill up to 17 points
(level-difference bonuses, luck bonus, team-kill negatives); rewards:
team-kill −1000 repl-money, enemy kill +300 and `Level·100` XP; the prize
pool lands in winner-side containers (caps × points·50, armor/weapon tiers
by points). State is a single in-memory global instance — one battle at a
time; that battle coordinator is not persisted. Spawned world data, rewards
and persistent properties (such as `LastLootTransfer`) have their own storage
contracts. The story intro
([Scripts/MainIntro.fos](../Scripts/MainIntro.fos)) reuses the same
death-replication trick for its finale (with the cost reset afterwards);
it is active only under `Story.MainStoryLineActive` (currently `False`).

## Disconnection

The critter stays in the world after disconnect; the `CritterIdle`
heartbeat unloads it (`Game.UnloadCritter`) once the player is gone for
`Account.MinimumOfflineTime` (3 minutes) and `TimeoutRemoveFromGame` has
expired — the persistent DB document
survives. Re-login races reuse the live critter. `Main::CritterFinish`
closes any open transfer session and removes the corpse blocker.

## Verification notes

Static source trace at the revision above. `Scripts/Tests/Test_PlayerRegistration.fos`
covers registration validation; death/replication has **no harness suite**
— verify changes through a real death (normal, hell-balance, car-owner) in
a local client, and remember the default Memory DB loses everything on
server restart (see [BuildAndLaunch](BuildAndLaunch.md#local-runtime-and-tests)).
