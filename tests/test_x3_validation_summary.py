import importlib.util
from pathlib import Path
from unittest import TestCase, mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "x3_validation_summary", ROOT / "scripts" / "summarize_x3_validation.py"
)
SUMMARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SUMMARY)


class X3ValidationSummaryTests(TestCase):
    def test_ambiguous_emissions_cannot_evade_the_causal_false_rate_gate(self):
        rows = [{"operational_confirmation_false_emission_count": "0",
                 "operational_confirmation_ambiguous_emission_count": "1", "exposure_years": "1"}] * 2
        metric = SUMMARY.ratio_interval(SUMMARY._with_unsafe_counts(rows),
                                       "operational_confirmation_unsafe_emission_count", "exposure_years")
        self.assertEqual(SUMMARY._gate(metric, .2, "below"), "FAIL")

    def test_ratio_uses_pooled_denominator_and_cluster_delta_mcse(self):
        rows = [{"hit": "1", "n": "1"}, {"hit": "0", "n": "9"}]
        metric = SUMMARY.ratio_interval(rows, "hit", "n")
        self.assertAlmostEqual(metric["estimate"], 0.1)
        self.assertAlmostEqual(metric["mcse"], 0.18)

    def test_zero_count_rare_rate_has_nonzero_wilson_upper(self):
        rows = [{"bad": "0", "events": "10"}, {"bad": "0", "events": "10"}]
        metric = SUMMARY.ratio_interval(rows, "bad", "events", rare=True)
        self.assertEqual(metric["estimate"], 0.0)
        self.assertGreater(metric["upper"], 0.0)
        self.assertGreaterEqual(metric["lower"], 0.0)
        self.assertLessEqual(metric["upper"], 1.0)

    def test_undefined_bias_vetoes_cell(self):
        rows = [{"total_bias": ""}, {"total_bias": ""}]
        metric = SUMMARY.mean_interval(rows, "total_bias")
        self.assertEqual(metric["undefined"], 2)
        self.assertEqual(SUMMARY._gate(metric, 0.02, "inside"), "INCONCLUSIVE")

    def test_missing_entire_cell_is_rejected_before_decisions(self):
        expected = {
            ("primary", "1910_1929", "random", "10.0", "X3", "C1_7", 0),
            ("primary", "1910_1929", "random", "10.0", "X3", "C1_7", 1),
        }
        row = {"case": "primary", "stratum": "1910_1929", "phase": "random",
               "threshold": "10.0", "extractor": "X3", "rule": "C1_7",
               "replicate": "0", "seed": "1", "truth_seed": "2", "measurement_seed": "3"}
        with mock.patch.object(SUMMARY, "_expected_grid", return_value=expected):
            with self.assertRaisesRegex(ValueError, "grid mismatch"):
                SUMMARY._validate_rows([row], {})

    def test_rule_selection_cannot_cherry_pick_cells(self):
        cells = []
        for rule in SUMMARY.RULES:
            for case in ("primary", "structured"):
                for era in SUMMARY.ERAS:
                    for phase in SUMMARY.PHASES:
                        cells.append({"case": case, "stratum": era, "phase": phase,
                                      "threshold": "10.0", "extractor": "X3", "rule": rule,
                                      "verdict": "PASS"})
        cells[0]["verdict"] = "FAIL"
        decisions = SUMMARY.candidate_decisions(cells)
        self.assertEqual([item["verdict"] for item in decisions], ["FAIL", "PASS"])
        self.assertEqual(SUMMARY.choose_rule(decisions), "C2_095")
        cells[-1]["verdict"] = "FAIL"
        self.assertIsNone(SUMMARY.choose_rule(SUMMARY.candidate_decisions(cells)))

    def test_structured_control_adds_prespecified_histories_and_cells(self):
        self.assertEqual(len(SUMMARY.expected_grid()), 79200)
        structured = [key for key in SUMMARY.expected_grid() if key[0] == "structured"]
        self.assertEqual(len(structured), 14400)


if __name__ == "__main__":
    import unittest
    unittest.main()
