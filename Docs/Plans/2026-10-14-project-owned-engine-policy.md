# Project-owned animation and content policy implementation plan

Historical task plan. Its revision numbers, check counts, publication steps and
status describe that assignment only. Re-establish the current task's scope and
authorization using [AGENTS.md](../../AGENTS.md) and
[DocumentationMaintenance](../DocumentationMaintenance.md) before reuse.
No fresh acceptance or Git/publication permission is implied.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the game-specific animation choices, historical game contracts, themed assets, authored day palette, and condition-dependent path/render policy identified in the audit from the reusable Engine, preserving TLA behavior.

**Architecture:** Engine consumes explicit playback parameters, opaque project animation
identifiers, generic path obstacles, and generic flat rendering. TLA scripts and configuration own
the actual animation names, walk/run thresholds, death/knockout frames, obstacle lifecycle, colors,
and assets. Format importers and generic RPG entity lifecycle remain engine-owned.

**Tech Stack:** C++ engine, AngelScript game, Python build/documentation tools, CMake.

**Spec:** User's audit request and subsequent instruction to move all reported dependencies out of Engine, write the plan, and execute it; scope and decisions are recorded below.

## Global constraints

- Work in the existing dirty `H:/fonline-tla` checkout: this extends the already reviewed, uncommitted script-owned animation migration. Preserve its index and other owner changes. No staging, commits, pushes, reset, or new checkout.
- Keep `Dynamic` grids and the existing TLA gameplay and serialized numeric identifiers. Regenerate contracts, never manually edit generated API models.
- Native identifiers and formatting follow adjacent engine code; script comments are Russian, engine source/docs English with maintained Russian mirrors.
- Format loaders/importers stay in Engine. Generic inventory, entity conditions, networking, geometry and animation playback stay reusable engine capabilities.
- Tests exercise actual consumer behavior. Builds sharing `Build/Auto` run sequentially, coordinated by the controller.

## Review focus

- A project using arbitrary state/action numbers must retain its selected motion animation and freeze frame, including direction changes and one-shot actions.
- Dead/knocked-out TLA characters retain their current presentation, while another project can animate the same condition differently.
- Restored entities and every condition transition must have correct obstacle and flat-render properties before path/render consumers run.
- Mapper, AnimationViewer and baker use the project's explicit preview pair, including a pair other than 1/1 and a missing clip.
- Asset relocation preserves TLA font/icon paths without hidden dependencies on deleted Engine files; empty engine configuration stays usable.

## Task 1: Project animation identifiers and playback selection

**Files:** Engine `Common.h`, `Settings.inc`, `Client.h`, `CritterHexView.*`, `ModelInstance.*`,
`ModelInfoBaker.cpp`, `Mapper.cpp`, `AnimationViewer.cpp`; relevant engine tests; TLA
`Scripts/Animation.fos`, `Scripts/GameEnums.fos`, `Scripts/Tests/Test_FalloutAnimation.fos`,
`TLA.fomain`.

**Interfaces and decisions:**
- Native `CritterStateAnim` and `CritterActionAnim` retain only `None=0`; all removed values are project metadata in `GameEnums.fos` with their current numbers.
- Introduce neutral `CritterAnimationContext`: Default, Moving, MovingBack, TurnLeft, TurnRight, Action, Preview. These describe motion/dispatch context, not asset identifiers.
- Introduce neutral `CritterAnimationFlags`: None, Freeze, Movement. Freeze uses normalized time, Movement enables 2D root-motion evaluation independently of action identifier.
- Extend `OnCritterAnimationInit` to receive context and effective moving speed, and return flags, normalized time and playback speed in addition to state/action. Proposed native signature: `(ptr<CritterView> cr, CritterStateAnim& stateAnim, CritterActionAnim& actionAnim, nptr<AbstractItem> contextItem, CritterAnimationContext context, int32_t movingSpeed, CritterAnimationFlags& flags, float32_t& normalizedTime, float32_t& speed)`.
- Model locomotion callback receives the generic context/speed, and a project-selected state/action/playback factor. Remove `_isRunning` and native walk/run speed policy. Validate returned time/speed; do not silently invent another animation.
- `Animation.PreviewStateAnim` and `Animation.PreviewActionAnim` are neutral native configuration, default zero, shared by render/baker settings. TLA explicitly sets 1/1. Baker prioritizes that exact pair, then its generic available bounds; no heuristic recognizing Unarmed or Idle. Tools use the same pair.
- Move Render.WalkAnimBaseSpeed=60, Render.RunAnimStartSpeed=81, Render.RunAnimBaseSpeed=120 to script-defined settings, preserving existing TLA values and config keys.
- TLA Default context chooses its existing idle/death/knockout animation and freeze time; Action context preserves one-shot playback. Motion contexts select walk/run/back/turn according to TLA rules. Root-motion choice is set explicitly by the script.

- [x] Add behavioral regressions for arbitrary animation identifiers, preserved hook choice, freeze at a project-selected time, movement with a nonstandard action identifier, and configurable preview bounds.
- [x] Run the regressions against the previous implementation and record the expected failures.
- [x] Implement the neutral engine API and migrate TLA/subscribers/tests/examples; keep test animation constants test-owned.
- [x] Run focused native tests and AngelScript compilation. Check normal and dead/knockout/moving selections in script tests.

## Task 2: Project-owned path and flat-render decisions

**Files:** Engine `EntityProperties.h`, `Server/Map.*`, `Server/MapManager.cpp`,
`Client/MapView.cpp`, `Client/MapSprite.h`, relevant path/client tests; TLA
`Scripts/CritterState.fos` or a focused `Scripts/CritterPresentation.fos` and script tests.

**Interfaces and decisions:**
- Add generic mutable persistent PublicSync critter bool `PathfindingObstacle`, default false. Server path classification tests this property rather than `IsDead()`; rename `HasLivingCritter` to `HasPathfindingObstacle`.
- Add generic mutable persistent PublicSync critter bool `DrawFlatten`, default false. Drawing selects the flat critter layer from this property, never from Condition. Rename engine `DrawOrderType::DeadCritter=13` to `FlatCritter=13`; TLA may declare the old numeric alias if consumers require it.
- Move `DeadDrawNoFlatten` into TLA metadata with its unchanged bool property type and persistence. TLA owns `PathfindingObstacle = Condition != Dead` and `DrawFlatten = Condition == Dead && !DeadDrawNoFlatten`.
- TLA installs property setters and an OnCritterInit handler to apply the policy for newly created and restored critters. Verify setter timing against the engine property system; use the incoming value if setters run before assignment.
- Mapper applies the same project policy on map load and view initialization. Its generic property-text edits must execute normal setters/post-setters, including undo/redo; DrawFlatten changes update the layer without manual reapplication.
- Client movement/collision predicates use the generic obstacle where they formerly inferred collision policy from death. Explicitly named life-state queries/filter APIs remain generic RPG features.

- [x] Add regressions showing that a dead obstacle is avoided and a living non-obstacle is not, plus property-controlled flat rendering independent of Condition.
- [x] Observe expected failures before changing consumers.
- [x] Implement engine properties and TLA lifecycle/setters; add script coverage for creation/restoration and Alive/Knockout/Dead transitions.
- [x] Run focused native and script tests. Preserve path-cost semantics: obstacle adds configured detour, not a hard block.

## Task 3: Historical contracts and authored content

**Files:** Engine `Common.h`, `Settings.inc`, `Resources/Core/Fonts/Fallout.*`, `Resources/Radiation.*`, `BuildTools/package.py`, packaging tests/examples; TLA `GameEnums.fos`, `TLA.fomain`, authored resource directories.

**Interfaces and decisions:**
- Move `EngineInfoMessage::NetWrongTagSkill=1029` and `NetPermanentDeath=1049` into TLA enum metadata. Transport remains opaque and preserves both values.
- Engine View.GlobalDayColorTime and GlobalDayColor defaults become empty; TLA's existing explicit values remain. Neutral examples must supply their own curve if they compute day color.
- Use the existing Fallout descriptor and bitmap in `Resources/FOnline/fonts`, delivered by the `FOnline` pack with `RawCopy` for font descriptions. The descriptor uses the byte-identical `Default.png` bitmap. Application icons belong at `Resources/TLA.ico` and `Resources/TLA.png`, referenced by CMake and Android configuration respectively; remove duplicate copies. Keep authored assets in their owning project packs.
- Remove radiation icon fallback from native settings and package.py. An omitted Android.Icon leaves the generated platform launcher unchanged; a supplied icon retains validation and copying behavior. Remove obsolete engine/example/test dependencies on deleted assets, using project/fixture assets where appropriate.

- [x] Add/run a packaging regression proving absent icon performs no themed fallback and explicitly supplied PNG still populates all launcher density directories.
- [x] Move contracts/defaults/assets and update consumers. Verify hashes when copying binary assets.
- [x] Run package/docs configuration tests and bake TLA resources to prove font delivery.

## Task 4: Integration, documentation and final verification

**Files:** TLA `Docs/Animation.md`, `Docs/Systems.md`, plan; Engine EN/RU owning docs, migration notes, generated contracts, version/compatibility metadata and disposition ledger.

- [x] Update migration and owning docs for the exact final API, settings, properties, enum ownership and asset paths. Include previously uncommitted animation migration in the coherent final version.
- [x] Regenerate API/reference/settings/native inventories, translation descriptions and contract dispositions. Run docs_prepare, docs_validate, relevant Python tool suites and contract enforcement.
- [x] Format touched files, respecting required final blank lines. Run the authoritative Verify :: All chain from .vscode/tasks.json and resolve warnings/failures.
- [x] Run an ordinary client/server smoke with current baked resources, covering map load, walk/run/direction changes, animation previews and death/knockout presentation; inspect client/server logs and screenshots.
- [x] Obtain independent whole-change review; fix material findings and rerun affected checks.
- [x] Repeat the source audit excluding format loaders, distinguish remaining generic engine capabilities, and report changes and any unpassed gate without committing.

## Acceptance evidence and limitations

- `Verify :: All` before the resource distribution correction: GREEN — 588 native cases, 107 script tests, 156 project Python tests and 82 subtests; formatting changed zero files. Final whitespace-only native rebuild/bake also passed.
- Isolated 3D: GREEN — 684 cases / 735652 assertions; focused regressions 4 cases / 241 assertions. Independent source review approved after corrections.
- Actual client: functional GREEN — ordinary GUI walk80/run160, direction changes, reload consumes12 rounds, global-map telemetry, real FRM/death/prone/single-frame preview QA. Screenshots inspected. Timing remains RED due measured overruns; no thresholds or priorities were changed.
- Persistent restart: functional GREEN — the same account/critter loaded through ordinary login and OnCritterInit(false), restoring PathfindingObstacle=true/DrawFlatten=false from saved false/true. QA fixtures explicitly retain their parent locations/maps; normal location creation is unchanged.
- Mapper: GREEN — existing corpse map, actual Condition text edits and flatten override, screenshot, clean diagnostics and preserved cache.
- Documentation: docs_prepare, docs_validate412 pages and contract enforcement79 changes/43 required/0 missing passed. Final changed owning Python suites:146 tests/75 subtests passed; Codegen CMake:25 tests passed separately on Linux. Logs are recorded under `Build/project-owned-engine-policy/`.
- The optional broad Engine Python run was interrupted during unchanged vendor compilation after1697 passes/275 subtests, with31 failures/4 errors/146 skips. Current Codegen25, translation7 and sprite-root-motion regressions close27 of those stale-collected failures. Remaining unrelated checks include GameplayTestRunner, removed ExitApp fixture and the local Clang's unsupported Android warning option; no full-suite GREEN is claimed.
- Resource distribution correction: the existing `FOnline` pack now copies its font descriptions through `RawCopy`; identical font/ICO duplicates were removed, and `Resources/TLA.png` supplies the configured Android icon. BakeResources, current client/mapper builds and an actual Mapper smoke passed without warnings; old copies were removed from baked Core. Main-config formatting changed zero files.
- Native spacing correction after owner review: separated control-flow blocks and semantic stages in 11 source files. Comparing against the pre-correction snapshot confirmed that no nonempty source line changed. The Engine rules now explicitly require manual spacing review independently of formatter/diff checks. Functional suites were not repeated for these blank-line-only edits.
- No staging, commits or pushes were performed; implementation is reviewable in the dirty worktrees.
