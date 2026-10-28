# Combat

Deep dive into TLA's real-time combat: the attack pipeline, action points,
hit chance, damage/armor/criticals and critter condition transitions. The
routing overview is [Systems](Systems.md); the single-threaded/server-authority
contract is [Scripts](Scripts.md). Animation of combat results on the client is
covered by [Animation](Animation.md). Source baseline: project `a213c7abe`,
Engine `28c84c5d9d`; static review on 2026-10-29 (verification limits below).

## Modules and ownership

| Module | Side | Responsibility |
| --- | --- | --- |
| [Scripts/Combat.fos](../Scripts/Combat.fos) | S | Hit/damage resolution: `CombatAttack`, `ApplyDamage`, `CommenceExplosion`, `CriticalFailure`, `InjureCritter`, the Fallout critical tables. |
| [Scripts/CritterActions.fos](../Scripts/CritterActions.fos) | S | Validated execution of player/NPC intents: `Attack`, `ReloadWeapon`, `UseSkill`, `UseItemOn`, pick/drop, container transfers; AP spending via `ProcessAp`. |
| [Scripts/ChosenActions.fos](../Scripts/ChosenActions.fos) | S/C | Client: input queue (`ChosenProcess`), AP prediction, remote calls. Server: `[[ServerRemoteCall]]` entry points that resolve the controlled critter and delegate to `CritterActions`. |
| [Scripts/CritterState.fos](../Scripts/CritterState.fos) | S | Condition transitions: `ToDead`, `ToKnockout`, `TryUpOnKnockout`, `ToAlive`; wait/busy timers (`Wait`, `IsBusy`). |
| [Scripts/Parameters.fos](../Scripts/Parameters.fos) | S/C | Derived stats used by combat (registered as engine property getters) and AP cost/range calculations (`GetItemUseApCost`, `GetItemAttackDistance`). |
| [Scripts/WeaponHelpers.fos](../Scripts/WeaponHelpers.fos) | S/C | Reads weapon-proto use data: skill, distance, damage, rounds, AP cost, effect per use slot. |
| [Scripts/GameTime.fos](../Scripts/GameTime.fos) | S | Combat/sneak/healing timeout formulas (`GameTime::BattleTimeout` …). |
| [Scripts/SmokeGrenade.fos](../Scripts/SmokeGrenade.fos) | S | Smoke/mustard gas clouds and the ranged to-hit penalty `GetSmokePenalty`. |
| [Scripts/NoPvpMaps.fos](../Scripts/NoPvpMaps.fos) | S | Safe-zone mode: marks maps `IsNoPvPMap`, toggles `IsNoPvp` on entry/exit. |

## The path of one attack

1. **Input.** The click is queued client-side in `ChosenActions`
   (`ChosenProcess` runs the queue; movement re-targeting rules live there).
   The attack action checks AP locally for UX only, then sends
   `CurPlayer.ServerCall.Attack(targetId, mode)`.
2. **RPC arrival.** `ChosenActions::Attack` (`[[ServerRemoteCall]]`,
   `Scripts/ChosenActions.fos`) resolves `player.GetControlledCritter()`
   and calls `CritterActions::Attack(cr, targetId, mode)`.
3. **Validation** (`CritterActions::Attack`, `Scripts/CritterActions.fos`):
   aim byte range (client-supplied `aim` outside `LocationNone..LocationUncalled`
   used to give free aimed shots and read foreign critical-table rows — now an
   exception), active item is a weapon, two-handed vs. damaged arms, use slot
   exists, aim allowed for weapon/`IsNoAim`, AP cost from
   `Parameters::GetItemUseApCost`, sight/alive checks, distance vs.
   `Parameters::GetCritterAttackDistance`, straight path trace, ammo
   resolution (loaded ammo proto, else weapon default), and
   `cr.TimeoutAggressor = Game.SynchronizedTime + 1 minute`.
   Rejections are `throw(...)` server exceptions (logged), not silent no-ops.
4. **Resolution.** `Combat::CombatAttack` computes hit chance, rolls, and
   dispatches per weapon class (below).
5. **Damage.** `Combat::ApplyDamage` applies armor, critical effects, HP loss,
   and calls `CritterState::ToDead`/`ToKnockout`.
6. **Reporting.** Effects are appended per-critter into a binary search tree
   of `CombatRes` nodes (`Combat::AddEff`) and flushed once per attack with
   `Combat::FlushResults` → each player's `PlayerClientCall.CombatResult(...)`
   (client handler `ClientMain::CombatResult`, `Scripts/ClientMain.fos`).
   Observers are chosen as `target.GetCritters(WhoSeeMe, Players)` — the set
   of players who can *see* each affected critter.

## Action points

- Storage is `int32 CurrentAp` (`Scripts/CritterProps.fos`, `NoSync`) in
  hundredths: `Tla::AP_DIVIDER = 100` (`Scripts/Tla.fos`). Max is
  `ActionPoints * 100` where `ActionPoints` is a virtual property computed by
  `Parameters::CritterGetActionPoints`.
- **Spending** (`CritterActions::ProcessAp`, `Scripts/CritterActions.fos`):
  if not enough AP, the critter is *put on wait* until regeneration would
  cover the deficit (`Wait(apRegeneration / ActionPoints * missingAp)`) and
  the action returns false — it is not queued. On success the server computes
  `(CurrentAp / 100 - cost) * 100`, discarding fractional AP, sets
  `ApRegenerationTick = FrameTime + Breaktime` and applies the
  `Movement.Breaktime` (1200 ms) busy pause to pace actions.
- **Regeneration (authoritative)** happens in `Main::CritterIdle`
  (`Scripts/Main.fos`, `CritterInit`/`CritterIdle`), a `[[TimeEvent]]`
  explicitly scheduled every 1000 ms. The 10000 ms `Critter.CritterIdleTick`
  setting and the old comment do not control this call. A pass with `delta >= 500 ms`
  adds `maxAp * delta.ms / apRegeneration`, clamped to max.
  `apRegeneration` is the critter's `ApRegenerationTime` or the default
  `Combat.ApRegeneration` (7000 ms) when zero. The client runs the same
  formula in `ChosenProcess` (`Scripts/ChosenActions.fos`) as a
  prediction. `CurrentAp` is `NoSync`; do not assume automatic reconciliation
  of this property. Server-side `ProcessAp` remains the action authority.
- **AP cost** (`Parameters::GetItemUseApCost`, `Scripts/Parameters.fos`):

```text
use == USE_USE        -> Movement.RtApCostUseItem (3)
use == USE_RELOAD     -> Movement.RtApCostReloadWeapon (2); -1 for weapon FastReload perk
weapon attack use     -> WeaponApCost(proto, use)
                         + GetAimApCost(aim)          if aimed (Combat.ApCostAim*, all 1)
                         - 1 if HtH attack  and BonusHthAttacks perk
                         - 1 if ranged attack and BonusRateOfFire perk
                         - 1 if FastShot trait and not HtH
final clamped to >= 1
```

That is the helper's cost calculation. `CritterActions::ReloadWeapon`
actually spends the fixed `RtApCostReloadWeapon`; the helper's FastReload
discount is not evidence that the server execution applies it.

- Movement AP costs (`Movement.RtApCost*` in [TLA.fomain](../TLA.fomain)):
  pick item 4, use item 3, use skill / reload / move-in-inventory 2, drop /
  pick critter 1; container move and walking/running themselves cost 0.
- **Knockout interacts with AP**: `CritterState::ToKnockout` records an AP debt
  `KnockoutAp`; the 1-second idle event `CritterState::OnCritterIdle` pays the
  debt from regenerating AP (`TryUpOnKnockout`) — a knocked-out critter stands
  up only after its AP debt is cleared and `CurrentAp >= 0`.

## Hit chance

Server resolution is in `Combat::CombatAttack`. The attack cursor uses its
own formula in `ClientMain::ToHit`, including aim and a final clamp.
`Combat::RawToHit` is a separate server helper used by AI; it omits aim,
Vampire Accuracy and the final clamp. Changes need a comparison of all three
consumers rather than an assumption that one delegates to another.

```text
baseToHit = weapon skill value
          - 25 if attacker IsDamagedEye
          + 13 if PerkVampireAccuracy and night        (quest perk)
          + 20 one-hander with one-handed weapon / -40 two-handed (not unarmed)
          - 20 per point of Strength shortfall below Weapon_MinStrength
            (Weapon Handling perk adds +3 ST; unarmed attacks skip ST/OneHander)
          + 20 if weapon perk Accurate

toHit = baseToHit
      - GetHitAim(aim)            ranged; -half of it for HtH attacks
      - distance penalty (ranged only, see below)
      - max(0, target.ArmorClass + ammo.Ammo_AcMod)
      + 40 if target knocked out
      + 15 if target Multihex > 0
      - 10 per blocking critter on the line, ranged only
        (a knocked-out target doesn't block itself)
toHit = clamp(toHit, 5, 95)
toHit -= SmokeGrenade::GetSmokePenalty(map, cr, target)   ranged only, AFTER clamp
```

Distance penalty for ranged weapons (recomputed per candidate target in
burst/spread code):

```text
distmod1 = 2 (4 LongRange perk, 5 ScopeRange perk), distmod2 = 0 (8 ScopeRange)
accloss  = (players: (PE-2) * distmod1; NPCs: PE * distmod1)
acc = dist; if dist < distmod2: acc += distmod2 else acc -= accloss
acc = max(acc, -2*PE); acc -= 2 * PerkSharpshooter
if acc > 0 and IsDamagedEye: acc *= 3
toHit += acc * -4
```

Throwing weapons cap `wpnMaxDist` to `3 * min(10, ST + 2*PerkHeaveHo)`.
`Combat.HitAim*` settings are the aim hit penalties (eyes 60, head 40,
groin/arms 30, legs 20, torso 0); aimed eyes behind the target's back
degrade to head. A burst (`rounds > 1`) always attacks unaimed.

## The roll and criticals

`margin = toHit - Game.Random(1, 100)`:

- **Miss** (`margin < 0`): unless `IsInvulnerable`, a critical miss can trigger
  (`-margin/10 >= Random(1,100)`; the Jinxed traits add a coin-flip chance).
  Severity `Random(1,100) - 5*(Luck-5)` is converted to tier 0..4
  (thresholds 20/50/75/95) before indexing
  `CriticalFailureTable[5 * Weapon_CriticalFailture + tier]`; flags `0` cancel
  the critical. `MF_HIT_RANDOMLY` re-targets via `ChooseRandomTarget`: start
  at a random index in the in-radius non-dead list and take the first candidate
  with a clear wall trace, excluding attacker and original target. Otherwise
  `CriticalFailure` executes the
  miss effects (self-damage, weapon drop/destroy/explode, lost ammo, lost
  turn, knockdown, crippled random limb) and reports
  `MessageSpecifications::CritMiss*`.
- **Hit**: `isCritical = Random(1,100) <= CriticalChance + margin/10 + HitAim(aim)`;
  guaranteed for HtH with the Slayer perk; Sniper perk rerolls crit on guns via
  `Random(1,10) <= Luck`; unarmed crit chance comes from the proto's
  `Weapon_UnarmedCriticalBonus`.

## Attack execution per weapon class

`CombatAttack` branches on weapon subtype (`WS_UNARMED/MELEE/THROWING/GUN`,
derived from the skill of the active use):

| Branch | Behavior |
| --- | --- |
| HtH (unarmed/melee) | Single `ApplyDamage`; sneak attack from behind with Silent Death doubles `DmgMul`. |
| Single gun shot | On miss, blockers on the line are tried with `toHit/3`; hit blocker takes the shot (`NotifyOops`). |
| Burst | `rounds = min(weaponRounds, AmmoCount)`; first `max(rounds/6, 1)` rounds at the target, the rest spread across the central line and — if the target is farther than 1 hex and `rounds > 3` — left/right adjacent lines (±89°), each critter consuming consecutive successful rolls until a miss. |
| Flamethrower | `flamer`/`improved_flamethrower`/gecko flame: checks hit rolls against candidates on the central and side lines; calls `ApplyDamage` once per distinct hit victim. Crit adds +20 to-hit past the clamp. |
| Rocket/explosive throwing | Hit → `CommenceExplosion`; miss → blockers at `toHit/3`, else an impact hex (grenades scatter randomly up to half the distance). Nonexplosive thrown knives/spears use direct damage and do not explode. |

`CommenceExplosion` runs the visual effect per pid (molotov/frag/pulse/plasma/
smoke/mustard/rocket/emp), then damages every non-dead critter in radius
(rockets 3, grenades 2). Smoke/mustard clouds only apply their cloud effects
(`SmokeGrenade::SmokeBlast`) and return. `EMP rockets` get +30/+40 damage and
`DamageTypes::Emp`.

## Damage: `ApplyDamage`

Order of operations (`Scripts/Combat.fos`):

1. Guards: dead target or missing map returns; PvP blocks (`IsNoPvp` on either
   player, or a NoPvp player hit by an ownerless mine); sneak modes dropped;
   battle/sneak timeouts (re)armed on the target.
2. Critical effect selection (only for crits or forced `ForceFlags`, used by
   `InjureCritter`): severity roll `Random(0,100) + 20 (BetterCriticals) -
   30 (HeavyHanded)` picks one of six table rows; the row indexes
   `CriticalTable[bt * 9*6*7 + aim_ * 6*7 + roll * 7]` with per-row damage
   multiplier (halved, `dmgMul >>= 1`), effect flags, an optional stat check
   (`Random(1,10) > stat + checkMod` upgrades to the failure effect/message),
   and two message ids (5000-series, `Texts/Combat.*.fotxt`). The table is the
   original Fallout 2 table (per body type: men, women, children, super
   mutant, ghoul, brahmin, radscorpion, rat, floater, centaur, robot, dog,
   mantis, deathclaw, spore plant, gecko, alien, giant ant, boss, giant
   beetle, wasp, player). Terminator perk can cancel a ranged crit
   (`(ST+EN base)*5 >= Random(1,100)`); `IsNoKnock`/`IsNoLooseLimbs`/`IsNoDrop`
   constrain effects (`IsNoKnock` specifically clears `HF_KNOCKDOWN`);
   EnhancedKnockout adds knockout. Stonewall can randomly cancel critical
   knockdown and separately reduces knockback distance.
3. Armor: `ApplyArmorModifiers(bypassArmor, penetrate, finesse, DRMod, DT, DR)`
   — armor-piercing crits (`HF_BYPASS_ARMOR`, not EMP) divide both DT and DR
   by 5 and disable the Finesse malus inside that branch; the Penetrate weapon
   perk divides DT by 5; Finesse adds +30 DR; ammo `Ammo_DrMod` adds; final DR
   clamped 0..100. Sources: `target.DamageResistance[type]` and
   `DamageThreshold[type]` (virtual properties from `Parameters`).
4. Per-hit damage (`ReduceDamage`, integer operations in this order): scale
   `dmg = roll * dmgMul / dmgDiv`, then `dmg -= DT`, then
   `dmg -= dmg * DR / 100`, finally clamp to at least 0. DR uses the
   post-DT value; for roll 100, multiplier/divisor 2/2, DT 10 and DR 50,
   the result is 45. `dmgMul` starts at 2 (the "/2" of the Fallout formula), is
   multiplied by the critical-table multiplier and `Ammo_DmgMult`;
   `dmgDiv = 2 * Ammo_DmgDiv`. HtH adds `MeleeDamage` to `DmgMax`; guns add
   `PerkBonusRangedDamage * 2` as bonus damage. After summing all rounds,
   LivingAnatomy adds 5 once (non-robot/alien) and Pyromaniac adds 5 once
   for fire damage; these are not per-round bonuses reduced by armor.
5. Condition effects and HP: limb/eye flags set on the target; `HF_DEATH`
   raises damage to at least `CurrentHp - Combat.DeadHitPoints`. Then
   `CurrentHp -= totalDmg`; if `CurrentHp < 1`: knockout when
   `CurrentHp > DeadHitPoints (-20)` and not `IsNoKnock`, else death.

## Death, knockout and knockback

- **Death** (`CritterState::ToDead`): lowers positive HP to 0, preserves
  negative HP, applies the supplied animation and fires `Game.OnCritterDead`,
  `cr.OnDead`, and `killer.OnKill`. It calls `StopMoving` before those events.
  `ApplyDamage` chooses the death animation
  by damage type/flags and handles the combat rewards. The killer receives
  `target.KillExperience`, kill counters per body type, and scores
  (`Scores::AddScore`, e.g. `Killer`/`Maniac`). Player death/respawn flow
  continues in [PlayerLifecycle](PlayerLifecycle.md).
- **Knockout** (`CritterState::ToKnockout`): traces a `LineTracer` ray from
  the attacker hex through the knockback direction (stopping before walls and
  before `Content::Item::Trigger` scenery), transfers the critter to the last
  free hex, sets the prone animation set, records the AP debt `KnockoutAp` and
  fires `Game.OnCritterKnockout`. Knockback distance (`ApplyDamage`): for
  explode/melee hits `knockDmg/10` (or `/5` with the Knockback weapon perk,
  halved again by Stonewall), `-1`, capped at 10 hexes. AP variants: plain
  knockdown costs 3 AP (1 with Quick Recovery), lost turn sets AP to
  `-maxAp`, knockout to `-Random(maxAp, 3*maxAp)`.
- Explosion damage over 9 sets the knockout candidate flag (`isKo`), even
  without critical flags. The eventual transition still depends on death,
  the target's current condition and `!IsNoKnock`.
- `InjureCritter` is the scripted-entry wrapper (traps, poison, events): it
  builds an `AttackStruct` with fixed damage and optional `ForceFlags` and
  runs the same `ApplyDamage`.

## Side effects of every attack

Sneak mode is dropped for attacker and target; `TimeoutBattle` is (re)armed as
`Game.SynchronizedTime + max(Combat.TimeoutBattle - ArmorClass, 12)` seconds
(AC shortens battle lock), `TimeoutSneak` as `max(34 - Sequence, 3)` s.
Ammo is consumed unless `IsUnlimitedAmmo`; a deteriorable weapon loses
`(MaxSkillValue - skillValue)/3` condition (`Repair::DeteriorateItem`), the
target's armor `((100-DR)*rounds + totalDmg)/3`; single-use weapons
(`Weapon_Remove`) are consumed; only non-grenade throwing weapons are placed
on the impact hex through `ItemStacks::AddItem`. Toxic/Radioactive attackers and specific body types
(radscorpion, floater, wasp, alien, centaur) apply poison/radiation resisted
by `Random(2,11) > Luck`. NPC combat barks go through
`AiSettings::TrySayCombatText`. `Game.OnCritterAttacked` always fires for the
original target.

## Settings (TLA.fomain)

| Setting | Value | Consumer |
| --- | --- | --- |
| `Combat.TimeoutBattle` | 45 s | `GameTime::BattleTimeout` (AC-shortened, min 12) |
| `Combat.ApRegeneration` | 7000 ms | AP regen divisor (`Main::CritterIdle`) |
| `Combat.DeadHitPoints` | -20 | Death/knockout threshold in `ApplyDamage` |
| `Combat.HitAim*` / `ApCostAim*` | 0..60 / 1 | Aim penalties and AP surcharge |
| `Combat.CombatMessagesType`, `Combat.DamageHitDelay` | 0 / 500 | Client message handling (`ClientMain::CombatResult`) |
| `Combat.NoPvpMaps` | True | Enables the module's checks; startup `SetNoPvp` map-marking call is commented out, so this alone does not establish safe zones on a fresh world |
| `Movement.Breaktime` | 1200 ms | Pacing after a successful `ProcessAp` call, including zero-cost calls |
| `Movement.RtApCost*` | see above | `CritterActions` per-action costs |

Changing a value here is a balance contract change: consumers above read the
setting directly, and saved critters keep `CurrentHp/KnockoutAp/Timeouts`.

## Extension points

- New weapon behavior belongs in the branch table of `CombatAttack` keyed by
  weapon subtype/proto ids (see `isFlamethrower`/`isRocket` pid checks against
  `Content::Item::*`); damage typing comes from the item proto's
  `Weapon_DmgType_0..2` and other properties read through `WeaponHelpers`.
- New on-hit conditions: the `HF_*`/`MF_*` flag vocabulary in `Scripts/Flags.fos`
  plus the critical tables. Keep table row layout (7 ints per row) intact —
  it is the Fallout 2 layout and `ApplyDamage` indexes it arithmetically.
- Use `Combat::InjureCritter` for scripted damage that should follow the
  armor/critical/knockout pipeline. Existing poison, radiation and drug code
  also writes HP directly; those paths do not establish the same contract.

## Verification

Static source trace only (this document); no runtime session was run for it.
Existing coverage: `Scripts/Tests/Test_CritterActions.fos` (AP/container
actions) and `Scripts/Tests/Test_Combat.fos` (damage operation order, armor
modifiers/clamps and aim tables). These formula tests do not execute the full
attack pipeline; historical audit coverage counts are not current coverage.
For changes, run
`Launch :: TLA_Tests [windows]` (inspect COMPLETE counts) and exercise a real
attack in the client per [BuildAndLaunch](BuildAndLaunch.md#local-runtime-and-tests);
formula changes additionally deserve a focused regression asserting the old
wrong result.
