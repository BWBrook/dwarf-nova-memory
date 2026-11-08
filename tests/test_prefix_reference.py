from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import dnmem.prefix_reference as reference


def row(jd):
    return {"JD": str(jd), "band": "Vis.", "val": "V", "mag": "9.0",
            "fainterThan": "0", "obsID": str(jd), "by": "a", "obsName": "a"}


def episode(peak, onset_lo, onset_hi, onset_t=None, end_t=None, *, end_hi=None,
            confirmed=True, method="fit"):
    return {
        "peak_t": peak,
        "peak_mag": 8.0,
        "onset_lo": onset_lo,
        "onset_hi": onset_hi,
        "onset_t": onset_t,
        "onset_method": method,
        "end_t": end_t,
        "end_lo": end_t,
        "end_hi": end_hi if end_hi is not None else end_t,
        "end_method": method,
        "confirmation": "observers" if confirmed else None,
        "confirmed_event": confirmed,
        "n_onset_fit": 2,
        "n_end_fit": 2,
    }


def emission(index, emitted, bright):
    return {"emission_index": index, "emitted_at": emitted, "bright_first_at": bright}


def fake_visits(times):
    return [{"t": t} for t in times]


class PrefixReferenceTests(unittest.TestCase):
    def test_prefix_window_excludes_future_poison_and_keeps_boundaries(self):
        rows = [row(89.9), row(90.0), row(90.1), row(100.0), row(100.1)]
        seen = {}

        def extract(prefix, threshold):
            seen["rows"] = prefix
            return [episode(99.0, 95.0, 96.0, 95.5, 98.0)]

        with patch.object(reference, "x4_episodes", side_effect=extract):
            result = reference.forecast_features(rows, emission(0, 100.0, 99.0), lookback=10)
        self.assertEqual([float(r["JD"]) for r in seen["rows"]], [90.1, 100.0])
        self.assertEqual(result["prefix_rows"], 2)
        self.assertEqual(result["prefix_last_jd"], 100.0)
        self.assertNotIn("future", result)

    def test_ledger_issue_filter_uses_issue_time_and_preserves_repeat_context(self):
        rows = [row(100), row(110)]
        emissions = [emission(0, 100.0, 99.0), emission(1, 110.0, 109.0)]
        def extract(prefix, threshold):
            if max(float(r["JD"]) for r in prefix) <= 100:
                return [episode(99.0, 95.0, 96.0, 95.5, 98.0)]
            return [episode(105.0, 95.0, 96.0, 95.5, 108.0)]
        with patch.object(reference, "causal_confirmations", return_value=emissions), \
             patch.object(reference, "x4_episodes", side_effect=extract):
            result = reference.forecast_ledger(rows, start=105, stop=115)
        self.assertEqual([r["emission_index"] for r in result], [1])
        self.assertTrue(result[0]["repeat_of_previous"])

    def test_repeat_at_exactly_one_day_is_not_flagged(self):
        rows = [row(100), row(110)]
        emissions = [emission(0, 100.0, 99.0), emission(1, 110.0, 109.0)]

        def extract(prefix, threshold):
            if max(float(r["JD"]) for r in prefix) <= 100:
                return [episode(99.0, 95.0, 96.0, 95.5, 98.0)]
            return [episode(105.0, 96.0, 97.0, 96.5, 108.0)]

        with patch.object(reference, "causal_confirmations", return_value=emissions), \
             patch.object(reference, "x4_episodes", side_effect=extract):
            result = reference.forecast_ledger(rows)
        self.assertFalse(result[1]["repeat_of_previous"])

    def test_validation_blocks_invalid_bounds_and_parameters(self):
        with self.assertRaises(ValueError):
            reference.forecast_features([], emission(0, 1, 0), latency=-1)
        with self.assertRaises(ValueError):
            reference.forecast_features([], emission(0, 1, 0), lookback=0)
        with self.assertRaises(ValueError):
            reference.forecast_ledger([], start=3, stop=2)

    def test_overtaken_candidate_is_excluded(self):
        rows = [row(10), row(20), row(30)]
        ledger = [{"emission_index": 0, "emitted_at": 10.0, "issue_time": 15.0}]
        retrospective = [episode(12.0, 11.0, 14.0, 12.5, 13.5)]
        with patch.object(reference, "x4_episodes", return_value=retrospective), \
             patch.object(reference, "visits", return_value=fake_visits([10.0, 20.0, 30.0])):
            result = reference.outcome_evidence(rows, ledger, stop=30.0)
        self.assertEqual(result[0]["kind"], "excluded")
        self.assertEqual(result[0]["reason"], "overtaken")
        self.assertTrue(result[0]["overtaken"])
        self.assertIsNone(result[0]["censor_at"])

    def test_gap_spanning_issue_censors_at_issue_without_resetting_gap(self):
        rows = [row(4), row(12), row(20)]
        ledger = [{"emission_index": 0, "emitted_at": 9.0, "issue_time": 10.0}]
        with patch.object(reference, "x4_episodes", return_value=[]), \
             patch.object(reference, "visits", return_value=fake_visits([4.0, 12.0, 20.0])):
            result = reference.outcome_evidence(rows, ledger, stop=20.0)
        self.assertEqual(result[0]["kind"], "right_censored")
        self.assertEqual(result[0]["reason"], "coverage")
        self.assertEqual(result[0]["censor_at"], 10.0)

    def test_poison_after_stop_never_reaches_retrospective_extractor(self):
        rows = [row(1), row(5), row(50)]
        ledger = [{"emission_index": 0, "emitted_at": 2.0, "issue_time": 3.0}]
        seen = {}

        def extract(asof_rows, threshold):
            seen["rows"] = asof_rows
            return []

        with patch.object(reference, "x4_episodes", side_effect=extract), \
             patch.object(reference, "visits", return_value=fake_visits([1.0, 5.0])):
            reference.outcome_evidence(rows, ledger, stop=10.0)
        self.assertEqual([float(r["JD"]) for r in seen["rows"]], [1.0, 5.0])

    def test_strict_interval_survival_and_one_onset_one_forecast(self):
        rows = [row(1), row(20)]
        ledger = [
            {"emission_index": 0, "emitted_at": 9.0, "issue_time": 10.0},
            {"emission_index": 1, "emitted_at": 14.0, "issue_time": 16.0},
        ]
        retrospective = [episode(14.5, 12.0, 15.0, 13.0, 14.0)]
        with patch.object(reference, "x4_episodes", return_value=retrospective), \
             patch.object(reference, "visits", return_value=fake_visits([1.0, 9.0, 12.0, 16.0, 20.0])):
            result = reference.outcome_evidence(rows, ledger, stop=20.0)
        self.assertEqual(result[0]["kind"], "interval")
        self.assertEqual(result[0]["onset_index"], 0)
        self.assertEqual(result[1]["kind"], "excluded")
        self.assertEqual(result[1]["reason"], "overtaken")
        self.assertEqual([r["onset_index"] for r in result if r["kind"] == "interval"], [0])


if __name__ == "__main__":
    unittest.main()
