#!/usr/bin/env python3
"""Publish dashboard/out into the GitHub Pages repository root."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dashboard" / "out"

if not (OUT / "index.html").is_file():
    raise SystemExit("dashboard/out/index.html is missing; run the dashboard build first")

assets = ROOT / "_next"
if assets.exists():
    shutil.rmtree(assets)

for source in OUT.iterdir():
    target = ROOT / source.name
    if source.is_dir():
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)
    else:
        shutil.copy2(source, target)

(ROOT / ".nojekyll").touch()
print("Published dashboard/out to repository root")
