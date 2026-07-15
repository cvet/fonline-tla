# The TLA Reanimation & Stabilization Plan

> Master plan to bring **FOnline: The Life After (TLA)** back into working order after years of
> dormancy, designed to be executed as a multi-stage, long-running campaign across many sessions.
> This document is the single coordinating plan; it **subsumes** [Docs/Refactoring.md](Refactoring.md)
> (the existing Scripts-only refactor) rather than duplicating it, and points at the existing tooling
> (`Tools/AiControlMcp/`, `Tools/ScriptQuality/`, `Tools/NullableEstimate/`) and docs as the
> machinery that executes it.

Audience: AI maintainers executing the revival. Read [AGENTS.md](../AGENTS.md) first for repository
practices, then this plan. Working language is Russian; this agent-facing doc stays English per the
repo convention.

---

## 1. Vision & Guiding Principles

### 1.1 The goal

A TLA install where a player can log in, traverse the world map, enter towns, talk to NPCs, accept
and complete quests across all regions, fight, trade, craft, use skills, and have the server run for
hours without exceptions. Concretely: **headless server reaches `"Start server complete!"` with zero
exceptions and stays clean under the `SOAK` profile (§2.2); the four currently-green quests stay
green; quest coverage grows region-by-region toward all 165 quest flags (denominated by
`catalog.yaml`); the three disabled subsystems (GameEvent, Caravan, BulletinBoard) are debugged and
re-enabled (probe-verified) or consciously retired; and the codebase reaches the polish/headers/
structure bar set by [Docs/ScriptStyle.md](ScriptStyle.md).**

This is a stabilization campaign, not a feature project. We are reviving what exists, not designing
new content.

**Out of scope (consciously excluded, so "done" is not silently blocked on them):**

- **Audio polish** — sound/music balance, missing audio events. Audio is `M` (manual) in the
  Section 6.1 matrix and stays that way; it does not gate any stage exit or the Definition of Done.
- **PvP fairness / balance** — PvP combat tuning and fairness are not part of reviving single-player
  and co-op flows; PvP is `M` in Section 6.1 and out of scope for "working order."
- **Rendering feel / visual polish** — GPU-dependent look, animation feel, layout aesthetics. We
  verify rendering only via golden-image diffs (regression, not improvement); subjective "feel" is
  out of scope.
- **New content** — no new quests, NPCs, maps, or items. We revive and stabilize the existing 165
  quest flags and existing systems only.

These exclusions are deliberate: a stage or the DoD is never blocked on an out-of-scope item. If an
out-of-scope item turns out to block a quest or a subsystem, it is logged in `Docs/KnownIssues.md`
and the quest/subsystem is marked `manual`/`blocked`, not held open indefinitely.

### 1.2 Hard constraints (non-negotiable; from AGENTS.md, Refactoring.md, owner decisions)

1. **Server-authoritative.** Gameplay state lives on the server. Client scripts are UI, input,
   presentation, and client-only probes. `Scripts/AiControl.fos` issues *commands* that go through
   the normal validated RPC flow. Some of those are **privileged QA commands** —
   `qa_set_prop`, `qa_set_game_prop`, `qa_give_item`, `qa_teleport_map/hex/global` directly mutate
   server state and are emphatically *not* normal gameplay. They are gated by
   `AiControl.AllowQaCommands` (**off in production**) and exist only for test/automation setup. The
   bridge therefore does grant elevated powers when `AllowQaCommands` is on; the discipline (see §5.2)
   is to reach quest prerequisites through real gameplay where feasible and treat `qa_set_*` setup as
   a documented shortcut, so the catalog can distinguish *verified end-to-end* from
   *verified-from-injected-state*.
2. **Behavior-preserving by default.** Refactors preserve behavior. Any behavior change must be a
   deliberate, code-verified bug fix with the original intent restored (check git history when
   load-bearing). Do not mask invariant failures with broad defensive fallbacks — assert or fail
   loudly.
3. **Never bulk-delete commented-out code.** Some commented blocks are migration breadcrumbs
   (Caravan/GameEvent/BulletinBoard inits, Fallout 2 reference logic). Surface and annotate with a
   reason; delete only per-block after reading git history.
4. **Comment language.** `.fos` code comments and the per-file header block are **Russian** (owner
   decision 2026-06-20). Serialized/contract names stay **English**: `///@ Property/Enum/Setting/
   Event/RemoteCall`, proto ids, text-pack keys, identifiers. Agent docs (`AGENTS.md`, `Docs/*` that
   are agent-facing) and native `SourceExt/` C++ stay English. Player-facing text follows the
   existing localized `russ engl` pack structure.
5. **Generated files are not hand-edited.** `Scripts/Content.fos` and `Scripts/GuiScreens.fos` are
   generated; `GuiScreens.fos` is regenerated from `Gui/*.fogui` via
   `Tools/InterfaceEditor/generate_gui_screens.py`. Any GUI code fix must be mirrored into the owning
   `.fogui` or it is lost on regen. `VERSION` is generated via `Tools/GenerateVersion`.
6. **Verify every step (warnings are failures).** Compile AngelScript (0 warnings) → Bake Resources
   (**Force Bake** after moving a `///@ Property`) → relevant `Build :: TLA_*` → for behavior
   changes run `TLA_ServerHeadless` to `"Start server complete!"`. Engine-facing native changes also
   run `TLA_UnitTests` (must stay 296/296).
7. **Engine is owned upstream.** `Engine/` is a pinned submodule. Report engine bugs upstream and
   cross-check `H:/lf-30` (and the active `lf-NN` sibling) for migration patterns; do not patch the
   engine in place for game behavior. The owner advances the submodule SHA.
8. **Do not commit/stage/push.** The owner reviews and commits. Never revert or overwrite dirty files
   you did not author; work with user changes if touched files contain them.

### 1.3 Operating posture

- **Document-as-you-go.** Durable docs (architecture, per-system, quest catalog, known issues) are
  produced alongside verification, in the same session, not deferred to an end sprint.
- **Triage before fix.** Categorize a defect (engine vs SourceExt vs Scripts vs content) and pick the
  narrowest correct layer before touching code.
- **Ratchet, don't regress.** Every quality dimension that is green stays green; baselines only move
  down.

---

## 2. The Standing Regression Gates

These gate **every** stage and every batch. A stage is not "done" until all applicable gates are
green. They are the contract that lets the campaign run for months without silent rot. **Which gates
apply to a given edit is set by the change tier (§2.1), not "all G1–G9 every time"** — that tiering is
what keeps the inner loop affordable instead of training the operator to skip gates. The
parameterized `SOAK` profile (§2.2) is the single definition of "soak clean" referenced throughout.

| # | Gate | Command / tool | Pass criterion | Scope |
|---|------|----------------|----------------|-------|
| G1 | **AngelScript compile** | `Compile AngelScript` | 0 warnings; `TLA_ASCompiler.log` / `Build/_errors.txt` clean | every script/content change |
| G2 | **Resource bake** | `Bake Resources` (Force Bake after `///@ Property` moves) | clean bake, 0 warnings; `TLA_Baker.log`, `Build/_bake.log` clean | every content/script change |
| G3 | **Target builds** | `Build :: TLA_Server`, `:: TLA_Client` (and `:: TLA_ServerHeadless`, `:: TLA_Mapper`, `:: TLA_Baker`, `:: TLA_ASCompiler` as touched) | 0 warnings; links; binaries produced | every code change |
| G4 | **Engine unit tests** | `Launch :: TLA_UnitTests` | 296/296 PASS | native/engine-facing changes, engine bumps |
| G5 | **Headless startup, 0 exceptions** | `Prepare :: TLA_ServerHeadless` then run `--ApplySubConfig LocalTest` | exactly one `"Start server complete!"`; 0 `EntitySyncException`/`Assertion`/`Fatal`. (The extended `SOAK` profile, §2.2, is the CI-side form.) | any server-side behavior change |
| G6 | **Script quality ratchet** | `Analyze :: Script Quality (Ratchet)` → `validate_scripts.py --ratchet` | no (check,file) pair above `Tools/ScriptQuality/baseline.json` | every `Scripts/*.fos` change |
| G7 | **Nullable contracts & native ABI** | `Analyze :: Nullable All` (`validate_nullable.py` plus focused tests/analyzers) | exact, no errors | every `?`/`ptr<T>`/`nptr<T>`-touching change |
| G8 | **Formatting** | `Format :: All` (or `:: Scripts`/`:: Prototypes`/`:: Main Config`) | no dirty files after format | before handoff |
| G9 | **Quest regression suite** | `tla_quest_runner.py` over the verified set | all green specs still green | content/script/dialog changes; nightly |

Notes:
- G9 starts at the four verified specs (`cassidy_letter`, `arroyo_mynoc_oil`, `den_smitty_robot`,
  `klam_vaccination`) and grows: each newly authored-and-verified quest spec joins the suite and must
  stay green thereafter.
- New `Scripts/*.fos` files have no baseline entries, so any violation in them fails G6 — keep new
  files clean.
- The baseline (`Tools/ScriptQuality/baseline.json`, ~299–284 violations: 149 commented-out-code, 56
  redundant-bool-return, 55 textpack-magic-id, 19 banner-tags, 11 file-too-large, 9 hand-rolled-utils)
  may only ratchet *down*, except commented-out-code preserved-breadcrumb and file-too-large
  split-deferred cases, which are annotated rather than forced.

### 2.1 Gate tiering by change class

Running the **full** G1–G9 set on *every* edit is economically impossible at campaign cadence
(160+ quest specs, ~16 refactor batches, nightly cycles) and, worse, it trains the operator to
silently skip gates. So the per-change gate set is **tiered by what the change touches**. Pick the
tier from the change class; the inner loop (§5.1) references these tiers.

| Tier | Change class | Required gates (inner loop) | Notes |
|------|--------------|-----------------------------|-------|
| **T0** | Pure spec/data edit — `tla_quest_runner` specs, `catalog.yaml`, `quest_critical_path.json`, doc-only, no `.fos`/native/content change | **G9** (quest regression) only | No compile/bake needed; the spec change *is* the test. |
| **T1** | Comment / header / format-only refactor in `.fos` (no behavior, no symbol rename, no `///@` move) | **G1** compile + **G6** ScriptQuality ratchet + **G8** format (+ **G7** if any nullable contract is touched) | No bake, no headless — behavior is provably unchanged. |
| **T2** | Behavior change, symbol rename, `///@ Property`/contract move, content edit, native change | **Full G-set** applicable to the surface: G1→G2→G3→(G4 if native/engine)→G5 headless→G6→G7→G8→G9 | The only tier that runs bake + headless in the inner loop. |

**Incremental-bake fast path.** Default to incremental `Bake Resources` in the inner loop. Reserve
**Force Bake** for two cases only: (a) a `///@ Property` move (proto/property layout changed), and
(b) the **nightly full bake** in CI that guards against incremental-bake staleness. Do not Force Bake
reflexively — it is the slowest gate in the loop.

**Push the expensive gates into CI (Track G), not the inner loop.** The full bake, the parameterized
soak (`SOAK`, §2.2), and `TLA_UnitTests` (G4, unless the change is native/engine-facing) run in the
nightly CI job, not on every edit. The inner loop stays cheap; CI catches what the tiered inner loop
deliberately defers. A T0/T1 change that lands green locally is still backstopped by the nightly full
bake + soak.

### 2.2 The SOAK profile (one number, referenced everywhere)

"Headless soak clean" and "multi-hour" appear in several stage exits and in the Definition of Done.
To keep them measurable rather than subjective, **SOAK is a single parameterized profile**, defined
once here and referenced by name from every stage exit and §8:

> **`SOAK` = run `TLA_ServerHeadless` for `N = 4` hours, with `M ≥ 100` NPCs active, rotating the
> active region across the populated towns (Arroyo → Klamath → Den → … ), and producing
> `0` unhandled exceptions (`EntitySyncException` / `Assertion` / `Fatal` / unhandled
> `runtime_exception`), with steady-state RSS (no monotonic growth).**

Any stage exit or DoD clause that says "soak clean" means exactly this `SOAK` run. `N` and `M` are the
knobs (raised for the Stage 4 extended/owner-playtest soak); the *clean* criterion — 0 unhandled
exceptions, region rotation, stable RSS — is fixed. The nightly CI soak job (Track G) runs `SOAK`.

---

## 3. Workstreams

Eight parallel tracks. They are not strictly sequential — within a stage, several advance together —
but each has dependencies that order it within the roadmap (Section 4).

### A. Systematic System Testing

**Objective:** Establish and maintain per-system smoke + behavior coverage via the AI control bridge,
and close the bridge-primitive gaps that block deeper testing.

**Tasks:**
- Build a per-system smoke matrix (Section 6.1) using the existing bridge commands documented in
  [Docs/AiControl.md](AiControl.md): movement, dialog, inventory, item-use, skills, combat, crafting,
  barter, screens, registration.
- Stand up the batch harness and aggregation: `tla_batch_quest_runner.py` + `aggregate_quest_results.py`
  (new, alongside `tla_quest_runner.py`), producing JUnit XML for CI.
- Close high-value bridge gaps in priority order: `qa_get_reputation` + faction observation (~50
  quests gate on rep), `chosen.effects`/`perks_active` observation (drugs/radiation/perk verification),
  `chosen.weight`/encumbrance, `qa_advance_time` (time-gated quests), worldmap travel/encounter
  observation. Each new command extends `SourceExt/ClientAiBridge.cpp` + `Scripts/AiControl.fos` +
  the MCP adapter, and follows server-authority (QA-gated).
- Per-mechanic regression suites beyond quests: combat (kill N mob types, verify exp/loot), barter
  (buy/sell at vendors, verify price math), crafting (N FixBoy recipes, skill gate + consumption),
  skills (first-aid/repair/science on targets).

**Tooling:** `Tools/AiControlMcp/` (smoke_ai_control_mcp.py, tla_mechanics_playtest.py,
tla_quest_runner.py), `save_screenshot` for golden-image diffs, `environment_query` for reachability.

**Dependencies:** Harness + gates (Stage 0). Bridge-primitive gaps must land before the quests/systems
that need them (faction rep before faction-gated quests; `qa_advance_time` before time-gated quests).

**Exit criteria:** Every system in Section 6.1 has at least one automated or partial-automated check;
the batch runner produces an aggregated pass/fail report; the priority bridge gaps are closed.

### B. Quest Coverage to All 165

**Objective:** Author data-driven `tla_quest_runner.py` specs for all automatable quests, region by
region, growing from 4 → toward 165, with non-automatable quests (time-gated escorts) consciously
marked `manual`.

**Tasks:** Execute the 17 region/cluster batches in Section 6.2 (which partition all 165 flags) using
the per-batch loop (Section 5.2). For each quest: identify giver NPC + map + hex, trace dialog with
`--trace-dialog` to extract Russian answer keywords, encode stage targets + `setup` prerequisites
(annotating injected setup), verify green, add to the regression suite. Non-automatable quests follow
the manual quest protocol (§5.6).

**Tooling:** `tla_quest_runner.py` (data-driven QUESTS dict; `Docs/quest_specs.yaml` data file) +
the **`--trace-dialog` keyword-extraction helper (a Stage-0 gated deliverable, §5.2 step 1)**,
`qa_teleport_map/hex/global`, `qa_set_prop`, `qa_set_game_prop`, `qa_give_item`, `qa_get_prop`
(Server-scope fallback for the ~63 Server-scope flags), `environment_query path` for
reachability/skip.

**Dependencies:** Track A harness **and the Stage-0 `--trace-dialog` + `catalog.yaml` deliverables
(Stage 0 gates Stage 2)**; Track C for content/code bugs that block a quest (e.g. `DenMomSlut` scope
mismatch, guard NPCs that never open dialog); faction-rep and time bridge gaps for the relevant
quests.

**Exit criteria:** Per region batch, all *automatable* quests are green and in the suite (counted
against `catalog.yaml`, the 165 denominator); every `manual` quest is `manual-verified` or
`manual-deferred` (§5.6); blockers are filed in `Docs/KnownIssues.md` and
`Tools/AiControlMcp/known_quest_issues.md`; the quest catalog (`Docs/Quests/catalog.yaml`) reflects
coverage status incl. verified-end-to-end vs verified-from-injected-state.

### C. Bug Triage & Fixing

**Objective:** Drive the headless server and live playtests to zero exceptions; resolve the documented
breakage backlog with verified fixes.

**Tasks (priority-ordered by the bug survey):**
1. **Re-enable the disabled subsystems** (the biggest playability blockers): debug the fresh-DB
   null-derefs in `GameEvent` (DeclareEvents), `Caravan` (`AddRoutePoint`/`CaravansInit`), and
   `BulletinBoard`, currently commented out in `Main.fos::start()`. This is owner-coordinated and is
   the gate for caravan escort quests and several game events.
2. **Async sync long tail (~114 conditional time events lacking `Sync::Lock...`).** Batches: 2 Item
   (`DeferredDestroyItem`, `AutoCloseDoor` in `Item.fos`), ~8 Map critter-iteration loops
   (`MapSfTanker.fos::TankerIdle`, Behemoth, Caravan guard loops), ~104 any-value GetItem/GetCritter
   sites. Add `if (!Sync::Lock...(x)) return;` covering the full entity set a callback touches.
   These fire only under conditions and throw `EntitySyncException` when they do.
3. **Content/data bugs:** `Bag N not found` (invalid critter `BagId` vs `BagsConfig.json`),
   `DenVirginIsAway` Property scope mismatch (`Game` decl vs `Player` demand) hiding an answer,
   guard NPCs (Arroyo Todd) that never open dialog, empty baked text in `repl_*` start-map dialogs,
   missing text id 3354 (`NrWriKidnap.fos:437`).
4. **Intermittent `Mob::Idle` "Null assignment to non-nullable handle"** — verify whether recent
   engine MT/sanitizer fixes resolved it; **scheduled as a concrete Stage-4 task** (confirm
   non-recurrence under the `SOAK` profile, §2.2), not left as an open question; audit the
   `TryGoHome → AddWalkPlane → AddPlane` chain in `Mob.fos`/`NpcPlanes.fos` if it recurs under `SOAK`.

**Tooling:** Tiered triage (Section 5.3): static (compile/bake/validators) → headless smoke →
bridge-driven exercise → targeted repro. Bug reports follow the survey's template (file/line/severity/
status/repro/snippet/suspected-fix/test-plan).

**Dependencies:** Track A harness for repro; owner coordination for subsystem re-enable (DB/serialization).

**Exit criteria:** The `SOAK` profile (§2.2) runs clean (0 unhandled exceptions); the documented
backlog items are CONFIRMED-fixed or RESOLVED-by-engine or consciously deferred with a logged reason.

### D. Refactoring (integrates Refactoring.md)

**Objective:** Carry [Docs/Refactoring.md](Refactoring.md) Round 2 to completion and execute the
god-module splits, behavior-preserving, without regressing gates.

**Tasks (Refactoring.md phases, mapped):**
- **R2-1 pilot** (pending): process 3–5 representative modules (Reputation, KlamCowboy, ClientItems,
  Combat, GlobalmapGroup) — header + Russian comments + structure per ScriptStyle.md + format + name
  cleanup + in-pass null/idiom fixes — get owner sign-off on the target look.
- **R2-2 per-domain batches** (blocked on pilot): ~16 batches, leaves first, core last (helpers →
  combat effects → equipment → client/GUI → critter → AI patterns → regional NPCs → maps → economy →
  quests → Worldmap → Caravan → Parameters → Main). 4–6 modules/batch.
- **R2-3 tests** (tier B harness): port `Testing.fos`, author pure-helper then critical-flow suites,
  gate on `Testing.Enabled`, run in CI.
- **God-module splits** (Phase 4 structural), in safe-order tiers: leaves (Poker, Combat→CombatCore/
  Effects/Tables, Flags, AnimHelpers) → domain (Worldmap 4–5 parts, Caravan 3–4, FixBoy+Parameters) →
  async/timer (GlobalmapGroup, NpcPlanes) → side/infra (ClientMain, MapperMain, AiControl) → core
  (Main, last). **Cross-cutting infra modules with no owning quest batch (Main, Worldmap, Caravan,
  NpcPlanes, Parameters) use the DIFFERENTIAL gate (§5.7): full quest-regression + `SOAK` before+after,
  diffed. Caravan is split bundled with its Stage-1 re-enable, or deferred until escort quests are
  green — never split independently (§5.7 double-exposure rule).** Save-safety: properties keyed by
  name not regIndex, so splits need no MigrationRule (confirmed in Phase 4); Force Bake after
  `///@ Property` moves.
- **Standing cleanups:** commented-out-code per-block triage (annotate, don't bulk-delete), Game.Log
  audit (diagnostic vs noise; prefix kept ones), redundant-bool-return mechanical fixes, banner-tag +
  header backfill (152/270 files lack headers).

**Tooling:** `Tools/ScriptQuality/` (validate_scripts.py, render_audit.py, baseline.json, `--ratchet`/
`--fix`), `Tools/NullableEstimate/`, `Build/_audit/` (38 group docs), `Format :: *`.

**Dependencies:** Pilot before batches; leaf splits before core; refactor of a system should follow
(or accompany) that system's test coverage so regressions are caught. For infra modules with no
owning quest batch, the §5.7 differential gate substitutes for "quests green first."

**Exit criteria:** R2-1/2/3 complete; all god-modules split (each infra split passed the §5.7
differential gate) or consciously deferred; baseline ratcheted down (headers 100%,
redundant-bool-return → ~0, banner-tags → 0); no gate regressions.

### E. Documentation

**Objective:** Produce the durable doc set the revival needs, document-as-you-go, each doc with a
steward.

**Tasks (new files under `Docs/`):** `Architecture.md` (engine/game split, authority, data flow,
subsystem map); `Systems/{Combat,Dialogs,Quests,Worldmap,AI,Crafting,Reputation,Economy}.md`
(contract + architecture + known issues + test coverage, written as each domain is refactored/tested);
`Quests/catalog.yaml` + `Quests/README.md` (all 165 quests: giver/stages/prereqs/test-status,
generated by a `Tools/QuestCatalog/generate_catalog.py` helper from CritterProps + dialogs + specs);
`ContentAuthoring.md` (how to add quest/NPC/dialog/map/item end-to-end); `TestingPlaybook.md` (bridge
setup, spec format, batch runner, troubleshooting — extracted/expanded from AiControl.md);
`KnownIssues.md` (live bug/gap register with severity/status/workaround). Cross-reference the new set
from `AGENTS.md` §Quick Reference and `README.md`.

**`catalog.yaml` is the single denominator.** `generate_catalog.py` is pulled forward into **Stage 0**
(not deferred to the doc sprint): its first job is to emit the authoritative quest inventory by
enumerating every `///@ Property Critter ... Group = Quests` flag — the **165** — and write one
`catalog.yaml` entry per flag (giver, region/batch, Max, scope, prereqs, and a `test_status` field:
`green` / `manual-verified` / `manual-deferred` / `blocked` / `untested`). Every "all quests" /
"all automatable quests" claim in this plan (Track B exit, §6.2, §8 #3) is measured **against
`catalog.yaml`**, so the denominator is generated from the repo, not asserted. The doc-prose layer
(`Quests/README.md`, the `Systems/*` quest doc) is still written later as the domains are covered.

**Tooling:** helper scripts (`generate_catalog.py`, doc link-checker, index generator).

**Dependencies:** Each system doc follows its Track A/D work; the quest catalog follows Track B.

**Exit criteria:** The end-of-run checklist in Section 8 is satisfied; a new contributor can read
`Architecture.md` + a system doc + `ContentAuthoring.md` and start fixing/authoring with confidence.

### F. Content Validation

**Objective:** Add the missing semantic-validation layer so content rot is caught at bake/startup,
not at runtime (or never).

**Tasks:** Build `Tools/ContentValidator/validate_content.py` (mirrors validate_scripts.py shape) with
tiers: **Tier 1 (fail build)** — proto-reference integrity (dialog DialogId, map NPC/item spawns,
critter inventory, caravan routes point at defined protos), text-key existence in *both* baked packs,
quest-property definitions referenced by dialogs; **Tier 2 (warn)** — dialog reachability, quest stage
≤ `Max` coherence, special answer-link `///@ Enum DialogAnswerLink` metadata presence, russ/engl
localization parity; **Tier 3/4 (info)** — quest property read/written coverage, orphaned protos/
dialogs/text keys. Integrate post-bake and optionally at headless startup
(`ValidateRuntimeConsistency`). Establish a baseline + ratchet like ScriptQuality.

**Tooling:** new validator + `Tools/ContentValidator/baseline.json`; `SourceExt/DialogBaker.cpp`
(today validates demand/result signatures only — does not check text keys or proto refs).

**Dependencies:** None hard; pairs naturally with Track B (quest authoring surfaces content gaps).

**Exit criteria:** Tier 1+2 checks run in the bake pipeline; baseline established; new content cannot
introduce dangling proto/text/quest references without failing.

### G. Tooling / CI / Automation

**Objective:** Make the gates enforceable in CI and the campaign resumable and measurable.

**Tasks:** Extend `.github/workflows/` with: a **smoke job** on every PR (bake → build → start headless
→ `smoke_ai_control_mcp.py`); a **nightly full bake + `SOAK`** (`schedule` cron; the `SOAK` profile of
§2.2 — `N=4h`, `M≥100` NPCs, region rotation, 0 unhandled exceptions, stable RSS); a **nightly quest
regression** matrix (region subsets in parallel → JUnit aggregation). This is where the expensive
gates deferred by the inner-loop tiers (§2.1) — full bake, `SOAK`, unit tests — are enforced. Add
`tla_batch_quest_runner.py` (with the required pre-batch hygiene + per-quest teardown features,
§5.2), `aggregate_quest_results.py`, `quest_critical_path.json` (15–20 core quests),
`known_quest_issues.md`. Wire fresh-server hygiene (rotate server per batch;
`InactivityDisconnectTime=0` gotcha → fresh name per client restart). Keep `validate_scripts.py
--ratchet`, nullable checks, and formatting in the PR `validate` job.

**Tooling:** GitHub Actions, the existing `.vscode/tasks.json` (authoritative task set),
`Build/_audit/` + `Build/_artifacts/` for progress artifacts.

**Dependencies:** Track A batch harness; the verified quest set for the regression matrix.

**Exit criteria:** PR pipeline enforces G1–G3, G6–G8; nightly enforces G5 + G9; reports land as CI
artifacts; the campaign progress log (`Build/_audit/progress.md`) is maintained per session.

### H. Engine-Update Upkeep

**Objective:** Absorb owner-driven submodule bumps with a deterministic protocol so engine churn never
stalls the campaign.

**Tasks:** On each bump, run the 7-step protocol (Section 5.4): inspect upstream + cross-check
`H:/lf-30`/active sibling → recompile → Force Bake → build toolchain → build targets → headless
startup → unit tests; fix fallout by category (new FIXED_SETTING in `TLA.fomain`, `///@ EngineHook`
rename in `SourceExt/`, core type/API/nullability change in Scripts, async-sync requirement, baker/
CMake `AddEngineSources` change, shader profile constraints). Note: engine default shader profile
`ps_4_0_level_9_3` forbids `gl_FragCoord`/position reads — keep engine `.fofx` within the minimal
profile; engine shader edits live in the submodule and must go upstream.

**Tooling:** git submodule, `Force Bake Resources`, all gates, `H:/lf-30/AGENTS.md` as migration
reference.

**Dependencies:** Runs out-of-band whenever the owner bumps; pauses other tracks until gates are
green again.

**Exit criteria:** After each bump, all gates green; engine SHA recorded; no committing unless asked.

---

## 4. Staged Roadmap

Stages are ordered by dependency: harness, gates, **`--trace-dialog`, and `catalog.yaml` first
(Stage 0 gates Stage 2's quest batches)**; the subsystem-probe primitives (esp. `qa_advance_time` +
worldmap observation) **before** the subsystem re-enable they verify; bridge-primitive gaps before the
quests that need them; leaf refactors before core; subsystem re-enable before the quests it unblocks.
Relative size is rough effort (S/M/L/XL). Stages overlap at the seams (e.g. region quest batches in
Stage 2 run while leaf refactors in Stage 3 begin), but a stage's exit gates the *next* stage's
heavier dependents.

### Stage 0 — Foundation: gates, harness, tracing, CI baseline (size: M)

**Entry:** current tree compiles/bakes/builds; 296/296 unit tests; 4 quests green.
**Work:**
- Lock the G1–G9 gate set + the **gate tiers** (§2.1) and the `SOAK` profile (§2.2) as the standing
  contract; capture the current baselines (ScriptQuality 284/299, nullable clean, quest suite = 4 green).
- **Build `--trace-dialog` (gated deliverable; gates Stage 2).** Add the dialog-keyword tracer to the
  runner toolchain. Given a giver NPC + dialog id, it extracts the candidate Russian answer-keyword
  sets that advance the quest's stage flag, ranked by stage-advance. This is the ~160×-repeated core
  action of Track B; quest batches **cannot start without it**. (Detailed contract + I/O in §5.2.)
  - *Exit criterion:* given a giver NPC + `dialogId`, `--trace-dialog` emits candidate answer-keyword
    sets **ranked by stage-advance**, for at least the 4 seed quests + 3 fresh Arroyo quests.
- **Build `generate_catalog.py` (gated deliverable; the denominator).** Emit the authoritative
  inventory of the **165** `///@ Property Critter ... Group = Quests` flags into
  `Docs/Quests/catalog.yaml`, one entry per flag with `test_status`. `catalog.yaml` is THE denominator
  for every "all quests" claim (Track B exit, §6.2, §8 #3).
  - *Exit criterion:* `catalog.yaml` contains exactly **165** entries; the 4 seed quests are
    `test_status: green`; the count matches `validate_content.py`'s flag enumeration.
- **Build `tla_batch_quest_runner.py`** (the batch driver) with its REQUIRED hygiene features baked in
  (so they are not bolted on later): **pre-batch** server-DB rotate/clean + fresh char name (dodging
  the `InactivityDisconnectTime=0` stale-session gotcha) + assert-no-residual-modal; **per-quest
  teardown** that drains modals via `screen.modalActive` → `close_screen` and resets to a known idle
  state. Plus `aggregate_quest_results.py` + `quest_critical_path.json`.
- **`qa_advance_time` feasibility SPIKE (load-bearing; see §5.2 / §6.1).** Prototype `qa_advance_time`,
  characterize its blast radius on a server-authoritative server (mass time-events firing at once; the
  ~114 unguarded `Sync::Lock` sites), and decide granularity (per-critter local clock vs global world
  clock). **If it cannot be made safe, ALL time-gated quests fall back to `manual`** (recorded in
  `catalog.yaml` + KnownIssues), and Stage 1's caravan/GameEvent re-enable verification adjusts
  accordingly. This spike's outcome gates Stage 1's subsystem re-enable verification.
- Land CI: PR smoke job, nightly headless **`SOAK`** soak, nightly quest regression matrix.
- Establish progress tracking: `Build/_audit/progress.md` (incl. a **last-known-green marker**, §5.5),
  `Build/_artifacts/` layout.
- Write `Docs/Architecture.md` (first pass) and `Docs/TestingPlaybook.md` (extract from AiControl.md);
  create `Docs/KnownIssues.md` seeded from the bug survey.
**Produces:** enforceable CI, batch harness with hygiene, `--trace-dialog`, `catalog.yaml` (the 165
denominator), the `qa_advance_time` spike verdict, baseline snapshot, foundational docs.
**Exit:** all gates + tiers runnable locally + in CI; `--trace-dialog` and `generate_catalog.py` meet
their exit criteria; `catalog.yaml` enumerates 165; the `qa_advance_time` spike has a recorded
verdict; nightly green on the 4-quest suite; docs landed.

### Stage 1 — Per-system smoke + bug triage + subsystem re-enable (size: L)

**Entry:** Stage 0 exit (incl. the `qa_advance_time` spike verdict).

Order within the stage matters: **the bridge primitives that probe a subsystem must land before that
subsystem is re-enabled and declared green.** Re-enabling GameEvent/Caravan/BulletinBoard is not
"done" at `"Start server complete!"` — startup only proves the init no longer null-derefs. Each
subsystem needs a **direct functional probe**, which needs the observation primitives first.

**Work (ordered):**
1. Fill the system × test-method matrix (Section 6.1): one automated/partial check per system.
2. **Land the subsystem-probe primitives first:** `qa_advance_time` (per the Stage-0 spike verdict;
   if the spike said *unsafe*, time-gated probes degrade to manual and time-gated quests are `manual`)
   + worldmap travel/encounter observation (`worldmap_move`/route-progress read); `qa_get_reputation`
   + faction observation; `chosen.effects`/`weight` observation.
3. **Re-enable GameEvent / Caravan / BulletinBoard** (Track C #1) — owner-coordinated; the central
   playability unblock; gates caravan escort quests. **Re-enable is verified by a DIRECT subsystem
   probe, not just startup:**
   - *Caravan:* spawn a caravan, **`qa_advance_time`**, and verify route/escort progress on the
     worldmap (needs step 2's primitives).
   - *GameEvent:* fire one GameEvent and observe its declared effect.
   - *BulletinBoard:* post one message and read it back.
   If the `qa_advance_time` spike came back *unsafe*, the Caravan probe falls back to an owner manual
   playtest and caravan escort quests stay `manual` (recorded in `catalog.yaml`).
4. Async sync long-tail batches 1–2 (Item deferred-destroy/door, Map critter loops); content bugs
   (Bag-not-found, DenVirginIsAway scope, guard-NPC dialog, repl_* text).
5. Stand up `Tools/ContentValidator/` Tier 1+2 (Track F) and wire into bake.
**Produces:** system smoke coverage, subsystem-probe primitives, three subsystems back online **and
probe-verified**, key bridge gaps closed, content validator gating bake.
**Exit:** `SOAK` (§2.2) clean with subsystems enabled; each re-enabled subsystem passes its direct
probe (or is owner-manual-verified with a logged reason); system matrix has no empty "missing
primitive" cell that blocks a planned Stage 2 region; content validator baseline set.

### Stage 2 — Region-by-region quest coverage + fixes (size: XL)

**Entry:** Stage 1 exit (bridge gaps + subsystem re-enable in place) **and the Stage-0 `--trace-dialog`
deliverable green** — Track B's per-quest loop is built on `--trace-dialog`, so Stage 0 **gates** Stage 2.
**Work:** Execute the region batches (Section 6.2) via the per-batch loop (Section 5.2), ordered
Arroyo → Klamath → Den (split batches) → Modoc → Redding → Vault City → NCR → SF → Navarro →
New Reno → Broken Hills → Vault 13 → GameEvent/Replicator → Tribal/Main long-chain → cross-region
long-chain. Each batch: trace (`--trace-dialog`) → author specs → run → triage (file blockers to
Track C) → fix → re-verify → ratchet → catalog. Long-chain (Max 8–21) and time-gated (caravan
escorts) handled last; escorts marked `manual` unless re-enabled caravans make them automatable.
Every `manual` quest follows the **manual quest protocol** (§5.6): it gets a recorded
owner-playtest pass and a `manual-verified` (vs `manual-deferred`) `test_status` in `catalog.yaml`.
**Produces:** growing green quest suite (4 → ~20 → ~50 → 100+); populated `Docs/Quests/catalog.yaml`
(the 165-entry denominator); a stream of content/code bug fixes; per-region known-issues entries.
**Exit:** every *automatable* quest across regions is green and in the regression suite (counted
against `catalog.yaml`); every `manual` quest is `manual-verified` (recorded pass) or
`manual-deferred` with a logged reason; remaining quests are explicitly `blocked` with logged reasons.

### Stage 3 — Deep system hardening + refactor (size: XL)

**Entry:** Stage 2 substantially done (a region's quests green before that region's NPC modules are
restructured, so refactor regressions are caught).
**Work:**
- Async sync long-tail batch 3 (~104 any-value GetItem/GetCritter sites), audited and locked.
- Refactoring Track D: R2-1 pilot → R2-2 domain batches → god-module splits (leaves → domain →
  async/timer → side/infra → Main). R2-3 test harness (`Testing.fos`) + pure-helper/critical-flow
  suites in CI.
- **Infra-module splits use the DIFFERENTIAL gate (§5.7).** Cross-cutting god-modules with **no owning
  quest batch** (Main, Worldmap 11.5k, Caravan, NpcPlanes, Parameters) cannot use "refactor after its
  quests are green" — there is no such batch. Instead, run the **full quest-regression suite + `SOAK`
  before and after the split and diff them**; the split is accepted only if the diff is clean.
  **Caravan is special:** bundle its split *with* its Stage-1 re-enable (touch the file once) **or**
  defer the split until the caravan escort quests are green — do **not** split it independently
  (double exposure of an already-fragile subsystem).
- Per-mechanic regression suites (combat/barter/crafting/skills) added to the harness.
- Game.Log audit; commented-out-code per-block triage; redundant-bool-return + header backfill.
**Produces:** ratcheted-down baseline, split god-modules, gameplay test harness, deeper regression
coverage.
**Exit:** R2-1/2/3 complete; god-modules split (each infra split passed its differential gate) or
consciously deferred; async sync tail closed; baseline at target (headers 100%, banner-tags 0,
redundant-bool-return ~0); `SOAK` (§2.2) still clean.

### Stage 4 — Content validation + soak + docs polish (size: L)

**Entry:** Stage 3 exit.
**Work:**
- Full `ContentValidator` Tier 3/4 (orphans, quest read/write coverage); resolve or accept findings.
- Localization parity pass (russ/engl text packs); fix empty `repl_*` text and missing text ids.
- **`Mob::Idle` "Null assignment to non-nullable handle" — confirm non-recurrence under `SOAK`.**
  Treat the intermittent as a real task, not an open question: run the extended `SOAK` profile and
  confirm the `Mob::Idle` null does not recur; if it does, audit the `TryGoHome → AddWalkPlane →
  AddPlane` chain in `Mob.fos`/`NpcPlanes.fos` and fix (Track C). Closing this is required for §8 #1.
- Extended `SOAK` (§2.2 with raised `N`/`M`, plus a live owner playtest session); regression-diff
  against the Stage 0 baseline logs.
- Documentation completion: all `Docs/Systems/*`, `Quests/`, `ContentAuthoring.md` finished; cross-
  references in `AGENTS.md`/`README.md`; doc link-check in CI.
**Produces:** validated content, clean `SOAK`, `Mob::Idle` confirmed non-recurring, complete doc set.
**Exit:** Section 8 Definition of Done satisfied.

### Ongoing (post-Stage-4)

Engine-update upkeep (Track H) per bump; nightly CI; new content goes through ContentValidator +
gets a quest spec; new bugs append to `KnownIssues.md`; quest catalog regenerated when quests change.

---

## 5. The Repeatable Stage / Loop Templates

The automated run resumes across sessions by reading the progress log and the dated artifacts under
`Build/_audit/` and `Build/_artifacts/`, then picking up at the documented resume point.

### 5.1 The fix-verify-document loop (atomic unit of work)

```
1. READ      — understand the system/bug (code + git history + relevant Docs/Systems/*).
2. TRIAGE    — classify layer (engine / SourceExt / Scripts / content); pick narrowest fix.
               Also classify the CHANGE TIER (§2.1: T0 spec/data, T1 comment/format, T2 behavior),
               which decides the gate set in step 4.
3. CHANGE    — behavior-preserving edit, or deliberate code-verified bug fix. Russian comments,
               English contracts. Never bulk-delete commented code.
4. VERIFY    — run the TIER's gate set (§2.1), not blindly all of G1–G9:
                 T0 → G9 only.
                 T1 → G1 compile + G6 ratchet + G8 format (+ G7 if a nullable contract is touched).
                 T2 → G1 → G2 incremental bake (Force Bake only if a ///@ Property moved) → G3 →
                      G5 headless (if server behavior) → G6 → G7 → G8 → G9.
               Expensive gates (full bake, SOAK, G4 unit tests unless native) run in CI, not here.
               Warnings = failure.
5. ROLLBACK  — if verification REGRESSES (a previously-green gate/quest goes red) and the root cause
               is not found within this loop: revert YOUR change only — `git stash` your own edits,
               NEVER touch the user's dirty files (§1.2 #8) — record the failed attempt in
               Docs/KnownIssues.md (symptom, hypothesis, what was tried), and re-establish green
               (the last-known-green marker, §5.5) before proceeding. Do not stack a second change
               on top of an un-diagnosed regression.
6. DOCUMENT  — update the relevant Docs/* (system doc, KnownIssues, quest catalog) IN THE SAME
               session; annotate any preserved commented block with a reason.
7. RECORD    — append to Build/_audit/progress.md (advance the last-known-green marker on success);
               drop artifacts (reports/screenshots) in Build/_artifacts/<stage>/. Do NOT commit (owner does).
```

### 5.2 The per-region quest batch loop (Track B)

> **Prerequisite:** this loop is built on the Stage-0 `--trace-dialog` deliverable. Until
> `--trace-dialog` exists and meets its exit criterion, Track B cannot start (Stage 0 gates Stage 2).

```
PRE-BATCH HYGIENE (REQUIRED features of tla_batch_quest_runner.py, not manual steps)
  - Rotate/clean the server DB so the batch starts from a known-fresh world.
  - Use a FRESH char name this batch (dodges the InactivityDisconnectTime=0 stale-session gotcha).
  - Assert NO residual modal before the first quest (a leftover screen poisons dialog_answer).
PRE-BATCH DISCOVERY
  - tla_mechanics_playtest.py --teleport-map <region> --report region.json → enumerate NPCs/reachability.
  - Map quest-flag prefixes (e.g. DenSmitty*) → dialog ids / giver NPCs; confirm map proto names.
  - Cross-check the prefixes against catalog.yaml so the batch covers its full share of the 165.
FOR EACH QUEST (simplest Max first):
  1. TRACE — extract the Russian answer-keyword sets with --trace-dialog (the ~160x core action):
       a. Identify giver NPC proto + dialogId (from the quest-flag prefix → dialog ref).
       b. INPUT : tla_quest_runner.py --trace-dialog --npc <proto> --dialog <dialogId>
                  --flag <Critter.QuestFlag> --report trace.json
       c. OUTPUT: trace.json = candidate answer-keyword sets RANKED by stage-advance (the answers
                  that move <flag> toward its stage target), each with the answer text + node path.
       d. Take the top-ranked set as `prefer[]`; keep alternates as fallbacks.
  2. AUTHOR  — add stage dict to QUESTS: {map, npc, npc_hex?, target, prefer[], setup[]}.
               Server-scope flags → verify via qa_get_prop; prereqs via qa_set_prop/game_prop/give_item.
               SETUP ANNOTATION (end-to-end vs injected): prefer reaching prereqs by real gameplay.
               Every qa_set_*/qa_give_item/qa_teleport_* used for setup is a privileged shortcut
               (§1.2 #1) and MUST be annotated in the spec (`setup_injected: [...]`), so catalog.yaml
               can mark the quest "verified end-to-end" vs "verified-from-injected-state".
  3. RUN     — tla_quest_runner.py --quest <name> --report run.json → expect ok:true, property advance.
  4. TRIAGE  — on failure: content/code bug? → file in KnownIssues + known_quest_issues.md, hand to
               Track C. Brittle keywords? → grow prefer[] from trace.json alternates. Unreachable/
               guard NPC? → probe + flag.
  5. FIX     — apply Track-C fix if in scope; re-verify gates.
  6. RE-VERIFY — re-run the quest; add to the regression suite (G9) so it stays green.
  7. RATCHET — G6/G7/G8 still green; baseline only moves down.
  8. DOCUMENT — update Docs/Quests/catalog.yaml entry (test_status, verified-e2e vs injected, notes);
               mark manual-verified/manual-deferred/blocked as needed.
  PER-QUEST TEARDOWN (REQUIRED feature of tla_batch_quest_runner.py)
  - Drain any open modal: while screen.modalActive → close_screen.
  - Reset to a known idle state (no dialog, no barter, character not mid-action) before next quest.
END
BATCH REPORT — summary of specs added, blockers filed, regressions; append to progress.md.
```

Mark time-gated escorts (`Redd*CaravanEscort`, `NcrReddingCaravanEscort`) and long-chains as
`manual` (then `manual-verified`/`manual-deferred` per §5.6); revisit escorts only after caravans are
re-enabled and probe-verified (Stage 1). If the Stage-0 `qa_advance_time` spike returned *unsafe*, all
time-gated quests are `manual` by default.

### 5.3 The bug triage tiers (Track C)

```
TIER 1 static    — Compile/Bake/validators; catches missing symbols, bad refs, magic ids, nullability.
TIER 2 headless  — Prepare :: TLA_ServerHeadless; "Start server complete!" + 0 exceptions; map symptom
                   ("Bag N not found"→NpcBags; "Null assignment"→Mob::Idle/plane; EntitySyncException→
                   missing Sync::Lock in named file).
TIER 3 bridge    — login → qa_teleport to high-NPC map → exercise (idle loops, item lifecycle, dialog,
                   quest path) → watch event stream for runtime_exception + server log.
TIER 4 repro     — minimal scripted repro + regression assertion; apply fix; re-run; confirm gone; no
                   side effects (re-run smoke).
```

### 5.4 The engine-update protocol (Track H)

```
PRE   — git -C Engine log/diff upstream; check H:/lf-30 + active sibling for the migration pattern;
        confirm tree is GREEN first.
BUMP  — git -C Engine checkout <SHA>.
GATES (in order, fix fallout at each):
  1 Compile AngelScript        (core type/API/nullability change → Scripts)
  2 Force Bake Resources       (new FIXED_SETTING → TLA.fomain; proto layout → SubProto/MigrationRule)
  3 Build TLA_ASCompiler/Baker (engine header/API drift)
  4 Build TLA_Server/Client    (EngineHook rename / native API → SourceExt; AddEngineSources → CMake)
  5 Headless startup           (async-sync requirement; init crash)
  6 TLA_UnitTests              (296/296; engine-core regression → escalate upstream)
POST  — local `SOAK` (§2.2) + one quest cycle (cassidy_letter); record SHA; do not commit unless asked.
```

### 5.5 Resuming across sessions

- **Source of truth for "where are we":** `Build/_audit/progress.md` (per-stage status, current
  sub-step, blockers, and the **last-known-green marker**) + dated `Build/_artifacts/` reports.
- **Last-known-green marker:** progress.md records the most recent state where the tier's gates + the
  quest suite were all green (which stage/batch/step, plus the SHA/spec snapshot). The ROLLBACK rule
  (§5.1 step 5) reverts to this marker when a regression can't be diagnosed in-loop; the resume rule
  starts from it.
- **Resume rule:** re-run the cheapest gate that proves the current state (compile + incremental bake
  + headless), confirm the last-known-green marker still holds, read progress.md, continue at the
  documented resume point of the active stage/batch.
- **Quest suite is the memory of Track B:** the QUESTS dict + catalog.yaml record exactly which quests
  are green (and end-to-end vs injected, manual-verified vs manual-deferred); the nightly regression
  proves they still are.

### 5.6 The manual quest protocol (`manual-verified` vs `manual-deferred`)

Some quests are not automatable by the bridge: long-chain quests (Max 8–21 — the NCR chains, the
Tribal **MainQuest** (Max 21, the game's main quest), the SF Imperator/ZAX arcs) and time-gated
escorts. Marking them `manual` is only meaningful if "manual" is **defined** — otherwise the MAIN
QUEST has no path to "done". So every `manual` quest carries one of two statuses in `catalog.yaml`:

- **`manual-verified`** — has at least one *recorded owner-playtest pass* against the checklist below.
- **`manual-deferred`** — known-not-yet-verified, with a logged reason (e.g. blocked on a subsystem,
  scheduled for a later session). Allowed during the campaign; **not** allowed at the Definition of
  Done for any quest in scope.

**Per-quest manual-verification checklist template** (one filled-in copy per manual quest, stored with
the catalog entry; screenshots into `Build/_artifacts/manual/<quest>/`):

```
QUEST: <name>   GIVER: <npc proto @ map/hex>   Max: <stage cap>
1. ENTRY STATE   — exact starting conditions (char level, items held, prior flags set, faction rep).
2. STEPS         — numbered player actions to drive the chain start → finish (each a concrete UI act).
3. EXPECTED      — per-step expected outcome (dialog node reached, flag value, item granted, screen).
4. EVIDENCE      — screenshot per key step into Build/_artifacts/manual/<quest>/NN.png.
5. RESULT        — PASS/FAIL + the final flag value vs Max; date + who ran it.
```

A `manual-verified` quest is "done" for §8 #3; a `manual-deferred` quest is a tracked open item.

### 5.7 The differential gate (infra-module splits with no owning quest batch)

For cross-cutting god-modules (Main, Worldmap 11.5k, Caravan, NpcPlanes, Parameters) there is no
"owning quest batch", so "refactor after its quests are green" is undefined. These splits use a
pre/post **differential** gate instead:

```
BEFORE the split — capture a baseline:
  - Run the FULL quest-regression suite (G9 over the whole verified set) → save results.
  - Run SOAK (§2.2) → save the exception/RSS profile.
PERFORM the split (behavior-preserving; leaves before core; Force Bake on ///@ Property moves).
AFTER the split — re-capture and DIFF:
  - Re-run the full quest-regression suite → diff against the before-results (must be identical-green).
  - Re-run SOAK → diff exception/RSS profile (no new exceptions, no new growth).
ACCEPT only if the diff is clean; else ROLLBACK (§5.1 step 5) and re-attempt smaller.
```

**Caravan is special (double-exposure rule):** Caravan is both a Stage-1 re-enable target and a
god-module split. Do **not** split it independently. Either (a) bundle the split *with* its Stage-1
re-enable so the file is touched once under one verification, or (b) defer the split until the caravan
escort quests are green and use the differential gate then. Splitting it on its own exposes an
already-fragile subsystem twice.

---

## 6. Coverage Matrices

### 6.1 System × test-method

`A` = automated E2E today, `P` = partial (observation/command only), `M` = manual-only, `gap` = needs
a new bridge primitive. Method = the bridge command(s)/tool used.

| System | Status | Method / primitive | Missing primitive |
|--------|--------|--------------------|-------------------|
| Movement | A | `move_to_hex`, `environment_query path` | — |
| Dialogs | A | `talk_to`, `dialog_answer`; `dialog.*` observation | (content: empty repl_* text) |
| Inventory ops | A | `move_item`, `drop_item`, `operate_container` | encumbrance: `chosen.weight` (gap) |
| Item use | A | `use_item`, `reload`, `unload` | — |
| Skills | A | `use_skill` | — |
| Combat | A | `attack_entity`; `inCombat`/`isAlive`/exp | PvP fairness = M; mob-AI path trace (gap) |
| Crafting (FixBoy) | A | `craft` | recipe-list observation (gap) |
| Barter/economy | A | dialog + `move_item`; screen obs | price-trace over campaign = P |
| Quests | A (4) / P (Server-scope) | runner + `qa_get_prop` | faction-rep gates → `qa_get_reputation` (gap) |
| Faction/reputation | gap | — | `qa_get_reputation` + faction observation |
| Buff/debuff (drugs/rad/perk) | gap | — | `chosen.effects` / `perks_active` observation |
| Party/followers | gap | — | `qa_recruit_npc` + party observation |
| Worldmap/encounters | P (canonical only) | `qa_teleport_global` (no-op from sandbox) | `worldmap_move` + encounter observation |
| Time-gated content | gap | — | `qa_advance_time` (Stage-0 feasibility spike; if unsafe → all time-gated quests `manual`) |
| Screens/GUI | A (verify M) | `show/hide/close_screen`; `screen.modalActive` | layout/animation feel = M |
| Rendering | M (+screenshot diff) | `save_screenshot` golden-image diff (CI) | GPU-dependent visuals = M |
| Audio | M | — | audio-event emit (engine) |
| Performance/soak | P | the `SOAK` profile (§2.2): headless 0-exception + region rotation + RSS tracking | profiler counters (gap) |
| Registration/login | A | `register`, `login` | — |

### 6.2 Quest region-batches (order, counts, done)

**165** quest flags (counted as distinct `///@ Property Critter ... Group = Quests` flags;
`generate_catalog.py` emits the authoritative inventory in Stage 0 — `catalog.yaml` is the
denominator). Order respects geographic coherence, automation readiness (simplest `Max` first), and
growing complexity. Already-green specs are the seeds. Every one of the 165 flags lives in exactly one
batch below; the counts sum to 165 (arithmetic under the table).

| Batch | Region cluster | Flag prefixes | Count | Already green (seeds) | Notes |
|-------|----------------|---------------|-------|-----------------------|-------|
| 1 | Arroyo | `Arroyo*`, `arroyo_*` | 8 | `cassidy_letter`, `arroyo_mynoc_oil` | 6 new traces (ProofOfDeath, LetterToLinnett, MynocDefence, …) |
| 2 | Klamath | `Klam*` | 12 | `klam_vaccination` (Server-scope) | SmilyModoc cross-town; FindTrappers/BugenLure long-chain |
| 3 | Den — batch A (foundation) | `Den*` (Max≤4) | 13 | `den_smitty_robot` | Max≤4; **skip DenMomSlut** (scope bug → Track C) |
| 4 | Den — batch B (medium) | `Den*` (Max 3–5) | 13 | — | medium chains |
| 5 | Den — batch C (deep) | `Den*` (deep/long) | 12 | — | remaining Den flags; deeper chains |
| 6 | Modoc | `Mod*` | 10 | — | ModBaltasArmor multi-prop; brahmin/ghost chain |
| 7 | Redding | `Redd*` | 13 | — | ReddDocRadio sub-tasks; `Redd*CaravanEscort` = `manual` (time-gated) |
| 8 | Vault City | `VC*` | 20 | — | high giver density; `cassidy_letter` already exercises vc_cindy |
| 9 | NCR | `Ncr*`, `NCR*` | 19 | — | many long-chains deferred (21/15/11); `NcrReddingCaravanEscort` = `manual` |
| 10 | San Francisco | `SF*` | 13 | — | good diversity; Imperator/ZAX long ones → long-chain batch |
| 11 | Navarro | `Nav*` | 3 | — | all automatable; quick round |
| 12 | New Reno | `NR*` | 3 | — | incl. NrWriKidnap (missing text id 3354 → Track C) |
| 13 | Broken Hills | `BH*` | 4 | — | BHRocketBase silo integration |
| 14 | Vault 13 | `V13*` | 2 | — | small, late-game |
| 15 | GameEvent / Replicator | `GERepl*` | 5 | — | **gated on GameEvent re-enable** (Stage 1) |
| 16 | Tribal / Main long-chain | `MainQuest`, `QChosen`, Tribal `Q*` | 7 | — | MainQuest = the Max-21 main quest → `manual` (§5.6) |
| 17 | Misc / core / cross-region | `MailDelivery`, `BarterLourensRats*`, other `Q*`-sub-flags, core | 8 | — | core/contract sub-flags + cross-region; caravan escorts = `manual` |

**Arithmetic (sums to 165):**
`8 (Arroyo) + 12 (Klamath) + 13 + 13 + 12 (Den A/B/C = 38) + 10 (Modoc) + 13 (Redding) + 20 (Vault City)
+ 19 (NCR) + 13 (SF) + 3 (Navarro) + 3 (New Reno) + 4 (Broken Hills) + 2 (Vault 13) + 5 (GERepl) +
7 (Tribal/Main) + 8 (Misc/core)`
= `8+12+38+10+13+20+19+13+3+3+4+2+5+7+8` = **165**. ✓
(Named-region subtotal `8+12+38+10+13+20+19+13+3+3+4+2 = 145`; plus `5+7+8 = 20` for the
GameEvent/Replicator, Tribal/Main, and Misc/core buckets = 165.)

The four already-green seed specs (`cassidy_letter`, `arroyo_mynoc_oil`, `den_smitty_robot`,
`klam_vaccination`) live in batches 1–3 and stay green throughout.

Structural blockers carried into batches: ~63 Server-scope flags need `qa_get_prop`; the caravan
escorts (`Redd*CaravanEscort`, `NcrReddingCaravanEscort`, + the cross-region escorts in batch 17) are
time-gated `manual` until caravans are re-enabled **and** the `qa_advance_time` spike succeeds;
batch 15 (`GERepl*`) is blocked until GameEvent is re-enabled (Stage 1); Russian dialog keyword
extraction is per-quest via `--trace-dialog` (grow `prefer[]` from its ranked alternates); content
bugs (DenMomSlut scope, guard NPCs, NrWriKidnap text id 3354) hand off to Track C.

---

## 7. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Intermittent sync bugs** (~114 conditional `EntitySyncException`; Mob::Idle null) fire only under specific conditions, hard to repro | High | High | Headless soak with high NPC count + the bridge stress scenarios (Section 5.3 Tier 3); batch the long-tail (Item → Map loops → any-value sites); lock the full entity cover per callback; verify Mob::Idle post engine-bump. |
| **Disabled subsystems block features** (GameEvent/Caravan/BulletinBoard fresh-DB null-derefs) | Certain (present) | High | Owner-coordinated re-enable in Stage 1; treat as DB/serialization investigation, not a script patch; gate caravan escort quests behind it. |
| **Content rot** (dangling proto/text/quest refs that bake silently, surface at runtime or never) | High | Medium | `Tools/ContentValidator/` Tier 1+2 fails bake on dangling refs; localization parity check; quest catalog cross-check. |
| **Engine churn** (frequent submodule bumps break compile/bake/native; shader-profile + FIXED_SETTING traps) | High | Medium | Deterministic 7-step protocol (Section 5.4); cross-check `H:/lf-30`/sibling; pause other tracks until gates green; keep engine shaders within the minimal profile. |
| **Automation fragility** (dialog keyword matching brittle to text changes; sandbox vs canonical world; fresh-server hygiene; Russian client requirement) | Medium | Medium | `--trace-dialog` (Stage-0 deliverable) extracts ranked keyword sets and grows `prefer[]` from its alternates; batch-runner pre-batch hygiene + per-quest teardown (§5.2) prevent stale-session/modal poisoning; document gotchas in TestingPlaybook + known_quest_issues; quest catalog records keyword sets and end-to-end-vs-injected status. |
| **`qa_advance_time` unsafe on a server-authoritative server** (mass time-events + ~114 unguarded Sync::Lock sites; load-bearing for time-gated quests, escorts, GameEvent, effect decay) | Medium | High | Stage-0 feasibility spike characterizes blast radius and picks granularity (per-critter vs global clock); explicit fallback: if unsafe, ALL time-gated quests + the Caravan subsystem probe go `manual`/owner-playtest (recorded in catalog.yaml + KnownIssues). |
| **Scope / never-ending campaign** (165 quests + full refactor + docs is months) | High | Medium | Stage gates with explicit exit criteria; the **manual quest protocol** (§5.6) gives even the Max-21 MainQuest a concrete `manual-verified` path; mark long-chain/time-gated quests `manual` rather than forcing; ratchet + last-known-green marker prevent backsliding; progress.md keeps the run measurable and resumable. |
| **Refactor regressions in big splits** (Worldmap 11.5k, Caravan 4k) | Medium | High | Infra modules with no owning quest batch use the **differential gate** (§5.7): full quest-regression + `SOAK` before+after, diffed; Caravan split bundled with its Stage-1 re-enable or deferred until escort quests are green (no independent split); ROLLBACK (§5.1) on any un-diagnosed regression; leaves before core; behavior-preserving discipline. |
| **Commented-code deletion regret** (breadcrumbs lost) | Low–Med | Medium | Never bulk-delete; annotate with reason; per-block triage with git-history check. |
| **Accidental commit / overwriting user changes** | Low | High | Do not commit/stage/push; read dirty files before touching; work with user changes, never revert them. |

---

## 8. Definition of Done

"In working order" is measured, not asserted. The campaign is done when **all** of the following hold
and are demonstrated by the gates/artifacts:

1. **Server runs clean.** `TLA_ServerHeadless` reaches `"Start server complete!"` and the `SOAK`
   profile (§2.2: `N=4h`, `M≥100` NPCs, region rotation, 0 unhandled exceptions, stable RSS) passes.
   The async sync long-tail is closed (Item, Map loops, any-value sites locked) and the `Mob::Idle`
   null is confirmed non-recurring under `SOAK` (Stage 4). [G5; Track C]
2. **Disabled subsystems resolved.** GameEvent, Caravan, BulletinBoard are debugged and re-enabled
   **and probe-verified** (each passes its Stage-1 direct subsystem probe, or is owner-manual-verified)
   — or consciously retired with a logged owner decision. Caravan escort quests are reachable or
   explicitly `manual` (per §5.6). [Track C #1]
3. **Quest coverage.** Measured **against `catalog.yaml`** (the 165 denominator): every *automatable*
   quest across all 17 batches (§6.2) has a green `tla_quest_runner.py` spec in the nightly regression
   suite, each marked **verified end-to-end** or **verified-from-injected-state** per its annotated
   `setup`; every `manual` quest is **`manual-verified`** (at least one recorded manual-verification
   pass, §5.6) — no in-scope quest is left `manual-deferred`; the remaining quests are explicitly
   `blocked` with reasons in `Docs/Quests/catalog.yaml` + `known_quest_issues.md`. The four seed quests
   stay green throughout. [G9; Track B]
4. **System coverage.** Every system in the Section 6.1 matrix has an automated or partial check; the
   priority bridge primitives (faction rep, effects, time, worldmap) are implemented and gated. [Track A]
5. **Content integrity.** `ContentValidator` Tier 1+2 run in the bake pipeline and pass; no dangling
   proto/text/quest references; russ/engl localization parity holds for touched content. [Track F]
6. **Code health.** Refactoring R2-1/2/3 complete; god-modules split or consciously deferred;
   ScriptQuality baseline ratcheted to target (headers 100%, banner-tags 0, redundant-bool-return ~0);
   nullable checks exact; gameplay test harness (`Testing.fos`) in CI. No gate regressions. [G6/G7; Track D]
7. **CI enforces it.** PR pipeline enforces the per-tier inner-loop gates (compile/bake/build/ratchet/
   nullable/format); nightly enforces the full bake + `SOAK` (§2.2) + quest regression; reports land
   as artifacts. [Track G]
8. **Docs are complete and live.** `Architecture.md`, all `Docs/Systems/*`, `Quests/` catalog,
   `ContentAuthoring.md`, `TestingPlaybook.md`, `KnownIssues.md` exist, are cross-referenced from
   `AGENTS.md`/`README.md`, and reflect the actual code. [Track E]
9. **Engine upkeep is routine.** The submodule sits at a SHA where all gates are green; the
   update protocol is documented and has been exercised. [Track H]

The standing gates (G1–G9) remain green at all times throughout — that is the invariant that makes
"working order" durable rather than a one-time snapshot.

---

## Appendix: Key references

- [AGENTS.md](../AGENTS.md) — repository practices, build/verify/commit policy, engine boundary.
- [Docs/Refactoring.md](Refactoring.md) — Scripts refactor plan (Phases 0–4 done; Round 2 R2-1/2/3
  pending); **subsumed** by Track D here.
- [Docs/ScriptStyle.md](ScriptStyle.md) — headers, Russian comments, structure, idioms, formatting.
- [Docs/AiControl.md](AiControl.md) — AI control bridge protocol, commands, observation, verified quests.
- [Docs/Nullability.md / Nullability.md](../Nullability.md) — script `T?` and native `ptr<T>`/`nptr<T>` strong-nullable rules.
- `Tools/AiControlMcp/` — bridge MCP adapter, `tla_quest_runner.py`, `tla_mechanics_playtest.py`,
  `smoke_ai_control_mcp.py` (+ planned `tla_batch_quest_runner.py`, `aggregate_quest_results.py`).
- `Tools/ScriptQuality/` — `validate_scripts.py`, `baseline.json` (`--ratchet`/`--fix`), `render_audit.py`.
- `Tools/NullableEstimate/` — `validate_nullable.py`, its focused unit tests, and the script-side nullable analyzers.
- `.vscode/tasks.json` — authoritative build/bake/format/launch/analyze tasks.
- `Build/_audit/` — per-module audit docs + `progress.md`; `Build/_artifacts/` — test reports/screenshots.
- `H:/lf-30` (and active `lf-NN` sibling) — migration reference on the same engine.
