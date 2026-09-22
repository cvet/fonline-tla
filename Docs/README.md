# Documentation index

Game-side documentation for FOnline: The Life After. The engine keeps its own set under
`Engine/Docs/`, indexed by `Engine/Docs/README.md`; nothing here duplicates it.

Start with [../AGENTS.md](../AGENTS.md) for repository practices, then with the map below.

## Orientation

| Document | What it answers |
| -------- | --------------- |
| [Systems.md](Systems.md) | What the gameplay systems are, where they live, what they talk to, what covers them. Read before opening a `.fos`. |
| [ScriptStyle.md](ScriptStyle.md) | How a `.fos` module is written: header block, comments, naming, structure. |
| [Animation.md](Animation.md) | Critter animation: state and action anims, how the client plays them. |
| [AiControl.md](AiControl.md) | The AI control bridge and its MCP adapter — driving a real client for tests and playtests. |

## Plans and status

| Document | What it answers |
| -------- | --------------- |
| [AuditPlan.md](AuditPlan.md) | The ten findings of the 2026-09-02 audit: measurement, steps, status. The current work queue. |
| [Refactoring.md](Refactoring.md) | Standing decisions and the open remainder of the Scripts refactoring rounds. |
| [ReanimationPlan.md](ReanimationPlan.md) | The staged campaign to bring the whole game into working order: gates, workstreams, stages. |

## History

Session narrative is kept out of the plans so that a plan stays readable as a plan.

| Document | What it holds |
| -------- | ------------- |
| [History/Refactoring-2026.md](History/Refactoring-2026.md) | Batch reports, engine-bump follow-ups and bug hunts from refactoring rounds R2 and R3. |

## Conventions

- Documentation here is written in English, like `AGENTS.md`. Script comments and module headers are
  Russian — see [ScriptStyle.md](ScriptStyle.md).
- A plan records decisions and what is still open. What happened in a session goes to `History/`.
- When behaviour changes, the owning document changes in the same commit.
