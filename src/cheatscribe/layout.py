"""Lay a CheatSheet out onto a page as positioned lines, cram-sheet style:
multiple columns, section headings, short bullet lines. Produces a flat list
of LinePlacement records that the render step turns into pixels/strokes —
this module knows nothing about how a line actually gets drawn.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass

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


def layout_cheat_sheet(
    sheet: CheatSheet,
    columns: int = 3,
    page_width: int = PAGE_WIDTH,
    page_height: int = PAGE_HEIGHT,
) -> list[LinePlacement]:
    column_width = (page_width - 2 * MARGIN - (columns - 1) * COLUMN_GAP) // columns
    placements: list[LinePlacement] = []

    col = 0
    y = MARGIN
    col_x = MARGIN

    def start_new_column():
        nonlocal col, y, col_x
        col += 1
        y = MARGIN
        col_x = MARGIN + col * (column_width + COLUMN_GAP)

    for section in sheet.sections:
        heading_lines = textwrap.wrap(
            section.heading.upper(), _wrap_width_chars(column_width, HEADING_FONT_SIZE)
        ) or [section.heading.upper()]
        item_line_groups = [
            textwrap.wrap(item, _wrap_width_chars(column_width, ITEM_FONT_SIZE)) or [item]
            for item in section.items
        ]

        needed = len(heading_lines) * HEADING_LINE_HEIGHT + (
            item_line_groups[0:1] and len(item_line_groups[0]) * ITEM_LINE_HEIGHT
        )
        if col < columns and y + needed > page_height - MARGIN:
            if col + 1 < columns:
                start_new_column()
            # if it's the last column, just overflow rather than drop content

        for hl in heading_lines:
            if y + HEADING_LINE_HEIGHT > page_height - MARGIN and col + 1 < columns:
                start_new_column()
            placements.append(
                LinePlacement(hl, col_x, y, column_width, HEADING_FONT_SIZE, True, col)
            )
            y += HEADING_LINE_HEIGHT

        for lines in item_line_groups:
            for line in lines:
                if y + ITEM_LINE_HEIGHT > page_height - MARGIN and col + 1 < columns:
                    start_new_column()
                placements.append(
                    LinePlacement(line, col_x, y, column_width, ITEM_FONT_SIZE, False, col)
                )
                y += ITEM_LINE_HEIGHT

        y += ITEM_LINE_HEIGHT // 2  # gap before next section

    return placements
