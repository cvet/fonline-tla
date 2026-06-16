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
`== null` probes (errors); banner tags, textpack magic ids, hand-rolled utils, Cyrillic comments,
redundant bool returns, commented-out code, file-too-large (warnings). Modes: `--summary`,
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

These need runtime checks, design decisions, or content/owner input and were deliberately not changed:

- **Idioms (low value):** textpack magic ids → named keys; flag-soups → enums; the few `any`/`double`
  `Tla::Clamp` call sites.
- **Migration debt (disabled subsystems):** racing event (`Main.fos` init commented out, plus a
  cross-file dialog property rename), `Caravan`/`GameEvent`/`NoPvpMaps` inits, lost `Say`/`SayMsg`
  player feedback, broken `CustomCall` hotkeys. Re-enabling needs to confirm *why* each was disabled.
- **Per-module backlog:** medium/low findings in `Build/_audit/`.

## Notes / lessons

- After relocating `///@ Property` declarations, run **Force Bake** — the incremental bake reports
  "baked 0 files" and leaves protos/maps on the old layout, producing transient startup errors.
- When creating a new domain module, verify the file does not already exist
  (`git cat-file -e HEAD:Scripts/<name>.fos`) before writing it — there is a pre-existing `GameTime`
  module; new metadata went into genuinely new files.
- Moved helpers that call symbols still resident in `Tla.fos` must qualify those calls (e.g.
  `Tla::MaxSkillValue`, `Tla::Max`); the compiler catches any that are missed.
