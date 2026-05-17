# Walk Animation: Root Motion and the Walk Cycle

This document describes how per-frame root motion baked into walk/run animations is consumed at
runtime to drive sprite frame selection and per-frame screen offsets for moving 2D critters.

It covers the contract between three layers:

- Baker: how root motion is encoded into the baked image format.
- Client sprite runtime: how that data is loaded into `SpriteSheet`.
- Critter view: how the walk cycle is aligned with the engine's linear hex motion in
  `CritterHexView`.

Code references in this document point into the `Engine/` submodule.

## Root motion in the baked image format

`ImageBaker::FrameShot` (see `Engine/Source/Tools/ImageBaker.h`) carries per-frame metadata for an
animation. The two relevant fields are:

- `NextX` (`int16_t`)
- `NextY` (`int16_t`)

These are **per-frame root-motion deltas in pixels**. The sum across all frames of an animation is
the total displacement the artist baked into one cycle (e.g. one full walk loop moves the visual
sprite by `sum(NextX, NextY)` over its frames). Conceptually:

```
total_root_motion = sum_{i=0..N-1}( (NextX[i], NextY[i]) )  =  T
```

The various format-specific loaders in `ImageBaker.cpp` (`LoadFofrm`, `LoadFrm`, `LoadArt`,
`LoadSpr`, `LoadPng`, ...) all populate `NextX/NextY` from their source-specific data; FOFRM key
names on disk (`next_x_N` / `NextX_N`) remain unchanged to preserve backward compatibility with
existing content.

`BakeCollection` serialises each frame's two `int16_t` deltas straight into the baked sprite stream;
the runtime layout is unchanged from previous versions.

## Runtime: `SpriteSheet::_sprOffset`

`DefaultSpriteFactory::LoadAnimation` (see `Engine/Source/Client/DefaultSprites.cpp`) reads the
baked deltas back into `SpriteSheet::_sprOffset` (one `ipos32` per frame, per direction).

`SpriteSheet::GetSprOffset()` exposes this vector to consumers. The values mean different things
depending on the animation kind:

- For non-moving animations (anything that is not `Walk` / `Run`), the runtime simply accumulates
  the per-frame delta into `CritterHexView::_offsAnim` so the sprite drifts along the authored path
  while the critter stays anchored to its hex.
- For `Walk` / `Run`, the deltas describe the cycle's spatial trajectory. The total
  `T = sum(_sprOffset)` is the displacement of the cycle, which typically covers one or more hex
  steps but need not be exactly aligned with the hex grid pitch.

## Aligning the walk cycle with engine motion (`CritterHexView`)

When a critter walks, two parallel things happen each frame:

1. The engine moves the critter linearly between hexes via `MovingContext::EvaluateProgress` and
   `_map->MoveCritter`. The critter's screen position is `cur_hex_pixel + hex_offset`, with
   `hex_offset` rounding to integer pixels component-wise inside `MovingContext::BuildProgress`.
2. The walk animation is meant to be shown at specific cumulative root-motion offsets - i.e. the
   artist drew frame *i* to be positioned at `cycle_start + accum[i]`, where
   `accum[i] = sum_{k=0..i}(_sprOffset[k])`.

These two things disagree because:

- The cycle's `T` may span more than one hex (e.g. 2.15 hexes per cycle).
- The cycle's `T` direction may not exactly align with the hex step vector for the given
  direction.
- Component-wise rounding inside `BuildProgress` makes `hex_offset` zig-zag in integer pixels rather
  than tracking a smooth float position.

The implementation drives the rendered frame and its offset from the engine's integer linear
position, so the sprite is snapped to the frame's authored position while the engine continues to
own the actual hex transitions underneath.

### Anchor and cycle phase

The cycle's spatial reference is an anchor:

```cpp
raw_ptr<const SpriteSheet> _walkAnchorAnim;   // the per-direction SpriteSheet the anchor is for
ipos32                     _walkAnchorDisp;   // pos at the moment the anchor was set
```

`pos` is the integer-pixel displacement from the start of the current `MovingContext` to the
critter's current linear position, computed by `EvaluateMovementDisplacement`:

```
pos = GetHexOffset(start_hex, cur_hex) + hex_offset - start_hex_offset
```

`pos` is continuous through hex snaps (`cur_hex` and `hex_offset` jump by opposite step vectors at
the snap point, so their sum is preserved).

The anchor-relative cycle progress is:

```
rel              = pos - _walkAnchorDisp
rel_dot_total    = rel . T               (scalar pixel projection, int64)
total_dot_total  = T . T                 (|T|^2 in pixel units, int64)

cycle_proj       = rel_dot_total mod total_dot_total    (wrapped into [0, |T|^2))
cycle_number     = floor(rel_dot_total / total_dot_total)
```

`cycle_proj / total_dot_total` is the cycle phase in `[0, 1)`. All arithmetic is integer; no
floating-point rounding is involved.

### Frame selection (`EvaluateMovementFrameIndex`)

For each frame *i*, project its cumulative root motion onto `T`:

```
accum_dot_total[i] = accum[i] . T
```

The picked frame minimises `|accum_dot_total[i] - cycle_proj|`. This selects the frame whose
authored position sits closest (along `T`) to the critter's current point in the cycle.

### Offset computation (`SetAnimSpr`, walk/run branch)

`_offsAnim` is computed so that the rendered sprite sits at the picked frame's intended position
relative to the integer cycle start:

```
cycle_start = _walkAnchorDisp + cycle_number * T
_offsAnim   = (cycle_start - pos) + accum[i]
```

Substituting `sprite_pos = cur_hex_pixel + hex_offset + _offsAnim` and
`cur_hex_pixel + hex_offset = start_hex_pixel + pos` gives:

```
sprite_pos = start_hex_pixel + start_hex_offset + cycle_start + accum[i]
```

This is **constant for the duration of one frame inside one cycle** - it depends only on the cycle
number, the frame index *i*, and the original movement start. While the frame is shown, the sprite
holds its position; `pos` advances and `_offsAnim` shifts by `-pos` exactly, cancelling the engine's
linear motion. The visual motion comes from frame transitions.

When the picked frame changes from *i* to *i+1*, `sprite_pos` advances by
`accum[i+1] - accum[i] = _sprOffset[i+1]`, i.e. the artist's authored per-frame root motion delta.
When the cycle wraps (`cycle_proj` rolls from near `|T|^2` back to `0`), `cycle_number` increments
by one, `accum[i]` resets from near `T` to `_sprOffset[0]`, and the net visual delta is
`_sprOffset[0]`. The sprite continues forward through the next cycle without backwards jumps.

### Direction changes mid-walk

When `progress.Dir` changes inside a single `MovingContext`, the per-direction `SpriteSheet`
returned by `ResourceManager::GetCritterAnimFrames` switches to a different pointer with a
different `T` and a different number of frames. Naively re-anchoring to the current `pos` would
restart the new cycle from `cycle_proj = 0`, which visually resets the leg to frame 0 on every
turn (very obvious during sustained running through curves).

To preserve the cycle phase across that switch, `Process()` recomputes `_walkAnchorDisp` such that
the new `rel . T_new / |T_new|^2` evaluates to the same fraction as `rel_old . T_old / |T_old|^2`
just before the switch:

```
phase           = old_cycle_proj / |T_old|^2
new_anchor_disp = pos - phase * T_new
```

Encoded in integer math:

```
new_anchor_disp.x = pos.x - round(old_cycle_proj * T_new.x / |T_old|^2)
new_anchor_disp.y = pos.y - round(old_cycle_proj * T_new.y / |T_old|^2)
```

After the switch, the new anim continues from the matching phase point and the next walking leg
lands naturally instead of restarting.

### Lifecycle

- `SetMoving` and `StopMoving` clear `_walkAnchorAnim` and `_walkAnchorDisp`. A fresh movement
  always begins with `cycle_proj = 0` and frame 0.
- The first `Process()` tick of a new movement (or after a direction change) re-runs the anchor
  setup as soon as it detects `cur_anim.Frames != _walkAnchorAnim`.
- For non-walk/non-run animations and for non-moving critters, the walk-cycle branch is skipped
  and `_offsAnim` falls back to the simple accumulation used by other animations.

## Editing notes

- `_sprOffset` values are produced exclusively by the baker from `FrameShot::NextX/NextY`; runtime
  code should not synthesise them.
- The FOFRM file format still uses the historical `next_x_N` / `NextX_N` (lowercase and camel)
  keys. Renaming those on-disk keys would break existing content - leave them as-is.
- All projection / cycle math in `CritterHexView` is integer (`int32_t` / `int64_t`) by design.
  Reintroducing float intermediates re-introduces the per-axis rounding jitter that the integer
  formulation was written to eliminate.
