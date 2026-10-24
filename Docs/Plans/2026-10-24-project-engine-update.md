# Project and Engine update

## Goal and scope

Integrate the fetched master histories into the existing published project
`fix/tla-scripts-20261019` and Engine `Tla_AnimationFixes` branches. Preserve all
review fixes, project settings and the owner's documentation layout decisions.
Do not push. Necessary merge commits are part of the requested history update;
unrelated changes and optional cleanup are outside scope.

## Baselines and owners

- Project: `caa982e3e`, target `origin/master` = `e2b5b90b0`.
- Engine: `0cd8146d6f42c263c869f35c183432cc00755cfa`, target
  `origin/master` = `57424cb5d2ac132b1fa8ba83e353d07cb6ca75e0`.
- Both worktrees and indexes were clean before the update.
- Owners: `AGENTS.md`, incoming `Docs/BuildAndLaunch.md`,
  `Docs/DocumentationMaintenance.md`, `Docs/NativeExtensions.md`, Engine
  documentation reconciliation/versioning guides, and `.vscode/tasks.json`.
- Private evidence: `Workspace/project-engine-update-20261024/`.

## Decisions and invariants

- Merge diverged published histories; retain the existing branches and ancestors.
- Keep `Docs/Nullability.md`, the deleted root `CLAUDE.md`, ignored operation
  journals and the local PR review artifact outside the repository root.
- Keep script comments Russian and reusable native/agent documentation English.
- Retain Memory storage, single-threaded script logic, Dynamic grids, disabled
  managed scripting and disabled 3D. Adopt the explicit false interthread-only
  transport setting from master.
- Reconcile the feature changelog against master's `2026.1.60-dev`, using the
  next Engine version for the integration and runtime contract `0.0.77`.
- History integration and policy conflicts stay with Codex. Delegate a bounded
  implementation only if compatibility fallout leaves meaningful suitable work.

## Ordered work and acceptance

- [x] Save the exact incoming source/test/doc inventories and baseline API model.
- [x] Merge Engine master, retain all source changes, reconcile VERSION and EN/RU
      changelogs, run owning documentation checks, and finish the necessary merge.
- [x] Merge project master, reconcile the submodule and documentation ownership,
      repair current links and preserve every local review decision.
- [x] Run a force/full resource bake and the authoritative `Verify :: All` chain.
      Preserve original failures and any controlled reruns separately.
- [ ] Run matching server/client startup and ordinary player-path smoke; close
      owned windows normally and confirm owned process cleanup.
- [x] Reconcile the final plan, exact project/Engine commits, gitlink, generated
      contracts, warning status and remaining manual/platform limits.

## Preservation and reconciliation

| Reviewed requirement | Final owner/decision |
| --- | --- |
| Verification operands cannot hide required actions; macros remain enabled in release | `Docs/NativeExtensions.md`, Binding and review |
| Nullability guide belongs in Docs | `Docs/Nullability.md`; all incoming current links rebased |
| Remove root CLAUDE wrapper | Keep the deletion; entry/maintenance guides reference only Copilot |
| Keep task reports out of root | `AGENTS.md`; new private evidence uses incoming Workspace convention; existing PR report stays under ignored Build |
| FixedFrame, special-hex visibility and reviewed source spacing | Project Items/Scripts/SourceExt/Animation guide unchanged by the incoming project range |

## Progress

Fetched both remotes and inspected the incoming player-admission, stored-map-load,
transport-setting and project documentation changes. No local work needed stashing.
Resolved Engine changelog overlap as version `2026.1.61-dev` while retaining
runtime marker 77. Normalized twelve incoming extra EOF blank lines without
native token changes. Engine docs preparation, 413-entry validation, version
check and six-change contract diff pass; 81 focused tests and 100 subtests pass.

Resolved incoming project documentation conflicts with a preservation map above;
257 current local links resolve. The existing two-argument LoadCritter consumer
needs no change. Merges are ready for their necessary local commits; full
native/bake/script/player-path qualification is pending.

## Final verification and user interruption

Project merge `cb72f6dcb724f5140f24d882bc6ea7e7fffb31a4` and Engine merge `65cf1919228e737960347a737db37bfd89d0b453` retain both published
histories. Gitlink matches; no push. All 18 Verify :: All commands and force
bake passed: 651 native cases / 735323 assertions,
113 scripts, 156 Python tests + 82 subtests; no build/baker warnings.

The first GUI fixture had an invalid 13-character name; preserve that failed
attempt. A corrected clean-root run registered, moved to (82,29), and closed
its first client with code 0. Physical Escape stopped Computer Use; no further
window automation was performed. Relogin/complete clean shutdown remain open;
remaining owned processes were forcibly cleaned up. Full receipts and limits
are in `Workspace/project-engine-update-20261024/qualification.json`.

This final plan update remains local and uncommitted.
