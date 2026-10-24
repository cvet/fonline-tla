# Sprite Offset and Frame Motion Terminology

Historical task plan. Its revision numbers, check counts, publication steps and
status describe that assignment only. Re-establish the current task's scope and
authorization using [AGENTS.md](../../AGENTS.md) and
[DocumentationMaintenance](../DocumentationMaintenance.md) before reuse.
No fresh acceptance or Git/publication permission is implied.

The owner's final terminology is explicit: offset is the ordinary sprite offset
to its root; motion is a per-frame delta of visual displacement. CritterHexView
derives cumulative displacement and compensation against logical hex movement.

1. Preserve the stopped, superseded migration and restore its pre-existing user
   baseline. Keep the public GetSpriteFrameOffset/GetSpriteFrameMotion contract
   and CreateSpriteSequence offsets,motions argument order.
2. SpriteSheet stores offsets in `_sprOffset` and motion deltas in `_sprMotion`.
   SetFrame accepts `offset, motion` and assigns each to its matching field.
   GetSprOffset(frame) returns the ordinary offset; GetSprMotion() returns the
   motion array. Replace the renderer's temporary frame offset terminology with
   OffsetOverride, preserving its borrowed owner and fallback behavior.
3. Reconcile EN/RU owning documentation, native image-format anchors, generated
   references and migration notes within pending 2026.1.58-dev/runtime 0.0.76.
4. Verify exact source transformations, unchanged public script sources and API,
   focused existing 2D/3D sprite, actor and scripting fixtures, formatting and docs.
   The change is native naming only; reuse earlier full-chain/runtime evidence
   with an explicit qualification boundary.
5. Refresh and independently verify the publication packet. Preserve both current
   Git stage-entry fingerprints; do not stage, commit or push.

The sheet/copy fixture distinguishes offset (42,-17) from motion (5,-9). Real
actor fixtures cover direction changes, copies and visual phase alignment. The
unchanged embedded script fixture independently distinguishes offsets (d*11+f,
-d*7-f) from motion deltas (d+f+1,-d-f-2). Retain all inputs and expected results.
MovingContext remains the movement authority; no separate motion object or change
to movement arithmetic is added.
