# cheatscribe

Upload however many notes, slides, or PDFs you want on any subject. cheatscribe
summarizes what's actually exam-relevant into a dense, one-page cheat sheet,
then renders it in handwriting instead of a typed font.

Started as a biology-cheat-sheet tool, built general-purpose — use it for
whatever you're studying.

See [RESEARCH.md](RESEARCH.md) for the survey of existing tools and handwriting-
synthesis approaches that shaped this design.

## How it works

```
your files (.pptx/.pdf/.txt/.md/images)
        │
        ▼
   ingest.py          — extracts text; sparse/scanned pages go through as images
        │
        ▼
   summarize.py        — Claude condenses everything into short, deduped,
        │                 exam-relevant bullet points under a word budget
        ▼
   layout.py           — arranges sections/bullets into a multi-column
        │                 cheat-sheet page (like a physical cram sheet)
        ▼
   render/             — draws each line in handwriting
        │
        ├─ handwriting_adapter.py   real handwriting-synthesis RNN, via Docker
        └─ fallback_font_renderer.py  handwriting-style font, zero setup
```

The summarizer is the "easy half" — a well-designed prompt beats generic
summarization tools by enforcing a hard density budget, clustering topics
across all your sources before compressing (instead of summarizing each file
separately), and outputting short standalone lines instead of paragraphs.

The handwriting half is the hard part — see below.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...  # your key
```

Try it immediately with the zero-setup fallback renderer (a handwriting-style
font — looks like a computer, but proves the pipeline works):

```bash
python -m cheatscribe.cli --input examples/sample_notes.txt --out out/cheatsheet.png
```

Optionally fetch a nicer placeholder font first:

```bash
scripts/fetch_fallback_font.sh
```

## Real handwriting rendering

The fallback font is intentionally the "robotic, repeated-glyph" look this
project exists to avoid. For actual natural stroke variation, build the
handwriting-synthesis engine (the RNN behind calligrapher.ai):

```bash
docker build -t cheatscribe-handwriting-engine docker/handwriting_engine
python -m cheatscribe.cli --input examples/sample_notes.txt --out out/cheatsheet.svg --backend engine
```

This clones `sjvasquez/handwriting-synthesis` fresh at Docker build time — see
**Credits** below for why it's never copied into this repo — and isolates its
2018-era TensorFlow 1.6 dependency inside the container. `render_bridge.py`
in `docker/handwriting_engine/` is cheatscribe's own code; it just imports
that project's public `Hand` API.

This ships with the RNN's 9 preset writing styles (not your own handwriting —
see RESEARCH.md for why true personal-handwriting mimicry is still
research-grade). `--backend auto` (default) uses the engine if it's built,
otherwise falls back to the font renderer automatically.

## Usage

```bash
python -m cheatscribe.cli \
  --input lecture1.pptx lecture2.pdf my_notes.md \
  --topic "midterm 2: cell respiration and photosynthesis" \
  --columns 3 \
  --out out/cheatsheet.png
```

| Flag | Purpose |
|---|---|
| `--input` | One or more files: `.pptx`, `.pdf`, `.txt`, `.md`, `.png/.jpg` (including photos of handwritten notes) |
| `--topic` | Optional focus hint passed to the summarizer |
| `--target-words` | Word budget for the summary (default 1000) |
| `--columns` | Cheat-sheet column count (default 3) |
| `--backend` | `auto` / `engine` / `fallback` |
| `--save-cheat-sheet-json` | Dump the intermediate structured summary for inspection |

## Credits

Handwriting rendering is powered by an implementation of:

> Alex Graves, ["Generating Sequences With Recurrent Neural Networks"](https://arxiv.org/abs/1308.0850), 2013.

via [sjvasquez/handwriting-synthesis](https://github.com/sjvasquez/handwriting-synthesis)
(Sean Vasquez) — the same model behind the [calligrapher.ai](https://www.calligrapher.ai/)
demo. That repository has no published LICENSE, so cheatscribe does not vendor
or redistribute its source. `docker/handwriting_engine/Dockerfile` clones it
directly from upstream at build time — nothing of it is committed to this
repository. If you build the engine locally, you're using it exactly as its
author published it.

## Project status

Scaffold stage: ingest/summarize/layout/fallback-render are wired end-to-end
and runnable today. The Docker engine path is implemented per the upstream
project's documented API but not yet verified against a real build (that
project's dependencies are old enough that first-run debugging is expected —
see RESEARCH.md § technical build options).
