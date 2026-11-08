"""Bounded, provenance-preserving native adapter for the A10f evaluation.

The adapter validates the pinned VSX native XML/CSV shape without normalising
the provider's values.  Raw response bytes and receipt files are managed by
the acquisition runner; this module only reads them.
"""

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
TARGET_NAME = "SS Cyg"
EVALUATION_START_JD = 2436934.0
EVALUATION_CUTOFF_JD = 2458119.5
ROW_CAP = 50_000
MAX_WINDOW_DAYS = 366.0
VSTAR_URL = "https://vsx.aavso.org/index.php"

_REQUIRED_COLUMNS = {
    "obsID",
    "JD",
    "mag",
    "uncert",
    "fainterThan",
    "band",
    "by",
    "val",
}
_MISSING_UNCERTAINTY = {"", "None"}


class RowCapError(ValueError):
    """The provider returned the native row cap and may have truncated rows."""


def _reject_quarantine(path: Path) -> None:
    absolute = path.absolute()
    resolved = path.resolve()
    if "quarantine" in absolute.parts or "quarantine" in resolved.parts:
        raise ValueError("reserved quarantine path cannot enter evaluation")


def _check_window(start_jd: float, end_jd: float) -> None:
    if (
        not all(math.isfinite(value) for value in (start_jd, end_jd))
        or start_jd < EVALUATION_START_JD
        or not start_jd < end_jd
        or end_jd >= EVALUATION_CUTOFF_JD
    ):
        raise ValueError(
            "require finite evaluation start <= start < end strictly before the cutoff"
        )


def request_url(start_jd: float, end_jd: float) -> str:
    """Return the pinned inclusive-endpoint VSX native request URL."""

    _check_window(start_jd, end_jd)
    parameters = {
        "view": "api.object",
        "ident": AUID,
        "data": "50000",
        "fromjd": start_jd,
        "tojd": end_jd,
        "csv": "",
        "mtype": "std",
        "page": "1",
    }
    return VSTAR_URL + "?" + urlencode(parameters)


def request_windows(start_jd: float, stop_jd: float) -> list[tuple[float, float]]:
    """Make inclusive-endpoint requests covering ``[start_jd, stop_jd)``.

    Adjacent requests intentionally share their endpoint.  The final endpoint
    is the greatest representable value below the exclusive evaluation cutoff.
    ``combine_native`` removes the resulting repeated observations by obsID.
    """

    if (
        not all(math.isfinite(value) for value in (start_jd, stop_jd))
        or start_jd < EVALUATION_START_JD
        or not start_jd < stop_jd
        or stop_jd > EVALUATION_CUTOFF_JD
    ):
        raise ValueError("require finite start < stop within the evaluation interval")
    final_stop = math.nextafter(stop_jd, -math.inf) if stop_jd == EVALUATION_CUTOFF_JD else stop_jd
    if not start_jd < final_stop:
        raise ValueError("evaluation interval has no representable inclusive endpoint")

    windows: list[tuple[float, float]] = []
    cursor = start_jd
    while cursor < final_stop:
        end = min(cursor + MAX_WINDOW_DAYS, final_stop)
        # A finite precision guard protects the loop if an unusual float is
        # supplied near the endpoint.
        if not cursor < end or end - cursor > MAX_WINDOW_DAYS:
            raise ValueError("could not construct a bounded request window")
        windows.append((cursor, end))
        cursor = end
    return windows


def _xml_element(element: ET.Element) -> dict:
    """Serialize XML metadata without collapsing repeated or unknown tags."""

    return {
        "tag": element.tag,
        "attributes": dict(element.attrib),
        "text": element.text,
        "children": [_xml_element(child) for child in element],
    }


def _metadata(root: ET.Element, *, columns: list[str] | None, count: int | None) -> dict:
    # Data contains the CSV payload itself and is represented by ``rows`` and
    # ``native_columns``.  Every other XML child remains available verbatim as
    # structured metadata, including provider tags unknown to this adapter.
    return {
        "target_name": root.findtext("Name"),
        "auid": root.findtext("AUID"),
        "xml_root_attributes": dict(root.attrib),
        "provider_count": count,
        "native_columns": list(columns or []),
        "extra_native_columns": [column for column in (columns or []) if column not in _REQUIRED_COLUMNS],
        "xml_metadata": [_xml_element(child) for child in root if child.tag != "Data"],
        "data_attributes": dict(root.find("Data").attrib) if root.find("Data") is not None else {},
        "time_format": "JD",
        "time_scale": "unresolved",
        "time_reference": "unresolved",
    }


def parse_native_bytes(
    payload: bytes, *, start_jd: float, end_jd: float
) -> tuple[list[dict[str, str]], dict]:
    """Parse one pinned native response while preserving provider strings.

    ``start_jd`` and ``end_jd`` describe the inclusive provider request.  JD
    is converted only transiently for finite/bounds checks; the returned value
    is the original string, with no time-scale or convention conversion.
    """

    _check_window(start_jd, end_jd)
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise ValueError("malformed native XML") from exc
    if root.findtext("Name") != TARGET_NAME or root.findtext("AUID") != AUID:
        raise ValueError("unexpected archive target identity")

    count_text = root.findtext(".//Count")
    try:
        count = int(count_text) if count_text is not None else None
    except (TypeError, ValueError) as exc:
        raise ValueError("native response Count is not an integer") from exc
    if count is not None and count < 0:
        raise ValueError("native response Count is negative")

    data = root.find("Data")
    csv_text = data.text if data is not None else None
    if not csv_text or not csv_text.strip():
        if count == 0:
            metadata = _metadata(root, columns=None, count=count)
            metadata.update({"rows": 0, "status": "provider explicitly returned zero rows"})
            return [], metadata
        raise ValueError("no native CSV payload; response may be an error or metadata only")

    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    columns = reader.fieldnames or []
    if not _REQUIRED_COLUMNS <= set(columns):
        raise ValueError("native CSV schema differs from the pinned VStar contract")
    if len(columns) != len(set(columns)) or any(column is None or not column for column in columns):
        raise ValueError("duplicate or empty native CSV columns")

    rows = list(reader)
    if not rows:
        if count == 0:
            metadata = _metadata(root, columns=columns, count=count)
            metadata.update(
                {
                    "rows": 0,
                    "requested_start_jd": start_jd,
                    "requested_end_jd": end_jd,
                    "status": "provider explicitly returned zero rows",
                }
            )
            return [], metadata
        raise ValueError("native CSV payload has no rows")
    if len(rows) >= ROW_CAP:
        raise RowCapError("native response reached the row cap; probable truncation")
    if count is not None and count != len(rows):
        raise ValueError("response Count differs from native CSV rows")

    seen: set[str] = set()
    for row in rows:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("malformed native CSV row")
        obs_id = row["obsID"]
        if not obs_id or obs_id in seen:
            raise ValueError("missing or duplicate native observation identity")
        seen.add(obs_id)
        try:
            jd = float(row["JD"])
        except (TypeError, ValueError) as exc:
            raise ValueError("nonfinite native JD") from exc
        if not math.isfinite(jd) or not start_jd <= jd <= end_jd or jd >= EVALUATION_CUTOFF_JD:
            raise ValueError("out-of-window or post-cutoff row rejected")
        try:
            magnitude = float(row["mag"])
        except (TypeError, ValueError) as exc:
            raise ValueError("nonfinite native magnitude") from exc
        if not math.isfinite(magnitude) or row["fainterThan"] not in {"0", "1"}:
            raise ValueError("unresolved magnitude or limiting-measurement representation")
        if row["uncert"] not in _MISSING_UNCERTAINTY:
            try:
                uncertainty = float(row["uncert"])
            except (TypeError, ValueError) as exc:
                raise ValueError("invalid native uncertainty") from exc
            if not math.isfinite(uncertainty) or uncertainty < 0:
                raise ValueError("invalid native uncertainty")
        if not row["band"] or not row["by"]:
            raise ValueError("missing native band or observer code")

    metadata = _metadata(root, columns=columns, count=count)
    metadata.update(
        {
            "rows": len(rows),
            "bands": {band: sum(row["band"] == band for row in rows) for band in sorted({row["band"] for row in rows})},
            "validation_flags": {flag: sum(row["val"] == flag for row in rows) for flag in sorted({row["val"] for row in rows})},
            "limiting_rows": sum(row["fainterThan"] == "1" for row in rows),
            "requested_start_jd": start_jd,
            "requested_end_jd": end_jd,
            "min_native_jd": min(float(row["JD"]) for row in rows),
            "max_native_jd": max(float(row["JD"]) for row in rows),
            "status": "native rows retained; analysis eligibility is explicit and separate",
        }
    )
    return rows, metadata


def row_is_analysis_eligible(row: dict[str, str]) -> bool:
    """Return whether a retained native row enters the frozen extraction."""

    return row.get("band") == "Vis." and row.get("val") == "V"


def select_analysis_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Select visual, ``V``-validated rows without changing their fields."""

    return [row for row in rows if row_is_analysis_eligible(row)]


def _receipt_window(receipt: dict, path: Path) -> tuple[float, float]:
    source_url = receipt.get("source_url")
    if not isinstance(source_url, str):
        raise ValueError(f"missing source_url in receipt for {path}")
    parsed = urlparse(source_url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    required = {
        "view": ["api.object"],
        "ident": [AUID],
        "data": ["50000"],
        "csv": [""],
        "mtype": ["std"],
        "page": ["1"],
    }
    if parsed.scheme != "https" or parsed.netloc != "vsx.aavso.org" or parsed.path != "/index.php":
        raise ValueError(f"unrecognized native request provenance for {path}")
    if any(query.get(key) != value for key, value in required.items()):
        raise ValueError(f"unrecognized native request query for {path}")
    if len(query.get("fromjd", [])) != 1 or len(query.get("tojd", [])) != 1:
        raise ValueError(f"missing or ambiguous acquisition window for {path}")
    try:
        start_jd, end_jd = float(query["fromjd"][0]), float(query["tojd"][0])
    except ValueError as exc:
        raise ValueError(f"invalid acquisition window for {path}") from exc
    _check_window(start_jd, end_jd)
    return start_jd, end_jd


def combine_native(acquisition_paths: list[str | Path]) -> tuple[list[dict[str, str]], dict]:
    """Verify receipts, then parse and merge native acquisitions by obsID."""

    combined: dict[str, dict[str, str]] = {}
    acquisitions: list[dict] = []
    duplicate_rows_removed = 0
    for raw_path in acquisition_paths:
        path = Path(raw_path)
        _reject_quarantine(path)
        payload = path.read_bytes()
        try:
            receipt = json.loads((path.parent / "receipt.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid receipt for {path}") from exc
        expected_hash = receipt.get("sha256")
        actual_hash = hashlib.sha256(payload).hexdigest()
        if expected_hash != actual_hash:
            raise ValueError(f"native acquisition hash differs from receipt for {path}")
        start_jd, end_jd = _receipt_window(receipt, path)
        rows, metadata = parse_native_bytes(payload, start_jd=start_jd, end_jd=end_jd)
        for row in rows:
            obs_id = row["obsID"]
            if obs_id in combined:
                if combined[obs_id] != row:
                    raise ValueError(f"conflicting native rows share obsID {obs_id}")
                duplicate_rows_removed += 1
            else:
                combined[obs_id] = row
        acquisitions.append(
            {
                "path": str(path),
                "sha256": actual_hash,
                "source_url": receipt["source_url"],
                "requested_start_jd": start_jd,
                "requested_end_jd": end_jd,
                "native_rows": len(rows),
            }
        )

    rows = list(combined.values())
    return rows, {
        "acquisitions": acquisitions,
        "native_rows": len(rows),
        "duplicate_rows_removed": duplicate_rows_removed,
        "analysis_rows": len(select_analysis_rows(rows)),
        "status": "native rows combined after receipt verification; no JD conversion",
    }

