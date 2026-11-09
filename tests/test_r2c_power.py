import math
from pathlib import Path
import sys
import unittest

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import r2c_power as power


class ScoreLevelPlanningTests(unittest.TestCase):
    def test_iterated_cap_and_permutation(self):
        counts = np.array([600, 300, 50, 50])
        actual = power.capped_star_weights(counts)
        np.testing.assert_allclose(actual, [.4, .4, .1, .1])
        order = np.array([2, 0, 3, 1])
        np.testing.assert_allclose(power.capped_star_weights(counts[order]), actual[order])
        with self.assertRaises(ValueError):
            power.capped_star_weights([2, 1])

    def test_exact_density_ratio_and_zero_nesting(self):
        x = np.array([-2., -.1, 0., .7, 3.])
        y = np.array([.3, -1., 2., .8, -1.])
        baseline = np.array([.1, -.2, .3, -.4, .5])
        coefficient = .17
        expected = norm.logpdf(y, baseline + coefficient * x) - norm.logpdf(y, baseline)
        np.testing.assert_allclose(power.paired_scores(x, y, baseline, coefficient), expected, atol=1e-15)
        np.testing.assert_array_equal(power.paired_scores(x, y, baseline, 0.), np.zeros_like(x))

    def test_weighted_cluster_estimator_independent_scalar(self):
        counts = np.array([12, 6, 6])
        weights = power.capped_star_weights(counts)
        star = np.repeat(np.arange(3), counts)
        block = np.concatenate([np.arange(c) * 6 // c for c in counts])
        scores = np.arange(24, dtype=float) / 100 - .1
        estimate = sum(float(w) * float(np.mean(scores[star == s])) for s, w in enumerate(weights))
        sums = [sum(float(weights[s] / counts[s]) * (float(g) - estimate)
                    for g in scores[(star == s) & (block == b)]) for s in range(3) for b in range(6)]
        se = math.sqrt(18 / 17 * sum(value * value for value in sums))
        actual = power.weighted_cr1(scores, star, block, counts, weights)
        self.assertAlmostEqual(actual["estimate"], estimate, places=15)
        self.assertAlmostEqual(actual["se"], se, places=15)

    def test_fit_boundary_and_no_future_input(self):
        x = np.array([-2., -1., 1., 2.])
        self.assertEqual(power.positive_offset(x, -.2 * x), 0.)
        self.assertAlmostEqual(power.positive_offset(x, .3 * x), .3)

    def test_effect_dependent_score_variance_from_normal_quadrature(self):
        nodes, weights = np.polynomial.hermite.hermgauss(8)
        x, error = np.meshgrid(math.sqrt(2) * nodes, math.sqrt(2) * nodes)
        mass = np.outer(weights, weights) / math.pi
        effect = .2
        scores = power.paired_scores(x, effect * x + error, 0., effect)
        mean = float(np.sum(mass * scores))
        variance = float(np.sum(mass * (scores - mean) ** 2))
        self.assertAlmostEqual(mean, effect ** 2 / 2, places=14)
        self.assertAlmostEqual(variance, effect ** 2 + effect ** 4 / 2, places=14)

    def test_counts_seed_and_declared_heterogeneity(self):
        self.assertEqual(sum(power.event_counts(1100, 7, "balanced")), 1100)
        self.assertEqual(power.seed_for("example", 3), power.seed_for("example", 3))
        self.assertNotEqual(power.seed_for("example", 3), power.seed_for("example", 4))
        effects = power.effect_profile(5, .01, .5)
        self.assertAlmostEqual(float(np.mean(effects ** 2)) / 2, .01)
        self.assertAlmostEqual(float(effects.std() / effects.mean()), .5)


if __name__ == "__main__":
    unittest.main()
