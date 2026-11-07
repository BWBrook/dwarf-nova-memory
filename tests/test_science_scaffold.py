from __future__ import annotations

import csv
from dataclasses import replace
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dnmem.cli import run_demo
from dnmem.forecast import compare_complete_oracle_cycles, fit_model
from dnmem.schema import REQUIRED, validate_photometry
from dnmem.simulate import Event, simulate_events, sample_photometry
from dnmem.survival import (conditional_event_probability, interval_probability,
                            lognormal_cdf, lognormal_logpdf, lognormal_survival)


class WaitingTimeTests(unittest.TestCase):
    def test_lognormal_median_and_density(self):
        self.assertAlmostEqual(lognormal_cdf(10, math.log(10), 0.4), 0.5)
        expected_density_at_median = 1 / (10 * 0.4 * math.sqrt(2 * math.pi))
        self.assertAlmostEqual(math.exp(lognormal_logpdf(10, math.log(10), 0.4)), expected_density_at_median)

    def test_partition_including_right_censoring(self):
        mu, sigma = math.log(30), 0.7
        probability = (interval_probability(0, 15, mu, sigma)
                       + interval_probability(15, 60, mu, sigma)
                       + interval_probability(60, math.inf, mu, sigma))
        self.assertAlmostEqual(probability, 1)
        self.assertAlmostEqual(interval_probability(60, math.inf, mu, sigma), lognormal_survival(60, mu, sigma))

    def test_landmark_probability_conditions_on_survival(self):
        mu, sigma = math.log(20), 0.6
        p = conditional_event_probability(20, 20, mu, sigma)
        self.assertAlmostEqual(p, (lognormal_cdf(40, mu, sigma) - 0.5) / 0.5)
        self.assertEqual(conditional_event_probability(10, 0, mu, sigma), 0)
        tiny = conditional_event_probability(0, 1, math.log(35), 0.4)
        self.assertGreater(tiny, 0)
        self.assertAlmostEqual(tiny / lognormal_cdf(1, math.log(35), 0.4), 1)
        with self.assertRaises(ValueError):
            conditional_event_probability(1e20, 1, 0, 1)

    def test_right_tail_interval_avoids_cdf_cancellation(self):
        p = interval_probability(math.exp(9), math.exp(10), 0, 1)
        self.assertGreater(p, 0)
        self.assertLess(p, 1e-18)

    def test_landmark_matches_independent_density_quadrature(self):
        mu, sigma, age, horizon = math.log(20), 0.6, 20.0, 20.0
        n = 2000
        step = horizon / n
        density = lambda q: math.exp(-0.5 * ((math.log(q) - mu) / sigma) ** 2) / (q * sigma * math.sqrt(2 * math.pi))
        integral = step / 3 * (density(age) + density(age + horizon)
                              + sum((4 if i % 2 else 2) * density(age + i * step) for i in range(1, n)))
        self.assertAlmostEqual(conditional_event_probability(age, horizon, mu, sigma), integral / 0.5, places=12)

    def test_invalid_distribution_and_intervals_fail(self):
        for sigma in (0, -1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                lognormal_cdf(10, 0, sigma)
        for pair in ((-1, 10), (10, 10), (20, 10), (0, math.nan)):
            with self.assertRaises(ValueError):
                interval_probability(*pair, 0, 1)


class ForecastTests(unittest.TestCase):
    def test_frozen_forecast_matches_analytic_regression_fixture(self):
        events, onset = [], 0.0
        for i in range(20):
            x = (-1, -1, 1, 1)[i % 4]
            residual = (-0.2, 0.2, -0.2, 0.2)[i % 4]
            duration, gap = math.exp(2 + x), math.exp(3 + 0.5 * x + residual)
            events.append(Event(i, onset, onset + duration, duration, gap, 0.0))
            onset += duration + gap
        summary, forecasts = compare_complete_oracle_cycles(events, train_fraction=0.8)
        model = summary["models"]["M1_duration"]
        self.assertAlmostEqual(model["fitted_duration_slope"], 0.5)
        self.assertAlmostEqual(model["fitted_residual_log_sigma"], 0.2)
        for row in forecasts:
            if row["model"] == "M1_duration":
                x = (-1, -1, 1, 1)[row["event_id"] % 4]
                self.assertAlmostEqual(row["median_gap"], math.exp(3 + 0.5 * x))
                expected_log_score = -math.log(row["observed_gap"]) - math.log(0.2) - 0.5 * math.log(2 * math.pi) - 0.5
                self.assertAlmostEqual(row["log_score"], expected_log_score)

    def test_simulator_is_reproducible(self):
        self.assertEqual(simulate_events("both", 50, 3), simulate_events("both", 50, 3))
        self.assertNotEqual(simulate_events("both", 50, 3), simulate_events("both", 50, 4))

    def test_cycles_are_nonoverlapping_and_end_anchored(self):
        events = simulate_events("memory", 50, 2)
        for a, b in zip(events, events[1:]):
            self.assertLess(a.onset, a.end)
            self.assertLess(a.end, b.onset)
            self.assertAlmostEqual(b.onset - a.end, a.next_quiescent_gap)

    def test_changing_test_targets_does_not_change_fitted_forecasts(self):
        events = simulate_events("memory", 100, 3)
        _, initial = compare_complete_oracle_cycles(events)
        changed = events[:70] + [replace(e, next_quiescent_gap=e.next_quiescent_gap * 4) for e in events[70:]]
        _, after = compare_complete_oracle_cycles(changed)
        self.assertEqual([r["median_gap"] for r in initial], [r["median_gap"] for r in after])
        self.assertNotEqual([r["log_score"] for r in initial], [r["log_score"] for r in after])

    def test_unresolved_training_target_rejected(self):
        for index in (10, 69):
            events = simulate_events("null", 100, 3)
            events[index] = replace(events[index], next_quiescent_gap=1e8)
            with self.assertRaises(ValueError):
                compare_complete_oracle_cycles(events)

    def test_chronological_order_required(self):
        with self.assertRaises(ValueError):
            compare_complete_oracle_cycles(list(reversed(simulate_events("null", 30))))

    def test_training_scales_are_not_taken_from_test_set(self):
        events = simulate_events("memory", 100, 3)
        _, initial = compare_complete_oracle_cycles(events)
        changed = events[:70] + [replace(e, duration=e.duration * 2) for e in events[70:]]
        _, after = compare_complete_oracle_cycles(changed)
        slope = fit_model(events[:70], True).slope
        for a, b in zip(initial, after):
            if a["model"] == "M0_renewal":
                self.assertEqual(a["median_gap"], b["median_gap"])
            else:
                self.assertAlmostEqual(b["median_gap"] / a["median_gap"], 2 ** slope)

    def test_visibility_gap_reduces_scheduled_coverage(self):
        events = simulate_events("null", 60, 11)
        full, _ = sample_photometry(events, 22, seasonal_gap_days=0)
        seasonal, visibility = sample_photometry(events, 22, seasonal_gap_days=180)
        self.assertLess(len(seasonal), len(full))
        self.assertTrue(any(v["above_threshold_hits"] == 0 for v in visibility))


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "observations.csv"
        self.row = dict(zip(REQUIRED, ["one", "SYNTH", "1.0", "relative_demo_days", "synthetic", "simulation_origin",
                                      "synthetic_V_like", "12.0", "0.1", "false", "", "SIMULATOR", "synthetic", "fixture"]))

    def write_rows(self, rows):
        with self.path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=REQUIRED)
            writer.writeheader()
            writer.writerows(rows)

    def test_detection_and_faint_limit_are_distinct(self):
        limit = dict(self.row, source_row_id="two", is_upper_limit="true", magnitude="", magnitude_error="", limit_magnitude="14.0")
        self.write_rows([self.row, limit])
        result = validate_photometry(self.path)
        self.assertEqual(result["rows"], 2)
        self.assertEqual(result["limits"], 1)

    def test_limit_cannot_be_treated_as_exact_magnitude(self):
        self.write_rows([dict(self.row, is_upper_limit="true", limit_magnitude="14")])
        with self.assertRaises(ValueError):
            validate_photometry(self.path)

    def test_duplicate_source_identity_rejected(self):
        self.write_rows([self.row, self.row])
        with self.assertRaises(ValueError):
            validate_photometry(self.path)

    def test_unresolved_time_and_nonfinite_measurement_rejected(self):
        for change in ({"time_scale": "unknown"}, {"time_reference": " unknown "}, {"magnitude": "nan"}):
            self.write_rows([dict(self.row, **change)])
            with self.assertRaises(ValueError):
                validate_photometry(self.path)


class IntegrationTests(unittest.TestCase):
    def test_demo_reproducible_csvs_and_protects_existing_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = run_demo(Path(tmp) / "a", seed=88, n_events=30)
            second = run_demo(Path(tmp) / "b", seed=88, n_events=30)
            self.assertEqual(first["sha256_csv"], second["sha256_csv"])
            self.assertEqual(len(first["scenarios"]), 4)
            with self.assertRaises(ValueError):
                run_demo(Path(tmp) / "a", seed=88, n_events=30)


if __name__ == "__main__":
    unittest.main()
