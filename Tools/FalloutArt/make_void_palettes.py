"""Writes the palettes that turn the void of the Fallout bridge tiles black.

The Arroyo bridge and Bridge Keeper tiles (art/tiles/brda*, brdb*) paint the depth of the chasm with Fallout
palette colour 50, a flat purple. Fallout never showed it: at 640x480 the scroll limits kept it off screen, and the
high resolution patch clips everything past the map edges to black. At TLA's resolutions the camera reaches it, so
these tiles bake with their own palette, the engine's default one with colour 50 set to black. The image baker picks
up <name>.pal beside an FRM (ImageBaker::LoadFrm), so the palettes go into the FOArt pack as Resources/FOArt.

Only the tiles that use colour 50 get a palette, and elsewhere in the tile set it shades a pixel or three, so no
other art changes. Run from the repository root after the data packs or the engine palette change:

    python Tools/FalloutArt/make_void_palettes.py
"""

import re
import struct
import sys
import zipfile
from pathlib import Path

VOID_INDEX = 50
SOURCE_PACK = Path("Resources/DataPacks/fo_art.zip")
ENGINE_BAKER = Path("Engine/Source/Tools/ImageBaker.cpp")
OUTPUT_DIR = Path("Resources/FOArt/art/tiles")


def engine_palette() -> list[tuple[int, int, int]]:
    # FoPalette is the engine's copy of Fallout's color.pal, stored as RGBA bytes at four times the 6-bit values
    source = ENGINE_BAKER.read_text(encoding="utf-8")
    body = source[source.index("FoPalette[") :]
    body = body[body.index("{") + 1 : body.index("};")]
    values = [int(value, 16) for value in re.findall(r"0x([0-9a-fA-F]{2})", body)]

    if len(values) != 256 * 4:
        raise SystemExit(f"FoPalette has {len(values)} bytes, expected 1024")

    return [(values[i], values[i + 1], values[i + 2]) for i in range(0, len(values), 4)]


def frm_uses_index(data: bytes, index: int) -> bool:
    frame_count = struct.unpack(">H", data[8:10])[0]
    offset = 0x3E

    for _ in range(frame_count):
        width, height, size = struct.unpack(">HHI", data[offset : offset + 8])

        if index in data[offset + 12 : offset + 12 + width * height]:
            return True

        offset += 12 + size

    return False


def main() -> int:
    palette = engine_palette()
    palette[VOID_INDEX] = (0, 0, 0)
    pal_data = bytes(channel // 4 for color in palette for channel in color)

    with zipfile.ZipFile(SOURCE_PACK) as pack:
        tiles = [name for name in pack.namelist() if re.fullmatch(r"art/tiles/brd[ab]\d+\.frm", name, re.IGNORECASE)]
        void_tiles = sorted(name for name in tiles if frm_uses_index(pack.read(name), VOID_INDEX))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for stale in OUTPUT_DIR.glob("*.pal"):
        stale.unlink()

    for name in void_tiles:
        (OUTPUT_DIR / (Path(name).stem + ".pal")).write_bytes(pal_data)

    print(f"{len(void_tiles)} of {len(tiles)} bridge tiles use colour {VOID_INDEX}; palettes written to {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
