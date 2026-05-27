#!/usr/bin/env python3
"""Call the comprehensive citation diagnostic script from this automator skill."""

from __future__ import annotations

import runpy
from pathlib import Path


HERE = Path(__file__).resolve()
CANDIDATES = [
    HERE.parents[2] / "legal-citation-comprehensive/scripts/citation_diagnose.py",
    Path.home() / ".codex/skills/legal-citation-comprehensive/scripts/citation_diagnose.py",
    Path.home() / ".agents/skills/legal-citation-comprehensive/scripts/citation_diagnose.py",
]

for script in CANDIDATES:
    if script.exists():
        runpy.run_path(str(script), run_name="__main__")
        break
else:
    raise FileNotFoundError("Cannot locate legal-citation-comprehensive/scripts/citation_diagnose.py")
