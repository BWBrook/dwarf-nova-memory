from dataclasses import replace
import math
import unittest

from dnmem import injection_truth
from dnmem import injection_truth_v2 as truth_v2


class SmoothInjectionTruthTests(unittest.TestCase):
    def make_series(self, **kwargs):
        arguments = dict(
            duration_marginal=(5.0, 8.0, 12.0),
            gap_marginal=(4.0, 7.0, 11.0),
            start=0.0,
            stop=60.0,
            seed=731,
            anchors=(0.0, 16.0, 34.0),
        )
        arguments.update(kwargs)
        return truth_v2.generate_events(**arguments)

    def test_reference_roots_and_duration_gap_identity(self):
        series = self.make_series()
        catalogue = truth_v2.truth_catalogue(series, 10.0)
        self.assertEqual(len(catalogue), len(series.events))
        for event, record in zip(series.events, catalogue):
            self.assertAlmostEqual(record["onset"], event.onset_jd, places=10)
            self.assertAlmostEqual(record["end"], event.end_jd, places=10)
            self.assertAlmostEqual(event.duration, event.end_jd - event.onset_jd)
        for event, following in zip(series.events, series.events[1:]):
            self.assertAlmostEqual(event.gap_after, following.onset_jd - event.end_jd)

    def test_numerical_roots_are_exact_at_all_test_thresholds(self):
        event = self.make_series().events[0]
        for threshold in (9.5, 10.0, 10.5):
            interval = event.threshold_interval(threshold)
            self.assertIsNotNone(interval)
            for crossing in interval:
                self.assertAlmostEqual(event.magnitude_at(crossing), threshold, places=11)

    def test_curve_and_derivative_are_smooth_through_thresholds(self):
        event = self.make_series().events[0]
        step = 1e-5
        for threshold in (9.5, 10.0, 10.5):
            interval = event.threshold_interval(threshold)
            self.assertIsNotNone(interval)
            for crossing in interval:
                left = (event.magnitude_at(crossing) - event.magnitude_at(crossing - step)) / step
                right = (event.magnitude_at(crossing + step) - event.magnitude_at(crossing)) / step
                self.assertLess(abs(left - right), 2e-4)
        for centre in (event.rise_centre_jd, event.decline_centre_jd):
            left = (event.magnitude_at(centre) - event.magnitude_at(centre - step)) / step
            right = (event.magnitude_at(centre + step) - event.magnitude_at(centre)) / step
            self.assertLess(abs(left - right), 2e-4)

    def test_reproducible_and_photometry_has_no_truth_labels(self):
        first = self.make_series()
        second = self.make_series()
        self.assertEqual(first, second)
        values = truth_v2.magnitudes_at(first, (-2.0, 0.0, 3.0, 20.0))
        self.assertEqual(len(values), 4)
        self.assertTrue(all(type(value) is float for value in values))

    def test_configurable_quiet_level_is_used_by_series_and_event_api(self):
        series = self.make_series(
            shape_config=truth_v2.ShapeConfig(quiet_magnitude=12.0)
        )
        far_time = -1e6
        self.assertEqual(series.evaluate((far_time,)), (12.0,))
        self.assertEqual(
            truth_v2.magnitudes_at(series.events, (far_time,)), (12.0,)
        )

    def test_active_support_sweep_matches_brute_envelope_and_preserves_order(self):
        series = self.make_series()
        first, second, third = series.events
        heterogeneous = (
            replace(first, rise_tau=0.03, decline_tau=0.07),
            replace(second, rise_tau=4.0, decline_tau=8.0),
            replace(third, rise_tau=0.4, decline_tau=25.0),
        )
        series = replace(series, events=heterogeneous)
        probe_times = (
            1e6,
            second.rise_centre_jd - 100.0,
            first.peak_jd,
            -1e6,
            third.decline_centre_jd + 150.0,
            second.peak_jd,
            0.0,
            third.peak_jd,
            first.rise_centre_jd - 1.0,
        )
        boundary_times = tuple(
            value
            for event in heterogeneous
            for boundary in truth_v2._event_support(event)
            for value in (
                math.nextafter(boundary, -math.inf),
                boundary,
                math.nextafter(boundary, math.inf),
            )
        )
        dense_times = tuple(250.0 - 0.225 * index for index in range(2001))
        times = probe_times + boundary_times + dense_times
        expected = tuple(
            min(
                series.baseline_magnitude,
                *(event.magnitude_at(jd) for event in series.events),
            )
            for jd in times
        )
        observed = series.evaluate(times)
        self.assertEqual(len(observed), len(times))
        for actual, target in zip(observed, expected):
            self.assertLessEqual(abs(actual - target), 1e-12)

    def test_null_and_alternative_inherit_timing_streams(self):
        for process in ("null", "alternative"):
            v2 = self.make_series(process=process, anchors=None)
            original = injection_truth.generate_events(
                (5.0, 8.0, 12.0),
                (4.0, 7.0, 11.0),
                0.0,
                60.0,
                731,
                process,
            )
            observed = [
                (e.onset_jd, e.end_jd, e.duration, e.gap_after, e.latent_duration, e.latent_gap)
                for e in v2.events
            ]
            expected = [
                (e.onset_jd, e.end_jd, e.duration, e.gap_after, e.latent_duration, e.latent_gap)
                for e in original.events
            ]
            self.assertEqual(observed, expected)

    def test_threshold_equal_to_peak_has_no_positive_duration_event(self):
        config = truth_v2.ShapeConfig(
            low_amplitude_probability=1.0,
            low_peak_magnitude_min=9.5,
            low_peak_magnitude_max=9.5,
        )
        series = self.make_series(shape_config=config)
        self.assertEqual(truth_v2.truth_catalogue(series, 9.5), ())

    def test_overlapping_threshold_intervals_are_explicitly_merged(self):
        series = self.make_series(
            duration_marginal=(5.0, 6.0),
            gap_marginal=(0.1, 0.2),
            anchors=(0.0, 5.1),
            shape_config=truth_v2.ShapeConfig(
                rise_rate_median=0.15,
                rise_rate_log_sd=0.0,
                decline_rate_median=0.12,
                decline_rate_log_sd=0.0,
                minimum_rise_rate=0.15,
                minimum_decline_rate=0.12,
            ),
        )
        catalogue = truth_v2.truth_catalogue(series, 10.5)
        self.assertEqual(len(catalogue), 1)
        self.assertEqual(catalogue[0]["id"], "0+1")
        self.assertEqual(catalogue[0]["type"], "merged")

    def test_short_duration_geometry_is_reduced_without_breaking_roots(self):
        series = self.make_series(
            duration_marginal=(0.5, 0.6),
            gap_marginal=(2.0, 3.0),
            anchors=(0.0, 3.0),
        )
        self.assertGreater(series.diagnostics["geometry_adjusted_count"], 0)
        for event in series.events:
            self.assertLessEqual(event.rise_centre_jd, event.decline_centre_jd + 1e-10)
            onset, end = event.threshold_interval(10.0)
            self.assertAlmostEqual(onset, event.onset_jd, places=10)
            self.assertAlmostEqual(end, event.end_jd, places=10)


if __name__ == "__main__":
    unittest.main()
