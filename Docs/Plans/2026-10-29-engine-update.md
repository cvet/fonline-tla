# Engine 2026.1.82 integration plan

**Goal:** Adopt the fetched Engine update and verify TLA's existing behavior.

**Architecture:** Keep the project and Engine on `master`. Advance the clean
Engine checkout to the reviewed upstream tip, retain project configuration, and
verify matching binaries and a forced bake before ordinary client interaction.

**Tech stack:** Windows x64, MSVC, CMake, AngelScript, 2D client, Memory database.

**Requirements:** [integration procedure](../DocumentationMaintenance.md#engine-submodule-updates),
[verification route](../BuildAndLaunch.md#select-verification-by-the-change), and
[configuration owner](../ContentWorkflow.md#configuration-and-secure-channel).

## Constraints and review focus

- No staging, commits, publication, project branch movement or unrelated edits.
- Preserve Memory, single-threaded logic, Dynamic grids, TCP, AngelScript and
  `Baking.FilterResources=False`.
- Keep active consumers away from bake/build writers; existing sessions require
  their owner's permission before closing.
- Check the full incoming range, including private AngelScript helper renames,
  Windows macro preservation, UDP session lifetime and updater resume fixtures.
- Require terminal native/script results, warning-free builds and bake, ordinary
  registration/movement/relogin, and clean task-owned process exits.
- Distinguish Windows ordinary-build acceptance from Unity, other platforms,
  packaged deployment, restart persistence and performance qualification.

## Baseline and incoming range

Project: `3f6494630cefea80941c0c8618a23fed0783a527`; clean `master`.
Engine and committed/index gitlink: `28c84c5d9d21f5a33b2122977314383842dfe414`
(`2026.1.79-dev`); clean `master`.
Fetched target: `629ea6f569f7af460a41fc1d582dd948fdcc6a97`
(`2026.1.82-dev`). Runtime `0.0.82` and Managed ABI `9` remain unchanged.

1. `fcac7eb0824ea23a67fa4e2bd8804d4e03fdda98`: private AngelScript/native test
   helper names and Windows SDK macros support Unity translation units.
2. `59deea3d01c8ca7d306c83e7c65967bcc57d0270`: completed UDP handshake ends
   connection-phase TCP fallback; later UDP loss disconnects the existing session.
3. `629ea6f569f7af460a41fc1d582dd948fdcc6a97`: example config regeneration and
   qualified/bounded UDP integration fixtures.

No public declarations, EngineHook signatures, property layouts, settings or
project script/resource inputs change. TLA's TCP and full-output packaging choices
remain valid. Existing BuildAndLaunch and ContentWorkflow guidance remains accurate;
no cosmetic owner-document edits are needed. No bounded project implementation is
currently required for delegation; Codex owns integration and verification.

## Steps and acceptance

- [x] Inspect both repositories, fetch upstream, inspect migrations and changed
  implementation/test owners, and check project consumers/configuration.
- [x] Advance Engine with fast-forward only and reconcile gitlinks.
- [x] Resolve existing runtime ownership, configure, force bake and execute every
  leaf of `Verify :: All`; inspect formatter output and repeat affected checks
  only if it changes source.
- [ ] Finish runtime cleanup: functional registration, movement, inventory and
  client-restart/relogin checks passed; both clients exited normally. The test
  server still needs a normal exit after a system permission prompt is dismissed
  by the owner.
- [ ] Review final diff, configuration preservation, docs links and terminal logs;
  record exact results and remaining qualification limits.

## Verification record

Evidence root: ignored `Workspace/engine-update-20261029/`.
Python: verified `py -3`, Python 3.14.7.

Engine `master` is now at the fetched target with a clean worktree. The root
working-tree gitlink is the new revision; committed and index pins remain the
baseline, intentionally unstaged. Project HEAD and branch are unchanged.

Completed checks at the target revision:

- `cmake --preset auto`: exit 0, MSVC 2026, Unity disabled, no warnings/errors.
- Script-quality ratchet and the four nullability checks: exit 0 each.
- Python tools: 192 tests and 89 subtests passed, exit 0.
- All three formatter leaves: exit 0, zero changed files.
- Documentation links/structure: 57 Markdown files, zero findings.
- `git diff --check`: exit 0 in the project; Engine worktree is clean.
- `TLA.fomain` SHA-256 remains
  `B014C226038CB718576F8BBE50DE15F8530C0A5D72F1A3D5EAB1368997ED5B5F`.

The reused private task runner's `--static` selection ran only the nine static/
formatter leaves, recorded in `verify-static.json`; its generic terminal
`VERIFY_ALL_COMPLETE` marker does **not** mean the full integration chain ran.

The owner authorized normal closure of the previous `bug-reports-20261028`
client/server session. On resumption, both recorded PIDs and all TLA binary
processes were already absent; no forced termination was used. The previously
shared outputs were unoccupied before the completed force bake and builds.

The existing private task runner is reused with an integration-only selection.
Its nine static/formatting leaves already passed at this same revision with zero
authored changes, so they are not repeated without a new source change.
The native execution leaf uses CMake `RunUnitTests` instead of directly launching
the same executable, retaining the resource-usage pipeline dependency required by
the incoming migration notes. Native tests are executed once.

Generated API reconciliation: `Engine/BuildTools/docs_api.py --check` regenerated
the source-backed model in memory and confirmed the existing model is current:
1,014 methods, 133 properties, 121 events, 297 settings, 2,587 classified symbols.
The previous generated model was retained under the private evidence root before
the check. No tracked Engine documentation or project API consumer needed edits.

Force bake completed with exit 0: all 19 packs succeeded, 18,703 outputs changed;
the following incremental bake completed with exit 0 and zero files changed.
Both JSON reports were retained under the private evidence root. Server,
ServerHeadless, Client, Mapper, ASCompiler and UnitTests builds passed.

`RunUnitTests` completed with exit 0: 710 test cases and 745,492 assertions passed.
Its resource-usage dependency passed full/incremental bake, exact selection,
native archive readback and two negative controls. A listing from the rebuilt
executable confirmed both new UDP regression cases are present. The three fatal
reports in the log come from the deliberate `CrashReporterHooks` assertions in
`Test_ExceptionHandling.cpp`, not an unexpected process termination.

The first integration-runner attempt failed before starting a subprocess because
its conditional log-path expression returned a string in integration mode.
The original runner and its incomplete manifest are retained as
`verify-all-attempt1.py/json`. The corrected runner is a separate attempt; this
helper failure does not constitute a failed product build or an accepted gate.

## Runtime verification and remaining environment blocker

The script harness completed with exit 0: **116 passed, 0 failed, 0 skipped of
116**, with no timeouts or runtime exceptions. Together with the earlier nine
static/formatting leaves, all `Verify :: All` leaves have now passed.

Fresh graphical server and client processes used isolated writable directories
under the evidence root, `LocalTest`, matching baked resources, and
`Baking.PrebakeOnStartup=False`. DirectX selected feature level 11.1. Client and
server logs agree on compatibility `f4d6915d8d77200f` and metadata
`59254290fafd1af5`.

Ordinary Windows mouse input opened Registration and its name dialog. A Windows
Firewall prompt labelled `lf_client.exe` then blocked desktop input. Its owning
process was not established; no permission choice was automated. The owner was
asked to dismiss it, as required by the computer-use skill's security-request
prohibition. The native game bridge remained usable without changing permissions.

The bridge used normal registration/login and player-control paths with QA
commands disabled. `Eng82Check` registered into `repl1`, moved from `(84,29)` to
`(87,29)`, and opened Inventory. Fresh composed world and inventory screenshots
were decoded as 1024x768 images and visually inspected. The client disconnected
through the normal Menu Exit callback and quit from Login; process exit was 0.
A fresh client logged in to the same live Memory server and retained character
ID `10000001245`, map ID `10000000004`, and `(87,29)`, then exited through the same
normal callbacks with code 0. This proves reconnect after client restart, not
server-restart persistence. World, UI and reconnect checks passed without runtime
warnings/exceptions or script overruns in the inspected logs.

The default free-threaded Python could not load Pillow's native extension;
the installed standard Python 3.14 decoded the screenshots successfully. This
artifact-conversion issue did not affect the game or its acceptance checks.

**Pending:** normal closure of the task-owned graphical server, PID `66288`, and
final cleanup reconciliation. The system permission prompt still overlays that
window, so Windows UI automation is stopped pending owner action. No forced
termination or firewall/security setting change was performed. This run does not
claim complete OS mouse/keyboard qualification after the prompt appeared, Unity,
other platforms, packaged deployment, server-restart persistence or performance.
