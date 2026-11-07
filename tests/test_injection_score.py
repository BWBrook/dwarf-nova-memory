from pathlib import Path
import math
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.injection_score import score_run


BASE = 2451544.5


def truth(event_id, onset, end, kind=None):
    return {"id": event_id, "onset": BASE + onset, "end": BASE + end,
            "peak_t": BASE + (onset + end) / 2,
            "type": kind or ("long" if end - onset >= 12 else "short")}


def episode(onset, end, *, confirmed=True, onset_missing=False):
    return {
        "onset_lo": None if onset_missing else BASE + onset - 0.2,
        "onset_hi": BASE + onset + 0.2,
        "end_lo": BASE + end - 0.2,
        "end_hi": BASE + end + 0.2,
        "peak_t": BASE + (onset + end) / 2,
        "confirmed_event": confirmed,
    }


def row(day, observer, magnitude=12.0, *, limit=False):
    return {"JD": str(BASE + day), "mag": str(magnitude),
            "fainterThan": "1" if limit else "0", "val": "V", "band": "Vis.",
            "obsID": f"{day}-{observer}", "by": observer, "obsName": observer}


class InjectionScoreTests(unittest.TestCase):
    def test_effective_denominator_retains_missed_and_unbracketed_truth(self):
        events = [truth(0, 10, 16), truth(1, 30, 44), truth(2, 60, 66)]
        extracted = [episode(10, 16), episode(30, 44, onset_missing=True), episode(80, 84)]
        result = score_run([], extracted, events, BASE, BASE + 100)[0]

        self.assertEqual(result["reference_event_count"], 3)
        self.assertEqual(result["completeness_count"], 2)
        self.assertEqual(result["unique_completeness_count"], 2)
        self.assertEqual(result["false_confirmed_count"], 1)
        self.assertEqual(result["onset_finite_matched_count"], 1)
        self.assertEqual(result["onset_effective_covered"], 1)
        self.assertAlmostEqual(result["onset_effective_coverage"], 1 / 3)
        self.assertEqual(result["end_finite_matched_count"], 2)
        self.assertEqual(result["end_effective_covered"], 2)
        self.assertAlmostEqual(result["end_effective_coverage"], 2 / 3)
        self.assertTrue(result["recovered_r_undefined"])

    def test_coverage_rules_have_exact_opportunity_and_conservative_censor_times(self):
        events = [truth(0, 2, 9), truth(1, 20, 27)]
        extracted = [episode(2, 10), episode(20, 27)]
        rows = [row(12, "a"), row(14, "b")]
        results = {result["rule"]: result for result in
                   score_run(rows, extracted, events, BASE, BASE + 40)}

        self.assertEqual(results["C1_4"]["eligible_count"], 0)
        self.assertAlmostEqual(results["C1_4"]["censor_time_min"], BASE + 14)
        self.assertEqual(results["C1_7"]["eligible_count"], 1)
        self.assertEqual(results["C2_095"]["eligible_count"], 0)
        self.assertAlmostEqual(results["C2_095"]["coverage_diagnostic_mean"], 0.4)
        self.assertAlmostEqual(results["C2_095"]["censor_time_min"], BASE + 12)
        self.assertEqual(results["C1_7"]["mapped_trueconsecutive"], 1)
        self.assertEqual(results["C1_4"]["rejected_trueconsecutive"], 1)
        self.assertEqual(results["C1_7"]["confirmation_observed_count"], 1)
        self.assertEqual(results["C1_7"]["confirmation_missing_count"], 1)

    def test_partial_correlations_use_complete_eligible_triples_and_pair_with_oracle(self):
        durations = [5, 8, 6, 10, 7, 11, 9, 13, 6]
        gaps = [12, 9, 15, 8, 14, 11, 17, 10]
        events = []
        extracted = []
        onset = 5.0
        for index, duration in enumerate(durations):
            end = onset + duration
            events.append(truth(index, onset, end))
            extracted.append(episode(onset, end))
            if index < len(gaps):
                onset = end + gaps[index]
        stop = onset + durations[-1] + 5
        rows = [row(day, "a" if day % 2 else "b") for day in range(0, math.ceil(stop) + 1)]

        results = {result["rule"]: result for result in
                   score_run(rows, extracted, events, BASE, BASE + stop)}
        for rule in ("C1_4", "C1_7", "C2_095"):
            result = results[rule]
            self.assertEqual(result["eligible_count"], len(events) - 1)
            self.assertEqual(result["association_n"], len(events) - 2)
            self.assertEqual(result["selected_association_n"], len(events) - 2)
            self.assertFalse(result["recovered_r_undefined"])
            self.assertAlmostEqual(result["recovered_r"], result["oracle_r_all"], places=9)
            self.assertAlmostEqual(result["selected_oracle_r"], result["oracle_r_all"], places=9)
            self.assertAlmostEqual(result["recovered_matched_r"], result["oracle_r_all"], places=9)
            self.assertAlmostEqual(result["total_bias"], 0.0, places=9)
            self.assertAlmostEqual(result["selection_bias"], 0.0, places=9)
            self.assertAlmostEqual(result["boundary_bias"], 0.0, places=9)
            self.assertEqual(result["hidden_passed"], 0)

    def test_split_and_merge_components_do_not_become_unique_boundary_matches(self):
        events = [truth(0, 10, 18), truth(1, 20, 28), truth(2, 50, 58)]
        split_a = episode(10, 14)
        split_b = episode(14, 18)
        merged = episode(20, 58)
        result = score_run([], [split_a, split_b, merged], events, BASE, BASE + 80)[0]

        self.assertEqual(result["split_truth_count"], 1)
        self.assertEqual(result["merged_episode_count"], 1)
        self.assertEqual(result["completeness_count"], 3)
        self.assertEqual(result["unique_completeness_count"], 0)
        self.assertEqual(result["onset_finite_matched_count"], 0)
        self.assertEqual(result["onset_effective_covered"], 0)

    def test_repeated_rows_from_one_observer_do_not_satisfy_two_observer_c2(self):
        events = [truth(0, 2, 9), truth(1, 20, 27)]
        extracted = [episode(2, 10), episode(20, 27)]
        rows = [row(10.0 + offset, "a") for offset in (0.0, 0.1, 2.0, 4.0)]
        result = {item["rule"]: item for item in
                  score_run(rows, extracted, events, BASE, BASE + 40)}["C2_095"]

        self.assertEqual(result["eligible_count"], 0)
        self.assertEqual(result["coverage_diagnostic_mean"], 0.0)

    def test_hidden_passed_requires_a_fully_contained_nonendpoint_event(self):
        events = [truth(0, 2, 8), truth(1, 15, 20), truth(2, 30, 36)]
        extracted = [episode(2, 8), episode(30, 36)]
        rows = [row(day, "a" if day % 2 else "b") for day in range(8, 31)]
        results = score_run(rows, extracted, events, BASE, BASE + 40)

        for result in results:
            self.assertEqual(result["pairs_passed"], 1)
            self.assertEqual(result["hidden_passed"], 1)
            self.assertEqual(result["mapped_trueconsecutive"], 0)


if __name__ == "__main__":
    unittest.main()
