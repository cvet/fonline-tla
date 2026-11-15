# Engine lifecycle findings: project fixes

**Goal:** Apply the project side of the 2026-11-14 Engine lifecycle round: drop the
never-fired Engine events the Engine removes, follow the CMake option rename, make
timed status effects survive a restart, close the authority holes found by the
mechanics audit, and report the dead project events and lost deferred calls.

**Requirements:** [Scripts](../Scripts.md), [ScriptStyle](../ScriptStyle.md),
[Systems](../Systems.md), [NativeExtensions](../NativeExtensions.md),
[BuildAndLaunch](../BuildAndLaunch.md). Engine contracts (integration checkout of
the round): `Docs/en/how-to/scripting/lifecycle-and-concurrency.md`,
`Docs/en/how-to/mechanics/timed-effect.md`,
`Docs/en/reference/scripting/remote-calls.md`,
`Docs/en/how-to/project/script-and-binding-checks.md`.

## State and authority

- Branch `fix/forks-audit-20261108`, base commit `7bff4608`. Working-tree edits
  only: no stage, commit, stash or reset.
- Owner's uncommitted work is preserved hunk for hunk: `Engine` (gitlink
  `657bcff4`, 2026.1.117-dev), `Gui/Game.fogui`,
  `Scripts/Generated/GuiScreens.fos`, `Scripts/Main.fos`, `Scripts/MsgStr.fos`,
  `Scripts/Parameters.fos` (this round adds only its two `///@ RemoteCall` limit
  lines) and `SourceExt/ClientAiBridge.cpp` (this round adds the `Common.h`
  first include and the token guard).
- No native build, bake or `cmake` in this round: Engine sources change in
  parallel. Everything below is static; the runtime routes are listed at the end.
- The Engine contracts come from the integration Engine checkout (2026.1.121-dev
  branch). The project gitlink stays at `657bcff4`; every change here compiles
  against both as far as static reading shows, except the migration listed under
  "Pending Engine-update migration".

## A1. Removed Engine events

`Critter.OnTalk`, `Critter.OnBarter`, `Map.OnCheckLook`, `Map.OnCheckTrapLook`,
`Player.OnGetAccess`, `Player.OnAllowCommand` and `Player.OnLogout` were never
fired by the Engine, so every project handler was dead. Nothing in the project
fires them. Removed:

| Module | Removed | Kept |
| --- | --- | --- |
| `BrokenCommon` | `OnBarter` subscription, `GhoulBarter`, `SedUraniumCost`, `URANIUM_DISCOUNT` | `GhoulTraderInit`; `BHUranDiscount` is still set by `bh_super.fodlg` |
| `DenLara` (file deleted) | `LaraInit` (only an `OnBarter` subscription) and `EventBarter`; `InitScript` line in `Maps/den.fomap` | Lara's dialog `den_lara` |
| `DenVirgin` | `OnTalk` subscription and `VirginTalk` | `GoAway` dialog result, `Check` timer |
| `GameEventRacing` | `OnTalk` subscribe/unsubscribe and `SpectatorTalk` | phase logic in `BeginRacing` and `Npc2HomePos` |
| `Hunter` | `OnBarter` subscription, `HoughBarter`, `DestroyItemsHough` | `HoughInit` and the rest |
| `MapGeckCity` | `OnBarter` subscription, `GeckTraderBarter`, `CITIZENS_TRADING_SKILL` | `GeckTraderInit`; property `MapGeckCityTraderSkillBarter` (persisted, now unused) |
| `MapPrimalTribe` | `OnTalk` subscription, `OnDial`, `STR_TALK_TO_SULIK` | everything else |
| `Patrol` | `OnTalk` subscription and `PatrollerTalk` | `PatrolInfo::MovePatrol` callers |
| `VcLynnet` | `OnTalk` subscription in `PrisonerName` and the event handler `PrisonerTalk(Critter, ...)` | the `[[TimeEvent]] PrisonerTalk(any[])` overload |

Same class, also cleaned: the empty `ClientMain` handlers `ItemMapChanged` and
`ItemInvChanged` of Engine events removed earlier (no subscription, no caller).

## A2. CMake options

- `FO_BUILD_EDITOR ON` removed from `SetOptionValues`; `FO_BUILD_MAPPER ON` was
  already present and owns the Mapper, AnimationViewer and ParticleViewer. Every
  other `FO_` name in `CMakeLists.txt` is declared by the integration Engine's
  `BuildTools/cmake/stages/Init.cmake`.
- The project variable `FO_SHA_SOURCE` became `TLA_SHA_SOURCE` (the Engine's
  migration note reserves the `FO_` prefix for Engine options).
- `Docs/BuildAndLaunch.md` packages paragraph updated.

## A3. Timed effects and lost deferred calls

The Engine does not store time events (`lifecycle-and-concurrency.md`, "Time
events after a database reload"); `TimeEventContext.Repeat` makes the event
periodic until `Stop` (`Source/Common/TimeEvents.cpp`, completion handling).

Fixed:

- **Drugs.** `DrugEffects` modifiers were persistent while the stage timers and
  the in-memory registry were not, so a restart left the modifiers forever. Now
  the persistent `Critter.DrugTimeline` (`int64[]`, `DrugTimelineStride` = 4:
  table slot, next stage, trait flags, deadline in `SynchronizedTime`
  milliseconds) is saved on every stage change; `Game.OnCritterInit` with
  `firstTime == false` rebuilds the registry and re-arms behind
  `CountTimeEvent(Drug) == 0`; the final stage calls `Stop`. Before, the last
  `Repeat` kept the event firing and re-applied later stages. A loaded critter
  with modifiers but no timeline (old saves) has them cleared: every table row
  sums to zero over its stages (checked with a script), so a finished course
  leaves no legitimate modifier. The slot order is persisted: append new drugs at
  the end of `DrugTableOrder`. Test: `Scripts/Tests/Test_Drugs.fos` (3 cases).
- **Radiation.** `RadiationStage` and `RadiationDue` persist the event data and
  deadline; re-armed the same way; final processing calls `Stop`. Also fixed the
  port of the original `ChangeTimeEvent(index, 0, stage)`: a dose that changes the
  stage now fires the event at once (`RepeatTimeEvent(Radiation, ZERO_TIMESPAN)`)
  with the old stage in its data. The previous `SetTimeEventData(newStage)` made
  the next firing remove the new stage's penalties (never applied) and left the
  old stage's penalties in base stats permanently.
- **Poison.** `PoisoningLevel` is persistent; `OnCritterInit` re-arms the tick
  from the full duration of the current level; recovery calls `Stop` (before, the
  "free of poison" message repeated every interval forever).

Classification of the 140 `SavedDeferredCall` markers
(inventory script and table in the task workspace, `saved_deferred.py`):

- **Survive a restart through a project path (2):** `KlamCowboy::InitCowboy`
  (map init re-arms the daily `StartAtack` unconditionally) and
  `VcGuardsman::MutantsOutGroundInit` (map init re-arms `DeleteQuestLocation`
  unconditionally; the 3-day deadline restarts on every load).
- **Lost, but only seconds or minutes of presentation (about 30):** `MainIntro`
  effects, `RatGrenade`, `Hunter::MoveRat`, `KlamDantonBrahmin::Follow`,
  `ReddingCommon::Broadcast`, `VcLynnet::Answer`, `Geiger`, explosions in
  `Explode`, `SeAndroid`, `GameEventReplicator`, `SmokeGrenade`, `HubLab`,
  `MapPrimalTribe` `Asap` calls, `KlamCowboy::SpawnMobs`.
- **Lost and leaving persistent state (owner decision, see below):**
  - world-state resets that never happen: `Item::AutoCloseDoor` (doors and
    `ElectronicLock` stay open), `ReddGates::CloseGates`,
    `EnergyBarier::TurnOnBarier(s)` (barrier stays off), `MapGeckCity` door,
    `CompRiddle::ResetRiddle`, `Elevator::ResetData`,
    `HostileLocationQuest::ResetHostileLoc`, `VcGuardsman::ResetCommander`,
    `Resources::AddResourcesCount`, `NcrCommon::TimeToHideMoney`;
  - deferred deletions that never happen (database growth, duplicate actors):
    `Item::DeferredDestroyItem`, `GameEventCaches`, `Location::SetLocationDeleteTime`
    (4 callers) and `GameEventStorehouse`, `Base::DeleteCar`,
    `Caravan::DeleteLeader` (the code itself warns of two leaders),
    `GameEventReplicator::DeleteSandbags`, `NcrInvasion::DeleteDeadRaider`,
    `SfInvasion::DeferredDestroyCritter`, `Purgatory::DeletePurgatory`,
    `NrWriKidnap::DeleteQuestLocation`, `Navarro::DeleteScaner`,
    `PatternTerm::DeleteFlare`, `SignalRocket::HideLocation`,
    `KlamCowboy::DeleteMobs`, `SeAndroid::DefferedDestroyItem`;
  - respawns that never happen: `Explode::RespawnTimerMine`, `Trap::RespawnTrap`,
    `RespawnItem::ProcessRespawnItem`, `KlamCowboy::CowToAlive`,
    `V13Goris` deathclaw rebirth;
  - quest timeouts and contracts that never end: `ArroyoMynocDefence::TimeExpired`,
    `Merc::ReleaseMerc`, `SfCommon::DoCancelContract`, `SeAndroid::AwakePlayer`;
  - repeating world chains that stop after the first restart, because their start
    is `if (firstTime)` or guarded by a persisted `*InvokeId` that stays non-zero:
    `NcrInvasion`, `NcrSiege` (declared only on the first `MapNcrDowntown` init),
    `SfInvasion` (first `TankerMapInit` only), `TownSupply`, `MobWave`,
    `Purgatory` radio, `NcrDusty`, `SfCommon::OneWeek`, `NcrWestin`
    evening/morning, `NcrCommon` beggar and brahmin illness, `Base::BaseRefresh`,
    `NrWriKidnap::Kidnap` (`OliverInit` checks `QNrWriKidnapInvokeId == 0`),
    `GameEvent::ProcessGameEvent`.

Decision: only the stat-changing player effects (drugs, radiation, poison) are
fixed in this round. Every other leaked case needs a per-feature deadline
property and an init re-arm, plus a restart test against a persistent database;
that is a design task for the owner (one shared durable-timer helper would serve
all of them).

## A4. Authority

- **Equipment slots.** The server RemoteCall `ChosenActions::MoveInvItem` now runs
  `CritterActions::IsInvItemMoveAllowed`, which fires the same
  `Game.OnCritterCheckMoveItem` the client checks, and rejects a forged move with
  an exception like the adjacent `CritterActions` checks. NPC AI keeps calling
  `CritterActions::MoveInvItem` directly. Test:
  `critter_actions.inv_item_move_slot_rule`. Docs: `Items.md`. Engine note, from
  reading only: a script exception or a rejected payload reaches
  `exceptions::report_and_continue`, whose headless callback requests quit, so a
  throwing RemoteCall check may let a forged call stop `TLA_ServerHeadless`;
  reported to the Engine round, unverified at runtime.
- **Unchecked RemoteCalls.** `Test::CreateLocationSelf` and `Test::GetPropValue`
  now return unless `AiControl.AllowQaCommands`, like the `AiControl` QA calls.
  The other 46 server handlers resolve `player.GetControlledCritter()` or are
  registration, ping and map-preview calls. `ConsoleCommands.AllowEveryone = True`
  stays (owner decision); `ConsoleCommands.md` now states what it exposes.
- **Registration.** The server repeated only the SPECIAL and tag-skill validity
  checks of the registration window. `AreStartTagSkillsValid` now rejects
  duplicate tags (each copy gave +20) and more than `Player.StartTagSkillPoints`
  tags; `AreStartTraitsAndLooksValid` rejects more than two traits, an age outside
  `Tla::AgeMin..AgeMax` and a gender other than male or female. The automated
  `AiControl` registration (no tags, no traits, age 25, male) still passes. Test:
  `player_registration.start_choices_validation`.
- **Remote-call limits.** All 41 server calls with arguments declare `MaxBytes`
  (exact for fixed arguments) and `MaxCollectionSize` for collections; the 7
  argument-less calls need none because the validator requires complete payload
  consumption. Wire sizes come from `Source/Server/ClientDataValidation.cpp` and
  the metadata types: `hstring` 8 (64-bit hash), `ident` 8, `mpos` 4 (16-bit
  coordinates while `FO_MAP_WIDE_COORDS` is off), `CritterProperty`/`GameProperty`
  2, `CritterItemSlot` and project enums 1, `string`/`any` 4 + UTF-8 bytes with up
  to 4 bytes per character because `string.length()` counts characters. String
  caps: console 512 characters (2052), say reply 100 characters (412/413), names 12
  characters from `Parameters::CheckPlayerName` (52; registration 248 with at most
  32 properties), `any` ids up to 20 digits (global map 52, `GetPropValue` 28).
  Free chat and radio have no cap in the client input or the handler: 4096 bytes
  of text (4101/4100). Barter lists cap at `MaxBarterOfferItems` = 512 (12308).
  Skill spending: 18 pairs (436, 36 elements). The rule is in `ScriptStyle.md`.
- **AiControl bridge.** `Client_Game_AiControlStart` throws for a non-loopback
  `AiControl.Host` with an empty token, matching the Engine listener rule. The
  bind uses `make_address` without name resolution, so an unparsable host still
  fails at bind. The owner's diff does not move to the Engine listener; that
  migration is out of scope. `AiControl.md` updated.

## A5. Project events without a producer

Script: `dead_events.py` (task workspace). It matches `///@ Event` declarations to
`.Name.Fire(` sites by scope (`Game` versus an entity receiver); `git log -S` gave
the history. All these events came from the 2022-05-30 "Engine sync" (`aee673b0`),
which moved Engine-fired events into project declarations without adding
producers; only the `NpcPlaneRun` and item-skill events ever had a script `Fire`.

Removed (no subscriber, no producer): `Critter.OnUseItem`, `Critter.OnUseItemOn`,
`Critter.OnUseSkill`, `Game.OnCritterSneak`, `Map.OnLoopEx1..4`,
`Game.OnCritterPickItem`, `Game.OnCritterPickScenery`, and `Game.OnContainerChanged`
with its empty `ClientMain` handler.

Remaining dead events with subscribers (owner decision; nothing changed):

| Event | Subscribers | Nearest producer | Recommendation |
| --- | --- | --- | --- |
| `Item.OnCritterUseSkill` | 33 (locks, traps, barriers, graves, …) | `Main::CritterUseSkill` handles a few item kinds itself | Wire `targetItem.OnCritterUseSkill.Fire` in the dispatcher; owner must confirm polarity per item |
| `Critter.OnAttacked` | 30 | `Main::CritterAttacked` (fired by `Combat`) | Fire `cr.OnAttacked` there; decide whether `StopChain` suppresses the default retaliation |
| `Item.OnCritterUse` / `OnCritterUseOn` / `OnCritterUseOnSelf` | 14 / 9 / 7 | `Main::CritterUseItem` | Fire item-scope events from the dispatcher; gameplay review per item |
| `Critter.OnAttack` | 9 | `Combat::CombatAttack` | Fire with `Game.OnCritterAttack`; owner |
| `Critter.OnRespawn` | 7 | `CritterState` line with `Game.OnCritterRespawn.Fire` | Mechanical one-line producer; not applied without a runtime check |
| `Critter.OnSomeUseItemOnMe` / `OnSomeUseSkillOnMe` / `OnUseSkillOn` | 4 / 1 / 3 | use-item and use-skill dispatchers | Owner |
| `Critter.OnNpcPlaneRun` | 3 (Slayer, Terminator patterns, test tracer) | `NpcPlanes` fires `Game.OnNpcPlaneRun`; `OnNpcPlaneBegin` already fires both scopes with the same polarity | Mirror the `OnNpcPlaneBegin` pair; changes NPC AI, so not applied |
| `Game.OnCritterAttack` | 1 (`Main::CritterAttack`) | `CritterActions::Attack` calls `Combat::CombatAttack` directly | Owner: fire it or delete the dead flow (`TimeoutAggressor`, EMP rocket test) |
| `Game.OnCritterReloadWeapon` | 1 (`Main::CritterReloadWeapon`, solar scorcher) | `CritterActions::ReloadWeapon` | Owner |
| `Item.OnCritterAttack` | 1 (`RatGrenade`) | `Combat` | Owner |
| `Game.OnItemsCollection` (client) | 1 (`ClientMain`) | none in the Engine any more | Owner: remove or replace with the current client item API |

## A6. Smaller items

- The native `Critter.Wait/IsBusy/IsFree` exports in `ClientExtension.cpp` and
  `ServerExtension.cpp` were no-op stubs with no consumer anywhere (scripts use
  `CritterState::Wait/IsBusy/IsFree` and `ChosenActions::IsBusy/IsFree`); removed.
- `SourceExt` include layout fixed in six files; the Engine
  `check_native_source_layout.py --root . --source-dir SourceExt --shallow` now
  runs in the CI `validate` job and in `Analyze :: Native Source Layout`, part of
  `Verify :: All`.
- Mutable-global rule: the touched allowlisted namespaces (`Drugs`, `Testing`,
  `GameEventRacing`, `MapPrimalTribe`, `Patrol`, `VcLynnet`) got a header line on
  their global lifetime; the other touched allowlisted modules already had one.

## Owner decisions

1. The dead event wiring in the A5 table, in particular `Item.OnCritterUseSkill`
   (33 subscribers) and `Critter.OnAttacked` (30).
2. Durable timers for the leaked `SavedDeferredCall` groups in A3.
3. Gameplay lost with the removed handlers (dead before this change): the Broken
   Hills uranium discount (`BHUranDiscount` is still granted), Lara's loyalty
   gate on barter, the Hough flute and toxin offers, the Gecko citizen barter
   skill, Sulik's remark, patrol resumption after talks, the racing spectator
   dialog, Den virgin leaving after the talk and the Lynette arrest dialog
   substitution (`vc_telman`), without which the arrest branch probably cannot
   start. Restoring any of them needs a project dialog/barter hook.
4. The unused persistent property `MapGeckCityTraderSkillBarter` (remove with a
   migration rule or keep).
5. A client-side length cap for chat and radio input: a longer line exceeds the
   4096-byte RemoteCall limit and is rejected as invalid data.

## Pending Engine-update migration (blocked by the pin)

The integration Engine renamed `OnCritterAnimationInit` to
`OnCritterAnimationPlaybackInit` (with `normalizedPosition`), `Game.SetSpriteTime`
to `SetSpritePhase` and `Item.SetAnimTime` to `SetAnimPhase` (Engine changelog,
2026.1.98-dev feature branch, merged in `9af8dc5ff4`). The project uses the old
names in `Animation.fos`, `CritterPresentation.fos`, `Core/Sprite.fos` and
`FixedItemFrame.fos`. The current gitlink `657bcff4` lacks the new names, so the
rename belongs to the Engine update that moves the gitlink.

## Verification (2026-11-14, static only)

- `check_native_source_layout.py --root . --source-dir SourceExt --shallow`
  (project Engine and integration Engine tools): exit 0; 7 findings before.
- Integration Engine `check_script_bindings.py --root . --scope Engine/Source
  --scope SourceExt --scripts Scripts --exclude 'SourceExt/SHA/*'`: exit 1 with 65
  `event-handler-nullability` findings, the same set as an export of `HEAD`
  (project event declarations without `?` where handlers accept null).
- Integration Engine `check_angelscript_hygiene.py --root . --scripts Scripts`:
  exit 1, one finding (`ColorExt.fos` namespace, the documented exception), same
  as `HEAD`.
- `Tools/NullableEstimate/test_validate_nullable.py`, `validate_nullable.py`,
  `apply_nullables.py --check`: exit 0.
- `Tools/ScriptQuality/validate_scripts.py --ratchet`: exit 0.
- `py -3 -m pytest Tools -q`: 220 passed, 89 subtests passed, exit 0.
- `Tools/Formatter/format_project.py scripts --check` (bundled clang-format 20):
  three edited files formatted, then the full check changed 0 files, exit 0.
- `Tools/DocsCheck/check_docs.py`: four broken links, all pre-existing in
  `2026-11-08-forks-audit.md`.
- `git diff --check`: clean.

Not run (no build or bake in this round): compile and bake
(`cmake --preset auto`, `Bake Resources`, `Build :: TLA_ServerHeadless`,
`Build :: TLA_Client`, `Build :: TLA_Mapper`, `Build :: TLA_UnitTests`), the
script harness (`Launch :: TLA_Tests [windows]` with `Testing.Filter` set to
`drugs`, `critter_actions`, `player_registration`), native tests
(`Launch :: TLA_UnitTests [windows]`), `Verify :: All`, a restart against a
persistent database for the drug, radiation and poison restore, and a player
smoke of equipping, registration, chat, console and say input with Cyrillic text.
