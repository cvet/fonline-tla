# Engine Update and Publication Preparation

> **For agentic workers:** Use `executing-plans` for coordinator execution. Use the official shared MiMo launcher for bounded implementation or independent review; one worker at a time. Preserve the existing worktree and review every worker result before another handoff.

**Goal:** Integrate the fetched Engine master and prepare the existing Engine and TLA fixes as a reviewed, verified publication unit.

**Architecture:** Keep reusable capabilities in Engine and game policy in TLA scripts/content. Replay the existing local changes onto the fetched Engine tip, reconcile moved test ownership and documentation, and qualify the resulting source tree before publication decisions.

**Tech Stack:** C++20, AngelScript, Python 3, CMake/MSBuild, Git submodule.

**Spec:** Owner request of 2026-10-21; root `AGENTS.md`; Engine upgrade and versioning guides; earlier project-owned-policy and ResourceManager plans.

## Global Constraints

- Baseline TLA: `797e6079152b8183efc677e8a384f72c716d893d`; baseline Engine: `cd5c1168f8f4bdab63a2909ceacb049ba87e070a`.
- Fetched Engine target: `aafc7fe74bb8` (`2026.1.57-dev`); resolve and record its full SHA in `Build/engine-update-20261021/incoming.json`.
- Root already has one unpublished commit over `origin/master`; preserve it. Engine can fast-forward to the fetched tip.
- Preserve every existing local edit and untracked authored input. Keep the external source/index snapshot and named safety refs until verification is complete.
- Keep `Server.ProtoMapGridType = Dynamic`, `Server.MapInstanceGridType = Dynamic`, and `Server.SingleThreadedLogic = True`.
- Preserve script-owned animation composition, map/day tint and sound selection. Keep `CritterFramesCache` and its tuple key; constructors precede ordinary native methods and native spacing follows adjacent code.
- Keep the existing AngelScript-only TLA backend selection. Do not start production services, modify production data, or publish remotely as part of preparation.
- Do not stage, commit or push without clear owner authorization. Prepare exact reviewable changes and publication ordering first.
- Engine notes, code comments and plan text are English; maintained Russian documentation mirrors remain equivalent.

## Review Focus

- Upstream test splitting must retain local resource-owner and map-observation coverage in the correct neutral/AngelScript owners.
- Native factory updates precede sprite updates; scene abort and shutdown detach callbacks without changing lifetime ownership.
- Source map placement overrides must satisfy the new dynamic-item validation without reinterpreting valid authored values.
- Persistence, atomic filesystem publication and shutdown changes must preserve current save/property identities; use isolated test storage.
- Direct packet writers, new compatibility markers and rebuilt metadata/resources must agree across client/server roles.

## Task 1: Preserve and integrate the complete incoming range

**Files:** Engine `Source/`, `BuildTools/`, `Docs/`, `ThirdParty/`; immutable evidence under `Build/engine-update-20261021/` and the external backup directory.

- [x] Capture source bytes, deleted/untracked paths, tracked/index patches, exact index bytes, revisions and safety refs for both repositories.
- [x] Fetch both remotes and record all 24 incoming Engine commits, all 273 changed paths, and the 69 overlapping local paths.
- [x] Independently inventory incoming production/build contracts from a frozen complete diff and reconcile that checklist against the source and tests.
- [x] Preserve Engine changes in a named stash, fast-forward to the exact fetched target, then restore the stash without deleting the safety copy.
- [x] Resolve native/build conflicts by retaining both upstream fixes and the local Engine/game ownership changes. Move test changes to the new owning fixtures instead of restoring removed duplicate suites.
- [x] Audit all incoming source/test changes and all manually written project protocol consumers. Record each required project adaptation and its independent check.

## Task 2: Reconcile contracts, content and release materials

**Files:** Engine `VERSION`, bilingual changelogs and owning guides, interface models, translation state and dispositions; affected TLA `Scripts/`, `SourceExt/`, `TLA.fomain`, build glue and authored content only when the inspected contract requires it.

- [x] Reconcile the current local Engine note with upstream history, draft `2026.1.58-dev` from the fetched 57-dev tip, and document every removed/replaced contract and deployment boundary.
- [x] Regenerate source-owned documentation in dependency order; preserve history and bind dispositions to the exact fetched baseline.
- [x] Apply verified TLA compatibility changes while preserving selected settings and project-owned behavior. Add focused regression coverage only for material new fixes.
- [x] Run focused static/metadata checks before expensive builds; resolve every new or surfaced warning at its owner.

## Task 3: Review and qualify the final publication unit

**Files:** Final Engine/TLA diffs, review evidence and verification receipts.

- [x] Obtain an independent review of the final native ownership/protocol changes with full owning APIs, fixtures and cleanup/rollback paths supplied. Review and correct its result before any subsequent handoff.
- [x] Run `Verify :: All` on the final tree. Run the affected real 3D test/viewer targets in their own configured output tree and inspect the exact executables used.
- [x] Run Engine version, generated-contract and documentation checks; inspect the rendered-site environment and record any unavailable gate explicitly.
- [x] Validate the ordinary local client/server and Mapper routes with isolated test storage and clean runtime markers. Retain the final screenshots/log receipts.
- [x] Check conflict markers, unmerged entries, final source formatting and warning counts, preservation of original work, and published ancestry.
- [x] Prepare the Engine-first, TLA-second publication package: exact revisions, reviewed change groups, validation, deployment/migration notes and outstanding owner actions. Never publish a root gitlink that depends on an unpublished Engine object.

## Execution Record

- 2026-10-21: external baseline saved at the path recorded in `Build/engine-update-20261021/baseline.json`; no existing changes were discarded.
- 2026-10-21: root has no incoming remote commits; Engine incoming range is a fast-forward. Root history and its unpublished map-preview commit remain intact.

- 2026-10-22 UTC: final precommit review corrected throwing-Stop handle retention, duplicate motion copying, stale EN/RU migration references and unfinished new contract records. The complete current source and publication evidence are in `Build/precommit-review-20261022/`.
- 2026-10-22 UTC: the surfaced nested-sync fixture now keeps its entities alive through timeout joins and tests progress with 30s inactivity/120s overall bounds. Slow-progress and stalled controls were qualified; production EntitySync is unchanged.
- 2026-10-22 UTC: fresh full project verification, actual isolated 3D selected tests and both 2D/3D viewer builds passed. Previous ordinary client/Mapper GUI receipts remain separate; no new GUI, performance or Managed runtime claim. Ruby/Bundler is unavailable, so rendered Jekyll remains unqualified.
- 2026-10-22 UTC: commit preparation preserves both initial stages. The owner creates the Engine commit first, then updates the TLA gitlink to that object and commits TLA; no staging, commit or push was performed by the agent.
