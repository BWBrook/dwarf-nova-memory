import copy
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]

from dnmem import r2b_features as features
from dnmem import r2_features as old
from dnmem.extract_x5 import decisive_visits
from test_extract import obs
from test_prefix_features import outbursts


def emission(issue=20.15, last=10.15, first=10.15, index=0):
    return {"emission_index": index, "emitted_at": issue,
            "bright_first_at": first, "last_bright_at": last}


class ScheduleTests(unittest.TestCase):
    def test_threshold_tail_does_not_abort_but_decisive_rise_does(self):
        rows = [obs(10, 8.5, "a"), obs(25, 9.9, "b"), obs(30, 12, "f")]
        original = emission()
        schedule = features.decoupled_schedule([original], decisive_visits(rows))[0]
        self.assertEqual(schedule["status"], "scheduled")
        self.assertEqual(old.decoupled_schedule([original], decisive_visits(rows))[0]["status"],
                         "aborted_bright_before_delayed_issue")
        for magnitude in (9, 8.5):
            changed = [rows[0], obs(25, magnitude, "b"), rows[-1]]
            self.assertEqual(features.decoupled_schedule([original], decisive_visits(changed))[0]["status"],
                             "aborted_decisive_bright_before_delayed_issue")

    def test_anchor_waits_for_visit_closure_and_retains_raw_support(self):
        rows = [obs(10, 8.5, "a"), obs(35.90, 12, "f"), obs(36.04, 12, "f")]
        schedule = features.decoupled_schedule([emission(issue=36)], decisive_visits(rows))[0]
        self.assertAlmostEqual(schedule["issue_time"], 36.05)
        self.assertEqual(schedule["anchor_first_at"], 35.90)
        self.assertEqual(schedule["anchor"], 36.04)

    def test_limit_can_anchor_but_a_weak_limit_cannot(self):
        rows = [obs(10, 8.5, "a"), obs(22, 10.9, "f", "1"), obs(25, 11, "f", "1")]
        schedule = features.decoupled_schedule([emission()], decisive_visits(rows))[0]
        self.assertEqual(schedule["anchor"], 25)

    def test_no_anchor_and_issue_cutoff_are_not_silently_issued(self):
        original = emission()
        self.assertEqual(features.decoupled_schedule([original], decisive_visits([obs(10, 8.5, "a")]))[0]["status"],
                         "no_decisive_faint_before_record_end")
        rows = [obs(10, 8.5, "a"), obs(40, 12, "f")]
        self.assertEqual(features.decoupled_schedule([original], decisive_visits(rows), stop=35)[0]["status"],
                         "past_issue_cutoff")


class CadenceControlTests(unittest.TestCase):
    def context(self, rows):
        return {"rows": rows, "observed": decisive_visits(rows)}

    def test_cadence_uses_raw_positive_times_with_explicit_availability(self):
        rows = [obs(10, 12, "f"), obs(10.05, 12, "f"), obs(10.4, 10.8, "a"),
                obs(19, 10.8, "a"), obs(19.07, 10.8, "a"), obs(20, 12, "f"), obs(20.1, 12, "f")]
        schedule = {"anchor_first_at": 20, "anchor": 20.1, "anchor_available_at": 20.15}
        episode = {"onset_report_eligible": True, "onset_lower_first_at": 10,
                   "onset_lower_last_at": 10.05}
        end, onset = features.cadence_gaps(self.context(rows), schedule, episode, 21)
        self.assertAlmostEqual(end["value_days"], 1.03)
        self.assertAlmostEqual(onset["value_days"], .35)
        self.assertEqual(end["lower_raw_at"], 19.07)
        self.assertAlmostEqual(end["available_at"], 20.15)
        self.assertAlmostEqual(onset["available_at"], 10.55)

    def test_limits_do_not_become_exact_positive_cadence_endpoints(self):
        rows = [obs(10, 12, "f"), obs(11, 10.7, "limit", "1"), obs(19, 10.8, "a"), obs(20, 12, "f")]
        schedule = {"anchor_first_at": 20, "anchor": 20, "anchor_available_at": 20.15}
        episode = {"onset_report_eligible": True, "onset_lower_first_at": 10,
                   "onset_lower_last_at": 10}
        end, onset = features.cadence_gaps(self.context(rows), schedule, episode, 21)
        self.assertEqual(onset["upper_raw_at"], 19)
        self.assertEqual(end["lower_raw_at"], 19)

    def test_unclosed_or_future_reports_cannot_set_a_cadence_gap(self):
        rows = [obs(10, 12, "f"), obs(12.1, 10.8, "a")]
        episode = {"onset_report_eligible": True, "onset_lower_first_at": 10,
                   "onset_lower_last_at": 10}
        _, onset = features.cadence_gaps(self.context(rows), None, episode, 12.2)
        self.assertIsNone(onset["value_days"])
        self.assertEqual(onset["status"], "no_subsequent_positive")

    def test_rate_counts_observer_nights_once_and_includes_limit_visits(self):
        rows = [obs(10.2, 8.8, "a"), obs(10.6, 8.8, "a"), obs(10.8, 12, "limit", "1"),
                obs(12.2, 8.8, "a"), obs(12.2, 8.8, "b"), obs(13, 8.8, "future")]
        source = emission(issue=20, first=10.35, last=12.35)
        rate = features.observing_rate(decisive_visits(rows), source, 20)
        self.assertEqual(rate["observer_nights"], 4)
        self.assertAlmostEqual(rate["value_per_day"], 4 / 3)
        self.assertAlmostEqual(rate["log_value"], math.log(4 / 3))
        self.assertEqual((rate["span_start"], rate["span_stop"]), (10.2, 12.2))
        self.assertLessEqual(rate["available_at"], 20)

    def test_rate_needs_two_distinct_closed_bright_epochs(self):
        rows = [obs(10.2, 8.8, "a"), obs(10.2, 8.8, "b"), obs(12.2, 8.8, "a")]
        source = emission(first=10.35, last=12.35)
        rate = features.observing_rate(decisive_visits(rows), source, 12.3)
        self.assertIsNone(rate["value_per_day"])


class HarmonizedHistoryTests(unittest.TestCase):
    def test_history_uses_past_emissions_own_immutable_scheduled_anchors(self):
        rows = outbursts(events=((100, 112), (150, 160), (200, 212)), nights=range(60, 240))
        ledgers = features.prepare_feature_ledgers(rows)
        schedules = {row["emission_index"]: row for row in ledgers["df_schedule_audit"]}
        self.assertTrue(any(row["previous_gap"] is not None for row in ledgers["df"]))
        nonempty = 0
        for row in ledgers["df"]:
            if row.get("historical_clock_anchor") is not None:
                self.assertEqual(row["historical_clock_anchor"], row["clock_anchor"])
            for gap in row["gap_history"]:
                if gap["anchor_emission_index"] is not None:
                    expected = schedules[gap["anchor_emission_index"]]["anchor"]
                    self.assertEqual(gap["clock_anchor"], expected)
                if gap["log_gap"] is not None:
                    nonempty += 1
                    self.assertAlmostEqual(gap["raw_gap"], gap["onset_support"] - gap["clock_anchor"])
                    self.assertAlmostEqual(gap["log_gap"], math.log(gap["raw_gap"]))
        self.assertGreater(nonempty, 0)

    def test_no_scheduled_anchor_makes_a_placeholder_not_a_join(self):
        rows = outbursts(events=((100, 112), (150, 160), (200, 212)), nights=range(60, 240))
        complete = features.prepare_feature_ledgers(rows)
        emissions = features.causal_confirmations(rows)
        altered = features.prepare_feature_ledgers(rows, emissions=emissions[1:])
        last_complete = complete["df"][-1]
        last_altered = altered["df"][-1]
        self.assertEqual([row["gap_id"] for row in last_complete["gap_history"]],
                         [row["gap_id"] for row in last_altered["gap_history"]])
        self.assertTrue(any(row["reason"] == "no_scheduled_anchor" for row in last_altered["gap_history"]))
        self.assertTrue(all(row["log_gap"] is None for row in last_altered["gap_history"]
                            if row["reason"] == "no_scheduled_anchor"))

    def test_ambiguous_anchor_emissions_are_not_chosen_arbitrarily(self):
        episode = {"raw_peak_t": 10}
        schedules = {0: {"status": "scheduled", "issue_time": 20, "anchor": 19},
                     1: {"status": "scheduled", "issue_time": 21, "anchor": 20}}
        emissions = {i: emission(issue=20+i, first=5, last=12, index=i) for i in range(2)}
        anchor, reason = features._scheduled_anchor(episode, schedules, emissions, 25)
        self.assertIsNone(anchor)
        self.assertEqual(reason, "ambiguous_scheduled_anchor")

    def test_future_scheduled_anchor_cannot_enter_an_earlier_history(self):
        episode = {"raw_peak_t": 10}
        schedules = {0: {"status": "scheduled", "issue_time": 21, "anchor": 20}}
        emissions = {0: emission(first=5, last=12)}
        self.assertEqual(features._scheduled_anchor(episode, schedules, emissions, 20),
                         (None, "no_scheduled_anchor"))

    def test_scheduled_anchor_at_or_before_raw_peak_is_unusable(self):
        episode = {"raw_peak_t": 10}
        emissions = {0: emission(first=5, last=12)}
        for anchor in (9, 10):
            schedules = {0: {"status": "scheduled", "issue_time": 21, "anchor": anchor}}
            self.assertEqual(features._scheduled_anchor(episode, schedules, emissions, 25),
                             (None, "scheduled_anchor_not_after_peak"))


class CausalLedgerTests(unittest.TestCase):
    def rows(self):
        return outbursts(events=((100, 112), (150, 160), (200, 212)), nights=range(60, 240))

    def test_later_photometry_cannot_change_issued_features(self):
        rows = self.rows()
        original = features.prepare_feature_ledgers(rows)
        issue = original["df"][1]["issue_time"]
        changed = [r if float(r["JD"]) <= issue else {**r, "mag": str(float(r["mag"]) - 1.5)} for r in rows]
        changed += [obs(issue + .01, 8, "new-a"), obs(issue + .02, 8.2, "new-b")]
        altered = features.prepare_feature_ledgers(changed)
        for name in ("df", "point_at_df", "point_original"):
            before = [r for r in original[name] if r["issue_time"] <= issue]
            after = [r for r in altered[name] if r["issue_time"] <= issue]
            self.assertEqual(before, after)

    def test_fitted_end_and_confirmation_poisoning_cannot_change_df(self):
        rows = self.rows()
        original = features.prepare_feature_ledgers(rows)
        detector = old.x4_episodes
        def poison(rows, threshold):
            episodes = detector(rows, threshold)
            for episode in episodes:
                for key in ("end_t", "end_lo", "end_hi", "onset_t", "onset_lo", "onset_hi"):
                    if episode[key] is not None:
                        episode[key] += 500
                episode["confirmed_event"] = not episode["confirmed_event"]
            return episodes
        with patch("dnmem.r2_features.x4_episodes", side_effect=poison):
            altered = features.prepare_feature_ledgers(rows)
        self.assertEqual(original["df"], altered["df"])
        self.assertNotEqual(original["point_original"], altered["point_original"])

    def test_pairing_and_full_fallback_population_are_preserved(self):
        rows = [obs(0, 12, "a"), obs(0, 12, "b"), obs(10, 8.5, "a"), obs(11, 8.5, "a"),
                obs(20, 12, "a"), obs(20, 12, "b")]
        ledgers = features.prepare_feature_ledgers(rows)
        self.assertEqual(len(ledgers["df"]), 1)
        df, point = ledgers["df"][0], ledgers["point_at_df"][0]
        self.assertEqual((df["emission_index"], df["issue_time"]), (point["emission_index"], point["issue_time"]))
        self.assertEqual(df["status"], "insufficient_raw_bright_observers")
        self.assertIsNone(df["clock_anchor"])
        self.assertIsNone(df["mark"])

    def test_failed_current_own_anchor_association_is_common_fallback(self):
        rows = outbursts(events=((100, 112),), nights=range(60, 140))
        for reason in ("ambiguous_scheduled_anchor", "scheduled_anchor_not_after_peak", "no_scheduled_anchor"):
            with patch("dnmem.r2b_features._scheduled_anchor", return_value=(None, reason)):
                ledgers = features.prepare_feature_ledgers(rows)
            self.assertEqual(len(ledgers["df"]), 1)
            row = ledgers["df"][0]
            self.assertEqual(row["status"], "current_" + reason)
            self.assertFalse(row["event_eligible"])
            self.assertIsNone(row["clock_anchor"])
            self.assertIsNone(row["historical_clock_anchor"])
            self.assertIsNone(row["mark"])

    def test_point_prediction_fields_retain_original_windowed_convention(self):
        rows = self.rows()
        previous = old.prepare_feature_ledgers(rows)
        current = features.prepare_feature_ledgers(rows)
        keys = ("clock_anchor", "mark", "previous_gap", "previous_gap_covered", "gap_history", "frozen_point_reference")
        for a, b in zip(previous["point_original"], current["point_original"]):
            self.assertEqual({key: a[key] for key in keys}, {key: b[key] for key in keys})

    def test_control_and_history_availability_are_bounded_by_issue(self):
        ledgers = features.prepare_feature_ledgers(self.rows())
        for name in ("df", "point_original", "point_at_df"):
            for feature in ledgers[name]:
                issue = feature["issue_time"]
                for field in ("cadence_end", "cadence_on", "observer_rate", "flux_proxy"):
                    if feature[field]["available_at"] is not None:
                        self.assertLessEqual(feature[field]["available_at"], issue)
                for gap in feature["gap_history"]:
                    self.assertLessEqual(gap["available_at"], issue)
                    for field in ("left_cadence_end_available_at", "right_cadence_on_available_at"):
                        if gap.get(field) is not None:
                            self.assertLessEqual(gap[field], issue)

    def test_date_cutoff_filters_ignored_later_rows_before_extraction(self):
        rows = self.rows()
        stop = 220
        a = features.prepare_feature_ledgers([r for r in rows if float(r["JD"]) < stop], stop=stop)
        b = features.prepare_feature_ledgers(rows + [obs(250, 8, "later")], stop=stop)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
