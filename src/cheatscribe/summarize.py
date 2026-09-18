"""Summarize uploaded notes/slides into a dense, structured cheat sheet.

Implements the density/clustering/relevance-filtering approach from
RESEARCH.md rather than a generic "summarize this" prompt: a hard length
target, cross-source topic clustering before compression, exam-relevance
filtering, and short-line output (so the handwriting renderer gets discrete
chunks, not paragraphs to wrap itself).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import anthropic

from .ingest import Document

MODEL = "claude-sonnet-5"

CHEAT_SHEET_TOOL = {
    "name": "emit_cheat_sheet",
    "description": "Emit the finished cheat sheet as structured sections and short bullet lines.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Short title for the cheat sheet."},
            "sections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "heading": {"type": "string"},
                        "items": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "Each item is one short, self-contained line "
                                "(aim for under ~60 characters) — a definition, "
                                "formula, step, or comparison point. Not a paragraph."
                            ),
                        },
                    },
                    "required": ["heading", "items"],
                },
            },
        },
        "required": ["title", "sections"],
    },
}

SYSTEM_PROMPT = """\
You are building an exam cheat sheet from a student's uploaded notes/slides. \
Your only goal is maximum useful information density in minimum space \
(the output will be handwritten onto a physical page, so it must be short).

Rules:
1. Target ~{target_words} words total across all items. This is a hard budget — \
   cut ruthlessly rather than padding.
2. First identify the topic/subtopic outline across ALL provided sources, \
   deduplicating overlapping content from different files before writing any \
   items — do not summarize each source separately and concatenate.
3. Keep only exam-relevant content: definitions, named mechanisms/processes/steps, \
   formulas, key numbers, comparison points. Drop narrative context, filler, \
   restatements, and anything not likely to be tested.
4. Each item must be a short, standalone line (aim under ~60 characters) — \
   shorthand notation is encouraged (arrows, abbreviations). No paragraphs.
5. Group items under clear topic headings. Prefer more headings with fewer \
   items each over one giant list.

Call the emit_cheat_sheet tool exactly once with the finished result.
"""


@dataclass
class CheatSheetItem:
    heading: str
    items: list[str] = field(default_factory=list)


@dataclass
class CheatSheet:
    title: str
    sections: list[CheatSheetItem]


def summarize(
    documents: list[Document],
    target_words: int = 1000,
    topic_hint: str | None = None,
    client: anthropic.Anthropic | None = None,
) -> CheatSheet:
    client = client or anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    content = [doc.as_content_block() for doc in documents]
    instruction = "Build a cheat sheet from the attached materials."
    if topic_hint:
        instruction += f" Focus: {topic_hint}."
    content.append({"type": "text", "text": instruction})

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT.format(target_words=target_words),
        tools=[CHEAT_SHEET_TOOL],
        tool_choice={"type": "tool", "name": "emit_cheat_sheet"},
        messages=[{"role": "user", "content": content}],
    )

    tool_use = next(b for b in response.content if b.type == "tool_use")
    data = tool_use.input
    return CheatSheet(
        title=data["title"],
        sections=[CheatSheetItem(heading=s["heading"], items=s["items"]) for s in data["sections"]],
    )


def cheat_sheet_to_dict(sheet: CheatSheet) -> dict:
    return {
        "title": sheet.title,
        "sections": [{"heading": s.heading, "items": s.items} for s in sheet.sections],
    }


def save_cheat_sheet(sheet: CheatSheet, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cheat_sheet_to_dict(sheet), f, indent=2)
