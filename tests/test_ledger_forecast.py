import math
from pathlib import Path
import sys
import time
import unittest

import numpy as np
from scipy.special import log_ndtr, logsumexp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.ledger_forecast import (
    _log_interval, _make_transform, _node_loglik, _prepare_likelihood,
    _scalar_model_objective, _endpoint_nodes, fit_models,
)


def make_training(n=42, *, seed=11, endpoint_width=0.0):
    rng = np.random.default_rng(seed)
    ledger, evidence = [], []
    for i in range(n):
        end = 20.0 + 12.0 * i
        issue = end + 2.0
        duration = (8.2 if i % 2 == 0 else 14.0) + rng.normal(0, 0.45)
        q = math.exp(3.25 + 0.35 * (math.log(duration) - math.log(11.0)) / 0.45 + rng.normal(0, 0.32))
        onset = end + q
        ledger.append({
            "emission_index": i, "issue_time": issue, "end_t": end,
            "end_lo": end - endpoint_width, "end_hi": end + endpoint_width,
            "onset_t": end - duration, "duration": duration,
            "previous_gap": 18.0 + 0.45 * i,
            "previous_gap_covered": True,
        })
        if i % 7 == 0:
            evidence.append({"emission_index": i, "issue_time": issue,
                             "kind": "right_censored", "censor_at": onset + 3.0,
                             "computed_as_of": 900.0, "evidence_available_at": 900.0})
        else:
            evidence.append({"emission_index": i, "issue_time": issue,
                             "kind": "interval", "onset_lo": onset - 0.15,
                             "onset_hi": onset + 0.15, "computed_as_of": 900.0,
                             "evidence_available_at": 900.0})
    return ledger, evidence


class LedgerForecastTests(unittest.TestCase):
    def test_optimizer_cannot_report_a_penalty_plateau_as_a_fit(self):
        from scipy.optimize import OptimizeResult
        from dnmem.ledger_forecast import _choose_result
        result = OptimizeResult(success=True, x=np.zeros(2), jac=np.zeros(2), fun=1e100,
                                message="penalty plateau")
        with self.assertRaisesRegex(ValueError, "optimization failed"):
            _choose_result([result], "fixture")

    def test_interval_log_difference_matches_scipy_in_tails_and_narrow_windows(self):
        cases = [(1.0e8, 1.0e8 + 1.0, 0.0, 1.0),
                 (1.0e-8, 1.0e-8 * (1.0 + 1.0e-7), 0.0, 1.0),
                 (1.0e5, 1.0e5 + 1.0e-4, 3.0, 0.7)]
        for lower, upper, mu, sigma in cases:
            if lower >= math.exp(mu):
                from scipy.special import log_ndtr
                hi = log_ndtr(-(math.log(lower) - mu) / sigma)
                lo = log_ndtr(-(math.log(upper) - mu) / sigma)
            else:
                from scipy.special import log_ndtr
                hi = log_ndtr((math.log(upper) - mu) / sigma)
                lo = log_ndtr((math.log(lower) - mu) / sigma)
            expected = hi + math.log(-math.expm1(lo - hi))
            self.assertAlmostEqual(_log_interval(lower, upper, mu, sigma), expected, places=12)

    def test_vectorized_likelihood_matches_independent_scalar_likelihood(self):
        ledger, evidence = make_training(endpoint_width=1.0)
        rows = [{"feature": feature, "evidence": ev,
                 "endpoints": _endpoint_nodes(feature, "uniform_end", 5),
                 "model_name": "M1"}
                for feature, ev in zip(ledger, evidence)]
        transform = _make_transform(rows, "M1", "log_duration", {})
        prepared = _prepare_likelihood(rows, ("duration",), transform, "log_duration")
        theta = np.array([3.2, 0.25, math.log(0.4)])
        scalar = _scalar_model_objective(theta, rows, ("duration",), transform, "log_duration")
        self.assertAlmostEqual(prepared.objective(theta), scalar, places=10)

    def test_vectorized_likelihood_handles_mixed_endpoint_node_counts(self):
        ledger, evidence = make_training(3, endpoint_width=1.0)
        theta = np.array([3.2, 0.25, math.log(0.4)])
        for order in ((5, 1, 5), (1, 5, 5)):
            rows = []
            for feature, ev, count in zip(ledger, evidence, order):
                endpoints = (np.linspace(feature["end_lo"], feature["end_hi"], count)
                             if count > 1 else np.array([feature["end_t"]]))
                rows.append({"feature": feature, "evidence": ev,
                             "endpoints": endpoints, "model_name": "M1"})
            transform = _make_transform(rows, "M1", "log_duration", {})
            prepared = _prepare_likelihood(rows, ("duration",), transform, "log_duration")
            scalar = _scalar_model_objective(theta, rows, ("duration",), transform, "log_duration")
            self.assertAlmostEqual(prepared.objective(theta), scalar, places=10)

        # Include a zero-exposure node and a mixed interval/censor row set.
        rows[0]["endpoints"] = np.linspace(ledger[0]["end_t"], ledger[0]["issue_time"], 5)
        rows[0]["evidence"] = dict(evidence[0], kind="right_censored",
                                    censor_at=ledger[0]["issue_time"])
        transform = _make_transform(rows, "M1", "log_duration", {})
        prepared = _prepare_likelihood(rows, ("duration",), transform, "log_duration")
        scalar = _scalar_model_objective(theta, rows, ("duration",), transform, "log_duration")
        self.assertAlmostEqual(prepared.objective(theta), scalar, places=10)

    def test_three_hundred_row_fit_timing_point_and_uniform(self):
        ledger, evidence = make_training(300, endpoint_width=1.0)
        start = time.perf_counter()
        fit_models(ledger, evidence, 20000.0, endpoint_mode="point")
        point_seconds = time.perf_counter() - start
        start = time.perf_counter()
        fit_models(ledger, evidence, 20000.0, endpoint_mode="uniform_end", nodes=5)
        uniform_seconds = time.perf_counter() - start
        self.assertLess(point_seconds, 5.0)
        self.assertLess(uniform_seconds, 5.0)

    def test_fit_and_exact_point_conditioning(self):
        ledger, evidence = make_training()
        bundle = fit_models(ledger, evidence, 2000.0)
        feature, outcome = ledger[4], evidence[4]
        score = bundle.score(feature, outcome, "M0")
        model = bundle.models["M0"]
        age = feature["issue_time"] - feature["end_t"]
        lo = outcome["onset_lo"] - feature["end_t"]
        hi = outcome["onset_hi"] - feature["end_t"]
        mu, sigma = model.intercept, model.sigma
        log_num = log_ndtr((math.log(hi) - mu) / sigma)
        log_num = log_num + math.log1p(-math.exp(log_ndtr((math.log(lo) - mu) / sigma) - log_num))
        expected = log_num - log_ndtr(-(math.log(age) - mu) / sigma)
        self.assertAlmostEqual(score, expected, places=11)

        censored_score = bundle.score(ledger[0], evidence[0], "M3")
        self.assertTrue(math.isfinite(censored_score))
        self.assertGreater(bundle.models["M1"].coefficients["duration"], 0.05)
        self.assertAlmostEqual(bundle.models["M1"].sigma, 0.32, delta=0.18)

    def test_uniform_end_uses_ratio_of_mixtures(self):
        ledger, evidence = make_training(endpoint_width=1.0)
        bundle = fit_models(ledger, evidence, 2000.0, endpoint_mode="uniform_end", nodes=5)
        feature, outcome = ledger[4], evidence[4]
        score = bundle.score(feature, outcome, "M1")
        model = bundle.models["M1"]
        endpoints = np.linspace(feature["end_lo"], feature["end_hi"], 5)
        nums, dens, ratios = [], [], []
        for end in endpoints:
            duration = end - feature["onset_t"]
            x = (math.log(duration) - model.centers["duration"]) / model.scales["duration"]
            mu = model.intercept + model.coefficients["duration"] * x
            lo = outcome["onset_lo"] - end
            hi = outcome["onset_hi"] - end
            age = feature["issue_time"] - end
            log_hi = log_ndtr((math.log(hi) - mu) / model.sigma)
            log_lo = log_ndtr((math.log(lo) - mu) / model.sigma)
            num = log_hi + math.log1p(-math.exp(log_lo - log_hi))
            den = log_ndtr(-(math.log(age) - mu) / model.sigma)
            nums.append(num)
            dens.append(den)
            ratios.append(num - den)
        expected = logsumexp(nums) - logsumexp(dens)
        wrong = float(np.mean(ratios))
        self.assertAlmostEqual(score, expected, places=10)
        self.assertGreater(abs(score - wrong), 1e-8)

    def test_training_cutoff_and_counts_are_strict(self):
        ledger, evidence = make_training()
        with self.assertRaisesRegex(ValueError, "feature.issue_time"):
            fit_models(ledger, evidence, ledger[-1]["issue_time"])
        poisoned = [dict(row) for row in evidence]
        poisoned[-1]["computed_as_of"] = 2001.0
        with self.assertRaisesRegex(ValueError, "computed_as_of"):
            fit_models(ledger, poisoned, 2000.0)
        excluded = dict(evidence[-1], kind="excluded")
        bundle = fit_models(ledger[:-1] + [ledger[-1]], evidence[:-1] + [excluded], 2000.0)
        self.assertEqual(bundle.counts["excluded"], 1)
        self.assertIsNone(bundle.score(ledger[-1], excluded, "M0"))

    def test_missing_mark_fallback_is_exact(self):
        ledger, evidence = make_training()
        bundle = fit_models(ledger, evidence, 2000.0)
        missing_duration = dict(ledger[4], duration=None, onset_t=None)
        self.assertEqual(bundle.route(missing_duration, "M1"), "M0")
        self.assertEqual(bundle.score(missing_duration, evidence[4], "M1"),
                         bundle.score(missing_duration, evidence[4], "M0"))
        missing_previous = dict(ledger[4], previous_gap=None, previous_gap_covered=False)
        self.assertEqual(bundle.route(missing_previous, "M2"), "M0")
        self.assertEqual(bundle.route(missing_previous, "M3"), "M1")
        self.assertEqual(bundle.score(missing_previous, evidence[4], "M2"),
                         bundle.score(missing_previous, evidence[4], "M0"))
        self.assertEqual(bundle.score(missing_previous, evidence[4], "M3"),
                         bundle.score(missing_previous, evidence[4], "M1"))
        both_missing = dict(missing_duration, previous_gap=None, previous_gap_covered=False)
        self.assertEqual(bundle.score(both_missing, evidence[4], "M3"),
                         bundle.score(both_missing, evidence[4], "M0"))

    def test_unknown_endpoint_uses_shared_r0_and_zero_exposure_is_zero(self):
        ledger, evidence = make_training()
        unknown = dict(ledger[4], end_t=None, end_lo=None, end_hi=None, onset_t=None, duration=None)
        bundle = fit_models(ledger, evidence, 2000.0)
        self.assertEqual(bundle.route(unknown, "M3"), "R0")
        self.assertEqual(bundle.score(unknown, evidence[4], "M0"),
                         bundle.score(unknown, evidence[4], "M3"))
        zero = dict(evidence[4], kind="right_censored", censor_at=unknown["issue_time"])
        self.assertEqual(bundle.score(unknown, zero, "M2"), 0.0)

        landmark_unavailable = dict(ledger[4], landmark_available=False)
        shared = [bundle.score(landmark_unavailable, evidence[4], name)
                  for name in ("M0", "M1", "M2", "M3")]
        self.assertEqual(len(set(shared)), 1)

    def test_point_and_zero_width_uniform_end_agree(self):
        point_ledger, evidence = make_training(endpoint_width=0.0)
        uniform_ledger, _ = make_training(endpoint_width=0.0)
        point = fit_models(point_ledger, evidence, 2000.0, endpoint_mode="point")
        uniform = fit_models(uniform_ledger, evidence, 2000.0, endpoint_mode="uniform_end", nodes=5)
        for name in ("M0", "M1", "M2", "M3"):
            self.assertAlmostEqual(point.score(point_ledger[4], evidence[4], name),
                                   uniform.score(uniform_ledger[4], evidence[4], name), places=9)

    def test_type_mode_centres_are_training_only_and_serializable(self):
        ledger, evidence = make_training()
        bundle = fit_models(ledger, evidence, 2000.0, mark_mode="type_within")
        model = bundle.models["M1"]
        logs = [math.log(row["duration"]) for row in ledger]
        expected = {"0": float(np.mean([x for x, row in zip(logs, ledger) if row["duration"] < 12])),
                    "1": float(np.mean([x for x, row in zip(logs, ledger) if row["duration"] >= 12]))}
        for key in expected:
            self.assertAlmostEqual(model.centers["duration_type"][key], expected[key], places=14)
        self.assertIsInstance(bundle.to_dict()["models"]["M1"]["metadata"], dict)


if __name__ == "__main__":
    unittest.main()
