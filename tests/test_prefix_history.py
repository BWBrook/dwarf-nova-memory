import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.prefix_features import forecast_features


def episode(onset, end, *, confirmed=True):
    return {
        "onset_t": onset,
        "onset_lo": onset - 0.5,
        "onset_hi": onset + 0.5,
        "onset_method": "fixture",
        "end_t": end,
        "end_lo": end - 0.5,
        "end_hi": end + 0.5,
        "end_method": "fixture",
        "peak_t": onset + 2.0,
        "peak_mag": 8.5,
        "confirmation": "fixture" if confirmed else None,
        "confirmed_event": confirmed,
        "n_onset_fit": 3,
        "n_end_fit": 3,
    }


def emission(cutoff=1000.0, bright_first_at=900.0):
    return {"emission_index": 0, "emitted_at": cutoff, "bright_first_at": bright_first_at}


def visit_times(times):
    return lambda _rows, _threshold: [{"t": t} for t in times]


class PrefixHistoryTests(unittest.TestCase):
    def test_new_fields_ignore_future_rows(self):
        episodes = [episode(700.0, 705.0), episode(740.0, 745.0), episode(800.0, 805.0)]
        rows = [{"JD": str(t)} for t in (640.0, 650.0, 700.0, 705.0, 740.0, 745.0, 800.0)]
        future = rows + [{"JD": "1000.1"}, {"JD": "1100.0"}]
        with patch("dnmem.prefix_features.x4_episodes", return_value=episodes), \
                patch("dnmem.prefix_features.visits", side_effect=visit_times(
                    [645.0, 652.0, 659.0, 666.0, 673.0, 680.0, 687.0, 694.0,
                     701.0, 708.0, 715.0, 722.0, 729.0, 736.0, 743.0, 750.0,
                     757.0, 764.0, 771.0, 778.0, 785.0, 792.0, 799.0])):
            before = forecast_features(rows, emission(bright_first_at=800.0))
            after = forecast_features(future, emission(bright_first_at=800.0))
        for key in ("duration", "previous_duration", "earlier_gaps", "previous_gap",
                    "previous_gap_covered"):
            self.assertEqual(after[key], before[key])

    def test_earlier_gaps_are_ordered_capped_and_exclude_current_gap(self):
        starts = [640.0, 660.0, 682.0, 705.0, 729.0, 754.0, 780.0, 807.0, 900.0]
        episodes = [episode(start, start + 5.0) for start in starts]
        times = [float(t) for t in range(640, 901, 3)]
        with patch("dnmem.prefix_features.x4_episodes", return_value=episodes), \
                patch("dnmem.prefix_features.visits", side_effect=visit_times(times)):
            result = forecast_features([{"JD": "900.0"}], emission())
        expected = [math.log(gap) for gap in (17.0, 18.0, 19.0, 20.0, 21.0, 22.0)]
        self.assertEqual(result["earlier_gaps"], expected)
        self.assertAlmostEqual(result["previous_duration"], 5.0)
        self.assertNotIn(math.log(88.0), result["earlier_gaps"])

    def test_edge_history_makes_previous_fields_unavailable(self):
        episodes = [episode(620.0, 625.0), episode(700.0, 705.0)]
        with patch("dnmem.prefix_features.x4_episodes", return_value=episodes), \
                patch("dnmem.prefix_features.visits", side_effect=visit_times(range(620, 801, 5))):
            result = forecast_features([{"JD": "700.0"}], emission(bright_first_at=700.0))
        self.assertIsNone(result["previous_duration"])
        self.assertIsNone(result["previous_gap"])
        self.assertEqual(result["earlier_gaps"], [])

    def test_nonpositive_point_duration_is_missing_without_dropping_record(self):
        episodes = [episode(700.0, 705.0), episode(760.0, 755.0), episode(820.0, 825.0)]
        with patch("dnmem.prefix_features.x4_episodes", return_value=episodes), \
                patch("dnmem.prefix_features.visits", side_effect=visit_times(range(700, 901, 5))):
            result = forecast_features([{"JD": "820.0"}], emission(bright_first_at=760.0))
        self.assertIsNone(result["previous_duration"])
        self.assertTrue(result["episode_found"])

        with patch("dnmem.prefix_features.x4_episodes", return_value=episodes[:2]), \
                patch("dnmem.prefix_features.visits", side_effect=visit_times(range(700, 801, 5))):
            current_bad = forecast_features([{"JD": "760.0"}], emission(bright_first_at=755.0))
        self.assertIsNone(current_bad["duration"])
        self.assertAlmostEqual(current_bad["previous_duration"], 5.0)

    def test_coverage_hole_excludes_earlier_gap(self):
        episodes = [episode(650.0, 655.0), episode(700.0, 705.0), episode(760.0, 765.0)]
        times = [655.0, 663.0, 670.0, 677.0, 684.0, 691.0, 698.0,
                 705.0, 713.0, 720.0, 727.0, 734.0, 741.0, 748.0, 755.0, 760.0]
        with patch("dnmem.prefix_features.x4_episodes", return_value=episodes), \
                patch("dnmem.prefix_features.visits", side_effect=visit_times(times)):
            result = forecast_features([{"JD": "760.0"}], emission(bright_first_at=760.0))
        self.assertFalse(result["previous_gap_covered"])
        self.assertEqual(result["earlier_gaps"], [])


if __name__ == "__main__":
    unittest.main()
