"""Validate a deliberately narrow, explicit normalized photometry CSV schema.

This checks representation only, not astronomical correctness, calibration,
catalogue identity or the validity of a time conversion. Raw archives remain
immutable and preserve additional native columns outside this minimal schema.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path


REQUIRED = ("source_row_id", "target_id", "time_value", "time_format", "time_scale", "time_reference",
            "band", "magnitude", "magnitude_error", "is_upper_limit", "limit_magnitude",
            "observer_id", "quality_flag", "provenance_id")


def _number(value: str, column: str, row: int) -> float:
    try:
        n = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"row {row}: {column} must be numeric") from exc
    if not math.isfinite(n):
        raise ValueError(f"row {row}: {column} must be finite")
    return n


def validate_photometry(path: str | Path) -> dict:
    path = Path(path)
    seen: set[tuple[str, str]] = set()
    targets, conventions = set(), set()
    n, limits = 0, 0
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = set(REQUIRED) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing columns: {', '.join(sorted(missing))}")
        for row_number, row in enumerate(reader, start=2):
            n += 1
            for key in ("source_row_id", "target_id", "time_format", "time_scale", "time_reference", "band", "observer_id", "quality_flag", "provenance_id"):
                if not row[key] or not row[key].strip():
                    raise ValueError(f"row {row_number}: {key} is required; use explicit unknown where appropriate")
            if any(row[k].strip().casefold() == "unknown" for k in ("time_scale", "time_format", "time_reference")):
                raise ValueError(f"row {row_number}: unresolved time convention cannot enter normalized analysis data")
            _number(row["time_value"], "time_value", row_number)
            key = (row["provenance_id"], row["source_row_id"])
            if key in seen:
                raise ValueError(f"row {row_number}: duplicate source row within provenance")
            seen.add(key)
            limit = row["is_upper_limit"].strip().casefold()
            if limit not in ("true", "false"):
                raise ValueError(f"row {row_number}: is_upper_limit must be true or false")
            if limit == "true":
                limits += 1
                _number(row["limit_magnitude"], "limit_magnitude", row_number)
                if row["magnitude"] or row["magnitude_error"]:
                    raise ValueError(f"row {row_number}: a limit is not an exact magnitude measurement")
            else:
                _number(row["magnitude"], "magnitude", row_number)
                if row["magnitude_error"]:
                    if _number(row["magnitude_error"], "magnitude_error", row_number) <= 0:
                        raise ValueError(f"row {row_number}: reported error must be positive")
                if row["limit_magnitude"]:
                    raise ValueError(f"row {row_number}: exact detection must not carry limit_magnitude")
            targets.add(row["target_id"])
            conventions.add((row["time_format"], row["time_scale"], row["time_reference"]))
    if not n:
        raise ValueError("photometry table is empty")
    return {"rows": n, "limits": limits, "targets": sorted(targets),
            "time_conventions": sorted(conventions),
            "status": "schema valid; scientific provenance not checked"}
