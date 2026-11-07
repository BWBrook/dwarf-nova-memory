from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
from dnmem.extract_x3 import crossing_interval, x3_fitted_episodes
from dnmem.extract_x4 import _quantile, causal_confirmations, crossing_posterior, x4_episodes
from dnmem.x3_validation_score import causal_confirmation_emissions as a04e_wrapper
from test_extract import obs
from test_extract_x3 import light_curve


def interval(points):
    comps = crossing_posterior(points, 10.0, 1, (0.35, 0.45))
    return _quantile(comps, 0.005), _quantile(comps, 0.995)


class CrossingFloorTests(unittest.TestCase):
    def test_systematic_floor_keeps_dense_intervals_from_collapsing(self):
        points = [(48 + 0.05 * k, 10 + 0.4 * (48 + 0.05 * k - 50)) for k in range(81)]
        x3_lo, x3_hi = crossing_interval(points, 10.0, 1, (0.35, 0.45))
        x4_lo, x4_hi = interval(points)
        self.assertLess(x4_lo, 50.0)
        self.assertGreater(x4_hi, 50.0)
        self.assertGreater(x4_hi - x4_lo, 1.5 * (x3_hi - x3_lo))
        self.assertGreater(x4_hi - x4_lo, 2 * 2.5 * 0.05 / 0.4)


class SingleObserverTests(unittest.TestCase):
    def test_one_observer_on_several_nights_confirms(self):
        rows = light_curve(observers="a")
        self.assertFalse(x3_fitted_episodes(rows)[0]["confirmed_event"])
        (episode,) = x4_episodes(rows)
        self.assertTrue(episode["confirmed_event"])
        self.assertEqual(episode["confirmation"], "single_observer")
        self.assertNotIn("confirmed", episode)

    def test_contradicting_faint_observer_blocks_single_observer_confirmation(self):
        rows = light_curve(observers="a") + [obs(105.65, 11.6, "z")]
        (episode,) = x4_episodes(rows)
        self.assertFalse(episode["confirmed_event"])

    def test_one_bright_night_is_not_enough(self):
        rows = [obs(100.6 + d, 12.0, "a") for d in range(10)] + [obs(110.6, 8.6, "a")]
        rows += [obs(111.6 + d, 12.0, "a") for d in range(10)]
        self.assertFalse(any(e["confirmed_event"] for e in x4_episodes(rows)))


class CausalConfirmationTests(unittest.TestCase):
    def test_one_emission_after_the_end(self):
        (emission,) = causal_confirmations(light_curve())
        self.assertGreater(emission["emitted_at"], 112.0)
        self.assertLess(emission["bright_first_at"], 112.0)

    def test_near_threshold_tail_noise_cannot_rearm(self):
        rows = light_curve() + [obs(114.62, 9.9, "d"), obs(114.64, 9.95, "e"),
                                obs(115.9, 11.6, "d"), obs(115.92, 11.6, "e")]
        self.assertEqual(len(a04e_wrapper(rows)), 2)
        self.assertEqual(len(causal_confirmations(rows)), 1)

    def test_single_observer_strong_on_two_nights_arms(self):
        self.assertEqual(len(causal_confirmations(light_curve(observers="a"))), 0)
        rows = light_curve(observers="a") + [obs(113.7 + d, 11.8, "b") for d in range(6)]
        (emission,) = causal_confirmations(rows)
        self.assertEqual(emission["strong_bright_observer_count"], 1)


if __name__ == "__main__":
    unittest.main()
