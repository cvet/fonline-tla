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

- Project base: `master` @ `8ba3c0b14` (`0.3.22`), clean before branching.
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

- [ ] Engine branch commits in the order above; update owning docs and
      `VERSION`/changelog per the Engine versioning contract.
- [ ] Build Engine paths warning-free; run the covered native targets, including
      `Test_ConfigBaker` and `Test_DataBase`.
- [ ] Project branch: apply script fixes with owning-doc updates; bump the
      Engine gitlink to the engine branch tip.
- [ ] `cmake --preset auto`; build Server, ServerHeadless, Client, Mapper,
      ASCompiler, UnitTests; force bake; warning-free.
- [ ] Execute `TLA_UnitTests` and the AngelScript harness; record actual counts,
      failures/timeouts and exit codes.
- [ ] Visible checks for GUI/input fixes: cursor in menu, empty main-hand plate,
      chosen drop animation, stimpak/medkit self-use, dialog approach distance.
- [ ] Translation branch: scripted key-clean merge, then script compile/bake and
      `russ`/`engl` key parity.
- [ ] Record final diff, checks and limitations here; leave all work on the
      local branches.

## Risks and review focus

- `breakdovvn`'s branch is ~390 commits behind; its patches are adapted by hand,
  not cherry-picked.
- Occlusion and occupied-hex rejection change client/AI behavior; they are
  isolated commits for owner review.
- The equipment fix changes the detached action item's slot semantics; verify
  inventory refresh and weapon stance after a swap.
- The oplog fix changes recovery-file truncation order; covered by a native test.
- Translation is content: wording and names remain owner-reviewed.
