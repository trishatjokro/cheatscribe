"""Local Flask app: drag files in, get a handwritten cheat sheet out.

Runs on your machine only — uploads go to a temp dir, the generated sheet
lands in out/web/. Nothing is sent anywhere except the summarization call to
the Anthropic API.
"""

from __future__ import annotations

import os
import tempfile
import traceback
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from ..ingest import IMAGE_EXTENSIONS, PDF_EXTENSIONS, PPTX_EXTENSIONS, TEXT_EXTENSIONS, load_documents
from ..layout import PAGE_HEIGHT, PAGE_WIDTH, layout_cheat_sheet
from ..render import engine_available, render_page
from ..summarize import cheat_sheet_to_dict, summarize

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO_ROOT / "out" / "web"
ALLOWED_EXTENSIONS = TEXT_EXTENSIONS | PPTX_EXTENSIONS | PDF_EXTENSIONS | IMAGE_EXTENSIONS

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB of notes is plenty
app.config["TEMPLATES_AUTO_RELOAD"] = True  # edit index.html and just refresh, even with debug=False


@app.route("/")
def index():
    return render_template(
        "index.html",
        accepted=sorted(ALLOWED_EXTENSIONS),
        has_api_key=bool(os.environ.get("ANTHROPIC_API_KEY")),
        engine_ready=engine_available(),
    )


@app.route("/generate", methods=["POST"])
def generate():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return jsonify(error="ANTHROPIC_API_KEY is not set — see the setup note at the top of the page."), 400

    uploads = request.files.getlist("files")
    if not uploads:
        return jsonify(error="No files received."), 400

    topic = (request.form.get("topic") or "").strip() or None
    columns = int(request.form.get("columns", 3))
    target_words = int(request.form.get("target_words", 1000))
    backend = request.form.get("backend", "auto")

    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for upload in uploads:
            name = secure_filename(upload.filename or "")
            if not name or Path(name).suffix.lower() not in ALLOWED_EXTENSIONS:
                return jsonify(error=f"Unsupported file: {upload.filename}"), 400
            dest = Path(tmp) / name
            upload.save(dest)
            paths.append(dest)

        try:
            documents = load_documents(paths)
            sheet = summarize(documents, target_words=target_words, topic_hint=topic)
            placements = layout_cheat_sheet(sheet, columns=columns)

            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            stem = f"cheatsheet-{uuid.uuid4().hex[:8]}"
            out_path = OUTPUT_DIR / f"{stem}.png"
            used = render_page(placements, PAGE_WIDTH, PAGE_HEIGHT, str(out_path), backend=backend)
        except Exception as exc:  # surface the real reason in the UI, not a blank 500
            traceback.print_exc()
            return jsonify(error=f"{type(exc).__name__}: {exc}"), 500

    produced = out_path if out_path.exists() else out_path.with_suffix(".svg")
    return jsonify(
        title=sheet.title,
        backend=used,
        sections=len(sheet.sections),
        lines=len(placements),
        image_url=f"/output/{produced.name}",
        summary=cheat_sheet_to_dict(sheet),
    )


@app.route("/output/<path:filename>")
def output(filename: str):
    return send_from_directory(OUTPUT_DIR, filename)


def main() -> None:
    port = int(os.environ.get("CHEATSCRIBE_PORT", 5001))
    print(f"\n  cheatscribe running at http://127.0.0.1:{port}\n  (press Ctrl+C to stop)\n")
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
