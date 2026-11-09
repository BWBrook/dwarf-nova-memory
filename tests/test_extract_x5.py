import copy
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts"), str(ROOT / "tests")]

from dnmem.extract_x5 import decisive_visits, x5_episodes
from dnmem.extract_x4 import x4_episodes
from r2a_observation_diagnostics import contradiction_diagnostics, diagnostics, window_visit_diagnostics
from test_extract import obs
from test_prefix_features import outbursts


def candidate(peak, confirmed=True, magnitude=8.5):
    return {"peak_t": peak, "peak_mag": magnitude, "confirmed_event": confirmed,
            "onset_t": peak - 2, "onset_lo": peak - 2.2, "onset_hi": peak - 1.8,
            "end_t": peak + 3, "end_lo": peak + 2.8, "end_hi": peak + 3.2}


def fixture():
    rows = [obs(t, m, who) for t, m, who in ((0, 8.5, "a"), (1, 8.7, "a"), (5, 12, "a"),
                                            (30, 8.9, "a"), (31, 8.5, "a"), (32, 8.8, "a"),
                                            (35, 12, "a"), (60, 8.5, "a"))]
    return rows, [candidate(0), candidate(31), candidate(60, False)]


class DecisiveVisitTests(unittest.TestCase):
    def test_limit_direction_and_positive_estimate_precedence(self):
        rows = [obs(5, 11.2, "limit", "1"), obs(6, 9, "weak-limit", "1"),
                obs(7, 10.5, "mixed"), obs(7.1, 12, "mixed", "1")]
        visits = decisive_visits(rows)
        self.assertEqual([(v["observer"], v["decisive"]) for v in visits], [("limit", "F"), ("mixed", "N")])
        self.assertIsNone(visits[0]["value"])
        self.assertEqual(visits[0]["faint_level"], 11.2)
        self.assertEqual(visits[1]["faint_level"], 10.5)

    def test_raw_support_and_closed_aggregation_availability_are_distinct(self):
        rows = [obs(4.9, 11.8, "q"), obs(5.0, 12.2, "q")]
        (v,) = decisive_visits(rows)
        self.assertAlmostEqual(v["t"], 4.95)
        self.assertEqual((v["first_at"], v["last_at"]), (4.9, 5.0))
        self.assertAlmostEqual(v["available_at"], 5.05)
        self.assertNotIn(v["t"], [float(r["JD"]) for r in rows])

    def test_threshold_rescaling_does_not_reuse_ss_cyg_decisive_levels(self):
        rows = [obs(5, 15, "f"), obs(30, 11, "b")]
        visits = decisive_visits(rows, threshold=13, margin=2)
        self.assertEqual([v["decisive"] for v in visits], ["F", "B"])

    def test_duplicate_identity_or_invalid_visit_support_is_rejected(self):
        row = obs(5, 12, "a")
        with self.assertRaisesRegex(ValueError, "unique"):
            decisive_visits([row, row])
        votes = [{"ids": [row["obsID"]], "value": 12.0, "t": 6.0, "cls": "F", "observer": "a"}]
        with self.assertRaisesRegex(ValueError, "support"):
            decisive_visits([row], votes=votes)


class CorrectedWindowTests(unittest.TestCase):
    def test_actual_candidate_detection_is_unchanged_and_points_are_not_refitted(self):
        rows = outbursts()
        frozen = x4_episodes(rows)
        actual = x5_episodes(rows)
        self.assertEqual(len(actual), len(frozen))
        self.assertEqual(len(actual), 2)
        self.assertTrue(actual[1]["onset_report_available"])
        for old, new in zip(frozen, actual):
            for key, value in old.items():
                self.assertEqual(new[key], value)

    def test_quiescence_prevents_previous_bright_tail_from_removing_lower_bound(self):
        rows, candidates = fixture()
        before = copy.deepcopy(candidates)
        episodes = x5_episodes(rows, episodes=candidates)
        e = episodes[1]
        self.assertEqual((e["quiescence_at"], e["onset_report_lo"], e["onset_report_hi"]), (5.0, 5.0, 30.0))
        self.assertEqual(e["onset_status"], "available")
        self.assertTrue(e["onset_report_eligible"])
        self.assertEqual(candidates, before)
        for key, value in candidates[1].items():
            self.assertEqual(e[key], value)

    def test_report_bounds_use_raw_support_not_representative_medians(self):
        rows, candidates = fixture()
        rows = [r for r in rows if float(r["JD"]) not in (5, 30)]
        rows += [obs(4.9, 12, "f"), obs(5.0, 12, "f"), obs(29.9, 8.8, "b"), obs(30.0, 8.8, "b")]
        e = x5_episodes(rows, episodes=candidates)[1]
        self.assertEqual((e["onset_report_lo"], e["onset_report_hi"]), (4.9, 30.0))
        self.assertAlmostEqual(e["onset_report_lo_rep"], 4.95)
        self.assertAlmostEqual(e["onset_report_hi_rep"], 29.95)

    def test_unconfirmed_neighbour_peak_still_limits_the_search(self):
        rows, candidates = fixture()
        rows += [obs(20, 8.5, "x"), obs(25, 12, "x")]
        candidates.insert(1, candidate(20, False))
        e = x5_episodes(rows, episodes=candidates)[2]
        self.assertEqual(e["previous_peak_at"], 20)
        self.assertEqual(e["quiescence_at"], 25.0)
        self.assertEqual(e["onset_report_lo"], 25.0)

    def test_missing_quiescence_and_faint_peak_are_explicit_no_substitution(self):
        rows, candidates = fixture()
        no_quiet = x5_episodes([r for r in rows if float(r["JD"]) != 5], episodes=candidates)[1]
        self.assertEqual(no_quiet["onset_status"], "no_quiescence_report")
        self.assertFalse(no_quiet["onset_report_available"])
        rows = [dict(r, mag="9.5") if 30 <= float(r["JD"]) <= 32 else r for r in rows]
        candidates[1]["peak_mag"] = 9.5
        faint = x5_episodes(rows, episodes=candidates)[1]
        self.assertEqual(faint["onset_status"], "faint_peak")
        self.assertIsNone(faint["onset_report_hi"])
        self.assertEqual(x5_episodes(rows, episodes=candidates)[0]["onset_status"], "left_record_boundary")

    def test_simultaneous_opposite_decisive_votes_are_visible_and_ineligible(self):
        rows, candidates = fixture()
        rows.append(obs(30, 12, "contradictor"))
        e = x5_episodes(rows, episodes=candidates)[1]
        self.assertTrue(e["onset_report_available"])
        self.assertFalse(e["onset_report_eligible"])
        self.assertIn("contested_decisive_epoch", e["onset_flags"])

    def test_overlapping_raw_visit_supports_are_not_treated_as_ordered_states(self):
        rows, candidates = fixture()
        rows = [r for r in rows if float(r["JD"]) != 30]
        rows += [obs(29.90, 12, "f"), obs(30.00, 12, "f"), obs(29.94, 8.8, "b"), obs(30.04, 8.8, "b")]
        e = x5_episodes(rows, episodes=candidates)[1]
        self.assertEqual((e["onset_report_lo"], e["onset_report_hi"]), (29.90, 30.04))
        self.assertIn("overlapping_or_touching_visit_support", e["onset_flags"])
        self.assertFalse(e["onset_report_eligible"])

    def test_decisive_faint_after_rise_is_a_recrossing_warning(self):
        rows, candidates = fixture()
        rows.append(obs(30.5, 12, "f"))
        e = x5_episodes(rows, episodes=candidates)[1]
        self.assertEqual(e["rise_decisive_faint_after_bright_count"], 1)
        self.assertIn("decisive_faint_after_bright_before_peak", e["onset_flags"])
        self.assertFalse(e["onset_report_eligible"])

    def test_end_anchor_stops_at_first_faint_and_cannot_follow_next_rise(self):
        rows, candidates = fixture()
        rows += [obs(32.1, 8.8, "a"), obs(35.1, 12, "a"), obs(59, 8.6, "b")]
        e = x5_episodes(rows, episodes=candidates)[1]
        self.assertEqual((e["end_report_lo"], e["end_report_hi"]), (32.0, 35.1))
        self.assertEqual(e["end_decisive_at"], 35.1)
        self.assertAlmostEqual(e["end_decisive_available_at"], 35.15)
        self.assertAlmostEqual(e["bright_span"], 2.05)
        self.assertTrue(e["post_end_decisive_bright_before_next_peak"])
        self.assertTrue(e["end_report_eligible"])

    def test_prefix_reconstruction_never_borrows_later_rows_or_catalogues(self):
        rows, candidates = fixture()
        candidates = candidates[:2]
        later = rows + [obs(35.1, 8.0, "a")]
        with patch("dnmem.extract_x5.x4_episodes", return_value=candidates) as detector:
            a = x5_episodes(rows, as_of=35.05)
            b = x5_episodes(later, as_of=35.05)
        self.assertEqual(a, b)
        self.assertTrue(all(float(r["JD"]) <= 35.05 for call in detector.call_args_list for r in call.args[0]))
        self.assertGreater(a[1]["end_decisive_available_at"], 35.05)
        with self.assertRaisesRegex(ValueError, "cached"):
            x5_episodes(rows, episodes=candidates, as_of=35.05)


class GainFreeDiagnosticTests(unittest.TestCase):
    def test_rate_report_separates_forced_detection_endpoint(self):
        rows, candidates = fixture()
        episodes = x5_episodes(rows, episodes=candidates)
        reports = decisive_visits(rows)
        result = window_visit_diagnostics(episodes[1], reports)
        self.assertEqual(result["inside_including_upper_visits"], 1)
        self.assertEqual(result["strict_interior_visits"], 0)

    def test_cross_observer_contradictions_count_visits_not_report_pairs(self):
        rows, candidates = fixture()
        rows += [obs(10, 12, "f"), obs(10.1, 8.8, "b"), obs(10.2, 8.7, "c")]
        observed = decisive_visits(rows)
        result = contradiction_diagnostics(x5_episodes(rows, episodes=candidates), observed)
        self.assertEqual(result["all"]["visits_with_opposite_other_observer"], 3)
        self.assertLessEqual(result["all"]["fraction"], 1)

    def test_aggregate_contains_no_observer_names_or_event_table(self):
        rows, candidates = fixture()
        shift = 2451545.0
        rows = [dict(r, JD=str(float(r["JD"]) + shift)) for r in rows]
        candidates = [{k: v + shift if k in ("peak_t", "onset_t", "onset_lo", "onset_hi", "end_t", "end_lo", "end_hi") else v for k, v in e.items()} for e in candidates]
        summary = diagnostics(x5_episodes(rows, episodes=candidates), decisive_visits(rows))
        self.assertEqual(summary["confirmed_candidates"]["episodes"], 2)
        self.assertIn("2000", summary["confirmed_by_decade"])
        self.assertNotIn("observer", summary)
        self.assertNotIn("episodes", summary)


if __name__ == "__main__":
    unittest.main()
