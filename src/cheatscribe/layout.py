"""Lay a CheatSheet out onto a page as positioned lines, cram-sheet style:
multiple columns, section headings, short bullet lines. Produces a flat list
of LinePlacement records that the render step turns into pixels/strokes —
this module knows nothing about how a line actually gets drawn.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, replace

from .summarize import CheatSheet

# US Letter at 150 DPI
PAGE_WIDTH = 1650
PAGE_HEIGHT = 1275  # landscape reads better for multi-column cheat sheets
MARGIN = 50
COLUMN_GAP = 40

HEADING_FONT_SIZE = 30
ITEM_FONT_SIZE = 22
HEADING_LINE_HEIGHT = int(HEADING_FONT_SIZE * 1.4)
ITEM_LINE_HEIGHT = int(ITEM_FONT_SIZE * 1.35)
AVG_CHAR_WIDTH_FACTOR = 0.52  # rough width-per-point for handwritten cursive


@dataclass
class LinePlacement:
    text: str
    x: int
    y: int
    width: int
    font_size: int
    is_heading: bool
    column: int


def _wrap_width_chars(column_width: int, font_size: int) -> int:
    char_width = font_size * AVG_CHAR_WIDTH_FACTOR
    return max(10, int(column_width / char_width))


@dataclass
class _Line:
    text: str
    font_size: int
    height: int
    is_heading: bool
    starts_section: bool


def _flatten(sheet: CheatSheet, column_width: int) -> list[_Line]:
    lines: list[_Line] = []
    for section in sheet.sections:
        heading_lines = textwrap.wrap(
            section.heading.upper(), _wrap_width_chars(column_width, HEADING_FONT_SIZE)
        ) or [section.heading.upper()]
        for i, hl in enumerate(heading_lines):
            lines.append(_Line(hl, HEADING_FONT_SIZE, HEADING_LINE_HEIGHT, True, i == 0))

        for item in section.items:
            wrapped = textwrap.wrap(item, _wrap_width_chars(column_width, ITEM_FONT_SIZE)) or [item]
            for wl in wrapped:
                lines.append(_Line(wl, ITEM_FONT_SIZE, ITEM_LINE_HEIGHT, False, False))

        if lines:  # gap before the next section rides on the last line of this one
            lines[-1] = replace(lines[-1], height=lines[-1].height + ITEM_LINE_HEIGHT // 2)
    return lines


def layout_cheat_sheet(
    sheet: CheatSheet,
    columns: int = 3,
    page_width: int = PAGE_WIDTH,
    page_height: int = PAGE_HEIGHT,
) -> list[LinePlacement]:
    column_width = (page_width - 2 * MARGIN - (columns - 1) * COLUMN_GAP) // columns
    available_height = page_height - 2 * MARGIN

    lines = _flatten(sheet, column_width)
    if not lines:
        return []

    # Balance across all columns instead of filling one and spilling over: aim
    # for an even share of the total, so a 3-column sheet actually reads as three.
    total_height = sum(line.height for line in lines)
    target_height = min(available_height, max(total_height / columns, HEADING_LINE_HEIGHT))

    placements: list[LinePlacement] = []
    col = 0
    y = MARGIN

    for i, line in enumerate(lines):
        limit = available_height if col == columns - 1 else target_height

        # keep a heading with the first couple of lines under it
        lookahead = line.height
        if line.starts_section:
            for follower in lines[i + 1 : i + 3]:
                lookahead += follower.height

        if y - MARGIN + lookahead > limit and col + 1 < columns and placements:
            col += 1
            y = MARGIN

        placements.append(
            LinePlacement(
                text=line.text,
                x=MARGIN + col * (column_width + COLUMN_GAP),
                y=y,
                width=column_width,
                font_size=line.font_size,
                is_heading=line.is_heading,
                column=col,
            )
        )
        y += line.height

    return placements
