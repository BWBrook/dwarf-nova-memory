import copy
import math
from pathlib import Path
import sys
import unittest

from scipy.stats import lognorm, t

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]

from dnmem.r2_models import ConditionalClock
from dnmem.r2b_scoring import (aggregate_contrast, autocorrelations, calendar_interval,
                               outcome_evidence, paired_clock_gain, residual_diagnostics,
                               score_contrast)
from test_extract import obs
from test_prefix_features import outbursts


def feature(index=0, issue=10., last=5., anchor=0.):
    return {"emission_index": index, "issue_time": issue, "original_last_bright_at": last,
            "clock_anchor": anchor, "clock": "point"}


def episode(peak=25., lo=20., hi=22., **fields):
    return {"peak_t": peak, "onset_report_lo": lo, "onset_report_hi": hi,
            "onset_t": (lo + hi) / 2 if lo is not None and hi is not None else None,
            "confirmed_event": True, "onset_report_available": lo is not None and hi is not None,
            "onset_report_eligible": True, "onset_flags": [], "onset_status": "available", **fields}


def evidence(ledger, candidates, stop=40., times=None, **kwargs):
    return outcome_evidence([], ledger, stop=stop, candidates=candidates,
                            observation_times=list(range(int(stop))) if times is None else times, **kwargs)


class FixedRule:
    def __init__(self, shift=.2, sigma=.6):
        self.shift, self.sigma = shift, sigma

    def predict(self, row, with_mark=False):
        return (ConditionalClock(row["clock_anchor"], row["issue_time"],
                                 math.log(20.) + (self.shift if with_mark else 0.), self.sigma),
                "fixed+mark" if with_mark else "fixed")


class AssociationTests(unittest.TestCase):
    def test_first_unconfirmed_or_unsupported_candidate_is_never_skipped(self):
        for first, reason in ((episode(peak=15., lo=12., hi=14., confirmed_event=False),
                               "unconfirmed_adjacent_candidate"),
                              (episode(peak=15., lo=None, hi=14., onset_report_available=False,
                                       onset_status="no_quiescence_report"),
                               "unsupported_adjacent_candidate:no_quiescence_report")):
            with self.subTest(reason=reason):
                row = evidence([feature()], [first, episode()])[0]
                self.assertEqual(row["kind"], "excluded")
                self.assertEqual(row["reason"], reason)
                self.assertEqual(row["candidate_all_index"], 0)

    def test_delayed_issue_does_not_skip_an_overtaken_candidate(self):
        ledger = [feature(issue=23., last=5.)]
        row = evidence(ledger, [episode(), episode(peak=35., lo=30., hi=32.)])[0]
        self.assertEqual((row["kind"], row["reason"], row["candidate_all_index"]),
                         ("excluded", "overtaken", 0))

    def test_issue_straddle_is_unsupported_instead_of_conditioning_it_away(self):
        row = evidence([feature(issue=21.)], [episode()])[0]
        self.assertEqual((row["kind"], row["reason"]), ("excluded", "ambiguous_survival"))

    def test_flagged_windows_are_separate_and_unsupported_do_not_become_flags(self):
        candidate = episode(onset_report_eligible=False, onset_flags=["contested_decisive_epoch"])
        primary = evidence([feature()], [candidate])[0]
        sensitivity = evidence([feature()], [candidate], include_flagged=True)[0]
        self.assertEqual(primary["reason"], "flagged_adjacent_window")
        self.assertEqual(sensitivity["kind"], "interval")
        self.assertFalse(sensitivity["window_eligible"])
        unavailable = evidence([feature()], [episode(lo=None, onset_report_available=False)], include_flagged=True)[0]
        self.assertEqual(unavailable["kind"], "excluded")

    def test_cutoff_straddle_backoff_and_fixed_cutoff_are_both_retained(self):
        ledger = [feature(0, 10.), feature(1, 15., last=5.)]
        a, b = evidence(ledger, [episode(peak=20., lo=12., hi=18.)])
        self.assertEqual((a["kind"], a["censor_at"], a["fixed_cutoff"]), ("right_censored", 12., 15.))
        self.assertEqual(a["censor_backoff_days"], 3.)
        self.assertEqual(a["fixed_cutoff_kind"], "superseded")
        self.assertEqual((b["kind"], b["reason"]), ("excluded", "ambiguous_survival"))
        self.assertFalse(a["cutoff_independence_established"])

    def test_only_the_later_issue_is_credited_and_cutoff_tie_is_resolved_once(self):
        ledger = [feature(0, 10.), feature(1, 15., last=5.)]
        a, b = evidence(ledger, [episode()])
        self.assertEqual((a["kind"], a["censor_at"], b["kind"]), ("right_censored", 15., "interval"))
        a, b = evidence(ledger, [episode(peak=18., lo=12., hi=15.)])
        self.assertEqual(a["kind"], "interval")
        self.assertEqual((b["kind"], b["reason"]), ("excluded", "overtaken"))

    def test_monitoring_hole_stops_at_its_left_edge_even_when_it_contains_issue(self):
        times = [0., 3., 8., 25., 26., 30.]
        row = evidence([feature(issue=10.)], [], stop=32., times=times)[0]
        self.assertEqual((row["kind"], row["fixed_cutoff"], row["censor_at"]),
                         ("right_censored", 10., 10.))
        self.assertEqual(row["fixed_cutoff_kind"], "coverage")
        self.assertFalse(row["latent_survival_verified"])
        row = evidence([feature()], [], stop=20., times=list(range(20)))[0]
        self.assertEqual((row["reason"], row["censor_at"]), ("record_end:no_candidate", 20.))

    def test_future_record_poisoning_does_not_change_training_evidence(self):
        rows = outbursts(events=((10., 20.), (60., 70.)), nights=range(0, 90))
        ledger = [feature(issue=25., last=17.)]
        original = outcome_evidence(rows, ledger, stop=45.)
        changed = [row if float(row["JD"]) < 45 else {**row, "mag": "8.0"} for row in rows]
        changed += [obs(50, 7, "new-a"), obs(51, 7, "new-b")]
        self.assertEqual(original, outcome_evidence(changed, ledger, stop=45.))
        with self.assertRaisesRegex(ValueError, "as-of"):
            evidence(ledger, [episode(peak=50., lo=46., hi=48.)], stop=45.)
        with self.assertRaisesRegex(ValueError, "has not closed"):
            evidence([feature()], [episode(peak=39.9, lo=38., hi=39.9,
                                           onset_upper_first_at=39.9)], stop=40.)

    def test_unclosed_final_visit_is_not_an_available_training_candidate(self):
        rows = [obs(day + .6, 12., who) for day in range(40) for who in "ab"]
        rows += [obs(39.95, 8.5, "a"), obs(39.95, 8.5, "b")]
        row = outcome_evidence(rows, [feature(issue=10.)], stop=40.)[0]
        self.assertEqual(row["candidate_all_index"], None)
        self.assertEqual(row["reason"], "record_end:no_candidate")


class ScoreTests(unittest.TestCase):
    def test_interval_scores_match_independent_conditional_lognormal_mass(self):
        features = [feature()]
        result = score_contrast(features, evidence(features, [episode()]), FixedRule())[0]
        scores = []
        for median in (20., 20. * math.exp(.2)):
            distribution = lognorm(s=.6, scale=median)
            scores.append(math.log(distribution.cdf(22) - distribution.cdf(20)) - distribution.logsf(10))
        self.assertAlmostEqual(result["baseline_score"], scores[0], places=12)
        self.assertAlmostEqual(result["marked_score"], scores[1], places=12)
        self.assertAlmostEqual(result["gain"], scores[1] - scores[0], places=12)
        expected_point = lognorm.logpdf(21, s=.6, scale=20 * math.exp(.2)) - lognorm.logsf(10, s=.6, scale=20 * math.exp(.2))
        expected_point -= lognorm.logpdf(21, s=.6, scale=20) - lognorm.logsf(10, s=.6, scale=20)
        self.assertAlmostEqual(result["point_gain"], expected_point, places=12)

    def test_working_backoff_survival_is_distinct_from_fixed_cutoff_bounds(self):
        features = [feature(0, 10.), feature(1, 15., last=5.)]
        ev = evidence(features, [episode(peak=20., lo=12., hi=18.)])
        result = score_contrast(features, ev, FixedRule())[0]
        baseline, marked = [FixedRule().predict(features[0], with_mark=mark)[0] for mark in (False, True)]
        self.assertAlmostEqual(result["gain"], marked.log_survival(12) - baseline.log_survival(12))
        targets = [marked.log_density(time) - baseline.log_density(time) for time in (12.00001, 13., 15.)]
        targets.append(marked.log_survival(15) - baseline.log_survival(15))
        for value in targets:
            self.assertLessEqual(result["bounds_lower"] - 1e-12, value)
            self.assertGreaterEqual(result["bounds_upper"] + 1e-12, value)
        self.assertNotEqual(result["gain"], marked.log_survival(15) - baseline.log_survival(15))

    def test_exact_identities_with_unsupported_evidence_are_not_observed_zeros(self):
        features = [feature()]
        ev = evidence(features, [episode(confirmed_event=False)])
        result = score_contrast(features, ev, FixedRule(shift=0.))[0]
        self.assertIsNone(result["gain"])
        self.assertIsNone(result["baseline_score"])
        self.assertEqual(result["known_contrast"], 0.)
        self.assertEqual(result["identity_gain"], 0.)
        self.assertEqual(aggregate_contrast([result])["six_year"]["n"], 0)
        self.assertEqual(aggregate_contrast([result], "known_contrast")["six_year"]["n"], 1)
        result = score_contrast(features, evidence(features, [episode()]), FixedRule(shift=0.))[0]
        self.assertEqual((result["gain"], result["bounds_lower"], result["bounds_upper"]), (0., 0., 0.))

    def test_df_has_no_point_density_sensitivity_and_cross_clock_pairing_is_exact(self):
        point = [feature()]
        df = [{**feature(anchor=2.), "clock": "decisive"}]
        ev = evidence(point, [episode()])
        p, d = score_contrast(point, ev, FixedRule()), score_contrast(df, ev, FixedRule())
        self.assertIsNone(d[0]["point_gain"])
        h3 = paired_clock_gain(d, p)[0]
        self.assertAlmostEqual(h3["gain"], d[0]["gain"] - p[0]["gain"])
        altered = copy.deepcopy(p)
        altered[0]["outcome_signature"]["fixed_cutoff"] -= 1
        with self.assertRaisesRegex(ValueError, "outcome mismatch"):
            paired_clock_gain(d, altered)
        with self.assertRaisesRegex(ValueError, "populations differ"):
            paired_clock_gain(d, [])

    def test_score_pair_cannot_have_forged_issue_or_different_anchor(self):
        features = [feature()]
        ev = evidence(features, [episode()])
        ev[0]["issue_time"] = 11.
        with self.assertRaisesRegex(ValueError, "issue mismatch"):
            score_contrast(features, ev, FixedRule())
        class DifferentAnchor(FixedRule):
            def predict(self, row, with_mark=False):
                clock, route = super().predict(row, with_mark)
                return ConditionalClock(clock.anchor + int(with_mark), clock.issue, clock.mu, clock.sigma), route
        with self.assertRaisesRegex(ValueError, "different issue or anchor"):
            score_contrast(features, evidence(features, [episode()]), DifferentAnchor())


class DiagnosticTests(unittest.TestCase):
    def test_weighted_cr1_matches_hand_arithmetic_and_actual_nonempty_df(self):
        rows = [{"issue_time": time, "gain": gain, "w": weight} for time, gain, weight in
                ((1., 1., 2.), (2., 2., 1.), (400., 3., 1.), (800., 0., 4.))]
        interval = calendar_interval(rows, origin=0., years=1., weight_field="w")
        mean = 7 / 8
        variance = 3 / 2 * (1.375**2 + 2.125**2 + (-3.5)**2) / 8**2
        self.assertEqual((interval["blocks"], interval["df"], interval["n"]), (3, 2, 4))
        self.assertEqual(interval["estimate"], mean)
        self.assertAlmostEqual(interval["se"]**2, variance)
        self.assertAlmostEqual(interval["lower"], mean - t.ppf(.95, 2) * math.sqrt(variance))
        self.assertIsNone(calendar_interval(rows[:1], origin=0., years=12)["lower"])
        bad = [{"issue_time": 1., "gain": 2., "w": -1.}]
        with self.assertRaisesRegex(ValueError, "invalid weight"):
            calendar_interval(bad, origin=0., weight_field="w")

    def test_missing_forecasts_and_calendar_blocks_are_not_joined_for_acf(self):
        acf = autocorrelations([1., None, 3., 4.], 2)
        self.assertEqual([row["pairs"] for row in acf["lags"]], [1, 1])
        self.assertAlmostEqual(acf["lags"][0]["acf"], 2 / 21)
        self.assertTrue(autocorrelations([0., 0.])["constant_or_insufficient"])
        rows = [{"issue_time": 1., "gain": 1.}, {"issue_time": 800., "gain": 3.}]
        result = calendar_interval(rows, origin=0., years=1.)
        self.assertEqual(result["block_mean_acf"]["lags"][0]["pairs"], 0)
        self.assertIsNone(result["block_mean_acf"]["lags"][0]["acf"])

    def test_midpoint_residual_proxy_excludes_censors_and_preserves_missing_slots(self):
        features, ev = [], []
        for index, (issue, z) in enumerate(((1., -1.), (2., 0.), (400., 1.), (401., 2.))):
            row = feature(index, issue=issue, anchor=issue)
            middle = issue + 20 * math.exp(.6 * z)
            features.append(row)
            ev.append({"emission_index": index, "issue_time": issue, "kind": "interval",
                       "onset_lo": middle - .01, "onset_hi": middle + .01})
        features.append(feature(4, issue=402., anchor=402.))
        ev.append({"emission_index": 4, "issue_time": 402., "kind": "right_censored"})
        result = residual_diagnostics(features, ev, FixedRule(), origin=0., years=1.)
        self.assertEqual(result["n"], 4)
        self.assertEqual(result["excluded"], {"right_censored": 1})
        self.assertAlmostEqual(result["block_icc"], 7 / 9, places=12)
        self.assertEqual(result["forecast_acf"]["n_slots"], 5)
        self.assertIn("not latent", result["scope"])


if __name__ == "__main__":
    unittest.main()
