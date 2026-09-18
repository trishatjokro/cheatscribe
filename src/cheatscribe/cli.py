"""cheatscribe CLI: upload notes -> AI-summarized, handwritten cheat sheet.

Usage:
    python -m cheatscribe.cli --input notes1.pptx notes2.pdf --out cheatsheet.png
    python -m cheatscribe.cli --input notes.txt --out sheet.svg --backend engine --columns 2
"""

from __future__ import annotations

import argparse

from .ingest import load_documents
from .layout import PAGE_HEIGHT, PAGE_WIDTH, layout_cheat_sheet
from .render import render_page
from .summarize import save_cheat_sheet, summarize


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a handwritten AI cheat sheet.")
    parser.add_argument("--input", nargs="+", required=True, help="Notes/slides/PDFs/images to summarize.")
    parser.add_argument("--out", required=True, help="Output image path (.png or .svg).")
    parser.add_argument("--topic", default=None, help="Optional hint, e.g. 'cell respiration only'.")
    parser.add_argument("--target-words", type=int, default=1000)
    parser.add_argument("--columns", type=int, default=3)
    parser.add_argument(
        "--backend",
        choices=["auto", "engine", "fallback"],
        default="auto",
        help="'engine' = real handwriting-synthesis via Docker, 'fallback' = handwriting-style font.",
    )
    parser.add_argument("--save-cheat-sheet-json", default=None, help="Optionally dump the intermediate summary.")
    args = parser.parse_args()

    print(f"[cheatscribe] Reading {len(args.input)} file(s)...")
    documents = load_documents(args.input)

    print("[cheatscribe] Summarizing into a cheat sheet...")
    sheet = summarize(documents, target_words=args.target_words, topic_hint=args.topic)
    print(f"[cheatscribe] '{sheet.title}' — {len(sheet.sections)} sections")

    if args.save_cheat_sheet_json:
        save_cheat_sheet(sheet, args.save_cheat_sheet_json)

    print(f"[cheatscribe] Laying out {args.columns} column(s)...")
    placements = layout_cheat_sheet(sheet, columns=args.columns)

    print(f"[cheatscribe] Rendering (backend={args.backend})...")
    used = render_page(placements, PAGE_WIDTH, PAGE_HEIGHT, args.out, backend=args.backend)
    print(f"[cheatscribe] Done via '{used}' backend -> {args.out}")


if __name__ == "__main__":
    main()
