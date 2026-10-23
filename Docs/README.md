# Documentation index

Game-side documentation for FOnline: The Life After. The engine keeps its own set under
`Engine/Docs/`, indexed by `Engine/Docs/README.md`; nothing here duplicates it.

Start with [../AGENTS.md](../AGENTS.md) for repository practices, then with the map below.

## Engine build configuration

TLA enables `FO_DATA_SOURCE_DAT`, `FO_DATA_SOURCE_ZIP`, `FO_IMAGE_FRM`, `FO_IMAGE_RIX` and
`FO_AUDIO_ACM` in `CMakeLists.txt` for its authored Fallout archives, images and sounds. PNG, TGA and FOFRM
importers are built in. `Server.DbStorage = Memory` needs no optional database provider.
To select persistent storage, enable its positive `FO_DATABASE_JSON`, `FO_DATABASE_SQLITE`
or `FO_DATABASE_MONGO` CMake option and reconfigure. Engine `2026.1.26-dev` requires new
empty storage for JSON and SQLite; it does not convert their old formats.
See the Engine's [component selection](../Engine/Docs/en/how-to/build/project-configuration.md#optional-native-components)
and [storage upgrade boundary](../Engine/Docs/en/explanation/persistence/index.md#storage-formats-and-upgrade-boundary).
After an Engine update, rebuild and rebake matching client/server outputs before running them.

Town and quest-camera previews use the Engine's `Player.ViewMapArea` through
`Scripts/MapPreview.fos`, with an inclusive hex radius and live subject updates.
Global-map previews keep the controlled critter attached; local quest cameras use
`Player.SwitchCritter(null)` temporarily and restore the same critter without moving it.
The TownView screen returns through `Player.ReturnFromViewMap` or `Player.SwitchCritter`;
city entry repeats the normal server access checks. Preview state is runtime-only on
`Player`, and disappearing target maps return the player automatically. Matching rebuilt
client/server outputs and rebaked metadata/effects are required for network `0.0.76`.

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
| [EngineSettingsAudit.md](EngineSettingsAudit.md) | Complete native settings register, relevance evidence, and remaining ownership migrations. |
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
