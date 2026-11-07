#!/usr/bin/env python3
"""Acquire only the D013-open 1956-01-01 to 1959-01-01 SS Cyg interval."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.aavso import VSTAR_COMMIT, read_native_payload, ss_cyg_request_url


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="new empty raw acquisition directory")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if any(args.output.iterdir()):
        raise ValueError("refusing to overwrite an acquisition")
    url = ss_cyg_request_url()
    request = Request(url, headers={"User-Agent": "dwarf-nova-memory/0.1 bounded research acquisition"})
    with urlopen(request, timeout=30) as response:
        payload = response.read()
        headers = dict(response.headers)
        final_url = response.url
    native = args.output / "native.xml"
    native.write_bytes(payload)
    receipt = {"source_url": url, "final_url": final_url,
               "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
               "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload),
               "response_headers": {key: value for key, value in headers.items()
                                    if key.casefold() in {"content-type", "last-modified", "etag"}},
               "vstar_source_commit": VSTAR_COMMIT, "python": platform.python_version(),
               "source_code_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                                      for name in ("scripts/acquire_ss_cyg.py", "src/dnmem/aavso.py")},
               "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
               "code_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
               "status": "retained native bytes; validation pending"}
    receipt_path = args.output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    _, summary = read_native_payload(native)
    receipt.update(summary)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
