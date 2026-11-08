import importlib.util
from pathlib import Path
import unittest


SPEC = importlib.util.spec_from_file_location("a10d_pipeline", Path(__file__).resolve().parents[1]/"scripts/a10d_pipeline.py")
PIPELINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PIPELINE)


class OperatingCharacteristicPipelineTests(unittest.TestCase):
    def records(self):
        records = []
        for family, case, replicate in PIPELINE.task_grid():
            intervals = {str(years): {field: {"estimate": 0., "n": 380, "confirmed": False}
                                    for field in PIPELINE.COMPARISONS} for years in (3, 6)}
            result = {"intervals": {"primary": intervals}}
            if family == "v2-phase" and case in ("null", "alternative"):
                result["reference_calibration"] = {
                    str(years): {"joint_mc_covers_zero": True, "interior": False} for years in (3, 6)}
            records.append({"task": [family, case, replicate], "success": True, "result": result})
        return records

    def test_fixed_grid_and_finite_screen_do_not_imply_size_certificate(self):
        grid = PIPELINE.task_grid()
        self.assertEqual(len(grid), 360)
        self.assertEqual(len(set(grid)), 360)
        summary = PIPELINE.summarize(self.records())
        self.assertTrue(summary["screen_pass"])
        self.assertFalse(summary["formal_certification_pass"])
        self.assertFalse(summary["real_fit_automatic"])
        self.assertEqual(len(summary["null_rate_checks"]), 6)

    def test_null_failure_stops_gate_but_slow_state_does_not(self):
        records = self.records()
        for row in records:
            if row["task"][:2] in (["v2-phase", "slow_098"], ["v4-phase", "null"]) and row["task"][2] < 2:
                row["result"]["intervals"]["primary"]["6"]["gain_M3_M2"]["confirmed"] = True
        self.assertFalse(PIPELINE.summarize(records)["screen_pass"])
        for row in records:
            if row["task"][:2] == ["v4-phase", "null"]:
                row["result"]["intervals"]["primary"]["6"]["gain_M3_M2"]["confirmed"] = False
        self.assertTrue(PIPELINE.summarize(records)["screen_pass"])

    def test_missing_or_failed_trial_cannot_pass(self):
        records = self.records()
        self.assertFalse(PIPELINE.summarize(records[:-1])["screen_pass"])
        records[-1] = {"task": records[-1]["task"], "success": False, "error": "fixture"}
        self.assertFalse(PIPELINE.summarize(records)["screen_pass"])


if __name__ == "__main__":
    unittest.main()
