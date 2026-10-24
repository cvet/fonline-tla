# Project documentation index

Game-side documentation for FOnline: The Life After. Start with
[AGENTS.md](../AGENTS.md) for agent authority and essential invariants or the root
[README](../README.md) for human setup. The separately owned
[Engine docs](../Engine/Docs/en/index.md) define reusable engine contracts.

## Current task guides

| Question | Read |
| --- | --- |
| Build, launch, tests, warnings, process cleanup, logs, CI or packages | [BuildAndLaunch](BuildAndLaunch.md) |
| Script sides, dispatch, globals, state, stacking, sounds or day tint | [Scripts](Scripts.md) |
| Russian script headers/comments, naming, formatting and safe refactoring | [ScriptStyle](ScriptStyle.md) |
| Nullable handles, components, Chosen and native boundary validation | [Nullability](Nullability.md), [tool README](../Tools/NullableEstimate/README.md) |
| Content inputs, localization, generated GUI or secure-channel config | [ContentWorkflow](ContentWorkflow.md) |
| Native extension files, bindings and CMake roles | [NativeExtensions](NativeExtensions.md), then [Engine instructions](../Engine/AGENTS.md) |
| Find a gameplay owner, caller or suite | [Systems](Systems.md) |
| Critter animations, offsets, motion and project/native split | [Animation](Animation.md) |
| AI-control/MCP launch, screenshots and quest tests | [AiControl](AiControl.md) |
| Bridge wire schema, observation, actions and privileged QA commands | [AiControlProtocol](AiControlProtocol.md) |
| Update instructions, audit docs/session evidence or reconcile an Engine bump | [DocumentationMaintenance](DocumentationMaintenance.md) |
| Script-quality checks, heuristics and ratchet | [ScriptQuality tool README](../Tools/ScriptQuality/README.md) |

## Plans and dated references

Plans describe intended work and dated progress. Recheck implementation, current
requirements and revision before treating an old status/count as accepted today.

| Document | Role and boundary |
| --- | --- |
| [AuditPlan](AuditPlan.md) | Ten findings measured in the 2026-09-02 audit, outcomes and remaining work. |
| [Refactoring](Refactoring.md) | Historical rounds, standing project decisions and deferred items; current contracts live in the guides above. |
| [ReanimationPlan](ReanimationPlan.md) | Current entry to the campaign proposal; distinguishes existing tools from proposed catalog/SOAK infrastructure. |
| [EngineSettingsAudit](EngineSettingsAudit.md) | 2026-10-16 static register; source locations and acceptance are historical, not today's Engine API. |
| [Project-owned engine policy plan](Plans/2026-10-14-project-owned-engine-policy.md) | Dated ownership extraction assignment. |
| [Settings audit plan](Plans/2026-10-16-engine-settings-audit.md) | Dated source/consumer audit assignment. |
| [Resource manager plan](Plans/2026-10-20-resource-manager.md) | Dated resource ownership/refactoring assignment. |
| [Engine update/publication plan](Plans/2026-10-21-engine-update-publication.md) | Historical validation/publication packet; no current publication authority. |
| [Sprite offsets plan](Plans/2026-10-22-sprite-frame-offsets.md) | Dated terminology and visual displacement contract work. |

## History and audit evidence

| Document | What it preserves |
| --- | --- |
| [Refactoring journal](History/Refactoring-2026.md) | Dated R2/R3 batches, engine follow-ups and bug hunts; read through its section map. |
| [AI-control runs/fixes](History/AiControl-2026.md) | Earlier runtime recipes/results and text-key fix narratives, separated from current procedure. |
| [Original campaign proposal](History/ReanimationPlan-2026.md) | Complete original roadmap/protocols/matrices; old Sync/branch/gate assumptions are explicitly superseded. |
| [2026-10-24 documentation audit](History/DocumentationAudit-2026-10-24.md) | Corpus/quality metrics, corrections, preservation and sanitized session findings for this refresh. |

## Maintenance convention

Update the owning guide in the same working change as behavior. Keep task
narrative and old pass counts out of current instructions. Continue existing
document language: general project/agent pages are English, `ScriptStyle.md`
and script comments/headers are Russian; contract identifiers remain English.
Size review, source ownership, preservation and link checks are defined in
[DocumentationMaintenance](DocumentationMaintenance.md).
