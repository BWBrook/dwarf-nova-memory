import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_a01_effect_size import gaussian_information, known_parameter_score_power


class GaussianScoreFixtureTests(unittest.TestCase):
    def test_density_scores_have_stated_mean_and_variance(self):
        r = 0.13
        variance = 1 - r**2
        nodes = ((-math.sqrt(3), 1/6), (0.0, 2/3), (math.sqrt(3), 1/6))
        scores = []
        for x, wx in nodes:
            for error, we in nodes:
                y = r * x + math.sqrt(variance) * error
                log_baseline = -0.5 * math.log(2 * math.pi) - y**2 / 2
                log_expanded = -0.5 * math.log(2 * math.pi * variance) - (y - r * x)**2 / (2 * variance)
                scores.append((log_expanded - log_baseline, wx * we))
        mean = sum(value * weight for value, weight in scores)
        actual_variance = sum((value - mean)**2 * weight for value, weight in scores)
        self.assertAlmostEqual(mean, gaussian_information(r), places=14)
        self.assertAlmostEqual(actual_variance, r**2, places=14)
        with self.assertRaises(ValueError):
            known_parameter_score_power(0, 470)


if __name__ == "__main__":
    unittest.main()
