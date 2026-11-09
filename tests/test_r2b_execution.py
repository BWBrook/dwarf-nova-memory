import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from r2b_execute import rehearsal_rows, require_periods, summarize_scores
from dnmem.r2b_features import prepare_feature_ledgers
from dnmem.r2b_scoring import outcome_evidence


class ExecutionTests(unittest.TestCase):
    def test_protected_period_is_not_an_adjustable_runner_option(self):
        config = json.loads((ROOT / "configs/r2b_execution.json").read_text())
        require_periods(config)
        for key in ("training_start", "training_stop", "evaluation_stop"):
            changed = {**config, key: config[key] + 1.}
            with self.assertRaises(ValueError):
                require_periods(changed)

    def test_raw_report_rehearsal_has_prefix_only_training_outcomes(self):
        config = json.loads((ROOT / "configs/r2b_execution.json").read_text())
        rows = rehearsal_rows({**config, "rehearsal_episodes": 45})
        split = config["training_stop"]
        ledgers = prepare_feature_ledgers(rows, stop=config["evaluation_stop"])
        changed = copy.deepcopy(rows)
        for row in changed:
            if row["JD"] >= split:
                row["mag"] = 30.
        checked = 0
        for clock in ("point_original", "df", "point_at_df"):
            features = [r for r in ledgers[clock] if r["issue_time"] < split]
            left = outcome_evidence(rows, features, stop=split)
            right = outcome_evidence(changed, features, stop=split)
            self.assertEqual(left, right)
            self.assertGreater(sum(e["kind"] == "interval" for e in left), 8)
            for ev in left:
                self.assertLessEqual(ev["evidence_available_at"], split)
                self.assertLessEqual(ev["computed_as_of"], split)
            checked += len(left)
        self.assertGreater(checked, 30)

    def test_unsupported_identity_has_no_empirical_score_or_bound(self):
        rows = [{"issue_time": 2437000., "gain": None, "known_contrast": 0.,
                 "bounds_lower": None, "bounds_upper": None, "point_gain": None,
                 "status": "excluded", "identical_forecasts": True}]
        summary = summarize_scores(rows)
        self.assertEqual(summary["working"]["six_year"]["n"], 0)
        self.assertEqual(summary["algebraically_known_contrasts"]["six_year"]["n"], 1)
        self.assertEqual(summary["deterministic_bounds"]["n"], 0)
        self.assertEqual(summary["unsupported_identities"], 1)


if __name__ == "__main__":
    unittest.main()
