from pathlib import Path
import random
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from a04h_morphology_targets import betainc, check, f_sf, spearman


class DistributionTests(unittest.TestCase):
    def test_incomplete_beta_and_f_tail(self):
        self.assertAlmostEqual(betainc(2, 3, 0.4), 0.5248, places=4)
        self.assertAlmostEqual(f_sf(3.8415, 1, 1e7), 0.05, places=3)
        self.assertAlmostEqual(f_sf(2.5191, 10, 90), 0.01, places=3)

    def test_spearman_uses_average_ranks(self):
        self.assertAlmostEqual(spearman([(1, 1), (2, 2), (3, 2), (4, 3)]), 0.9487, places=4)


class PredictiveCheckTests(unittest.TestCase):
    def setUp(self):
        rng = random.Random(1)
        self.names = ("a", "b", "c")
        self.reps = []
        for _ in range(200):
            shared = rng.gauss(0, 1)
            self.reps.append({"a": shared + rng.gauss(0, 0.5), "b": shared + rng.gauss(0, 0.5), "c": rng.gauss(0, 1)})

    def test_typical_real_vector_passes(self):
        result = check({"a": 0.3, "b": 0.2, "c": -0.4}, self.reps, self.names)
        self.assertTrue(result["pass"])

    def test_vector_breaking_the_correlation_fails_jointly_but_not_marginally(self):
        result = check({"a": 1.6, "b": -1.6, "c": 0.0}, self.reps, self.names)
        self.assertTrue(result["marginal_pass"])
        self.assertFalse(result["joint_pass"])

    def test_joint_gate_rejects_about_one_percent_of_draws_from_the_same_process(self):
        rng = random.Random(2)
        rejections = 0
        for _ in range(300):
            shared = rng.gauss(0, 1)
            real = {"a": shared + rng.gauss(0, 0.5), "b": shared + rng.gauss(0, 0.5), "c": rng.gauss(0, 1)}
            rejections += not check(real, self.reps, self.names)["joint_pass"]
        self.assertLessEqual(rejections, 10)

    def test_single_large_shift_fails_marginally(self):
        result = check({"a": 0.0, "b": 0.0, "c": 4.0}, self.reps, self.names)
        self.assertFalse(result["marginal_pass"])


if __name__ == "__main__":
    unittest.main()
