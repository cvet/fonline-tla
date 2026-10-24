# Resource loading ownership implementation plan

Historical task plan. Its revision numbers, check counts, publication steps and
status describe that assignment only. Re-establish the current task's scope and
authorization using [AGENTS.md](../../AGENTS.md) and
[DocumentationMaintenance](../DocumentationMaintenance.md) before reuse.
No fresh acceptance or Git/publication permission is implied.

> **For agentic workers:** Use superpowers:executing-plans task-by-task; bounded mechanical consumer migration uses the official MiMo launcher. Keep steps checked as verification completes.

**Goal:** Give ResourceManager ownership of sprite loading, factories, caches and invalidation; keep SpriteManager responsible for rendering and updating sprite instances.

**Architecture:** ResourceManager is constructed after SpriteManager and before its resource
consumers, owns factories/templates, and exposes loading services. A generic begin-scene observer
preserves factory-update ordering without a SpriteManager dependency on ResourceManager.
CritterFramesCache owns script-resolved directional sequences; Mapper owns mutable critter preview
models. FileSystem continues to own mounted sources. Shared model/particle texture caching is a
separate subsequent change, not part of this approved first step.

**Tech Stack:** C++, CMake, native Catch tests, existing TLA verification and renderer smoke runners.

**Spec:** The user's approval of the preceding architecture proposal: move sprite
loading/cache/factory code from SpriteManager into ResourceManager, preserve independent animation
instances, separate critter cache and editor previews. Existing uncommitted migration is the
starting implementation.

## Global constraints

- Preserve staged root changes and both dirty worktrees. No stage, commit, push or destructive Git operations.
- Continue in this checkout: an isolated HEAD checkout would omit the approved uncommitted implementation on which this refactor depends. Baseline bytes and index state are retained in ignored Build/resource-manager-20261020.
- Existing copyable templates stay keyed by `(path, AtlasType)`; first and subsequent loads return independent copies where currently copyable. Preserve plain-image sharing and missing-load suppression.
- Preserve factory update before sprite-instance update inside BeginScene, exception propagation, low-memory cleanup, atlas cleanup and explicit shutdown detachment.
- Resources/factories outlive FontManager, critter animation cache and all sprite consumers; SpriteManager and FileSystem outlive ResourceManager.
- No old SpriteManager loading forwarding APIs, invented game defaults, or gameplay policy. Public script method signatures remain unchanged.
- Match adjacent names, blank lines around native control flow, real noexcept contracts and exactly one final native blank line.
- MiMo uses exact context/read paths, one worker at a time, shared launcher profile v5. Shell/build/tests remain Codex-owned. Reports stay files_only.

## Review focus

- A cache hit must not share animation time, direction or play state; preserve atlas-specific resources.
- Missing-resource retries and editor invalidation must reach the moved owner and specialized factory hooks.
- ResourceManager destruction/shutdown must detach both begin-scene and low-memory callbacks before releasing factories or backend objects.
- Font, updater-only, Mapper/viewer, disabled-3D and standalone test contexts all need a real ResourceManager; no backend dependency on ClientEngine.
- Cleanup order must preserve active sprite instances and release unused template/frame owners; borrowed GPU texture ownership is unchanged in this phase.

## Task 1: Establish the boundary and move core ownership

**Files:** ResourceManager.*, SpriteManager.*, DefaultSprites.*, new CritterFramesCache.*, EngineSources.cmake, Test_SpriteSheet.cpp; factory/Font owner declarations.

**Interfaces:** ResourceManager(FileSystem*, SpriteManager*) through engine ptr aliases; same
LoadSprite overloads, LoadSpriteAsQuad, registration/access, retry/invalidate/cache cleanup methods
moved from SpriteManager. LoadDefaultSprites(const RenderSettings&) initializes existing configured
defaults. CritterFramesCache(AnimationResolver*) retains GetCritterAnimFrames/CleanupCritterFrames.
SpriteManager has a generic GetOnBeginScene observer.

- [x] Add a compiling native ownership-boundary assertion which rejects the old SpriteManager loading surface; run it and observe semantic RED.
- [x] Move factory registry, resource caches, loading/invalidation methods and low-memory subscription into ResourceManager. Preserve begin-scene factory update through a generic observer and explicit unsubscription.
- [x] Move dummy atlas construction to DefaultSpriteFactory; extract directional critter cache unchanged into its own native module and unconditional source inventory.
- [x] Give factories/FontManager the resource owner explicitly; remove FileSystem/resource-loading state from SpriteManager. Pin missing-cache/invalidation and callback cleanup behavior with native tests.

## Task 2: Migrate all consumers and editor previews

**Files:** Client.*, Updater.*, CritterHexView.cpp, ItemHexView.cpp, MapView.cpp, scripting wrappers, Mapper.*, AnimationViewer.*, ParticleViewer.*, particle editors, affected native tests/app constructors.

- [x] Provide MiMo Flash a frozen verified API/context manifest and exact consumer edit set. It mechanically migrates all old loader/factory calls, constructor sites and viewer dependencies, preserving unrelated dirty changes.
- [x] Codex reviews the preserved original result and fixes integration/lifetime problems before another worker or build handoff.
- [x] Mapper owns the existing mutable preview model cache/functions. Client owns CritterFrames; cleanup clears project animation cache before resource template/atlas cleanup. ResourceManager precedes FontManager/animation consumers in construction order.
- [x] Run focused native boundary, sprite-copy/cache, client lifetime and mapper/viewer tests; no old loading calls may remain on SpriteManager.

## Task 3: Document, independently review and verify

- [x] Update owning EN/RU rendering/migration documents and current pending release notes; regenerate affected references and check contracts without changing public script API meaning.
- [x] Obtain a fresh independent review of the final ownership/destruction/event-dispatch paths with a finite source corpus and preserved baseline. Address material findings with regression proof.
- [x] Run authoritative Verify :: All, Engine documentation/contracts, affected optional 3D checks and actual client/mapper rendering smoke. Report unrun or failed gates explicitly.
- [x] Verify final EOF/diff checks, source inventory and untouched index; save launcher reports and finish with changes and verification only.
