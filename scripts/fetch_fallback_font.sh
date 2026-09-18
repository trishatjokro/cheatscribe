#!/usr/bin/env bash
# Downloads the Caveat handwriting font (SIL Open Font License) from Google
# Fonts for use by the zero-setup fallback renderer. Not bundled in the repo
# since it's a binary asset with its own license file — fetched on demand.
set -euo pipefail

DEST_DIR="$(dirname "$0")/../src/cheatscribe/render/assets"
mkdir -p "$DEST_DIR"

curl -L -o "$DEST_DIR/Caveat-Regular.ttf" \
  "https://github.com/google/fonts/raw/main/ofl/caveat/Caveat%5Bwght%5D.ttf"

echo "Saved to $DEST_DIR/Caveat-Regular.ttf"
