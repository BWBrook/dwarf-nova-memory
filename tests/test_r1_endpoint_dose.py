import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np
from scipy.stats import lognorm

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]

import r1_endpoint_dose as dose
from dnmem.directional_forecast import fit_directional


def episode(onset, end, key):
    return {"onset_t": onset, "onset_lo": onset - 0.2, "onset_hi": onset + 0.2,
            "end_t": end, "end_lo": end - 0.2, "end_hi": end + 0.2,
            "peak_t": onset + 1, "confirmed_event": True, "event_key": key}


def context():
    episodes = [episode(0.0, 10.0, "older"), episode(30.0, 42.0, "previous"),
                episode(70.0, 80.0, "current")]
    feature = {"emission_index": 0, "emitted_at": 85.0, "issue_time": 85.0,
               "bright_first_at": 71.0, "prefix_start": -315.0, "onset_t": 70.0,
               "end_t": 80.0, "end_lo": 79.8, "end_hi": 80.2,
               "duration": 10.0, "age_at_issue": 5.0, "landmark_available": True,
               "previous_end_t": 42.0, "previous_gap": 28.0, "previous_gap_covered": True,
               "previous_longest_hole": 1.0, "previous_duration": 12.0,
               "earlier_gaps": [math.log(20.0)]}
    return {"feature": feature, "episodes": episodes, "current": 2,
            "times": [float(i) for i in range(-315, 86)]}


def training_fixture(n=80):
    rng = np.random.default_rng(4102)
    features, evidence = [], []
    for i in range(n):
        end = 100.0 + i * 100.0
        wait = float(rng.lognormal(math.log(30.0), 0.35))
        mark = 9.0 + i % 5
        f = {"emission_index": i, "issue_time": end + 2.0, "end_t": end,
             "end_lo": end, "end_hi": end, "landmark_available": True,
             "onset_t": end - mark, "duration": mark,
             "previous_duration": 8.0 + i % 4, "previous_gap": 20.0 + i % 7,
             "previous_gap_covered": True, "earlier_gaps": [math.log(20.0 + i % 3)]}
        e = {"emission_index": i, "issue_time": end + 2.0, "kind": "point",
             "onset_t": end + wait, "evidence_available_at": 10000.0,
             "computed_as_of": 10000.0, "reason": "true_onset"}
        features.append(f)
        evidence.append(e)
    return features, evidence


class EndpointDoseTests(unittest.TestCase):
    def test_zero_jitter_preserves_original_features(self):
        c = context()
        feature, flags = dose.jitter_feature(c, 0.0, "null", 0)
        self.assertEqual(flags, {})
        for key, value in c["feature"].items():
            self.assertEqual(feature[key], value, key)

    def test_one_event_error_propagates_to_duration_age_gap_history_and_lag(self):
        c = context()
        errors = {"older": 1.0, "previous": 2.0, "current": -3.0}
        with patch.object(dose, "dose_z", side_effect=lambda case, replicate, key, base: errors[key]):
            f, flags = dose.jitter_feature(c, 1.0, "null", 0)
        self.assertEqual(flags, {})
        self.assertEqual(f["duration"], 7.0)
        self.assertEqual(f["age_at_issue"], 8.0)
        self.assertEqual(f["previous_gap"], 26.0)
        self.assertEqual(f["previous_duration"], 14.0)
        self.assertEqual(f["earlier_gaps"], [math.log(19.0)])
        self.assertEqual(f["issue_time"], c["feature"]["issue_time"])

    def test_dose_vector_is_paired_across_sigma(self):
        c = context()
        a, _ = dose.jitter_feature(c, 1.0, "structured", 3)
        b, _ = dose.jitter_feature(c, 2.0, "structured", 3)
        self.assertEqual(b["r1_added_end_error"], 2 * a["r1_added_end_error"])
        self.assertEqual(a["r1_event_key"], b["r1_event_key"])

    def test_future_jittered_end_disables_landmark_without_clipping(self):
        with patch.object(dose, "dose_z", return_value=10.0):
            f, flags = dose.jitter_feature(context(), 1.0, "null", 0)
        self.assertEqual(f["end_t"], 90.0)
        self.assertEqual(f["age_at_issue"], -5.0)
        self.assertFalse(f["landmark_available"])
        self.assertEqual(flags["end_after_issue"], 1)

    def test_negative_duration_is_exposed_and_mark_missing(self):
        c = context()
        with patch.object(dose, "dose_z", side_effect=lambda case, rep, key, base: -20.0 if key == "current" else 0.0):
            f, flags = dose.jitter_feature(c, 1.0, "null", 0)
        self.assertIsNone(f["duration"])
        self.assertEqual(f["r1_raw_duration"], -10.0)
        self.assertEqual(f["end_t"], 60.0)
        self.assertEqual(flags["nonpositive_duration"], 1)

    def test_nonpositive_gap_and_history_are_flagged(self):
        with patch.object(dose, "dose_z", return_value=50.0):
            f, flags = dose.jitter_feature(context(), 1.0, "null", 0)
        self.assertIsNone(f["previous_gap"])
        self.assertEqual(f["r1_raw_previous_gap"], -22.0)
        self.assertEqual(f["earlier_gaps"], [])
        self.assertEqual(flags["nonpositive_previous_gap"], 1)
        self.assertEqual(flags["nonpositive_history_gap"], 1)

    def test_raw_bright_membership_unifies_episode_identity_when_peak_changes(self):
        ledger = [{"emitted_at": t, "issue_time": t, "bright_first_at": 5.0} for t in (20.0, 25.0)]
        a = episode(1.0, 10.0, "unused")
        b = dict(a, peak_t=6.0)
        with patch.object(dose, "visits", return_value=[]), \
             patch.object(dose, "x4_episodes", side_effect=[[a], [b]]), \
             patch.object(dose, "bright_groups", side_effect=[[["b", "c"]], [["a", "b"]]]):
            contexts = dose.prepare_contexts([], ledger)
        self.assertEqual([c["episodes"][0]["event_key"] for c in contexts], ["a", "a"])

    def test_fixed_anchors_exclude_repeat_uncompleted_and_missed_cycle_before_issue(self):
        truth = [{"id": "a", "block": 0, "onset": 10.0, "end": 20.0},
                 {"id": "b", "block": 0, "onset": 30.0, "end": 40.0},
                 {"id": "c", "block": 0, "onset": -5.0, "end": -1.0}]
        meta = {"blocks": [{"block": 0, "synthetic_start": 0.0, "synthetic_stop": 100.0}]}
        ledger = [{"emission_index": i, "issue_time": issue, "bright_first_at": bright}
                  for i, (issue, bright) in enumerate(((21.0, 15.0), (22.0, 15.0), (35.0, 35.0),
                                                      (45.0, 15.0), (46.0, 35.0), (47.0, 5.0), (48.0, -2.0)))]
        anchors, counts, _ = dose.fixed_anchors(ledger, truth, meta)
        self.assertEqual(anchors, {0: "a"})
        self.assertEqual(sum(counts.values()), len(ledger))
        self.assertEqual(counts["repeat_truth_event"], 3)
        self.assertEqual(counts["true_event_not_completed"], 1)
        self.assertEqual(counts["next_true_onset_before_issue"], 1)
        self.assertEqual(counts["unmatched_or_false_emission"], 1)

    def test_extracted_backoff_does_not_replace_true_administrative_cutoff(self):
        ledger = [{"emission_index": 0, "issue_time": 22.0, "emitted_at": 22.0}]
        observed_episode = {"peak_t": 35.0, "confirmed_event": True,
                            "onset_lo": 28.0, "onset_hi": 32.0, "onset_t": 30.0}
        votes = [{"t": t} for t in (22.0, 25.0, 30.0, 50.0)]
        with patch("dnmem.outcome_evidence_v4.visits", return_value=votes), \
             patch("dnmem.outcome_evidence_v4.x4_episodes", return_value=[observed_episode]):
            extracted = dose.outcome_evidence_v4([], ledger, stop=50.0)[0]
        self.assertEqual(extracted["stopping_cutoff"], 30.0)
        self.assertEqual(extracted["censor_at"], 28.0)
        truth = [{"id": "a", "block": 0, "onset": 10.0, "end": 20.0},
                 {"id": "b", "block": 0, "onset": 29.0, "end": 40.0}]
        exact = dose.truth_evidence(ledger, truth, {0: "a"}, {0: (30.0, "coverage")}, 50.0)[0]
        self.assertEqual(exact["kind"], "point")
        self.assertEqual(exact["onset_t"], 29.0)

    def test_true_onset_before_cutoff_is_event_even_when_end_is_partial(self):
        ledger = [{"emission_index": 0, "issue_time": 22.0}]
        truth = [{"id": "a", "block": 0, "onset": 10.0, "end": 20.0},
                 {"id": "b", "block": 0, "onset": 30.0, "end": 90.0}]
        evidence = dose.truth_evidence(ledger, truth, {0: "a"}, {0: (35.0, "coverage")}, 50.0)
        self.assertEqual(evidence[0]["kind"], "point")
        self.assertEqual(evidence[0]["onset_t"], 30.0)

    def test_reset_block_prevents_cross_seam_truth_target(self):
        ledger = [{"emission_index": 0, "issue_time": 22.0}]
        truth = [{"id": "a", "block": 0, "onset": 10.0, "end": 20.0},
                 {"id": "b", "block": 1, "onset": 30.0, "end": 40.0}]
        evidence = dose.truth_evidence(ledger, truth, {0: "a"}, {0: (28.0, "reset_block_end")}, 50.0)
        self.assertEqual(evidence[0]["kind"], "right_censored")
        self.assertEqual(evidence[0]["censor_at"], 28.0)

    def test_exact_density_and_survival_match_independent_scipy_formulas(self):
        mu, sigma, end, issue = math.log(20.0), 0.6, 10.0, 15.0
        for target in (16.0, 30.0, 150.0):
            evidence = {"issue_time": issue, "kind": "point", "onset_t": target}
            expected = lognorm.logpdf(target - end, s=sigma, scale=math.exp(mu)) \
                - lognorm.logsf(issue - end, s=sigma, scale=math.exp(mu))
            self.assertAlmostEqual(dose.point_loglik(evidence, end, mu, sigma), expected, places=12)
        for target in (issue, 20.0, 150.0):
            evidence = {"issue_time": issue, "kind": "right_censored", "censor_at": target}
            expected = lognorm.logsf(target - end, s=sigma, scale=math.exp(mu)) \
                - lognorm.logsf(issue - end, s=sigma, scale=math.exp(mu))
            self.assertAlmostEqual(dose.point_loglik(evidence, end, mu, sigma), expected, places=12)

    def test_truth_score_rejects_overtaken_onset(self):
        with self.assertRaisesRegex(ValueError, "after issue"):
            dose.point_loglik({"issue_time": 10.0, "kind": "point", "onset_t": 10.0}, 0.0, 2.0, 0.5)

    def test_composite_oracle_refit_zero_nesting_and_serialization(self):
        features, evidence = training_fixture()
        for f in features:
            f["duration"], f["previous_duration"] = 10.0, 10.0
            f["onset_t"] = f["end_t"] - 10.0
        bundle = dose.fit_oracle(features, evidence, 10000.0)
        self.assertEqual(bundle.models["M3"].coefficients["beta"], 0.0)
        self.assertEqual(bundle.models["P3"].coefficients["beta"], 0.0)
        scores = dose.truth_scores(bundle, features, evidence)
        self.assertTrue(all(row["gain_M3_M2"] == 0.0 for row in scores))
        restored = dose.DirectionalBundle.from_dict(bundle.to_dict())
        self.assertEqual(scores, dose.truth_scores(restored, features, evidence))

    def test_oracle_rejects_training_truth_after_freeze(self):
        features, evidence = training_fixture()
        evidence[0]["evidence_available_at"] = 10001.0
        with self.assertRaisesRegex(ValueError, "leakage"):
            dose.fit_oracle(features, evidence, 10000.0)

    def test_oracle_vector_fit_objective_matches_scalar_point_and_censor_scores(self):
        features, evidence = training_fixture()
        for i in range(0, len(evidence), 5):
            evidence[i].update(kind="right_censored", censor_at=features[i]["end_t"] + 12.0)
        bundle = dose.fit_oracle(features, evidence, 10000.0)
        scored = dose.truth_scores(bundle, features, evidence)
        for name in ("M0", "M2"):
            self.assertAlmostEqual(-sum(r[name] for r in scored), bundle.models[name].metadata["objective"], places=9)

    def test_oracle_failed_identifiable_optimizer_is_not_a_zero_effect_fit(self):
        features, evidence = training_fixture()
        failed = type("Failed", (), {"success": False, "message": "declared failure"})()
        with patch.object(dose, "minimize", return_value=failed):
            with self.assertRaisesRegex(ValueError, "optimization failed"):
                dose.fit_oracle(features, evidence, 10000.0)

    def test_measured_truth_scoring_uses_same_routes_and_r0_remaining_origin(self):
        features, evidence = training_fixture()
        intervals = [{**e, "kind": "interval", "onset_lo": e["onset_t"] - 0.1,
                      "onset_hi": e["onset_t"] + 0.1} for e in evidence]
        bundle = fit_directional(features, intervals, 10000.0)
        f = dict(features[0], landmark_available=False, end_t=features[0]["issue_time"] + 10.0)
        score = dose.truth_scores(bundle, [f], evidence[:1])[0]
        self.assertTrue(all(score[name + "_route"] == "R0" for name in dose.MODELS))
        expected = dose.point_loglik(evidence[0], f["issue_time"], bundle.r0.intercept, bundle.r0.sigma)
        self.assertEqual(score["M2"], expected)
        self.assertEqual(score["gain_M3_M2"], 0.0)


if __name__ == "__main__":
    unittest.main()
