from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
from dnmem.extract import x1_vote_episodes
from dnmem.extract_x3 import crossing_interval, x3_fitted_episodes
from test_extract import obs


def light_curve(onset=100.0, end=112.0, rise=1.0, decline=0.33, peak=8.5, skip=(), observers="abc"):
    """Nightly estimates from three observers on a continuous rise/plateau/decline."""
    def mag(t):
        if t < onset - 2.2 / rise:
            return 12.2
        if t < onset + (10 - peak) / rise:
            return max(peak, 10 - rise * (t - onset))
        if t < end - (10 - peak) / decline:
            return peak
        return min(12.2, 10 + decline * (t - end))
    rows = []
    for night in range(90, 125):
        if night in skip:
            continue
        for k, who in enumerate(observers):
            t = night + 0.6 + 0.1 * k
            rows.append(obs(round(t, 2), round(mag(t), 1), who))
    return rows


class CrossingIntervalTests(unittest.TestCase):
    def test_noiseless_decline_interval_holds_crossing(self):
        points = [(48 + 0.25 * k, 10 + 0.4 * (48 + 0.25 * k - 50)) for k in range(17)]
        lo, hi = crossing_interval(points, 10.0, 1, (0.35, 0.45))
        self.assertLess(lo, 50.0)
        self.assertGreater(hi, 50.0)
        self.assertAlmostEqual((lo + hi) / 2, 50.0, places=2)

    def test_single_estimate_uses_slope_prior(self):
        lo, hi = crossing_interval([(10.0, 10.8)], 10.0, -1, (0.8, 0.8))
        self.assertGreater(hi, 10.0)
        self.assertLess(lo, 10.0 + 0.8 / 0.8)
        self.assertGreater(hi - lo, 1.0)

    def test_no_estimates_gives_none(self):
        self.assertIsNone(crossing_interval([], 10.0, 1, (0.35, 0.45)))


class X3Tests(unittest.TestCase):
    def test_true_crossings_inside_intervals(self):
        (episode,) = x3_fitted_episodes(light_curve())
        self.assertLess(episode["onset_lo"], 100.0)
        self.assertGreater(episode["onset_hi"], 100.0)
        self.assertLess(episode["end_lo"], 112.0)
        self.assertGreater(episode["end_hi"], 112.0)
        self.assertEqual((episode["onset_method"], episode["end_method"]), ("fit", "fit"))

    def test_noisy_faint_night_before_end_does_not_truncate_interval(self):
        rows = [r for r in light_curve() if not (r["JD"] in ("111.6", "111.7"))]
        rows += [obs(111.6, 10.1, "a"), obs(111.7, 10.2, "b")]
        x1 = x1_vote_episodes(rows)[0]
        (x3,) = x3_fitted_episodes(rows)
        self.assertLess(x1["end_hi"], 112.0)
        self.assertLess(x3["end_lo"], 112.0)
        self.assertGreater(x3["end_hi"], 112.0)

    def test_plateau_gap_up_to_seven_days_does_not_split(self):
        rows = light_curve(end=118.0, skip=range(104, 109))
        self.assertEqual(len(x1_vote_episodes(rows)), 2)
        (episode,) = x3_fitted_episodes(rows)
        self.assertFalse(episode["gap_split"])

    def test_fast_rise_without_near_threshold_estimates_falls_back_to_adjacency(self):
        rows = light_curve(rise=6.0)
        (episode,) = x3_fitted_episodes(rows)
        self.assertEqual(episode["onset_method"], "adjacency")
        self.assertLess(episode["onset_lo"], 100.0)
        self.assertGreater(episode["onset_hi"], 100.0)

    def test_confirmation_needs_two_observers_half_a_magnitude_faint(self):
        (episode,) = x3_fitted_episodes(light_curve())
        self.assertGreater(episode["confirmed"], 112.0 + 0.5 / 0.33)
        (single,) = x3_fitted_episodes(light_curve(observers="a"))
        self.assertIsNone(single["confirmed"])


if __name__ == "__main__":
    unittest.main()
