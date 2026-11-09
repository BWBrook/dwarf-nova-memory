import copy
import math
from pathlib import Path
import sys
import unittest

import numpy as np
from scipy.stats import norm, t as student_t

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dnmem.r2d_simulation import (allocate_counts, capped_star_weights, causal_level_shift,
                                  fit_star, forecast_trial, generate_histories,
                                  positive_pooled_offset, recent_mark_center, trial, weighted_cr1)


class GuardTests(unittest.TestCase):
    def test_centering_uses_only_previous_available_marks_and_minimum_count(self):
        mark = np.array([0., 1., np.nan, 2., 5., 6., 7., 8.])
        z, usable, transform = recent_mark_center(mark, 5, window=3, minimum=3)
        self.assertFalse(usable[:4].any())
        self.assertTrue(usable[4])
        expected = (5. - np.mean([0., 1., 2.])) / transform["scale"]
        self.assertAlmostEqual(z[4], expected)
        changed = mark.copy(); changed[6:] = 100000.
        checked, _, changed_transform = recent_mark_center(changed, 5, window=3, minimum=3)
        np.testing.assert_array_equal(z[:6], checked[:6])
        self.assertEqual(transform, changed_transform)

    def test_recalibration_waits_for_report_availability_not_target_resolution(self):
        issue = np.array([0., 10., 20., 30.])
        available = np.array([15., 25., 35., 45.])
        residual = np.array([1., 3., 7., 100.])
        shift, count = causal_level_shift(issue, available, residual, window=2)
        np.testing.assert_array_equal(shift, [0., 0., 1., 2.])
        np.testing.assert_array_equal(count, [0, 0, 1, 2])
        changed = residual.copy(); changed[2:] = -9999.
        np.testing.assert_array_equal(shift, causal_level_shift(issue, available, changed, window=2)[0])

    def test_out_of_order_report_arrivals_use_latest_eligible_forecast_indices(self):
        issue = np.array([0., 10., 20., 30., 40.])
        available = np.array([35., 15., 25., 45., 50.])
        residual = np.array([100., 2., 6., 11., 15.])
        shift, count = causal_level_shift(issue, available, residual, window=2)
        np.testing.assert_array_equal(shift, [0., 0., 2., 4., 4.])
        np.testing.assert_array_equal(count, [0, 0, 1, 2, 2])

    def test_impossible_availability_is_rejected(self):
        with self.assertRaises(ValueError):
            causal_level_shift([0., 10.], [0., 11.], [1., 1.])
        history = generate_histories({"stars": 3, "test_forecasts": 90, "development_per_star": 30},
                                     np.random.default_rng(122))[0]
        history["outcome_available_at"][5] = history["issue"][5] + .001
        with self.assertRaises(ValueError):
            fit_star(history)


class SequentialModelTests(unittest.TestCase):
    def setUp(self):
        self.config = {"stars": 3, "test_forecasts": 120, "development_per_star": 50,
                       "nominal_oracle_gain": .004, "outcome_delay_days": 30.,
                       "outcome_delay_probability": .2}
        self.histories = generate_histories(self.config, np.random.default_rng(41235))

    def test_development_refit_and_offset_ignore_all_future_labels_and_marks(self):
        original = forecast_trial(self.histories)
        poisoned = copy.deepcopy(self.histories)
        for h in poisoned:
            first = h["development_n"]
            h["y"][first:] += .5
            h["mark"][first:] = 10000.
            h["outcome_available_at"][first:] = h["issue"][first:] + np.exp(h["y"][first:]) + 100.
        changed = forecast_trial(poisoned)
        self.assertEqual(original["beta"], changed["beta"])
        for a, b in zip(original["fitted"], changed["fitted"]):
            self.assertEqual(a["model"], b["model"])
            first = a["history"]["development_n"]
            np.testing.assert_array_equal(a["baseline_mean"][:first], b["baseline_mean"][:first])

    def test_scores_and_score_derivative_match_independent_normal_probabilities(self):
        result = forecast_trial(self.histories)
        cursor = 0
        for star in result["fitted"]:
            first = star["history"]["development_n"]
            y = star["history"]["y"][first:]
            mu, variance, z = star["baseline_mean"][first:], star["variance"][first:], star["z"][first:]
            shift = result["beta"] * z
            gain = norm.logpdf(y, loc=mu + shift, scale=np.sqrt(variance)) - norm.logpdf(y, loc=mu, scale=np.sqrt(variance))
            np.testing.assert_allclose(result["gain"][cursor:cursor+len(y)], gain, rtol=0, atol=1e-12)
            epsilon = 1e-5
            derivative = (norm.logpdf(y, loc=mu+epsilon*z, scale=np.sqrt(variance)) -
                          norm.logpdf(y, loc=mu-epsilon*z, scale=np.sqrt(variance))) / (2*epsilon)
            np.testing.assert_allclose(result["score"][cursor:cursor+len(y)], derivative, rtol=0, atol=1e-8)
            cursor += len(y)

    def test_missing_marks_produce_exact_gain_and_score_identity(self):
        result, vectors = trial({**self.config, "missing_mark_fraction": 1.}, 983, return_vectors=True)
        self.assertEqual(result["beta_hat"], 0.)
        self.assertTrue(result["gain_identity"])
        np.testing.assert_array_equal(vectors["gain"], np.zeros(120))
        np.testing.assert_array_equal(vectors["score"], np.zeros(120))
        self.assertFalse(result["methods"]["star"]["gain"]["reject_one_sided"])

    def test_oracle_control_has_true_null_mean_variance_and_no_estimated_level_step(self):
        config = {**self.config, "nominal_oracle_gain": 0., "oracle_base": True,
                  "level_shift": -.5, "shared_state_loading": .4, "residual_ar": .3}
        result, vectors = trial(config, 1129, return_vectors=True)
        for star in vectors["fitted"]:
            np.testing.assert_array_equal(star["baseline_mean"], star["history"]["true_mean"])
            np.testing.assert_array_equal(star["variance"], star["history"]["innovation_variance"])
            np.testing.assert_array_equal(star["level_shift"], np.zeros(len(star["level_shift"])))
        self.assertAlmostEqual(result["conditional_expected_score"], 0.)
        self.assertLessEqual(result["conditional_expected_gain"], 0.)

    def test_development_effect_overshoot_can_have_positive_score_and_negative_gain(self):
        config = {"stars": 3, "test_forecasts": 600, "development_per_star": 300,
                  "nominal_oracle_gain": .004, "development_effect_multiplier": 4.,
                  "guard_marks": False, "oracle_base": True}
        result = trial(config, 9841)
        self.assertGreater(result["conditional_expected_score"], 0.)
        self.assertLess(result["conditional_expected_gain"], 0.)

    def test_heterogeneous_signs_and_shared_state_are_not_mislabeled_predictive_nulls(self):
        config = {**self.config, "nominal_oracle_gain": 0., "shared_state_loading": .7,
                  "null_class": "no_direct_effect_shared_state", "effect_profile": [1., 0., -1.]}
        result = trial(config, 7441)
        self.assertEqual(result["scientific_null_class"], "no_direct_effect_shared_state")
        self.assertTrue(result["direct_effect_zero"])
        self.assertIn("realized-path", result["expected_target"])
        self.assertEqual(result["nominal_direct_oracle_gain"], 0.)
        generated = generate_histories({**self.config, "effect_profile": [1., 0., -1.]}, np.random.default_rng(125))
        self.assertGreater(generated[0]["direct_beta"], 0.)
        self.assertEqual(generated[1]["direct_beta"], 0.)
        self.assertLess(generated[2]["direct_beta"], 0.)

    def test_seed_reproduction_and_expected_gain_algebra(self):
        a, vector = trial(self.config, 902, return_vectors=True)
        self.assertEqual(a, trial(self.config, 902))
        rng = np.random.default_rng(993)
        true_mean, base_mean, shift, sd = .3, -.1, .2, .5
        y = rng.normal(true_mean, sd, 50000)
        observed = norm.logpdf(y, base_mean + shift, sd) - norm.logpdf(y, base_mean, sd)
        expected = shift * (true_mean - base_mean) / sd**2 - .5 * shift**2 / sd**2
        self.assertLess(abs(observed.mean() - expected), 6 * observed.std() / math.sqrt(len(y)))
        self.assertEqual(len(vector["gain"]), self.config["test_forecasts"])


class InferenceTests(unittest.TestCase):
    def test_development_pooling_caps_large_stars_and_requires_three_contributors(self):
        def star(n, residual, usable=True):
            return {"training": np.ones(n, dtype=bool), "mark_usable": np.full(n, usable),
                    "z": np.ones(n), "history": {"y": np.full(n, residual)},
                    "baseline_mean": np.zeros(n), "variance": np.ones(n)}
        stars = [star(10, 1.), star(10, 1.), star(10, 1.), star(100, 10.)]
        self.assertAlmostEqual(positive_pooled_offset(stars), 4.6)
        self.assertEqual(positive_pooled_offset([star(10, 1.), star(10, 1.), star(10, 1., False)]), 0.)
        self.assertEqual(positive_pooled_offset([star(10, 10.)] * 3), 10.)

    def test_normalized_cap_and_allocation_are_exact(self):
        weights = capped_star_weights([600, 100, 100, 100, 100])
        self.assertAlmostEqual(weights.sum(), 1.)
        self.assertLessEqual(weights.max(), .4)
        self.assertEqual(weights[0], .4)
        self.assertEqual(allocate_counts(1100, 5).sum(), 1100)
        with self.assertRaises(ValueError):
            capped_star_weights([100, 100])

    def test_cluster_variance_matches_independent_group_arithmetic(self):
        values = np.array([-1., 0., 1., 2., 0., 1., 2., 3., 1., 2., 3., 4.])
        stars = np.repeat(np.arange(3), 4)
        epochs = np.tile([0, 1, 3, 5], 3)
        result = weighted_cr1(values, stars, epochs)
        mean = values.mean()
        sums = [sum(values[(stars == s) & ((epochs // 3) == half)] - mean) / len(values)
                for s in range(3) for half in range(2)]
        expected_se = math.sqrt(6 / 5 * sum(x*x for x in sums))
        self.assertAlmostEqual(result["se"], expected_se)
        self.assertAlmostEqual(result["lower90"], mean - student_t.ppf(.95, 5) * expected_se)
        permutation = np.array([10, 3, 2, 0, 9, 4, 5, 7, 8, 6, 11, 1])
        permuted = weighted_cr1(values[permutation], stars[permutation], epochs[permutation])
        for key in ("estimate", "se", "lower90", "upper90", "statistic", "maximum_star_weight"):
            self.assertAlmostEqual(result[key], permuted[key], delta=1e-12)
        for key in ("reject_one_sided", "clusters", "df", "zero_variance", "clustering"):
            self.assertEqual(result[key], permuted[key])

    def test_zero_variance_is_explicit_not_a_fabricated_finite_t_statistic(self):
        result = weighted_cr1(np.zeros(18), np.repeat(np.arange(3), 6), np.tile(np.arange(6), 3))
        self.assertTrue(result["zero_variance"])
        self.assertIsNone(result["statistic"])
        self.assertFalse(result["reject_one_sided"])


if __name__ == "__main__":
    unittest.main()
