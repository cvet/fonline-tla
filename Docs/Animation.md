# Animation and Frame Offsets

TLA owns Fallout filenames, weapon/death anchors, first/last poses and paired actions in
`Scripts/FalloutAnimation.fos`. `Scripts/Animation.fos` resolves a ready sprite through
`Game.OnCritterAnimationSprite`; the Engine caches the result and renders it.

`Game.GetSpriteFrameOffset` reads an absolute frame draw anchor.
`Game.GetSpriteFrameMotion` reads an authored per-frame pixel delta.
`Game.CreateSpriteSequence(... offsets, motions, ...)` stores both independently and
shares original atlas frames. `FalloutAnimation::TotalMotion` sums the deltas. Last-pose
extraction keeps the inclusive sum; the death/reload splice subtracts the first part's
total motion from the second part's first delta on both axes. Client QA in
`Scripts/Tests/Test_FalloutAnimation.fos` checks actual assets, directions and joins.

`Animation.SelectPlayback` chooses idle, movement, knockout and death playback.
`OnCritterAnimationInit` receives the neutral context and authoritative movement speed;
scripts return state/action, flags, normalized time and playback speed. `Movement`
enables alignment with world movement for any action; `Freeze` takes precedence and
selects an inclusive normalized pose. TLA owns animation identifiers and the configured
preview pair in `TLA.fomain`.

The Engine separates the following responsibilities:

- `SpriteSheet` owns images, ordinary sprite offsets (`_sprOffset`) and independent per-frame motion deltas (`_sprMotion`).
- `CritterHexView::SetAnimSpr` selects the image and draw anchor.
- `AnimationMovement` accumulates motion deltas, transfers cycle phase, selects poses
  by distance and computes visual compensation using pure integer math.
- `CritterHexView::RefreshAnimOffset` retains the active sheet and anchor, measures
  displacement from the current `MovingContext` start and applies that compensation.
- `RefreshOffs` combines logical `HexOffset`, extra smoothing and `_offsAnim` once.
  `MapSprite` applies the absolute draw anchor separately.

Frame offsets are presentation data. They never change the entity's hex, path,
travel distance or speed. An active Movement animation cancels within-frame
interpolation and preserves phase on direction/sheet changes. Timed/frozen poses use
inclusive accumulated offsets; a zero-total cycle cannot spatially drive frames.
Stop normalization repartitions hex and offset
without changing world placement.

The reusable formulas, data format and acceptance matrix live in the
[Engine frame-offset guide](../Engine/Docs/en/how-to/content/sprite-root-motion.md).
`NextX`/`NextY` source keys and baked SpriteResource v2 remain unchanged.
