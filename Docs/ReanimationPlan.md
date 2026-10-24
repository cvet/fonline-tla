# TLA reanimation and stabilization campaign

This is the current **entry to a campaign proposal**, not proof that the campaign
has been completed or that its proposed infrastructure exists. The complete
earlier proposal, including workstream detail, stage estimates, SOAK definition,
quest matrices and manual protocols, is preserved in
[History/ReanimationPlan-2026.md](History/ReanimationPlan-2026.md).

For any assigned stage, re-establish requirements, source owners, fixtures,
baseline and acceptance in a task plan before implementation. Current instructions
are [AGENTS.md](../AGENTS.md), [Scripts](Scripts.md),
[BuildAndLaunch](BuildAndLaunch.md) and [ContentWorkflow](ContentWorkflow.md).
Historical claims do not override them.

## Current implementation boundary

The checkout has the script harness (`Scripts/Testing.fos`, `Scripts/Tests/`),
quality/nullable validators, local `Verify :: All`, AI-control/MCP tooling and a
data-driven `QUESTS` dictionary in `Tools/AiControlMcp/tla_quest_runner.py`.
Its actual `--list` and source define available specs; previous successful runs
do not qualify today's revision.

The proposed `catalog.yaml`, `KnownIssues.md`, batch quest runner, aggregate
results tool and nightly four-hour SOAK job are **not implemented by this plan**
and were not found among current tracked project tools/docs/workflow definitions
during the 2026-10-24 documentation audit. Do not execute their example paths as
existing commands or claim CI coverage from their proposed descriptions.
The actual CI does not run the script gameplay harness; see
[the build guide](BuildAndLaunch.md#select-verification-by-the-change).

## 1. Vision & Guiding Principles

Restore existing gameplay: login, travel, town entry, dialogs/quests, combat,
trade, crafting and skills, with clean server runtime. This does not authorize new
content, balance redesign or a migration to another scripting backend. Preserve
serialized identities and verify intended behavior before a fix. The original
scope/exclusions and proposed completion definition remain
[in the proposal](History/ReanimationPlan-2026.md#1-vision--guiding-principles).

The supported scripts run with `Server.SingleThreadedLogic=True`; old sections
about adding `Sync::Lock...` / `[[Async]]` describe a superseded configuration.
Native lifetime and callback reentrancy still need owner proof. Scripts and
module headers use Russian comments; general project/native docs remain English.

## 2. The Standing Regression Gates

Use [BuildAndLaunch](BuildAndLaunch.md#select-verification-by-the-change) for
current gates and exact task labels, not a frozen test count. The old G1–G9
table and [tiering/SOAK proposal](History/ReanimationPlan-2026.md#2-the-standing-regression-gates)
are retained for campaign design. In particular:

- Documentation-only changes validate facts, links, structure and preservation;
  they do not require running a quest merely because the old T0 table says G9.
- All expected tests must actually execute; zero failures plus zero exercised
  cases is not acceptance. Inspect terminal counts and runtime diagnostics.
- `Verify :: All` is a local task and includes mutating formatters. CI has a
  different job graph. A nightly SOAK is a future deliverable requiring a real
  runner, isolated storage, observed load and a retained report.
- Force bake follows Engine/property-layout/stale-output boundaries; do not copy
  the old “two cases only” restriction over the current integration workflow.

## 3. Workstreams

The [eight proposed tracks](History/ReanimationPlan-2026.md#3-workstreams) cover
system testing, quest coverage, bug triage, refactoring, documentation, content
validation, tooling/CI and Engine upkeep. They remain a decomposition aid.
Choose the active track from the owner's assignment; do not start every track
or enable disabled subsystems incidentally.

Refactor current owners rather than chasing size metrics. Distinguish a proven
bug from an unresolved gameplay decision; keep migration breadcrumbs until
their exact purpose has been inspected. [Refactoring](Refactoring.md) records
historical rounds and decisions; [AuditPlan](AuditPlan.md) retains its dated queue.

## 4. Staged Roadmap

The [original stages](History/ReanimationPlan-2026.md#4-staged-roadmap) are
foundation, system smoke/triage, regional quests, deeper hardening and final
content/soak/docs acceptance. Stage status must come from a fresh source/revision
and evidence ledger, not the proposal's old “green” counts. Keep estimates and
historical progress separate from accepted delivery.

## 5. The Repeatable Stage / Loop Templates

The [full original protocols](History/ReanimationPlan-2026.md#5-the-repeatable-stage--loop-templates)
retain fix/verify/document loops, per-region quest batches, triage tiers, resumption,
manual quest evidence and differential checks. Apply them only after reconciling
their assumptions with the current owners:

- Engine updates keep the owner's branch policy; follow
  [revision reconciliation](DocumentationMaintenance.md#engine-submodule-updates),
  not the old detached `checkout <SHA>` recipe.
- Local ignored progress files are evidence only when they exist and their
  revision matches. Missing old `Build/_audit/progress.md` is not current status.
- A rollback never authorizes reverting user/other-agent work. Preserve the
  failing attempt and exact task-owned diff; follow current Git authority.
- Real quest acceptance observes the action's fresh completion/state transition.
  Privileged setup is labeled as injected state. Cleanup/restoration must account
  for authored side effects that cannot be rolled back generically.
- Persistence/reconnect checks use an isolated persistent provider; Memory storage
  only keeps data within one server process.

## 6. Coverage Matrices

The [system and regional matrices](History/ReanimationPlan-2026.md#6-coverage-matrices)
are historical/planning inventories. Validate current content IDs, quest flags,
test registrations, prerequisites and manual exclusions before using their
counts. Record expected versus exercised coverage, including blocked/manual
cases; a reusable runner alone does not prove a region's content rollout.

## 7. Risk Register

Review the [original risks](History/ReanimationPlan-2026.md#7-risk-register) for
the assigned work. Re-evaluate causes that mention removed synchronization or
unimplemented tools. Keep runtime correctness, manual quest acceptance, native
failures, visual inspection, performance and platform qualification separate.

## 8. Definition of Done

An assigned slice is complete only when its explicit scope and current gates
pass, ordinary player behavior is exercised, persistence is checked where
required, and owners/docs/report agree on the final revision. Open/manual cases
remain explicit. The [campaign-wide proposal](History/ReanimationPlan-2026.md#8-definition-of-done)
requires a separate adopted scope; this documentation refresh does not claim to
have achieved it or enable publication.

## Appendix: Key references

Use [Docs/README.md](README.md) for current guides and
[the preserved proposal](History/ReanimationPlan-2026.md#appendix-key-references)
for its complete original reference list. Proposed tools are not executable
instructions until implemented and qualified.
