"""
Runnable entry point for Chapter 1.

Requires a Gemini API key (free tier: https://aistudio.google.com/apikey).
Export it before running:

    export GEMINI_API_KEY=your-key-here
    uv run scripts/run_demo.py

Without a key, Demos 1 and 3 (pure data-layer demos) still run. Demo 2's
two LLM calls are skipped with a clear message, since they require a
live model.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.workflow import run_all

if __name__ == "__main__":
    run_all()
