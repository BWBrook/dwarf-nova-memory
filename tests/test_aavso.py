from pathlib import Path
import sys
import hashlib
import json
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.aavso import read_acquisition, read_native_payload, ss_cyg_request_url


class NativeAavsoTests(unittest.TestCase):
    def test_receipt_bounds_and_hash_control_each_acquisition(self):
        payload = (ROOT / "data/fixtures/synthetic_aavso_vstar.xml").read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "native.xml"
            path.write_bytes(payload)
            receipt_path = Path(tmp) / "receipt.json"
            receipt = {"sha256": hashlib.sha256(payload).hexdigest(),
                       "source_url": ss_cyg_request_url(2435473.5, 2436569.5)}
            receipt_path.write_text(json.dumps(receipt))
            self.assertEqual(read_acquisition(path)[1]["rows"], 2)
            receipt["source_url"] = ss_cyg_request_url(2435500.6, 2436569.5)
            receipt_path.write_text(json.dumps(receipt))
            with self.assertRaises(ValueError):
                read_acquisition(path)
            receipt["sha256"] = "wrong"
            receipt_path.write_text(json.dumps(receipt))
            with self.assertRaises(ValueError):
                read_acquisition(path)

    def test_reserved_or_invalid_request_window_is_rejected(self):
        for start, end in ((2436934.0, 2436934.5), (2436934.0, 2437000.0),
                           (2436500.0, 2436400.0), (float("nan"), 2436500.0)):
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                ss_cyg_request_url(start, end)

    def test_native_limits_and_missing_uncertainties_stay_native(self):
        rows, summary = read_native_payload(ROOT / "data/fixtures/synthetic_aavso_vstar.xml", start_jd=2435473.5, end_jd=2436569.5)
        self.assertEqual(rows[1]["fainterThan"], "1")
        self.assertEqual(rows[1]["mag"], "12.5")
        self.assertEqual(summary["limiting_rows"], 1)
        self.assertEqual(summary["positive_reported_uncertainties"], 0)
        self.assertEqual(summary["time_scale"], "unresolved")

    def test_copied_future_row_wrong_identity_and_incomplete_payload_fail(self):
        text = (ROOT / "data/fixtures/synthetic_aavso_vstar.xml").read_text()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "development.xml"
            for changed in (text.replace("2435500.5", "2437000.5"),
                            text.replace("000-BCP-220", "wrong-target"),
                            text.replace("synthetic-2", "synthetic-1"),
                            text.replace("<Count>2", "<Count>3"),
                            text.replace("11.9", "nan")):
                path.write_text(changed)
                with self.subTest(changed=changed), self.assertRaises(ValueError):
                    read_native_payload(path, start_jd=2435473.5, end_jd=2436569.5)

    def test_quarantine_path_and_symlink_are_rejected(self):
        text = (ROOT / "data/fixtures/synthetic_aavso_vstar.xml").read_text()
        with tempfile.TemporaryDirectory() as tmp:
            quarantine = Path(tmp) / "quarantine"
            quarantine.mkdir()
            native = quarantine / "native.xml"
            native.write_text(text)
            link = Path(tmp) / "development.xml"
            link.symlink_to(native)
            for path in (native, link):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    read_native_payload(path, start_jd=2435473.5, end_jd=2436569.5)


if __name__ == "__main__":
    unittest.main()
