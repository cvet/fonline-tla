# Optional resource filtering implementation plan

**Goal:** Make package resource filtering opt-in in Engine and package every
current baked resource in TLA without project resource-root catalogs.

**Requirement:** The owner requests a switch, filtering disabled by default, and
no filtering in this project. Existing `.foinfo` support for authored FixedType
data remains available independently of this feature.

**Design:** Add the immutable boolean `Baking.FilterResources`, default `false`.
The native Baker always publishes its authoritative, hash-bound usage manifest.
With filtering disabled it lists every available output registered by the current
bake; required-output checks, stale-output sweeping, target/pack-role exclusions
and packaging validation remain intact. With filtering enabled it keeps the
existing typed-root/dependency closure. Disabled mode skips root collection and
dependency traversal. Packaging continues to consume one manifest contract.

**Approach:** Keep selection in its existing native owner. A packager-only
filesystem fallback would duplicate policy, keep native filtering work enabled
and bypass the current-bake output registry. Removing the feature would prevent
other games from opting into it. These alternatives do not satisfy the request
as directly as one setting in the current owner.

**Owners:** `Engine/Source/Common/Settings.inc`, `Source/Tools/Baker.cpp`,
`ResourceUsage.h/.cpp`, existing baker/image-dependency tests and the real
producer/archive/native-reader integration fixture. Project config and content
workflow own the TLA opt-out and removal of the task-created catalogs.

## Steps

- [x] Freeze the native handoff baseline, retain task-owned catalog bytes, and qualify the existing real output and
  packaging fixtures, including a semantic RED for an unreferenced resource.
- [x] Delegate the bounded native switch, regressions, and fixture migration to
  DeepSeek Flash/max; Codex retains design, shell, integration and final review.
- [x] Set `Baking.FilterResources = False` in TLA, remove the 12 task-created
  catalogs and `Scripts/ResourceSets.fos`, and remove their `Protos.InputDirs`
  entry. Preserve other local changes and general `.foinfo` tooling.
- [x] Update owning EN/RU Engine guidance, source-owned contract projections and
  version/migration notes; replace TLA's catalog instructions with its policy.
- [x] Review the immutable worker delivery, build/run affected native tests,
  exercise default/False/True and incremental mode changes through real
  bake/archive/native readback, and run Python/contract/documentation gates.
- [x] Bake TLA with the new Baker to an isolated output/cache/writable tree and
  verify its manifest and real archive contain every current target-eligible
  output without any TlaResourceSet metadata. Reconcile exact revisions/index.

## Acceptance and review focus

- **C1:** Omitted/False filtering includes unreferenced outputs, source outputs
  and empty configured packs deterministically; no dependency callback executes.
- **C2:** True preserves typed roots, transitive closure, provider identity and
  missing-root/required-output errors. Explicitly migrate tests that own this
  opt-in behavior; do not weaken their expected results.
- **C3:** Real full/incremental/default/False/True transitions produce fresh
  manifests; packaging and native archive readback agree on exact file sets.
  Missing/mismatched manifests and markers still fail closed.
- **C4:** TLA has no catalog inputs/type and explicitly opts out; all current
  target-eligible outputs are packaged, while role exclusions remain effective.
- **C5:** Settings/default, guides/locales, generated contracts and migration
  notes agree; no unrelated source or index changes and no publication.

## Constraints and evidence

Root master starts at `ad0815441087c03fe4885e98b4713145d1bd11d6` with earlier
Engine-integration changes. Engine master is clean at
`00c3c4cf5207ec7080179e4c9d455221ff1149d4`; the root committed/index pin still
names `4588149fa4e4493ed6dddfea0a2fdf65d17c1f3e`. This task does not authorize
staging, commits, pushes or moving either branch.

Existing GUI server/client consumers of the shared `Baking/` tree remain open.
Use quoted argument arrays and separate task-owned bake/cache/writable roots;
do not overlap a shared-output writer or resume the stopped GUI automation.
Private evidence belongs in `Workspace/optional-resource-filter-20261026/`.

## Actual verification

The existing Engine 70 binary qualifies the actual RawCopy/manifest consumer:
unreferenced JSON is physically baked but absent from export (the semantic RED
for the requested default), and a missing manifest is rejected. The original
integration fixture failed before selection because it omitted required
AngelScript bytecode. A private qualified projection compiled all three role
bytecodes and passed full/incremental archive/native readback before handoff.

The worker delivery is retained by the launcher. Codex reviewed the native
branch and fixtures, restored three files' original CRLF format, removed an
unnecessary pre-cleanup of a unique temporary path, and separated fixture
FixedType data into `.foinfo`. The two new native cases cover full/filtered modes
and required-output failures. The pipeline covers default/False/True/False and
incremental root removal. CMake wiring and strict package-manifest tests pass:
34 tests. Native layout/module gates and configuration pass. The API generator correctly rejected its stale source-owned inventory
(2585 -> 2586 for the new setting); its exact inventory annotation/test update
is deferred until the compiler releases `Common.h`. The first attempted write
was refused by Windows and left that header unchanged.

The final Baker and UnitTests build passed. Focused native validation passed 12
cases/168 assertions; the full native suite passed 707 cases/745,326 assertions.
The real AS integration pipeline passed all modes and negative controls. TLA's
isolated full bake passed in 2m47s without warnings. The manifest exactly matches
all available physical outputs in 19 packs, with no `TlaResourceSet` metadata.
All 26 Client/Server pack views were checked through real archives and exact
native byte readback; identical file sets reuse the same verified archive.

Private archive-fixture failures are retained separately: `Embedded.zip` selected
the reserved embedded provider, an uppercase `.OGG` needed a lowercase extension
allowlist, and the 1.65 GB FOArt archive exceeded a 120-second reader deadline.
The corrected run uses `EmbeddedPayload.zip`, normalized extension filters and a
600-second bounded reader; it passed all files. The native FNV accelerator was
qualified with its actual byte/streaming controls and reused. A stopped pure
Python hash run and its unverified partial archive are preserved, not accepted.

Project Python tests pass: 156 tests and 82 subtests. The final owning Engine
Python suites pass 138 tests and 78 subtests, including API/public-contract,
contract diff, versioning, baking guidance and documentation-validation tests.
A broad collection of all
Engine BuildTools tests was interrupted at 43% after partial failures and has no
terminal summary; it is not qualified. Its partial failures are not reclassified
by the separately passing required owning suites with stable final inputs.

Generated API/settings/package/public-contract pages, reviewed Russian overlays,
version 2026.1.73-dev and exact digest-bound inventory disposition are updated.
The full-context delivery originally exceeded its existing byte limit; the
owning explanation was shortened without changing its semantics or the limit.
Documentation preparation now passes; validation passes 413 Markdown entries;
version/migration validation passes; aggregate comparison passes all 17 domains
with one required, completed disposition. Native formatting passes after one
whitespace-only call-layout correction; executable branch semantics are unchanged
from the tested sources. No native rebuild is needed for the later API-inventory
comment or documentation/format-only corrections.

All five acceptance criteria are satisfied by these focused/full-native and
real-project artifact checks. Runtime gameplay, other platforms, 3D/Managed and
performance are not claimed. The existing GUI processes were left open; the
shared `Baking/` tree is not this task's accepted bake. Before ordinary launch,
build matching applications and bake from the final sources. Both branches and
the root committed/index gitlink retain their initial revisions; Engine changes
remain reviewable and uncommitted.
