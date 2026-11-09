from dataclasses import dataclass
import json
import math
from pathlib import Path
import sys
import unittest

import numpy as np
from scipy.integrate import quad
from scipy.stats import lognorm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.r2_scores import (
    interval_log_mass, latent_point_gain_bounds, mixed_score_bounds,
    right_censored_contrast, route_compatibility_window, working_interval_contrast,
)


@dataclass(frozen=True)
class TestClock:
    anchor: float
    issue: float
    mu: float
    sigma: float

    def log_survival(self, calendar_time):
        model = lognorm(s=self.sigma, scale=math.exp(self.mu))
        return float(model.logsf(calendar_time - self.anchor) - model.logsf(self.issue - self.anchor))

    def log_density(self, calendar_time):
        if calendar_time <= self.issue:
            return -math.inf
        model = lognorm(s=self.sigma, scale=math.exp(self.mu))
        return float(model.logpdf(calendar_time - self.anchor) - model.logsf(self.issue - self.anchor))


class IntervalMassTests(unittest.TestCase):
    def test_conditional_mass_against_independent_density_integral(self):
        clock = TestClock(10., 15., math.log(20), .6)
        result = interval_log_mass(clock, 20., 45.)
        normalizer = lognorm.sf(5., s=.6, scale=20.)
        integral = quad(lambda t: lognorm.pdf(t - 10, s=.6, scale=20.) / normalizer,
                        20., 45., epsabs=1e-13, epsrel=1e-13)[0]
        self.assertEqual(result["status"], "usable")
        self.assertAlmostEqual(result["log_mass"], math.log(integral), places=12)
        self.assertTrue(result["numerical"]["survival_conditioned_once"])
        self.assertLess(result["numerical"]["log_survival_at_issue"], 0)

    def test_extreme_normal_tails_against_scaled_density_quadrature(self):
        clock = TestClock(0., 0., 0., 1.)
        scaled = quad(lambda z: math.exp(-.5 * (z*z - 40*40)), 40., 41.,
                      epsabs=1e-13, epsrel=1e-13)[0]
        expected = -.5 * 40**2 - .5 * math.log(2*math.pi) + math.log(scaled)
        for lower, upper, branch in ((40., 41., "survival"), (-41., -40., "cdf")):
            result = interval_log_mass(clock, math.exp(lower), math.exp(upper))
            self.assertEqual(result["status"], "usable")
            self.assertEqual(result["numerical"]["tail_branch"], branch)
            self.assertAlmostEqual(result["log_mass"], expected, places=11)
            self.assertLess(result["log_mass"], -800.)

    def test_unresolvable_transformed_interval_is_unavailable_not_epsilon(self):
        clock = TestClock(0., 0., 0., 1.)
        lower = math.exp(100.)
        upper = math.nextafter(lower, math.inf)
        result = interval_log_mass(clock, lower, upper)
        self.assertEqual(result["status"], "numerical_failure")
        self.assertNotIn("log_mass", result)


class RoutingTests(unittest.TestCase):
    def test_cutoff_ties_and_straddle_policy(self):
        cases = ((15, 20, 20, "interval", None, False),
                 (20, 25, 20, "right_censored", 20, False),
                 (15, 25, 20, "right_censored", 15, True),
                 (25, 30, 20, "right_censored", 20, False))
        for lo, hi, cutoff, kind, censor, backoff in cases:
            with self.subTest(lo=lo, hi=hi, cutoff=cutoff):
                result = route_compatibility_window(lo, hi, 10, cutoff)
                self.assertEqual(result["status"], "usable")
                self.assertEqual((result["kind"], result["censor_at"], result["censor_backoff"]),
                                 (kind, censor, backoff))

    def test_missing_overtaken_ambiguous_and_nonfinite_windows(self):
        cases = ((None, 20, "missing_window"), (15, None, "missing_window"),
                 (math.nan, 20, "nonfinite_window"), (15, math.inf, "nonfinite_window"),
                 (20, 15, "reversed_window"), (10, 10, "reversed_window"),
                 (8, 10, "overtaken"), (9, 20, "ambiguous_survival"),
                 (10, 20, "ambiguous_survival"))
        for lo, hi, status in cases:
            with self.subTest(lo=lo, hi=hi):
                result = route_compatibility_window(lo, hi, 10, 25)
                self.assertEqual(result["status"], status)
                self.assertNotIn("gain", result)

    def test_invalid_cutoff_and_clock_contract(self):
        b = TestClock(0., 5., math.log(20), .6)
        for cutoff, status in ((None, "missing_cutoff"), (math.inf, "nonfinite_cutoff"),
                               (4., "cutoff_before_issue")):
            self.assertEqual(working_interval_contrast(b, b, 10, 20, cutoff)["status"], status)
        for d in (TestClock(1., 5., math.log(20), .6), TestClock(0., 6., math.log(20), .6),
                  TestClock(0., 5., math.log(20), 0.)):
            with self.assertRaises(ValueError):
                mixed_score_bounds(b, d, 10, 20, 25)
        class UnconditionedClock(TestClock):
            def log_survival(self, calendar_time):
                return float(lognorm.logsf(calendar_time-self.anchor, s=self.sigma, scale=math.exp(self.mu)))
        with self.assertRaisesRegex(ValueError, "already condition"):
            interval_log_mass(UnconditionedClock(0., 5., math.log(20), .6), 10, 20)


class BoundTests(unittest.TestCase):
    def pair(self):
        return TestClock(0., 5., math.log(20), .7), TestClock(0., 5., math.log(30), .5)

    def assert_contains(self, bounds, value):
        self.assertLessEqual(bounds["lower"] - 1e-12, value)
        self.assertGreaterEqual(bounds["upper"] + 1e-12, value)

    def test_unequal_variance_stationary_extrema(self):
        for base_sigma, duration_sigma, extremum in ((.5, 1., "lower"), (1., .5, "upper")):
            b = TestClock(0., 2., math.log(20), base_sigma)
            d = TestClock(0., 2., math.log(20), duration_sigma)
            result = latent_point_gain_bounds(b, d, 10., 40.)
            self.assertEqual(result["status"], "usable")
            stationary = [row for row in result["numerical"]["candidates"] if row["location"]=="stationary"]
            self.assertEqual(len(stationary), 1)
            self.assertAlmostEqual(stationary[0]["time"], 20., places=12)
            self.assertAlmostEqual(result[extremum], d.log_density(20)-b.log_density(20), places=12)
            for time in np.linspace(10.000001, 40., 200):
                self.assert_contains(result, d.log_density(time)-b.log_density(time))

    def test_equal_variance_monotonic_bounds_in_both_shift_directions(self):
        b = TestClock(10., 12., math.log(20), .7)
        for delta in (-.2, .2):
            d = TestClock(10., 12., math.log(20)+delta, .7)
            result = latent_point_gain_bounds(b, d, 20., 45.)
            expected = [d.log_density(t)-b.log_density(t) for t in (20., 45.)]
            self.assertAlmostEqual(result["lower"], min(expected), places=12)
            self.assertAlmostEqual(result["upper"], max(expected), places=12)
            self.assertEqual(len(result["numerical"]["candidates"]), 2)

    def test_fixed_cutoff_straddle_bounds_union_of_points_and_survival(self):
        b, d = self.pair()
        mixed = mixed_score_bounds(b, d, 15., 35., 25.)
        self.assertEqual(mixed["kind"], "straddle")
        self.assertEqual(mixed["event_bounds"]["onset_hi"], 25.)
        for time in np.linspace(15.000001, 35., 300):
            target = (d.log_density(time)-b.log_density(time) if time <= 25 else
                      d.log_survival(25)-b.log_survival(25))
            self.assert_contains(mixed, target)
        survival = d.log_survival(25)-b.log_survival(25)
        self.assertEqual(mixed["survival_gain"], survival)
        working = working_interval_contrast(b, d, 15., 35., 25.)
        self.assertEqual(working["censor_at"], 15.)
        self.assertAlmostEqual(working["gain"], d.log_survival(15)-b.log_survival(15), places=12)
        self.assertNotEqual(working["gain"], mixed["survival_gain"])

    def test_fixed_cutoff_exact_event_and_survival_ties(self):
        b, d = self.pair()
        event = mixed_score_bounds(b, d, 15., 25., 25.)
        self.assertEqual(event["kind"], "event")
        self.assert_contains(event, d.log_density(25)-b.log_density(25))
        censor = mixed_score_bounds(b, d, 25., 30., 25.)
        self.assertEqual(censor["kind"], "right_censored")
        self.assertEqual(censor["lower"], censor["upper"])
        self.assertEqual(censor["lower"], d.log_survival(25)-b.log_survival(25))
        immediate = mixed_score_bounds(b, d, 15., 25., b.issue)
        self.assertEqual(immediate["lower"], 0.)
        self.assertEqual(immediate["upper"], 0.)

    def test_same_distribution_nests_exactly_across_policies(self):
        b, _ = self.pair()
        for lo, hi, cutoff in ((15., 20., 25.), (15., 35., 25.), (30., 40., 25.)):
            working = working_interval_contrast(b, b, lo, hi, cutoff)
            mixed = mixed_score_bounds(b, b, lo, hi, cutoff)
            self.assertEqual(working["gain"], 0.)
            self.assertEqual((mixed["lower"], mixed["upper"]), (0., 0.))
            json.dumps({"working": working, "mixed": mixed}, allow_nan=False)

    def test_censored_survival_is_not_an_unknown_latent_point_bound(self):
        b, d = self.pair()
        result = right_censored_contrast(b, d, 25.)
        self.assertFalse(result["bounds_latent_point_gain"])
        self.assertNotAlmostEqual(result["gain"], d.log_density(300)-b.log_density(300))
        unsupported = latent_point_gain_bounds(b, d, 25., math.inf)
        self.assertEqual(unsupported["status"], "nonfinite_window")
        self.assertFalse(unsupported["finite_latent_point_bounds_supported"])
        self.assertNotIn("lower", unsupported)
        self.assertEqual(mixed_score_bounds(b, d, None, None, 25.)["status"], "missing_window")


if __name__ == "__main__":
    unittest.main()
