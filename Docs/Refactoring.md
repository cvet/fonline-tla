# Scripts Refactoring Plan

This document is the plan and running status for the end-to-end refactor of the TLA AngelScript
gameplay layer (`Scripts/*.fos`). The code is old, has been through many engine migrations, and is
inhomogeneous (mixed idioms, dead/relic code, latent bugs). The goal is tidy, reliable, correct
code: ordered modules, clearer naming and readability, fewer stray comments (more where they help),
and bugs fixed with the original intent restored.

Scope is `Scripts/*.fos` (≈262 editable files) plus the supporting validators under
`Tools/ScriptQuality/`. `Scripts/Content.fos` and `Scripts/GuiScreens.fos` are generated — do not
hand-edit (see [AGENTS.md](../AGENTS.md)).

## Principles and constraints

- **lf-30 (`H:/lf-30`) is a STYLE/idiom reference, not a source of content or names.** TLA owns its
  serialized properties (e.g. `CurrentHp`/`MaxLife`); do not rename toward lf-30 equivalents.
- **Committed content is English** (code, comments, docs), even though working discussion is in
  Russian. Do not mass-translate existing Russian rationale comments; translate only when already
  editing the surrounding line.
- **Refactor carefully — no thoughtless bulk edits.** In particular, never bulk-delete commented-out
  code: some of it is a migration breadcrumb that may still need porting. Surface, don't delete.
- **Server holds authoritative gameplay state.** Keep behavior-preserving changes behavior-preserving;
  fix bugs deliberately, verifying each against the code (and git history where load-bearing).
- **Do not commit/stage/push** unless explicitly asked; the repo owner reviews and commits.
- **Every step is verified:** Compile AngelScript (0 warnings — warnings are failures) → Bake
  Resources → relevant `Build :: TLA_*`. Behavior-changing server work additionally runs
  `TLA_ServerHeadless` to `"Start server complete!"`. After moving `///@ Property` declarations use
  **Force Bake** (incremental bake leaves stale proto/map layout).

## Approved decisions

1. **Split `Tla.fos`** (a ~2400-line god-module holding most of the project's `///@` metadata plus
   shared helpers) into domain modules, with full bake + headless verification.
2. **Serialized-name alignment** to a single TLA standard and typo fixes, packaged through
   `///@ MigrationRule`. Cross-project-sensitive renames are confirmed case by case.
3. **Process:** validators → full audit → phased implementation.

## Phases

- **Phase 0 — Tooling & audit.** Quality validators (report-only, `--baseline`/`--ratchet`/`--fix`),
  a full module audit, and a baseline snapshot.
- **Phase 1 — Safe cleanups.** Banner/divider removal, obvious dead code, comment hygiene — strictly
  no behavior change. Commented-out code is preserved (surfaced, not deleted).
- **Phase 2 — Idiom modernization.** Replace hand-rolled utilities with native/engine equivalents
  (`UtilsForArray`→native array ops, `Tla::` math→`Math::`), prefer named keys over magic numbers,
  flag-soups → enums (non-serialized only). Behavior-preserving.
- **Phase 3 — Bug fixes.** Each fix re-verified by reading the code and, where load-bearing,
  cross-checked against git history to restore the original intent.
- **Phase 4 — Structural.** Split god-modules; (future) parallel arrays → structs, `any[]` tables →
  typed data.

Module order: low-coupling leaves first, core (`Tla`/`Main`/`Parameters`) last. Each change is
compiled, baked, and smoke-tested as above.

## Validators and verification

`Tools/ScriptQuality/validate_scripts.py` is a report-only quality validator (not a formatter) for
`Scripts/*.fos`: trailing-blank-line, `namespace`==filename, preprocessor-guard balance, component
`== null` probes (errors); banner tags, textpack magic ids, hand-rolled utils,
redundant bool returns, commented-out code, file-too-large (warnings; the `cyrillic-comment`
check was retired 2026-06-20 — comments are Russian now). Modes: `--summary`,
`--baseline`, `--ratchet` (fail only on new violations vs `baseline.json`), `--fix` (safe autofixes).
Run via the VS Code task `Analyze :: Script Quality`. See also `Tools/NullableEstimate/`.

Adversarial bug-hunting uses read-only finder agents over modules (whole-file or line-range chunks
for the giants), then independent skeptic agents that try to refute each finding; only findings that
survive majority verification are applied, after a manual re-check.

## Status

- **Phase 0 — done.** Validators in `Tools/ScriptQuality/`; full audit recorded under `Build/_audit/`
  (gitignored, local source of truth); baseline established.
- **Phase 1 — done** (decluttering: banners/dividers removed; commented-out code preserved).
- **Phase 2 — done** for the high-value items: `UtilsForArray.fos` deleted (8 callers → native
  `.find`/`.insertLast`); ≈145 `Tla::Clamp/Min/Max/Abs` → `Math::` (type-aware; a few `any`/`double`
  call sites intentionally left on `Tla::`). Remaining low-value idioms (textpack magic ids, some
  flag-soups) deferred.
- **Phase 3 — done.** Audit-driven passes fixed ≈87 verified crit/high bugs across ≈63 files; a later
  adversarial bug-hunt (rounds over under-reviewed and giant modules) added ≈33 more, plus a
  systematic cluster of **26 `? StopChain : StopChain` EventResult-polarity** fixes and 4 architectural
  fixes (`ArroyoMynocDefence` stale timer, `NrWriKidnap` Location→Critter quest property, `SfInvasion`
  re-enabled `OnDead`, `Patrol` per-instance registry). Highlights include `ItemMovement` (all item
  moves were blocked), `Entrance::GetFreeHex` (out-of-bounds crash), NPC plane-AI inversions, AP
  scaling, perk loss, and several economy/quest defects. All verified (compile + bake + headless smoke).
- **Phase 4 — done.** `Tla.fos` split from ~2410 lines to a 675-line core, with metadata and helpers
  relocated to domain modules:
  - Metadata (zero caller churn — properties/enums/settings/events are accessed unqualified):
    `CritterProps`, `ItemProps`, `GameProps`, `GameSettings`, `GameEvents`, `GameEnums`.
  - Helpers (`Tla::` references renamed to the new namespace): `AnimHelpers`, `GameTime` (merged into
    the pre-existing module), `WeaponHelpers`, `Flags`.
  - Cross-cutting core kept in `Tla.fos` (`MaxSkillValue`, `RootContainerStack`, `AP_DIVIDER`,
    `GetCritPropsDict`, the `Chosen*` action ids, the `Min/Max/Clamp/Abs` math, `Elevator*`,
    `Fixboy*`, dialog helpers, `GlobalProcess*`).

  Save-safety was confirmed against the engine: disk/DB persistence is keyed by property **name**
  (`PropertiesSerializator::SaveToDocument`), so relocating a `///@ Property` declaration (without
  renaming it) does not change the serialized contract; `regIndex` is used only for same-build network
  sync. No `MigrationRule` was required for the relocation.

## Remaining / deferred

The active phases above are complete. What is intentionally not changed, and why:

- **Idioms — done where it applies.** Magic text ids were named in all active modules (Behemoth and
  the live map/quest modules). The residual sits in **dead code** (events under the disabled
  `GameEvent::DeclareEvents`), **generated** `GuiScreens.fos` (validator-excluded), one **missing-string
  ref** (`NrWriKidnap.fos:437` → text id 3354 absent from the pack — a separate content bug), and a
  handful of **single-use** ids where a named const adds no readability. `flag-soups → enums` is gated
  by the plan's "non-serialized only" rule: the discriminator groups (`AI_PLANE_*`→`plane.Type`→
  serialized `Planes[]`, `TYPE_ORDER_*`/`ORDER_TYPE_*`→properties, `HF_*`/`MF_*`/`USE_*`→bitwise) are
  all serialized or bitwise, so none qualify. The two `any`/`double` `Tla::Clamp` sites are correct as
  is (no `Math::` double overload).
- **Migration debt — empirically broken; kept disabled.** Re-enabling the commented `start()` inits was
  tested one at a time (compile + bake + headless smoke). **Every one crashes startup** with a
  null-pointer on a fresh (in-memory) DB, non-deterministically: `Caravan` (`CaravanInfo::AddRoutePoint`
  → `CaravanRoute.AddPoint`, Caravan.fos:761), `GameEvent` (`DeclareEvent`, GameEvent.fos:391; also
  schedules the broken racing event), `BulletinBoard` (`StartMessenger` → `Messenger.Load`,
  BulletinBoard.fos:243). Enabling any of them makes the server fail to start, so they are left disabled
  (the working state). Completing them is WIP feature work for the owner, not refactoring.
- **Structural array→struct** is explicitly **(future)** in the Phases section; the Phase-4 deliverable
  (god-module split) is done.
- **Per-module backlog:** remaining medium/low findings in `Build/_audit/` (most medium/high already
  fixed in the bug passes).

## Notes / lessons

- After relocating `///@ Property` declarations, run **Force Bake** — the incremental bake reports
  "baked 0 files" and leaves protos/maps on the old layout, producing transient startup errors.
- When creating a new domain module, verify the file does not already exist
  (`git cat-file -e HEAD:Scripts/<name>.fos`) before writing it — there is a pre-existing `GameTime`
  module; new metadata went into genuinely new files.
- Moved helpers that call symbols still resident in `Tla.fos` must qualify those calls (e.g.
  `Tla::MaxSkillValue`, `Tla::Max`); the compiler catches any that are missed.

---

# Round 2 (2026-06-20) — Polish, headers, comments, bug fixes, tests

Reopened by the owner after the Phase 0–4 close. New goal: bring every `Scripts/*.fos`
module to a uniformly readable, well-documented, correct state. The detailed style rules
live in [ScriptStyle.md](ScriptStyle.md); this section is the **plan and running status**.

## Owner decisions (2026-06-20)

1. **Comment language = Russian, including translating existing English comments.** This
   reverses the prior English-only convention and the 2026-06-17 "don't touch comments"
   feedback. `AGENTS.md` and memory are updated so future agents don't revert it.
   Serialized names (`///@ Property/Enum/Setting/Event`, proto ids, text-pack keys) stay
   English.
2. **File headers everywhere.** Every non-generated script gets a Russian header block
   above `namespace` describing its purpose and side (SERVER/CLIENT/MAPPER).
3. **Aggressive behavior changes allowed.** Bug fixes and cross-file function relocation
   are applied in-pass, verified by compile + bake + headless smoke. Gameplay/quest
   changes that smoke can't catch are still applied but **flagged in the batch report**
   (owner playtest). Serialized-contract changes still gate on `///@ MigrationRule` +
   owner confirmation.

## Scope

269 `Scripts/*.fos` + 3 `Scripts/Json/*.fos`. Generated files excluded (`Content.fos`,
`GuiScreens.fos`). Work proceeds in domain batches, low-coupling leaves first, core
(`Tla`/`Main`/`Parameters`) last — same ordering principle as round 1.

## Phases

- **R2-0 — Inventory & criteria.** `ScriptStyle.md` (done). A read-only workflow builds a
  per-module map: purpose (→ header text), domain, size, formatting/naming/structure issues,
  suspected bugs (line refs), test-feasibility (pure helpers), dependencies. Feeds headers
  + batching. *(Status: criteria done; inventory pending.)*
- **R2-1 — Pilot.** 3–5 representative modules (one leaf, one NPC/quest, one client/GUI,
  one mid-size system) taken fully through ScriptStyle.md so the owner can approve the
  target look before fan-out. *(Status: pending.)*
- **R2-2 — Per-domain polish batches.** Each batch, per module: confirm intent → header →
  translate/add Russian block comments → reorganize structure (radel 4) → format → naming →
  idiom/nullability cleanup → in-pass bug fixes → verify. Batches sized small (4–6 modules)
  to stay under server rate limits and keep review tractable. *(Status: pending.)*
- **R2-3 — Tests.** Per the testing decision below. *(Status: initial harness and seven suites operational;
  expand coverage with each gameplay batch.)*

## Testing strategy — decided (2026-06-20): B, lightweight harness

Owner chose tier **B**. Port a compact `Testing.fos` from lf-7 down to TLA's systems
(RegisterTest / Expect / Pass / Fail + fixtures: isolated location, spawn NPC/player/item,
cleanup with leak check), gated by a `Testing.Enabled` setting, plus a `Launch :: Tests`
task. Then `Test_*` suites starting with pure helpers (Reputation, Math/Flags, GameTime,
WeaponHelpers), growing into critical server flows. The initial harness is now implemented;
new suites remain an incremental part of each refactoring batch.

For the record, the tiers considered:

- **A. Minimal** — keep relying on compile + bake + headless smoke + engine `TLA_UnitTests`;
  add `//~run`-style dev commands (like `Test.fos`) for manual checks. ~0 new infra.
- **B. Lightweight harness (recommended)** — a small TLA `Testing.fos` (RegisterTest /
  Expect / Pass / Fail + fixtures: isolated location, spawn NPC/player/item, cleanup with
  leak check) gated by a `Testing.Enabled` setting and a `Launch :: Tests` task, seeded by
  adapting lf-7's `Testing.fos` down to TLA's systems. Then `Test_*` suites starting with
  pure helpers, growing into critical server flows. Moderate effort, incremental.
- **C. Full port** of the lf-7 framework (parallel suites, embedded-client warmup, etc.).
  High effort; overkill for current needs.

## Verification & process

Per ScriptStyle.md §9. Do not commit/stage/push (owner reviews). Surface contentious or
gameplay-affecting changes in each batch report rather than applying silently.

## R2-2 progress — header coverage complete + verified bug batch (2026-07-03)

**Headers/polish batch (workflow, 116 files).** All remaining `Scripts/*.fos` without a header block
were taken through the strict-safe polish (Russian header above `namespace` + English→Russian comment
translation), giving **header coverage across the whole tree**. 103 modules got the full comment
polish; the 13 giants (Worldmap, Caravan, Combat, Poker, Parameters, Main, ClientMain, MapperMain,
NpcPlanes, ChosenActions, FixBoy, GlobalmapGroup, Purgatory) got header-only — their full comment
polish is deferred, to be done carefully in chunks. Machine-verified code-equivalent vs HEAD
(`Build/_auditall_head.py`: no code / `///@`-tag / midline drift, CRLF); Format (changed 0) → Compile →
Bake → `--ratchet` all green.

**Verified bug batch (adversarial workflow).** The 264 suspicions the polish agents flagged were
triaged: 111 bug/gameplay candidates run through a triage verifier + a 2-skeptic panel (consumer-contract
and git-intent lenses, refute-by-default). **14 survived (97 refuted). 11 applied** (each re-checked by
reading the code + git):

- NoPvpMaps `NoPvpOff` — missing `return;` dropped PvP protection inside safe zones (mirrors Purgatory). *high*
- QuestWarehouse `ProcessSubQuest1` — null-guard; an offline party member returned null → CreateLocation crash.
- Perks `PerkBetterCriticals` — gated on effective stats, switched to `*Base` (drugs could flip availability).
- V13ZSoldier `FriendlyFirePlane` / WarehouseTurret `TurretBeginPlane` — EventResult polarity (friendly/inactive → veto = `ContinueChain`).
- VcGateGuard — removed a dead `removeAt(find == -1)` crash in the contraband branch.
- MsgStr `StrKarmaGenDescription` 6001→6002 — id collided with the caption; the description text lives at 6002.
- Radiation `RADIATION_DURATION` — restored the `*60` (stages wore off ~60× too fast). *[balance — playtest]*
- Repair `SetItemCost` — no longer zeroes cost for good-condition items. *[economy — playtest]*
- Scores `AddScore` — removed the record-holder early-return that froze the global top. *[leaderboard — playtest]*
- ReddWanamingo — un-inverted the map-leave delete guard (was deleting the cavern while players were still on it). *[map lifecycle — playtest]*

**Confirmed but NOT applied (owner follow-up):**

- MsgStr id68 — the legacy numeric `*TextId` helpers (summed `.hstr().uhash`) resolve to empty text since
  the post-#144 hash change; repointing the live callers (ClientMain SPECIAL panel, Drugs, GuiScreens PipBoy,
  NrWriKidnap) to the two-key helpers is a cross-file migration that also touches generated `GuiScreens.fos`.
- VcCommon `CheckIsBlackHere` passes an item proto to `GetCritters` (always empty) — but the function has
  **no callers** (dead) and git never held a critter proto here; the verifier's suggested
  `Content::Critter::vc_black_jack` is a **dialog** proto, not a critter, and does not compile. Left as-is
  (needs the owner to name the real "Black" critter proto). Good reminder that even 3/3-verified fixes get
  the compile gate.
- Trap id90 — the "grenade explodes on failed setup" flavor never fires (guard needs Hidden+IsTrap); restoring
  it adds player damage — a design decision.

**Verification:** Compile + ForceBake (550 maps) + `--ratchet` + headless smoke → "Start server complete!"
(0 exceptions). Only the 11 fix files changed code; the other 105 polished files are comment-only. Not
committed (owner reviews). Full flag data lives in the workflow task journals / `Build/` scratch.

**Giants comment polish (2026-07-03, follow-up workflow).** The 13 giants had header-only before; a chunked
workflow (large files split into sequential ~2000-line ranges, files in parallel) translated their English
comments to Russian — **776 comments** across the 13 modules (Worldmap 132, Combat 142+8, ClientMain 97,
Main 115, GlobalmapGroup 81, NpcPlanes 52, Parameters 51, MapperMain 43, ChosenActions 40, Poker 13, Caravan
9, FixBoy 1, Purgatory already-RU). One Combat chunk hit the account session limit; its residual (~8 real
labels) was finished by hand, leaving `clang-format` directives / Fallout2.exe offset references / code
breadcrumbs untranslated by design. Code-equivalence re-verified (still exactly the 11 fix files changed
code; giants comment-only) + Compile + Bake + `--ratchet` green. So **every non-generated `Scripts/*.fos`
now has a Russian header and Russian comments.**

Those translation agents surfaced **69 more (unverified) flags**. The five representative candidates
originally listed here were verified in the follow-up batch below. The remaining content-table smells in
Worldmap (weight-0 encounters, duplicate location pids, reused special-encounter ids) still need designer
review; the full set remains in `Build`/scratch.

**R2-2 follow-up verified batch (2026-07-10).** The five representative flags were independently checked
against their consumers, engine contracts, and git history before applying anything:

- **Worldmap `CheckChecks` AND-chain restored.** `CHECK_RANDOM`, `CHECK_HOUR`, `CHECK_PARAM_ANY`, and
  `CHECK_PROPERTY_ANY` returned success from the whole function instead of continuing to later checks. Three
  authored chains were affected: the android encounter ignored `SpecialAndroid`, the dead SF paladin ignored
  the armour counter and player level, and the racing encounter ignored Sneak / the one-shot trap property.
  The cases now return only on failure and otherwise continue. *[encounter/quest availability — playtest]*
- **ClientMain chosen item views restored.** The obsolete `EngineCallback_ItemChanged(false)` had been removed
  during the GUI migration but its empty `if (cr.IsChosen)` shell remained. It now refreshes the five chosen-side
  item-view collections through `Gui::RefreshItemViewsByUserDataExts`; the duplicate `SexTagFemale` assignment
  was removed.
- **ChosenActions nullable casts made explicit.** The item lookup and the expected-to-fail `ProtoItem`→`Item`
  downcast now use `cast<T?>`, matching the strong-nullability contract without changing runtime behavior.
- **Vault 13 cleanup.** `V13ZGuard::DenyAccess` had an inverted guard: it did nothing for an allowed player and
  attempted `removeAt(-1)` for a disallowed one. It now resolves the index once and removes only a present entry
  (currently latent: the helper has no authored callers). Eight behavior-equivalent boolean-return warnings were
  also removed across `V13ZGuard` and `V13Goris`.

**Refuted/stale flags:** Poker's `ModChFr / GameNum` cannot see zero in a valid game/save flow (`InitGame`
establishes 1 before the only caller and the 48-field blob preserves it); the duplicate Worldmap Param/Property
helpers are intentional legacy names over the unified `CritterProperty` storage; MapperMain already increments
the conversion failure counter.

**Verification:** formatter check + nullable validator + quality `--ratchet` → Compile AngelScript → ForceBake
(550 maps) → `TLA_Server`, `TLA_Client`, and `TLA_ServerHeadless` builds → headless smoke to
`"Start server complete!"` with no exceptions. Engine unit tests exited 0. A focused AI-control client smoke
registered a fresh character, entered `repl1`, and observed the chosen/map/inventory path without client or
server exceptions. Not committed (owner reviews).

**R2-2 crafting follow-up (2026-07-10).** A focused re-audit of the FixBoy triple protocol
`(pid, count, orNext)` confirmed that `orNext = 1` joins the current entry to the next one as an alternative.
The server had three divergent decoders for that protocol, so OR requirements were broken in different ways:

- `NeedTools` checked only the first alternative. This made the later tools unusable in four live recipes:
  leather armour (id 1), leather armour Mk II (id 2), cured leather armour (id 4), and sharpened pole (id 82).
- The currently latent resource-OR path required every alternative during validation, used `>` instead of
  `>=` during consumption, and never considered the terminal alternative. Validation and consumption now use
  one group interpretation; resources consume the first sufficient alternative and tools remain reusable.
- The FixBoy GUI dropped the final recipe because its list loop rejected an exact five-field tail record. Its
  requirement text also read the connector flag from the wrong triple, used hard-coded Russian `и` / `или` on
  the English client, and relabelled resources as tools after refresh. The `.fogui` source and generated
  `GuiScreens.fos` now agree, use localized `StrAnd` / `STR_OR`, and preserve the final recipe.

The live craft regression exposed an independent multithreading bug: the deferred
`Parameters::UpdateExperienceLevel` time event did not inherit the crafting RPC's sync cover and accessed the
critter from a worker without a lock. It is now `[[Async]]` and locks that critter before calculating level,
skill points, health, and perk awards. The narrow critter-only lock matches the callback's actual access set.

**Verification:** formatter/quality/nullability checks and Compile AngelScript passed; ForceBake rebuilt 550
maps; `TLA_Server`, `TLA_Client`, and `TLA_ServerHeadless` built; startup reached `"Start server complete!"`.
A fresh AI-control character on `repl1`, owning only the last tool alternative (`combat_knife`), crafted recipe
1: exact resources went to zero, the tool remained, and one leather armour appeared. A threshold run advanced
experience 900→1050, level 1→2, and max HP 33→38. The final server log contained no exception,
access-without-sync, error, or assertion entries. Not committed (owner reviews).

## R2-3 harness and barter/GUI regression batch (2026-07-11)

The lightweight `Testing.fos` harness is live behind `Testing.Enabled`, with the
`Launch :: TLA_Tests [windows]` task, isolated location/NPC fixtures, cleanup, filtering,
timeouts, and exit status. Seven suites now cover Flags, GameTime, Stdlib serialization,
fixtures, WeaponHelpers, barter pricing/count bounds, and the NpcPlanes null-entry regression.
The final server run completed **24 passed, 0 failed, 0 skipped**.

The barter/container batch added authoritative transfer sessions, stale-RPC guards, duplicate/count/slot
validation, bounded 64-bit cost and weight arithmetic, zero-cost sale rejection, shared client/server pricing,
and an MCP `Dialog → Barter → Dialog` flow. A live run bought `healing_powder` for 27 caps, refreshed the
same session, and returned to the same dialog. The GUI generator now enables draw callbacks for every authored
`OnDraw` and for legacy sibling-cell `ItemView`s; this restored Barter panels, Inventory equipment slots,
Credits motion, and other dynamic content.

Screenshot verification now combines engine TGA integrity checks with per-screen ROI oracles. The final live
matrix passed Options, Inventory, Character, PipBoy, FixBoy, Menu, and Credits (7/7); the barter oracle also
requires four item panels and both totals. The quest runner completed Cassidy's monotonic 0→1→2 cycle through
the exact `vault_city/vcity_courtyard` map target and reports how many transitions were genuinely exercised.
Compile AngelScript, ForceBake (550 maps), native server/client builds, Python/unit/static MCP checks, and
script quality gates were green for the batch. Not committed (owner reviews).

## R2-3 contextual GUI/container mechanics batch (2026-07-12)

The second R2-3 mechanics pass hardened the real server contracts behind contextual windows instead of
treating screenshot setup as a client-only concern:

- Container transfers now validate the complete session/transfer tuple, current map and range, ownership,
  `NoLoot`/`NoSteal`, opened state, count, authoritative AP, and destination capacity. Volume/count arithmetic
  is overflow-safe; moving a container into itself or one of its descendants is rejected. The server takes the
  full synchronization cover before resolving the operation, closes stale sessions/snapshots, and the client
  suppresses duplicate clicks until an authoritative refresh clears its pending marker.
- `UseItemOn` now requires an item owned by the acting critter, accepts at most one real target, checks the
  correct self/target capability, resolves targets only on the current map under the full lock cover, and keeps
  the historical null-target contract for self-use. This fixes the Timer path that previously passed the chosen
  as an explicit target and therefore failed to activate dynamite.
- Radio editing now writes the parsed channel back on Enter, clamps it to `0..65535`, and keeps fixed-channel
  radios read-only. Elevator validation rejects invalid types/maps/levels, fixes the level-count boundary and
  Military 3/4/6 display mapping, and gives its buttons/indicator valid geometry. DialogBox now has a dynamic
  layout, bounded answer count, expiry/session validation, and a three-argument answer contract; delayed answers
  cannot act on a newer prompt.

The AI-control surface grew with the same contracts. `tla_use_item` accepts only canonical, self-only
`timer:<seconds>` values in `1..599`. `tla_ui_answer` accepts an exact `answer_N`/`level_N` or a zero-based
index; DialogBox answers must include `expectedSession` from the same observation, so stale captures are
rejected. `tla_qa_show_dialog_box` supplies a gated, server-backed two-answer fixture with a safe no-op choice.
Map/inventory observation now includes real ownership, stackability, cost/weight, use/pick-up/timer capability,
and door/container/locker state, allowing automation to reject unsafe candidates from data rather than proto-id
guesses.

`tla_show_context_screen` builds the genuine parameter contract for `SkillBox`, `Aim`, `Split`, `Timer`, and
`Use`. `tla_context_gui_playtest.py` combines those with mechanic-owned `PickUp`, `Radio`, `Elevator`, and
`DialogBox` for a nine-window, ROI-aware screenshot matrix. It requires owned/capable items, a safe visible
container, an owned radio, an authored elevator trigger, and the gated DialogBox fixture; it does not preserve an
explicit-id escape hatch around those checks. The `Aim` oracle follows the authored interface and recognizes its
green labels (rather than the gold text used by several other windows).

Live graphical verification is complete. A standalone DirectX client passed all eight Arroyo contexts available
there (`SkillBox`, `Aim`, `Split`, `Timer`, `Use`, `PickUp`, `Radio`, and `DialogBox`) and a dedicated Mariposa
run passed `Elevator`, for **9/9** contextual windows overall. The actual Timer command consumed one dynamite
stack entry and created one `active_dynamite`; selecting semantic answer `level_2` in the real three-button
Military elevator transferred the chosen from `mariposa_level1` to `mariposa_level2`. Embedded-headless captures
were valid TGA files but contained a black framebuffer, so visual regression capture uses the standalone graphical
client; the headless client remains suitable for non-visual protocol and gameplay checks.

The same follow-up removed a systematic scenery-parameter migration hazard: authored `SceneryParams` are strings,
so numeric fields are now parsed as signed decimal text (with explicitly allowed legacy `@` prefixes) instead of
using string hashes, and content ids are normalized without treating a textual `0` sentinel as a proto id. The new
content validator scanned **275 maps**, **169599 item sections**, and **141 known scenery contracts** with
**0 errors**. It reports **3 non-failing warnings** for ambiguous legacy `Scenery::TransferToMap` records whose map
proto is passed to an API that expects a location proto; these require content-owner decisions rather than an
automatic rewrite.

**Confirmed verification:** MCP Python discovery **89/89**, GUI-generator/formatter units **6/6**, and static
MCP smoke **PASS**; formatter, quality-ratchet, nullable, and AngelScript compilation gates passed; ForceBake
rebuilt **550 maps**; `TLA_Server`, `TLA_ServerHeadless`, and `TLA_Client` built; the script harness completed
**61/61**; native `TLA_UnitTests` exited **0** in **433.7 s**. Not committed (owner reviews).

## R2-3 trigger synchronization and prompt-safety follow-up (2026-07-13)

A live Silo run exposed a strict-sync failure that static compilation could not see: the authored multihex trigger
did fire, but `Silo::Transit` read `Location.SiloMissileLaunched` without holding the location. The callback is now
async, locks the player/current map/location/target map as one cover, and revalidates the topology before transfer.
The corrected mechanic was exercised from `q_silo2` at `39,83` through the trigger to `q_silo3` entry 1 at
`116,77`.

The same audit fixed eight other location-aware `ItemTrigger` callbacks in `GameEventReplicator`, `KlamTrappers`,
`ModocVampire`, `NrWriKidnap`, and `SeAndroid`. Their covers now include the source and target maps, locations,
affected NPCs, doors/containers, and inventory items as required. Script quality gained the zero-tolerance
`item-trigger-location-sync` check plus four validator unit tests, so a callback that calls `GetLocation()` without
both `[[Async]]` and an explicit `Sync::` cover is rejected before bake.

Three NPC AI modules (`PatternMedic`, `PatternSlayer`, and `PatternTerm`) also had nullable global pattern handles
instead of constructed instances; explicit construction removes the null dereferences seen while generating a fresh
`silo_base`. A clean repeat location creation contained no pattern, null, sync, assertion, or error markers.

DialogBox dispatch was hardened beyond the safe QA answer. NCR brahmin confirmation now locks the player, target
brahmin, and both current maps with revalidation. Purgatory invite confirmation uses a dedicated
`PurgatoryInviteSync` snapshot/cover for battle state, target/source maps, request critters, inventories, and the team
container. The invite callback's `transit` flag is now a genuine `bool&` inout parameter, so `transit=false` actually
prevents the unintended direct map transfer. Observed DialogBox buttons expose `answer_0` as
`role=confirm, dangerous=true` and `answer_1` as the safe cancel choice.

The scenery content validator now matches the runtime decoder bounds exactly (positive roles/net ids, NPC dialog
line/radius lower bounds, wait `1..60`, radius `1..100`). Its **8/8** tests cover both valid boundaries and rejected
runtime-invalid records; the full scan remains **275 maps / 169599 item sections / 141 contracts / 0 errors**, with
the same three owner-decision `TransferToMap` warnings.

**Final verification:** AngelScript compilation, formatter check, quality ratchet, nullable validation, ForceBake
(**550 maps**), and `TLA_Server`/`TLA_ServerHeadless`/`TLA_Client` builds passed. The script harness completed
**62/62**; MCP discovery completed **90/90** plus static smoke PASS; GUI/formatter/content-quality units completed
**14/14**, and the new script-quality validator units completed **4/4**. A fresh live DialogBox cancel plus the Silo
transition completed with no server/client exception, null, sync, assertion, or error markers. Not committed (owner
reviews).

## Latest Engine compatibility bump (2026-07-13)

The Engine submodule was fast-forwarded by 15 upstream commits from `67ee893ae721d149cd44ff314abd8036adfd3821`
to the current `origin/master`, `0bdb06bb59fef02b58496ef89105f66d7a243f32`. The range contains the smart-pointer
and exception-safety refactors, nullable `ItemStatic` marshalling, resource-pack glob filters, finite-float/font
changes, and the additive `OnCritterPreLoad` lifecycle event.

TLA's native script boundary now follows the new borrow-wrapper ABI. Export receivers and dialog accessors use
`ptr<T>`/`nptr<T>`; dialog `FindFunc`/`CheckFunc` signatures preserve a non-null actor and nullable talker; and the
three `SafeAlloc::MakeRaw` ownership hand-offs use `make_unique_del_ptr` (with `reinterpret_as<uint8_t>` for opaque
engine user data). Internal raw pointers that do not cross the script ABI remain unchanged. The nullable validator
was extended with focused tests so these forbidden raw script-boundary pointers fail before CMake code generation.

All 25 TLA `[[ItemStatic]]` callbacks now expose the engine's exact
`bool(Critter, StaticItem, Item?, any)` contract. The mining entrypoint narrows the nullable item before calling its
non-null tool helper; callbacks that do not consume an item retain their behavior. `CompileAngelScript` alone does
not validate this attribute signature, so the baker and a dedicated static quality check are part of the gate.

Resource packs were migrated from the removed `RecursiveInput` setting. Directories are recursive in the new
engine, while `Metadata` and `Scripts` use `IncludePatterns = *` to preserve their former top-level-only behavior
and avoid mounting `Scripts/Json` twice. `OnCritterPreLoad` needs no TLA subscriber for this bump; existing
`OnCritterInit` handlers were deliberately left in place because several require an attached map/world.

Persistent-login testing exposed two strict-sync regressions that the compile/bake gates could not see. TLA's
`PlayerLogin` is now async and preserves the complete `player + optional unloginedPlayer + main critter + map +
location` cover while loading or switching the controlled critter; the map/location links are revalidated after
each replacement `Game.Sync`. This fixes login after the previous client has disconnected and the main critter
must be loaded or rebound.

The simultaneous reconnect path also exposed an upstream Engine gap after `OnPlayerLogin`: native
`SendCritterInitialInfo` ran with only the two login players covered, so a controlled critter on a local map failed
on the first map access. The local Engine follow-up preserves both login entities for rollback, acquires the
critter/map/location chain in two validated stages, bounds topology retries, and delays destruction of the
displaced login entity until the new player job is scheduled. A focused `PlayerRegistrationCppApi` regression
covers this exact live-player/local-map reconnect.

**Verification:** Compile AngelScript and the build-hash-triggered full bake passed (**550 maps**), followed by
`TLA_Server`, `TLA_ServerHeadless`, `TLA_Client`, and `TLA_UnitTests` builds. The full native suite exited **0**;
its focused reconnect case passed **144 assertions**, and the full run passed **355538 assertions in 335 test
cases**. The live script harness completed **62/62**; MCP discovery completed **90/90** and both static and live
bridge smokes passed. Script-quality and nullable gates passed, and the scenery scan remained at **0 errors**
with the same three owner-decision warnings. A standalone DirectX client registered `EngBot7`, entered and
QA-transferred to Arroyo, reached a real dialog, and passed the seven parameterless GUI screenshot oracles plus
`SkillBox` and safe-cancel `DialogBox` (**9/9** captures). A second persisted session verified disconnected
relogin for `LiveBot7`, while a fresh `GreenBot7` session verified online-client replacement, observation, and
movement; the post-relogin GUI matrix passed another **7/7** content oracles without server/client sync or
exception markers. Reports are under
`Workspace/AiControlScreenshots/engine-bump-20260713` and
`Workspace/AiControlScreenshots/engine-bump-context-20260713`, with reconnect reports and captures under
`Workspace/AiControlScreenshots/engine-bump-relogin-20260713`. Not committed (owner reviews).

## Latest Engine updater cutover follow-up (2026-07-15)

The Engine submodule was fast-forwarded by another 16 upstream commits from
`0bdb06bb59fef02b58496ef89105f66d7a243f32` to the current `origin/master`,
`2f4fc0adfdabf71316f087bf36ceb6baf49c81da`. The functional range through `1bcf6e101` completes the
smart-pointer refactor, hardens AngelScript synchronization and deferred `ScriptFunc` return cleanup,
synchronizes the player argument for inbound server RPCs, updates movement call sites to the implicit borrow
form, and replaces the client updater bootstrap with the host/runtime selector. It also raises the forced
migration version to `0.0.30`; the final `2f4fc0adf` commit only strengthens an upstream test. No TLA-facing
script API, hook, event, setting, CMake, or native export signature changed. The resulting TLA compatibility hash
is `93b603081c433c36`.

Two local Engine synchronization fixes remain necessary. Reconnect now acquires and stabilizes the complete
player/unlogged-player/critter/map/location cover before controlled-critter initial state is sent, while keeping
the displaced player alive until the login can no longer roll back. `LoadCritter` now restores and stabilizes the
critter/map/location cover after the re-entrant `OnCritterInit` callback before processing visible critters and
items; it also stops cleanly if the critter is destroyed while the cover is being rebuilt. Both paths have focused
lifecycle regressions in `Test_EntityLifecycle.cpp`.

On the game side, newly registered player critters are now explicitly persistent. Previously their only
persistence came from map attachment, so offline unload removed that implicit flag and deleted the critter
document before a later login. Strict synchronization exposed four additional reconnect boundaries: dynamic
`KnownLocations` serialization, global-map group movement data, replication transfer/map-location access, and
the `PlayerLogin`/`SwitchCritter` chain. These paths now preserve the caller cover, lock the complete dependent
entity set, and reacquire it after re-entrant transfers or switches.

The updater change is an intentional deployment cutover: `FO_UPDATER_VERSION` is now 2 and the client runtime
host ABI is now 3. The Windows build therefore includes both `TLA_Client.exe` and the separately built
`TLA_Client.dll`; the host accepted DLL build hash `586344806a74f05a03ddcc9c785a5dbcb1c9b1bc` with matching
compatibility and ABI 3 metadata. Generation-1 clients are rejected before `InitData`, and an ABI-2 host cannot
load the ABI-3 runtime, so this engine version must be shipped as a complete client package and existing
installations require a one-time manual replacement rather than an in-place self-update.

**Verification:** Compile AngelScript passed; ForceBake rebuilt **550 maps**; `TLA_Server`,
`TLA_ServerHeadless`, `TLA_Client`, `TLA_ClientLib`, and `TLA_UnitTests` built. Focused reconnect, runtime-ABI,
handshake, update-list, and obsolete-updater rejection tests passed **308 assertions in 5 test cases**; the final
lifecycle and registration regressions independently passed **219** and **158 assertions**. The exact final full
native suite passed **355727 assertions in 341 test cases** and exited **0** in **246.624 s**. The live script
harness completed **62/62**; script-quality, nullable, and content gates remained green; MCP tests passed
**96/96**; and the scenery scan remained at **0 errors** with the same three owner-decision warnings.

The MCP navigation adapter now normalizes TLA's flat `hexX` / `hexY` observations and lets both navigation plan
and safe-step queries fall back from unsupported `tactical_path` to `path` without hiding other query failures.
A standalone client registered `Persist10`, moved, disconnected, survived offline unload, then logged into the
same critter, observed the restored map, passed reachability, and moved again without sync, exception, assertion,
or missing-document markers. Reports and preserved logs are under
`Workspace/AiControlScreenshots/engine-2f4f-20260715/persistence-final`. The seven parameterless GUI screenshot
oracles plus `SkillBox` and safe-cancel `DialogBox` remain green under
`Workspace/AiControlScreenshots/engine-1bcf-20260715`; the only later upstream commit is test-only.

The Windows installed-client staged restart and Linux runtime DSO paths remain release/CI checks. Registration
still has a same-name race between parallel requests, and a failed post-creation login can leave an orphaned
persistent critter; those need a transactional follow-up. The local Engine fixes and game changes are intentionally
left uncommitted for owner review.
