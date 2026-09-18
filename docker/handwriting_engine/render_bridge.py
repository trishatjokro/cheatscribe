"""Original cheatscribe code — NOT part of sjvasquez/handwriting-synthesis.

Runs inside the Docker image built from ./Dockerfile, which clones that
project fresh at build time into /engine. This script just imports its public
`Hand` class (the same API documented in that project's README) and drives it
from a JSON request instead of a hardcoded lyrics demo.

Usage (inside the container): python render_bridge.py <request.json> <out_dir>
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, "/engine")
from demo import Hand  # noqa: E402  (sjvasquez/handwriting-synthesis's public API)


def main(request_path: str, out_dir: str) -> None:
    request = json.loads(Path(request_path).read_text())
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    hand = Hand()
    for line in request["lines"]:
        hand.write(
            filename=str(out / f"{line['id']}.svg"),
            lines=[line["text"]],
            biases=[line.get("bias", 0.75)],
            styles=[line.get("style", 7)],
        )


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
