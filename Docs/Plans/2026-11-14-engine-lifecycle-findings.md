# Engine lifecycle findings: project fixes

**Goal:** Apply the project side of the 2026-11-14 Engine lifecycle round: drop the
never-fired Engine events the Engine removes, follow the CMake option rename, make
timed status effects survive a restart, close the authority holes found by the
mechanics audit, report the dead project events and lost deferred calls, and carry
the project to the integration Engine (2026.1.123-dev) with the migration below.

**Requirements:** [Scripts](../Scripts.md), [ScriptStyle](../ScriptStyle.md),
[Systems](../Systems.md), [NativeExtensions](../NativeExtensions.md),
[BuildAndLaunch](../BuildAndLaunch.md). Engine contracts (integration checkout of
the round): `Docs/en/how-to/scripting/lifecycle-and-concurrency.md`,
`Docs/en/how-to/mechanics/timed-effect.md`,
`Docs/en/reference/scripting/remote-calls.md`,
`Docs/en/how-to/project/script-and-binding-checks.md`.

## State and authority

- Branch `fix/forks-audit-20261108`. The first round of this plan (A1-A5 and the
  owner's seven working-tree files) was committed and published by the owner as
  `2646c933` (branch equal to `origin/fix/forks-audit-20261108`); that commit also
  moved the Engine gitlink `f5a37d9fc9` to `ef89118d2e`. The second round (this
  update: Engine migration, tooling, decisions) is committed locally on top of it,
  never pushed. `origin/master` moved (`2fce2ba8`, three commits: Engine pin
  `7d134df5f8` = 2026.1.118-dev, GUI tip guards, version 0.3.24); it is merged into
  the branch (see "Branch integration").
- No native build, bake or `cmake` in either round: Engine sources change in
  parallel. Everything below is static; the runtime routes are listed at the end.
- The Engine contracts come from the integration Engine checkout (branch
  `lifecycle-docs-and-tooling`, 2026.1.123-dev). The recorded pin of this branch
  stays at `ef89118d2e`; the coordinator moves the gitlink to `<ENGINE_HEAD>`.

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

Decision (2026-11-15): only the stat-changing player effects (drugs, radiation,
poison) are fixed. The lost-timer chains above (`NcrSiege`, `SfInvasion`,
`NcrInvasion`, `NrWriKidnap`, the deferred deletes, respawns and auto-close calls)
are left as they are: the Engine is adding persistent time events (documented in
`Engine/Docs/en/how-to/scripting/lifecycle-and-concurrency.md` when it lands), and
the durable-timer migration of these call sites follows that API instead of a
per-feature deadline property now. Engine facts that changed meanwhile: snapshot
time events are restored before the init events, so a `CountTimeEvent(...) == 0`
guard sees them (this round's Drugs/Radiation/Poison re-arm needs no change), and
`Entity.EnsureTimeEvent` / `Game.EnsureTimeEvent` replace that guard in one call
(optional).

## A4. Authority

- **Equipment slots.** The server RemoteCall `ChosenActions::MoveInvItem` now runs
  `CritterActions::IsInvItemMoveAllowed`, which fires the same
  `Game.OnCritterCheckMoveItem` the client checks, and rejects a forged move with
  an exception like the adjacent `CritterActions` checks. NPC AI keeps calling
  `CritterActions::MoveInvItem` directly. Test:
  `critter_actions.inv_item_move_slot_rule`. Docs: `Items.md`. The headless-server
  concern recorded earlier (a throwing check or a rejected payload reaching
  `report_and_continue`) is fixed in the Engine 2026.1.123-dev: an unknown call, an
  oversized or invalid payload and every other forged message disconnect only the
  sender, and a script exception in a server RemoteCall handler is logged as
  `Remote call .* handler failed` instead of being reported (unverified at runtime
  here).
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
  Free chat and radio allow 4096 bytes of text (4101/4100); the client now stops a
  longer line itself (`Messaging::MaxChatTextLength` = 1024 characters, at most 4
  bytes each, checked in `Messaging::SendSay` before the prefixes are parsed),
  because an oversized call now disconnects the sender. Barter lists cap at `MaxBarterOfferItems` = 512 (12308).
  Skill spending: 18 pairs (436, 36 elements). The rule is in `ScriptStyle.md`.
- **AiControl bridge.** Superseded by the Engine listener, see "Engine update:
  project migration" (the project listener is deleted, so its token guard is the
  Engine's rule).

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

Decision (2026-11-15): wiring a producer for any remaining event changes gameplay
and needs a playtest, so no `Fire` site is added: the declarations and the
subscribers stay, and each event below is an owner follow-up with its evidence
(subscriber count from `dead_events.py`, rerun 2026-11-15 on the current tree:
64 declared, 15 without a `Fire`, all 15 with subscribers; no event is left with
neither a subscriber nor a producer, and every Engine event the project subscribes
to is declared by the integration Engine).

Remaining dead events with subscribers (nothing changed):

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
  `check_native_source_layout.py --root . --source-dir SourceExt --shallow
  --comments` now runs in the CI `validate` job and in `Analyze :: Native Source
  Layout`, part of `Verify :: All` (the comment rules found four findings in
  `ClientExtension.cpp` and `Dialogs.h`, fixed).
- Mutable-global rule: the touched allowlisted namespaces (`Drugs`, `Testing`,
  `GameEventRacing`, `MapPrimalTribe`, `Patrol`, `VcLynnet`) got a header line on
  their global lifetime; the other touched allowlisted modules already had one.
- The persistent Critter property `MapGeckCityTraderSkillBarter` is removed
  together with `GeckTraderBarter` (its only reader and writer). An unused
  persisted property needs a tombstone, so `Scripts/Migration.fos` has
  `MigrationRule Property Critter Remove MapGeckCityTraderSkillBarter`; old saves
  drop the stored value on load.
- Free chat and radio input is capped on the client, see A4.

## Decisions taken (2026-11-15) and owner follow-ups

Taken (no owner input needed):

1. Dead events: keep every declaration and subscriber, wire nothing (A5).
2. Lost-timer chains: leave the code; migrate to the Engine persistent time events
   when that API ships (A3).
3. Removed dead gameplay stays removed (list below).
4. `MapGeckCityTraderSkillBarter`: removed with a migration rule (A6).
5. Chat and radio input cap: added on the client (A4).

Owner follow-ups:

- Wiring of the 15 dead events in the A5 table, in particular `Item.OnCritterUseSkill`
  (33 subscribers) and `Critter.OnAttacked` (30), each with a playtest.
- Durable timers for the lost-timer groups of A3 once the Engine API exists.
- Reinstating any of the gameplay below needs a project dialog or barter hook that
  fires from the code owning the action (the Engine has no dialog runtime hooks any
  more; a project that wants one declares its own `///@ Event` and fires it).
  None of these ever ran in this project (the Engine never fired the events), so
  nothing regressed:
  - `BrokenCommon`: Broken Hills ghoul trader, 25 percent discount on
    `refined_ore` for a player with `BHUranDiscount == 1` (granted by
    `bh_super.fodlg`), applied at barter start and removed at barter end (a hook
    with begin/end and a barter counter below 2).
  - `DenLara`: barter only when `Lara.Loyality[player.Id] >= 5` (hook with a
    veto at barter start). The module and the `Maps/den.fomap` `InitScript` line
    are deleted; her dialog `den_lara` is unchanged.
  - `Hunter` (Hough): at barter start, once per 12-28 game hours minus Luck, add
    `lourence_flute`, `danton_poison` (when the player knows the recipe) and
    `supertoxine` to Hough's stock, destroy the added items 10 game minutes later
    if the player did not take them, and destroy the player's `bottle_caps` stock
    at barter end (`ModHoughRatsFluteTimeout`, `ModLourenceToxinTimeout`,
    `ModLourenceFloater`, `ModLourenceToxinRecipe` stay as properties).
  - `MapGeckCity`: Gecko citizens (`IsPlayerCitizen`) trade with `SkillBarter` 10
    (`CITIZENS_TRADING_SKILL`), restored at barter end.
  - `VcLynnet`: Lynette's arrested prisoner opens dialog `vc_telman` once per
    prisoner (`NpcStory` marker) when the player talks to him
    (`VCLynettPrisonerId`), and sets `MercCancelOnGlobal`; without that
    substitution the arrest branch probably cannot start (hook needed at dialog
    start, with a way to replace the dialog).
  - Smaller talk reactions: Sulik's remark `STR_TALK_TO_SULIK` from the other Primal
    Tribe citizens after the raid succeeds (`MapPrimalTribe`), patrol resuming after
    the patrollers finish talking (`Patrol`), the racing spectator dialog
    `den_spectator` once per spectator (`GameEventRacing`), and the Den virgin
    walking to `AWAY_X/AWAY_Y` after the talk (`DenVirgin`, the `GoAway` dialog
    result still sets the flag but nothing starts the walk).

## Engine update: project migration

Done in this round against the integration Engine (every item verified by reading
the Engine source or contract and the project source; nothing compiled):

- `Game.OnCritterAnimationInit` became `Game.OnCritterAnimationPlaybackInit` (last
  `float&` is `normalizedPosition`): `Animation.fos`, `CritterPresentation.fos`
  (Mapper), the `SelectPlayback` signature and its test, `Docs/Animation.md`. Also
  `OnCritterAnimationProcess` takes `AbstractItem? contextItem`.
- `Game.SetSpriteTime` to `Game.SetSpritePhase` (`Core/Sprite.fos`) and
  `Item.SetAnimTime` to `Item.SetAnimPhase` (`FixedItemFrame.fos`, `Lockers.fos`).
  The arguments were already normalized zero to one values.
- The project AiControl listener is replaced by the Engine `AiControlListener`:
  `SourceExt/ClientAiBridge.cpp` and its asio include are deleted (the unused
  `Client_Game_AiControlGetEntityId` export goes with it), `ClientExtData` loses
  the listener state, `CMakeLists.txt` gets the project option `TLA_AI_CONTROL`
  (default `ON`; release and store builds pass `OFF`) feeding `FO_AI_CONTROL`.
  `Scripts/AiControl.fos`: `Game.AiControlStart` has no `enabled` argument and
  throws instead of returning false; `Game.AiControlPullCommand` has no
  `sceneryProtoId` and gains `paramsJson`, from which `ReadParamsString` reads
  `sceneryProtoId` for `use_skill` (the wire field is unchanged for the MCP
  adapter). Static contract test in `Tools/AiControlMcp` updated. Docs:
  `AiControl.md`, `AiControlProtocol.md`, `NativeExtensions.md`. Not done: moving
  the Python adapter in `Tools/AiControlMcp` onto Engine `BuildTools/ai_control_mcp`
  (a larger owner decision); the Engine reference client now requires a token for
  a non-loopback endpoint, and the project adapter was not re-checked against that rule.
- The project `Game.LoadImage(slot, name)` / `Game.GetImageColor(slot, pos)` exports
  are deleted (`ServerExtension.cpp`, including its `SpriteResource.h` include);
  `Worldmap.fos` keeps the `ServerImage` returned by the Engine `Game.LoadImage` in
  `Worldmap::ReliefImage` (`LoadReliefImage`, also called from `GlobalmapGroup`
  module init as before), `GetGlobalMapRelief` reads `ReliefImage.GetColor`.
  `Tla::ImageRelief` is deleted. The Engine rejects images with several directions
  or frames, which `relief_tla.png` is not expected to have; the existing
  `worldmap.relief_image_full_size` test proves it on the next script run.
- `CMakeLists.txt`: the Applications stage now copies `TLA_BakerLib` next to the
  Client, Server, ServerService and ServerHeadless executables, and a repeated
  `CopyTargetRuntimeToTarget` for the same pair aborts configure, so the project
  copies for those four are removed; the Mapper and ASCompiler copies stay.
  `FO_BUILD_EDITOR` and the `FO_` prefix of project variables were handled in the
  first round; every remaining `FO_` name in `CMakeLists.txt` is declared by the
  Engine.
- CI `prepare-workspace.sh`: `linux`, `packages` and the target words are no longer
  feature names; the Android and Web matrix legs now pass `android-arm32`,
  `android-arm64` and `web`, and all legs drop the `${{matrix.app}}` word.
- Script-binding checks: the Engine `check_script_bindings.py` found 65 event-handler
  nullability mismatches, the 65 previously recorded as pre-existing. They are real
  (a declaration without `?` while a handler accepts null, or the reverse): the
  `OnCritterActionEx`, `OnCritterUseItemOn`, `OnCritterUseSkill`,
  `OnCritterReloadWeapon`, `OnCritterAttack` and `OnNpcPlaneEnd` declarations and
  the `OnItemOnMapAppeared` and `OnCritterAnimationProcess` handlers were corrected,
  which fixed 10; the other 55 are baselined with a reason in
  `Tools/ScriptQuality/script_bindings_baseline.tsv` (each needs the handlers of
  that event reviewed before its declaration becomes nullable: `Critter.OnDead`
  and `Game/Map/Critter.OnCritterDead/OnSomeCritterDead` killer, `OnSomeCritterUseItem`,
  `OnSomeCritterUseSkill`, `OnCritterUseOn`, `OnCritterUseOnSelf`, `OnUseSkillOn`,
  `OnSomeCritterDropItem`). The AngelScript compiler ignores `?` when it matches a
  handler, so none of this changed behavior. `check_angelscript_hygiene.py` reports
  only `ColorExt.fos`, recorded as an exception in `angelscript_hygiene.json`.
  `Tools/ScriptQuality/check_engine_scripts.py` runs both with the project scopes
  (task `Analyze :: Engine Script Checks`, part of `Verify :: All`, and a `validate`
  CI step).
- Engine native source audits (`native_source_audit.py allocator` and
  `smart-pointer` over `SourceExt`) report 1 and 31 findings, all in code older
  than this round (`std::to_string` in `Dialogs.cpp`, raw wrapper unwraps and
  `refcount` assignments in `ServerExtension.cpp`, `Dialogs.cpp`, `ClientExtension`,
  `CommonExtension.cpp`). They are not wired into CI: baselining or fixing them
  needs a compile, which this round does not run (owner follow-up; the Engine page
  is `Docs/en/how-to/project/native-source-audits.md`).

Checked and needing nothing: no use of `GetMovingUid`, `Map.RemovedStaticItemIds`,
`Player.HasPlayerMovementControl`, the removed Engine events, `Script.*` setting
names, `RecursiveInput`, `GlobalDayColor*`, `OnPlayerMovementAuthority` (TLA has no
indirect movement control), or a `ref` value setter on an Engine property: the
property setters with a `&` value (`Experience`, `Level`, `HandsProtoItemId`,
`HandsItemMode`, `Perks`, `Opened`) are on project-declared properties, which keep
transforming setters; `Condition`, `Contour`, `CritterSlot`, `KnownLocations`,
`InSneakMode` and `IsTraitFastShot` handlers take no value. `Item.ContainerStack`
is read-only now and merges nothing; the project only reads it and merges in
`ItemStacks`. `$TARGET_FILE{/var/tla/TLA_CHANNEL_SECRET_KEY}` is absolute, so the
relative-path rule does not apply. `MapSpriteHolder` (Mapper) gains
`DepthOffset`, default zero. The `Version` migration marker moves `0.0.88` to
`0.0.90`: rebuild and rebake every role together, no saved-data conversion.

### Reconciliation record

| Item | Value |
| --- | --- |
| Project repository | `fix/forks-audit-20261108`, HEAD before this round `2646c933` (published); `origin/master` `2fce2ba8` merged, see below |
| Old Engine (gitlink at HEAD) | `ef89118d2e8777c51d6adec277498821d5833a03`, `2026.1.117-dev`, Engine branch `fix/forks-audit-20261108` (the pin before the owner's commit was `f5a37d9fc9`; the first round of this plan worked against `657bcff4c2`, a commit of the same branch) |
| New Engine | `<ENGINE_HEAD>` (verified against `d99b9b5193dc012091744eb7bdfc7a71e09fd654`, `2026.1.123-dev`, branch `lifecycle-docs-and-tooling`) |
| Common ancestor | `c5101d149a7f0d9b37df34ce59c8c661f9aa8841`, `2026.1.116-dev` |
| Ancestry | the old pin is NOT an ancestor of the new one (`engine_upgrade_report.py` reports a different history line) |
| Incoming range | 141 commits `c5101d149a..d99b9b5193`, 786 files (Source 152, BuildTools 240, Docs 278, Examples 109), master steps 2026.1.117-dev to 2026.1.123-dev |
| Safety refs | none created; the old pin stays reachable as `origin/fix/forks-audit-20261108` of the Engine repository, and the project commit `2646c933` is published |

Audit done: the whole `Current - 2026-11-15` block (2026.1.123-dev) and the blocks
`2026.1.122-dev`, `2026.1.121-dev`, `2026.1.120-dev` (with its retained feature-branch
records 2026.1.97-dev to 2026.1.101-dev), `2026.1.119-dev`, `2026.1.118-dev` and the
master `2026.1.117-dev` Changed, Removed, Fixed and Migration sections; the
generated contract model of the old and the new pin compared symbol by symbol
(`api.json`: 11 removed, 50 added, no signature change except the `Version` rule,
`0.0.88` to `0.0.90`; the other models change only by the new `FO_AI_CONTROL` CMake
option, two documented CMake helpers, a model-format rule and the loadable client
startup hook entry); the migration search commands of each entry were run against
`Scripts`, `SourceExt`, `CMakeLists.txt`, `TLA.fomain`, `.github` and `.vscode`. The
project-relevant incoming changes and their disposition: renames, removals and the
AiControl and `LoadImage` replacement (above); the forged-message and remote-call
hardening (the project limits stay valid, an oversized call now disconnects the
sender); `Game.UnloadCritter` keeping NPC records (the project does not unload NPCs
to delete them: `git grep UnloadCritter` is empty); `Player.SetName` persisting the
name and the new-record `_Name` key (the project writes no `_Name`); snapshot time
events restored before init events (A3); the relative `$TARGET_FILE` rule (absolute
here); `ClientStartupSettingsHook` running in the loadable client runtime (the
project defines none); Python 3.12 floor for BuildTools (CI runners already provide
it); and `Game.MoveItem` refusing before detaching (no project code repairs an
orphaned item).

Fork-audit Engine commits that the new pin does NOT contain (21 commits,
`git log d99b9b5193..ef89118d2e` of the Engine): the SDL_GPU texture-upload ring
(`0d0c6e6a99`, `27c50e1f58`, `5d7fe24264`, `f5a37d9fc9`, `ef89118d2e`), mouse
coordinates scaled by the window pixel density (`220cd635d0`), authoritative
equipment slots applied before the client view refresh (`fa313ab4b0`), database
recovery log cleanup (`160067e7f5`), the lazy `ConfigBaker` output and written-spelling
tracking of the baker (`3cdf83e726`, `5409935446`), the compile fix for 3D-off
builds (`38315f51b6`) and the refreshed examples (`0ad16ad176`), with their tests
and the version bump (`fe3d6eb676`); the occupied-hex rejection, occluder fade and
visual item movement were added and dropped again inside the same branch
(`96dc621b82`, `d8b488df97`, `877f910802`, `4842c17404`, `300b768790`,
`ddc89d58b3`). The net Engine source effect against the common ancestor is 12 files
(`Client.cpp`, `Application.cpp`, `Rendering-SDLGpu.cpp`, `DataBase.cpp`, `Baker.cpp`,
`ConfigBaker.cpp` and tests). A bare move of the gitlink to the integration Engine
drops these project-visible fixes (equipment display, 2x-display mouse input, SDL_GPU
uploads, recovery cleanup) unless they are merged into the integration Engine
first: this is the coordinator's decision before the gitlink moves, and the reason
this branch's Engine pin is left unchanged here.

Verification of the migration is static only (below). Before the pin moves and the
branch is used: reconfigure, rebuild all roles, force a rebake of metadata and
scripts together, run `TLA_UnitTests`, the script harness, and one ordinary client
session (registration, equipment, world map walk, combat).

### Branch integration

`origin/master` (`2fce2ba8`: Engine pin `7d134df5f8`, `Gui/Character.fogui` and
`Gui/Registration.fogui` tip guards with the regenerated `GuiScreens.fos`, version
0.3.24, two plans) is merged into this branch. Conflicts were the Engine gitlink
(kept at the branch's own `ef89118d2e`, so the merge does not pick the older 2026.1.118
pin; the coordinator moves it) and `VERSION`, which was regenerated with
`Tools/GenerateVersion` (0.3.24 to 0.3.25) instead of being hand-edited.
`GuiScreens.fos` merged without a conflict and was checked by running
`generate_gui_screens.py` and `format_project.py scripts` over the merged tree:
the result is byte-identical to the merged file.

## Verification (2026-11-15, static only)

- `check_native_source_layout.py --root . --source-dir SourceExt --shallow
  --comments` (integration Engine tool): exit 0, 0 findings.
- Integration Engine `check_script_bindings.py` with the project scopes and
  `script_bindings_baseline.tsv`: exit 0 (55 findings, 0 above the baseline);
  `check_angelscript_hygiene.py --config angelscript_hygiene.json`: exit 0;
  `Tools/ScriptQuality/check_engine_scripts.py` against the integration Engine: exit 0.
- `Tools/NullableEstimate/test_validate_nullable.py`, `validate_nullable.py`,
  `apply_nullables.py --check`: exit 0.
- `Tools/ScriptQuality/validate_scripts.py --ratchet`: exit 0.
- `py -3 -m pytest Tools -q`: 220 passed, 89 subtests passed, exit 0.
- `Tools/Formatter/format_project.py scripts --check`: exit 0, 0 files changed.
- `Tools/DocsCheck/check_docs.py`: exit 0, 0 findings (the four broken links of
  `2026-11-08-forks-audit.md` were repaired).
- `git diff --check`: clean.

Not run (no build or bake): compile and bake (`cmake --preset auto`, `Bake
Resources`, `Build :: TLA_ServerHeadless`, `Build :: TLA_Client`,
`Build :: TLA_Mapper`, `Build :: TLA_UnitTests`), the script harness
(`Launch :: TLA_Tests [windows]`, filters `drugs`, `critter_actions`,
`player_registration`, `worldmap`), native tests, `Verify :: All`, a restart against
a persistent database for the drug, radiation and poison restore, the AiControl
client smoke (`Game.AiControlStart` against the Engine listener, `use_skill` with a
scenery target), and a player smoke of equipping, registration, chat, console and
say input with Cyrillic text.
