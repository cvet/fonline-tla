# Reported gameplay regressions — investigation and verification plan

**Goal:** Resolve the five reported failures against the current checkout, preserving existing fixes and adding a discriminating regression where coverage is missing.

**Scope:** NPC death playback, local/global map UI transition, map music lifecycle, random encounter generation, and server NPC dialog diagnostics. Project and Engine stay on master. After verification, the owner authorized local commits; push and publication remain outside scope.

**Baseline:** Project c0d14a690; Engine 28c84c5d9d (committed project pin matches). Both working trees initially clean. Do not update Engine merely to address historical reports.

**Owners:** `Engine/Source/Client/CritterHexView.cpp`, `Scripts/Animation.fos`, `Scripts/GuiScreensExt.fos`, `Scripts/Media.fos`, `Scripts/Worldmap.fos`, `Scripts/GlobalmapGroup.fos`, `Scripts/Dialogs.fos`, `SourceExt/Dialogs.cpp`, their tests, `Docs/Animation.md`, `Docs/AiControl.md`, `Docs/BuildAndLaunch.md`.

## Steps

- [x] Inspect instructions, revisions, owners and available journals. Preserve task evidence under ignored `Workspace/bug-reports-20261028/`.
- [x] Trace existing fixes: frozen animation playback and neutral animation policy; GUI map-presence switch; map-music absence guard; NPC encounter list initialization. A nullable-looking expression is not permission to add a guard when its owner guarantees a result.
- [x] Qualify a real isolated random-encounter fixture and cleanup. Demonstrate that removing NPC list initialization produces a semantic failure, while the current path generates populated groups. Delegate useful remaining regression implementation through the required launcher after qualification.
- [x] Compile/bake changes and run focused plus full script tests, quality/nullable checks and formatting. Run existing affected native tests without altering Engine if its behavior is already fixed.
- [ ] Exercise ordinary visible local/global-map transition and input, map music without a local map, and death playback. Separate QA fixture setup from subsequent player actions and rendered observations.
- [x] Triage NPC-dialog evidence: the owner confirmed no original journal exists. Validate available parser/bake/harness paths and retain the specific report as unreproduced, without inventing a cause or claiming closure.
- [x] Review final diffs, documentation and actual checks; report resolved/current/unreproduced/blocked states separately.

## Acceptance

- A1: after a death action, the corpse remains at the final pose across several animation periods; no background loop overwrites it. Existing animation policy tests are supplementary.
- A2: ordinary exit to the world map activates GlobalMap, removes Game and permits world-map input with no absent-map access.
- A3: the map-loaded notification with no local map does not throw in Media. Audible track selection is a separate check.
- A4: a generated encounter with NPC groups completes without a null nested array; expected NPCs and generated state are present, and created locations/critters are cleaned up. A wrong-state control removing initialization must fail.
- A5: each supplied dialog error maps to a concrete owner and reproduction; no generic null suppression or speculative dialog edits.

## Decisions and verification ledger

2026-10-28: Existing reports describe causes already changed in current source. Verify before deciding whether further production changes are needed. Requested the original server journal asynchronously; current root logs have no matching failures.

- Native baseline: `CritterAnimationPreservesProjectSelectionWhileMoving` passed (151 assertions); sprite playback and four native dialog cases passed (41 assertions). The model-only 3D case is not built by this TLA configuration and is not counted as coverage.
- First fixture bake finished but had two nullable warnings in the temporary probe. This attempt is not accepted; changed the probe to narrow its nullable map explicitly and rerunning the fixture. No production source was changed by that correction.

- Fixture controls: current code generated a populated encounter (3 authored Brahmin and 2 added rats), COMPLETE 1/0 and exit 0. Removing the single NPC-list initialization produced Null pointer access, COMPLETE 0/1 and exit 1. Restored Worldmap bytes and completed a warning-free restoration bake. The transient qualification test was restored to its baseline before handing off two durable regressions through the shared launcher.
- Python tools: 156 tests and 82 subtests passed. Nullable ABI validator passed. Native application builds are in progress; no runtime consumes the bake during the control writes.
- Existing Animation.md and Scripts.md already describe the current frozen-pose and lifecycle contracts accurately. Update Systems.md with the new generation regression coverage; no production behavior/API change is intended.

## Current handoff after owner stopped Computer Use

- User stopped Windows Computer Use with physical Escape during the post-exit observation. All app input stopped; no alternative app-control path is authorized by that interruption.
- Native builds: TLA_Server, TLA_Client and TLA_ServerHeadless completed with exit 0 and no warnings. Earlier baseline native checks passed: 151 assertions in CritterAnimationPreservesProjectSelectionWhileMoving, plus 41 assertions across sprite playback and four dialog cases. The separate model-only case was unavailable, not counted as passing.
- A1 runtime: isolated QA map/attribute setup, then ordinary movement and attacks killed three Brahmin. After stepping away, six native screenshots over irregular intervals had identical corpse-region pixels (ROI 390,270,500,370). Actual corpse sprite was visually inspected. QA setup is not proof of ordinary prerequisites. The first capture series was obscured by living attackers and was superseded by the clear series.
- A2/A3 runtime: QA placement near the exit resolved requested (9,44) to actual walkable (10,45); the original exact-coordinate setup wait failed and is retained. From that local-map position, the ordinary move_to_hex step to (9,46) reached GlobalMap with hasMap=false, hasChosen=true and only GlobalMap active. Client log recorded Start load global map / Map loaded without absent-map/music exceptions. Further world-map clicks and clean GUI shutdown were not executed because the owner stopped Computer Use.
- A4: current existing production fix passed the qualified real fixture; removing row initialization reproduced Null pointer access (exit 1 / one failed test), then source bytes were restored. DeepSeek delivered two new durable tests in Test_Worldmap.fos. Their compilation, bake and execution are NOT RUN. Read-only Codex review found no important defects; two minor wording issues remain in comments. All-six-direction fixture geometry was not exercised and remains a qualification limit.
- Python tooling passed: 156 tests / 82 subtests. Initial nullable validator passed before the new test delivery; final nullable/ratchet/format checks remain pending.
- Runtime logs contain script execution overruns (including AiControl and RenderIface). Functional observations do not establish performance acceptance.
- A5 remains blocked on the original server dialog error, NPC identity and steps. Existing native dialog tests and server startup are only general checks.
- Client PID 32968 and GUI server PID 20228 belong to this task and were left running after the UI stop. Do not bake while they consume current resources. Process/command receipts are in Workspace/bug-reports-20261028.
- Source changes remain local and unstaged: Test_Worldmap.fos, Systems.md and this plan. Engine source and gitlink were not changed. No commits, pushes or publication.

## Follow-up: no original journals exist

The owner confirmed that only the five report descriptions are available. A5 is unresolved/unreproduced rather than waiting for a log known to exist; no speculative dialog fix is authorized by that missing evidence. Complete available source/bake/parser/harness checks and report their limited scope.

Continue A4 verification using task-private Baking.BakeOutput=Workspace/bug-reports-20261028/validation-bake, separate CacheResources/UserWritablePath, and ServerNetwork.DisableNetworking=True. Current GUI client/server continue consuming root Baking. This does not resume Computer Use or send app input. The two contexts must never share bake/cache output writers.

A required formatting gate exposed an existing wrapper defect: NULLABLE_RETURN_RE rejects namespace separators inside parameter lists, so formatting CreateFixtureLeader(Testing::TestContext...) changes Critter? to Critter ?. Add a bounded Python regression and permit paired :: while still rejecting a lone ternary colon. This small dependency correction stays in Codex; it does not introduce a general parser or another worker assignment.

The first attempted isolated bake was not isolated: PowerShell split unquoted -Baking.BakeOutput into -Baking and .BakeOutput (confirmed with a harmless argv probe). It completed against root Baking while the GUI runtime was active. Preserve this as an invalid isolation attempt. The subsequent Python argument-list launch explicitly logged the private BakeOutput and private writable/cache paths. Verify unchanged root markers before accepting isolation.

## Final qualification (2026-10-28 follow-up)

- Final isolated bake compiled Server, Client and Mapper without warnings. Correct argument-list runs used only the task-private output/cache/writable roots; root Baking markers stayed unchanged during those runs. The earlier incorrect PowerShell-isolation attempt remains a separate failure and is not counted as isolated acceptance.
- Original worker test source: focused worldmap 3/3, exit 0. Legacy player-only row initialization: relief passes, both encounter regressions fail with Null pointer access, exit 1. Empty-Raiders-only missing initialization: relief and populated-NPC case pass, empty-row case fails with Null pointer access, exit 1. Production Worldmap.fos restored to exact baseline bytes.
- Final full harness: COMPLETE 116 passed, 0 failed, 0 skipped (of 116), exit 0; no runtime exceptions or stopped time events. Test-owned isolated headless processes shut down normally. The earlier UTF-8 console-print failure occurred after the first semantic RED result was saved; that result was reused instead of rerunning it. Remaining controls used explicit UTF-8 transport.
- Formatting dependency: reproduced the qualified-parameter nullable-return wrapper defect with a failing Python regression, then corrected paired :: handling without changing real ternaries. Four existing spaced nullable-return declarations were normalized by one space each; byte comparisons establish that those are their only changes. No gameplay or serialized contract changed.
- Worker test corrections are exactly two comment replacements; its executable source is otherwise unchanged. Read-only Codex review found no important defects. Fixture directions remain random as in production; all-six-direction geometry is not separately qualified.
- Python tools: 159 tests / 89 subtests passed. Final project formatting reports zero changes. Nullable ABI validation, nullable marker dry-run (zero changes), coverage inventory, script-quality ratchet and git diff --check passed. No baseline was weakened.
- Fresh full bake covered all 859 root dialog files selected by the pack; their baked bytes match authored inputs. Dialog parser/binding checks and dialog/dialogbox/say harness tests passed. This does not establish the cause or resolution of the unspecified NPC-dialog exception; no speculative production dialog change was made.
- A1 and A3 retain the earlier Windows x64 2D runtime evidence. A2 confirms the ordinary grid exit and screen/map state; post-exit world-map clicking, clean GUI shutdown and audible music playback remain unexecuted after the owner stopped Computer Use. Runtime overruns remain a separate performance limitation.
- Existing GUI client/server were neither controlled nor stopped during this follow-up. Managed, 3D, other platforms, CI, restart persistence and performance remain unqualified. Root/Engine revisions and committed gitlink remain at the baseline; indexes are empty, Engine is clean, and all authored changes stay local.

## Local commit handoff (2026-10-28)

The owner authorized local commits after final verification. Split the reviewable changes into the nullable-return formatter correction (including its regression tests and canonical declaration spacing) and encounter regression coverage with investigation documentation. The qualification above describes the pre-commit state; Engine and its gitlink remain unchanged. No push or publication is authorized.
