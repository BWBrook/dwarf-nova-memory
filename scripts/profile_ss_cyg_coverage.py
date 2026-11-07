#!/usr/bin/env python3
"""Profile hashed SS Cyg native acquisitions without event or effect inference."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.coverage import combine_acquisitions, profile


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("native_xml", type=Path, nargs="+")
    args = parser.parse_args()
    results = []
    for path in args.native_xml:
        receipt = json.loads((path.parent / "receipt.json").read_text())
        query = parse_qs(urlparse(receipt["source_url"]).query)
        rows, _ = combine_acquisitions([path])
        results.append({"acquisition": path.parent.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "start_jd": float(query["fromjd"][0]), "end_jd": float(query["tojd"][0]),
                        **profile(rows, float(query["fromjd"][0]), float(query["tojd"][0]))})
    combined, repeated = combine_acquisitions(args.native_xml)
    print(json.dumps({"acquisitions": results, "combined_unique_observations": len(combined),
                      "repeated_identical_observations_across_acquisitions": repeated}, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
