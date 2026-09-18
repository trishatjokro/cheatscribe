"""Zero-setup renderer: draws the laid-out cheat sheet with a handwriting-style
font via Pillow. This is the "looks like a computer" baseline — it exists so
the pipeline runs end-to-end with no engine setup. Swap in the docker/
handwriting-synthesis backend (render.handwriting_adapter) for output that
actually varies stroke-to-stroke.

Uses a Google Fonts handwriting face (SIL Open Font License) rather than
anything proprietary. Falls back to Pillow's default font with a printed
warning if the font file isn't found, so this never hard-fails.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ..layout import LinePlacement

DEFAULT_FONT_CANDIDATES = [
    # Populate by running: scripts/fetch_fallback_font.sh (downloads Caveat
    # from Google Fonts into this directory). Not bundled in the repo.
    Path(__file__).parent / "assets" / "Caveat-Regular.ttf",
    Path("/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf"),  # common on macOS
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for candidate in DEFAULT_FONT_CANDIDATES:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    print(
        "[cheatscribe] No handwriting font found — using Pillow's default font. "
        "Run scripts/fetch_fallback_font.sh for a nicer placeholder, or set up "
        "the real handwriting-synthesis engine (see README).",
        file=sys.stderr,
    )
    return ImageFont.load_default(size=size)


def render_fallback(
    placements: list[LinePlacement],
    page_width: int,
    page_height: int,
    out_path: str,
    ink_color: tuple[int, int, int] = (25, 25, 112),
) -> None:
    img = Image.new("RGB", (page_width, page_height), "white")
    draw = ImageDraw.Draw(img)
    font_cache: dict[int, ImageFont.FreeTypeFont] = {}

    for placement in placements:
        if placement.font_size not in font_cache:
            font_cache[placement.font_size] = _load_font(placement.font_size)
        font = font_cache[placement.font_size]
        color = (0, 0, 0) if placement.is_heading else ink_color
        draw.text((placement.x, placement.y), placement.text, font=font, fill=color)

    img.save(out_path)
