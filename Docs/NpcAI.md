# NPC AI

The plane-based NPC behavior system: the plane queue, the global decision
layer, Fallout 2 AI packets, behavior patterns, guards, mercs and pets.
Combat execution used by planes is [Combat](Combat.md); planes call
`CritterActions::Attack/PickItem/MoveInvItem` like any other client.
Source baseline: project `a213c7abe`, Engine `28c84c5d9d`;
static review on 2026-10-29.

## The plane model — [Scripts/NpcPlanes.fos](../Scripts/NpcPlanes.fos)

Every non-player critter runs a 1-second repeating time event (first fire
randomized) → `ProcessAi`. Its behavior is a priority queue of **planes**,
held in the script-side pool `dict<ident, NpcPlane[]> AllNpcPlanes`
(`NpcPlanes.fos`) — planes are *not* persisted and are dropped when the
NPC leaves a map (`OnMapCritterOut` → `DropPlanes`). A declared
`Critter.Planes` property is a migration breadcrumb, not the live pool.

| Type | Const | Default priority |
| --- | --- | --- |
| Misc (timed callback) | `AI_PLANE_MISC` = 0 | 10 |
| Attack | `AI_PLANE_ATTACK` = 1 | 50 |
| Walk | `AI_PLANE_WALK` = 2 | 20 |
| Pick | `AI_PLANE_PICK` = 3 | 35 |
| Patrol / Courier | 4 / 5 | 25 / 30 (marked "in development") |

Higher priority runs first; `planes[0]` is current; max
`MAX_PLANES_PER_CRITTER = 10`. `NpcPlane` fields carry per-type payloads
(`Attack_TargId/MinHp/GagHex`, `Walk_Hex/Dir/Cut`, `Pick_Hex/Pid/ToOpen`,
`Misc_WaitSecond/Script`) plus generic `Identifier`/`IdentifierExt` used by
patterns to find their planes. Child planes (`SetChild`) let a plane spawn a
temporary sub-goal. The deepest child executes first; when it completes,
that child is detached and the parent remains queued to resume.

Lifecycle hooks: `Game.OnNpcPlaneBegin/End/Run` (+ critter-level). `AddPlane`
inserts sorted by priority and fires `OnNpcPlaneBegin` — `StopChain` vetoes
(the plane is discarded). `NextPlane(reason)` fires `OnNpcPlaneEnd`;
`ContinueChain` removes the plane, `StopChain` **re-queues** it behind equal
priorities (a handler veto keeps the plane alive). The `REASON_*` vocabulary
(`NpcPlanes.fos`) is the API between the engine-side execution and the
decision layer: begin `GO_HOME/FOUND_IN_ENEMY_STACK/FROM_DIALOG/FROM_SCRIPT/
RUN_AWAY`, end `SUCCESS/HEX_BUSY/DEADLOCK/TRACE_FAIL/...`, run
`ATTACK_WEAPON/ATTACK_DISTANTION/ATTACK_USE_AIM`.

`ProcessAi` per tick: busy critters wait; without a current plane the NPC
talks → wait, scans its **enemy stack** (`EnemyStack::ScanEnemyStack`,
persistent `ident[] EnemyStack` of attackers — filled by combat, guards,
team alarms) and attacks a visible enemy, else walks/faces home
(`HomeDir`). With a plane: movement bookkeeping (damaged legs/overweight
disable running; move-AP deficits convert to a wait; being blocked by a
critter/door fires `GAG_CRITTER`/`GAG_ITEM` *before* `StopMoving`), then the
type switch — attack resolves weapon → distance → aim in three `OnNpcPlaneRun`
steps and finally calls `CritterActions::Attack`; walk/pick move and act at
range `1 + Multihex`.

## The decision layer — [Scripts/MainPlanes.fos](../Scripts/MainPlanes.fos)

Subscribed to all plane events; this is where AI packets turn into behavior:

- `NpcPlaneEnd`: navigation failures → short or 20 s waits. The
  `CANT_SEE_TARGET` recovery handler needs a non-null `someCr` to create a
  child walk-plane, but `ProcessAi` calls `NextPlane`, which supplies null;
  that traced path does not establish the intended recovery. Other branches:
  `GAG_CRITTER` by a player → child gag-attack plane; `GAG_ITEM` → child pick
  plane (doors opened if `AiCanOpenDoors` and a key is available); `RUN_AWAY`
  → flee 30–50 hexes opposite the threat and bark; `NO_UNARMED` → silently
  restore one broken weapon and wait.
- `NpcPlaneRun`: `ATTACK_WEAPON` picks the weapon (best combat skill with
  `BestWeap` preference, reuse of `LastWeaponId`, proto special cases,
  unarmed fallback distribution); `ATTACK_DISTANTION` computes approach or
  retreat (`r2 <= 0` → run away; safe distances per weapon family; melee
  closing); `ATTACK_USE_AIM` runs `CogitateFiring` — burst validation
  (friendly-fire trace on three lines), aim scoring (to-hit × location
  weight ÷ AP), AP-shortfall → wait time.

## Fallout 2 AI packets — [Scripts/Ai.fos](../Scripts/Ai.fos) + [Scripts/AiSettings.fos](../Scripts/AiSettings.fos)

`AiId` on the critter proto (e.g. `Critters/AHS9.focr` `AiId = 24`) selects a
row of the original `ai.txt` table — 282 packets, 22 columns, kept verbatim
in `AiSettings::AIData_`. Typed getters (`AiMinToHit`, `AiBestWeapon`,
`AiRunAway`, `AiCanOpenDoors`, `AiMessageChance`, …) fall back to packet 0
for ids at or above `Count`; negative ids are not guarded there. The
`Aggr` column is read but currently unconsumed —
the live aggression knobs are `AiMinToHit` (retreat threshold),
`AiBestWeapon`, door opening and the runaway handling above. Combat barks
(`AiSettings::TrySayCombatText`) roll `MessChance < Random(1,500)` and index
general/body phrase tables by packet `GeneralType`/`BodyType`.

## Behavior patterns

Patterns are script attachments, not a registry: they hang on `NpcRole`
families (`AiPattern::PatternInit`, roles 21-24 sniper / 31-35 term / 41-45
medic / 51-55 slayer), but in live content they are attached as **init
scripts of worldmap encounter groups** (`.Script(AiPattern::Term1Init)` in
`Scripts/Worldmap.fos`), per map/team via `FighterPattern::SetMapMobsTemplate`,
per dialog via `Merc::Merc2Player`, or from item scripts (`Pet::BoxUse`).

- `PatternCommon` — base: inter-NPC messages (`MsgAttackTarget`,
  `MsgHealme`, …, radius 12), stim use under 50% HP, auto-attack on seen
  players, corpse gear degradation, team-fire veto.
- `PatternSniper` — players only, always aims eyes, evaluates escape 60 game
  seconds after a shot and flees toward the fewest players (runaway plane
  `Identifier = 76`, priority 100), re-hides with sneak.
- `PatternMedic` — heals teammates on `MsgHealme` (walk plane
  `Identifier = 124`, then `Drugs::UseDrugOn` with a super stimpak),
  self-heal priority tiers.
- `PatternSlayer` — melee sneaker: forces run/sneak during attack planes,
  eye-aimed melee, attacks seen players within 10 hexes.
- `PatternTerm` — heavy gunner: distance-based weapon swap (flamer ≤ 5,
  minigun 6-30, rockets beyond), anti-sneak flare drops.
- `FighterPattern` — map/team combat template: spotter raises a team alarm
  (`MSG_KILLEM` to N allies in radius), dead-allies counters escalate to
  local/global map alarms, self-heal below a threshold, optional forced
  armor levels (+resists/HP, high tiers may grant Terminator).

## Guards, mercs, pets

- [Scripts/GuardLib.fos](../Scripts/GuardLib.fos) — town-guard prototype
  (parts explicitly unfinished): per-guard observation of players with an
  alert counter (weapon drawn → warn, holster → cool; gunshot at 4× sight →
  alarm; stealing → attack plane at half HP; alcohol/drugs/explosives
  escalate), `GuardWarn` walks toward, then attacks stopping ~10 HP above
  zero. Patrol/courier job constants exist but are unimplemented (matching
  the dormant plane types).
- [Scripts/Merc.fos](../Scripts/Merc.fos) — hireable followers: contract
  properties (`MercMasterId`, `MercLoseDist`, `MercDefendMaster`,
  `MercCancelTime`, default contract 90 game days), follow/teleport across
  maps, charisma-capped global-group pull, defend/assist reactions,
  dialog-facing API (`AddMerc2Player`, `WaitMaster`, `GetPlayerMercs`).
- [Scripts/Pet.fos](../Scripts/Pet.fos) — non-combat pets stored in a box
  item: invulnerable followers with a lifetime, follow-or-despawn idle,
  instant destruction when attacked (to free corridors).

## Extension and verification

New autonomous behavior = a plane type or an `Identifier`-tagged plane
consumed in a pattern + subscription to the plane events; new decision
inputs usually belong in `MainPlanes` or a pattern, not in `ProcessAi`.
`Scripts/Tests/Test_NpcPlanes.fos` is the regression owner for the queue
mechanics; plane-driven behavior changes need a live NPC exercise (spawn an
encounter or use `Docs/AiControl.md` playtests) — a headless startup does
not exercise AI ticks meaningfully.
