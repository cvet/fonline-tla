# Documentation review and upstream reconciliation

## Goal and scope

Review the uncommitted gameplay guides and their documentation/quest tools,
correct source-backed defects, commit the reviewed package, rebase project
`master` onto fresh `origin/master`, and reconcile the guides with incoming
changes. The owner explicitly authorized commit and rebase on 2026-10-28.
Push, publication and gameplay changes are outside this assignment.

Baseline: project `e2b5b90b0ea407a68e4672825446664b8a5f5ea2`, Engine
`57424cb5d2ac132b1fa8ba83e353d07cb6ca75e0`, both on `master`; root has
26 documentation/tooling files to preserve, Engine is clean. Original bytes
and hashes are retained under ignored `Workspace/documentation-review-20261028/`;
`safety/docs-review-20261028-pre` preserves the original project revision.

## Owners and review focus

- Nine new gameplay guides, their routes in `Docs/Systems.md` and
  `Docs/README.md`, content-format notes and the two originating plans.
- `Tools/DocsCheck/`: actual Markdown coverage, links/anchors, structure,
  safe self-test setup/cleanup and honest validation limits.
- `Tools/QuestInventory/`: property/binding/transition evidence, deterministic
  TSVs and limits of static reachability inference.
- `Tools/ContentQuality/`: new text checks must detect new violations rather
  than permit replacements under aggregate ceilings.
- `.vscode/tasks.json`: executable commands and preservation of upstream tasks.
- Incoming gameplay/dialog/Engine contracts: retain upstream behavior and
  adapt documentation without treating old static evidence as runtime proof.

## Ordered work and acceptance

- [x] Inventory project/Engine state and preserve all original local files.
- [x] Fetch both remotes and inspect complete incoming project and Engine ranges.
- [x] Review every new guide against source; correct actionable findings.
- [x] Review new tools using real inputs and independent wrong-state controls;
  delegate a coherent bounded implementation if one remains after diagnosis.
- [x] Run the documentation checker/self-tests, Python tool tests and byte-stable
  quest regeneration; inspect formatting and the complete staged diff.
- [x] Commit the reviewed package, then rebase onto fresh `origin/master`;
  preserve safety refs and resolve conflicts by source ownership.
- [x] Align clean Engine `master` with the resulting project pin, recheck incoming
  contract changes, rerun affected checks and commit reconciliation if needed.
- [x] Record actual results, remaining findings and qualification boundaries;
  verify ancestry and exact root/Engine gitlink alignment.
- [x] Commit the reconciliation and confirm clean final project/Engine trees.

## Decisions and verification

Native builds/bakes are not required solely for these docs and Python tools.
Incoming Engine integration is reviewed as already authored upstream; this task
does not claim new native/runtime/platform acceptance for that integration.
Open gameplay choices D-1..D-7 remain owner decisions; documentation review does
not authorize their implementation. Historical plans retain their original scope
and results, with corrections clearly dated.

## Review results so far

Fetched project target: `c0d14a690` (five incoming commits: `3465ebccb`,
`4d2984482`, `70c8c7958`, `ad0815441`, `c0d14a690`). Its Engine pin is
`28c84c5d9d21f5a33b2122977314383842dfe414`, a descendant of the starting pin.
The two later Engine-origin commits are outside that project pin; this docs
task does not independently upgrade the integration to them.

During review, `origin/master` advanced to `a213c7abe` through `2d473ff7e`
(nullable return formatting and regressions) and `a213c7abe` (real NPC-encounter
regressions and coverage routing). Both changes were inspected; the Engine pin
is unchanged. Rebase and final checks will use the fresh complete range.

Source review corrected attack/armor/AP formulas and test-coverage claims;
character generation, skill bases and nullable/default-item distinctions;
trade/craft/repair contracts; map GC/entry/group/encounter behavior;
replication/drop/account conditions; plane-child and dialog result semantics.
The format quick reference now describes recursive prototype inheritance rather
than requiring a parent's physical declaration before its child.

Original included checks passed (`164` Python tests / `88` subtests and a
45-page supported Markdown audit). Those passes did not prove the incorrect
source claims or detect the tooling escapes. Real wrong-state controls exposed
destructive fixed-path selftest setup, fence/anchor errors, Unicode Git-path
loss, omitted quest predicates, aggregate-ceiling substitution and English
section truncation at literal brackets. Each original failure is retained under
the private task directory; corrected checks are recorded separately.

The Markdown checker now has isolated selftest fixtures, consistent bounded
fence/heading handling, duplicate anchors and NUL-separated UTF-8 Git discovery.
Its 11 regression tests pass; the pre-task checker fails 8 of those tests.
The Unicode fixture additionally failed against the first delivery before its
focused correction. Syntax/size/readability limits are documented explicitly.

Quest generators: five behavior tests pass after corrections to native inline
comment semantics, fixture identity and TSV tab/quote transport. Independent
whole-source regeneration matches all three versioned files byte-for-byte:
165 properties (158 bound-reference, 1 unbound, 6 no-dialog), 1684 answer rows,
159 chain rows, 48 properties in multiple map-file families. Temporary outputs
were removed by their owned context manager. The index retains all predicates
but does not preserve cross-column demand interleaving or evaluate OR groups.

Content quality: 36 focused tests pass after replacing aggregate ceilings with
exact per-file entry identities and language/property/key gap tuples. Both Quest
languages need numeric nonzero states and explicit metadata checks. Real bare
`.fotxt` packs, sectioned `.fodlg`, literal brackets, trailing whitespace and
invalid UTF-8 have discriminating controls. The independently frozen identity
baseline remains byte-identical; no existing exception was expanded to pass.
The scanner's supported syntax and lack of runtime/translation acceptance are
documented in `Tools/ContentQuality/README.md`.

Pre-commit scope gate: exactly 32 authorized files, strict UTF-8 without NUL or
replacement corruption; VS Code task labels unique; supported Markdown audit
46 pages / 0 findings, isolated selftest passes, root/Engine diff checks pass.
Full Python pre-rebase run: `py -3 -X utf8 -m pytest Tools -q` — 189 tests and
82 subtests passed (2026-10-29). Git reconciliation and final checks follow below.

## Gameplay discrepancies preserved without code changes

These source findings require separate gameplay/design work and runtime proof;
documenting them is not permission to implement them.

| Finding | Owners and boundary |
| --- | --- |
| Password not sent/validated on the traced login path; tag-count budget client-only | `PlayerRegistration`, Engine admission; originating D-5 is corrected in the follow-up plan. |
| Permanent-death writes critter ID but login checks player ID | `Replication::AddPermanentDeath` / `Main::PlayerLogin`; account-ban behavior cannot be promised for different IDs. |
| PipBoy quest lookup still uses summed numeric IDs against authored two-token keys | `MsgStr::GetQuestText`, `Quest*TextId`, `Gui/PipBoy.fogui`; the property-change message uses a different, two-token path. |
| Lost-target recovery requires a critter argument that `NextPlane` does not supply | `MainPlanes::NpcPlaneEnd` / `NpcPlanes::NextPlane`; no unconditional recovery claim. |
| Drug stages update the addiction array, while legacy flags still have dialog consumers | `Drugs`, `CritterProps`, `klam_jura`; no assumption that the flags mirror live stages. |
| Caravan/event/safe-zone startup calls are commented out; group-size config has no traced consumer | `Main`, `Caravan`, `GameEvent`, `NoPvpMaps`, `GlobalmapGroup`; references/settings alone do not prove activation. |

## Rebase and final qualification — 2026-10-29

The reviewed package was committed as `a7fb926ce`, preserved by
`safety/docs-review-20261028-reviewed`, then rebased without conflicts onto
`a213c7abe0013e0b1d82c7e8aae78d8b24805199`. Its replayed commit is `514f87f8d`.
Engine `master` fast-forwarded from `57424cb5d2` to the project's committed pin
`28c84c5d9d21f5a33b2122977314383842dfe414`; no separate Engine commit/bump was made.

Reconciliation covers `SayScript`/`SayRevision` and server answer selection,
public equipment data, actual worn-armor refresh/removal/replication, fixed item
frames, stopping movement before death events and the new Worldmap regression
owners. Source revision markers now identify the integrated baseline; obsolete
line offsets were replaced by owning paths/symbols. The docs index routes to
DialogSay and ConsoleCommands. Incoming plan/test/history changes were preserved.

Actual post-rebase checks:

- `py -3 -X utf8 -m pytest Tools -q`: **192 passed / 89 subtests passed**.
- `check_docs.py --selftest`: OK; supported corpus audit: **56 pages / 0 findings**.
- Both quest generators execute and independently regenerate the same three
  files byte-for-byte (165 properties, 1684 answer rows, 159 chains, 48 multi-family
  properties); created temporary roots are removed.
- Raw UTF-8/inventory and size review pass. Largest new guide is 19,583 bytes;
  startup/index/overview thresholds hold. The three existing oversized reference/
  history records retain their dated scope and section maps.
- Frozen English identity baseline bytes are unchanged. Git checkout's EOL
  conversion was reconciled with owned output contracts; no tool content diff
  remains after rebase. Root/Engine whitespace checks and unmerged-path checks pass.

This task changes documentation and Python verification tooling, not gameplay,
content or native implementation. No new native build, bake, script-harness run,
GUI/runtime, performance, persistence, platform or CI acceptance is claimed.
Upstream's recorded integration/runtime results remain historical evidence.
The reconciliation commit was followed by clean project/Engine status checks,
project divergence **ahead 2 / behind 0**, no unmerged paths and exact committed
gitlink/Engine-HEAD equality. Both remain on `master`; commits are local.
Private evidence and safety references are retained.
