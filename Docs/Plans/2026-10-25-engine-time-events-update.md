# Engine time event update implementation plan

**Goal:** Integrate Engine `2026.1.62-dev` into TLA and verify the changed timer
lifetime/counting contract with matching binaries and baked resources.

**Architecture:** Keep TLA on AngelScript and preserve its settings and gameplay.
Review the incoming Engine contract, classify every project timer-count consumer,
then advance the clean Engine master at the existing upstream boundary.

**Tech stack:** CMake, native C++, AngelScript, Python 3 and Windows x64.

**Spec:** The owner's Engine-maintenance request, project instructions,
[integration procedure](../DocumentationMaintenance.md#engine-submodule-updates)
and Engine's `2026.1.62-dev` changelog migration.

## Constraints and baselines

- Project master: `3465ebccb62d97c4f0c79dee53b8f4dc90688c9d`.
- Engine master and committed/index pin:
  `af0770a5ef98ef31fa57c448f27ed4ce3fa86ee4` (`2026.1.61-dev`).
- Target: `4588149fa4e4493ed6dddfea0a2fdf65d17c1f3e` (`2026.1.62-dev`).
- Both worktrees/indexes were clean; keep branches, settings and authored content.
- No staging, commits, pushes, publication or unrelated history integration.
- Private evidence: `Workspace/engine-time-events-20261025/`.
- Codex owns lifetime decisions and verification. A bounded DeepSeek source
  inventory may supply unreviewed consumer evidence; it cannot decide gameplay.

## Review focus

- Singleton guards must include executing callbacks to prevent duplicate loops.
- A callback queuing a new one-shot may need to exclude its current execution.
- Yielded callbacks must complete before repeat scheduling; cancellation must win.
- Runtime compatibility is `0.0.78`; resources and all native roles must match.
- Original test failures, controlled reruns and GUI cleanup have separate evidence.

## Tasks and acceptance

- [x] Fetch Engine upstream and inspect the complete incoming commit/file range,
      migration and current project status. One incoming commit changes timer
      completion and `CountTimeEvent(..., bool excludeExecuting = false)`.
- [x] Classify all 34 project `CountTimeEvent` calls with callback/caller evidence;
      inspect custom native dispatch references and both Yield consumers.
- [x] Fast-forward Engine master and make only verified compatibility corrections;
      update owning docs if project behavior or guidance changes.
- [x] Configure `cmake --preset auto`, force/full bake, then execute every leaf of
      `.vscode/tasks.json` `Verify :: All`, retaining exit codes and complete logs.
- [x] Exercise matching server/client startup, ordinary registration/login and
      movement, then normal GUI shutdown with exit code 0.
- [x] Inspect final diff, warnings, generated outputs, branches, index and
      committed/index/working-tree gitlinks; record actual checks and limits.

## Progress and decisions

Initial inspection: no project native `CountTimeEvent` callers; 34 AngelScript
calls require semantic classification. The two authored `Yield` calls are in
`ClientMain.fos` and `Core/Gui.fos`. No persistence format conversion is specified
by upstream; deploy/rollback binaries and resources as a matching set.

Execution continues in this authorized checkout. Project-specific rules override
generic workflow suggestions for extra worktrees, commits and approval pauses.

Engine master advanced by fast-forward to the exact target above. The complete
incoming diff and original statuses are retained privately. Native extension
search found no removed dispatcher API consumers. `Gui.HighlightProcess` is a
yielding one-shot client timer without count/repeat/requeue calls; the initial
classification of both Yield sites as non-timers was corrected after reading its
attribute and scheduler. No script adaptation is justified there. Consumer
classification and final verification remain open. The existing task runner from
the preceding integration is reused against
the current `.vscode/tasks.json`, rather than introducing another verification
implementation.

Consumer review is complete: all 34 keys and 107 cited source ranges were checked.
Inclusive counts are retained. The proposed `Traveller.SheduleTravel` exclusion
was rejected as an update migration: the old manager also retained a synchronous
callback's record until after return, and this callback does not Yield. Its
self-requeue concern is pre-existing and needs a separate gameplay requirement
and regression oracle. GuardLib and MoveRandom transitive owners were inspected
to close the bounded inventory's context gaps. Original and corrected private
inventories remain separate. The maintained timer guidance is in `Docs/Scripts.md`.

`cmake --preset auto` completed without warnings. Force/full bake and all 18
current `Verify :: All` leaf commands passed on their first runs (19 commands
including force bake). Native execution: 652 cases / 735398 assertions. The
script harness completed 113 passed, 0 failed, 0 skipped, without overruns or
runtime exceptions. Python tools passed 156 tests and 82 subtests. Quality,
nullable and formatter gates passed. Formatting produced no source changes.
## Final functional acceptance and limits

Windows x64 / 2D / AngelScript smoke passed with matching binaries/resources:
registration, movement to `(86,29)`, same character/map/position after relogin,
and three normal exits with code 0. Inventory opened and closed through its
ordinary visible buttons. The second smoke's process registry was empty after
normal shutdown; no owned game process remains.

Preserve the first smoke as failed normal-shutdown acceptance: both clients
exited 0, but Codex delayed the server close during optional diagnostics and the
runner's 180-second coordination deadline caused forced cleanup. The second
smoke used a fresh account/root/ports and a 600-second coordination deadline;
product timeouts and test thresholds were unchanged.

Performance remains unqualified. The second GUI run logged ten script execution
overruns (up to 442.808 ms), despite successful functional actions and normal
exits. No script/verification exception or compiler/baker warning was found.
An attempted priority control was invalid because of a path-alias guard and
active-log sharing errors; its apparent zero counters are not evidence. The
cause of the GUI overruns is not established, and no performance repair or
regression/exoneration claim is made. Original logs and both smoke attempts are
retained privately.

Final Engine master is `4588149fa4e4493ed6dddfea0a2fdf65d17c1f3e`; project master
is unchanged. The committed/index gitlink still names `af0770a5`, while the working
tree gitlink shows the intended uncommitted update to `4588149fa4`. Both indexes
are empty, Engine has no local diff, settings are preserved and existing output
junction targets were verified. Project documentation links resolve; final diff
checks pass. Changes remain local: no staging, commits or pushes.

Private `qualification.json` separates full checks, original failure, accepted
repeat smoke and performance limits. Memory-DB reconnect does not qualify server
restart persistence; Managed, 3D, other platforms, CI and performance were not
qualified.

Independent Kimi review initially reached the same raw `Traveller` recommendation
as the delegated inventory, then checked the exact old Engine object and withdrew
it. The old manager also removed a one-shot only after its synchronous callback
returned; `Travel` has no `Yield`, so the self-requeue concern is pre-existing and
is not an Engine 62 compatibility correction. All 34 existing calls remain
unchanged for this update. The initial review and
`kimi-consumer-review-correction.md` are retained separately.
`kimi_validate_audit.py` confirmed the raw inventory's 34 exact keys and source
hashes, not runtime behavior. `GuardLib`, `MoveRandom` and `StartTimeEvent` were
inspected to close the inventory's source gaps. A separate static runner audit
confirmed Force Bake plus all 18 executable Verify :: All leaves in order.
