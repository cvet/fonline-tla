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
async registration/login path now owns the caller cover across Engine calls: it holds the request and an existing
live player before an offline load, then stabilizes the main critter, its map and location, dynamic
`KnownLocations`, and every member of its global-map group before login. Each topology-dependent set is
revalidated after replacement `Game.Sync` calls. This fixes login after the previous client has disconnected and
the main critter must be loaded or rebound.

The simultaneous reconnect path also exposed a failure after `OnPlayerLogin`: native `SendCritterInitialInfo`
needs more than the two login players when the controlled critter is on a local map or in a global-map group. An
initial Engine-side cover-rebuild attempt was superseded by the caller-owned contract documented in the 2026-07-15
follow-up below. `LoginPlayerToExistentRecord` now only validates the cover prepared by AngelScript and fails fast;
it never narrows or expands that cover. The remaining native change is rollback hardening: destruction of the
displaced login entity is delayed until the new player job has been scheduled. Focused `PlayerRegistrationCppApi`
regressions exercise local-map and global-group reconnects with an explicitly prepared caller cover.

**Historical 2026-07-13 verification (before the later synchronization ownership correction):** Compile
AngelScript and the build-hash-triggered full bake passed (**550 maps**), followed by
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

The Engine submodule was fast-forwarded by another 17 upstream commits from
`0bdb06bb59fef02b58496ef89105f66d7a243f32` to the current `origin/master`,
`81748b948a36b5737107bea9d87e03982cc4b3cc`. The functional range through `1bcf6e101` completes the
smart-pointer refactor, hardens AngelScript synchronization and deferred `ScriptFunc` return cleanup,
synchronizes the player argument for inbound server RPCs, updates movement call sites to the implicit borrow
form, and replaces the client updater bootstrap with the host/runtime selector. It also raises the forced
migration version to `0.0.30`; `2f4fc0adf` only strengthens an upstream test. The final `81748b948` commit adds
the common `Game.GetModelAnimDuration` script API and always emits model-animation metadata in 3D-enabled model
bakes. TLA has `FO_ENABLE_3D=OFF` and no `ModelInfo` pack, so it needs no authored config/content migration; the
missing `ModelAnimInfo.foinfo` startup line is informational and duration lookup falls back to zero. The resulting
TLA compatibility hash is `d4721a8cce1d01c0`.

The final synchronization boundary is script-owned. Neither `LoadCritter` nor
`LoginPlayerToExistentRecord` calls `SyncEntities`, narrows the held set, or discovers and adds dependent
entities. TLA AngelScript owns the required cover in the outer async context before every Engine call. The offline
path holds the request and any existing live player before `LoadCritter`; because the loaded critter does not exist
in memory before that call, `OnCritterInit` no longer performs topology-changing placement. Immediately after
`LoadCritter` returns, the caller adds the critter and performs placement under an explicit source/target cover.
Before login and initial-info delivery it stabilizes the full graph: request player, existing live account player
when present, main critter, current map and location, dynamic `KnownLocations`, and every member of the
global-map group. Topology snapshots are checked after each replacement `Game.Sync`, with bounded retries. The
Engine only validates access through the caller-provided cover and fails fast when the contract is violated. Its
reconnect-only change is unrelated rollback hardening: the displaced player remains alive until login scheduling
succeeds, so a thrown callback can still restore the connection. Focused lifecycle tests model the script caller
by explicitly synchronizing the local-map or global-group cover before entering the Engine API.

Newly registered player critters are now explicitly persistent. Previously their only persistence came from map
attachment, so offline unload removed that implicit flag and deleted the critter document before a later login.
Topology-changing placement was also removed from `CritterInit`: the caller performs it only after
`CreateCritter` or `LoadCritter` returns, while it still owns the surrounding synchronization context. Replication
and story-intro transfers preserve both the source graph and the target map/location (including dynamically
created intro locations), then reacquire and validate them after the re-entrant transfer. The registration/login
and `SwitchCritter` paths likewise retain the player/request entities, critter graph, known locations, and
global-map group through initial-info delivery.

The updater change is an intentional deployment cutover: `FO_UPDATER_VERSION` is now 2 and the client runtime
host ABI is now 3. The Windows build therefore includes both `TLA_Client.exe` and the separately built
`TLA_Client.dll`; the host accepted DLL build hash `62be3ea7d6d7138f0ac198a89c3566ff839b8061` with matching
compatibility and ABI 3 metadata. Generation-1 clients are rejected before `InitData`, and an ABI-2 host cannot
load the ABI-3 runtime, so this engine version must be shipped as a complete client package and existing
installations require a one-time manual replacement rather than an in-place self-update.

**Current script-owned synchronization verification:** Compile AngelScript passed with **0 warnings**; ForceBake
rebuilt **550 maps**; `TLA_Server`, `TLA_ServerHeadless`, `TLA_Client`, `TLA_ClientLib`, and `TLA_UnitTests`
built. Focused model-animation, player-registration, and server-script regressions passed **672 assertions in 3
test cases**. The exact final full native suite passed **355733 assertions in 342 test cases** and exited **0**.
The live script harness completed **62/62**; script-quality, nullable ABI, formatting, build-warning, and diff
gates remained green; and MCP tests passed **96/96**. The live compatibility probe also caught and corrected a
stale unpackaged `TLA_Client.dll`, confirming that `TLA_ClientLib` is a required build/deployment artifact after
an Engine compatibility change. The TLA CMake finalization hook now makes `TLA_Client` depend on
`TLA_ClientLib`, and a clean `Build :: TLA_Client` verification rebuilt/copied the runtime before the host.

The MCP navigation adapter now normalizes TLA's flat `hexX` / `hexY` observations and lets both navigation plan
and safe-step queries fall back from unsupported `tactical_path` to `path` without hiding other query failures.
A standalone MCP-controlled client registered `SyncLatest`, disconnected, reached server-side offline unload,
then loaded the same persisted critter (`1233`), passed observation and reachability probes, and moved again
without sync, exception, assertion, or missing-document markers. MCP discovery and a live command round-trip
passed on the relogged client. The post-relogin GUI screenshot matrix passed Options, Inventory, Character,
PipBoy, FixBoy, Menu, and Credits (**7/7**). Reports, captures, and preserved logs are under
`Workspace/AiControlScreenshots/engine-81748-20260715/script-owned-sync-final`.

The Windows installed-client staged restart and Linux runtime DSO paths remain release/CI checks. At this point
registration still had a same-name race between parallel requests, and a failed post-creation login could leave
an orphaned persistent critter; the 2026-07-18 registration transaction follow-up below resolves both. The
caller-owned script synchronization, native rollback hardening, and game changes are intentionally left
uncommitted for owner review.

## Latest Engine sprite/3D/baker bump (2026-07-22)

The Engine submodule was fast-forwarded by 23 `origin/master` commits from
`236165de4c55c041a9cc532ab617756ea3d022f2` to `0109fee5a` (four upstream merges plus the `#186` 3D-subsystem
and `#187` polygonal-sprites PRs, `small_vector`/perf refactors, sprite/atlas/font rework, MapperEngine
`std::string` buffers, socket-error message stabilisation, and BakeFiles/BakerDataSource changes). Pre-scan
confirmed **no script-API export was removed** and **no `EngineHook`/native-bridge signature changed**; the risk
was concentrated in the baker ABI, the baked sprite format, new settings, and the two changed Core `.fofx`
shaders.

Three concrete migrations were required:

1. **`SourceExt/DialogBaker.cpp` — baker ctor.** `BaseBaker`'s constructor gained a `string_view baker_name`
   second parameter (each engine baker passes its `NAME`). Both `DialogBaker` and `DialogTextBaker` (whose
   headers already declare `static constexpr string_view_nt NAME` and a `GetName()` override) now pass `NAME` to
   the base ctor.
2. **`SourceExt/ServerExtension.cpp` — `Server_Game_LoadImage` baked-sprite format.** This was the load-bearing
   fix: the module-init call `Game.LoadImage(ImageRelief, "relief_tla.png")` (GlobalmapGroup/Worldmap) crashed
   startup with `ScriptException: File is not image`. The atlas/sprite rework replaced the old hand-parsed header
   (single `42` magic byte) with a formalised container (`SPRITE_RESOURCE_MAGIC` 43 + `SPRITE_RESOURCE_VERSION`,
   per-frame mesh payload, footer magic) read by the new `Common/SpriteResource.h` API. TLA's hand-rolled parser
   was replaced by `ReadSpriteResource(file.GetData())` + `ExtractSpriteResourceFrameImage(<dir 0, frame 0>)`,
   storing `image.Size`/`image.Pixels` into `ServerImage`. Correctness verified against the baker: cropping only
   occurs for non-`Quad` frames (ImageBaker `CropSpriteFrameToMeshBounds` is gated on `mesh.Kind != Quad`), and
   TLA runs `SpriteMesh.Enabled = false`, so every frame is `Quad` and stored at full logical size — so
   `relief_tla.png` loads at its exact 1400×1500, keeping the absolute-coordinate relief lookup
   (`GetGlobalMapRelief`, which does no bounds check) correct.
3. **`TLA.fomain` — new required settings.** The polygonal-sprites PR added `FIXED_SETTING`s that are
   Uninitialized-fatal at bake; added with engine defaults: `SpriteMesh.Enabled = False`,
   `SpriteMesh.AlphaThreshold = 0`, `SpriteMesh.MaxTriangles = 4096`, `SpriteMesh.AreaSavingsWeight = 32.0`, and
   `Render.DrawWireframe = False`. The two changed Core `.fofx` shaders (`2D_Default`, `2D_WithoutEgg`) baked
   within the minimal profile (no `gl_FragCoord`/X4502).

A new **`Scripts/Test_Worldmap::relief_image_full_size`** regression pins the migration: it samples the loaded
relief image at `(0,0)` and the far corner `(1399,1499)` — a cropped/shrunk image would throw
`Invalid coords arg` there — and checks the `GetGlobalMapRelief` low-nibble contract.

**Verification:** Baker rebuilt first (after the DialogBaker fix) → Compile AngelScript 0 warnings → full
compatibility-triggered bake (all packs + 550 maps) → `TLA_Server`, `TLA_ServerHeadless`, `TLA_Client`,
`TLA_ClientLib`, `TLA_Mapper`, `TLA_UnitTests` built without warnings (`ServerExtension.cpp` and the sprite/3D
client rework included). Native `TLA_UnitTests` passed **419310 assertions in 360 test cases** (up from
355962/346 — the new sprite-resource/mesh suites), exit 0. `LocalTest` headless reached `Start server
complete!`; the live script harness completed **66 passed, 0 failed, 0 skipped** (added the relief regression),
with no exception/sync/assertion/fatal marker. Formatter idempotent, quality ratchet and nullable ABI green,
`git diff --check` clean. Not committed (owner reviews); this bump sits on top of the still-uncommitted R3
bug-fix working tree.

## Latest Engine handle-only Destroy bump (2026-07-19)

The Engine submodule was fast-forwarded by eight `origin/master` commits from
`14bb6c85e33cd55fede7e7bac3a5d124d51031f6` to `236165de4c55c041a9cc532ab617756ea3d022f2`. Seven are build/test
housekeeping (`f667a85d9` third-party update, `3accf133e` rpmalloc C-standard macro, `65dfb851c` MSVC /W4 shadow
fix, `42b038cf5` effect-baker warning suppression, `998eefcbf` internal `ResolveTargetHex` fallback-hex fix, plus
two merges) and need no game-layer change. The load-bearing one is **`845bdcce4` "Remove id-based entity Destroy*
script exports (handle-only)"**: it drops the `ident_t` overloads of
`Game.Destroy{Entity,Entities,Item,Items,Critter,Critters,Location,Map}`, leaving only the live-handle (and
handle-array) forms. `Game.DestroyUnloadedCritter(id)` is intentionally kept, since an unloaded critter has no
live handle.

TLA had exactly **eight** id-based call sites, all `Game.DestroyLocation(<handle>.Id)` where the `Location`
handle was already resolved and in scope (five plain `loc.Id` in deferred/quest cleanup — `ArroyoMynocDefence`,
`GameEventStorehouse`, `KlamSmily`, `Purgatory`, `ReddWanamingo`, `VcGuardsman`; plus `SeAndroid`
`map.GetLocation().Id` and `SfCommon` `locations[i].Id`). Each now passes the handle directly. A tree-wide scan of
every `Game.Destroy*` call confirmed no other id-based form (no `ident`-typed variable, `.Id`, or `ZERO_IDENT`
argument) reaches these methods; all remaining calls already pass handles or handle arrays. The removed exports
change the script-API surface, so the compatibility hash advanced to `221e34cf740c6ba0` and the bake rebuilt the
full tree (all packs + 550 maps).

**Verification:** Baker rebuilt first, then Compile AngelScript passed with 0 warnings (it pinpointed exactly the
eight `DestroyLocation(ident)` sites, and reported clean after the fix). Full bake (550 maps, compatibility-hash
triggered) → `TLA_Server`, `TLA_ServerHeadless`, `TLA_Client`, `TLA_ClientLib`, and `TLA_UnitTests` built without
warnings (`TLA_Client` correctly rebuilt/copied `TLA_ClientLib` after the compatibility change). A `LocalTest`
headless run reached `Start server complete!`, the live script harness completed **65 passed, 0 failed, 0
skipped**, and the log contained no exception, sync, assertion, or fatal marker (only the benign
`DestroyInnerEntities`/`DestroyAllEntities` shutdown-stage lines). The native `TLA_UnitTests` suite passed
**355962 assertions in 346 test cases**, exit 0 (the single `Map baking error` line is a negative test that
feeds the baker an invalid map to confirm it is rejected). Not committed (owner reviews); this bump sits on top
of the still-uncommitted R3 bug-fix working tree.

## Latest Engine server follow-up (2026-07-18)

The Engine working tree was fast-forwarded in two steps by twelve `origin/master` commits from `5ce19ec24`
through `260c3d883` to `14bb6c85e33cd55fede7e7bac3a5d124d51031f6`. The first server-facing range adds strict
init-script resolution failures, `Map.FindPathToAny` with target validation, lifecycle tracking for sent
messages, and retention of already covered player/critter and singleton-owned entity links within the current
script chain. The retention changes do not discover topology or call blocking `SyncEntities`; TLA remains
responsible for preparing the complete cover with `Game.Sync` before entering the Engine API. Generated build
configuration now uses macros instead of a re-includable typed constants header, and malformed compressed
transport input now disconnects cleanly through `DecompressException`.

The final server update tracks every accepted interthread, TCP, UDP, and WebSocket connection across concurrent
accept/shutdown boundaries. `NetworkServer::Shutdown` closes registration, snapshots and disconnects live
connections, and only then stops the transport implementation. A new `ServerNetwork.LoginTimeout` independently
limits pre-login connections that make no handshake, authentication, or updater progress, so ping-only peers
cannot occupy unauthenticated slots forever. TLA enables a five-minute timeout (`300000` ms) for normal/public
configuration and explicitly disables it in the `Unpackaged` and `LocalTest` profiles for long local debugging
and MCP sessions. This network/unlogged-player job path is not script-initiated and does not acquire entity
synchronization locks. The
upstream `d94f6d9e8` commit also absorbed the temporary local `NetworkClient.h` include-guard fix, leaving the
Engine working tree clean. The resulting compatibility version is `806044423476dc46`.

**Verification:** `BakeResources` updated the three config outputs; `TLA_Server`, `TLA_ServerHeadless`,
`TLA_Client`, and `TLA_UnitTests` built without compiler warnings. Focused login-timeout and concurrent-shutdown
coverage passed **38 assertions in 3 test cases**. The complete native test executable exited **0** in **440.2
seconds**. A `LocalTest` headless run reached `Start server complete!`, completed the live script harness with
**62 passed, 0 failed, 0 skipped**, and shut down all three active connection servers cleanly. Main-config
formatting/check, script-quality ratchet, nullable ABI validation, and the nullable validator's **7/7** self-tests
passed. Runtime initialization still reports execution-overrun timings for the data-heavy `CritterTypes`,
`NpcBags`, trader, and world-generation setup; there were no runtime exceptions or failed tests.

## Registration transaction follow-up (2026-07-18)

New-account registration now claims the `PlayerNames` key while the request still holds the shared start-map
cover and before the next replacement `Game.Sync`. This placement matters: replacing a cover releases the old
set before acquiring the new one, so merely retaining the same map in successive calls still leaves a scheduling
window. A parallel request now observes the reservation before it can create a second critter. Reservations carry
the expected `CritterId`; a mismatched request cannot publish or remove another registration's name.

`PlayerId` publication moved from after `LoginPlayerToNewRecord` into a dedicated `OnPlayerLogin` subscriber.
That event runs inside the Engine's new-player rollback scope: if publication or any later login subscriber
fails, the Engine removes the new `Players` record and detaches the player before the outer registration handler
rolls back the persistent critter. The script removes the name reservation only after critter rollback succeeds;
if cleanup cannot be proven, the reservation remains claimed instead of allowing a second account to reuse a
possibly orphaned character. Display/generation properties are prepared before login, leaving no fallible
persistence step after the Engine transaction returns.

A focused script regression covers reservation visibility, critter ownership checks, `PlayerId` publication,
and owner-only rollback. A two-client MCP race submitted the same fresh name concurrently: exactly one client
entered the game, the loser disconnected back to Login, the server created exactly one player critter, and no
script/sync/assertion error was logged. The winner then disconnected and the losing client successfully logged
into the same account and controlled the same critter id. MCP discovery/live smoke passed, and the graphical
client screenshot audit verified Options, Inventory, Character, PipBoy, FixBoy, Menu, and Credits (**7/7**) with
content-specific oracles. Captures and the manifest are under
`Workspace/AiControlScreenshots/registration-transaction-20260718`.

**Verification:** AngelScript compilation, incremental baking, and `TLA_Server`, `TLA_ServerHeadless`, and
`TLA_Client` builds passed without warnings. The focused reservation test passed, then the complete live script
harness finished with **63 passed, 0 failed, 0 skipped**. Script formatting was idempotent, the quality ratchet
and nullable ABI validator passed, `git diff --check` was clean, and the final headless log contained no test
failure, script/sync exception, assertion, or fatal marker.

## R3 adversarial bug hunt over under-audited giants (2026-07-19)

A workflow re-audited the modules whose round-1 coverage was thinnest (the giants: Combat, Worldmap, Caravan,
Poker, GlobalmapGroup, Parameters, EnergyBarier, Purgatory, NpcPlanes, ChosenActions, FixBoy, Dialog, Main) in
line-range chunks, and separately re-validated the deferred medium/low backlog in `Build/_audit/`. Every candidate
went through a three-lens skeptic panel (consumer contract / engine API / git history, refute-by-default);
**44 of 123 candidates survived unanimously**. The session limit killed part of the verify phase, so the
split-vote and unverified remainder is still open — see "Remaining" below.

**Applied (each re-read against the code before editing):**

- **NPC AI was globally disabled.** `AddPlane` treated `ContinueChain` as a veto, but the engine's
  `Entity::FireEvent` returns `ContinueChain` for an event with **no** subscribers. Only a handful of critters
  subscribe a per-critter `OnNpcPlaneBegin`, so every other NPC had each freshly inserted plane erased on the
  spot — no attack, walk, pick or misc plane ever survived. The polarity is now engine-idiomatic (`StopChain` =
  veto) across `NpcPlanes` and all ten handlers (`MainPlanes`, `Eli`, `MapKlamath`, `Mob`, `Patrol`, `Pet`, and
  the four `Pattern*` wrappers), applied as one atomic change. *[AI-wide — playtest]*
- **`GetPlanes(..., NpcPlane[] planes)` never filled its out-parameter** (found by the new regression test, not
  by the hunt): all three overloads did `planes = crPlanes`, rebinding the local handle, so callers in `Combat`,
  `Item`, `EncounterNpc` and `Patrol` got the right count but an empty array. Now filled in place.
- `AddWalkPlane` 8-arg overload called itself (infinite recursion, dropped `cut`); attack repositioning cancelled
  its own successful manoeuvre via an unconditional `NextPlane(REASON_POSITION_NOT_FOUND)`.
- **Poker was unplayable and leaked caps.** Nested per-NPC state arrays were declared `{{}}`, so the first
  pokerman indexed a zero-length row and threw; `Replace()` dealt the same card to several players; `BetCall`
  destroyed the player's caps without adding them to the pot; the all-in `WinKoef` truncated to 0 so a winning
  all-in paid nothing; the NPC bet-chance ratio collapsed via integer division; `TwoPairReplace` picked a pair
  card as the kicker and passed 0-based indices to a 1-based `SetBit5` (negative shift). `Roulette` had the same
  `{{}}` declaration defect. *[economy/minigame — playtest]*
- **FixBoy workbench charges were never seeded**, so every workbench-gated recipe was permanently uncraftable;
  "no entry" now means "full workbench" (seeded at the timeout check, which keeps the craft count exact).
- `GlobalmapGroup`: entrance ordinals were validated against the flat `MapEntrances` length (client-supplied,
  out-of-bounds reachable) in `GroupToLoc` and `GM_CMD_VIEW_MAP`; `GM_CMD_ENTRANCES` passed the raw index to
  `CheckEntrance` so town-screen and entry rules disagreed; `GroupToMap` overwrote the passenger hex with the car
  hex and ignored its `entry` parameter (all entrances arrived at the main gate).
- `Combat`: burst central line clamped to-hit *before* the knockout/multihex bonuses (95% cap bypassed, a
  knocked-out bystander soaked the whole volley); `HF_DEATH` raised damage only to exactly `CurrentHp`, which
  lands in the knockdown branch because `DeadHitPoints` is -20, so instant-death criticals never killed; the
  flamethrower left line was missing the `- 1` that excludes the victim from the blocker count.
- `Parameters`: `UseMainItem` branched on the packed weapon mode instead of the decoded use-slot, so every aimed
  attack was a no-op; drug resistance bonuses were written one `DamageTypes` slot too low (Psycho gave nothing,
  Rad-X gave poison resistance); `ProcessSkillsUp` wrote a client-supplied property id without checking it is a
  skill; the name language-mixing scan skipped the last character.
- `Main` / `Replication`: the corpse drop filter wrote `null` into the array it then passed to `MoveItems`,
  aborting the whole death handler for any critter carrying a gag/hidden item; steal XP used a stale `StealCount`
  after a streak reset (up to 12× the intended award).
- `Purgatory`: nullable `killer` was forwarded into `OnCritterDead`, which dereferenced it (deaths from
  overdose/poison/radiation on a battle map threw and the winner was never checked); `GetTeamPlayers` indexed
  `Players[]` with a `Requests[]` index; the invite watchdog re-invited after the player had already accepted,
  silently dropping him; `TeamCount` emitted four duplicate `team` lexemes instead of `team0..team3`.
- `Dialog`: `TimeoutCheck` read `player.DialogTimeout` while `TimeoutSet` writes `npc.DialogTimeout`, so all 23
  `TimeoutCheck` / 18 `NotTimeoutCheck` gates were constants; `GetCurrentDialogNumber` used the throwing
  single-argument `dict.get`. *[quest cooldowns now actually gate — playtest]*
- `ChosenActions`: reload deducted AP twice; a vanished move target sent the character to hex (0,0).
- `Worldmap`: `RotatePosition` permanently rotated the module-global formation table (aliased handle, not a
  copy); the weighted encounter roll could exceed the candidate pool and select nothing.
- `Caravan`: `FindCabPlace` took its loop bound from the first entry name only (no wagons placed when entry 243
  is absent); `IsFullParty` accepted one player past `MaxPlayers`, who was then silently truncated at departure.
- `FavoriteItem`: an inverted slot check made NPC favorite-item auto-equip a permanent no-op (NPCs undressed and
  never re-equipped); `EnergyBarier::GetGuards` compared a Location proto against an Item proto.

**New regression test.** `Test_NpcPlanes::add_plane_without_subscriber` covers the exact broken case (an NPC with
no per-critter subscriber must keep an added plane). It was validated as a negative control: reverting only the
`AddPlane` polarity makes it fail on its first assertion, and it is what exposed the `GetPlanes` out-parameter bug.

**Deferred (need an owner decision, not a mechanical fix):**

- `Caravan::CaravanLeaderOnGlobal` assigns to by-value event parameters (`toX/toY/speed/waitForAnswer`, plus
  `x/y/encounterDescriptor` via `Worldmap::FindEncounter`), so caravan global-map movement never reaches the
  group. Fixing it means marking the args mutable in the `///@ Event` declaration and updating every subscriber.
- `Purgatory::TeamContainerId` is never assigned, so the invite flow kills the player without stashing his
  inventory while telling him it was stashed. Both the reporter's and the verifier's placements have problems
  (a location-owned container is garbage-collected with the arena).
- `FixBoy::CheckOnCraft` builds the craft list through the interactive `FixboyButton` path, spamming failure
  messages and mutating persistent map state; a side-effect-free query state is the right fix.
- `GlobalmapGroup::GetGlobalMapGroup` reads `AllGlobalGroups` unlocked and uses `opIndex`, which inserts a
  phantom entry on a miss; failing loudly would widen the return type across ~16 call sites.
- `Combat` `ForceFlags`-only hits send critical-message id 0 (broken combat text); the verifier refuted both
  proposed fixes and points at a client-side guard instead.

**Verification:** Compile AngelScript (0 warnings) → formatter idempotent (changed 0) → quality ratchet →
nullable ABI validator → bake → `TLA_Server`, `TLA_ServerHeadless`, `TLA_Client` builds, all without warnings.
The live script harness finished **64 passed, 0 failed, 0 skipped** (63 + the new regression), the headless run
reached `Start server complete!`, and the log contained no exception, sync, assertion, or fatal marker.
`git diff --check` is clean. Not committed (owner reviews).

The gameplay-affecting entries above are flagged for playtest: NPC AI overall, poker/roulette economy, workbench
crafting, dialog cooldowns, town entrances, and instant-death criticals.

### R3 second pass — the candidates the session limit had dropped (2026-07-19)

The first R3 run lost 164 of 397 verify agents to an account session limit. Reconstructing the finder output from
the workflow journal showed that **67 candidates had never been adjudicated at all** (the post-processing counted
them as neither confirmed nor split, because they had zero votes). A follow-up workflow re-ran them against the
already-patched tree with two independent lenses (consumer contract, engine API + git history), unanimity
required: **17 confirmed, 11 split, 6 already fixed** by the first pass. All 134 agents completed.

**Applied:**

- **FixBoy expired-timeout branch.** `CheckWorkbenchTimeOut` refilled via `SetWorkbenchCharges`, which is a
  *decrement-or-refill* helper, and never cleared `FixBoyWorkBenchTimeout`. So after the first expiry the branch
  ran on every later check and **consumed** a charge instead of refilling — and since `CheckOnCraft` runs once per
  listed recipe, merely opening the FixBoy screen next to a shared workbench (11 recipes share `SCENERY_AMMO_PRESS`)
  drained it. Split out a dedicated `RefillWorkbenchCharges` and reset the timeout.
- `Replication`: the post-`FindEncounter` guard tested the `-1` sentinel, but `FindEncounter` uses `0` for "none"
  (`-1` is an unrelated global-map convention), so `InviteToEncounter` ran with a blank descriptor.
- `MapBarterGround`: the same null-into-`Item[]`-then-`MoveItems` pattern fixed earlier in `Main`/`Replication`.
- `PatternSniper` / `PatternTerm`: `MsgReact` returns true for "should react", but both guards returned early on
  true — snipers and terminators ignored ally help calls *within* range and answered only out-of-range ones.
- **Racing quest was uncompletable.** `Coords` has 13 checkpoints so `player.RacingCheckPoints` tops out at 13,
  while `Win()` requires >= 14. The dialog's final result wrote `RacingCheckpointNumber` — which resolves to the
  *Location* property, not the Critter counter `Win()` reads. Fixed in `Dialogs/den_racing_mechanic.fodlg`.
- `Explode`: an unlinked `toggle_switch` passed `ZERO_IDENT` to `Game.GetItem`, which throws rather than
  returning null (the `!= null` guard could never help).
- `Combat::CriticalFailure` ignored the `IsNoKnock` immunity (turrets, Horrigan, bodyguards, spore plants were
  knocked down); the flag is now stripped at entry so clients also stop playing the knockdown reaction.
- `Poker`: `NpcAction` advanced `MHod` twice when seats had folded, ending the betting round early — it now
  returns the seat that acts next; `ManyWinsCheck` compared a game-time lockout against real-time `Time::Days`.
- `Parameters::CritterSetPropertyQuests` built the Quest text-pack id by summing hashes into one numeric key,
  but the pack is two-token `{CritterProperty::X}{value}` — quest-update messages never fired. Now uses
  `MsgStr::PropPrefix`, matching the post-migration helpers.
- `MirelurkCombat`: the move-out emote fired once per search iteration and `GetFreeHex` was called with radius 0.
- `MapArroyoRaydersCamp`: the XP actually granted was 10 higher than the amount reported to the player, in both
  quest stages (duplicated round-up expression).
- `Caravan::IsAppear` used `<` against the inclusive `Game.Random(1, 100)`, so 100%-chance loot appeared 99% of
  the time and 1%-chance loot never appeared; `NpcPlanes` go-home passed a toggled 0/1 facing instead of `HomeDir`.

**Deferred (owner decision — these are feature/data work, not regressions):**

- `Item::ChangeProto` is an unimplemented `TODO` stub that returns its input unchanged, while `Sandbag` and
  `EnergyBarier` assign its result expecting a different proto. Implementing it means destroying and recreating a
  persisted map item, which can break handles held elsewhere (e.g. the barrier's `Blockers` registry) — it needs an
  ownership/migration decision rather than a blind fix.
- `Resources::MakeDataKey` silently drops its `pid` argument, so different-proto sceneries on one hex share a
  single depletion counter (each yields about half its intended resources). Mixing the proto into the key orphans
  every existing `Map.ResourcesData` entry, and orphans are never erased — so this needs a migration that clears
  the property, not just a code change.

**Verification:** Compile AngelScript (0 warnings) → formatter idempotent (changed 0) → quality ratchet →
nullable ABI validator → bake (the `.fodlg` change is baked content) → `TLA_Server`, `TLA_ServerHeadless`,
`TLA_Client` builds without warnings → live script harness **64 passed, 0 failed, 0 skipped** → headless reached
`Start server complete!` with no exception, sync, assertion or fatal marker. The native suite passed
**356029 assertions in 346 test cases**, exit 0. Not committed (owner reviews).

Playtest additions from this pass: workbench charge economy, the Den racing quest end-to-end, sniper/terminator
assist behaviour, poker betting rounds, and caravan loot rates.

### R3 wave 3 — the previously unhunted modules (2026-07-19)

A third workflow hunted the ~254 modules that had had no R3 deep pass (client bootstrap/HUD, mapper, text,
critter actions, drugs/perks, economy, items, maps, AI support, mobs, guards, events, replication, quests,
dialogs, devices). The session limit again killed part of the verify phase (178/398 agents), but **38 candidates
survived unanimous verification** (36 at full 3-vote, 2 at 2-vote). The unverified remainder is recovered from the
journal and re-queued for the next pass.

**A self-inflicted regression fixed first.** The earlier `GetPlanes(...)` out-parameter fix (`planes.clear();
planes.insertLast(...)`) broke the ~8 call sites that pass `null` as the out-array to use only the count
(`GetPlanes(guard, null)` in GuardLib, GameEventReplicator, NcrInvasion, EncounterNpc, SlaversHunt,
PatternMedic). All three overloads now take `NpcPlane[]? planes` and guard the fill. Covered by a new
`Test_NpcPlanes::get_planes_null_out` regression (negative-control verified). **Also**: the first-session
`OnNpcPlaneBegin` polarity flip had missed **WarehouseTurret** and **V13ZSoldier** (the grep was truncated at 20
lines) — under the new AddPlane contract both were inverted, so active warehouse turrets and V13 guardians could
never attack. Both flipped to match.

**Applied (contained, high-confidence):**

- **ClientMain freeze/grief.** `CritterAction` sent `Rpc_Wait(1200)` for *every visible critter's* action, so any
  nearby NPC firing/reloading/looting stamped the local player's own `WaitEndTick` 1.2 s ahead and starved the
  action pump — a player in a firefight or crowd was continuously frozen, and any client could grief a bystander.
  Gated on `cr.IsChosen`. *critical*
- **Drugs null-array crash.** `DropDrugEffects` stored `null` into `AllActiveDrugEffects`, so the next drug use
  after any respawn/antidote dereferenced null. Now removes the key. *critical*
- **Repair re-break loop.** `DeteriorateItem` never set `IsBroken`, so a worn-out item re-ran the break block on
  every subsequent hit — cost repeatedly divided by 3, BrokenCount inflated to unrepairable. Now latches the flag. *critical*
- **GlobalMapFog 32-bit shift.** `SetFog` packed with a 32-bit shift while the property is `int64` and the map is
  28 wide (offset reaches 54), so the right ~43% of the world map was permanently black; also added the missing
  negative-coord guard both callers rely on. *critical*
- `MainPlanes`: `CTraceFirstCritter.Cr` was sticky (a rejected corpse/too-close critter was still returned as a
  burst blocker); `ValidateBurst` was called with the single-shot mode while deciding to switch to burst;
  `ChooseAim`'s "1/3 pick second-best zone" always converged on the max (dead diversification).
- `CritterActions`: `Attack` accepted an unvalidated client aim value (free aimed shots + out-of-range crit-table
  reads) — now range-checked and masked; `ReloadWeapon` unload called `AddItem` with count 0 on an empty weapon
  (server exception).
- `ClientItems::BarterTransfer` double-subtracted the offer, blocking a second transfer from the same stack.
- `ClientMain` text/casing: age-bracket scan ran downward (wrong bracket, unrelated text for ages 14–15); the
  look description replaced `Max` but the pack uses `MAX` (max HP/ammo never shown); the inventory SPECIAL block
  used a summed-hash key (seven blank lines) — switched to the existing two-token helper.
- `Drugs`: stat-change messages built a summed-hash `@text` tag (blank stat name) — now the 3-token form; drug
  stage durations are game-minute table values but were scheduled with `Time::Seconds` (~3× too fast) — now
  `Time::GameMinutes`. *[drug pacing — playtest]*
- `Repair`: a successful repair left the `BrokenLow/Norm/High` severity flags set (item read as broken forever,
  next break re-applied the old severity) — factored a `ClearBrokenLevel` helper used by both repair and
  `SetDeterioration`.
- `MapTime`: the game-time offset truncated to int32, wrapping the in-game calendar backwards ~49.7 days every
  ~30 h of uptime — now built as a 64-bit `timespan`.
- `GameEventRacing::RacingWhen` always overwrote the "Никогда" fallback with a zero timestamp.

**Deferred — flagged for the owner (feature-work, cross-file migration, or serialized-contract change):**

- **`Item::OnCritterUseSkill` and `Resources::OnCritterUseOn` are never fired** (Item.fos:23, Resources.fos:380).
  These are whole dormant subsystems — wiring the events would activate ~18 sealed quest doors, the entire
  resource-gathering module, Navarro scanner/collar handlers, etc. The verifiers themselves note subscribers
  return `StopChain` unconditionally and need coordinated changes; this is feature activation, not a contained fix.
- **`ItemMovement` free-ammo exploit** (empty weapon refilled on every inventory entry): the correct fix moves the
  initial load to `OnItemInit(firstTime)`, a new event subscription — deferred to keep it deliberate.
- **MsgStr legacy hash keys** (MsgStr.fos:164/513/1155 — radio messages, the whole PipBoy quest tab, NPC look
  names/descriptions render blank): the known cross-file text-pack migration that also touches generated
  `GuiScreens.fos` + the owning `.fogui`, previously flagged as owner follow-up.
- **Radiation stage bookkeeping** (AffectRadiation/DropRadiation, Radiation.fos:106/126): permanent stat loss or a
  free permanent buff. The fix needs a redesign of how the applied stage is tracked (no `GetTimeEventData` API
  exists), so it is not a one-liner.
- **Repair `SetItemCost`** compounds a persistent per-instance cost discount that is never restored — the correct
  fix makes it a pure read-path accessor and must preserve `ReplicationTrader`'s authored per-instance prices.
- **Repairer stack loss** (whole hand stack destroyed, one item returned): needs a new `RepairItemCount` serialized
  property.
- **GMTown RPCs** (`Rpc_TransferToMap`/`Rpc_ShowTownView`/`Rpc_ShowGMTown`): an arbitrary-teleport map-unlock
  exploit on dead inbound RPCs with no client caller — the clean fix deletes the `ServerRemoteCall` surface, a
  network-contract change for the owner.
- **CritterIcons follow-icon** (CritterProps.fos:107 `FollowLeaderId` is `OwnerSync`, so the group-member icon is
  never drawn): the fix flips it to `PublicSync`, a serialized/network-sync contract change.
- **Hunter/Lourence barter** dead-locked by `IsBarterOnlyCash` + a buy whitelist omitting caps — a content/design
  decision on whether Lourence trades for caps or pelts.
- **Resources respawn** rebuilds the scenery proto id from a numeric uhash (over-caps regrowth), and `ToolAxe`
  grants count 0 on the last chop — both live only if the Resources module is wired (see the deferred event above),
  and the respawn fix additionally needs a persisted-time-event migration.

**Verification:** Compile AngelScript (0 warnings) → formatter idempotent → quality ratchet → nullable ABI →
bake → `TLA_Server`/`TLA_ServerHeadless`/`TLA_Client` builds without warnings → live script harness **65 passed,
0 failed, 0 skipped** (added `get_planes_null_out`) → headless reached `Start server complete!` with no exception,
sync, assertion or fatal marker. `git diff --check` clean. Not committed (owner reviews).

Playtest additions from this wave: general responsiveness in crowds/combat (the ClientMain freeze), drug
durations, NPC aimed-shot behaviour and burst decisions, warehouse-turret / V13-guardian aggression, weapon repair
display and severity, and world-map fog coverage.
