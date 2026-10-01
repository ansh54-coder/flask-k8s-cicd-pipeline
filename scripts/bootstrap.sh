#!/usr/bin/env bash

set -euo pipefail

echo "Bootstrapping ShopAPI..."

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

python -m venv .venv

source .venv/bin/activate

pip install --upgrade pip

pip install -r requirements.txt
pip install -r requirements-dev.txt

flask --app app.main db upgrade

echo "Bootstrap complete."
