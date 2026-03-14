#!/bin/bash
# Nova Technologies — Watermark Remover
# Usage: ./start.sh
# Set your Replicate API key before running:
#   export REPLICATE_API_TOKEN=your_key_here

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Create uploads dir if missing
mkdir -p uploads

# Initialize DB and start with gunicorn (production)
echo "Starting Watermark Remover on http://0.0.0.0:5000"
python -c "from app import init_db; init_db()"
gunicorn app:app --bind 0.0.0.0:5000 --workers 2 --timeout 120

# For development instead, use:
# python app.py
