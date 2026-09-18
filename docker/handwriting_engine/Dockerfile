# Builds an isolated environment for sjvasquez/handwriting-synthesis (the
# model behind calligrapher.ai — Graves 2013 handwriting synthesis RNN).
#
# That project has no published LICENSE, so cheatscribe does not vendor or
# redistribute its source: this Dockerfile clones it fresh at build time,
# straight from upstream, the same as any local checkout would. Only
# render_bridge.py (cheatscribe's own code) is copied in.
#
# Its pinned tensorflow==1.6.0 needs an old Python; the container isolates
# that from your normal environment.
FROM python:3.6-slim

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/sjvasquez/handwriting-synthesis.git /engine
WORKDIR /engine
RUN pip install --no-cache-dir -r requirements.txt

COPY render_bridge.py /engine/render_bridge.py

ENTRYPOINT ["python", "render_bridge.py"]
