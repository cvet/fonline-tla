# Character

SPECIAL, traits, skills, perks, derived combat stats, experience and level
progression. Property *declaration* lives in
[Scripts/CritterProps.fos](../Scripts/CritterProps.fos); every derived value
is a **virtual property** whose getter is registered by
`Parameters::InitParameters` (`Scripts/Parameters.fos`) through
`Game.SetPropertyGetter` — reading `cr.MaxLife` (or combat code reading
`cr.DamageResistance[dt]`) always evaluates the formulas below on both
sides. Source baseline: project `a213c7abe`, Engine `28c84c5d9d`;
static review on 2026-10-29.

## Base vs virtual

Each stat exists as a persisted `<Name>Base` property (SPECIAL groups:
`Group = SpecialBase`, saved with the critter) and a virtual `<Name>` that
computes `Base + modifiers`, clamped. Modifiers come from traits, perks
(many perks are pure flags consumed elsewhere — combat, barter, dialogs),
the worn armor (`CurrentArmorPerk`, set on equip — see [Items](Items.md#equipment-slots))
and drug effects (`Drugs::GetDrugEffect` reads the critter's
`DrugEffects` dict property; stages/addictions are server time events in
[Scripts/Drugs.fos](../Scripts/Drugs.fos)).

## SPECIAL getters (`Scripts/Parameters.fos`)

| Stat | Extra modifiers beyond Base + drugs |
| --- | --- |
| Strength | +1 Adrenaline Rush (in battle at ≤ half base HP); +3 Powered armor perk, +4 Advanced I/II; clamp 1..10 |
| Perception | damaged eye replaces the starting base with 1, then Night Person and drugs apply; final value can exceed 1 |
| Endurance / Agility / Luck | drugs only |
| Charisma | +1 with the Charisma armor perk |
| Intellect | Night Person ±1 |

All SPECIAL getters clamp the final result to 1..10. Night Person uses the
game clock, including minutes at the 06:00/18:00 boundaries.

## Derived stats (runtime getters)

| Property | Formula (`Parameters.fos`) |
| --- | --- |
| `MaxLife` | `MaxLifeBase + ST_base + EN_base*2` + drugs, clamp 1..9999 |
| `ActionPoints` | `ActionPointsBase + AG_impl/2` + drugs, clamp 1..9999; stored `CurrentAp` uses hundredths, see [Combat](Combat.md#action-points) |
| `ArmorClass` | `ArmorClassBase + AG_impl` + drugs + worn armor `Armor_AC·(100−wear%)/100`, clamp 0..90 |
| `DamageResistance[type]` | `<type>ResistanceBase` + armor `Armor_DR<type>·(100−wear%)/100`; poison += EN·5, radiation += EN·2; armor perk radiation bonuses (+20..+75); drugs; clamp 0..90 (EMP 0..999) |
| `DamageThreshold[type]` | physical-type base + worn armor `Armor_DT<type>`, then per-type drug effects; poison/radiation start at 0, without the DR getter's EN/radiation-perk additions; clamp 0..999 |
| `CarryWeight` | `max(CarryWeightBase,0)` + drugs + `ConvertGrams(25 + ST_impl·(25 − 10·SmallFrame))`, clamp 0..2000000000; pounds convert at 453 grams |
| `MeleeDamage` | `MeleeDamageBase + (ST_impl > 6 ? ST_impl−5 : 1)` + drugs, clamp 1..9999 |
| `Sequence` | `SequenceBase + PE_impl·2` + drugs, clamp 0..9999 |
| `HealingRate` | `HealingRateBase + max(1, EN_impl/3)` + drugs, clamp 0..9999 |
| `CriticalChance` | `CriticalChanceBase + LK_impl` + drugs, clamp 0..100 |
| `MaxCritical` | `MaxCriticalBase` + drugs, clamp −100..100 |
| `IsOverweight` | `ItemsWeight > CarryWeight` |

Armor contributions scale down with wear (`GetDeteriorationProc`,
`Parameters.fos`) — a worn-out armor protects less; the default
protos (`default_armor`/`default_weapon`, `Items/Custom/`) are fallback
values, not physical slot items. DR/DT armor contributions require an
actual worn `Item`. Poison/radiation *damage* effects are separate systems
(`Poison.fos`, `Radiation.fos`); resistances above feed their checks.

## Character generation — `Parameters::CritterGenerate`

Runs on both sides from registration input (7 SPECIAL, 3 tag slots, up to
2 traits, age, gender). Shared base calculations feed creation, while the
`#if CLIENT` block materializes derived preview values. The server reads
derived getters and `Main::CritterInit` restores full HP/AP; the two result
dictionaries are deliberately not identical. Sequence: trait base
adjustments (Small Frame +1 AG, Bruiser +2 ST/−2 AP, Good Natured ±15/−10
skills, Fast Metabolism resist/heal changes, Kamikaze, Heavy Handed,
Finesse, Fast Shot → `IsNoAim`), then skill bases:

```text
SmallGuns 5+4·AG    BigGuns/Energy 2·AG        Unarmed 30+2·(AG+ST)
Melee 20+2·(AG+ST)  Throwing 4·AG              FirstAid 2·(PE+IN)
Doctor 5+PE+IN      Sneak 5+3·AG               Lockpick 10+PE+AG
Steal 3·AG          Traps 10+PE+AG             Science 4·IN
Repair 3·IN         Speech 5·CH                Barter 4·CH
Gambling 5·LK       Outdoorsman 2·(EN+IN)      +20 per tag skill
```

then client-only derived preview values (a mirror of the runtime getters:
AC += AG, HP += ST+2·EN, AP += AG/2, CarryWeight from pounds→grams
conversion, MeleeDamage, resistances, Sequence, HealingRate, CritChance +=
LK), plus the base increments `MaxLifeBase += 15`, `ActionPointsBase += 5`.
The player budget is 40 SPECIAL points / 3 tag skills
(`Player.StartSpecialPoints`/`StartTagSkillPoints`). SPECIAL budget is checked
server-side; tag membership is checked there, but the tag-count budget is
client-side only
(see [PlayerLifecycle](PlayerLifecycle.md#registration-and-login)).

## Experience and levels

- `CritterSetExperience` (server setter, `Parameters.fos`): at the
  level cap without `LevelCapAddExperience` the gain is discarded;
  otherwise Swift Learner adds `5%·rank`, then the level check runs as a
  time event.
- `UpdateExperienceLevel`: while `Experience ≥ NextLevelNeedExp`
  and below `Player.LevelCap` (666): `Level += 1`; skill points
  `5 + 2·IN_base` (+5 Skilled trait, +2·Educated rank, cap 99); HP growth
  `MaxLifeBase += 2 + EN_base/2 + 4·Lifegiver` only up to
  `Player.MaxLifeLevelSoftCap` (36); a perk slot every 3rd level (4 with
  Skilled).
- `NextLevelNeedExp = NumericalNumber(level)·1000` — the classic triangular
  sequence (level 2 at 1000, 3 at 3000, 4 at 6000, …; `Tla.fos`).
- Skill spending `ProcessSkillsUp` (server RPC, the same module): the skill id is
  validated against `CritterPropertyGroup::Skills` (untrusted input), each
  point costs 1 while skill ≤ 100 (`SkillModAdd2`), then 2..6 points per
  +1 by tier (`SkillModAdd2..6` = 100/125/150/175/200), tag skills get +2
  per spend, everything capped by `Player.SkillMaxValue` (300).
- Perk spending `ProcessPerkUp`: requires an `UnspentPerks` slot
  and `Perks::PerkCheck` — a large per-perk switch of rank/level/base-stat/
  skill requirements with mutual exclusions (Slayer/Sniper/Terminator;
  `Scripts/Perks.fos`). Taking a perk routes through the
  `CritterSetPerks` setter → `Perks::PerkUp`, which applies server-side
  stat/skill modifiers; most combat perks are flags consumed by
  [Combat](Combat.md). Client UX: level-up sound + Character tab marker
  (`CritterSetLevel`, the same module). `CritterSetUnspentPerks` contains an auto-open
  handler but is not registered in `InitParameters`; its existence alone
  does not prove the screen opens on property changes. The actual
  `Gui/Character.fogui` open handler opens Perk when slots are available.

## Drugs (brief)

[Scripts/Drugs.fos](../Scripts/Drugs.fos): `DrugEffects` is a
`CritterProperty=>int32` dict property — drug use starts staged time events
(effect → withdrawal → addiction per the inline table: Jet, Psycho,
Buffout, Mentats, RadAway, NukaCola) writing modifiers into that dict;
withdrawal/addiction stages update the `Addictions` array. Separate legacy
flags such as `IsJetAddicted` still have dialog consumers, but this drug
pipeline does not update them. Jet's exit stage requires the Jet Antidote.

## Verification

`Scripts/Tests/Test_Parameters.fos` currently covers `timed_item_contract`,
not getters or generation parity. A formula change needs focused coverage
on **both sides** (the
generation function duplicates the getter math under `#if CLIENT`) — compile
and run the harness, then verify level-up/skill/perk spending through the
real Character GUI in a client ([BuildAndLaunch](BuildAndLaunch.md#local-runtime-and-tests)).
`PerkCheck` requirements are data-like: changing them is a balance contract
change for saved characters mid-progression.
