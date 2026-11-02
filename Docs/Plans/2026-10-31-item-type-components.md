# Item type components — implementation plan

> **For agentic workers:** use superpowers:subagent-driven-development or
> superpowers:executing-plans task by task; steps use `- [ ]` checkboxes.
> Project rules in [AGENTS.md](../../AGENTS.md) override generic workflow steps:
> no `git add`, commit or push. A task ends with its ledger entry, not a commit.

**Goal:** Replace the `ItemType` enum/`Item.Type` property and the flat
`<Kind>_<Field>` item properties with engine property components
(`///@ Property Item Common bool <Kind> Component` plus `<Kind>.<Field>`), used as
`item.Has<Kind>` / `item.<Kind>.<Field>`, without gameplay changes and without
losing authored or saved data.

**Architecture:** One component per former kind that owns behavior or data
(Armor, Drug, Weapon, Ammo, Key, Container, Door, Grid, Car) plus Locker and
Lockpick. Kinds without a capability (None, Wall, Generic, Misc) become the
absence of a component and are classified by a small Common `ItemKinds` module
over components and engine flags. Work proceeds in batches; `Item.Type` remains
declared and authored until Task 7, and a content validator enforces
`Type = X` ⇔ `X = True` meanwhile. Persisted flat names migrate through
`///@ MigrationRule Property Item Rename|Remove`.

**Tech stack:** AngelScript (`Scripts/*.fos`, embedded `Gui/*.fogui` code),
INI-like `.foitem`/`.fomap`, Python 3 tools, FOnline Engine (unchanged).

**Spec:** owner request, 2026-10-31: «Перенимаем лучшие практики из проекта Last
Frontier (~/lf-10). Переводим типы с енума и нотации e.Type_Name на компоненты
(///@ Property ... Component): e.Type.Name.» The evidence and decisions below are
the design; this file is both spec digest and plan.

**Status:** implemented 2026-11-01; committed on `master` at the owner's request 2026-11-02. Open: Task 8
Steps 2–3 manual acceptance (Mapper inspect/save, SkillBox scenery cursor, exit-grid,
drug and car-selection paths limited by pre-existing defects D1–D4).

**Baseline:** root `d7561fd5`, Engine `629ea6f5` (equals the committed pin), both
trees clean at planning time. Planning probes:
`Workspace/item-type-components/` (ignored).

## Evidence

### Current TLA state

- `Scripts/GameEnums.fos:422-434` declares `ItemType` None, Armor, Drug, Weapon,
  Ammo, Misc, Key=7, Container, Door, Grid, Generic, Wall, Car=13.
  `Scripts/ItemProps.fos:186` declares `ItemType Type Mutable PublicSync Persistent`;
  `:189` declares `ItemType Grid_Type`.
- 111 flat prefixed Item properties, all `Persistent`: `ItemProps.fos` 96 (Weapon
  57, Armor 18, Ammo 5, Car 9, Grid 4, Lockpick 2, Container 1) and
  `Lockers.fos:15-31` 15 (Locker 5, Door 7, Container 3). Related flags:
  `Car.fos:11-12` `CarIsBioEngine`/`CarIsNoLockpick`, `ItemProps.fos:137` `IsLockpick`.
- Existing components: Item `Radio` (`Radio.fos:17`), Critter `DialogContext`
  (`Dialogs.fos:19`). Critter/Map/Location/Game have no `<Kind>_<Field>` groups;
  `BehemothParam_1/2`, `ChildPid_0..4`, `ChildLines_0..4` are numbered, not kind prefixes.
- Script consumers outside `Scripts/Generated/` and declarations: 156 `ItemType::`
  occurrences on 134 lines in 50 files; 23 property filters
  `(ItemProperty::Type, ItemType::X)` plus the Mapper panel row `MapperMain.fos:1781`;
  274 prefixed field references on 230 lines in 29 files; implicit `int type = item.Type`
  at `Collector.fos:101`, `EncounterNpc.fos:279`, `FixBoy.fos:772`, `GuardLib.fos:422`,
  `MapBarterGround.fos:265`, `Repairer.fos:81`, `RespawnItem.fos:53`, `Trap.fos:24`.
  `Scripts/Generated/GuiScreens.fos` mirrors 6 lines (8 occurrences) from
  `Gui/Game.fogui`, `Gui/GlobalMap.fogui`, `Gui/SkillBox.fogui`.

| Kind | `ItemType::` refs/files | Field refs/files | Largest field consumers |
| --- | --- | --- | --- |
| Weapon | 59/24 | 174/17 | WeaponHelpers 42, ClientMain 26, MainPlanes 24, ChosenActions 14 |
| Container | 27/17 | 4/2 | Lockers, CritterActions |
| Door | 18/13 | 0 | — (all `Door_*` are dead declarations) |
| Armor | 12/9 | 20/2 | Parameters 15, ItemMovement 5 |
| Key | 10/8 | — | Lockers, NrTRay |
| Car | 8/5 | 26/8 | GlobalmapGroup 12, NrTRay 4 |
| Ammo | 7/7 | 27/5 | Combat 19 |
| Grid | 6/5 | 13/4 | Main 5, Entrance 3, MapperMain 3 |
| Drug | 4/4 | — | GuardLib, GameEventStorehouse |
| Generic / Misc | 3/3, 2/2 | — | GUI skill cursor, Mapper; NcrCommon, RespawnItem |
| Locker / Lockpick | — | 10/3, 0 | Lockers, AiControl, MapperMain |

- Authored content: 2827 `Type =` lines in `Items/`. Effective kinds after `$Parent`
  resolution: Weapon 137, Container 122, Door 118, Grid 54 (24 inherit
  `exit_grid`), Drug 29, Ammo 28, Armor 23, Key 8, Car 7, Misc 343, Generic 1980,
  Wall 1766 (`base_wall`), None 3641 (tiles). No child overrides an inherited
  `Type`; no proto has several parents.
- Flat keys: `Items/` Weapon_ 3180, Armor_ 280, Container_ 223, Ammo_ 106, Car_ 58,
  Grid_ 27 (all `Grid_Type`), Locker_ 7. `Maps/`: 4835 Grid lines in 274 files
  (`Grid_ToMapEntry` 3831, `Grid_ToMap` 545, `Grid_ToMapDir` 459). Critters/dialogs/
  texts reference none.
- Partition of current content: Wall ⇔ `IsWall`; None ⇔ tile protos (`IsTile` via
  `base_tile`); Generic ∪ Grid ⇔ `Static && !IsWall && !IsTile`; every other kind
  is non-static.
- `Grid_Type` is a misdeclared Fallout grid subtype. Initial history stored 2..5;
  the `ItemType` typing turned them into enum names. Art confirms the meaning:
  `Drug`(2) stairs (`grid_2068` VSTAIR), `Weapon`(3) ladder (`grid_2139` LADDER),
  `Ammo`(4) ladder down/hole (`grid_2977` LADRDWN), `Misc`(5) elevator
  (`grid_3655` ELEV01). No script reads it; all 27 protos are static.
- No `ItemPropertyGroup::` consumer; `Group =` tags only steer formatter order.
- AiControl item JSON (`AiControl.fos:1826-1844`, [protocol](../AiControlProtocol.md))
  publishes `hasContainer`, `hasDoor`, `hasLocker`, `lockerLocked`… — keys stay.
- Touched namespaces in `AngelScript.MutableGlobalsAllowedNamespaces`: EncounterNpc,
  FixBoy, GameEventCaches, GlobalmapGroup, GuardLib, InputHandler, MapperMain,
  Maps, NcrCommon, NpcPlanes, NrWriKidnap, Parameters, PatternSlayer,
  PatternSniper, Purgatory, Replication, Sandbag, SfCommon, Worldmap.
- Persistent providers JSON/SQLite are off by default
  (`Engine/BuildTools/cmake/stages/Init.cmake:73-74`); `TLA.fomain` uses
  `Server.DbStorage = Memory`.
- A DB document stores only differences from the proto
  (`Engine/Source/Server/EntityManager.cpp:1498-1501`). No script writes `Type` or a
  renamed field, so existing saves carry those keys only where a value diverged from
  its proto (for example after a proto edit).

### Engine contract (no Engine change needed)

- A marker is an unqualified plain bool (`Engine/Source/Common/Properties.cpp:2715-2719`);
  `A.B` splits into component and field (`:2554-2562`).
- AngelScript registers `<Comp>` getters and `Has<Comp>` on Item, AbstractItem,
  ProtoItem and StaticItem; the getter throws when the marker is false and returns
  the same entity (`Engine/Source/Scripting/AngelScript/AngelScriptEntity.cpp:220-245,1236-1260`).
- The property enum of `Weapon.Caliber` is `ItemProperty::Weapon_Caliber`
  (`Engine/Source/Common/MetadataRegistration.cpp:305`). Enum spellings in scripts
  stay; a flat and a qualified spelling of one name cannot coexist, so each batch
  swaps declarations atomically.
- Rename/Remove rules apply to stored text (protos, maps) and DB documents
  (`Properties.cpp:1356-1370,2416-2425`); a rename to a qualified target is covered by
  `Engine/Source/Tests/Test_MetadataBaker.cpp:993`. Retired names cannot be redeclared.
- Owners: [property components](../../Engine/Docs/en/how-to/content/prototype-format.md#property-components),
  [nullability of component accessors](../../Engine/Docs/en/contributing/coding-contracts/nullability.md).

### Last Frontier practice (`~/lf-10` at `b60676cc98`)

- `7b496b118a` (2018-10-06) «Типы предметов переведены на компонентную систему»:
  the same migration in AngelScript; consumers moved from `Type ==` to component
  presence; Drug/Misc briefly kept as field-less components.
- `94275c38c6` (#166): markers and filters `ItemProperty::Weapon`.
- Current `Scripts/Weapon.cs:17-59`, `Scripts/Lockers.cs:10-44`: marker and fields in
  one block of the owning module; authored config immutable, runtime state
  `Mutable`. `Docs/Properties.md#компоненты-свойств`: fields never enable a marker,
  `Has` before access, persisted fields need a Rename to the qualified name.
  `Docs/Prototypes.md`: an item base never enables a component.
  `Tools/MigrationGuard`: retired property names are never reused.

| LF practice | This plan |
| --- | --- |
| Marker + qualified fields, `Has<Comp>`, filters `ItemProperty::<Comp>, 1` | Adopted |
| Immutable markers; flags chosen per field | Adopted for markers; field flags kept (D7) |
| Rename persisted names, never reuse retired ones | Adopted (Task 1 manifest, Engine rejection) |
| Validator: fields require marker, marker not inferred | Adopted (Task 1) |
| One declaration block per component in its owner | Adopted (D9) |
| LF names (MapExit, Transport, Medicine) | Not adopted: TLA names stay ([AGENTS.md](../../AGENTS.md)) |
| Runtime weapon state in component, arrays for modes, no base-enabled markers | Deferred (Out of scope) |

## Decisions (accepted 2026-10-31)

| ID | Decision | Recommendation |
| --- | --- | --- |
| D1 | Component set and names | Armor, Drug, Weapon, Ammo, Key, Container, Door, Grid, Car, Locker, Lockpick — TLA names. |
| D2 | Kinds without capability | None → absence (tiles: `IsTile`); Wall → engine `IsWall`; Generic and Misc → absence with `ItemKinds` predicates (exact on current content). Alternative: field-less `Misc`/`Generic` markers (LF 2018). |
| D3 | Kind invariants | Validator keeps the old single-kind rule: at most one of the nine kind markers; Locker ⇔ Door or Container; Grid only static; other kinds only non-static. Relax later deliberately. |
| D4 | Lock data | `Locker` marker on every Door and Container proto; `Locker.Locked/Jammed/Broken/NoOpen/IsElectro`. `LockerId`, `LockerComplexity`, `LockerCondition`, `Opened`, `IsCanOpen` stay flat: keys share `LockerId`. |
| D5 | `Grid_Type` | New `GridType` enum (None 0, Stairs 2, LadderBottom 3, LadderTop 4, Elevator 5); author `Grid.Type` values; `Remove Grid_Type` (static-only data). |
| D6 | Field names | Verbatim after the prefix, typos and `_0.._2` included (`Container.Changeble`, `Door.IsMultyHex`, `Weapon.CriticalFailture`, `Weapon.Skill_0`). |
| D7 | Flags | Markers immutable, `Common` (Lockpick `Server`, matching its fields); every field keeps its side/Mutable/Sync/Persistent flags. |
| D8 | `Group =` tags on moved fields | Drop (no `ItemPropertyGroup::` consumers; component replaces grouping). |
| D9 | Declaration layout | `ItemProps.fos`: Armor, Drug, Weapon, Ammo, Key, Grid, Lockpick, Car (incl. the two `Car.fos` flags). `Lockers.fos`: Container (incl. `MagicHandsGrnd` from ItemProps), Door, Locker. |
| D10 | Adjacent flags | `CarIsBioEngine` → `Car.IsBioEngine`, `CarIsNoLockpick` → `Car.IsNoLockpick` (Rename); `IsLockpick` → `Lockpick` marker (`Remove IsLockpick`: no writer, no authored value). |
| D11 | Save-compatibility evidence | Static rule coverage (Task 1) plus a private JSON-provider restart test with crafted legacy keys (Tasks 0 and 8). No production snapshot was provided; that remains a qualification limit. |
| D12 | Mapper property panel | Drop the `ItemProperty::Type` row; no marker rows; kind blocks keyed by `Has<Comp>`. |
| D13 | Non-weapon contract of `WeaponHelpers` | `IsWeapon{Primary,Secondary,Third}Available` return false without `HasWeapon`; per-use getters require a weapon, callers guard. |
| D14 | Delivery | Batches Tasks 2–7 with `Type` kept until Task 7, not a single big change. |

## Global constraints

- No `git add`, commit, push, Engine change or publication. Leave unstaged edits;
  record each task in the ledger. Re-anchor from this plan, source and diff after
  any handoff; preserve edits by others.
- Script comments and module headers are Russian; identifiers, metadata and keys
  English. Translate remaining English comments in every touched module and update
  its header when responsibilities or declarations move.
- For each touched namespace from the allowlist above: move its mutable state to an
  owner and drop it from the list, or add one module-header line explaining the
  global lifetime. Do not sweep untouched namespaces.
- Markers: `///@ Property Item <Common|Server> bool <Comp> Component`, no
  `Mutable`/`Persistent`/sync tags. Fields: `<Comp>.<Field>` with the old flags.
- Every removed or renamed persisted name gets a rule in `Scripts/Migration.fos`
  in the same task.
- Presence: `Has<Comp>`, never `== null`. Filters: `GetItems(ItemProperty::<Comp>, 1)`,
  `GetItemOnHex/GetItemInRadius/GetStaticItems(..., ItemProperty::<Comp>, 1)`.
- Behavior preservation: a read that was `0`/`false`/empty for other kinds becomes an
  explicit guard with that default only where other kinds legitimately reach it;
  elsewhere prove presence. No broad guards that hide invariant violations.
- GUI: edit `.fogui`, apply the identical edit to `Scripts/Generated/GuiScreens.fos`
  ([paired exception](../ContentWorkflow.md#gui-generation)); `Generate :: GuiScreens.fos`
  must then produce no further diff. Never hand-edit `Content.fos`, `VERSION`, baked data.
- Compiler, bake and native warnings are failures; never inflate the script-quality
  baseline. Do not overlap bake writers with running consumers.

## Review focus

1. A field read on an item without the component (formerly `0`/`false`) now throws
   mid-action: non-weapon in hand, use-mode cycling, armor paths, client HUD.
   Tests: Task 6 `non_weapon_active_item_paths`; Task 5 `non_armor_paths`; B5
   site tables.
2. A persisted document or old map keeps a legacy key with no rule; its value is
   silently dropped (magazine size, lock state, exit destination). Tests: Task 1
   `missing-migration-rule`; Task 8 restart with crafted legacy keys.
3. Map instance overrides (4835 grid lines) are rewritten wrongly; exits lead
   nowhere. Tests: Task 2 `grid_map_overrides`; validator `field-without-marker`.
4. Client-only branches (ammo counter, skill cursor on scenery, car selection) are
   invisible to the headless harness. Test: Task 8 ordinary visible actions.
5. Category predicates for new content: a non-static item without a kind marker is
   now Misc (it was None and excluded). Tests: Task 7 `item_kinds_partition`;
   validator `static-mismatch`; documented in Items.md.

## File map

| Path | Responsibility |
| --- | --- |
| `Scripts/ItemProps.fos` | Item property contract; component blocks per D9. |
| `Scripts/Lockers.fos` | Door/Container/Locker blocks and lock behavior. |
| `Scripts/GameEnums.fos` | `GridType` added; `ItemType` removed in Task 7. |
| `Scripts/Migration.fos` | All Rename/Remove rules. |
| `Scripts/ItemKinds.fos` (new, Common) | Category predicates replacing enum ranges. |
| `Scripts/Tests/Test_ItemComponents.fos` (new) | Suite `item_components`. |
| `Tools/ContentQuality/validate_item_components.py` (new) + test + `item_component_legacy_names.txt` | Content/migration contract. |
| `Tools/ScriptQuality/validate_scripts.py` | `legacy-item-kind` check (Task 7). |
| `Workspace/item-type-components/rewrite_components.py` (private) | One-shot key rewrite. |
| Consumers in `Scripts/`, `Gui/` | Listed per task. |
| Docs | Scripts, ScriptStyle, ContentWorkflow, Items, Combat, Character, World, Refactoring, BuildAndLaunch, Tools READMEs, [Docs index](../README.md). |

## Batch procedure (referenced by Tasks 2–7)

- B1 Add the task's tests to `Test_ItemComponents.fos`; run `Compile AngelScript`
  and expect failure on the missing `Has<Comp>`/fields.
- B2 Swap declarations and add rules.
- B3 Run `py -3 Tools/ContentQuality/validate_item_components.py --summary`; expect
  exactly the task's content errors (`transition-mismatch`, `legacy-prefixed-key`).
- B4 Rewrite content with the private script; format the rewritten files (`Format :: Prototypes`
  does not recurse into `Items/` subfolders, so pass them explicitly); validator
  reports 0. Review the diff for the task's files only.
- B5 Classify every field site of the task in
  `Workspace/item-type-components/sites-task<N>.tsv`: (a) presence proven by a guard
  or invariant → `item.<Comp>.<Field>`; (b) other kinds legitimately reach it →
  `item.Has<Comp> && …` or `item.Has<Comp> ? … : <old default>`. Then convert.
  Convert an `ItemType` site only when all its values belong to migrated kinds;
  mixed predicates wait for Task 7.
- B6 Constraints for touched modules (comments, headers, allowlist line).
- B7 `Format :: Scripts`; `Compile AngelScript`; `Bake Resources`;
  `Launch :: TLA_Tests [windows]` → `[Testing] COMPLETE` = baseline + new tests, no
  failures/timeouts, exit 0; `Analyze :: Script Quality (Ratchet)`;
  `Analyze :: Nullable All`; `Test :: Python Tools`; `Build :: TLA_Client` and
  `Build :: TLA_Mapper` when GUI or Mapper code changed.
- B8 Update owning docs; ledger entry with real results and limits.

Private rewrite interface (written in Task 2, extended later):
`py -3 -I Workspace/item-type-components/rewrite_components.py --root . --component <Comp> [--type-value <ItemType value>] [--locker] [--rename <Old>=<New>]... [--value-map <Field>:<Old>=<New>,...] [--drop-type]`.
It renames keys `^<Comp>_(\w+)\s*=` to `<Comp>.\1 =` in `Items/**/*.foitem` and
`Maps/*.fomap`, inserts `<Comp> = True` (and `Locker = True` with `--locker`) after
each own `Type = <value>` line, maps values, deletes `Type` lines with
`--drop-type`, and prints totals per kind of edit.

---

### Task 0: Baseline, decisions and inventory

**Files:** this plan; `Workspace/item-type-components/`.

- [x] **Step 1:** Re-anchor: `git status`, `git -C Engine status`,
  `git rev-parse HEAD HEAD:Engine`, `git -C Engine rev-parse HEAD`. Record SHAs and
  any foreign dirty files.
- [x] **Step 2:** Record owner answers for D1–D14; update affected tasks before work.
- [x] **Step 3:** Rerun `inventory2.py` and `consumers.py` from the private folder;
  numbers must match Evidence or be reconciled here.
- [x] **Step 4:** Baseline: `Configure :: Auto`, `Force Bake Resources`,
  `Launch :: TLA_Tests [windows]` (record COMPLETE counts), ratchet, `Analyze :: Nullable All`,
  `Test :: Python Tools`, `Build :: TLA_Client`, `Build :: TLA_Mapper`. Keep
  pre-existing failures separate from later results.
- [x] **Step 5 (D11):** configure a private tree
  `Workspace/item-type-components/build-json` with `-DFO_DATABASE_JSON=ON`
  (never change `Build/Auto` or `TLA.fomain`); build `TLA_ServerHeadless` only; run it
  on the current bake with `--ApplySubConfig LocalTest --Server.DbStorage "JSON <abs>/Workspace/item-type-components/db"`
  until `Start server complete!`, then stop it cleanly. A plain boot persists only
  `Game/1.json`; the fixture therefore registers a player and QA-teleports it to
  `arroyo` (embedded AiControl client), which persists that location with its maps,
  NPCs and items. Keep the DB for Task 8 and record which documents hold a weapon item
  and a container item. Loading migrates documents and writes the new keys back
  (`EntityManager.cpp:989-996`), so Task 8 can verify the result in the JSON files.

### Task 1: Component contract validator and conventions

**Files:**
- Create: `Tools/ContentQuality/validate_item_components.py`,
  `Tools/ContentQuality/test_validate_item_components.py`,
  `Tools/ContentQuality/item_component_legacy_names.txt`
- Modify: `Tools/ContentQuality/README.md`, `.vscode/tasks.json`
  (`Analyze :: Item Components` → `py -3 ${workspaceFolder}/Tools/ContentQuality/validate_item_components.py --summary`),
  `Docs/BuildAndLaunch.md` (task row), `Docs/Scripts.md` (new subsection
  "Property components"), `Docs/ScriptStyle.md` §6 (Russian), `Docs/ContentWorkflow.md`
  (quick reference: `<Comp> = True` + `<Comp>.<Field>`, markers only on protos)

**Interfaces — produces:**
- `validate(root: Path) -> list[Violation]`; `Violation(code: str, path: str, line: int, message: str)`;
  CLI `--root`, `--summary`; exit 1 on any violation.
- Components and fields are read from `///@ Property Item ...` in `Scripts/**/*.fos`
  (excluding `Generated/`). Proto values resolve like the baker: parents left to
  right, child last. Map instances are sections with `$Proto`.
- `KIND_COMPONENTS = ("Armor", "Drug", "Weapon", "Ammo", "Key", "Container", "Door", "Grid", "Car")`.
  A rule involving an undeclared component is inactive, so batches activate checks
  by declaring markers. Static means effective `Static = True` or the legacy
  `IsStatic = True` (Engine rename in `EntityProperties.h:116`).
- Codes: `legacy-prefixed-key` (`<C>_<F>` where `<C>` is a declared component),
  `legacy-type-key` (a `Type` key once `Type` is no longer declared),
  `transition-mismatch` (while `Type` is declared: effective `Type = X` ≠ marker `X`
  for declared kinds), `field-without-marker`, `marker-on-instance`,
  `exclusive-kind`, `locker-mismatch`, `static-mismatch`,
  `missing-migration-rule` (a manifest name no longer declared lacks
  `MigrationRule Property Item Rename|Remove`), `dangling-migration-target`.
- Manifest: the 115 baseline names (111 prefixed + `Type`, `CarIsBioEngine`,
  `CarIsNoLockpick`, `IsLockpick`), one per line, frozen after creation.

- [x] **Step 1:** Write pytest cases with `tmp_path` fixtures:
  `test_field_without_marker_is_error`, `test_inherited_marker_enables_child_fields`,
  `test_marker_on_map_instance_is_error`, `test_two_kind_markers_is_error`,
  `test_locker_requires_door_or_container`, `test_portable_kind_on_static_is_error`,
  `test_grid_on_dynamic_is_error`, `test_type_marker_mismatch_while_type_declared`,
  `test_type_key_after_type_removed_is_error`, `test_legacy_prefixed_key_for_declared_component_is_error`,
  `test_removed_legacy_name_requires_migration_rule`, `test_rename_target_must_be_declared`,
  `test_repository_is_clean` (runs on the real root, expects no violations).
- [x] **Step 2:** `py -3 -m pytest Tools/ContentQuality/test_validate_item_components.py -q` → fails (module missing).
- [x] **Step 3:** Implement the validator; generate the manifest from current declarations.
- [x] **Step 4:** Tests pass; `--summary` on the repository reports 0 (only Radio is declared).
- [x] **Step 5:** Conventions: Scripts.md (declaration, Has, filters, MigrationRule,
  no new `<Comp>_<Field>` or kind enums, validator); ScriptStyle.md (examples
  `item.HasWeapon`, `item.Weapon.MaxAmmoCount`); ContentWorkflow.md; README and task row.
- [x] **Step 6:** `Test :: Python Tools`, `Check :: Docs Links`, `git diff --check`; ledger.

### Task 2: Grid component (pilot)

**Files:**
- Modify: `Scripts/GameEnums.fos` (GridType), `Scripts/ItemProps.fos:189-192`,
  `Scripts/Migration.fos`, `Items/**` (30 markers, 27 values), `Maps/*.fomap` (4835 keys, 274 files)
- Modify consumers: `Scripts/Entrance.fos:270-277,321`, `Scripts/Main.fos:509-512`,
  `Scripts/Scenery.fos:35-69`, `Scripts/MapperMain.fos:1807-1811`. The mixed
  Generic/Grid GUI checks stay for Task 7.
- Create: `Scripts/Tests/Test_ItemComponents.fos`, `Workspace/item-type-components/rewrite_components.py`
- Docs: `Docs/World.md:27`

**Interfaces — produces:**
- `///@ Enum GridType None = 0`, `Stairs = 2`, `LadderBottom = 3`, `LadderTop = 4`, `Elevator = 5`.
- `///@ Property Item Common bool Grid Component`; `Grid.Type` (GridType, Common Mutable
  PublicSync Persistent); `Grid.ToMap`, `Grid.ToMapEntry` (hstring), `Grid.ToMapDir`
  (uint8), Server Mutable Persistent.
- Rules: `Rename Grid_ToMap Grid.ToMap`, `Rename Grid_ToMapEntry Grid.ToMapEntry`,
  `Rename Grid_ToMapDir Grid.ToMapDir`, `Remove Grid_Type`.
- Value map: Drug→Stairs, Weapon→LadderBottom, Ammo→LadderTop, Misc→Elevator.

- [x] **Step 1 (B1):** suite `item_components` with
  `grid_marker` — `Entrance`, `ExitGrid`, `grid_2068` have `HasGrid`; `_10mm_pistol`,
  `wall_5001` do not;
  `grid_subtypes` — `grid_2068` Stairs, `grid_2139` LadderBottom, `grid_2977` LadderTop,
  `grid_3655` Elevator, `Entrance` None;
  `grid_map_overrides` — `Testing::CreateTestLocation(ctx, Content::Location::arroyo)`,
  map `GetMap(Content::Map::arroyo)`: 16 `GetStaticItems(ItemProperty::Grid, 1)` items
  with non-empty `Grid.ToMap`, one of them `arroyo_garden`;
  `Entrance::MapGetAllEntries(map).length() == 7`;
  `Entrance::MapGetEntryCoords(map, "51".hstr(), 0, hex)` is true.
- [x] **Step 2 (B2–B4):** declarations, rules; validator shows 54 `transition-mismatch`
  plus 27 + 4835 `legacy-prefixed-key`; rewrite with
  `--component Grid --type-value Grid --value-map "Grid.Type:Drug=Stairs,Weapon=LadderBottom,Ammo=LadderTop,Misc=Elevator"`
  (expect 27 + 4835 renames, 30 markers); format; validator 0.
- [x] **Step 3 (B5):** `Type == Grid` → `HasGrid`; fields → `Grid.*`. Mapper block
  keyed by `item.HasGrid`; `ItemProperty::Grid_*` spellings unchanged. `Main.fos:509`
  receives any scenery: `targetScen.HasGrid && targetScen.Grid.ToMap != EMPTY_HSTRING`.
- [x] **Step 4 (B6–B8):** run the batch checks; ledger.

### Task 3: Lockers family — Container, Door, Locker, Key, Lockpick

**Files:**
- Modify: `Scripts/Lockers.fos:10-31`, `Scripts/ItemProps.fos` (Key, Lockpick;
  move `Container_MagicHandsGrnd` out), `Scripts/Migration.fos`, `Items/**`
- Consumers (`ItemType::Container/Door/Key` sites that are not mixed, all
  `Container_/Door_/Locker_/Lockpick_` fields): Lockers, CritterActions, AiControl,
  MapperMain, Item, FixedItemFrame, Sandbag, Trap, Maps, Collector (filters),
  Purgatory, GameEventCaches, EncounterItems, RespawnItem (filter), ReddGates,
  ElectronicLock, Worldmap, Main, MainPlanes, NpcPlanes, NrTRay, ClientMain,
  NcrCommon (container part)
- Docs: `Docs/Items.md:57-95,170-175`

**Interfaces — produces:**
- `Lockers.fos`: `Container` marker; `Container.Volume`, `Container.Changeble`,
  `Container.CannotPickUp`, `Container.MagicHandsGrnd`; `Door` marker;
  `Door.NoBlockMove/NoBlockShoot/NoBlockLight` (Common), `Door.IsMultyHex`,
  `Door.MultyHexLine1/2`, `Door.BlockerIds` (Server); `Locker` marker;
  `Locker.Locked/Jammed/Broken/NoOpen/IsElectro`. Flags as today.
- `ItemProps.fos`: `Key` marker; `Lockpick` marker (Server); `Lockpick.Points`, `Lockpick.IsElectro`.
- Rules: 18 Renames (`Container_*` 4, `Door_*` 7, `Locker_*` 5, `Lockpick_*` 2), `Remove IsLockpick`.
- AiControl: `hasContainer = item.HasContainer`, `hasDoor = item.HasDoor`,
  `hasLocker = item.HasLocker`; comment `AiControl.fos:1828-1830` rewritten.
- `Container || Door` predicates become `HasLocker` only where the block reads lock
  state; otherwise `HasContainer || HasDoor`.

- [x] **Step 1 (B1):** `locker_family_markers` — `chest`: Container + Locker, not Door,
  `Container.Volume == 250`, `Container.Changeble`; `door_2002`: Door + Locker;
  `blue_pass_key`: Key, no Locker; `gravesite_1`: `Locker.NoOpen`; `alien_forward`:
  `Container.MagicHandsGrnd && Container.CannotPickUp`; `_10mm_pistol`: none.
- [x] **Step 2 (B2–B4):** rewrite Container (`--type-value Container --locker`), Door
  (`--type-value Door --locker`), Key, Locker keys; expect 122+122, 118+118, 8 markers;
  223 + 7 key renames; validator 0.
- [x] **Step 3 (B5–B8):** consumers; existing container-transfer tests in
  `Test_CritterActions` pass; batch checks; ledger.

### Task 4: Car

**Files:** `Scripts/ItemProps.fos` (Car block), `Scripts/Car.fos:11-12` (move flags),
`Scripts/Migration.fos`, `Items/**`; consumers GlobalmapGroup, NrTRay, Car, Base,
ClientMain, NcrRatch, SfCommon, Worldmap, Replication, Main, Maps, `Gui/GlobalMap.fogui:1441`
+ mirror; `Docs/World.md:96-102`.

**Interfaces — produces:** `Car` marker; `Car.Speed`, `Car.Passability`,
`Car.DeteriorationRate`, `Car.CrittersCapacity`, `Car.TankVolume`,
`Car.MaxDeterioration`, `Car.FuelConsumption`, `Car.Entrance`, `Car.MovementType`;
`Car.IsBioEngine`, `Car.IsNoLockpick` (Server Mutable Persistent). Rules: 9 + 2 Renames.

- [x] **Step 1 (B1):** `car_component` — `hummer`: Car, `TankVolume == 12000`,
  `MaxDeterioration == 50000`, `Speed == 80`; `bike`: `Speed == 120`; `_10mm_pistol`: none.
- [x] **Step 2 (B2–B8):** 7 markers, 58 renames; existing `Test_GlobalmapGroup`; batch checks; ledger.

### Task 5: Ammo, Armor, Drug

**Files:** `Scripts/ItemProps.fos`, `Scripts/Migration.fos`, `Items/**`; consumers
Combat, MainPlanes, ChosenActions, ClientMain, NpcPlanes, CritterActions,
PatternCommon, Parameters, ItemMovement, Main; docs `Docs/Character.md:43-45`,
`Docs/Combat.md:122,213-222`, `Docs/Items.md:57,165-170`.

**Interfaces — produces:** `Armor` marker + 18 `Armor.*`; `Ammo` marker +
`Ammo.Caliber/AcMod/DrMod/DmgMult/DmgDiv`; `Drug` marker. Rules: 23 Renames.

- [x] **Step 1 (B1):** `armor_ammo_drug_components` — `combat_armor`: `Armor.AC == 20`,
  `Armor.DRNormal == 40`, `Armor.CrTypeMale == "art/critters/hmcmbt".hstr()`;
  `default_armor`: Armor; `_10mm_jhp`: `Ammo.Caliber == Caliber::Bullet_10mm`,
  `DrMod == 25`, `DmgMult == 2`, `DmgDiv == 1`; `antidote`: Drug only;
  `abnormal_brain`: none. `non_armor_paths` — for each Armor field site reachable
  with a non-armor item (from the call-site audit), drive it with `abnormal_brain`
  and assert the old default result and no exception.
- [x] **Step 2 (B2–B8):** 23 + 28 + 29 markers, 280 + 106 renames; existing
  `Test_Combat`, `Test_Parameters`; batch checks; ledger.

### Task 6: Weapon

**Files:** `Scripts/ItemProps.fos`, `Scripts/Migration.fos`, `Items/**`; consumers
WeaponHelpers, ClientMain, MainPlanes, ChosenActions, Combat, NpcPlanes,
CritterActions, Parameters, ItemMovement, VcGuardsman, Main, Trap, Animation,
NrWriKidnap, PatternSlayer, PatternSniper, FighterQuest, GuardLib (weapon-only
parts), V13GuardLib, DropMenuHandler, InputHandler, GuiScreensExt, Repairer
(non-mixed parts), `Gui/Game.fogui:2482,2622,3104` + mirror; docs `Docs/Combat.md`,
`Docs/Items.md:52-64,159-164`.

**Interfaces — produces:** `Weapon` marker + 57 `Weapon.*` (names per D6); 57
Renames. `WeaponHelpers` per D13; its availability predicates are class (b).

- [x] **Step 1 (B1):** `weapon_component` — `_10mm_pistol`: `MaxAmmoCount == 12`,
  `Caliber == Caliber::Bullet_10mm`, `DefaultAmmoPid == Content::Item::_10mm_jhp`,
  `StateAnim == CritterStateAnim::Pistol`, `Skill_0 == CritterProperty::SkillSmallGuns`,
  `DmgMin_0 == 5`, `DmgMax_0 == 12`; `default_weapon`: `Weapon.IsUnarmed`.
  `non_weapon_active_item_paths` — `SpawnTestNpc` on a test location, put
  `abnormal_brain` into the Main slot: `Animation::GetStateAnim(npc) == CritterStateAnim::Unarmed`,
  `WeaponHelpers::IsWeaponPrimaryAvailable(item) == false`, no exception.
- [x] **Step 2 (B2–B8):** classify about 230 sites before editing; 137 markers, 3180 renames; existing `Test_WeaponHelpers`,
  `Test_Combat`, `Test_CritterActions`; batch checks; ledger.

### Task 7: Remove `ItemType`

**Files:**
- Create: `Scripts/ItemKinds.fos`
- Modify mixed sites: `Collector.fos:101-102`, `EncounterNpc.fos:41,279-280`,
  `MapBarterGround.fos:265-266`, `RespawnItem.fos:53-54`, `GameEventStorehouse.fos:152`,
  `FixBoy.fos:772-773`, `Repairer.fos:81-96`, `GuardLib.fos:422+`, `NcrCommon.fos:838`,
  `MapperMain.fos:1781,1814`, `Gui/Game.fogui:92`, `Gui/SkillBox.fogui:363` + mirror,
  and every remaining `ItemType`/`.Type` item site; breadcrumbs
  `MapGeckCity.fos:676` and `ItemMovement.fos:162` keep their text with new identifiers
- Delete: `ItemProps.fos` `Type`; `GameEnums.fos` `ItemType`; 2827 `Type =` lines
  (`--drop-type`); add `Remove Type`
- Modify: `Tools/ScriptQuality/validate_scripts.py`, its test and README
- Docs: Scripts.md, ScriptStyle.md, Items.md (category rules), Refactoring.md
  (standing decision: kinds are components; retired names)

**Interfaces — produces (`namespace ItemKinds`, Common):**
- `bool IsPortableGoods(AbstractItem item)` — former `Armor..Key` range:
  `!item.Static && !item.HasContainer && !item.HasDoor && !item.HasCar`.
- `bool IsMisc(AbstractItem item)` — `IsPortableGoods` and none of Armor, Drug, Weapon, Ammo, Key.
- `bool IsSceneryObject(AbstractItem item)` — former Generic or Grid:
  `item.Static && !item.IsWall && !item.IsTile`.
- `bool IsGenericScenery(AbstractItem item)` — `IsSceneryObject && !item.HasGrid`.
- Mapping: ranges → `IsPortableGoods`; `RespawnItem` list → `IsPortableGoods && !HasAmmo`;
  `GetItems(Type, Misc)` → all items filtered by `IsMisc`; GUI → `!IsSceneryObject`;
  Mapper Generic → `IsGenericScenery`; `switch` on kind → `if` chains.
- ScriptQuality `legacy-item-kind` (ERROR): identifier `ItemType`, `ItemProperty::Type`,
  or `///@ Property <Entity> ... <Comp>_<Field>` for a declared component of that
  entity; component names also derived from `Component` declarations.

- [x] **Step 1 (B1):** `item_kinds_partition` — IsPortableGoods true for `_10mm_pistol`,
  `combat_armor`, `_10mm_jhp`, `antidote`, `blue_pass_key`, `abnormal_brain`; false for
  `chest`, `door_2002`, `hummer`, `Entrance`, `generic_2692`, `wall_5001`, `tile_ADB001`.
  IsMisc true only for `abnormal_brain`. IsSceneryObject true for `generic_2692`,
  `Entrance`, `grid_2068`; false for `wall_5001`, `tile_ADB001`, `_10mm_pistol`.
  IsGenericScenery true for `generic_2692`, false for `Entrance`.
  `respawn_validity` — items created on a test map: `_10mm_pistol` and
  `abnormal_brain` valid, `_10mm_jhp` and `chest` invalid for
  `RespawnItem::CheckItemValidToRespawn`. Python test for `legacy-item-kind`.
- [x] **Step 2:** convert mixed sites; then delete declarations, enum and `Type` lines;
  add `Remove Type`. Validator: `legacy-type-key` active and 0.
- [x] **Step 3:** `git grep -nE "ItemType|ItemProperty::Type\b|\b(Weapon|Armor|Ammo|Car|Door|Locker|Container|Grid|Lockpick)_[A-Z]" -- Scripts Gui Items Maps Docs`
  matches only `Docs/Plans/`, `Docs/History/` and `ItemProperty::<Comp>_<Field>` spellings.
- [x] **Step 4:** batch checks; ratchet unchanged; ledger.

### Task 8: Integration and acceptance

- [x] **Step 1:** stop task-owned processes; `Force Bake Resources`; `Verify :: All`.
  COMPLETE counts = baseline + new tests, no failures; `Format :: All` leaves no diff.
- [ ] **Step 2:** client + server (`LocalTest`), ordinary visible actions: equip and
  reload `_10mm_pistol` (HUD counter and max), wear `combat_armor` (appearance),
  science/lockpick on a door, a container and a scenery object, open a locked
  container with its key, use an exit grid and a stairs grid, choose a car on the
  global map, use a drug in sight of a guard. Clean exit code 0; no script exceptions.
- [ ] **Step 3:** Mapper: open `arroyo`, inspect an exit grid (`Grid.ToMap/ToMapEntry/ToMapDir`)
  and a container (`Locker.Locked`, `LockerId`, `LockerComplexity`); save a copy into
  the private folder: only qualified names, no marker keys on instances.
- [x] **Step 4:** AiControl JSON for a door, a container and a misc map item keeps
  the same keys and values as before the migration.
- [x] **Step 5 (D11):** copy `Workspace/item-type-components/db-baseline-copy`; in the
  copy add legacy keys to a map or container weapon document such as
  `Items/10000001252.json` (`"Weapon_MaxAmmoCount": 99`; NPC inventory items are
  re-rolled on restart), to the container document `Items/10000001140.json`
  (`"Locker_Locked": true`, `"Container_Volume": 999`) and retired keys (`"Type"`,
  `"IsLockpick"`, `"Grid_Type"`). Rebuild the private JSON tree from the new sources
  and start it on the copy: `Start server complete!` with no property load errors;
  after a clean stop the documents hold `Weapon.MaxAmmoCount: 99`,
  `Locker.Locked: true`, `Container.Volume: 999`. Restart once more: clean start, same
  values. Crafted documents are private test data only.
- [x] **Step 6:** reconcile docs and this plan; `Check :: Docs Links`; `git diff --check`;
  status of both repositories, gitlink unchanged; final ledger with limits.

## Out of scope (candidate follow-ups)

- LF runtime weapon state in the component: `AmmoPid`, `AmmoCount`, `Mode` →
  `Weapon.*` (81 script references, 922 authored lines).
- Weapon modes as arrays (`Weapon.Skill` instead of `Skill_0..2`): a shape change
  needing Transform rules.
- Other role flags: `IsHolodisk`/`HolodiskNum`, `IsTrap`/`TrapValue`, `IsBigGun`,
  `LockerId`/`LockerComplexity`/`Opened`/`IsCanOpen`, Deterioration group.
- `Format :: Prototypes` does not recurse into `Items/` subfolders (`RecursiveInput`
  unset), although the baker does.
- Owner decisions found during Task 5: server reload accepts ammo of any caliber
  (client checks it); any item can reach the Armor slot through `MoveInvItem`/
  `ChangeItemSlot` (reads are guarded and keep the old `aa.frm` model).
- Owner decision found during Task 6: `Parameters::SetWeaponMode` keeps the aim
  nibble for non-weapons (pre-existing behavior, preserved).
- Pre-existing defects found in Task 8 (reproduce from the old code, not fixed here):
  D1 the client move queue survives a map transfer, so `ChosenActions.fos:207` throws
  `Invalid toHex arg` after an exit grid to a smaller map; D2 drugs cannot be used on
  oneself (no `IsCanUse`); D3 guards never react to drug use (Main returns before
  notifying observers); D4 the GlobalMap ViewCar panel has no item source; D5 a script
  `throw` in a client RemoteCall handler stops the headless server (non-interactive
  error path → `RequestQuit`), for example reloading a full weapon through AiControl.
- `Items/vindicator_minigun.foitem`: `Weapon.DefaultAmmoPid = _7_7mm_caseless` names no
  proto (pre-existing; harmless today).
- `Lockpick` component has no authored marker and no reader (preserves the old dead
  `IsLockpick`/`Lockpick_*`); it stays at the old `IsLockpick` position, not after Grid.
- Dead data `ChildPid_*`/`ChildLines_*` on cars; typo fixes; immutability of
  authored fields; LF "no base enables a component"; full MigrationGuard manifests;
  critter feature-prefixed state (Merc, Behemoth, Caravan).

## Overall acceptance

- No `ItemType`, `Item.Type` or `<Comp>_<Field>` declaration, key or consumer remains.
- Every former kind maps to its marker or engine flag exactly on current content.
- All 115 retired names have rules; old maps and saves load with values.
- Harness, Python tools, ratchet, nullable chain and builds are green with no new
  warnings; AiControl checks pass; GUI and Mapper checks are partial (see the Task 8
  ledger) and need owner/player acceptance; limits are recorded.

## Decisions and verification ledger

2026-10-31: plan written from repository, Engine and `~/lf-10` evidence; no source
changed. Waiting for D1–D14. `Check :: Docs Links` 0 findings; `git diff --check`
clean. The file exceeds the 24 KiB review trigger on purpose: the owner asked for an
exhaustive plan, and evidence, decisions and tasks form one reading unit.

2026-10-31, owner: accept every recommendation and execute task by task.
Execution rulings: work in place on `master`, no commits; per-task review diffs are
private tree snapshots; delegation artifacts live in `Workspace/item-type-components/sdd/`.

Task 0 (baseline, root `d7561fd5`, Engine `629ea6f5` = pin, trees clean):
- Inventory probes match the per-kind table; Evidence prose counts corrected above.
- `Configure :: Auto` ok; `ForceBakeResources` ok (19 packs, no warnings);
  `TLA_ServerHeadless`, `TLA_Client`, `TLA_Mapper` built without warnings.
- Harness: `[Testing] COMPLETE: 116 passed, 0 failed, 0 skipped (of 116)`, exit 0,
  no script exceptions. Ratchet ok; nullable chain ok; `pytest Tools`: 192 passed,
  89 subtests.
- GUI generator at baseline produces no diff, so later tasks must leave it at zero.
- Private JSON tree (`build-json`, output `json-out`) built without touching shared
  `Binaries/` or `Baking/` (runs use `--Baking.PrebakeOnStartup False`). The headless
  server stops cleanly on CTRL_BREAK sent to its own console, not on Ctrl+C. Fixture
  DB `db-baseline-copy` holds `arroyo` (5 maps), 126 NPCs, 716 items and one player;
  no item document carries a legacy key (documents store differences only).
  NPC inventory items are re-rolled on restart; map and container items are stable.

Task 1: `validate_item_components.py` (10 codes), its tests and the frozen 115-name
manifest; `Analyze :: Item Components`; conventions in Scripts.md, ScriptStyle.md,
ContentWorkflow.md, Tools README. 16 new tests, `pytest Tools` 208 passed/89
subtests; validator on the repository: 0 violations; docs check 0 findings. Review
approved; four hardening notes parked (U+FFFD tolerance, Proto renames in `$Parent`,
manifest guarded by count/prefix only, no static-override instance test).

Task 2 (Grid pilot): `GridType` enum, `Grid` component (marker + `Grid.Type/ToMap/
ToMapEntry/ToMapDir`), 3 Renames + `Remove Grid_Type`; 30 markers, 27 subtype values,
4835 map keys in 274 files rewritten (pairing audit: every removed line has its
qualified counterpart, no line-ending change); consumers in Entrance, Main (guarded),
Scenery, MapperMain; new suite `item_components` (3 tests). Harness 119/119, exit 0;
compile, force bake, ServerHeadless/Client/Mapper builds clean; nullable chain ok;
validator 0. The ratchet exposed false positives (`Gui::Object.Grid`): ruling — the
`component-null-probe` check now takes names from declarations and skips receivers
declared with a non-entity type (ternary/bitwise operands are not declarations);
baseline unchanged, ratchet OK, `pytest Tools` 215 passed/89 subtests. Review
approved after one fix round.

Task 3 (Lockers family): `Container`, `Door`, `Locker` blocks in Lockers.fos
(`MagicHandsGrnd` moved in), `Key` and `Lockpick` (Server) markers in ItemProps;
18 Renames + `Remove IsLockpick`; markers Container 122, Door 118, Locker 240, Key 8;
230 key renames (pairing audit clean; maps had none). 22 modules converted (60 sites,
one class b: ElectronicLock passes doors to `ShowContainer`, now
`HasContainer && Container.Changeble`); 11 filters use `ItemProperty::<Comp>, 1`;
AiControl JSON unchanged. Allowlist header lines: GameEventCaches, Maps, NcrCommon,
NpcPlanes, Purgatory, Sandbag. Harness 120/120, exit 0; builds, ratchet, nullable,
pytest 215 clean; validator 0. Review approved. Open for Task 8: client door and
container animation, ordinary open/loot/lockpick, Mapper inspector.

Task 4 (Car): `Car` block in ItemProps (9 fields + `IsBioEngine`/`IsNoLockpick`
moved from Car.fos), 11 Renames; 7 markers, 58 key renames (pairing clean); 11
modules plus the GlobalMap.fogui/GuiScreens.fos pair (generator: no further diff);
37 sites, presence proven by origin (reviewer traced the GlobalProcess chain, NrTRay,
init scripts). Harness 121/121, exit 0; builds, ratchet, nullable, pytest 215 clean;
validator 0. Review approved. Open for Task 8: client car HUD and global-map selection.

Task 5 (Ammo, Armor, Drug): `Armor` (18 fields), `Drug`, `Ammo` (5 fields) in
ItemProps; 23 Renames; markers 23/28/29, 386 key renames (pairing clean). Class b
sites: five Armor reads reachable with a non-armor item in the Armor slot, guarded
with the old values (test `non_armor_paths` drives the real slot swap). Review found
that server `ReloadWeapon` accepted any item as ammo, so the loaded `AmmoPid`
invariant was not provable: ruling — reject non-ammo at the writer
(`reload_rejects_non_ammo`), caliber check left to the owner. Items.md fixes from Task 3
applied. Harness 124/124, exit 0; builds, ratchet, nullable, pytest 215 clean;
validator 0. Review approved after one fix round.

Task 6 (Weapon): `Weapon` marker + 57 fields (D6 names, `Group` dropped), 57 Renames;
137 markers, 3180 key renames (pairing clean). 251 sites classified, 8 class b with
the old defaults (ClientMain `ToHit` reached from the Aim/Cursor slot proto,
VcGuardsman, FighterQuest, NpcPlanes unarmed checks). `WeaponHelpers` availability
predicates return false without `HasWeapon` (D13). Client writes of
`HandsProtoItemId` run the server setter, which accepts only weapon protos.
`Animation::GetStateAnim` moved to common code (one definition); GuardLib dropped
from the mutable-globals allowlist (no namespace-level mutable state). Harness
126/126, exit 0; builds, ratchet, nullable, pytest 215, generator clean; validator 0.
Review approved.

Task 7 (remove `ItemType`): new Common `ItemKinds` (IsPortableGoods, IsMisc,
IsSceneryObject, IsGenericScenery); mixed sites converted (Collector, EncounterNpc,
MapBarterGround, RespawnItem, GameEventStorehouse, FixBoy, Repairer, GuardLib,
NcrCommon, MapperMain with the `Type` row dropped, Game/SkillBox GUI pair). Probe:
0 mismatches between old formulas and predicates over 8256 protos; the 343 unmarked
non-static protos are exactly the former Misc. Deleted the `ItemType` enum, `Type`
property and 2827 `Type =` lines (one line per file); `Remove Type` added.
ScriptQuality `legacy-item-kind` (ERROR) reports 0; ratchet baseline unchanged.
Harness 128/128, exit 0; force bake, builds, nullable, pytest 220, generator clean;
validator 0. Review approved; two wording fixes applied.

Task 8 (integration, 2026-11-01): force bake and all builds without warnings; native
tests 710 cases / 745471 assertions passed; harness 128/128; pytest 220; ratchet,
nullable, validator 0; `Format :: All` and the GUI generator leave no diff.
AiControl-driven ordinary actions with clean client/server exits: pistol equip,
unload and reload (HUD 0 → 12, inventory 12/12); `combat_armor` worn (AC 25, DR/DT equal
the `Armor.*` values); science/lockpick on a door, a container and scenery; a locked
container opened with its key; stairs transfer to `repl_bank_den`; the global map used
a given car. Partial: the exit-grid transfer happened but the client then hit D1;
drug self-use blocked by D2, guard reaction by D3; car selection panel by D4. Not
run: client SkillBox cursor branch, Mapper property inspection and save (no Mapper
automation; the Mapper opened `arroyo` and exited 0). AiControl JSON keys unchanged and
values consistent (no Task 0 capture to compare). Save compatibility: the private
JSON build loaded crafted legacy keys from the baseline DB and wrote
`Weapon.MaxAmmoCount: 99`, `Locker.Locked: true`, `Container.Volume: 999`; restart
clean with the same values; no property load errors. Engine gitlink unchanged.
Qualification limits: Windows only; AiControl commands instead of manual mouse play;
no production DB snapshot.

Final whole-change review (2026-11-01): ready to hand over; no Critical/Important
defects; all deferred minors triaged as follow-ups. The new `Ammo item isn't ammo`
throw matches the existing throws of the same RemoteCall; D5 (a throw in a client
RemoteCall handler stops the headless server) needs its own task before public
hosting. No push or Engine change. 2026-11-02: the owner asked to commit; one
local commit on `master`, not pushed.
