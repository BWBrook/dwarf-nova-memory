"""Bounded native VStar/AID acquisition checks; no time conversion or event fit."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse
import xml.etree.ElementTree as ET


AUID = "000-BCP-220"
TUNING_CUTOFF_JD = 2436934.5
VSTAR_COMMIT = "6797f17fe106097fd84c1822a24d51021aea9fdd"


def check_window(start_jd: float, end_jd: float) -> None:
    if not all(math.isfinite(value) for value in (start_jd, end_jd)) or not 0 < start_jd < end_jd < TUNING_CUTOFF_JD:
        raise ValueError("require finite positive start < end strictly before the D013 cutoff")


def ss_cyg_request_url(start_jd: float, end_jd: float) -> str:
    check_window(start_jd, end_jd)
    parameters = {"view": "api.object", "ident": AUID, "data": "50000",
                  "fromjd": start_jd, "tojd": end_jd, "csv": "", "mtype": "std", "page": "1"}
    return "https://vsx.aavso.org/index.php?" + urlencode(parameters)


def read_native_payload(path: str | Path, *, start_jd: float, end_jd: float) -> tuple[list[dict[str, str]], dict]:
    check_window(start_jd, end_jd)
    path = Path(path)
    if "quarantine" in path.absolute().parts or "quarantine" in path.resolve().parts:
        raise ValueError("reserved path cannot enter development")
    root = ET.parse(path).getroot()
    if root.findtext("Name") != "SS Cyg" or root.findtext("AUID") != AUID:
        raise ValueError("unexpected archive target identity")
    data = root.find("Data")
    count = root.findtext(".//Count")
    if data is None or not data.text or not data.text.strip():
        if count == "0":
            return [], {"rows": 0, "bands": {}, "native_validation_flags": {}, "limiting_rows": 0,
                        "status": "provider explicitly returned zero rows in the requested window"}
        raise ValueError("no native CSV payload; response may be an error or metadata only")
    reader = csv.DictReader(io.StringIO(data.text.strip()))
    required = {"obsID", "JD", "mag", "uncert", "fainterThan", "band", "by", "val"}
    if not required <= set(reader.fieldnames or []):
        raise ValueError("native CSV schema differs from the pinned VStar contract")
    if len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise ValueError("duplicate native CSV columns")
    rows = list(reader)
    if not rows or len(rows) >= 50000:
        raise ValueError("empty or potentially truncated bounded export")
    seen = set()
    for row in rows:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("malformed native CSV row")
        jd = float(row["JD"])
        if not math.isfinite(jd) or not start_jd <= jd <= end_jd or jd >= TUNING_CUTOFF_JD:
            raise ValueError("out-of-window row rejected; do not summarize this payload")
        if not row["obsID"] or row["obsID"] in seen:
            raise ValueError("missing or duplicate native observation identity")
        seen.add(row["obsID"])
        if not math.isfinite(float(row["mag"])) or row["fainterThan"] not in ("0", "1"):
            raise ValueError("unresolved magnitude or limiting-measurement representation")
        if row["uncert"] and (not math.isfinite(float(row["uncert"])) or float(row["uncert"]) < 0):
            raise ValueError("invalid native uncertainty")
        if not row["band"] or not row["by"]:
            raise ValueError("missing native band or observer code")
    if count is not None and int(count) != len(rows):
        raise ValueError("response count differs from rows; pagination/completeness unresolved")
    bands = sorted({row["band"] for row in rows})
    summary = {"rows": len(rows), "native_columns": reader.fieldnames,
               "requested_start_jd": start_jd, "requested_end_jd": end_jd,
               "bands": {band: sum(row["band"] == band for row in rows) for band in bands},
               "limiting_rows": sum(row["fainterThan"] == "1" for row in rows),
               "positive_reported_uncertainties": sum(bool(row["uncert"]) and float(row["uncert"]) > 0 for row in rows),
               "native_validation_flags": {flag: sum(row["val"] == flag for row in rows)
                                           for flag in sorted({row["val"] for row in rows})},
               "min_native_jd": min(float(row["JD"]) for row in rows),
               "max_native_jd": max(float(row["JD"]) for row in rows),
               "time_format": "JD", "time_scale": "unresolved", "time_reference": "unresolved",
               "status": "native development rows only; not normalized analysis data"}
    return rows, summary


def read_acquisition(path: str | Path) -> tuple[list[dict[str, str]], dict]:
    path = Path(path)
    if "quarantine" in path.absolute().parts or "quarantine" in path.resolve().parts:
        raise ValueError("reserved path cannot enter development")
    receipt = json.loads((path.parent / "receipt.json").read_text(encoding="utf-8"))
    if hashlib.sha256(path.read_bytes()).hexdigest() != receipt["sha256"]:
        raise ValueError("native acquisition hash differs from receipt")
    url = urlparse(receipt["source_url"])
    query = parse_qs(url.query, keep_blank_values=True)
    if (url.scheme != "https" or url.netloc != "vsx.aavso.org" or url.path != "/index.php"
            or query.get("view") != ["api.object"] or query.get("ident") != [AUID]):
        raise ValueError("unrecognized native request provenance")
    if len(query.get("fromjd", [])) != 1 or len(query.get("tojd", [])) != 1:
        raise ValueError("missing or ambiguous acquisition window")
    return read_native_payload(path, start_jd=float(query["fromjd"][0]), end_jd=float(query["tojd"][0]))
