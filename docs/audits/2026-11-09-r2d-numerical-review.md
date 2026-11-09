# Independent R2d precision audit

{
  "status": "passed",
  "cases_checked": 35,
  "unique_seeds": 70000,
  "counts": {
    "logical_checks": 3858056,
    "trial_rows": 70000
  },
  "representatives": [
    {
      "case": "common-delayed-s8-effect",
      "replicate": 0,
      "seed": 15963477226494849907,
      "forecasts": 1100,
      "sign_flip_p": 0.40625
    },
    {
      "case": "core-s8-n1100-effect",
      "replicate": 0,
      "seed": 18402721014457594029,
      "forecasts": 1100,
      "sign_flip_p": 0.015625
    },
    {
      "case": "oracle-s4-persistent",
      "replicate": 0,
      "seed": 3233342904271554655,
      "forecasts": 1100,
      "sign_flip_p": 0.125
    },
    {
      "case": "specificity-development-overshoot",
      "replicate": 0,
      "seed": 9468254381196293068,
      "forecasts": 1100,
      "sign_flip_p": 0.0625
    }
  ],
  "maximum_absolute_errors": {
    "aggregate": 7.216449660063518e-16,
    "trial_algebra": 3.469446951953614e-17,
    "trial_interval": 2.7755575615628914e-17,
    "mc_interval": 2.7755575615628914e-15,
    "representative": 7.105427357601002e-14
  },
  "failures": [],
  "current_checkout_drift": [
    {
      "path": "tests/test_r2d_simulation.py",
      "classification": "test-only",
      "frozen_sha256": "500ed89e46683e8f6fbd1c7f94d097efedf7cf5f1b9eeb6b421ad08ca38db498",
      "current_sha256": "056128948fa5975a5473f47ef91ad4f55a1bdc0710b82415cfcdc38bfe9756b9",
      "diff": "--- freeze/tests/test_r2d_simulation.py\n+++ checkout/tests/test_r2d_simulation.py\n@@ -176,7 +176,11 @@\n         self.assertAlmostEqual(result[\"se\"], expected_se)\n         self.assertAlmostEqual(result[\"lower90\"], mean - student_t.ppf(.95, 5) * expected_se)\n         permutation = np.array([10, 3, 2, 0, 9, 4, 5, 7, 8, 6, 11, 1])\n-        self.assertEqual(result, weighted_cr1(values[permutation], stars[permutation], epochs[permutation]))\n+        permuted = weighted_cr1(values[permutation], stars[permutation], epochs[permutation])\n+        for key in (\"estimate\", \"se\", \"lower90\", \"upper90\", \"statistic\", \"maximum_star_weight\"):\n+            self.assertAlmostEqual(result[key], permuted[key], delta=1e-12)\n+        for key in (\"reject_one_sided\", \"clusters\", \"df\", \"zero_variance\", \"clustering\"):\n+            self.assertEqual(result[key], permuted[key])\n \n     def test_zero_variance_is_explicit_not_a_fabricated_finite_t_statistic(self):\n         result = weighted_cr1(np.zeros(18), np.repeat(np.arange(3), 6), np.tile(np.arange(6), 3))\n"
    }
  ]
}

- Full-grid SEs are checked from saved estimate/SE/cluster metadata; raw vector CR1 is independently rebuilt for four representative trials only.
- Representative raw generator histories come from same-seed candidate reruns; the RNG/DGP itself is not independently regenerated.
- Exact Monte Carlo intervals are inverted binomial tails and are per-cell, not simultaneous guarantees.
- Predictable target is conditional on the realized generator path and frozen forecasts, not unconditional long-run KL or actual astronomical forecast gain.
