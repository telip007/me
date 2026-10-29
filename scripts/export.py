#!/usr/bin/env python3
"""Build a static compatibility copy; production runtime is blog.main:app."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from blog.export import export_site

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--root", type=Path, default=Path.cwd())
args = parser.parse_args()
export_site(args.root / "src", args.root / "dist")
print(f"Exported {args.root / 'dist'}")
