"""
Runnable entry point for Chapter 1. From the repo root:

    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python scripts/run_demo.py

Expected output is documented in README.md under "Expected Output."
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.workflow import run_all

if __name__ == "__main__":
    run_all()
