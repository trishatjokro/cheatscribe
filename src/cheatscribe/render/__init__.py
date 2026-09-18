from ..layout import LinePlacement
from .fallback_font_renderer import render_fallback
from .handwriting_adapter import engine_available, render_with_engine


def render_page(
    placements: list[LinePlacement],
    page_width: int,
    page_height: int,
    out_path: str,
    backend: str = "auto",
) -> str:
    """backend: "engine" (real handwriting-synthesis via Docker), "fallback"
    (handwriting-style font, zero setup), or "auto" (engine if built, else
    fallback). Returns the backend actually used."""
    if backend == "engine" or (backend == "auto" and engine_available()):
        render_with_engine(placements, page_width, page_height, out_path)
        return "engine"

    fallback_path = out_path if out_path.lower().endswith((".png", ".jpg", ".jpeg")) else out_path + ".png"
    render_fallback(placements, page_width, page_height, fallback_path)
    return "fallback"
