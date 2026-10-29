#!/usr/bin/env python3
"""Validate publication metadata and the full route/translation graph."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from blog.content import load_content

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source", type=Path, default=Path.cwd() / "src")
args = parser.parse_args()
store = load_content(args.source)
print(f"Validated {len(store.posts)} public posts and {len(store.routes)} routes")
