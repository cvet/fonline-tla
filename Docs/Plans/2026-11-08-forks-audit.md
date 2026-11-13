# Fork audit integration plan

**Goal:** Bring the verified, reusable changes from the audited `fonline` and
`fonline-tla` forks into the Engine and the project without merging any fork
branch wholesale.

**Architecture:** Two independent local branches keep repositories separate:
`fix/forks-audit-20261108` in `Engine` (native fixes and capabilities) and the
same-named branch in the project (script/content fixes plus the gitlink bump).
English dialog localization from `T4lus` is prepared separately in
`content/engl-dialogs-20261108`; it is content for owner review, not a bug fix.

**Requirements:** [Engine instructions](../Engine/AGENTS.md) for native work,
[BuildAndLaunch](../BuildAndLaunch.md), [Scripts](Scripts.md),
[ContentWorkflow](ContentWorkflow.md), [Nullability](Nullability.md).

## Branch and repository state

- Project base: `master` @ `59e32f720` (`0.3.22`), clean before branching.
- Engine base: `master` @ `c5101d149a` (`2026.1.116-dev`), which includes the
  owner's `de3dfb6c8c -> c5101d149a` pull; the project gitlink still names
  `de3dfb6c8c` until the engine branch is ready.
- No push, merge, force-push or publication. Local branches only.

## Scope

### Engine branch `fix/forks-audit-20261108`

Adopt, with adaptation to the current source:

1. `fysh`: SDL_GPU upload correctness and bounded staging
   (`c4c0205357`, `a7789f95ea`, `0d83a316f8`), high-DPI mouse coordinates
   (`4b0ba945aa`), `BakerDataSource` always-stale config outputs
   (`095fa70330`) with a test, and bundled examples updated to the current
   Engine (`27c2328052`).
2. `breakdovvn`: written-output spelling tracking in `MasterBaker`; item fly
   movement frame-delta clamp; visual-only item movement API; occluder alpha
   pass with picking filter; occupied-hex movement rejection. The last three
   are separate commits so the owner can drop them.
3. `qwear0`: authoritative equipment slots before view/action callbacks;
   interrupted oplog recovery cleanup with a native test; non-3D `IsModel`
   warning and the unused `FindFunc` lambda.

Not adopted: fork test-suite deletions, local TLA CMake patch, version numbers
from fork commits, and animation fixes already covered by the FOFRM rework.

### Project branch `fix/forks-audit-20261108`

Adopt only the generic fixes from `qwear0/fonline-tla`:

- energy-barrier blocker array construction;
- injury message text ids;
- female sound selection after model substitution;
- server dialog distance parity with the client;
- `MainPlanes` weapon-search retry;
- cursor drawing without a loaded map;
- active non-weapon item mode, stimpak self-use and medical-kit self-treatment;
- empty main-hand plate refresh;
- chosen drop animation;
- non-blocking AI bridge writes with a deadline.

Not adopted: the Den/Sierra campaign, mercenary/self-care/zoom/hotkey features,
LAN/SQLite/updater changes, test deletions, `TLA.fomain`/`EngineRevision`
fork state, `TownSupply` disabling, the `GameTime` calendar rewrite, and the
`NpcPositioning` AI redesign.

### Translation branch `content/engl-dialogs-20261108`

Apply only key-clean English blocks from `T4lus/fonline-tla`: 63 new blocks and
288 improved existing blocks, plus key-aware `Text.engl.fotxt` additions. Exclude
the `vc_hartmann.fodlg` regression and preserve upstream keys added after the
fork. Owner reviews wording before merge.

## Steps and acceptance

- [x] Engine branch commits in the order above; update owning docs and
      `VERSION`/changelog per the Engine versioning contract. Branch tip:
      `300b768790`, `2026.1.117-dev`; `docs_engine_version.py`, both docs test
      suites and `docs_validate.py` pass.
- [x] Build Engine paths warning-free; run the covered native targets, including
      `Test_ConfigBaker` and `Test_DataBase`. Full `TLA_UnitTests`: 843 passed,
      4 skipped, 1,326,956 assertions.
- [x] Project branch: apply script fixes with owning-doc updates; bump the
      Engine gitlink to the engine branch tip and the project version to `0.3.23`.
- [x] `cmake --preset auto`; build Server, ServerHeadless, Client, Mapper,
      ASCompiler, UnitTests; force bake; warning-free. All six targets exited 0;
      the force bake completed in 2:44 with no warnings or errors.
- [x] Execute `TLA_UnitTests`: 843 passed, 4 skipped, 1,326,940 assertions,
      exit 0. AngelScript harness: `128 passed, 0 failed, 0 skipped`, exit 0.
      One `Testing::ExecuteTest` overrun log line (132.9 ms) is timing output,
      not a failed test.
- [ ] Visible checks for GUI/input fixes: cursor in menu, empty main-hand plate,
      chosen drop animation, stimpak/medkit self-use, dialog approach distance.
      Not exercised in a graphical client in this environment; static compile,
      bake and script coverage only. Owner should run these ordinary actions.
- [x] Translation branch: scripted key-clean merge, then script compile/bake and
      `russ`/`engl` key parity. 62 dialog blocks added, 287 updated; 573
      `Text.engl.fotxt` and 104 `Game.engl.fotxt` entries translated; the
      shrink-only English baseline was updated; `Tools/ContentQuality` passes
      52/52.
- [x] Record final diff, checks and limitations here; leave all work on the
      local branches.

## Verification record

Branches and revisions:

- Engine `fix/forks-audit-20261108`: 17 commits, tip `300b768790`,
  `VERSION` `2026.1.117-dev`, 55 files changed.
- Project `fix/forks-audit-20261108`: script fixes, AI bridge fix, docs,
  Engine gitlink `300b768790`, `VERSION` `0.3.23`.
- Project `content/engl-dialogs-20261108`: two content commits, 349 dialog files,
  two text packs and the English-surface baseline.

Actual checks:

| Check | Result |
| --- | --- |
| Engine `TLA_UnitTests` | 843 passed, 4 skipped, 1,326,956 assertions |
| Engine docs (`docs_engine_version.py`, `test_docs_validate.py`, `docs_validate.py`) | pass, 414 Markdown entries |
| Project build (six targets) | exit 0, no warnings/errors |
| Project `TLA_UnitTests` | 843 passed, 4 skipped, 1,326,940 assertions |
| Force bake | complete in 2:44, no warnings/errors |
| AngelScript harness | 128 passed, 0 failed, 0 skipped, exit 0 |
| `Tools` pytest | 220 passed, 89 subtests |
| Script-quality ratchet | no new violations |
| Nullable chain | pass |
| `Tools/ContentQuality` | 52 passed |
| Project formatters | changed nothing |

Limitation: no graphical client session was launched, so cursor, main-hand plate,
drop animation, item use and dialog distance remain owner-visible checks.

## Review pass (2026-11-12)

Both branches are already pushed, so the review is added as new commits on top of
`1078d617` (project) and `300b768790` (Engine); no history rewrite.

Owner decisions:

- Drop all three `breakdovvn` runtime changes. Occupied-hex rejection ran in the
  generic `ProcessCritterMovingBySteps` for every critter (not only client paths, as
  the changelog claimed), counted corpses through `CritterFindType::Any`, and
  contradicted the Engine rule that critters are passable. `Map.UpdateCritterOccluders`
  and `Item.MoveToHexVisual*` have no TLA consumer; the fade API cannot be cleared,
  and the fly-delta clamp only delays catch-up after a stall. Source equals the
  `c5101d149a` base again; changelog, API model, references and the RU description
  catalog no longer list them. The written-output spelling fix stays.
- Self-use: `IsUseItemCapabilityAllowed` (since Refactoring #49) rejected self-use of
  `IsCanUseOnSmth`-only items, i.e. every drug except via special cases. The rule now
  admits `IsCanUse || IsCanUseOnSmth` for a self target; the stimpak `IsCanUse`
  prototype edits and the medical-kit exception are reverted.
- Empty main hand shows the unarmed attack (use picture, AP, aim) from
  `HandsProtoItemId`/`HandsItemMode` instead of a blank panel.
- Medical-kit use stays routed through First Aid/Doctor.

Refactoring kept with the adopted fixes:

- `Dialogs::GetTalkDistance` is the single talk-range rule for the client approach,
  the server check and the QA talk diagnostic (the diagnostic used the player's range).
- `MsgStr::InjuryTextOffset` replaces two duplicated switches.
- `LastWeaponNotFound` became write-only after the weapon-search fix; the property is
  removed with `///@ MigrationRule Property Critter Remove LastWeaponNotFound`.
- `CritterItem::GetItemActiveMode`/`GetUsePic` feed `UseMainItem`, the main-hand panel,
  the cursor hit chance and AP cost; `SwitchMainItemMode` no longer writes an unused
  `Mode` to non-weapons. `GetMedicalKitSkill` moved next to its only caller in `Main`.
- Comments corrected in `EnergyBarier` (no `grow`) and `ClientMain` (only drop is
  confirmed by the server; pick-up is animated locally).
- Engine: redundant null re-checks removed from the SDL_GPU upload ring, its idle wait
  is now checked; redundant target guard removed from the `ContentShowcase` example.

Kept as is after review: energy-barrier array construction, injury text ids, female
sound selection, cursor without a map, empty-hand cell reset point, chosen drop
animation, non-weapon active mode, `UseMainItem` cursor data, AI bridge
non-blocking writes; Engine SDL_GPU upload fixes, high-DPI mouse, equipment slots
and empty snapshots, oplog cleanup order, baker output spelling, lazy config
outputs, examples, `IsModel` warning fix.

Not possible without force-push: squashing the three intermediate SDL_GPU commits
and moving the non-chosen snapshot hunk from the oplog commit to the equipment
commit. The review is committed as Engine `ddc89d58b3`/`f5a37d9fc9` (tip `f5a37d9fc9`, still
`2026.1.117-dev`) and one project commit with the gitlink; nothing is pushed.

Review verification (on the same tree before committing):

| Check | Result |
| --- | --- |
| Engine docs: `docs_reference`/`docs_api`/`docs_public_api` `--write`, `docs_prepare.py`, `test_docs_validate.py`, `docs_validate.py`, `docs_engine_version.py` | generated API docs equal `c5101d149a` again; 50 tests OK; 414 entries pass; `2026.1.117-dev` pass |
| `cmake --preset auto`, `ForceBakeResources`, then incremental bake | exit 0, no warnings or errors |
| Build Server, ServerHeadless, Client, Mapper, ASCompiler, UnitTests | all exit 0, no warnings or errors |
| `TLA_UnitTests` | 843 passed, 4 skipped, 1,326,943 assertions, exit 0 |
| AngelScript harness | `128 passed, 0 failed, 0 skipped`, exit 0 |
| GUI generator vs paired `GuiScreens.fos` edit | identical |
| Script-quality ratchet, nullable chain, item components, `Tools` pytest (220) | pass |
| Project formatters, `git diff --check` (project and Engine) | no changes, clean |

Still owner-visible: empty-hand panel (fist icon, AP, aim), drug self-use from inventory
and the main hand, medical kits on self/others, dialog approach distance, chosen drop
animation, cursor in the main menu.

## Risks and review focus

- `breakdovvn`'s branch is ~390 commits behind; its patches are adapted by hand,
  not cherry-picked.
- Occlusion and occupied-hex rejection change client/AI behavior; they are
  isolated commits for owner review.
- The equipment fix changes the detached action item's slot semantics; verify
  inventory refresh and weapon stance after a swap.
- The oplog fix changes recovery-file truncation order; covered by a native test.
- Translation is content: wording and names remain owner-reviewed.
