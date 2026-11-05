#!/usr/bin/env python3
"""Run without installing the package: python scripts/run_demo.py --output outputs/demo."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dnmem.cli import main

if __name__ == "__main__":
    main(["demo", *sys.argv[1:]])
