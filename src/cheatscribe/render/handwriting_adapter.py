"""Bridge to the real handwriting-synthesis engine (Graves RNN, the model
behind calligrapher.ai), run via the Docker image in docker/handwriting_engine/
so its 2018-era TensorFlow 1.x requirement never touches your main Python
environment.

The engine's source is never vendored into this repo — the Dockerfile clones
it fresh from github.com/sjvasquez/handwriting-synthesis at image build time.
See README.md § Credits.

Contract with docker/handwriting_engine/render_bridge.py:
  in:  JSON file {"lines": [{"id": int, "text": str, "style": int, "bias": float}]}
  out: one SVG per line at <out_dir>/<id>.svg
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from ..layout import LinePlacement
from .compose import compose_page

DOCKER_IMAGE = "cheatscribe-handwriting-engine"


def engine_available() -> bool:
    try:
        result = subprocess.run(
            ["docker", "image", "inspect", DOCKER_IMAGE],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def render_with_engine(
    placements: list[LinePlacement],
    page_width: int,
    page_height: int,
    out_path: str,
    style: int = 7,
    bias: float = 0.75,
) -> None:
    if not engine_available():
        raise RuntimeError(
            "Docker image "
            f"'{DOCKER_IMAGE}' not found. Build it with: "
            "docker build -t cheatscribe-handwriting-engine docker/handwriting_engine "
            "(see README.md § Real handwriting rendering)."
        )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        request = {
            "lines": [
                {"id": i, "text": p.text, "style": style, "bias": bias}
                for i, p in enumerate(placements)
            ]
        }
        request_path = tmp_path / "request.json"
        request_path.write_text(json.dumps(request))

        out_dir = tmp_path / "out"
        out_dir.mkdir()

        subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{tmp_path}:/data",
                DOCKER_IMAGE,
                "/data/request.json",
                "/data/out",
            ],
            check=True,
        )

        line_svg_paths = {i: str(out_dir / f"{i}.svg") for i in range(len(placements))}
        compose_page(placements, line_svg_paths, page_width, page_height, out_path)
