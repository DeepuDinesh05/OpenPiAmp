#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

python3 -m venv .venv
source .venv/bin/activate

sudo apt update
sudo apt install -y python3-dev build-essential
pip install evdev

pip install pygame mutagen

echo "Virtual environment ready. Activate it later with: source .venv/bin/activate"
