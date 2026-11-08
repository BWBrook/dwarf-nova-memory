import math
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


def episode(peak, onset, end, *, confirmed=True, onset_lo=None, end_hi=None):
    return {
        "peak_t": peak,
        "peak_mag": 8.0,
        "onset_lo": onset if onset_lo is None else onset_lo,
        "onset_hi": onset + 1.0 if onset is not None else None,
        "onset_t": onset,
        "onset_method": "fit",
        "end_t": end,
        "end_lo": end,
        "end_hi": end if end_hi is None else end_hi,
        "end_method": "fit",
        "confirmed_event": confirmed,
        "confirmation": "observers" if confirmed else None,
        "n_onset_fit": 2,
        "n_end_fit": 2,
    }


def emission(index=0, emitted=250.0, bright=220.0):
    return {"emission_index": index, "emitted_at": emitted, "bright_first_at": bright}


class PrefixReferenceHistoryTests(unittest.TestCase):
    def features(self, episodes, visits, *, rows=None, lookback=200.0,
                 emitted=250.0, bright=220.0):
        rows = [row(emitted)] if rows is None else rows
        with patch.object(reference, "x4_episodes", return_value=episodes), \
                patch.object(reference, "visits", return_value=[{"t": t} for t in visits]):
            return reference.forecast_features(
                rows, emission(emitted=emitted, bright=bright), lookback=lookback
            )

    def test_version_duration_and_earlier_gap_exclude_current_gap(self):
        episodes = [episode(145.0, 140.0, 150.0),
                    episode(185.0, 180.0, 190.0),
                    episode(225.0, 220.0, 230.0)]
        result = self.features(episodes, range(155, 221, 5))
        self.assertEqual(result["definition_version"], "a10-prefix-v3")
        self.assertEqual(result["duration"], 10.0)
        self.assertEqual(result["previous_duration"], 10.0)
        self.assertEqual(result["previous_gap"], 30.0)
        self.assertEqual(result["previous_gap_covered"], True)
        self.assertEqual(result["earlier_gaps"], [math.log(30.0)])

    def test_missing_current_onset_keeps_prior_history_but_not_current_gap(self):
        episodes = [episode(145.0, 140.0, 150.0),
                    episode(185.0, 180.0, 190.0),
                    episode(225.0, None, 230.0)]
        result = self.features(episodes, range(155, 221, 5))
        self.assertIsNone(result["duration"])
        self.assertEqual(result["previous_duration"], 10.0)
        self.assertEqual(result["earlier_gaps"], [math.log(30.0)])
        self.assertIsNone(result["previous_end_t"])
        self.assertIsNone(result["previous_gap"])
        self.assertIsNone(result["previous_longest_hole"])
        self.assertIsNone(result["previous_gap_covered"])

    def test_earlier_gaps_are_chronological_and_capped_at_six(self):
        episodes = [episode(105.0 + 40.0 * i, 100.0 + 40.0 * i, 110.0 + 40.0 * i)
                    for i in range(9)]
        result = self.features(episodes, range(115, 461, 5), emitted=500.0, bright=420.0,
                               lookback=500.0)
        self.assertEqual(result["previous_duration"], 10.0)
        self.assertEqual(result["earlier_gaps"], [math.log(30.0)] * 6)

    def test_uncovered_or_invalid_earlier_gaps_are_unavailable(self):
        episodes = [episode(145.0, 140.0, 150.0),
                    episode(185.0, 180.0, 190.0),
                    episode(225.0, 220.0, 230.0)]
        # The earlier gap has a nine-day hole; the current previous gap does not.
        result = self.features(episodes, [155.0, 164.0, 185.0, 195.0, 200.0, 205.0,
                                          210.0, 215.0, 225.0])
        self.assertEqual(result["previous_gap_covered"], True)
        self.assertEqual(result["earlier_gaps"], [])

        invalid = [episode(145.0, 140.0, 150.0),
                   episode(185.0, 180.0, 170.0),
                   episode(225.0, 220.0, 230.0)]
        result = self.features(invalid, range(155, 221, 5))
        self.assertIsNone(result["previous_duration"])

    def test_window_edge_and_missing_boundaries_do_not_make_marks(self):
        # prefix_start is 50, so onset 80 is exactly at the excluded 30-day edge.
        edge = [episode(85.0, 80.0, 85.0),
                episode(125.0, 120.0, 125.0, end_hi=220.0)]
        result = self.features(edge, range(90, 121, 5))
        self.assertIsNone(result["previous_duration"])
        self.assertEqual(result["earlier_gaps"], [])

        missing = [episode(145.0, None, 150.0),
                   episode(185.0, 180.0, 190.0),
                   episode(225.0, 220.0, 230.0)]
        result = self.features(missing, range(195, 221, 5))
        self.assertEqual(result["earlier_gaps"], [])

    def test_future_rows_cannot_change_prefix_history_fields(self):
        episodes = [episode(145.0, 140.0, 150.0),
                    episode(185.0, 180.0, 190.0),
                    episode(225.0, 220.0, 230.0)]
        base = self.features(episodes, range(155, 221, 5), rows=[row(250.0)])
        poisoned = self.features(episodes, range(155, 221, 5),
                                 rows=[row(250.0), row(260.0), row(9999.0)])
        for key in ("duration", "previous_duration", "previous_gap", "earlier_gaps",
                    "previous_gap_covered"):
            self.assertEqual(poisoned[key], base[key])


if __name__ == "__main__":
    unittest.main()
