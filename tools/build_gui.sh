#!/bin/zsh
# Build the standalone GUI patcher app with PyInstaller.
# Output: tools/dist/MarioSportsMix-Patcher.app (macOS) or dist/MarioSportsMix-Patcher/ (other OSes).
# `wit` is not bundled here -- put it on PATH, or use the CI workflow, which bundles it.
set -eu
cd "${0:a:h}"
command -v pyinstaller >/dev/null || { echo "pyinstaller not found (pip install pyinstaller tkinterdnd2)"; exit 1; }
pyinstaller --noconfirm MarioSportsMix-Patcher.spec
echo "built: tools/dist/MarioSportsMix-Patcher"
