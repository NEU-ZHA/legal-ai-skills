#!/usr/bin/env python3
"""Wrapper for the legal-homework-formatter DOCX compatibility checker."""

from pathlib import Path
import runpy

HERE = Path(__file__).resolve()
CANDIDATES = [
    HERE.parents[2] / "legal-homework-formatter/scripts/docx_compat_check.py",
    Path.home() / ".codex/skills/legal-homework-formatter/scripts/docx_compat_check.py",
    Path.home() / ".agents/skills/legal-homework-formatter/scripts/docx_compat_check.py",
]

for checker in CANDIDATES:
    if checker.exists():
        runpy.run_path(str(checker), run_name="__main__")
        break
else:
    raise FileNotFoundError("Cannot locate legal-homework-formatter/scripts/docx_compat_check.py")
