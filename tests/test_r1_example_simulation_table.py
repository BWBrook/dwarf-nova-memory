from pathlib import Path
import math
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from r1_example_simulation_table import (ORIGIN, WIDTH, binomial_interval,
                                         real_interval, recompute_reference,
                                         remaining_cdf, remaining_median)


class R1IndependentScalarChecks(unittest.TestCase):
    def test_zero_observed_confirmations_do_not_certify_zero_probability(self):
        interval = binomial_interval(0, 40)
        self.assertEqual(interval["rate_mc_se"], 0.0)
        self.assertAlmostEqual(interval["exact_upper95"], 1 - .025 ** (1 / 40), places=14)
        self.assertAlmostEqual(interval["one_sided_upper95"], 1 - .05 ** (1 / 40), places=14)
        self.assertGreater(interval["one_sided_upper95"], .05)

    def test_one_trial_exact_binomial_edges(self):
        zero, one = binomial_interval(0, 1), binomial_interval(1, 1)
        self.assertAlmostEqual(zero["exact_upper95"], .975)
        self.assertAlmostEqual(one["exact_lower95"], .025)
        self.assertEqual(one["exact_upper95"], 1.0)

    def test_conditional_median_uses_survival_to_issue(self):
        location, sigma, age = math.log(10), .4, 10.0
        known_normal_third_quartile = .6744897501960817
        expected = 10 * math.exp(sigma * known_normal_third_quartile) - age
        calculated = remaining_median(age, location, sigma)
        self.assertAlmostEqual(calculated, expected, places=12)
        self.assertAlmostEqual(remaining_cdf(calculated, age, location, sigma), .5, places=14)
        self.assertEqual(remaining_cdf(0.0, age, location, sigma), 0.0)
        self.assertGreater(calculated, 0.0)

    def test_half_day_origin_error_can_change_cluster_arithmetic(self):
        rows = [{"issue_time": ORIGIN + WIDTH - .25, "gain": 1.0},
                {"issue_time": ORIGIN + WIDTH + .25, "gain": 10.0},
                {"issue_time": ORIGIN + 2 * WIDTH - .25, "gain": 100.0}]
        result = real_interval(rows)
        self.assertEqual((result["n"], result["blocks"], result["mean"]), (3, 2, 37.0))
        known_df1_t95 = math.tan(.45 * math.pi)
        self.assertAlmostEqual(result["lower90"], 37 - 24 * known_df1_t95, places=8)
        self.assertAlmostEqual(result["upper90"], 37 + 24 * known_df1_t95, places=8)

    def test_nonzero_interval_cannot_be_an_analytic_zero_identity(self):
        counterfeit = {"intervals": {"primary": {"6": {"gain_M3_M2": {"estimate": .1, "se": 0}}}},
                       "reference_calibration": {"6": {}}, "reference_replicas": [],
                       "models": {"primary": {"models": {"M3": {"coefficients": {"beta": 0.0}}}}}}
        with self.assertRaises(ValueError):
            recompute_reference(counterfeit, "6", [], "synthetic counterfeit")


if __name__ == "__main__":
    unittest.main()
