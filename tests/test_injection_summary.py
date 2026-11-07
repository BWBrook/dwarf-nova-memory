import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("injection_summary", ROOT / "scripts/summarize_injection_recovery.py")
SUMMARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SUMMARY)


class InjectionSummaryTests(unittest.TestCase):
    def test_ratio_weights_event_denominators_and_uses_replicates(self):
        rows = [{"hit": "1", "n": "1"}, {"hit": "0", "n": "9"}]
        metric = SUMMARY.ratio_interval(rows, "hit", "n")
        self.assertAlmostEqual(metric["estimate"], .1)
        self.assertAlmostEqual(metric["mcse"], .18)

    def test_undefined_replicates_cannot_pass_a_bias_gate(self):
        metric = SUMMARY.mean_interval([{"bias": "0"}, {"bias": "0"}, {"bias": ""}], "bias")
        self.assertEqual(metric["undefined"], 1)
        self.assertEqual(SUMMARY.gate(metric, .02, "inside"), "INCONCLUSIVE")

    def test_uncertain_and_failed_coverage_are_distinct(self):
        self.assertEqual(SUMMARY.gate({"lower": .88, "upper": .92, "undefined": 0}, .9, "above"), "INCONCLUSIVE")
        self.assertEqual(SUMMARY.gate({"lower": .85, "upper": .89, "undefined": 0}, .9, "above"), "FAIL")
        self.assertEqual(SUMMARY.gate({"lower": -.01, "upper": .01, "undefined": 0}, .02, "inside"), "PASS")

    def test_missing_entire_design_cells_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            content = "stratum,phase,process,threshold,extractor,rule\n1900_1909,random,null,10.0,X1,C1_4\n"
            (root / "replicates.csv").write_text(content)
            receipt = {"replicates_sha256": hashlib.sha256(content.encode()).hexdigest(), "replicates_per_cell": 1}
            (root / "receipt.json").write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, "grid"):
                SUMMARY.summarize(root, root / "summary")


if __name__ == "__main__":
    unittest.main()
