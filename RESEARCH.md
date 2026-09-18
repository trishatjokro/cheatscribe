# cheatscribe — research notes

Initial research pass (2026-09-18) into what already exists for the two halves of this project:
1. Summarizing uploaded notes/slides into a dense cheat sheet
2. Rendering that cheat sheet in the user's own handwriting

Four research passes were run in parallel: academic/SOTA handwriting synthesis, existing consumer handwriting-mimicry apps, existing note→cheat-sheet summarization tools, and practical build options for a hobbyist. Raw findings below, followed by a synthesis.

---

## 1. Academic / state-of-the-art handwriting synthesis

**Online vs. offline lineage**

- **Graves 2013, "Generating Sequences With Recurrent Neural Networks"** (arxiv.org/abs/1308.0850) — the foundational **online** (stroke/pen-trajectory) LSTM model. Live demo: **calligrapher.ai** (built by Sean Vasquez, code at github.com/sjvasquez/handwriting-synthesis). Generates fluid, natural cursive with real stroke variation — but mimics one of a fixed set of ~9–13 pretrained writer styles, not an arbitrary new person from samples.
- **GANwriting** (offline, few-shot, word-level) and successors **HiGAN / HiGAN+**, **SmartPatch**, **Deepwriting/CoSE** (disentangles style vs. content in a latent stroke space) — early GAN-era offline style-conditioning work.
- **Handwriting Transformers (HWT)**, ICCV 2021, github.com/ankanbhunia/Handwriting-Transformers — self-attention encoder captures global+local style from a handful of reference word images; generalizes to unseen styles/words few-shot; has a HuggingFace demo. Preferred 81% of the time over prior methods in human eval.
- **VATr / VATr++** (2024) — transformer + learned "archetype" glyph book, improved rare-character generalization.
- **DiffusionPen** (ECCV 2024), github.com/koninik/DiffusionPen, weights on huggingface.co/konnik/DiffusionPen — few-shot **latent diffusion** model, learns a writer's style from as few as **5 reference samples**. Best-documented, most reproducible option for "new person, modest sample count."
- **One-DM** (ECCV 2024), github.com/dailenson/One-DM — pushes to **a single reference sample** via high-frequency style extraction (slant, joining) fused into the diffusion condition.
- **DiffInk** (ICLR 2026) — first latent diffusion transformer for full-line (not just word-level) online handwriting generation — closer to multi-line cheat-sheet needs, but very new/research-only.
- **Emuru / Eruku** (2025/2026) — autoregressive latent-image generation, better zero-shot generalization and length flexibility.
- Survey: "A Survey of Modern Handwriting Generation Models" (2025); curated list github.com/koninik/awesome-handwritten-text-generation.

**Usable open-source for a hobbyist:** DiffusionPen (released checkpoints, documented) and HWT (HuggingFace Space demo, lowest friction to try) are most realistic. One-DM is newer/less battle-tested but needs only 1 sample. sjvasquez/handwriting-synthesis is easiest to run but doesn't condition on your own handwriting — only preset styles. All are research code: expect Python/PyTorch environment wrangling, GPU preference, sparse docs.

**Online vs. offline — which fits this project:** Online (stroke/xy/pressure/time) needs capturing handwriting *as it's written* (tablet/stylus), not photos — highest quality pen dynamics but impractical if source is scanned notes. Offline (image-only: GANwriting, HWT, VATr, DiffusionPen, One-DM) trains/conditions on photos/scans — matches an "upload samples" plan. Output is rendered word/line images, not editable stroke paths, so page layout means stitching generated images together.

**Honest feasibility (Sept 2026):** Still mostly research-grade, not a polished consumer pipeline. No one-click "upload photos, get natural AI handwriting" product exists at research quality. Consumer "handwriting-to-font" tools are the opposite of what's wanted (fixed glyph repeated = robotic). Realistic hobbyist path: try HWT HuggingFace Space or DiffusionPen zero/few-shot against your own samples first with no training; if promising, fine-tune DiffusionPen's style-encoder on ~5–20 samples (feasible on one consumer GPU/Colab); treat One-DM as a lighter fallback. Expect quality to degrade on out-of-distribution content (numbers, jargon, symbols) and longer multi-line text — both heavy in a cheat sheet. Budget this as a multi-week experimentation effort, not a weekend build, if pursuing real ML.

Sources: arxiv.org/abs/1308.0850, calligrapher.ai, github.com/sjvasquez/handwriting-synthesis, github.com/ankanbhunia/Handwriting-Transformers, github.com/koninik/DiffusionPen, huggingface.co/konnik/DiffusionPen, github.com/dailenson/One-DM, arxiv.org/abs/2409.06065, arxiv.org/abs/2409.04004, arxiv.org/abs/2104.03964, arxiv.org/pdf/2509.23624, github.com/koninik/awesome-handwritten-text-generation, cse.buffalo.edu/tech-reports/2026-43.pdf, lipi.ai/handwriting, handfonted.xyz, calligraphr.com.

---

## 2. Existing consumer handwriting-mimicry apps/tools

**"Handwriting → font" tools (samples → installable font)**
- **Calligraphr** (formerly iFontMaker) — category leader. Free tier: 75 chars; Pro: full charset, ligatures, letter alternates. Output: TTF/OTF. Limitation: static glyph substitution — same "A" every time, cursive joins hard to fake, caps out short of professional quality. calligraphr.com
- **Fontself** — Illustrator/Photoshop plugin / standalone Mac app, designer-tool flavor, same fixed-glyph limitation. fontself.com
- **Handwriting.io** — patented API (Gracious Eloise) compositing pre-captured glyph variants; B2B/API for personalized mail, not a simple consumer upload flow.
- Mobile apps: "Handwriting Font Maker," "Fontmaker," "Cursive Handwriting Font Maker" — same basic model as Calligraphr.

**Student note-taking apps with AI summarization**
- **GoodNotes** — real AI summarization, Study Sets, lecture transcription, on-device handwriting recognition. Does NOT render summaries back in the user's own handwriting.
- **MyScript Notes (formerly Nebo)** — handwriting recognition + summarization/quizzes, but handwriting→text only, not the reverse.
- **NotesBuilder / handwrittennotes.app** — "print-ready A4 handwritten notes" from PDFs/slides, closest to "cheat sheet in handwriting," but uses a generic handwriting-look font, not the user's own sample.
- **No product found combines "summarize my notes" + "output in my actual handwriting."**

**Newer generative/ML tools (2024–2026)**
- **Calligrapher.ai** — in-browser RNN (IAM dataset), 9 preset styles with sliders, SVG export. Real stroke variation but presets only, not conditioned on an uploaded personal sample.
- Academic (2025–2026): One-DM, zero-shot paragraph-level latent-diffusion imitation (IJCV 2025), DiffInk (ICLR 2026) — the real "type text → ML generates natural strokes conditioned on your sample" approach, but papers/GitHub code, not consumer products.
- **ScribbleSync** (scribblesync.app) — free web app, closest hybrid: draw each letter/ligature once, stores as an image (not a fixed font), composites pages preserving size/slant/baseline variation, exports PNG/PDF. Handles common joins so it looks less mechanical than a pure font.

**Overall read:** No tool today does "type/paste text → instant image in true, natural-variation, your-own handwriting" in one step. Closest ready-made options: Calligraphr (fastest, free tier, accept repetitive/robotic look) or ScribbleSync (more natural, more manual letter-drawing effort). Calligrapher.ai if open to *not* using your own handwriting. True sample-conditioned ML synthesis exists only as research code — confirms this is a genuine build-it-yourself gap.

Sources: calligraphr.com, fontself.com, calligrapher.ai, handwriting.io, goodnotes.com/blog/ai-note-taking-apps, handwrittennotes.app, scribblesync.app/handwriting-generator, link.springer.com (One-DM, IJCV 2025 zero-shot paragraph-level diffusion imitation), ijsat.org survey of handwriting generation models 2025.

---

## 3. Existing note/PPT → cheat-sheet summarization tools

**General note-summarizers**
- **NotebookLM** (notebooklm.google.com) — free. PDFs/Docs/Slides/text/YouTube/audio → Study Guide, flashcards, quizzes, mind maps, audio overviews. Grounded/cited, low hallucination, but output is a study guide/FAQ, not a dense one-pager.
- **Mindgrasp AI** (mindgrasp.ai) — freemium. PDFs/PPTs/lecture recordings/notes → structured summaries, flashcards, quizzes, grounded AI tutor. Has a "study guide from slides" tool but multi-section, not one-pager dense.
- **StudyFetch** (studyfetch.com) — freemium "Spark.E" tutor, strong on lecture recording/video transcription.
- **Quizgecko** — PDFs, docs, audio, and images of handwritten notes → bullet notes, flashcards, quizzes.
- Sana, Wisdolia, Glean — lean more corporate-knowledge/flashcard-browser, less relevant.

**Tools specifically targeting the "exam cheat sheet" format** (dense, one-page, hierarchical) — a real distinct product category:
- **Scholarly** (scholarly.so/tools/cheat-sheet-maker) — free tier (1 lifetime credit). Upload PDF/Word/slides/text or paste notes; AI extracts only exam-relevant formulas/terms/dates and lays out to fit one page (extends to two if dense).
- **SlideSpeak** (slidespeak.co) — free, takes .ppt/.pptx or PDF directly, purpose-built "cheat sheet from PowerPoint/PDF."
- **Cheatish** (cheatish.com) — $3.49/sheet, no subscription. PDF/DOCX/TXT/Markdown → dense 4-column print-ready layout for finals/open-note exams. Closest to a real "cram sheet."
- **SqueezeNotes** (squeezenotes.com) — lecture PDFs → dense exam-ready cheat sheets, editable before download.
- **Solvely** (solvely.ai/ai-cheat-sheet-maker) — up to 10 files + course context → exam-focused sheet with key concepts/formulas/likely-tested topics.
- **MyLens AI** — visual/diagram-oriented, closer to a mind-map hybrid.
- **StudyPDF, Hyperknow, ChatSlide, Testopia** — smaller competitors, same basic flow, some citing source slide/page.

This confirms a real "cheat sheet" sub-niche exists, characterized by: single/few-page output, print-layout awareness (columns, small fonts), "keep only exam-relevant" extraction logic, multi-file upload.

**Handwritten note OCR support:** Few cheat-sheet-specific tools advertise handwriting OCR directly (most assume typed PDFs/slides). Adjacent tools solve it well: **CamNotes**, **AI Study Scanner**, **Taskade's handwriting digitizer**, **Transkribus** (neural handwriting recognition, strong for cursive) convert photographed/handwritten notes to clean text first. Quizgecko also accepts handwritten-note images directly. Pattern: OCR handwriting → clean text → feed into summarization.

**Practical recommendation:** The summarization half is very buildable with an off-the-shelf LLM API and arguably better-tailored than existing tools (most gate cheat-sheet generation behind credits/paywalls, limited layout control). Claude/GPT-4 can directly ingest PPT/PDF (as images or extracted text) plus handwritten-note photos in one pass. What makes a purpose-built pipeline meaningfully better than a generic "summarize this" prompt:
1. **Information-density constraint as a hard target** (e.g. "~800–1200 words, must fit one page at 9pt in 2–3 columns") forces real compression instead of a padded bullet list.
2. **Topic/subtopic clustering before compression** — first pass: extract a topic outline across all sources (dedupe overlap), second pass: compress within each topic. Avoids "summarize each file separately and concatenate."
3. **Exam-relevance filtering** — prioritize definitions, formulas, named processes/mechanisms, comparison tables, anything repeated/emphasized; drop narrative/context filler.
4. **Layout awareness** — hierarchical headers, tables for compare/contrast, short-hand notation, suited to scanning under time pressure — also exactly what the downstream handwriting renderer needs (discrete short chunks, not paragraphs).
5. **Cross-source synthesis** — merge multiple lecture files on the same topic into one entry rather than repeating near-duplicate content, which single-file tools don't do well.

Sources: notebooklm.google.com, mindgrasp.ai, studyfetch.com, scholarly.so/tools/cheat-sheet-maker, slidespeak.co, cheatish.com, squeezenotes.com, solvely.ai/ai-cheat-sheet-maker, mylens.ai/ai-cheatsheet-creator, quizgecko.com/ai-note-maker, transkribus.org/letters-notes, camnotes.com.

---

## 4. Practical build options for a hobbyist

**Open-source repos (generative, stroke/style-conditioned)**
- **sjvasquez/handwriting-synthesis** — classic Graves 2013 RNN, pretrained checkpoint, runs on CPU, generates *online* (pen-stroke) handwriting with a style index. Actively forked as recently as 2025 (nblasgen/handwriting-synthesis-2025, updated pretrained model + training instructions). Style conditioning is via "priming" with a short stroke sequence in the same alphabet the model trained on (IAM dataset) — mimicking *your* handwriting needs priming tricks (mixed results per GitHub issue #70) or fine-tuning on your own online stroke data. Easiest to run today; weakest at true personalization without real stroke data.
- **ankanbhunia/Handwriting-Transformers (HWT)** — few-shot style transfer from a handful of *offline* (photographed/scanned) word images. Pretrained weights via Google Drive. Outperforms older GANwriting. Modest single consumer GPU plausible; no stroke data needed.
- **koninik/DiffusionPen** — diffusion-based, learns a writer's style from as few as **5 reference samples**, pretrained weights on HuggingFace. Built on Stable Diffusion v1.5 components (VAE/DDIM) — needs a decent GPU (8GB+ VRAM) for inference, more for fine-tuning; doable on a gaming PC or rented cloud GPU for a weekend, not a laptop CPU.
- Awareness list: **koninik/awesome-handwritten-text-generation** for further options (One-DM, DiffInk, ScriptViT, etc.) — mostly 2024–2026 research code, less turnkey.

**"Good enough" glyph-stitching approach**
Demonstrated by Julia Evans (jvns.ca/blog/2020/08/08/handwritten-font) and the PyPI `handwriting-generator` package: segment handwriting into glyphs, build a renderer with **fontTools** (Python) using OpenType contextual substitution — multiple variants per letter swapped by neighboring characters — or a simpler Pillow-based script applying per-glyph seeded random jitter (rotation, baseline wander, scale wobble, spacing). **Calligraphr** is the no-code version: upload a filled template, get a TTF/OTF with basic ligature support, under an hour.
- **Pros:** buildable in a day, no GPU/ML, controllable, cheap to iterate.
- **Cons:** even Evans' own conclusion was "uncanny valley" — contextual substitution alone still looks artificial; true naturalness needs 5–10+ variants per glyph plus randomized selection/jitter (more prep writing each letter many times), but no ML risk. For a cheat sheet (short-lived, mostly-static text), very likely "good enough" — the pragmatic recommendation.

**iPad/Apple Pencil stroke capture — worth it?**
Yes, meaningfully, *if* pursuing the generative-model route. Apple Pencil + PencilKit captures real stroke sequences (x/y every ~4–17ms, plus pressure/tilt/azimuth) — exactly the "online" format Graves-style RNNs and modern diffusion-on-strokes models (DiffInk) train on natively, vs. reconstructing strokes from a static photo (lossy). For glyph-stitching, stroke data isn't needed at all — photographed/scanned glyphs suffice. Skip the Pencil for glyph-stitching; get one only if attempting RNN-based fine-tuning.

**Recommended stack for a weekend/hobby project**
- **Weekend-scale (recommended):** Calligraphr for a first pass (1–2 hrs) → if insufficient, Python + Pillow/fontTools glyph-stitching with 5–10 variants per letter, randomized rotation/scale/baseline/spacing (2–3 days). No GPU, no ML framework. Realistically gets "looks like a person wrote it."
- **Week-scale stretch:** DiffusionPen with HF pretrained weights + 5–20 of your own word-image samples, on a rented GPU (Colab/RunPod) — more natural stroke connectivity/variation, at the cost of PyTorch/Stable-Diffusion environment setup and fine-tuning debugging.
- **Not weekend-scale:** training/fine-tuning an online RNN from scratch on your own captured Pencil stroke data — collecting enough samples and getting priming/style conditioning to work is multi-week, per open issues in that repo.

**Bottom line:** glyph-stitching (Calligraphr → custom fontTools/Pillow script if needed) is the realistic hobbyist path — days not weeks, no GPU, good-enough quality. DiffusionPen is the best "real ML" option for more authentic full-page variation if a GPU is available. Apple Pencil stroke capture only pays off on the RNN/stroke route.

Sources: github.com/sjvasquez/handwriting-synthesis, github.com/nblasgen/handwriting-synthesis-2025, github.com/ankanbhunia/Handwriting-Transformers, github.com/koninik/DiffusionPen, huggingface.co/konnik/DiffusionPen, github.com/koninik/awesome-handwritten-text-generation, calligraphr.com, jvns.ca/blog/2020/08/08/handwritten-font, pypi.org/project/handwriting-generator.

---

## Synthesis / recommendation

**No existing product combines both halves.** That's a genuine gap, not something to overlook in favor of an existing tool.

- **Summarization half:** build with a custom LLM prompt (fast, low-risk, weekend-buildable). Beat existing cheat-sheet tools by enforcing a hard density constraint, cross-source dedup/clustering, exam-relevance filtering, and short-line/structured output.
- **Handwriting half:** start with **glyph-stitching** (Calligraphr as a first pass, custom Pillow/fontTools script with letter variants + jitter if that looks too robotic) as the MVP. Only escalate to DiffusionPen/HWT (real ML, GPU required, week+ effort, uncertain quality on jargon/long text) if the stitched version isn't convincing enough.
- Skip stroke-capture hardware (Apple Pencil/tablet) unless committing to the RNN/stroke-based ML route.
