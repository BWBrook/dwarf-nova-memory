from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.evaluation_native import (  # noqa: E402
    AUID,
    EVALUATION_CUTOFF_JD,
    EVALUATION_START_JD,
    RowCapError,
    combine_native,
    parse_native_bytes,
    request_url,
    request_windows,
    select_analysis_rows,
)


FIXTURE = ROOT / "data/fixtures/a10g_native/native_mixed.xml"


def native_payload(rows: list[dict[str, str]], *, count: int | None = None, extra_xml: str = "") -> bytes:
    columns = ["obsID", "JD", "mag", "uncert", "fainterThan", "band", "by", "val"]
    text = ",".join(columns) + "\n" + "\n".join(
        ",".join(row[column] for column in columns) for row in rows
    ) + "\n"
    if count is None:
        count = len(rows)
    return (
        "<?xml version=\"1.0\"?><VSXObject>"
        f"<Name>SS Cyg</Name><AUID>{AUID}</AUID>{extra_xml}"
        f"<Count>{count}</Count><Data><![CDATA[{text}]]></Data></VSXObject>"
    ).encode()


def row(obs_id: str, jd: float, *, mag: str = "11.0") -> dict[str, str]:
    return {
        "obsID": obs_id,
        "JD": format(jd, ".17g"),
        "mag": mag,
        "uncert": "",
        "fainterThan": "0",
        "band": "Vis.",
        "by": "SIM",
        "val": "V",
    }


class EvaluationNativeTests(unittest.TestCase):
    def test_request_bounds_and_windows_use_exclusive_cutoff(self):
        with self.assertRaises(ValueError):
            request_url(EVALUATION_START_JD - 1, EVALUATION_START_JD)
        with self.assertRaises(ValueError):
            request_url(EVALUATION_START_JD, EVALUATION_CUTOFF_JD)
        with self.assertRaises(ValueError):
            request_url(EVALUATION_START_JD, math.nan)

        windows = request_windows(EVALUATION_START_JD, EVALUATION_CUTOFF_JD)
        self.assertEqual(windows[0][0], EVALUATION_START_JD)
        self.assertEqual(windows[-1][1], math.nextafter(EVALUATION_CUTOFF_JD, -math.inf))
        self.assertTrue(all(end < EVALUATION_CUTOFF_JD for _, end in windows))
        self.assertTrue(all(end - start <= 366.0 for start, end in windows))
        self.assertTrue(all(windows[i][1] == windows[i + 1][0] for i in range(len(windows) - 1)))

    def test_parser_retains_all_rows_columns_metadata_and_analysis_selector(self):
        payload = FIXTURE.read_bytes()
        rows, metadata = parse_native_bytes(payload, start_jd=EVALUATION_START_JD, end_jd=2436934.5)
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0]["JD"], "2436934.0")
        self.assertEqual(rows[0]["timeReference"], "unknown")
        self.assertEqual(rows[0]["extraColumn"], "kept-lower")
        self.assertEqual(metadata["extra_native_columns"], ["timeReference", "commentCode", "extraColumn"])
        by_tag = {item["tag"]: item for item in metadata["xml_metadata"]}
        self.assertEqual(by_tag["TimeReference"]["text"], "provider reference unspecified")
        self.assertEqual(by_tag["UnknownMetadata"]["attributes"], {"key": "kept"})
        selected = select_analysis_rows(rows)
        self.assertEqual([item["obsID"] for item in selected], ["lower", "limit", "upper"])
        self.assertEqual(selected[1]["fainterThan"], "1")

    def test_provider_endpoints_are_inclusive_but_cutoff_is_exclusive(self):
        endpoint = 2436934.5
        rows, _ = parse_native_bytes(
            native_payload([row("lower", EVALUATION_START_JD), row("upper", endpoint)]),
            start_jd=EVALUATION_START_JD,
            end_jd=endpoint,
        )
        self.assertEqual([item["obsID"] for item in rows], ["lower", "upper"])
        cutoff_payload = native_payload([row("cutoff", EVALUATION_CUTOFF_JD)])
        with self.assertRaises(ValueError):
            parse_native_bytes(
                cutoff_payload,
                start_jd=EVALUATION_CUTOFF_JD - 1,
                end_jd=math.nextafter(EVALUATION_CUTOFF_JD, -math.inf),
            )

    def test_empty_response_requires_explicit_zero_count(self):
        empty = b"<VSXObject><Name>SS Cyg</Name><AUID>000-BCP-220</AUID><Count>0</Count></VSXObject>"
        rows, metadata = parse_native_bytes(
            empty, start_jd=EVALUATION_START_JD, end_jd=EVALUATION_START_JD + 1
        )
        self.assertEqual(rows, [])
        self.assertEqual(metadata["provider_count"], 0)
        not_empty = empty.replace(b"<Count>0", b"<Count>1")
        with self.assertRaises(ValueError):
            parse_native_bytes(not_empty, start_jd=EVALUATION_START_JD, end_jd=EVALUATION_START_JD + 1)

    def test_empty_csv_with_valid_header_is_allowed_only_for_count_zero(self):
        rows, metadata = parse_native_bytes(
            (ROOT / "data/fixtures/a10g_native/native_empty_count_zero.xml").read_bytes(),
            start_jd=EVALUATION_START_JD,
            end_jd=EVALUATION_START_JD + 1,
        )
        self.assertEqual(rows, [])
        self.assertEqual(metadata["native_columns"][:2], ["obsID", "JD"])
        self.assertEqual(metadata["extra_native_columns"], ["timeReference", "commentCode", "extraColumn"])
        invalid_count = (ROOT / "data/fixtures/a10g_native/native_empty_count_zero.xml").read_bytes().replace(
            b"<Count>0</Count>", b"<Count>1</Count>"
        )
        with self.assertRaises(ValueError):
            parse_native_bytes(
                invalid_count,
                start_jd=EVALUATION_START_JD,
                end_jd=EVALUATION_START_JD + 1,
            )

    def test_row_cap_and_invalid_rows_fail(self):
        many = [row(f"obs-{i}", EVALUATION_START_JD + i / 100000) for i in range(50_000)]
        with self.assertRaises(RowCapError):
            parse_native_bytes(
                native_payload(many),
                start_jd=EVALUATION_START_JD,
                end_jd=EVALUATION_START_JD + 1,
            )
        bad = row("bad", EVALUATION_START_JD)
        bad["JD"] = "nan"
        with self.assertRaises(ValueError):
            parse_native_bytes(
                native_payload([bad]), start_jd=EVALUATION_START_JD, end_jd=EVALUATION_START_JD + 1
            )

    def test_combine_deduplicates_identical_obsid_and_rejects_conflicts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def write_acquisition(name: str, payload: bytes, start: float, end: float, **receipt_extra):
                directory = root / name
                directory.mkdir()
                native = directory / "native.xml"
                native.write_bytes(payload)
                receipt = {
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "source_url": request_url(start, end),
                    **receipt_extra,
                }
                (directory / "receipt.json").write_text(json.dumps(receipt))
                return native

            duplicate = row("same", EVALUATION_START_JD + 0.5)
            first = write_acquisition(
                "first", native_payload([duplicate]), EVALUATION_START_JD, EVALUATION_START_JD + 1
            )
            second = write_acquisition(
                "second", native_payload([duplicate]), EVALUATION_START_JD + 0.25, EVALUATION_START_JD + 1
            )
            rows, metadata = combine_native([first, second])
            self.assertEqual(len(rows), 1)
            self.assertEqual(metadata["duplicate_rows_removed"], 1)

            conflicting = dict(duplicate, mag="12.0")
            third = write_acquisition(
                "third", native_payload([conflicting]), EVALUATION_START_JD, EVALUATION_START_JD + 1
            )
            with self.assertRaisesRegex(ValueError, "conflicting"):
                combine_native([first, third])

    def test_receipt_hash_and_provenance_are_checked_before_parse_and_quarantine_rejected(self):
        payload = native_payload([row("one", EVALUATION_START_JD + 0.5)])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / "acquisition"
            directory.mkdir()
            native = directory / "native.xml"
            native.write_bytes(payload)
            (directory / "receipt.json").write_text(
                json.dumps({"sha256": "0" * 64, "source_url": request_url(EVALUATION_START_JD, EVALUATION_START_JD + 1)})
            )
            with patch("dnmem.evaluation_native.parse_native_bytes", side_effect=AssertionError("parsed before hash")):
                with self.assertRaises(ValueError):
                    combine_native([native])

            quarantine = root / "quarantine" / "native.xml"
            quarantine.parent.mkdir()
            quarantine.write_bytes(payload)
            with self.assertRaises(ValueError):
                combine_native([quarantine])

            (directory / "receipt.json").write_text(
                json.dumps(
                    {
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "source_url": request_url(EVALUATION_START_JD, EVALUATION_START_JD + 1).replace(
                            AUID, "wrong-target"
                        ),
                    }
                )
            )
            with self.assertRaises(ValueError):
                combine_native([native])


if __name__ == "__main__":
    unittest.main()
