# FOnline: The Life After — Agent Instructions

Read this project guide fully, then the task's owning documents. Human entry:
[README.md](README.md); full index: [Docs/README.md](Docs/README.md).
`CLAUDE.md` and `.github/copilot-instructions.md` point here; do not maintain
competing instruction bodies.

## Start and authority

1. Confirm checkout, branch, requested outcome and dirty files. Inspect the project
   and `Engine/` independently; preserve user and other-agent edits. Re-anchor from
   the plan, current source and diff after a handoff or compaction.
2. Read owners, validators and callers before designing a change. Requirements
   establish intended behavior; source establishes current behavior. Historical
   logs, summaries and worker reports are evidence, not new action authority.
3. Carry the authorized scope through implementation and verification. Resolve
   routine choices from source; ask for material missing requirements or actions
   outside scope. If a required source is unavailable, report it and wait before
   synthesizing conclusions.
4. Before non-trivial implementation, write a plan in `Docs/Plans/`, including
   plans produced by workflow skills. Update its scope, steps, decisions,
   acceptance and actual verification results as work proceeds. Update affected
   documentation alongside the changes; do not defer plans or docs to the final
   handoff. Follow [the working procedure](Docs/DocumentationMaintenance.md#planning-and-documentation-during-work).
5. Put private task logs, screenshots, scripts, dumps, drafts and worker inputs in ignored
   `Workspace/<task-id>/`. Standard tool outputs keep their owning paths; permanent
   delegation history follows the governing launcher procedure.

- No `git add`, commit, push, merge, destructive Git operation, publication or
  deployment without explicit action authority. Prepare reviewable local edits;
  “prepare for commit” does not mean create a commit. Past permissions do not
  authorize a new task. Never revert work you did not make.
- Stay on the requested project branch/worktree. Engine-only branch/history
  instructions apply only to Engine. Normal Engine updates keep its `master`
  branch; do not detach or move the project branch incidentally.
- Chat with the owner in Russian unless requested otherwise. General project/
  agent docs and native C++ stay English; keep existing documents in their own
  language (`Docs/ScriptStyle.md` is Russian). Script comments and module headers
  are Russian; translate existing English comments when touching the module.
  Serialized metadata, IDs, text keys and identifiers stay English.
- Do not read credentials for unrelated maintenance or copy secrets/raw private
  sessions into source, chat or reports. The base config's public development
  channel pair is for local use; production keys remain host-owned.

## Choose the owner and preserve behavior

- TLA stays **AngelScript** (`Scripts/*.fos`); Managed scripting is disabled.
  `Scripts/Core/` is TLA's utility library. Do not import the C# architecture or
  gameplay/content names of a sibling project as a migration requirement.
- Gameplay, quests, AI, GUI and content policy belong to scripts/authored assets;
  project native bridges belong to `SourceExt/`, registered in CMake; reusable
  Engine capability belongs to `Engine/` only when the task calls for it.
  Read [Engine/AGENTS.md](Engine/AGENTS.md) explicitly before native/Engine work.
  Its C++ checklist applies to `SourceExt/`; its release procedures apply to Engine.
- Refactor for a demonstrated responsibility or defect, preserving behavior unless
  fixing a verified bug. Do not reshape code solely to satisfy size metrics.
  Never bulk-delete commented migration breadcrumbs; inspect each block and its
  history. Ask for unresolved gameplay/design choices, and flag player acceptance
  still needed. Do not hide invariant failures with broad guards/defaults.
- Match adjacent naming, declaration order and semantic spacing. A formatter does
  not choose meaningful groups. Verify native ownership and every throwing call
  before introducing `noexcept`; use current Engine pointer/invariant vocabulary.
- Properties, proto IDs, text keys and save/network-visible data are contracts.
  Check consumers and migration/version implications before changing them. Do not
  rename toward another game or silently reinterpret valid units/defaults.

## Essential script and content invariants

- The supported server uses `Server.SingleThreadedLogic=True`; scripts take no
  explicit entity cover. Do not reintroduce `Sync` or `[[Async]]`. Disabling this
  mode is a separate script migration; a passing harness alone does not prove it.
- Every script directory is explicitly listed in the `Metadata` **and** `Scripts`
  pack `InputDirs` in `TLA.fomain`; baking does not recurse. Use `#if SERVER`,
  `#if CLIENT`, `#if MAPPER`, matching namespaces and dispatcher-owned entrypoints.
- For a touched namespace in `AngelScript.MutableGlobalsAllowedNamespaces`, move
  mutable state to its owner and drop the exception, or explain the necessary
  global lifetime in one module-header line. Do not sweep the list incidentally.
- Use `T?` for real absence, narrow locals, guard components with `Has<Component>`
  and `Game.Chosen` with `HasChosen`. Keep Event/RemoteCall nullable parity.
  [Nullability.md](Nullability.md) owns examples and checks.
- Count-aware item operations go through `ItemStacks::`; Engine item calls do not
  stack. Sound names go through `Sounds::Play`; client/mapper day tint through
  `DayColor` and `Map.SetDayColors`. See [project adapters](Docs/Scripts.md#project-adapters-that-must-not-be-bypassed).
- Engine settings are read-only configuration. Runtime state belongs to its
  subsystem, saved client options to `UserOptions::Save` with `Group.Name` keys.
- Edit authored inputs. GUI code belongs in `.fogui`, generated output in
  `Scripts/Generated/GuiScreens.fos`; use the Python generator. The narrow paired
  source/output exception and regeneration conditions are in
  [ContentWorkflow](Docs/ContentWorkflow.md#gui-generation). Never hand-edit
  `Content.fos`, `VERSION`, baked data or cache. Keep expected `russ engl` parity.

## Build, verify and finish

Exact tasks/arguments are in `.vscode/tasks.json`; the full procedure is
[BuildAndLaunch](Docs/BuildAndLaunch.md). Configure with `cmake --preset auto`,
then `cmake --build Build/Auto --config RelWithDebInfo --target <target>`.
Verify a real Python 3 interpreter and use UTF-8 for Cyrillic.

- Compiler, bake and native build warnings are failures. Keep the existing
  script-quality ratchet distinct from compiler diagnostics; never lower a gate
  or inflate its baseline to obtain green.
- Script/content changes compile, bake and run owning checks; Engine bumps and
  broad integration use `Verify :: All`. Documentation-only changes validate
  claims, links, preservation and diff without a native build.
- Build **and execute** covered native tests; inspect the script harness terminal
  COMPLETE counts, failures/timeouts, exit code and runtime exceptions. Startup,
  partial PASS lines and static/MCP discovery alone do not prove player behavior.
- Validate GUI/input/animation through ordinary visible actions. QA-injected setup
  proves only the path after injection; restart persistence requires an isolated
  persistent provider, not the default Memory DB.
- Do not overlap bake writers and consumers. Check exact process paths, command
  lines and ownership; stop only the task-owned tree and verify exit/cleanup.
  Never kill by image name or delete a lock to bypass ownership. Normal GUI smoke
  closes normally and exits 0; forced cleanup is not clean-session acceptance.
- Keep original failures and controlled reruns separate. Report focused/full,
  static/native/runtime, manual, performance and platform qualification honestly.
  Reconcile final root/Engine revisions and gitlink; no stale evidence after moves.
- Update owning docs with behavior. Finish with changed files, actual checks and
  blockers, leaving local edits unless further Git/publication action was authorized.

## Read by task

| Task | Required project owner |
| --- | --- |
| Build/launch/tests/logs/CI/packages | [BuildAndLaunch](Docs/BuildAndLaunch.md) |
| Script state/dispatch/adapters | [Scripts](Docs/Scripts.md), [ScriptStyle](Docs/ScriptStyle.md), [Nullability](Nullability.md) |
| Find gameplay or content consumers | [Systems](Docs/Systems.md), then the actual module/assets |
| GUI/content/localization/config | [ContentWorkflow](Docs/ContentWorkflow.md) |
| Animation/frame offsets | [Animation](Docs/Animation.md) |
| Native/binding work | [NativeExtensions](Docs/NativeExtensions.md), [Engine instructions](Engine/AGENTS.md) |
| AI control, screenshots, quest playtests | [AiControl](Docs/AiControl.md) |
| Engine update or instruction/doc audit | [DocumentationMaintenance](Docs/DocumentationMaintenance.md) |
| Improvement backlog/campaign | [AuditPlan](Docs/AuditPlan.md), [Refactoring](Docs/Refactoring.md), [ReanimationPlan](Docs/ReanimationPlan.md); verify historical/proposed status first |
