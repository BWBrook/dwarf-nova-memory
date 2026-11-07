from pathlib import Path
import math
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.injection_truth import LatentCoefficients
from dnmem.injection_truth import generate_events as generate_original
from dnmem.injection_truth_v3 import (
    ShapeConfig,
    generate_events,
    magnitudes_at,
    truth_catalogue,
)


class InjectionTruthV3Tests(unittest.TestCase):
    durations = tuple(2.0 + 0.25 * index for index in range(32))
    gaps = tuple(8.0 + 0.75 * index for index in range(48))

    def test_timings_are_unchanged_and_reference_roots_are_exact(self):
        coefficients = LatentCoefficients(gap_persistence=0.3)
        original = generate_original(
            self.durations, self.gaps, 0.0, 800.0, 19, "alternative", coefficients=coefficients
        )
        truth = generate_events(
            self.durations, self.gaps, 0.0, 800.0, 19, "alternative", coefficients=coefficients
        )
        self.assertEqual(
            tuple((event.onset_jd, event.end_jd, event.gap_after) for event in truth.events),
            tuple((event.onset_jd, event.end_jd, event.gap_after) for event in original.events),
        )
        for event in truth.events:
            self.assertEqual(event.threshold_interval(10.0), (event.onset_jd, event.end_jd))
            self.assertEqual(event.magnitude_at(event.onset_jd), 10.0)
            self.assertEqual(event.magnitude_at(event.end_jd), 10.0)

    def test_diagnostic_thresholds_are_analytic_roots(self):
        truth = generate_events(self.durations, self.gaps, 0.0, 300.0, 29)
        for event in truth.events:
            for threshold in (9.5, 10.5):
                interval = event.threshold_interval(threshold)
                self.assertIsNotNone(interval)
                self.assertAlmostEqual(event.magnitude_at(interval[0]), threshold, places=12)
                self.assertAlmostEqual(event.magnitude_at(interval[1]), threshold, places=12)
            self.assertIsNone(event.threshold_interval(event.peak_magnitude - 0.01))

    def test_reference_crossing_is_not_a_knot(self):
        event = generate_events(self.durations, self.gaps, 0.0, 100.0, 37).events[2]
        h = 1e-5
        left = (event.magnitude_at(event.onset_jd) - event.magnitude_at(event.onset_jd - h)) / h
        right = (event.magnitude_at(event.onset_jd + h) - event.magnitude_at(event.onset_jd)) / h
        self.assertAlmostEqual(left, right, delta=2e-4)
        self.assertAlmostEqual(-0.5 * (left + right), event.rise_slope_at_reference, delta=2e-4)
        left = (event.magnitude_at(event.end_jd) - event.magnitude_at(event.end_jd - h)) / h
        right = (event.magnitude_at(event.end_jd + h) - event.magnitude_at(event.end_jd)) / h
        self.assertAlmostEqual(left, right, delta=2e-4)
        self.assertAlmostEqual(0.5 * (left + right), event.decline_slope_at_reference, delta=2e-4)

    def test_seed_is_deterministic_and_shape_stream_does_not_change_timing(self):
        first = generate_events(self.durations, self.gaps, 0.0, 500.0, 41)
        second = generate_events(self.durations, self.gaps, 0.0, 500.0, 41)
        changed_shape = generate_events(
            self.durations,
            self.gaps,
            0.0,
            500.0,
            41,
            shape_config=ShapeConfig(rise_rate_median=2.5),
        )
        self.assertEqual(first, second)
        self.assertEqual(
            tuple((event.onset_jd, event.end_jd) for event in first.events),
            tuple((event.onset_jd, event.end_jd) for event in changed_shape.events),
        )
        self.assertNotEqual(first.events[0].rise_width, changed_shape.events[0].rise_width)

    def test_explicit_geometry_constraints_preserve_timing_and_separate_supports(self):
        config = ShapeConfig(
            rise_rate_median=0.02,
            rise_rate_log_sd=0.0,
            minimum_rise_rate=0.02,
            decline_rate_median=0.02,
            decline_rate_log_sd=0.0,
            minimum_decline_rate=0.02,
        )
        truth = generate_events((0.2, 0.3), (0.25, 0.35), 0.0, 4.0, 53, shape_config=config)
        self.assertGreater(truth.diagnostics["shape_geometry_constrained_count"], 0)
        self.assertGreater(truth.diagnostics["shape_duration_constrained_count"], 0)
        for event in truth.events:
            self.assertGreaterEqual(
                event.plateau_end_jd - event.plateau_start_jd,
                config.minimum_plateau_fraction * event.duration - 1e-12,
            )
            self.assertEqual(event.threshold_interval(10.0), (event.onset_jd, event.end_jd))
        for left, right in zip(truth.events, truth.events[1:]):
            self.assertLess(left.support_end_jd, right.support_start_jd)

    def test_unsorted_batch_matches_point_evaluation(self):
        truth = generate_events(self.durations, self.gaps, 0.0, 500.0, 61)
        times = (150.2, -2.0, 41.7, 499.9, 0.0, 41.7, 902.0)
        expected = tuple(
            min((event.magnitude_at(time) for event in truth.events), default=truth.baseline_magnitude)
            for time in times
        )
        self.assertEqual(magnitudes_at(truth, times), expected)

    def test_catalogue_retains_runner_fields_and_adds_shape_truth(self):
        truth = generate_events(self.durations, self.gaps, 0.0, 100.0, 71)
        record = truth_catalogue(truth, 10.0)[0]
        self.assertTrue({"id", "onset", "end", "peak_t", "type"}.issubset(record))
        self.assertEqual(record["duration"], record["end"] - record["onset"])
        self.assertTrue(math.isfinite(record["peak"]))


if __name__ == "__main__":
    unittest.main()
