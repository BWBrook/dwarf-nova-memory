from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dnmem.aavso import ss_cyg_request_url
from dnmem.coverage import combine_acquisitions, profile


class CoverageTests(unittest.TestCase):
    def test_overlap_is_deduplicated_and_conflicting_versions_fail(self):
        fixture = Path(__file__).resolve().parents[1] / "data/fixtures/synthetic_aavso_vstar.xml"
        payload = fixture.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for name in ("a", "b"):
                directory = Path(tmp) / name
                directory.mkdir()
                native = directory / "native.xml"
                native.write_bytes(payload)
                (directory / "receipt.json").write_text(json.dumps({"sha256": hashlib.sha256(payload).hexdigest(),
                    "source_url": ss_cyg_request_url(2435473.5, 2436569.5)}))
                paths.append(native)
            rows, repeated = combine_acquisitions(paths)
            self.assertEqual((len(rows), repeated), (2, 2))
            changed = payload.replace(b"11.9", b"11.8")
            paths[1].write_bytes(changed)
            receipt = paths[1].parent / "receipt.json"
            values = json.loads(receipt.read_text())
            values["sha256"] = hashlib.sha256(changed).hexdigest()
            receipt.write_text(json.dumps(values))
            with self.assertRaises(ValueError):
                combine_acquisitions(paths)

    def test_repeats_limits_flags_and_missing_days_are_distinct(self):
        base = {"band": "Vis.", "val": "V", "fainterThan": "0", "mag": "12", "by": "SIM"}
        rows = [dict(base, JD="10.2"), dict(base, JD="10.3"),
                dict(base, JD="12.2", fainterThan="1", mag="9"),
                dict(base, JD="14.2", val="T"),
                dict(base, JD="16.2", fainterThan="1", mag="11")]
        result = profile(rows, 10, 18)
        self.assertEqual(result["native_rows"], 5)
        self.assertEqual(result["informative_visual_V_rows_at_mag10"], 3)
        self.assertEqual(result["observer_JD_bin_pairs"], 2)
        self.assertEqual(result["repeat_rows_within_observer_JD_bin"], 1)
        self.assertEqual(result["observed_JD_bins"], 2)
        self.assertEqual(result["internal_informative_gaps_over_4d"], 1)
        self.assertAlmostEqual(result["span_after_last_informative_d"], 1.8)


if __name__ == "__main__":
    unittest.main()
