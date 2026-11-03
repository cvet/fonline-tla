# Engine 2026.1.96 integration plan

**Goal:** Adopt the fetched Engine update (2026.1.82-dev → 2026.1.96-dev) and
verify TLA's existing behavior without project regressions.

**Architecture:** Keep the project on `master` and return Engine to its owner's
`master` branch via fast-forward to the fetched upstream tip. Retain project
configuration, scripts and content; adapt only where the incoming range requires
it, then force a complete bake and run the full local integration chain.

**Tech stack:** Windows x64, MSVC, CMake, AngelScript, 2D client, Memory database.

**Requirements:** [integration procedure](../DocumentationMaintenance.md#engine-submodule-updates),
[verification route](../BuildAndLaunch.md#select-verification-by-the-change), and
[configuration owner](../ContentWorkflow.md#configuration-and-secure-channel).

## Constraints and review focus

- No staging, commits, publication, project branch movement or unrelated edits;
  the root gitlink bump stays uncommitted for owner review.
- Preserve Memory, single-threaded logic, Dynamic grids, TCP, AngelScript and
  `Baking.FilterResources=False`; `TLA.fomain` stays byte-identical unless the
  range forces a setting change.
- Preserve the Engine safety branch `safety/tla2-engine-update-20261023-ca18bfee`
  and any stashes until the result is verified.
- Keep active consumers away from bake/build writers; no TLA processes are
  running at the baseline.
- Require terminal native/script results, warning-free builds and bake, ordinary
  script-harness completion, and clean task-owned process exits.
- Distinguish Windows ordinary-build acceptance from Unity, Linux, wide
  coordinates, packaged deployment, restart persistence and performance
  qualification.

## Baseline and incoming range

Project: `3d0991ac7cf792c40391a4b2fa427a35cbdd86a4`; clean `master`.
Engine worktree HEAD and committed/index gitlink:
`629ea6f569f7af460a41fc1d582dd948fdcc6a97` (`2026.1.82-dev`); worktree clean,
HEAD detached, local `master` at `28c84c5d9d` (behind origin by 18; the previous
update left HEAD detached instead of advancing `master`).
Fetched target: `efefc47f3ace19b4e45428a20c2a1b12fc7f7666` (`2026.1.96-dev`).
Current HEAD is an ancestor of the target, so a fast-forward of `master` applies.

Complete incoming commit range (oldest first):

1. `c80e173595`: context-aware map view visibility hooks; optional SERVER hooks
   `CheckViewMapCritterVisibilityHook`/`CheckViewMapItemVisibilityHook` with
   default stubs; runtime marker 0.0.83. Existing hook signatures unchanged.
2. `843a470bb4` (`2026.1.84-dev`): BuildTools README documentation correction.
3. `47f2e992cd` (`2026.1.85-dev`): malformed peer frames disconnect only the
   offending connection; `NetBufferException` context values; new warning line
   `Invalid network data from host ...` replaces engine-exception reports for
   peer framing faults.
4. `f116c907c1` (`2026.1.86-dev`): writable-root migration record names
   `--Common.UserWritablePath`; TLA launch tasks use no such flag.
5. `e8eb12f279` (`2026.1.87-dev`): `Game.CreateItem(protoId, properties)`
   `Dictionary<ItemProperty, any>` overload (additive; the unpublished
   `CreateItemWithInitialProperties` name is removed — unused in TLA),
   `MapSpriteHolder.Elevation`, dynamic roof rebuild fixes, Common-property
   snapshot bypass removal; compatibility marker 0.0.83 → 0.0.84 and
   `FO_COMPATIBILITY_VERSION` changes.
6. `522d825ef3` (`2026.1.88-dev`): WebSocket `SO_REUSEADDR` on POSIX restarts;
   retry log lines gain a trailing reason suffix.
7. `0acab586bb`/`f2a8756706` (`2026.1.89-dev`): non-handshake first message
   rejected as a protocol error; Unity-qualified test helper.
8. `56683c4737` (`2026.1.90-dev`): public `ServerEngine::ValidateServerSnapshotState`,
   named simulation holds under a drained external lock, packaged sub-config
   rejection without the throw loop; no setting conversion.
9. `680c444d1d` (`2026.1.91-dev`): event chain continues after a faulting Managed
   handler without a result; TLA has Managed scripting disabled.
10. `50e1ddb1ea` (`2026.1.92-dev`): client-only `Critter.VisualOffset` property
    (additive, defaults to zero); Critter property registry shifts, manual
    compatibility marker 0.0.84 → 0.0.85.
11. `27553fd71d` (`2026.1.93-dev`): `FO_MAP_WIDE_COORDS` (default OFF) and
    `FO_MAP_MAX_SIZE` (default 4000) CMake options; layouts rehashed into
    `FO_COMPATIBILITY_VERSION`; maps above 4000 cells per side now fail load.
12. `c1b3f7114d` (`2026.1.94-dev`): scoped simulation-hold mutex ownership; map
    and grid resize overflow rejection.
13. `1ab76a88f2` (`2026.1.95-dev`): CMake interface test expectations (62 options,
    10 native-extension hooks).
14. `efefc47f3a` (`2026.1.96-dev`): partial Vulkan buffer allocations released
    safely on failure; rebuild Client/Mapper.

## Project consumer analysis (baseline)

- Largest authored map side is 400 (`geck01.fomap`), far below the 4000
  `FO_MAP_MAX_SIZE` default; wide coordinates stay OFF; no
  `SetOption(FO_MAP_MAX_SIZE/FO_MAP_WIDE_COORDS ...)` is required.
- `SourceExt` uses no `.square()`, `mpos`/`msize` component types,
  `int16_t` coordinates, `HoldSimulation` or snapshot validation; hook
  signatures it implements (`ClientInitHook`, `CheckCritterVisibilityHook`,
  `CheckItemVisibilityHook`, Baker hook) are unchanged.
- `CreateItemWithInitialProperties` appears nowhere in project sources.
- Compatibility markers advance 0.0.82 → 0.0.85 and the baking hash changes:
  a complete forced bake and full rebuild of every native role are mandatory;
  old/new mixed artifacts must be refused.
- No `TLA.fomain` setting changes are required by any migration note in the
  range; SHA-256 at baseline is
  `4021F550DCDCFBB89C77B36710BA1775E50EDCFA336718A87CB8346108C410D9`.

## Steps and acceptance

- [x] Inspect both repositories, fetch upstream, read every migration note in
  the range, and check project consumers/configuration.
- [x] Advance Engine `master` fast-forward to `efefc47f3a`, leaving HEAD
  attached; reconcile and record the root working-tree/index/committed gitlinks.
- [x] Reconfigure (`cmake --preset auto`), force a complete bake, and execute
  every leaf of `Verify :: All`; inspect terminal COMPLETE counts, exit codes
  and runtime exceptions.
- [x] Verify ordinary startup and affected player routes (headless script
  harness) and clean task-owned exits; graphical smoke not repeated this
  session — see qualification limits.
- [x] Review the final diff, configuration preservation, docs impact and
  evidence; record exact results and remaining qualification limits.

## Verification record

Evidence root: ignored `Workspace/engine-update-20261102/`. Python: `py -3`,
Python 3.14.7. No TLA processes were running at the baseline.

Engine advanced: `master` checked out (no longer detached) and fast-forwarded
to `efefc47f3ace19b4e45428a20c2a1b12fc7f7666`; Engine worktree clean. Root
working-tree gitlink is the new revision; committed and index pins remain the
baseline `629ea6f569...`, intentionally unstaged. Project HEAD and branch are
unchanged; the safety branch and stashes are untouched.

`cmake --preset auto` (Configure :: Auto): exit 0, MSVC 19.51, Unity disabled.
`FO_MAP_MAX_SIZE = 4000` and `FO_MAP_WIDE_COORDS = OFF` apply from defaults;
`FO_MANAGED_SCRIPTING = OFF` retained; baking configuration hash is now
`46ad849c8a0da44a0e87f2eae4ba1f50ee4f1587a67efde57b2c220a6cd3a402`.

First forced bake failed in `TLA_Baker.log` (2026-11-02 21:02): the only
project consumer of the `2026.1.83-dev` migration,
`Scripts/MapPreview.fos:60`, still called `Player.ViewMapArea(map, hex, radius)`
without the required `Entity@? context`. The call now passes `null` — TLA
implements no `CheckViewMap*VisibilityHook`, so the generated fallback admits
every subject within Engine bounds, preserving pre-update behavior; a Russian
comment states the policy, and [Scripts](../Scripts.md#contracts-and-tests)
now records it. No other `ViewMapArea`/`ViewMap`/`RefreshViewMapVisibility`
consumer exists in project sources.

Second forced bake after the migration completed with exit 0: `Baking complete!`,
report `Baking/Baking.report.json` status `success`, build hash unchanged; all
19 packs plus Protos and 550 maps rebaked in 00:02:12 (for example FOArt 12,516
files, FOnline 1,894, ServerData 866, Core 476). `TLA_Baker.log` timestamps
11/2/2026 21:07. `Verify :: All` then started (first leaf 21:09).

`Verify :: All` progress: Bake, Server, ServerHeadless, Client and Mapper leaves
completed with fresh binaries (TLA_Server 21:13, ServerHeadless 21:14, Client
21:14, Mapper 21:16). The chain then stopped at `Build :: TLA_ASCompiler`; the
controlled direct rerun exposed the cause:

```
LINK : fatal error LNK1140: limit exceeded for program database
```

The `H:` volume is full (≈10 MB free of ~1 TB). This is an environment blocker,
not an Engine-update defect: the repository occupies ~13.4 GB (Build 3.3,
Baking 6.4, .git 2.0, Binaries 1.1, Resources 0.6); the remaining ASCompiler
and UnitTests links need roughly 2–4 GB of PDB space. Disk cleanup outside this
repository is owner-owned; verification resumes after space is freed.

The owner freed disk space (86.8 GB free) and committed/published the prepared
integration as `76fc9af27231eb1089d9bfc667e2200706172563` at 22:43 (MapPreview
migration, `Docs/Scripts.md`, this plan, Engine gitlink). The committed pin,
index and Engine HEAD all equal `efefc47f3a...`; project and Engine `master`
worktrees are clean. The failed link had also left a partial `TLA_ASCompiler.pdb`;
a direct rebuild relinked it cleanly (exit 0).

Completed verification at the final revision:

- Incremental `Bake Resources` (22:46–22:52, Baker exit 0) after the owner's
  commit changed the build hash to `76fc9af27...`.
- Builds: Server 21:13, ServerHeadless 21:14, Client 21:14, Mapper 21:16,
  ASCompiler 23:02 (exit 0), UnitTests 23:10 — all without warnings.
- `Launch :: TLA_UnitTests`, direct controlled rerun capturing stdout:
  **All tests passed (746,323 assertions in 726 test cases)**, exit 0
  (baseline 745,492/710 on 2026-10-29; the range adds 16 cases). The engine
  log's error lines are deliberate negative-test fixtures.
- `Launch :: TLA_Tests` headless harness: **COMPLETE: 128 passed, 0 failed,
  0 skipped (of 128)** at 23:29:46, followed by the full normal shutdown
  sequence ending `Server stopped!`; no TLA processes remain.
- `Analyze :: Script Quality (Ratchet)`: OK, no new violations above baseline.
- `Analyze :: Nullable All`: apply --check 0 changes across 335 files,
  validator tests 7/7 OK, ABI contracts valid, estimate report only.
- `Test :: Python Tools`: **220 passed, 89 subtests passed** in 29.8 s.
- `Format :: All`: scripts/fomain/prototypes each changed 0 files.
- `Check :: Docs Links`: 59 Markdown files, 0 findings.
- `git diff --check` clean; `TLA.fomain` SHA-256 remains
  `4021F550DCDCFBB89C77B36710BA1775E50EDCFA336718A87CB8346108C410D9`
  (byte-identical to baseline).

## Qualification limits

Windows x64 RelWithDebInfo only; Unity builds, Linux, `FO_MAP_WIDE_COORDS=ON`,
packaged deployment, restart persistence (Memory DB default) and performance
are not qualified by this run. The graphical client smoke
(registration/movement/inventory/relogin) that passed on 2026-10-29 was not
repeated: the headless harness covers the same script routes, and the only
client-visible deltas are the additive `Critter.VisualOffset` (defaults to
zero) and a Vulkan failure-path fix. The engine bump is committed and
published by the owner; no further Git action was taken by the agent.
