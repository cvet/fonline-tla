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
| 8 | One aggregate verification task | S | planned |
| 3 | Quality gates in CI | S | planned |
| 9 | Split the journal from the plan, add a systems map | M | planned |
| 4 | Record the single-threaded constraint | S | planned |
| 5 | Generated and test scripts into their own folders | S | planned |
| 6 | Fold the copied guard init back into `GuardLib` | S | planned |
| 10 | Mutable-globals allowlist becomes a boundary again | rule | planned |
| 2 | Tests on the hot paths | L | planned |
| 1 | Tables out of code into authored data | XL | planned |
| 7 | Cut the giant combat functions | L | planned |

---

## 8. One aggregate verification task

**Measurement.** `.vscode/tasks.json` holds 43 tasks and no aggregate; the full pre-handoff chain is
reassembled by hand every session.

**Steps.**
1. Add `Verify :: All`, chaining through `dependsOn` in order: bake → build targets → engine unit tests →
   script harness → validators → formatters.
2. Keep every step an existing task where one exists, so there is one definition per step.

**Done when.** A single task runs the whole chain and its step order matches what CI runs (item 3).

---

## 3. Quality gates in CI

**Measurement.** CI runs formatting, nullable contracts, engine unit tests, script compilation, baking and
the platform builds. It does not run the script harness (72 tests), `validate_scripts --ratchet`,
`Tools/ContentQuality` (19 tests) or the `Tools/AiControlMcp` static suite.

**Steps.**
1. Add a `quality-gates` job that bakes, then runs the four gates above.
2. Reuse the ratchet baseline as-is; the job fails only on new violations.

**Done when.** A pull request that adds a script-quality violation, a harness failure or a content-quality
failure is red in CI.

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

**Done when.** A newcomer can name the ten main systems and their entry points without opening a `.fos`.

---

## 4. Record the single-threaded constraint

**Measurement.** With `Server.SingleThreadedLogic = False` the harness still reports 72/72 but logs 794
`Entity access without sync` exceptions and 253 time events stopped by exception — the throws are
recoverable at the job frontier, so the breakage is invisible in the exit code. `Server.WorkerThreads = 6`
remains in the config and looks live.

**Steps.**
1. State the constraint in `AGENTS.md` beside the synchronization section.
2. Mark `Server.WorkerThreads` in `TLA.fomain` as inactive while the mode is on.

**Done when.** Both files say that the multithreaded configuration is not supported by the current scripts.

---

## 5. Generated and test scripts into their own folders

**Measurement.** 294 hand-written modules sit flat beside 27 352 lines of generated `GuiScreens.fos` and
`Content.fos`; `Scripts/Json/` proves subdirectories bake.

**Steps.**
1. Move the generated pair to `Scripts/Generated/` and update the GUI generator's output path.
2. Move `Test_*.fos` and `Testing.fos` to `Scripts/Tests/`.
3. Update the tools that address these files by path.

**Done when.** A search over `Scripts/*.fos` returns only hand-written gameplay code.

---

## 6. Fold the copied guard init back into `GuardLib`

**Measurement.** 463 duplicated eight-line windows across the scripts, 1 060 occurrences. `GuardInit` is
copied into five modules and three of the five bodies are byte-identical, though `GuardLib.fos` exists for
exactly this.

**Steps.**
1. Collapse the three identical copies onto `GuardLib`.
2. Diff the two divergent copies; either parameterize the difference or record it as a drift bug.

**Done when.** Guard behaviour has one definition, or every remaining copy carries a written reason.

---

## 10. Mutable-globals allowlist becomes a boundary again

**Measurement.** `Script.MutableGlobalsAllowedNamespaces` lists 75 namespaces — nearly everything in the
project, so the mechanism no longer marks an exception.

**Steps.** No sweep. Adopt the rule: a module touched for any other reason either leaves the allowlist or
gains a header line saying why it stays.

**Done when.** The rule is written down; the list shrinks as a side effect of other work.

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

**Done when.** Each of the five modules has a `Test_*.fos` suite and the harness total reflects it.

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

**Done when.** A designer can change an encounter, a route or a recipe without recompiling scripts, and the
tables are reachable by the content validators.

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

**Done when.** No gameplay function exceeds 250 lines, or the exceptions carry a written reason.
