#!/usr/bin/env python3
"""Reproduce a synthetic witness of retrospective confirmation replacement."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.extract_x3 import x3_fitted_episodes
from dnmem.x3_validation_score import audit_final_confirmation_prefix, causal_confirmation_emissions


def witness():
    base = 2451544.5
    rows = [{"JD": str(base + day + offset), "mag": str(magnitude), "obsID": f"{day}-{observer}",
             "obsName": observer, "by": observer, "fainterThan": "0", "val": "V", "band": "Vis."}
            for day, magnitude in ((100, 9), (101, 9), (102, 9), (103, 9), (104, 11),
                                   (105, 9), (106, 9), (107, 9), (108, 11))
            for offset, observer in ((.6, "a"), (.7, "b"))]
    episodes = x3_fitted_episodes(rows)
    return {"data_kind": "synthetic adversarial control", "base_jd": base,
            "candidate_sha256": hashlib.sha256((ROOT / "src/dnmem/extract_x3.py").read_bytes()).hexdigest(),
            "batch_confirmed": episodes[0]["confirmed"],
            "prefix_audit": audit_final_confirmation_prefix(rows, episodes),
            "immutable_causal_emissions": causal_confirmation_emissions(rows)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(witness(), indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(result)
    else:
        print(result, end="")
