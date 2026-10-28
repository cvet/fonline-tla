# Gameplay Systems Documentation

Task plan for documenting TLA's implemented gameplay systems, mechanics,
quests, dialogs and content contracts from the actual repository content.
Dated assignment; re-establish scope and authority via [AGENTS.md](../../AGENTS.md)
before reuse. Working evidence originally lived in ignored
`Workspace/DocumentationAudit/` (manifest, coverage, sources, discrepancies,
verification); **that directory was found removed on 2026-10-27** — the
durable artifacts it backed now live in the repository (these guides and
`Tools/QuestInventory/`), and the open findings are carried by the
[2026-10-27 follow-up plan](2026-10-27-documentation-followup.md).
No game logic, content, config, Engine or save changes;
no Git actions.

Baseline: project `e2b5b90b0ea407a68e4672825446664b8a5f5ea2`, Engine pin
`57424cb5d2ac132b1fa8ba83e353d07cb6ca75e0`, both clean on `master`.

## Goal and owners affected

New focused deep-dive guides in `Docs/`, linked from [Systems](../Systems.md)
and indexed in [Docs/README.md](../README.md). Existing owners
([Scripts](../Scripts.md), [ContentWorkflow](../ContentWorkflow.md),
[Animation](../Animation.md), [BuildAndLaunch](../BuildAndLaunch.md)) are
extended only where they lack the contract detail; no parallel reference
duplicating them.

## Planned documents

| Document | Scope |
| --- | --- |
| `Docs/Combat.md` | Attack pipeline, AP, hit chance, damage/armor/criticals, conditions; `Combat`, `CritterActions`, `CritterState`, `CritterProps`. |
| `Docs/Dialogs.md` | Dialog runtime, `.fodlg` format and baking, `Dialog` handler library, `NpcDialog`. |
| `Docs/Quests.md` | Quest architecture (critter-property state, text pack, PipBoy) and per-quest technical cards. |
| `Docs/Character.md` | SPECIAL/skills/perks/level progression (`Parameters`, `Perks`, experience). |
| `Docs/Items.md` | Item prototypes/properties, stacks, equipment, containers, movement, deterioration/repair. |
| `Docs/Economy.md` | Barter, currencies, `FixBoy` crafting, repair services. |
| `Docs/World.md` | Locations, entrances/transfers, global-map groups, worldmap encounters, vehicles. |
| `Docs/PlayerLifecycle.md` | Registration/login, death/respawn, replication. |
| `Docs/NpcAI.md` | `NpcPlanes`/`MainPlanes`, behavior patterns, guards. |

Coverage is prioritized: the pilot (Combat plus one full quest card) sets
format and evidence bar first; remaining areas are processed in the order
above, and anything not completed is recorded as an explicit gap in
`Workspace/DocumentationAudit/coverage.tsv` and the final report rather
than silently dropped.

## Method and acceptance

- Every substantial claim is traced source-first: entrypoint → registration →
  validation → state change → events/side effects → result. Static analysis
  is labeled as such; no runtime claims without runtime observation.
- Attachments are verified (pack `InputDirs`, dialog links, proto script
  bindings); formulas documented with input sources, units, modifier order
  and clamps from `TLA.fomain` settings.
- Docs-only verification: claim re-check against source, local link/anchor
  audit, UTF-8, `git diff --check`, status/index inspection. No native build
  or mutating `Verify :: All` for Markdown.

## Progress

- 2026-10-24 (complete): all nine planned guides delivered — `Combat`,
  `Dialogs`, `Quests`, `Character`, `Items`, `Economy`, `World`,
  `PlayerLifecycle`, `NpcAI` — plus the quest registry
  (`Workspace/DocumentationAudit/quests_inventory.tsv`, 165 properties:
  158 reachable / 1 unbound / 4 no-dialog / 2 script-only, generator script
  alongside), a content-format quick-reference section in
  [ContentWorkflow](../ContentWorkflow.md), and routing updates in
  [Systems](../Systems.md) and [Docs/README](../README.md).
- Method notes: three research agents died on a usage limit mid-task
  (Character/World/quest inventory); those areas were researched directly in
  the main thread instead. The four completed agent reports (Items, NpcAI,
  Economy, PlayerLifecycle) had their load-bearing formulas spot-verified
  against source before use (log in `Workspace/DocumentationAudit/verification.md`).
- Findings recorded as discrepancies: stale `QuestRuntime` namespace entry,
  disabled Caravan init (`Main.fos:59`), unused `Player.FixBoyDefaultExperience`,
  hell map pointing at the start replicator (TODO), password absent from
  script-level login, unreachable `KlamKuklachev` quest content.
- Verification: claim re-checks during writing; link/anchor audit, UTF-8,
  `git diff --check` and status/index inspection at completion (results in
  the workspace verification log). No native build or runtime session —
  static documentation pass, boundaries labeled in each guide.

## Subsequent review

The [2026-10-28 review](2026-10-28-documentation-review.md) corrected substantive
formula, lifecycle, ownership, availability and coverage errors in these guides.
The original delivery narrative above is historical evidence, not acceptance of
every claim. Quest registry classifications now describe binding references,
and the answer index preserves repeated/cross-quest conditions. Current static
limits and gameplay discrepancies live in the corrected guides and review plan.
