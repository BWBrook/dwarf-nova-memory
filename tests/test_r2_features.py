import copy
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]

from dnmem import r2_features as features
from dnmem.extract_x5 import decisive_visits
from test_extract import obs
from test_prefix_features import outbursts


def emission(issue=20.15, last=10.15, first=10.15, index=0):
    return {"emission_index": index, "emitted_at": issue,
            "bright_first_at": first, "last_bright_at": last}


class DecoupledPolicyTests(unittest.TestCase):
    def test_anchor_waits_for_aggregate_availability_not_median_time(self):
        rows = [obs(10, 8.5, "a"), obs(35.90, 12, "f"), obs(36.04, 12, "f"), obs(35.91, 12, "g")]
        (schedule,) = features.decoupled_schedule([emission(issue=36.0)], decisive_visits(rows))
        self.assertAlmostEqual(schedule["issue_time"], 36.05)
        self.assertEqual(schedule["anchor"], 36.04)
        self.assertGreater(schedule["anchor_available_at"], 36.0)

    def test_faint_visit_tied_with_last_bright_availability_is_not_selected(self):
        rows = [obs(10, 8.5, "a"), obs(10, 12, "f"), obs(30, 12, "f")]
        (schedule,) = features.decoupled_schedule([emission()], decisive_visits(rows))
        self.assertEqual(schedule["anchor"], 30.0)

    def test_new_threshold_bright_aborts_pending_issue_even_if_not_decisive(self):
        rows = [obs(10, 8.5, "a"), obs(25, 9.7, "b"), obs(30, 12, "f")]
        (schedule,) = features.decoupled_schedule([emission()], decisive_visits(rows))
        self.assertEqual(schedule["status"], "aborted_bright_before_delayed_issue")
        rows = [obs(10, 8.5, "a"), obs(30, 9.7, "b"), obs(30, 12, "f")]
        self.assertEqual(features.decoupled_schedule([emission()], decisive_visits(rows))[0]["status"],
                         "aborted_bright_before_delayed_issue")

    def test_no_faint_and_past_cutoff_are_explicit_pending_states(self):
        rows = [obs(10, 8.5, "a"), obs(30, 10.7, "f")]
        self.assertEqual(features.decoupled_schedule([emission()], decisive_visits(rows))[0]["status"],
                         "no_decisive_faint_before_record_end")
        rows.append(obs(40, 12, "f"))
        self.assertEqual(features.decoupled_schedule([emission()], decisive_visits(rows), stop=35)[0]["status"],
                         "past_issue_cutoff")

    def test_single_raw_bright_observer_is_a_retained_common_fallback(self):
        rows = [obs(0, 12, "a"), obs(0, 12, "b"), obs(10, 8.5, "a"), obs(11, 8.5, "a"),
                obs(20, 12, "a"), obs(20, 12, "b")]
        ledgers = features.prepare_feature_ledgers(rows)
        self.assertEqual(len(ledgers["df"]), 1)
        row = ledgers["df"][0]
        self.assertEqual(row["status"], "insufficient_raw_bright_observers")
        self.assertIsNone(row["clock_anchor"])
        self.assertIsNone(row["mark"])
        self.assertFalse(row["event_eligible"])

    def test_missing_bright_span_does_not_drop_an_eligible_scheduled_issue(self):
        rows = [obs(0, 12, "a"), obs(0, 12, "b"), obs(10, 8.5, "a"), obs(10, 8.6, "b"),
                obs(20, 12, "a"), obs(20, 12, "b")]
        ledgers = features.prepare_feature_ledgers(rows)
        self.assertEqual(len(ledgers["df"]), 1)
        self.assertTrue(ledgers["df"][0]["event_eligible"])
        self.assertIsNone(ledgers["df"][0]["mark"])
        self.assertEqual(ledgers["df"][0]["clock_anchor"], 20.0)


class PrefixFeatureTests(unittest.TestCase):
    def test_later_rows_cannot_change_an_already_issued_df_or_matched_point(self):
        rows = outbursts(events=((100, 112), (150, 160), (200, 212)), nights=range(60, 240))
        original = features.prepare_feature_ledgers(rows)
        first = original["df"][0]
        issue = first["issue_time"]
        changed = [r if float(r["JD"]) <= issue else {**r, "mag": str(float(r["mag"]) - 1.5)} for r in rows]
        changed += [obs(issue + .01, 8, "new-a"), obs(issue + .02, 8.2, "new-b")]
        altered = features.prepare_feature_ledgers(changed)
        self.assertEqual(first, altered["df"][0])
        self.assertEqual(original["point_at_df"][0], altered["point_at_df"][0])
        self.assertEqual(original["point_original"][0], altered["point_original"][0])

    def test_poisoned_interpolated_boundaries_and_confirmation_cannot_change_df(self):
        rows = outbursts(events=((100, 112), (150, 160), (200, 212)), nights=range(60, 240))
        original = features.prepare_feature_ledgers(rows)
        self.assertTrue(any(f["previous_gap"] is not None for f in original["df"]))
        self.assertTrue(any(f["mark"] is not None for f in original["df"]))
        detector = features.x4_episodes
        def poison(rows, threshold):
            episodes = detector(rows, threshold)
            for e in episodes:
                for key in ("end_t", "end_lo", "end_hi", "onset_t", "onset_lo", "onset_hi"):
                    if e[key] is not None:
                        e[key] += 500.0
                e["confirmed_event"] = not e["confirmed_event"]
            return episodes
        with patch("dnmem.r2_features.x4_episodes", side_effect=poison):
            altered = features.prepare_feature_ledgers(rows)
        self.assertEqual(original["df"], altered["df"])
        self.assertEqual(original["df_schedule_audit"], altered["df_schedule_audit"])
        self.assertNotEqual(original["point_original"], altered["point_original"])
        self.assertEqual([f["flux_proxy"] for f in original["point_original"]],
                         [f["flux_proxy"] for f in altered["point_original"]])

    def test_df_and_matched_point_use_identical_issue_population_and_available_histories(self):
        rows = outbursts(events=((100, 112), (150, 160), (200, 212)), nights=range(60, 240))
        ledgers = features.prepare_feature_ledgers(rows)
        self.assertEqual([(f["emission_index"], f["issue_time"]) for f in ledgers["df"]],
                         [(f["emission_index"], f["issue_time"]) for f in ledgers["point_at_df"]])
        self.assertTrue(any(f["issue_delay_days"] > 0 for f in ledgers["df"]))
        for feature in ledgers["point_original"] + ledgers["df"] + ledgers["point_at_df"]:
            self.assertLessEqual(feature["available_at"], feature["issue_time"])
            self.assertTrue(all(h["available_at"] <= feature["issue_time"] for h in feature["gap_history"]))
            history = feature["gap_history"]
            self.assertEqual(len(history), len({h["gap_id"] for h in history}))
            if history and history[-1]["log_gap"] is not None:
                self.assertAlmostEqual(math.log(feature["previous_gap"]), history[-1]["log_gap"])
                self.assertTrue(feature["previous_gap_covered"])

    def test_raw_association_failure_keeps_a_common_fallback_row(self):
        rows = outbursts()
        context = features._prefix_context
        def no_match(*args):
            value = context(*args)
            if args[-1] == "decisive":
                value["episodes"] = []
            return value
        with patch("dnmem.r2_features._prefix_context", side_effect=no_match):
            ledgers = features.prepare_feature_ledgers(rows)
        self.assertGreater(len(ledgers["df"]), 0)
        self.assertTrue(all(f["status"] == "raw_candidate_not_found" and f["clock_anchor"] is None for f in ledgers["df"]))
        self.assertEqual(len(ledgers["df"]), len(ledgers["point_at_df"]))

    def test_future_history_availability_is_rejected(self):
        rows = outbursts()
        def future(context, current, issue, clock):
            return [{"gap_id": "bad", "log_gap": 3.0, "available_at": issue + 1,
                     "raw_gap": math.exp(3), "covered": True}]
        with patch("dnmem.r2_features._gap_history", side_effect=future), self.assertRaisesRegex(ValueError, "future"):
            features.prepare_feature_ledgers(rows)


class AdjacentHistoryTests(unittest.TestCase):
    def context(self):
        episodes = [{"raw_candidate_id": str(i), "confirmed_event": i != 1,
                     "onset_lo": 5 + 40 * i, "onset_t": 6 + 40 * i,
                     "end_t": 20 + 40 * i} for i in range(4)]
        return {"episodes": episodes, "prefix_start": -250, "times": [float(t) for t in range(-50, 151)]}

    def test_unconfirmed_candidate_creates_placeholders_and_never_a_joined_gap(self):
        context = self.context()
        history = features._gap_history(context, 3, 150, "point")
        self.assertEqual(len(history), 3)
        self.assertEqual([h["gap_id"] for h in history], ["0:1", "1:2", "2:3"])
        self.assertEqual([h["log_gap"] for h in history[:2]], [None, None])
        self.assertAlmostEqual(history[-1]["log_gap"], math.log(26))

    def test_uncovered_pair_is_missing_in_history_not_joined_or_imputed(self):
        context = self.context()
        context["times"] = [float(t) for t in range(-50, 106)] + [140.0, 150.0]
        history = features._gap_history(context, 3, 150, "point")
        self.assertEqual(history[-1]["reason"], "coverage_hole")
        self.assertIsNone(history[-1]["log_gap"])
        self.assertFalse(history[-1]["covered"])

    def test_duplicate_pair_would_be_a_duplicate_state_update_and_is_rejected(self):
        context = self.context()
        for e in context["episodes"]:
            e["raw_candidate_id"] = "same"
        with self.assertRaisesRegex(ValueError, "duplicate timing"):
            features._gap_history(context, 3, 150, "point")

    def test_window_boundary_margin_is_required(self):
        context = self.context()
        context["prefix_start"] = 60
        history = features._gap_history(context, 3, 150, "point")
        self.assertTrue(all(h["log_gap"] is None for h in history))
        self.assertEqual(history[-1]["reason"], "incomplete_window_onset")


class BrightSpanFluxProxyTests(unittest.TestCase):
    def proxy(self, rows, issue=30, first=10.2, last=20.2):
        source = emission(issue=issue, first=first + .15, last=last + .15)
        return features.bright_span_flux_proxy(decisive_visits(rows), source, issue)

    def test_constant_excess_has_declared_threshold_flux_day_units(self):
        result = self.proxy([obs(10.2, 9, "a"), obs(12.2, 9, "a")])
        self.assertEqual(result["status"], "available")
        self.assertAlmostEqual(result["value_threshold_flux_days"], 2 * (10 ** .4 - 1))
        self.assertEqual(result["balanced_night_points"], 2)
        self.assertEqual((result["support_start"], result["support_stop"]), (10.2, 12.2))

    def test_limits_never_supply_an_exact_flux_point_or_fill_a_gap(self):
        rows = [obs(10.2, 9, "a"), obs(18.2, 9, "a"), obs(14.2, 22, "limit", "1")]
        result = self.proxy(rows)
        self.assertEqual(result["positive_visits"], 2)
        self.assertEqual(result["status"], "internal_gap_over_seven_days")
        self.assertIsNone(result["value_threshold_flux_days"])
        self.assertAlmostEqual(result["maximum_internal_gap_days"], 8)

    def test_fainter_positive_measurement_contributes_zero_excess(self):
        result = self.proxy([obs(10.2, 9, "a"), obs(11.2, 11, "a"), obs(12.2, 9, "a")])
        self.assertEqual(result["status"], "available")
        self.assertAlmostEqual(result["value_threshold_flux_days"], 10 ** .4 - 1)

    def test_observer_night_balancing_and_no_extrapolation_to_span_edges(self):
        rows = [obs(t, 8, "prolific") for t in (10.2, 10.5, 10.8, 12.2, 12.5, 12.8)]
        rows += [obs(t, 10, "quiet") for t in (10.5, 12.5)]
        result = self.proxy(rows)
        self.assertEqual(result["positive_visits"], 8)
        self.assertEqual(result["observer_nights"], 4)
        self.assertEqual(result["balanced_night_points"], 2)
        self.assertEqual((result["span_start"], result["span_stop"]), (10.2, 12.8))
        self.assertEqual((result["support_start"], result["support_stop"]), (10.5, 12.5))
        self.assertAlmostEqual(result["value_threshold_flux_days"], 2 * (10 ** .4 - 1))

    def test_multiple_visits_on_one_night_do_not_create_integration_support(self):
        result = self.proxy([obs(10.2, 9, "a"), obs(10.6, 9, "b")])
        self.assertEqual(result["status"], "fewer_than_two_balanced_nights")
        self.assertIsNone(result["value_threshold_flux_days"])

    def test_exact_seven_day_gap_is_allowed(self):
        result = self.proxy([obs(10.2, 9, "a"), obs(17.2, 9, "a")])
        self.assertEqual(result["status"], "available")
        self.assertAlmostEqual(result["value_threshold_flux_days"], 7 * (10 ** .4 - 1))

    def test_a_visit_not_yet_closed_cannot_create_a_proxy_span(self):
        result = self.proxy([obs(10.2, 9, "a"), obs(12.2, 9, "a")], issue=12.3)
        self.assertEqual(result["status"], "no_decisive_bright_span")
        self.assertIsNone(result["value_threshold_flux_days"])


if __name__ == "__main__":
    unittest.main()
