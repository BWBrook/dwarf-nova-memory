import math
import unittest

from dnmem.injection_truth import LatentCoefficients, generate_events as generate_original
from dnmem.injection_truth_v4 import (
    ShapeConfig,
    generate_events,
    magnitudes_at,
    truth_catalogue,
)


DURATIONS = (5.2, 6.0, 7.5, 9.0, 11.0, 13.5, 16.0, 20.0)
GAPS = (18.0, 24.0, 31.0, 42.0, 55.0)


class InjectionTruthV4Tests(unittest.TestCase):
    def test_timing_is_identical_for_all_process_specifications(self):
        specifications = (
            ("null", None),
            ("alternative", None),
            (
                "alternative",
                LatentCoefficients(
                    duration_persistence=-0.2,
                    duration_prior_gap=0.18,
                    gap_persistence=0.25,
                    partial_duration_gap=0.08,
                ),
            ),
        )
        for process, coefficients in specifications:
            original = generate_original(
                DURATIONS, GAPS, 1000.0, 1800.0, 47, process, coefficients=coefficients
            )
            shaped = generate_events(
                DURATIONS, GAPS, 1000.0, 1800.0, 47, process, coefficients=coefficients
            )
            original_rows = [
                (e.onset_jd, e.end_jd, e.duration, e.gap_after) for e in original.events
            ]
            shaped_rows = [
                (e.onset_jd, e.end_jd, e.duration, e.gap_after) for e in shaped.events
            ]
            self.assertEqual(original_rows, shaped_rows)

    def test_deterministic_and_shape_stream_is_separate(self):
        first = generate_events(DURATIONS, GAPS, 1000.0, 1800.0, 91)
        second = generate_events(DURATIONS, GAPS, 1000.0, 1800.0, 91)
        self.assertEqual(first, second)
        self.assertEqual(first.diagnostics["shape_timing_independent"], 1)

    def test_ten_magnitude_roots_are_preserved(self):
        history = generate_events(DURATIONS, GAPS, 1000.0, 1800.0, 13)
        for event in history.events:
            interval = event.threshold_interval(10.0)
            self.assertIsNotNone(interval)
            self.assertAlmostEqual(interval[0], event.onset_jd, places=11)
            self.assertAlmostEqual(interval[1], event.end_jd, places=11)
            self.assertAlmostEqual(interval[1] - interval[0], event.duration, places=11)
        catalogue = truth_catalogue(history, 10.0)
        self.assertEqual(len(catalogue), len(history.events))
        self.assertTrue(all("duration" in row and "peak" in row for row in catalogue))

    def test_flanks_are_monotone_and_turnover_is_rounded(self):
        history = generate_events(DURATIONS, GAPS, 1000.0, 1800.0, 22)
        for event in history.events:
            left = [
                event.magnitude_at(event.onset_jd + (event.peak_jd - event.onset_jd) * i / 20)
                for i in range(21)
            ]
            right = [
                event.magnitude_at(event.peak_jd + (event.end_jd - event.peak_jd) * i / 20)
                for i in range(21)
            ]
            self.assertTrue(all(a >= b for a, b in zip(left, left[1:])))
            self.assertTrue(all(a <= b for a, b in zip(right, right[1:])))
            self.assertGreater(event.turnover_power, 1.0)
            coarse = 1e-3
            fine = 1e-6
            coarse_change = max(
                abs(event.magnitude_at(event.peak_jd + coarse) - event.peak_magnitude),
                abs(event.magnitude_at(event.peak_jd - coarse) - event.peak_magnitude),
            ) / coarse
            fine_change = max(
                abs(event.magnitude_at(event.peak_jd + fine) - event.peak_magnitude),
                abs(event.magnitude_at(event.peak_jd - fine) - event.peak_magnitude),
            ) / fine
            self.assertLess(fine_change, coarse_change)

    def test_no_value_or_slope_kink_at_ten_and_rates_match_draws(self):
        event = generate_events(DURATIONS, GAPS, 1000.0, 1800.0, 28).events[8]
        for crossing, expected in (
            (event.onset_jd, -event.rise_rate),
            (event.end_jd, event.decline_rate),
        ):
            epsilon = 1e-5
            left = (event.magnitude_at(crossing) - event.magnitude_at(crossing - epsilon)) / epsilon
            right = (event.magnitude_at(crossing + epsilon) - event.magnitude_at(crossing)) / epsilon
            self.assertAlmostEqual(event.magnitude_at(crossing), 10.0, places=11)
            self.assertAlmostEqual(left, expected, delta=2e-4)
            self.assertAlmostEqual(right, expected, delta=2e-4)

    def test_tangent_and_band_slopes_are_geometrically_sensible(self):
        history = generate_events(DURATIONS, GAPS, 1000.0, 2200.0, 37)
        eligible = [event for event in history.events if event.peak_magnitude < 9.5]
        self.assertGreater(len(eligible), 5)
        for event in eligible:
            brighter = event.threshold_interval(9.5)
            fainter = event.threshold_interval(10.5)
            rise_band = 1.0 / (brighter[0] - fainter[0])
            decline_band = 1.0 / (fainter[1] - brighter[1])
            self.assertGreater(rise_band, 0.0)
            self.assertGreater(decline_band, 0.0)
            self.assertLess(rise_band / event.rise_rate, 2.5)
            self.assertLess(decline_band / event.decline_rate, 2.5)

    def test_duration_amplitude_coupling_has_declared_direction(self):
        config = ShapeConfig(
            rise_rate_log_spread=0.0,
            decline_rate_log_spread=0.0,
            peak_scatter=0.0,
        )
        anchors = tuple(1000.0 + 80.0 * i for i in range(40))
        history = generate_events(
            DURATIONS,
            GAPS,
            1000.0,
            4300.0,
            7,
            anchors=anchors,
            shape_config=config,
        )
        ordered = sorted(history.events, key=lambda event: event.duration)
        low = sum(event.peak_magnitude for event in ordered[:10]) / 10
        high = sum(event.peak_magnitude for event in ordered[-10:]) / 10
        self.assertGreater(low, high)

    def test_unsorted_batch_matches_direct_evaluation_and_tails_do_not_overlap(self):
        history = generate_events(DURATIONS, GAPS, 1000.0, 1800.0, 64)
        times = [
            history.events[7].peak_jd,
            999.0,
            history.events[2].onset_jd,
            history.events[-3].end_jd + 0.2,
            history.events[0].support_start_jd,
        ]
        expected = []
        for time in times:
            active = [
                event.magnitude_at(time)
                for event in history.events
                if event.support_start_jd <= time <= event.support_end_jd
            ]
            expected.append(min(active) if active else history.baseline_magnitude)
        self.assertEqual(magnitudes_at(history, times), tuple(expected))
        for left, right in zip(history.events, history.events[1:]):
            self.assertLess(left.support_end_jd, right.support_start_jd)

    def test_invalid_shape_parameters_fail_explicitly(self):
        with self.assertRaises(ValueError):
            generate_events(
                DURATIONS,
                GAPS,
                1000.0,
                1800.0,
                1,
                shape_config=ShapeConfig(decline_rate_median=0.0),
            )
        with self.assertRaises(ValueError):
            generate_events(
                DURATIONS,
                GAPS,
                1000.0,
                1800.0,
                1,
                shape_config=ShapeConfig(peak_scatter=math.nan),
            )


if __name__ == "__main__":
    unittest.main()
