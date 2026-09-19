# Audit Plan

Working plan for the ten findings of the 2026-09-02 project audit. Each item states the measurement it
rests on, the steps, and the condition that closes it. This file is a **plan**, not a journal: when an item
is done its steps collapse to a one-line outcome. Session narrative belongs in `Docs/History/`.

Order below is execution order, not severity. Items 3 and 8 come first because everything else is verified
through the chain they define; item 9 comes next because it is what a newcomer reads; the heavy work
(2 → 1 → 7) follows, because extracting data and cutting giant functions is only safe on top of tests.
Items 4, 5, 6 and 10 are local and are woven in wherever they fit.

| # | Item | Size | Status |
| - | ---- | ---- | ------ |
| 8 | One aggregate verification task | S | **done** |
| 3 | Quality gates in CI | S | **done**, harness deferred |
| 9 | Split the journal from the plan, add a systems map | M | **done** |
| 4 | Record the single-threaded constraint | S | **done** |
| 5 | Generated and test scripts into their own folders | S | **done** |
| 6 | Fold the copied guard init back into `GuardLib` | M | re-scoped, blocked on 2 |
| 10 | Mutable-globals allowlist becomes a boundary again | rule | **done** (rule written) |
| 2 | Tests on the hot paths | L | **done**, two modules substituted |
| 1 | Tables out of code into authored data | XL | crafting done, caravans and worldmap next |
| 7 | Cut the giant combat functions | L | two slices done, rest needs a combat fixture |

---

## 8. One aggregate verification task

**Measurement.** `.vscode/tasks.json` holds 43 tasks and no aggregate; the full pre-handoff chain is
reassembled by hand every session.

**Steps.**
1. Add `Verify :: All`, chaining through `dependsOn` in order: bake → build targets → engine unit tests →
   script harness → validators → formatters.
2. Keep every step an existing task where one exists, so there is one definition per step.

**Outcome.** `Verify :: All` chains bake → six target builds → engine unit tests → script harness →
validators → formatters. Every step reuses an existing task except `Test :: Python Tools`, added because the
156 tests under `Tools/` had none. Both are listed in the `AGENTS.md` task table.

---

## 3. Quality gates in CI

**Measurement.** CI runs formatting, nullable contracts, engine unit tests, script compilation, baking and
the platform builds. It does not run the script harness (72 tests), `validate_scripts --ratchet`,
`Tools/ContentQuality` (19 tests) or the `Tools/AiControlMcp` static suite.

**Steps.**
1. Add a `quality-gates` job that bakes, then runs the four gates above.
2. Reuse the ratchet baseline as-is; the job fails only on new violations.

**Outcome.** A `quality-gates` job runs `validate_scripts --ratchet` and `pytest Tools -q` (156 tests) on
every push and pull request.

**Deferred, with the reason.** The script harness is not in CI yet: it needs a Linux server build plus a bake,
and the binary layout under `Workspace/output/` in the runner differs from the local `Binaries/` tree. Writing
that step blind would put an unverified job in front of everyone else's pull requests. It needs one session
with a real runner to pin the path, and then it belongs in the same job.

---

## 9. Split the journal from the plan, add a systems map

**Measurement.** `Docs/Refactoring.md` is 115 KB and `Docs/ReanimationPlan.md` 69 KB, both append-only,
with forty-odd out-of-order "Latest Engine … bump (date)" sections. The engine has `Docs/Architecture.md`
and `Docs/SourceTree.md`; the game has no systems map at all.

**Steps.**
1. Move the session narrative of `Refactoring.md` into `Docs/History/`, leaving standing decisions and the
   open remainder in place.
2. Write `Docs/Systems.md`: one screen per system — what it is, where it lives, what it talks to, what
   covers it.
3. Add `Docs/README.md` as the index, mirroring the engine's.

**Outcome.** `Docs/Systems.md` maps the systems by area with side, entry point and coverage, and traces one
player action through six of them in order. `Docs/README.md` indexes the set. The `Refactoring.md` narrative
moved to `Docs/History/Refactoring-2026.md`, taking the plan from 1352 lines to 208.

---

## 4. Record the single-threaded constraint

**Measurement.** With `Server.SingleThreadedLogic = False` the harness still reports 72/72 but logs 794
`Entity access without sync` exceptions and 253 time events stopped by exception — the throws are
recoverable at the job frontier, so the breakage is invisible in the exit code. `Server.WorkerThreads = 6`
remains in the config and looks live.

**Steps.**
1. State the constraint in `AGENTS.md` beside the synchronization section.
2. Mark `Server.WorkerThreads` in `TLA.fomain` as inactive while the mode is on.

**Outcome.** `AGENTS.md` states the constraint with its measurement, and the three stale rules that still
told maintainers to take a `Sync::` cover and mark `[[Async]]` were removed with it. `TLA.fomain` says the
same beside `Server.WorkerThreads`.

---

## 5. Generated and test scripts into their own folders

**Measurement.** 294 hand-written modules sit flat beside 27 352 lines of generated `GuiScreens.fos` and
`Content.fos`; `Scripts/Json/` proves subdirectories bake.

**Steps.**
1. Move the generated pair to `Scripts/Generated/` and update the GUI generator's output path.
2. Move `Test_*.fos` and `Testing.fos` to `Scripts/Tests/`.
3. Update the tools that address these files by path.

**Outcome.** `Scripts/Tests/` holds the 26 suites, `Scripts/Generated/` the generated `GuiScreens.fos`, and
the InterfaceEditor config writes there. Baking does not recurse, so both directories are listed in the
`InputDirs` of the `Metadata` and `Scripts` resource packs — now stated in `AGENTS.md`.

**Left in place.** `Content.fos`: nothing in the repository or the engine writes it, so its producer is
unidentified and a move risks a duplicate namespace when something regenerates it at the old path.

---

## 6. Fold the copied guard init back into `GuardLib`

**Measurement.** 463 duplicated eight-line windows across the scripts, 1 060 occurrences. `GuardInit` is
copied into five modules and three of the five bodies are byte-identical, though `GuardLib.fos` exists for
exactly this.

**Re-scoped after reading the code.** The measurement stands, the proposed fix does not. Two things the
audit got wrong:

- `GuardLib::GuardInit` is inside a commented-out migration block marked "не удалять" — `GuardLib` is a live
  library (`CGuardsManager`, `ObservationPeriod`) but has no live guard-init to fold into.
- The five copies are not redundant text. Each module subclasses `CGuardsManager` with its own dialog and
  behaviour, and the eight handlers are three-line forwarders to *that module's* instance. They read
  identically because engine event subscription takes a free function, and a free function cannot know which
  module's manager to reach.

**Real fix.** A registry in `GuardLib` that owns the subscription and dispatches to the manager registered
for the critter, so the eight forwarders and `GuardInit` exist once. That is a design change to five live
location subsystems with no test coverage at all.

**Sequencing.** Blocked on item 2: cover guard behaviour first (appearance, alert escalation, attack,
observation timer), then collapse. Doing it the other way round is an unverified rewrite of working content.

**Done when.** Guard subscription has one definition, proven by tests that pass before and after.

---

## 10. Mutable-globals allowlist becomes a boundary again

**Measurement.** `AngelScript.MutableGlobalsAllowedNamespaces` (formerly `Script.MutableGlobalsAllowedNamespaces`) listed 75 namespaces — nearly everything in the
project, so the mechanism no longer marks an exception.

**Steps.** No sweep. Adopt the rule: a module touched for any other reason either leaves the allowlist or
gains a header line saying why it stays.

**Outcome.** The rule is in `AGENTS.md` under the AngelScript conventions. The list shrinks as modules are
touched; nothing sweeps it.

---

## 2. Tests on the hot paths

**Measurement.** 26 test modules, 72 harness tests, covering 22 of 267 modules. 81 866 of 112 457 lines
(73 %) sit in modules with no test module at all — including `Combat.fos` (3 216 lines), `Main.fos`
(1 583), `GlobalmapGroup.fos` (1 744), `ChosenActions.fos` (1 342) and `Dialog.fos` (1 292).

**Steps.** Not coverage for its own sake. Three to four boundary cases per module, on the paths that change
most often:
1. `Combat` — hit chance and damage formulas at their boundaries.
2. `ChosenActions` — the action-queue state transitions.
3. `Main` — player enter/leave and map transfer.
4. `Dialog` — demand/result evaluation.
5. `GlobalmapGroup` — group membership changes.

**Outcome.** The harness went from 72 to 86 tests. Four suites landed, and two of the five planned modules
were substituted after reading them:

| Module | Suite | What it pins |
| ------ | ----- | ------------ |
| `Combat` | `Test_Combat` | damage threshold applied before percentage resistance, integer truncation, paired limbs reading the arms/legs settings |
| `Dialog` | `Test_Dialog` | the comparison direction of every numeric demand, strict-comparison boundaries, unknown operator failing closed |
| `GlobalmapGroup` | `Test_GlobalmapGroup` | zone boundaries under integer division, field extent, group snapshot comparing identity *and* order |
| `CritterState` | `Test_CritterState` | death → revive restoring life with positive health, revive idempotent on the living, wait predicates complementary |

**Substituted, with the reason.** `ChosenActions`'s testable helpers (`IsBusy`, `IsFree`) are under
`#if CLIENT` and the harness is a server; `Main`'s `CheckLook` and `CheckTrapLook` are stubs returning
`true`. Neither has a surface worth pinning today. `CritterState` took their place: it is the death and
revive path `Replication` is built on, and it was equally uncovered.

**Follow-on.** `Combat`'s coverage exists because `ApplyDamage`'s inline arithmetic was extracted into the
pure `ReduceDamage` — the same move item 7 needs, done on the smallest slice. Guard behaviour still has no
coverage, which is what blocks item 6.

---

## 1. Tables out of code into authored data

**Measurement.** `Worldmap::WorldmapInit` is a single 9 971-line function (1 323 `AddEncounter`, 1 601
`AddGroup`, 313 `AddLocationPid`); `Caravan::CaravansInit` is 1 073 lines and `FixBoy::InitFixBoy` 880.
About 10 % of hand-written script lines are content, not logic.

**Steps.**
1. Start with crafting (`FixBoy`, 880 lines): the most self-contained table, and the one that establishes
   the data format and the loader shape.
2. Then caravans, reusing the format.
3. `Worldmap` last, by then along a known path.

**The mechanism is already proven in this project.** `CritterTypes.fos` and `NpcBags.fos` read
`Game.ReadResource("...json")` and parse it with `Scripts/Json/`; the data lives in `Resources/ServerData/`.
The migration follows that path rather than inventing one.

**Safety net first — done.** `Test_FixBoy` now covers the table as it stands in code, so the migration is
verifiable rather than hoped-for: recipe ids unique and dense, every out item, resource and tool resolving
to a real proto, resources and tools in triples and skill checks in pairs, the first recipe reproduced field
by field, and a fingerprint over the whole table — 95 recipes, 15 090 experience, 276 resource entries,
728 resource units, 109 tool entries, 16 409 summed skill thresholds, 29 scripted recipes. The loaded table
must reproduce all seven.

**Three obstacles, with their answers.**
1. *Proto ids.* JSON carries the name and the loader hashes it, losing the compile-time check that
   `Content::Item::` gives today. The per-record proto resolution test is what replaces it.
2. *Skill checks.* `CritterProperty` values must resolve from a name; the loader needs a small explicit
   map for the properties the recipes actually use.
3. *Scripted recipes.* 29 recipes bind a callback. The loader needs a name → function registry in
   `FixBoy`, since a data file cannot hold a function handle.

**Stage 1 — crafting: done.** The 95 recipes live in `Resources/ServerData/CraftRecipes.json`; a 107-line
loader replaced the 881-line `InitFixBoy`, and `FixBoy.fos` went from 1548 lines to 877. Skill-check
properties and the 12 recipe scripts bind by name through closed registries that throw on an unknown name.
`Test_FixBoy` passes unchanged against the loaded table.

**What the net caught.** The first converter reproduced five of seven aggregates and lost 20 resource
entries: five `AddNeedResources` calls carry their brace on the next line after clang-format, and the parser
matched the literal `.AddNeedResources({`. The fingerprint failed before anything was migrated. This is the
reason the net comes first, and the same trap waits in the two remaining tables.

**Stage 2 — caravans (`CaravansInit`, 1 073 lines), measured.** 11 caravans built from ten call forms:
`SetupCaravan` (11), `SetupCaravanLeader` (11), `SetupCaravanLiderPosition` (22), `SetupCaravanCabs` (7),
`AddRoutePoint` (86), `AddGuardInfo` (58), `AddFollowerInfo` (6), `AddLootToCaravanCabs` (106),
`SheduleCaravan` (11), backed by eight record classes. Three `SetupCaravanCabs` calls pass
`Game.Random(a, b)`, so the table is not fully static — the data needs a min/max pair the loader rolls.
Wider per record than crafting; the format is the work, not the volume.

**Stage 3 — encounters (`WorldmapInit`, 9 970 lines), measured.** Tall *and* wide: `AddGroup` (1 961),
`AddEncounter` (1 322), `Fighting` (1 190), `SetZone` (892), `CheckProperty` (827), `AddItem` (769),
`LocationPid` (436), `AssignProperty` (432), `Special` (429), `CheckParam` (423), `AddCritter` (391),
`Dialog` (391). Twelve-plus chained methods, so the fingerprint has to cover every one of them before a
converter is written. This is the item that pays most — 86 % of an 11 587-line module — and the one that
must not be rushed.

**Method, proven twice.** Fingerprint the live table from the running game → write the converter →
require it to reproduce every aggregate → only then write the loader → re-run the tests unchanged.

**Done when.** All three tables live in `Resources/ServerData/`, their tests pass unchanged, and a designer
can change a recipe, a route or an encounter without recompiling scripts.

---

## 7. Cut the giant combat functions

**Measurement.** Of 4 040 functions, 3 637 are 30 lines or shorter; the problem is eighteen functions over
250 lines. Excluding the three data tables of item 1, the real candidates are
`MapperMain::InitializeTabs` (1 559), `Combat::CombatAttack` (1 392),
`ChosenActions::ChosenProcess` (1 084), `Combat::ApplyDamage` (726), `NpcPlanes::ProcessAi` (547) and
`Animation::ProcessTactics` (444).

**Steps.** Only on top of item 2's tests for the same module.
1. `Combat::CombatAttack` → target selection, hit resolution, damage, effects.
2. `Combat::ApplyDamage` → per-effect application.
3. The rest by the same pattern, one at a time.

**Started.** Two pure slices are out of `ApplyDamage` and covered by `Test_Combat`: `ReduceDamage` (the
per-shot arithmetic) and `ApplyArmorModifiers` (threshold and resistance adjustment, including the finesse
bonus that armour bypass silently cancels). `ApplyDamage` is 710 lines, `CombatAttack` still 1 393.

**What the rest needs.** Everything remaining in both functions touches the world — targets, weapons,
messages, broadcasts — so it cannot be extracted into pure helpers and tested the same way. The next slice
needs a behavioural fixture: a map with an attacker and a target, and assertions on the resulting state.
That fixture does not exist yet and is the real prerequisite, not more extraction.

**Done when.** No gameplay function exceeds 250 lines, or the exceptions carry a written reason.
