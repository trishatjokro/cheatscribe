"""Compose per-line SVGs (produced by the handwriting engine) onto one page
SVG at the positions/scales the layout step computed.

Kept as a small, dependency-free XML transform so it doesn't care about the
engine's internal drawing code — only that each line comes back as a
standalone SVG file with a width/height we can scale against.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from ..layout import LinePlacement

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def _dimension(value: str | None, fallback: float) -> float:
    if not value:
        return fallback
    return float(value.rstrip("px").rstrip("pt") or fallback)


def compose_page(
    placements: list[LinePlacement],
    line_svg_paths: dict[int, str],
    page_width: int,
    page_height: int,
    out_path: str,
) -> None:
    """line_svg_paths maps the index into `placements` to the rendered SVG file
    the engine produced for that line's text."""
    svg = ET.Element(
        f"{{{SVG_NS}}}svg",
        {
            "width": str(page_width),
            "height": str(page_height),
            "viewBox": f"0 0 {page_width} {page_height}",
        },
    )
    ET.SubElement(svg, f"{{{SVG_NS}}}rect", {"width": "100%", "height": "100%", "fill": "white"})

    for i, placement in enumerate(placements):
        line_path = line_svg_paths.get(i)
        if not line_path or not Path(line_path).exists():
            continue
        line_root = ET.parse(line_path).getroot()
        natural_width = _dimension(line_root.get("width"), placement.width)
        scale = placement.width / natural_width if natural_width else 1.0

        group = ET.SubElement(
            svg,
            f"{{{SVG_NS}}}g",
            {"transform": f"translate({placement.x},{placement.y}) scale({scale})"},
        )
        for child in line_root:
            group.append(child)

    ET.ElementTree(svg).write(out_path, xml_declaration=True, encoding="UTF-8")
