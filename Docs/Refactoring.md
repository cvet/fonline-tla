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
- **R2-3 — Tests.** Per the testing decision below. *(Status: blocked on owner decision.)*

## Testing strategy — decided (2026-06-20): B, lightweight harness

Owner chose tier **B**. Port a compact `Testing.fos` from lf-7 down to TLA's systems
(RegisterTest / Expect / Pass / Fail + fixtures: isolated location, spawn NPC/player/item,
cleanup with leak check), gated by a `Testing.Enabled` setting, plus a `Launch :: Tests`
task. Then `Test_*` suites starting with pure helpers (Reputation, Math/Flags, GameTime,
WeaponHelpers), growing into critical server flows. Done as phase R2-3 after the polish
batches establish stable module shapes.

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
