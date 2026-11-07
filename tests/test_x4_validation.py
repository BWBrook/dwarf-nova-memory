from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.extract_x4 import causal_confirmations as reference_causal_confirmations
from dnmem.x3_validation_score import score_validation as x3_score_validation
from dnmem.x4_validation import (
    causal_confirmation_emissions,
    reference_checked_emissions,
    score_validation,
)


BASE = 2451544.5


def row(day, magnitude, observer, *, limit=False, obs_name=None, band="Vis.", val="V", suffix=""):
    return {
        "JD": str(BASE + day),
        "mag": str(magnitude),
        "fainterThan": "1" if limit else "0",
        "val": val,
        "band": band,
        "obsID": f"{day}-{observer}-{suffix}",
        "by": observer,
        "obsName": observer if obs_name is None else obs_name,
    }


class X4CausalValidationTests(unittest.TestCase):
    def test_equal_close_time_bright_suppresses_faint_batch_atomically(self):
        rows = [
            row(1.0, 9.0, "a"), row(1.0, 9.0, "b"),
            row(2.0, 11.0, "a"),
            row(3.0, 11.0, "b"), row(3.0, 9.9, "c"),
            row(4.0, 11.0, "a"), row(4.0, 11.0, "b"),
        ]

        (emission,) = causal_confirmation_emissions(rows)

        self.assertAlmostEqual(emission["bright_first_at"], BASE + 1.15)
        self.assertAlmostEqual(emission["last_bright_at"], BASE + 3.15)
        self.assertAlmostEqual(emission["faint_first_at"], BASE + 4.15)
        self.assertAlmostEqual(emission["emitted_at"], BASE + 4.15)
        self.assertEqual(emission["bright_observer_count"], 3)
        self.assertEqual(emission["strong_bright_observer_count"], 2)

    def test_one_observer_arms_only_on_two_distinct_nights(self):
        same_night = [
            row(1.00, 9.0, "a"), row(1.30, 9.0, "a"),
            row(2.00, 11.0, "b"), row(2.00, 11.0, "c"),
        ]
        two_nights = [
            row(1.00, 9.0, "a"), row(2.00, 9.0, "a"),
            row(3.00, 11.0, "b"), row(3.00, 11.0, "c"),
        ]

        self.assertEqual(causal_confirmation_emissions(same_night), [])
        (emission,) = causal_confirmation_emissions(two_nights)
        self.assertEqual(emission["bright_observer_count"], 1)
        self.assertEqual(emission["strong_bright_observer_count"], 1)

    def test_weak_bright_visits_reset_faint_evidence_but_do_not_arm(self):
        rows = [
            row(1.0, 9.7, "a"), row(1.0, 9.8, "b"),
            row(2.0, 11.0, "c"),
            row(3.0, 9.9, "d"),
            row(4.0, 11.0, "e"), row(4.0, 11.0, "f"),
        ]

        self.assertEqual(causal_confirmation_emissions(rows), [])

    def test_repeated_estimates_are_one_visit_vote_anchored_at_first_row(self):
        rows = [
            row(1.00, 9.0, "a", suffix="1"),
            row(1.10, 9.0, "a", suffix="2"),
            row(1.20, 11.0, "a", suffix="3"),
            row(2.00, 9.0, "b"),
            row(3.00, 11.0, "c"), row(3.00, 11.0, "d"),
        ]

        (emission,) = causal_confirmation_emissions(rows)

        self.assertAlmostEqual(emission["bright_first_at"], BASE + 1.15)
        self.assertAlmostEqual(emission["last_bright_at"], BASE + 2.15)
        self.assertEqual(emission["bright_observer_count"], 2)
        self.assertEqual(emission["strong_bright_observer_count"], 2)

    def test_detections_dominate_limits_and_limit_direction_is_respected(self):
        rows = [
            row(1.00, 9.0, "a"), row(1.00, 9.0, "b"),
            row(2.00, 10.2, "c", suffix="detection"),
            row(2.05, 12.0, "c", limit=True, suffix="limit"),
            row(3.00, 10.4, "d", limit=True),
            row(4.00, 10.5, "d", limit=True),
            row(4.00, 11.0, "e"),
        ]

        (emission,) = causal_confirmation_emissions(rows)

        self.assertAlmostEqual(emission["faint_first_at"], BASE + 4.15)
        self.assertAlmostEqual(emission["emitted_at"], BASE + 4.15)
        self.assertEqual(emission["faint_observer_count"], 2)

    def test_unarmed_two_observer_faint_state_cannot_arm_later_event(self):
        rows = [
            row(1.0, 9.0, "a"),
            row(2.0, 11.0, "b"), row(2.0, 11.0, "c"),
            row(3.0, 9.0, "d"), row(3.0, 9.0, "e"),
            row(4.0, 11.0, "f"), row(4.0, 11.0, "g"),
        ]

        (emission,) = causal_confirmation_emissions(rows)

        self.assertAlmostEqual(emission["bright_first_at"], BASE + 3.15)
        self.assertEqual(emission["bright_observer_count"], 2)
        self.assertEqual(emission["strong_bright_observer_count"], 2)

    def test_tail_noise_does_not_rearm_after_immutable_emission(self):
        rows = [
            row(1.0, 9.0, "a"), row(1.0, 9.0, "b"),
            row(2.0, 11.0, "c"), row(2.0, 11.0, "d"),
            row(3.0, 9.0, "a"),
            row(4.0, 11.0, "c"), row(4.0, 11.0, "d"),
            row(5.0, 11.0, "e"), row(5.0, 11.0, "f"),
        ]

        emissions = causal_confirmation_emissions(rows)

        self.assertEqual(len(emissions), 1)
        self.assertEqual(emissions[0]["emission_index"], 0)
        self.assertAlmostEqual(emissions[0]["emitted_at"], BASE + 2.15)

    def test_only_finite_visual_valid_rows_and_normalized_observers_contribute(self):
        rows = [
            row(1.0, 9.0, "raw-a", obs_name=" A "),
            row(2.0, 9.0, "raw-a", obs_name="a"),
            row(2.0, 9.0, "b"),
            row(3.0, 11.0, "c"), row(3.0, 11.0, "d"),
            row(1.0, 8.0, "x", band="V"),
            row(1.0, 8.0, "y", val="Z"),
            {**row(1.0, 8.0, "z"), "mag": "nan"},
        ]

        (emission,) = causal_confirmation_emissions(rows)

        self.assertEqual(emission["bright_observer_count"], 2)
        self.assertEqual(emission["strong_bright_observer_count"], 2)

    def test_independent_emissions_match_reference_on_finite_seeded_fuzz(self):
        generator = random.Random(20261108)
        for replicate in range(500):
            rows = []
            for position in range(generator.randrange(1, 45)):
                observer = generator.choice(("a", "b", "c", "d"))
                day = generator.randrange(0, 12) + generator.choice((0.0, 0.05, 0.10, 0.20))
                magnitude = generator.choice((9.0, 9.5, 9.8, 10.0, 10.2, 10.5, 11.0))
                limit = bool(generator.getrandbits(1))
                obs_name = generator.choice((observer, f" {observer.upper()} ", ""))
                rows.append(row(day, magnitude, observer, limit=limit, obs_name=obs_name,
                                suffix=f"{replicate}-{position}"))

            self.assertEqual(
                causal_confirmation_emissions(rows),
                reference_causal_confirmations(rows),
                msg=f"reference mismatch in fuzz replicate {replicate}",
            )


class X4ScoreAdapterTests(unittest.TestCase):
    @staticmethod
    def episode(onset, end):
        return {
            "onset_lo": BASE + onset - 0.5,
            "onset_hi": BASE + onset + 0.5,
            "onset_t": BASE + onset,
            "onset_method": "fit",
            "end_lo": BASE + end - 0.5,
            "end_hi": BASE + end + 0.5,
            "end_t": BASE + end,
            "end_method": "fit",
            "peak_t": BASE + (onset + end) / 2,
            "confirmed_event": True,
            "confirmation": "observers",
            "gap_split": False,
        }

    def test_adapter_changes_only_operational_metrics(self):
        rows = [
            row(2.0, 9.0, "a"), row(2.0, 9.0, "b"),
            row(4.0, 11.0, "c"), row(4.0, 11.0, "d"),
            row(5.0, 9.8, "e"), row(5.0, 9.9, "f"),
            row(6.0, 11.0, "c"), row(6.0, 11.0, "d"),
        ]
        episodes = [self.episode(2.0, 4.0)]
        truth = [{"id": "event", "onset": BASE + 2.0, "end": BASE + 4.0,
                  "peak_t": BASE + 3.0, "type": "short"}]

        old = x3_score_validation(rows, episodes, truth, BASE, BASE + 10.0)
        new = score_validation(rows, episodes, truth, BASE, BASE + 10.0)

        for old_result, new_result in zip(old, new):
            self.assertEqual(
                {key: value for key, value in old_result.items()
                 if not key.startswith("operational_confirmation_")},
                {key: value for key, value in new_result.items()
                 if not key.startswith("operational_confirmation_")},
            )
            self.assertEqual(old_result["operational_confirmation_emission_count"], 2)
            self.assertEqual(old_result["operational_confirmation_false_emission_count"], 1)
            self.assertEqual(new_result["operational_confirmation_emission_count"], 1)
            self.assertEqual(new_result["operational_confirmation_false_emission_count"], 0)

    def test_reference_disagreement_stops_before_recovery_scoring(self):
        rows = [row(1.0, 9.0, "a")]
        with patch("dnmem.x4_validation.causal_confirmation_emissions", return_value=[]), patch(
                "dnmem.x4_validation._reference_causal_confirmations",
                return_value=[{"emission_index": 0}]), patch(
                "dnmem.x4_validation._x3_score_validation") as recovery_score:
            with self.assertRaisesRegex(RuntimeError, "before recovery scoring"):
                score_validation(rows, [], [], BASE, BASE + 10.0)
        recovery_score.assert_not_called()

    def test_reference_check_returns_independent_ledger(self):
        rows = [
            row(1.0, 9.0, "a"), row(1.0, 9.0, "b"),
            row(2.0, 11.0, "c"), row(2.0, 11.0, "d"),
        ]
        self.assertEqual(reference_checked_emissions(rows),
                         causal_confirmation_emissions(rows))


if __name__ == "__main__":
    unittest.main()
