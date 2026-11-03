# Engine 2026.1.98 integration plan

**Goal:** Adopt the fetched Engine update (2026.1.96-dev → 2026.1.98-dev) and
verify TLA's existing behavior without project regressions.

**Architecture:** Keep the project on `master` and fast-forward the Engine's
`master` to the fetched upstream tip. Remove the retired `OGL` package token
from the profiling package, retain the rest of the project configuration
unchanged, force a complete bake (runtime compatibility marker advances) and
run the full local integration chain.

**Tech stack:** Windows x64, MSVC, CMake, AngelScript, 2D client, Memory database.

**Requirements:** [integration procedure](../DocumentationMaintenance.md#engine-submodule-updates),
[verification route](../BuildAndLaunch.md#select-verification-by-the-change), and
[configuration owner](../ContentWorkflow.md#configuration-and-secure-channel).

## Constraints and review focus

- No staging, commits, publication or project branch movement; the gitlink bump
  stays uncommitted for owner review. Preserve the uncommitted verification
  record of [2026-11-02](2026-11-02-engine-update.md) and all other local work.
- Preserve Memory, single-threaded logic, TCP, AngelScript and
  `Baking.FilterResources=False`; `TLA.fomain` pack layout stays unchanged
  (engine examples keep the separate `Configs` pack with ordinary
  `Bakers=Config`, which "retains its outputs").
- Keep active consumers away from bake/build writers; check for running TLA
  processes before starting.
- Require warning-free builds and bake, terminal native/script results, and
  clean task-owned process exits.

## Baseline and incoming range

Project: `76fc9af27231eb1089d9bfc667e2200706172563`; `master`, in sync with
origin; local edit: the 2026-11-02 plan verification record (kept).
Engine worktree HEAD and committed/index gitlink:
`efefc47f3ace19b4e45428a20c2a1b12fc7f7666` (`2026.1.96-dev`); clean `master`.
Fetched target: `ac37c9d217b314b3f3a1f567f67be535cfe15cac` (`2026.1.98-dev`).

Complete incoming commit range (oldest first):

1. `d6742fb78664773f64f09d497243db08106aed35` (`2026.1.97-dev`): packaged
   applications load the selected `.fomain-server`/`.fomain-client` from the
   `Metadata` resource pack before frontend creation (`ReadResourceConfig`
   applies only when `IsPackaged()` and reads only the pack named `Metadata`);
   new `ClientConfigBaker` for complete client profiles in a shared
   `Bakers=Metadata Config ClientConfig` pack (optional — ordinary
   `Bakers=Config` retains outputs, engine examples keep separate packs);
   `AppInitFlags::ClientMode` renamed to `StandaloneClient` (bit `0x01`
   unchanged; unused in TLA `SourceExt`); **`OGL` package token removed**
   (`package.py` now rejects tokens absent from `PackageInterface.json`;
   OpenGL is selected with `--Render.ForceOpenGL 1` instead); runtime
   compatibility marker 0.0.85 → 0.0.86 — rebuild and rebake everything
   together.
2. `ac37c9d217b314b3f3a1f567f67be535cfe15cac` (`2026.1.98-dev`): corrupted
   native updater payloads are recovered within the current launch (temp file
   removed and re-requested from offset zero; refused removal or second
   failure aborts without promotion); `///@ Enum <Name> <Entry> = -` truncated
   negative enum declarations are rejected. No conversion; marker 0.0.86 and
   Managed ABI 9 unchanged.

## Project consumer analysis (baseline)

- `OGL` appears only in `CMakeLists.txt:108` (`Test` package client binary
  `TotalProfiling+OGL+Raw`); no OGL references in `.vscode/tasks.json`,
  launch flows or project docs that require edits. Removal is mandatory.
- `AppInitFlags::ClientMode`/`InitApp` are not used in `SourceExt`.
- No `///@ Enum ... = -` truncated declarations in `Scripts/`.
- The dev launch flow (`--ApplySubConfig LocalTest`, non-packaged) is outside
  the new resource-config path; packaged TLA builds have no `.fomain-*` in
  their `Metadata` pack, so the executable's bootstrap snapshot stays active —
  same as before the update.
- `TLA.fomain` SHA-256 at baseline:
  `4021F550DCDCFBB89C77B36710BA1775E50EDCFA336718A87CB8346108C410D9`.

## Steps and acceptance

- [x] Inspect both repositories, fetch upstream, read the migration notes and
  check project consumers/configuration.
- [x] Advance Engine `master` fast-forward to `ac37c9d217` and record the root
  working-tree/index/committed gitlinks.
- [x] Remove the retired `OGL` token from the `Test` package in
  `CMakeLists.txt`.
- [ ] Reconfigure (`cmake --preset auto`), force a complete bake, and execute
  every leaf of `Verify :: All`; inspect terminal COMPLETE counts, exit codes
  and runtime exceptions.
- [ ] Review the final diff, configuration preservation, docs impact and
  evidence; record exact results and remaining qualification limits.

## Verification record

Evidence root: ignored `Workspace/engine-update-20261103/`.

Engine advanced: `master` fast-forwarded `efefc47f3a → ac37c9d217`, worktree
clean. Root working-tree gitlink is the new revision; committed and index pins
remain `efefc47f3a`, intentionally unstaged. No TLA processes were running.

`CMakeLists.txt` Test package client binary is now `TotalProfiling+Raw`
(OGL removed). `cmake --preset auto` (Configure :: Auto): exit 0, MSVC 19.51,
package listing accepts the token set; baking configuration hash unchanged
(`46ad849c...`), codegen compatibility version now `131196189f115abb`.
Forced bake started 2026-11-03 (first run in this plan).
