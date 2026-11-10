import copy
import json
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dnmem.g3a_qualification import (CUTOFF, LAST_DECADE_START, base_convergence, coverage_summary,
                                      morphology_screen, prepare_df_features, qualify_star, summarize_features,
                                      validated_rows)
from dnmem.r2b_models import fit_bases


def observation(jd, magnitude, who="a", limit="0"):
    return {"JD": str(jd), "mag": str(magnitude), "band": "Vis.", "val": "V",
            "fainterThan": limit, "obsName": who, "by": who,
            "obsID": f"{jd}-{magnitude}-{who}-{limit}"}


def timing_fixture(n=48):
    rng = np.random.default_rng(305781)
    features, evidence = [], []
    for index in range(n):
        anchor = LAST_DECADE_START + index * 60.
        history = rng.normal(3.5, .25, 6)
        wait = math.exp(3.5 + .12 * (history[-1] - 3.5) / .25 + rng.normal(0, .3))
        features.append({"emission_index": index, "issue_time": anchor + 1., "available_at": anchor + 1.,
                         "clock_anchor": anchor, "mark": 6. + index % 13,
                         "previous_gap": math.exp(history[-1]), "previous_gap_covered": True,
                         "gap_history": [{"log_gap": value, "available_at": anchor} for value in history]})
        evidence.append({"emission_index": index, "issue_time": anchor + 1., "kind": "interval",
                         "onset_lo": anchor + wait - .2, "onset_hi": anchor + wait + .2,
                         "computed_as_of": CUTOFF, "evidence_available_at": CUTOFF})
    return features, evidence


class NativeBoundaryTests(unittest.TestCase):
    def test_post_split_nonfinite_wrong_band_and_duplicates_are_rejected(self):
        row = observation(CUTOFF - 3, 14)
        for change in ({"JD": str(CUTOFF)}, {"JD": "nan"}, {"mag": "inf"},
                       {"band": "V"}, {"val": "Z"}, {"fainterThan": ""}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validated_rows([{**row, **change}])
        with self.assertRaises(ValueError):
            validated_rows([row, row])
        with self.assertRaises(ValueError):
            qualify_star([], "SS Aur", 13.5, stop=CUTOFF + 1)

    def test_limits_remain_bounds_and_repeat_observer_reports_do_not_inflate_nights(self):
        base = LAST_DECADE_START
        rows = [observation(base + .6, 12., limit="1"),
                observation(base + 1.6, 15., limit="1"),
                observation(base + 1.65, 15.2, limit="1"),
                observation(base + 1.66, 14., "b")]
        result = coverage_summary(validated_rows(rows), 13.5)
        self.assertEqual(result["limits"], 3)
        self.assertEqual(result["observer_nights"], 3)
        self.assertEqual(result["observed_nights"], 2)
        self.assertEqual(result["informative_visits"], 2)
        self.assertEqual(result["informative_nights"], 1)
        self.assertEqual(result["annual"][0]["year"], 1980)
        self.assertNotIn("a", json.dumps(result).split('"'))

    def test_empty_and_sparse_history_fail_qualification_without_fitting_a_mark(self):
        with patch("dnmem.r2b_models.fit_mark", side_effect=AssertionError("mark fit forbidden")), \
             patch("dnmem.r2b_scoring.score_contrast", side_effect=AssertionError("gain forbidden")):
            empty = qualify_star([], "RU Peg", 11.5)
            base = LAST_DECADE_START
            rows = [observation(base + day + .6, 14 if day < 5 or day > 12 else 10., who)
                    for day in range(22) for who in ("a", "b")]
            sparse = qualify_star(rows, "RU Peg", 11.5)
        self.assertFalse(empty["qualified"])
        self.assertIsNone(empty["x5_eligible_fraction"])
        self.assertEqual(sparse["confirmed_events"], 1)
        self.assertEqual(sparse["x5_eligible_events"], 0)
        self.assertFalse(sparse["qualified"])
        self.assertEqual(sparse["x5_margin"], 1.)
        json.dumps(sparse, allow_nan=False)

    def test_custom_emission_cannot_claim_bright_information_after_issue(self):
        emissions = [{"emission_index": 0, "emitted_at": LAST_DECADE_START + 1,
                      "bright_first_at": LAST_DECADE_START, "last_bright_at": LAST_DECADE_START + 2}]
        with self.assertRaises(ValueError):
            prepare_df_features([], 13.5, emissions=emissions)


class MorphologyTests(unittest.TestCase):
    def plateau(self, start, days, observers=("a", "b"), spacing=1):
        return [observation(start + day + .6, 11., who)
                for day in range(0, days + 1, spacing) for who in observers]

    def test_long_or_repeated_supported_plateaus_fail(self):
        start = LAST_DECADE_START
        long = morphology_screen(self.plateau(start, 60), 13.5)
        self.assertFalse(long["passed"])
        self.assertEqual(long["runs_at_least_60_days"], 1)
        repeated = []
        for offset in (0, 70, 140):
            repeated.extend(self.plateau(start + offset, 40))
        self.assertFalse(morphology_screen(repeated, 13.5)["passed"])
        self.assertTrue(morphology_screen(self.plateau(start, 39), 13.5)["passed"])

    def test_sparse_or_single_observer_runs_do_not_supply_supported_plateau_evidence(self):
        start = LAST_DECADE_START
        for rows in (self.plateau(start, 80, spacing=8), self.plateau(start, 80, observers=("a",))):
            result = morphology_screen(rows, 13.5)
            self.assertTrue(result["passed"])
            self.assertEqual(result["supported_runs"], 0)


class OutcomeSupportTests(unittest.TestCase):
    def test_missing_marks_uncovered_history_and_zero_exposure_are_separate(self):
        features, evidence = timing_fixture(4)
        features[0]["mark"] = None
        features[1]["previous_gap"] = None
        features[1]["previous_gap_covered"] = False
        features[1]["gap_history"][-1]["log_gap"] = None
        evidence[2].update(kind="right_censored", censor_at=features[2]["issue_time"])
        evidence[3].update(kind="right_censored", censor_at=features[3]["issue_time"] + 1)
        counts, normalized = summarize_features(features, evidence)
        self.assertEqual(counts["df_feature_supported_marked"], 2)
        self.assertEqual(counts["df_outcome_supported_marked"], 1)
        self.assertEqual(counts["df_zero_exposure_outcomes"], 1)
        self.assertEqual(counts["supported_last_decade_count"], 1)
        self.assertEqual(normalized[2]["kind"], "excluded")
        self.assertEqual(evidence[2]["kind"], "right_censored")

    def test_reversed_interval_future_features_and_future_outcomes_are_not_repaired(self):
        features, evidence = timing_fixture(2)
        bad = copy.deepcopy(evidence)
        bad[0]["onset_lo"], bad[0]["onset_hi"] = bad[0]["onset_hi"], bad[0]["onset_lo"]
        with self.assertRaises(ValueError):
            summarize_features(features, bad)
        bad = copy.deepcopy(evidence)
        bad[0]["evidence_available_at"] = CUTOFF + 1
        with self.assertRaises(ValueError):
            summarize_features(features, bad)
        features[0]["gap_history"][0]["available_at"] = features[0]["issue_time"] + 1
        with self.assertRaises(ValueError):
            summarize_features(features, evidence)


class ConvergenceAndIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.features, cls.evidence = timing_fixture()
        cls.base = fit_bases([{**row, "mark": None} for row in cls.features], cls.evidence,
                             CUTOFF, rungs=("B0",))["B0"]

    def test_actual_unmarked_multistart_fit_and_no_mark_path(self):
        with patch("dnmem.g3a_qualification.fit_bases", wraps=fit_bases) as fitting, \
             patch("dnmem.r2b_models.fit_mark", side_effect=AssertionError("forbidden")):
            result = base_convergence(self.features, self.evidence)
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["declared_starts"], 6)
        self.assertTrue(all(row["mark"] is None for row in fitting.call_args.args[0]))
        self.assertEqual(fitting.call_args.kwargs["rungs"], ("B0",))
        self.assertNotIn("objective", json.dumps(result))
        self.assertNotIn("parameters", result)

    def test_failed_start_rank_loss_or_bound_parameter_fails(self):
        for change in ("start", "rank", "bound"):
            base = copy.deepcopy(self.base)
            if change == "start":
                base.metadata["remaining_fit"]["attempts"][0]["successful"] = False
            elif change == "rank":
                base.metadata["base_fit"]["design_rank"] = 2
            else:
                base.metadata["base_fit"]["attempts"][0]["parameters"][1] = 3.
            with self.subTest(change=change), patch("dnmem.g3a_qualification.fit_bases", return_value={"B0": base}):
                self.assertFalse(base_convergence(self.features, self.evidence)["passed"])

    def test_external_eclipse_boolean_does_not_change_non_eclipse_gates(self):
        episodes = [{"confirmed_event": True, "onset_report_available": True, "onset_report_eligible": True}]
        with patch("dnmem.g3a_qualification.x4_episodes", return_value=[]), \
             patch("dnmem.g3a_qualification.x5_episodes", return_value=episodes), \
             patch("dnmem.g3a_qualification.prepare_df_features", return_value=(self.features, [])) as preparing, \
             patch("dnmem.g3a_qualification.outcome_evidence", return_value=self.evidence), \
             patch("dnmem.g3a_qualification.fit_bases", return_value={"B0": self.base}), \
             patch("dnmem.r2b_models.fit_mark", side_effect=AssertionError("forbidden")), \
             patch("dnmem.r2b_scoring.score_contrast", side_effect=AssertionError("forbidden")):
            held = qualify_star([], "U Gem", 12., emissions=[{"sentinel": True}])
            passed = qualify_star([], "U Gem", 12., eclipse_passed=True)
            ordinary = qualify_star([], "SS Aur", 13.5)
        self.assertTrue(held["ordinary_passed"])
        self.assertFalse(held["qualified"])
        self.assertTrue(passed["qualified"])
        self.assertTrue(ordinary["qualified"])
        self.assertEqual(preparing.call_args_list[0].kwargs["emissions"], [{"sentinel": True}])
        self.assertEqual(held["df_outcome_supported_marked"], 48)
        self.assertEqual(held["supported_last_decade_rate_per_year"], 4.8)
        json.dumps(held, allow_nan=False)

    def test_forty_gate_counts_outcome_supported_rows_not_feature_only_rows(self):
        evidence = copy.deepcopy(self.evidence)
        for row in evidence[:9]:
            row.update(kind="right_censored", censor_at=row["issue_time"])
        episodes = [{"confirmed_event": True, "onset_report_available": True, "onset_report_eligible": True}]
        with patch("dnmem.g3a_qualification.x4_episodes", return_value=[]), \
             patch("dnmem.g3a_qualification.x5_episodes", return_value=episodes), \
             patch("dnmem.g3a_qualification.prepare_df_features", return_value=(self.features, [])), \
             patch("dnmem.g3a_qualification.outcome_evidence", return_value=evidence), \
             patch("dnmem.g3a_qualification.fit_bases", return_value={"B0": self.base}):
            result = qualify_star([], "SS Aur", 13.5)
        self.assertEqual(result["df_feature_supported_marked"], 48)
        self.assertEqual(result["df_outcome_supported_marked"], 39)
        self.assertFalse(result["ordinary_passed"])


if __name__ == "__main__":
    unittest.main()
