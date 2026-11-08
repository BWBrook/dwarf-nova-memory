import math
from pathlib import Path
import random
import statistics as st
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from a04i_predictive_gate import check_block, f_sf, hotelling_prediction_f


def gaussian_replicates(dimension, seed, correlated=False):
    rng = random.Random(seed)
    names = tuple(f"x{index}" for index in range(dimension))
    replicates = []
    for _ in range(150):
        shared = rng.gauss(0.0, 1.0)
        values = []
        for index in range(dimension):
            if correlated and index < 2:
                values.append(shared + rng.gauss(0.0, 0.15))
            else:
                values.append(rng.gauss(0.0, 1.0))
        replicates.append(dict(zip(names, values)))
    return names, replicates


class FReferenceTests(unittest.TestCase):
    def test_direct_upper_tail_matches_r_reference_quantiles(self):
        references = (
            (4, 146, 3.4503203196008134),
            (8, 142, 2.6388556008726409),
            (12, 138, 2.3160766492496103),
        )
        for d1, d2, quantile in references:
            with self.subTest(d1=d1, d2=d2):
                self.assertAlmostEqual(f_sf(quantile, d1, d2), 0.01, places=13)

    def test_one_new_vector_scaling_matches_r_critical_values(self):
        references = (
            (4, 14.1787683782, 3.4503203196008134),
            (8, 22.2991970569, 2.6388556008726409),
        )
        for dimension, q_critical, f_critical in references:
            with self.subTest(dimension=dimension):
                self.assertAlmostEqual(
                    hotelling_prediction_f(q_critical, 150, dimension), f_critical, places=10
                )


class PredictiveGateTests(unittest.TestCase):
    def test_typical_vectors_pass_actual_block_dimensions(self):
        for dimension in (8, 4):
            names, replicates = gaussian_replicates(dimension, 100 + dimension)
            means = {name: st.fmean(row[name] for row in replicates) for name in names}
            real = {name: means[name] + 0.1 for name in names}
            result = check_block(real, replicates, names)
            with self.subTest(dimension=dimension):
                self.assertTrue(result["valid"])
                self.assertTrue(result["qualified"])
                self.assertEqual(result["dimension"], dimension)
                self.assertEqual(result["f_df2"], 150 - dimension)

    def test_correlation_break_fails_jointly_without_marginal_failure(self):
        names, replicates = gaussian_replicates(8, 8, correlated=True)
        means = {name: st.fmean(row[name] for row in replicates) for name in names}
        real = dict(means)
        real[names[0]] += 1.5
        real[names[1]] -= 1.5
        result = check_block(real, replicates, names)
        self.assertTrue(result["valid"])
        self.assertFalse(result["joint_pass"])
        self.assertTrue(result["marginal_pass"])
        self.assertFalse(result["qualified"])

    def test_raw_z_above_cap_fails_even_when_display_rounds_to_cap(self):
        names, replicates = gaussian_replicates(8, 4)
        means = {name: st.fmean(row[name] for row in replicates) for name in names}
        sds = {name: st.stdev(row[name] for row in replicates) for name in names}
        real = dict(means)
        real[names[0]] += 3.304 * sds[names[0]]
        result = check_block(real, replicates, names)
        self.assertTrue(result["joint_pass"])
        self.assertGreater(result["z_raw"][names[0]], 3.3)
        self.assertEqual(result["display"]["z"][names[0]], 3.3)
        self.assertFalse(result["marginal_pass"])
        self.assertFalse(result["qualified"])

    def test_fewer_than_150_replicates_fails_closed(self):
        names, replicates = gaussian_replicates(4, 44)
        result = check_block({name: 0.0 for name in names}, replicates[:-1], names)
        self.assertFalse(result["valid"])
        self.assertFalse(result["qualified"])
        self.assertIn("at least 150", result["reason"])

    def test_missing_and_nonfinite_values_fail_closed(self):
        names, replicates = gaussian_replicates(4, 45)
        missing = [dict(row) for row in replicates]
        del missing[0][names[0]]
        result = check_block({name: 0.0 for name in names}, missing, names)
        self.assertFalse(result["valid"])
        self.assertIn("missing statistic", result["reason"])

        nonfinite = [dict(row) for row in replicates]
        nonfinite[0][names[0]] = math.nan
        result = check_block({name: 0.0 for name in names}, nonfinite, names)
        self.assertFalse(result["valid"])
        self.assertIn("finite numeric", result["reason"])

        result = check_block({**{name: 0.0 for name in names}, names[0]: math.inf}, replicates, names)
        self.assertFalse(result["valid"])
        self.assertIn("finite numeric", result["reason"])

    def test_zero_variance_and_singular_covariance_fail_closed(self):
        names, replicates = gaussian_replicates(4, 46)
        constant = [dict(row) for row in replicates]
        for row in constant:
            row[names[0]] = 1.0
        result = check_block({name: 0.0 for name in names}, constant, names)
        self.assertFalse(result["valid"])
        self.assertIn("positive finite replicate variance", result["reason"])

        singular = []
        for index, row in enumerate(replicates):
            item = dict(row)
            item[names[1]] = 2.0 * item[names[0]]
            singular.append(item)
        result = check_block({name: float(index) for index, name in enumerate(names)}, singular, names)
        self.assertFalse(result["valid"])
        self.assertTrue("singular" in result["reason"] or "ill-conditioned" in result["reason"])

    def test_numerically_ill_conditioned_covariance_fails_closed(self):
        rng = random.Random(47)
        names = tuple(f"x{index}" for index in range(4))
        replicates = []
        for _ in range(150):
            base = rng.gauss(0.0, 1.0)
            replicates.append(
                {
                    names[0]: base,
                    names[1]: base + 1.0e-6 * rng.gauss(0.0, 1.0),
                    names[2]: rng.gauss(0.0, 1.0),
                    names[3]: rng.gauss(0.0, 1.0),
                }
            )
        result = check_block({name: 0.0 for name in names}, replicates, names)
        self.assertFalse(result["valid"])
        self.assertTrue("singular" in result["reason"] or "ill-conditioned" in result["reason"])


if __name__ == "__main__":
    unittest.main()
