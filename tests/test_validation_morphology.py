from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.validation_morphology import J1910, qualify, records, summary


def morphology_record(duration, end_slope=0.3):
    return {
        "duration": duration,
        "onset": (-0.6, 0.2),
        "end": (end_slope, 0.22),
        "n_onset": 8,
        "n_end": 12,
        "above": (0.2, 0.2),
        "below": (0.2, 0.2),
    }


def qualifying_summary():
    return {
        "episodes": 100,
        "onset": {
            "abs_slope_mag_per_d": {"q50": 0.667, "n": 70},
            "residual_sd_mag": {"q50": 0.2, "n": 70},
        },
        "end": {
            "abs_slope_mag_per_d": {"q50": 0.333, "n": 90},
            "residual_sd_mag": {"q50": 0.222, "n": 90},
        },
        "end_slope_vs_duration_spearman": 0.04,
        "decline_slope_above_threshold": {"q50": 0.203, "n": 83},
        "decline_slope_below_threshold": {"q50": 0.2, "n": 78},
        "fit_diagnostics": {
            "above_threshold": {"positive_fit_fraction": 0.83},
            "below_threshold": {"positive_fit_fraction": 0.78},
        },
    }


class ValidationMorphologyTests(unittest.TestCase):
    def test_records_preserve_a04d_selection_and_fields(self):
        onset = J1910 + 10
        end = onset + 10
        episode = {
            "onset_lo": onset,
            "onset_hi": onset + 0.5,
            "end_lo": end,
            "end_hi": end + 0.5,
            "peak_t": onset + 4,
            "confirmed_event": True,
            "gap_split": False,
        }
        synthetic_visits = [
            {"t": onset + offset, "value": value}
            for offset, value in ((-0.5, 10.8), (0, 10.4), (0.5, 10.0), (1, 9.6))
        ] + [
            {"t": end + offset, "value": value}
            for offset, value in (
                (-2, 9.2), (-1.5, 9.4), (-1, 9.6), (-0.5, 9.8),
                (0, 10.0), (0.5, 10.2), (1, 10.4), (1.5, 10.6), (2, 10.8),
            )
        ]
        with patch("dnmem.validation_morphology.visits", return_value=synthetic_visits), patch(
            "dnmem.validation_morphology.x1_vote_episodes", return_value=[episode]
        ):
            result = records([], 10.0)
        self.assertEqual(len(result), 1)
        self.assertEqual(
            set(result[0]),
            {"duration", "onset", "end", "n_onset", "n_end", "above", "below"},
        )
        self.assertLess(result[0]["onset"][0], 0)
        self.assertGreater(result[0]["end"][0], 0)
        self.assertIsNotNone(result[0]["above"])
        self.assertIsNotNone(result[0]["below"])

    def test_summary_uses_average_ranks_for_ties(self):
        records_ = [
            morphology_record(duration, slope)
            for duration, slope in zip((1, 2, 2, 3), (1, 1, 2, 3))
        ]
        result = summary(records_)
        self.assertAlmostEqual(result["end_slope_vs_duration_spearman"], 0.833, places=3)
        self.assertEqual(result["end_slope_vs_duration_status"], "ok")
        self.assertEqual(result["end_slope_vs_duration_n"], 4)

    def test_summary_marks_insufficient_and_constant_correlations(self):
        insufficient = summary([morphology_record(8)])
        self.assertIsNone(insufficient["end_slope_vs_duration_spearman"])
        self.assertEqual(insufficient["end_slope_vs_duration_status"], "insufficient")
        constant = summary([morphology_record(8, 0.2), morphology_record(8, 0.4)])
        self.assertIsNone(constant["end_slope_vs_duration_spearman"])
        self.assertEqual(constant["end_slope_vs_duration_status"], "constant")
        empty = summary([])
        self.assertIsNone(empty["fit_diagnostics"]["below_threshold"]["positive_fit_fraction"])

    def test_summary_reports_positive_fit_counts_and_fractions(self):
        records_ = [morphology_record(8, 0.3), morphology_record(9, -0.2)]
        records_[1]["below"] = (-0.2, 0.1)
        result = summary(records_)
        self.assertEqual(result["fit_diagnostics"]["end"]["fit_count"], 2)
        self.assertEqual(result["fit_diagnostics"]["end"]["positive_fit_count"], 1)
        self.assertEqual(result["fit_diagnostics"]["end"]["positive_fit_fraction"], 0.5)
        self.assertEqual(result["fit_diagnostics"]["below_threshold"]["wrong_sign_fit_count"], 1)

    def test_qualification_passes_matching_summaries_and_fails_each_gate(self):
        real = qualifying_summary()
        passed = qualify(real, deepcopy(real))
        self.assertTrue(passed["passed"])
        modifications = {
            "onset_slope_median": lambda value: value["onset"]["abs_slope_mag_per_d"].update(q50=0.8),
            "end_slope_median": lambda value: value["end"]["abs_slope_mag_per_d"].update(q50=0.4),
            "end_residual_sd_median": lambda value: value["end"]["residual_sd_mag"].update(q50=0.3),
            "end_slope_duration_spearman": lambda value: value.update(end_slope_vs_duration_spearman=0.3),
            "decline_side_slope_ratio": lambda value: value["decline_slope_below_threshold"].update(q50=0.4),
            "above_positive_fit_fraction": lambda value: value["fit_diagnostics"]["above_threshold"].update(positive_fit_fraction=0.6),
            "below_positive_fit_fraction": lambda value: value["fit_diagnostics"]["below_threshold"].update(positive_fit_fraction=0.6),
        }
        for gate, modify in modifications.items():
            with self.subTest(gate=gate):
                synthetic = deepcopy(real)
                modify(synthetic)
                result = qualify(real, synthetic)
                self.assertFalse(result["passed"])
                self.assertFalse(result["gates"][gate])

    def test_qualification_fails_closed_on_missing_statistics(self):
        result = qualify(qualifying_summary(), {})
        self.assertFalse(result["passed"])
        self.assertTrue(all(not value for value in result["gates"].values()))


if __name__ == "__main__":
    unittest.main()
