from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from dnmem.extract_x3 import x3_fitted_episodes
from dnmem.x3_validation_score import (
    audit_final_confirmation_prefix,
    causal_confirmation_emissions,
    score_validation,
)
from test_extract import obs


BASE = 2451544.5


def truth(event_id, onset, end, kind=None):
    return {"id": event_id, "onset": BASE + onset, "end": BASE + end,
            "peak_t": BASE + (onset + end) / 2,
            "type": kind or ("long" if end - onset >= 12 else "short")}


def episode(onset, end, *, onset_t=None, end_t=None, confirmed_event=True,
            confirmed=None, gap_split=False, onset_method="fit", end_method="fit"):
    return {
        "onset_lo": BASE + onset - 1.0,
        "onset_hi": BASE + onset + 1.0,
        "onset_t": BASE + (onset if onset_t is None else onset_t),
        "onset_method": onset_method,
        "end_lo": BASE + end - 1.0,
        "end_hi": BASE + end + 1.0,
        "end_t": BASE + (end if end_t is None else end_t),
        "end_method": end_method,
        "peak_t": BASE + (onset + end) / 2,
        "confirmed_event": confirmed_event,
        "confirmed": None if confirmed is None else BASE + confirmed,
        "gap_split": gap_split,
    }


def row(day, observer, magnitude=12.0):
    return {"JD": str(BASE + day), "mag": str(magnitude), "fainterThan": "0",
            "val": "V", "band": "Vis.", "obsID": f"{day}-{observer}",
            "by": observer, "obsName": observer}


class X3ValidationScoreTests(unittest.TestCase):
    def test_causal_wrapper_closes_visits_without_median_time_backdating(self):
        def raw(jd, magnitude, observer, *, limit=False, suffix=""):
            return {"JD": str(BASE + jd), "mag": str(magnitude),
                    "fainterThan": "1" if limit else "0", "val": "V", "band": "Vis.",
                    "obsID": f"{jd}-{observer}-{suffix}", "by": observer, "obsName": observer}

        rows = [raw(1.00, 9.0, "a"), raw(1.02, 9.0, "b"),
                raw(2.00, 11.0, "a", suffix="first"),
                raw(2.14, 11.0, "a", suffix="last"),
                raw(2.05, 11.0, "b", limit=True),
                raw(2.06, 10.2, "c", limit=True)]

        (emission,) = causal_confirmation_emissions(rows)

        self.assertAlmostEqual(emission["faint_first_at"], BASE + 2.15)
        self.assertAlmostEqual(emission["emitted_at"], BASE + 2.20)
        self.assertAlmostEqual(emission["trigger_visit_first_jd"], BASE + 2.05)
        self.assertEqual(emission["faint_observer_count"], 2)

    def test_confirmed_faint_quiescence_clears_unarmed_provisional_bright_state(self):
        def raw(jd, magnitude, observer):
            return {"JD": str(BASE + jd), "mag": str(magnitude), "fainterThan": "0",
                    "val": "V", "band": "Vis.", "obsID": f"{jd}-{observer}",
                    "by": observer, "obsName": observer}

        rows = [raw(1.00, 9.0, "a"),
                raw(2.00, 11.0, "a"), raw(2.02, 11.0, "b"),
                raw(10.00, 9.0, "a"), raw(10.02, 9.0, "b"),
                raw(11.00, 11.0, "a"), raw(11.02, 11.0, "b")]

        (emission,) = causal_confirmation_emissions(rows)

        self.assertAlmostEqual(emission["bright_first_at"], BASE + 10.15)
        self.assertAlmostEqual(emission["last_bright_at"], BASE + 10.17)
        self.assertAlmostEqual(emission["emitted_at"], BASE + 11.17)
        self.assertEqual(emission["bright_observer_count"], 2)

    def test_equal_close_time_mixed_batch_is_observer_label_invariant(self):
        def raw(jd, magnitude, observer):
            return {"JD": str(BASE + jd), "mag": str(magnitude), "fainterThan": "0",
                    "val": "V", "band": "Vis.", "obsID": f"{jd}-{observer}",
                    "by": observer, "obsName": observer}

        def fixture(mixed_faint_observer):
            return [raw(1.0, 9.0, "a"), raw(1.0, 9.0, "d"),
                    raw(2.0, 11.0, "a"),
                    raw(3.0, 11.0, mixed_faint_observer), raw(3.0, 9.0, "c"),
                    raw(4.0, 11.0, "a"), raw(4.0, 11.0, "b")]

        original = causal_confirmation_emissions(fixture("b"))
        renamed = causal_confirmation_emissions(fixture("z"))

        self.assertEqual(original, renamed)
        self.assertEqual(len(original), 1)
        self.assertAlmostEqual(original[0]["emitted_at"], BASE + 4.15)
        self.assertNotAlmostEqual(original[0]["emitted_at"], BASE + 3.15)
        self.assertEqual(original[0]["bright_observer_count"], 3)

    def test_duration_and_quiet_interval_use_points_not_interval_midpoints(self):
        events = [truth(0, 5, 15), truth(1, 25, 35)]
        extracted = [episode(5, 15, onset_t=6, end_t=14),
                     episode(25, 35, onset_t=27, end_t=34)]
        rows = [row(day, "a" if day % 2 else "b") for day in range(0, 41)]

        result = score_validation(rows, extracted, events, BASE, BASE + 40)[0]

        self.assertEqual(result["duration_point_bias"], -2.5)
        self.assertEqual(result["pair_records"][0]["start"], BASE + 14)
        self.assertEqual(result["pair_records"][0]["stop"], BASE + 27)
        self.assertNotEqual(result["pair_records"][0]["start"], BASE + 15)
        self.assertEqual([item["rule"] for item in score_validation(
            rows, extracted, events, BASE, BASE + 40)], ["C1_7", "C2_095"])

    def test_unconfirmed_episode_and_gap_split_are_explicit_pair_barriers(self):
        events = [truth(0, 2, 8), truth(1, 20, 26), truth(2, 40, 46)]
        extracted = [episode(2, 8),
                     episode(12, 14, confirmed_event=False),
                     episode(20, 26, gap_split=True),
                     episode(40, 46)]
        rows = [row(day, "a" if day % 2 else "b") for day in range(0, 51)]

        result = score_validation(rows, extracted, events, BASE, BASE + 50)[0]
        first, second = result["pair_records"]

        self.assertFalse(first["passed"])
        self.assertEqual(first["barrier_candidate_indices"], [1])
        self.assertIn("unconfirmed_bright_barrier", first["censor_reasons"])
        self.assertIn("following_gap_split", first["censor_reasons"])
        self.assertFalse(second["passed"])
        self.assertIn("current_gap_split", second["censor_reasons"])
        self.assertIsNotNone(first["censor_time"])
        self.assertEqual(result["eligible_count"], 0)

    def test_confirmation_fallback_type_and_month_denominators_are_explicit(self):
        events = [truth(0, 10, 16, "short"), truth(1, 42, 56, "long"),
                  truth(2, 70, 77, "short"), truth(3, 100, 114, "long")]
        extracted = [
            episode(10, 16, confirmed=17, onset_method="adjacency"),
            episode(42, 56, confirmed=55),
            episode(70, 77, confirmed=None, end_method="adjacency"),
        ]
        rows = [row(day, "a" if day % 2 else "b") for day in range(0, 121)]

        result = score_validation(rows, extracted, events, BASE, BASE + 120)[0]

        self.assertEqual(result["batch_confirmation_candidate_count"], 3)
        self.assertEqual(result["batch_confirmation_observed_count"], 2)
        self.assertEqual(result["batch_confirmation_missing_count"], 1)
        self.assertEqual(result["batch_confirmation_premature_count"], 1)
        self.assertEqual(result["batch_confirmation_premature_rate_issued"], 0.5)
        self.assertAlmostEqual(result["batch_confirmation_premature_rate_conservative"], 1 / 3)
        self.assertEqual(result["onset_fallback_count"], 1)
        self.assertAlmostEqual(result["onset_fallback_rate"], 1 / 3)
        self.assertEqual(result["end_fallback_count"], 1)
        self.assertEqual(result["completeness_by_true_type"]["short"]["reference_count"], 2)
        self.assertEqual(result["completeness_by_true_type"]["long"]["complete_count"], 1)
        self.assertEqual(result["completeness_by_gregorian_month"]["1"]["reference_count"], 1)
        self.assertEqual(result["completeness_by_gregorian_month"]["4"]["complete_count"], 0)
        self.assertEqual(result["onset_adjacency_reference_count"], 1)
        self.assertEqual(result["onset_adjacency_conditional_coverage"], 1.0)

    def test_adversarial_prefix_exposes_selective_confirmation_disappearance(self):
        rows = []
        for day, magnitude in ((100, 9.0), (101, 9.0), (102, 9.0), (103, 9.0),
                               (104, 11.0), (105, 9.0), (106, 9.0), (107, 9.0),
                               (108, 11.0)):
            for offset, observer in ((0.6, "a"), (0.7, "b")):
                rows.append(obs(BASE + day + offset, magnitude, observer))
        episodes = x3_fitted_episodes(rows)

        audit = audit_final_confirmation_prefix(rows, episodes)

        self.assertEqual(len(episodes), 1)
        self.assertAlmostEqual(episodes[0]["confirmed"], BASE + 108.7)
        self.assertTrue(audit["reported_confirmation_prefix_measurable"])
        self.assertFalse(audit["no_selective_disappearance"])
        self.assertFalse(audit["passed"])
        witness = next(record for record in audit["records"]
                       if record["prefix_confirmation"] is not None
                       and not record["confirmation_matches_full"])
        self.assertAlmostEqual(witness["cutoff"], BASE + 104.7)
        self.assertAlmostEqual(witness["prefix_confirmation"], BASE + 104.7)
        self.assertEqual(witness["full_confirmation"], episodes[0]["confirmed"])
        self.assertIn("confirmed", witness["discrepant_fields"])

        emissions = causal_confirmation_emissions(rows)
        self.assertEqual(len(emissions), 2)
        self.assertAlmostEqual(emissions[0]["emitted_at"], BASE + 104.85)
        self.assertAlmostEqual(emissions[1]["emitted_at"], BASE + 108.85)
        self.assertLess(emissions[0]["emitted_at"], episodes[0]["confirmed"])
        self.assertEqual(emissions[0]["bright_observer_count"], 2)
        self.assertEqual(emissions[0]["faint_observer_count"], 2)

        scored = score_validation(
            rows, episodes,
            [{"id": "adversarial", "onset": BASE + 99.0, "end": BASE + 108.0,
              "type": "short"}],
            BASE + 90.0, BASE + 120.0,
        )[0]
        self.assertEqual(scored["operational_confirmation_observed_count"], 1)
        self.assertEqual(scored["operational_confirmation_premature_count"], 1)
        self.assertEqual(scored["operational_confirmation_duplicate_emission_count"], 1)
        self.assertEqual(scored["operational_confirmation_false_emission_count"], 0)
        self.assertFalse(scored["operational_confirmation_early_gate_passed"])
        self.assertTrue(scored["operational_confirmation_missing_gate_passed"])


if __name__ == "__main__":
    unittest.main()
