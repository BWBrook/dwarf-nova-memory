import copy
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np
from scipy.optimize import OptimizeResult

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dnmem.r2_models import ConditionalClock, TimingRule
from dnmem.r2b_models import R2bRule, fit_bases, fit_mark, local_lag_index, optimize, training_pairs


def fixture(n=32):
    rng = np.random.default_rng(72691)
    rows, evidence = [], []
    for i in range(n):
        anchor = 1000. + 100 * i
        history = [3.5 + .2 * math.sin(i + j) for j in range(6)]
        mark = math.exp(2.4 + .3 * math.sin(i))
        cadence = .7 + .5 * math.cos(i)
        wait = math.exp(3.5 + .15 * math.sin(i) + .15 * math.cos(i) + .2 * rng.normal())
        rows.append({"emission_index": i, "issue_time": anchor + 1., "available_at": anchor + 1.,
                     "clock_anchor": anchor, "mark": mark, "previous_gap": math.exp(history[-1]),
                     "previous_gap_covered": True,
                     "gap_history": [{"log_gap": value, "available_at": anchor} for value in history],
                     "cadence_end": {"value_days": cadence, "available_at": anchor},
                     "flux_proxy": {"value_threshold_flux_days": mark * 2, "available_at": anchor},
                     "observer_rate": {"value_per_day": 1. + .2 * math.sin(i), "available_at": anchor}})
        evidence.append({"emission_index": i, "issue_time": anchor + 1., "kind": "point",
                         "onset_t": anchor + wait, "computed_as_of": 10000., "evidence_available_at": 10000.})
    return rows, evidence


class R2bModelsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.evidence = fixture()
        cls.base = fit_bases(cls.rows, cls.evidence, 10000., rungs=("B0",))["B0"]
        cls.cadence = fit_bases(cls.rows, cls.evidence, 10000., include_cadence=True, rungs=("B0",))["B0"]

    def test_fixed_baseline_offsets_preserve_timing_and_all_zero_missing_routes(self):
        for marker in ("duration", "flux", "rate"):
            rule = fit_mark(self.base, self.rows, self.evidence, 10000., marker)
            self.assertEqual(rule.timing, self.base.timing)
            self.assertGreaterEqual(rule.beta, 0.)
            zero = R2bRule.from_dict({**rule.to_dict(), "beta": 0.})
            for original in self.rows[:3]:
                self.assertEqual(zero.predict(original), zero.predict(original, True))
                row = copy.deepcopy(original)
                row["mark"] = None
                row["flux_proxy"]["value_threshold_flux_days"] = None
                row["observer_rate"]["value_per_day"] = None
                self.assertEqual(rule.predict(row), rule.predict(row, True))
                row["clock_anchor"] = None
                self.assertEqual(rule.predict(row), rule.predict(row, True))

    def test_cadence_is_fitted_in_both_arms_and_missing_cadence_is_centered(self):
        self.assertIsNotNone(self.cadence.cadence_transform)
        rule = fit_mark(self.cadence, self.rows, self.evidence, 10000.)
        self.assertEqual(rule.cadence_beta, self.cadence.cadence_beta)
        row = copy.deepcopy(self.rows[1])
        row["cadence_end"]["value_days"] = None
        clock, _ = self.cadence.predict(row)
        expected, _ = self.cadence.timing.predict(row)
        self.assertEqual(clock, expected)
        self.assertTrue(math.isfinite(rule.predict(row, True)[0].log_density(self.evidence[1]["onset_t"])))

    def test_rejects_future_covariates_marks_and_training_support(self):
        row = copy.deepcopy(self.rows[0])
        row["cadence_end"]["available_at"] = row["issue_time"] + 1
        with self.assertRaises(ValueError):
            self.cadence.predict(row)
        marked = fit_mark(self.base, self.rows, self.evidence, 10000., "rate")
        row = copy.deepcopy(self.rows[1])
        row["observer_rate"]["available_at"] = row["issue_time"] + 1
        if marked.beta == 0:
            marked = R2bRule.from_dict({**marked.to_dict(), "beta": .1})
        with self.assertRaises(ValueError):
            marked.predict(row, True)
        evidence = copy.deepcopy(self.evidence)
        evidence[0]["onset_t"] = 10001.
        with self.assertRaises(ValueError):
            training_pairs(self.rows, evidence, 10000.)

    def test_multistart_disagreement_and_failed_starts_are_retained(self):
        fits = [OptimizeResult(x=np.array([x]), fun=y, jac=np.array([0.]), success=ok,
                               message="fixture", nit=1) for x, y, ok in [(0., 2., True), (1., 3., True), (2., 9., False)]]
        with patch("dnmem.r2b_models.minimize", side_effect=fits):
            theta, meta = optimize(lambda x: float(x[0]), [[0.], [1.], [2.]], [(-3., 3.)])
        self.assertEqual(theta, [0.])
        self.assertFalse(meta["stable"])
        self.assertEqual(meta["multistart_spread"], 1.)
        self.assertEqual(len(meta["attempts"]), 3)
        self.assertFalse(meta["attempts"][-1]["successful"])

    def test_equivalent_cadence_and_standard_rule_round_trip(self):
        for rule in (self.base, self.cadence):
            restored = R2bRule.from_dict(rule.to_dict())
            self.assertEqual(restored.predict(self.rows[0]), rule.predict(self.rows[0]))
            self.assertEqual(len(rule.metadata["base_fit"]["attempts"]), 2)

    def test_lag_index_uses_absolute_local_derivative_and_is_not_a_bound(self):
        row = copy.deepcopy(self.rows[1])
        row["cadence_on"] = {"value_days": .5, "available_at": row["issue_time"]}
        row["gap_history"][-1].update(left_cadence_end_days=.4, left_cadence_end_available_at=row["issue_time"])
        timing = TimingRule("B0", [3.6, -.2, 0., math.log(.4)], [(3.5, 1., False)] * 2,
                            0., [3.6, .4], [3.6, .4], 0., 1., 0., {})
        rule = R2bRule(timing, None, 0., "duration", 0., 1., 0., {})
        result = local_lag_index(rule, row)
        self.assertAlmostEqual(result["previous_log_gap_derivative"], -.2, places=9)
        self.assertGreaterEqual(result["lag_scale_days"], row["cadence_end"]["value_days"])
        self.assertFalse(result["is_upper_bound"])
        row["cadence_on"]["available_at"] += 1
        with self.assertRaises(ValueError):
            local_lag_index(rule, row)


if __name__ == "__main__":
    unittest.main()
