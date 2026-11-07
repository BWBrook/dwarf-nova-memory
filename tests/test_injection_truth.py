from pathlib import Path
import math
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.injection_truth import generate_events, magnitudes_at, truth_catalogue


class InjectionTruthTests(unittest.TestCase):
    durations = tuple(2.0 + 0.25 * index for index in range(32))
    gaps = tuple(8.0 + 0.75 * index for index in range(48))

    def test_same_seed_reproduces_complete_truth(self):
        first = generate_events(self.durations, self.gaps, 1000.0, 1500.0, 73, "alternative")
        second = generate_events(self.durations, self.gaps, 1000.0, 1500.0, 73, "alternative")
        self.assertEqual(first, second)
        self.assertLessEqual(first.events[0].onset_jd, first.start_jd)
        self.assertGreater(first.events[-1].onset_jd, first.stop_jd)

    def test_exact_crossings_nonoverlap_and_unlabelled_evaluation(self):
        truth = generate_events(self.durations, self.gaps, 0.0, 800.0, 9)
        for event in truth.events:
            self.assertEqual(event.threshold_interval(10.0), (event.onset_jd, event.end_jd))
            for threshold in (9.5, 10.5):
                interval = event.threshold_interval(threshold)
                if interval is not None:
                    self.assertAlmostEqual(event.magnitude_at(interval[0]), threshold, places=12)
                    self.assertAlmostEqual(event.magnitude_at(interval[1]), threshold, places=12)
        for left, right in zip(truth.events, truth.events[1:]):
            self.assertLessEqual(left.end_jd, right.onset_jd)
            self.assertGreaterEqual(right.onset_jd - left.end_jd, min(self.gaps))
        evaluated = magnitudes_at(truth, [0.0, 1.0, 2.0])
        self.assertEqual(len(evaluated), 3)
        self.assertTrue(all(isinstance(value, float) for value in evaluated))

    def test_threshold_interval_can_represent_no_bright_crossing(self):
        truth = generate_events(self.durations, self.gaps, 0.0, 100.0, 5)
        event = truth.events[0]
        self.assertIsNone(event.threshold_interval(event.peak_magnitude - 0.01))

    def test_null_has_independent_duration_gap_streams_and_alternating_duration(self):
        truth = generate_events(self.durations, self.gaps, 0.0, 500000.0, 101, "null")
        diagnostics = truth.diagnostics
        self.assertLess(abs(diagnostics["raw_duration_gap_correlation"]), 0.04)
        self.assertLess(abs(diagnostics["raw_duration_prior_gap_correlation"]), 0.04)
        self.assertLess(abs(diagnostics["raw_gap_serial_correlation"]), 0.04)
        self.assertLess(diagnostics["raw_duration_serial_correlation"], -0.3)

    def test_alternative_has_positive_requested_dependence_directions(self):
        truth = generate_events(self.durations, self.gaps, 0.0, 500000.0, 202, "alternative")
        diagnostics = truth.diagnostics
        self.assertGreater(diagnostics["raw_gap_serial_correlation"], 0.25)
        self.assertGreater(diagnostics["raw_duration_prior_gap_correlation"], 0.15)
        self.assertGreater(diagnostics["raw_duration_gap_partial_prior_gap"], 0.05)
        self.assertEqual(diagnostics["latent_duration_gap_partial_target"], 0.13)

    def test_aligned_uses_fixed_anchors_and_reports_realized_gaps(self):
        anchors = (10.0, 21.0, 35.0, 52.0)
        truth = generate_events(
            self.durations,
            (1.0, 2.0, 3.0),
            10.0,
            52.0,
            88,
            "null",
            anchors=anchors,
        )
        self.assertEqual(tuple(event.onset_jd for event in truth.events), anchors)
        for event, next_anchor in zip(truth.events, anchors[1:]):
            self.assertAlmostEqual(event.gap_after, next_anchor - event.end_jd)
            self.assertGreaterEqual(event.gap_after, 1.0)
        self.assertTrue(math.isnan(truth.diagnostics["raw_gap_serial_correlation"]) is False)
        self.assertIn("not an independent null", truth.diagnostics["aligned_warning"])
        self.assertFalse(truth.diagnostics["independent_null"])

    def test_aligned_uses_protocol_gap_floor_not_empirical_minimum(self):
        truth = generate_events(
            (8.0, 9.0),
            (16.34, 30.0),
            0.0,
            20.0,
            404,
            "null",
            anchors=(0.0, 10.0, 20.0),
        )
        self.assertEqual(tuple(event.duration for event in truth.events[:2]), (5.0, 5.0))
        self.assertEqual(tuple(event.gap_after for event in truth.events[:2]), (5.0, 5.0))
        self.assertEqual(truth.diagnostics["aligned_duration_capped_count"], 2)

    def test_threshold_catalogue_has_exact_runner_schema(self):
        truth = generate_events(self.durations, self.gaps, 0.0, 100.0, 77)
        catalogue = truth_catalogue(truth, 10.0)
        self.assertTrue(catalogue)
        self.assertEqual(set(catalogue[0]), {"id", "onset", "end", "peak_t", "type"})
        for record in catalogue:
            expected = "short" if record["end"] - record["onset"] < 12.0 else "long"
            self.assertEqual(record["type"], expected)

    def test_fast_evaluation_matches_brute_force(self):
        truth = generate_events(self.durations, self.gaps, 0.0, 500.0, 303)
        times = tuple(-20.0 + index * 0.125 for index in range(4400))
        expected = tuple(
            min(
                (event.magnitude_at(jd) for event in truth.events),
                default=truth.baseline_magnitude,
            )
            for jd in times
        )
        self.assertEqual(magnitudes_at(truth, times), expected)


if __name__ == "__main__":
    unittest.main()
