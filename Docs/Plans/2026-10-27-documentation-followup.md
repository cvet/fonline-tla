# Documentation follow-up: tooling, content audit, quest map

Follow-up to [2026-10-24 gameplay docs](2026-10-24-gameplay-systems-docs.md),
authorized as "do the recommended package in order". Dated assignment;
re-establish scope and authority via [AGENTS.md](../../AGENTS.md) before
reuse. Documentation/tooling only — no game logic, content, config, Engine
or save changes; no Git actions. Baseline: project `e2b5b90b0` (plus the
uncommitted 2026-10-24 documentation edits), Engine pin `57424cb5d`.

## Ordered steps

1. **Preserve the audit tooling in `Tools/`.** The 2026-10-24 link checker
   and quest-registry generator live only in ignored
   `Workspace/DocumentationAudit/` and are referenced by maintained docs.
   Deliver `Tools/DocsCheck/check_docs.py` (whole-corpus Markdown link/
   anchor/UTF-8/heading audit, Engine and generated trees excluded) with a
   README and a `Check :: Docs Links` VS Code task; port the registry
   builder to `Tools/QuestInventory/build_quest_inventory.py` with a
   versioned `quests_inventory.tsv` output and a `Generate :: Quest
   Inventory` task. Update `Docs/Quests.md` and
   [DocumentationMaintenance](../DocumentationMaintenance.md) to point at
   the maintained tools.
2. **Content-quality contract tests** (extend `Tools/ContentQuality/`,
   unittest style, ratcheted like `test_text_pack_parity.py`):
   `test_quest_text_coverage.py` — every `Group = Quests` property must
   have `QName`/`QDesc` and state entries in both Quest packs; gaps are
   recorded as an explicit baseline, never silently expanded.
   `test_english_text_surface.py` — English surfaces (`Texts/*.engl.fotxt`
   entries and `[Text engl]` blocks in dialogs) must not contain Cyrillic;
   known offenders captured in a baseline that only shrinks.
3. **Semi-automatic quest map.** `Tools/QuestInventory/build_quest_transitions.py`
   extracts state-transition tables from `.fodlg` demand/result lines into a
   versioned `quest_transitions.tsv`; a generated `quest_chains.tsv`
   aggregates per-city quests and cross-location chains. A compact
   data-backed "Quest chains" section lands in [Quests](../Quests.md).
4. **Owner decision table** for discrepancies D-1..D-7 (disabled Caravan
   init, unreachable `KlamKuklachev`, stale `QuestRuntime` config entry,
   unused `Player.FixBoyDefaultExperience`, hell map pointing at the
   replicator, password/tag-count checks, `GetCarCost` stub) — recorded
   below with options and risk; **no code changes without a separate
   authorization**.

## Acceptance

- `py -3 Tools/DocsCheck/check_docs.py` exits 0 on the current corpus and
  flags injected bad links/anchors in a self-test.
- `py -m pytest Tools -q` (the existing `Test :: Python Tools` task) passes
  including the two new ContentQuality modules; baselines match the current
  content exactly (documented counts).
- Both quest tools regenerate byte-stable TSVs; `Quests.md` cites the
   maintained paths; the decision table is complete.
- Docs-only verification per [DocumentationMaintenance](../DocumentationMaintenance.md):
  claim checks, link audit, UTF-8, `git diff --check`, status/index.

## Owner decision requests (D-1..D-7)

Originally recorded on 2026-10-24 in the task's private workspace log; that
directory was found removed on 2026-10-27 (not deleted by this task), so the
findings are carried here in full. Each row needs an owner choice before any
code change task is opened.

| Id | Finding | Options | Risk of doing nothing |
| --- | --- | --- | --- |
| D-1 | `QuestRuntime` listed in `AngelScript.MutableGlobalsAllowedNamespaces` with no such namespace | (a) drop the entry; (b) keep until a sweep task | None at runtime; list misleads readers |
| D-2 | `Caravan::CaravansInit()` commented out in `Main.fos` (route-setup null-reference warning) | (a) debug + reactivate (game-code task); (b) retain dormant scheduler and explicit reference-only inventory | Scheduled escorts do not start normally; callable dialog handlers still require separate tracing |
| D-3 | `Player.FixBoyDefaultExperience` declared, no consumer | (a) remove setting (config migration); (b) wire it as the JSON default | Dead config misleads balance edits |
| D-4 | `HellMapPid = repl1` with TODO to restore `repl_hell` | (a) restore hell map (game-code task); (b) drop the TODO and rename the concept | "Hell" death penalty is the ordinary start map |
| D-5 | Password is not sent by registration/login RPCs and the traced Engine admission path does not validate it; tag-skill count is client-only | Separate gameplay/account task: choose the intended authentication contract and server tag-count validation; transport encryption alone does not supply authentication | Current name-based login and client-only tag-budget checks remain; do not assume an unseen Engine password gate |
| D-6 | `KlamKuklachev` quest unreachable (no NPC binding) | (a) bind an NPC (content task); (b) remove dialog/module/texts; (c) keep as dormant example | Dormant content, quest text visible in packs |
| D-7 | `GetCarCost` world-count stub (constant 10) | (a) restore `GetWorldItemCount`-based pricing (game-code task); (b) leave documented | Car pricing ignores scarcity |

## Progress

- 2026-10-27 (complete):
  1. `Tools/DocsCheck/` delivered (`check_docs.py` + README, `Check :: Docs
     Links` task); corpus audit: 31 tracked Markdown files, 0 findings;
     selftest verified; [DocumentationMaintenance](../DocumentationMaintenance.md)
     final-review section now references it. `Tools/QuestInventory/`
     delivered (`build_quest_inventory.py`, README, `Generate :: Quest
     Inventory` task) with a versioned `quests_inventory.tsv`.
  2. `Tools/ContentQuality/test_quest_text_coverage.py` (4 tests: state
     texts for all 165 properties; QName/QDesc ratchet = 2 known; Quest-pack
     english-gap ratchet = 2 known; no dead pack entries) and
     `test_english_text_surface.py` (4 tests: per-pack Cyrillic ceilings
     21/104/49/30/783/681; 481 dialogs with Cyrillic `[Text engl]`; 63
     dialogs without the block). `Test :: Python Tools` (pytest over Tools):
     **164 passed**.
  3. `build_quest_transitions.py` + `Generate :: Quest Transitions` task:
     1669 transition rows and 159 chain rows, byte-stable regeneration
     verified; data-backed "Quest chains" section added to
     [Quests](../Quests.md) (46 cross-location quests; Den 41 / NCR 21 /
     Vault City 20 top cities; `TODO` city = disabled story-line quests).
     Registry correction vs the 2026-10-24 bash version: `KlamSmilyGecko`
     and `V13Dclaw` were false "script-only" positives (substring matches
     against `KlamSmilyGeckoCounter`/`V13DclawEggs`); correct classes are
     158 reachable / 1 unbound / 6 no-dialog.
  4. Decision table above completed; awaiting owner choices. No code or
     content changes were made for D-1..D-7.
- Verification: pytest Tools 164 passed; docs corpus audit 0 findings;
  both quest generators byte-stable on rerun; `git diff --check` clean.
  Docs/tooling-only change — no native build, bake or runtime session.

## Subsequent review

The [2026-10-28 review](2026-10-28-documentation-review.md) found that those green
checks did not establish all claimed behavior: the selftest could overwrite a
fixed file, the quest extractor dropped predicates and cross-quest actions,
and aggregate English-text ceilings admitted same-count substitutions. The
corrected tools have independent behavioral regressions and explicit syntax
limits. The revised answer index has 1684 rows and 48 properties with bindings
in multiple map-file families; neither count proves runtime reachability.
The dated counts above preserve the original extractor/checker result.
