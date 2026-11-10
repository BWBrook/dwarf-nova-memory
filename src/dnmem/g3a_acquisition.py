"""Date-limited native transport for the ten approved G3a development targets."""

import csv
from datetime import date
import io
import math
import re
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

STOP = 2447892.5
END = math.nextafter(STOP, -math.inf)
TARGETS = ("SS Aur", "RU Peg", "AR And", "X Leo", "TW Vir", "UU Aql", "CH UMa", "DX And", "U Gem", "IP Peg")
ROW_CAP = 50000
URL = "https://vsx.aavso.org/index.php"
REQUIRED = {"obsID", "JD", "mag", "uncert", "fainterThan", "band", "by", "val"}


class UncertainCap(ValueError):
    pass


class ScopeViolation(ValueError):
    pass


def check_window(start, end):
    if not all(math.isfinite(v) for v in (start, end)) or not 0 < start < end < STOP:
        raise ValueError("G3a requires positive inclusive endpoints strictly before 1990")


def request_windows():
    edges = [1.] + [date(y, 1, 1).toordinal() + 1721424.5 for y in range(1900, 1990, 10)] + [END]
    return list(zip(edges, edges[1:]))


def request_url(name, start, end, *, auid=None, page=1, metadata=False):
    check_window(start, end)
    if name not in TARGETS or type(page) is not int or not 1 <= page <= 100:
        raise ValueError("unapproved target or pagination")
    if auid is not None and not re.fullmatch(r"\d{3}-[A-Z]{3}-\d{3}", auid):
        raise ValueError("invalid resolved AUID")
    parameters = {"view": "api.object", "ident": auid or name,
                  "data": "0" if metadata else str(ROW_CAP), "fromjd": start, "tojd": end}
    if not metadata:
        parameters.update(csv="", mtype="std", page=page)
    return URL + "?" + urlencode(parameters)


def identity(payload, name, auid=None):
    if name not in TARGETS:
        raise ValueError("unapproved target")
    root = ET.fromstring(payload)
    returned = root.findtext("Name")
    resolved = root.findtext("AUID")
    if returned != name or not re.fullmatch(r"\d{3}-[A-Z]{3}-\d{3}", resolved or "") or (auid and resolved != auid):
        raise ScopeViolation("native target identity differs")
    return root, resolved


def parse_page(payload, name, auid, start, end, page):
    check_window(start, end)
    root, _ = identity(payload, name, auid)
    count_text = root.findtext(".//Count")
    count = int(count_text) if count_text is not None else None
    if count is not None and count < 0:
        raise ValueError("negative native pagination marker")
    data = root.find("Data")
    text = data.text.strip() if data is not None and data.text else ""
    if not text:
        if count == 0 or page > 1:
            return [], {"continue": False, "termination": "explicit_zero" if count == 0 else "no_data_after_page"}
        raise ValueError("metadata-only first page does not establish an empty archive")
    reader = csv.DictReader(io.StringIO(text))
    if (not REQUIRED <= set(reader.fieldnames or []) or
            len(reader.fieldnames) != len(set(reader.fieldnames))):
        raise ValueError("native CSV schema differs")
    rows = list(reader)
    seen = set()
    for row in rows:
        if None in row or any(v is None for v in row.values()):
            raise ValueError("malformed native CSV row")
        jd = float(row["JD"])
        if not math.isfinite(jd) or not start <= jd <= end or jd >= STOP:
            raise ScopeViolation("out-of-window row: reject before any summaries")
        if not row["obsID"] or row["obsID"] in seen:
            raise ValueError("duplicate/missing native observation identity")
        seen.add(row["obsID"])
        if not math.isfinite(float(row["mag"])) or row["fainterThan"] not in {"0", "1"}:
            raise ValueError("invalid magnitude/limit convention")
        if row["uncert"] not in {"", "None"}:
            value = float(row["uncert"])
            if not math.isfinite(value) or value < 0:
                raise ValueError("invalid uncertainty")
        if not row["by"] or not row["band"]:
            raise ValueError("missing observer or band")
    if len(rows) >= ROW_CAP and count is None:
        raise UncertainCap("row cap without continuation marker; subdivide date window")
    if not rows and count not in (None, 0):
        raise ValueError("nonzero continuation marker with empty CSV")
    if rows and count == 0:
        raise ValueError("zero pagination marker with nonempty CSV")
    return rows, {"continue": count is not None and bool(rows),
                  "termination": "explicit_zero" if count == 0 else "continuation_marker" if count is not None and rows else "marker_absent"}


def combine_rows(groups):
    combined = {}
    duplicates = 0
    for rows in groups:
        for row in rows:
            key = row["obsID"]
            if key in combined:
                if row != combined[key]:
                    raise ValueError("conflicting repeated source observation")
                duplicates += 1
            combined[key] = row
    return sorted(combined.values(), key=lambda r: (float(r["JD"]), r["obsID"])), duplicates
