import copy
import math
from pathlib import Path
import sys
import unittest

import numpy as np
from scipy.integrate import quad
from scipy.stats import lognorm, norm, truncnorm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "scripts"))

from dnmem.directional_forecast import DirectionalBundle
from dnmem.extract import visits
from dnmem.extract_x4 import x4_episodes
from dnmem.observation_scores_r1 import (BLOCK_DAYS, ORIGIN, CalendarForecast,
    calendar_forecast, cluster_summary, kernel_score, normal_logmass, point_route,
    reconstruct_onsets, score_alternatives, set_route, stopping_cutoffs)
from check_a10d_scores import conditional_score
from test_extract import obs, outburst
from test_extract_x3 import light_curve


def synthetic_spec():
    base = {"name": "M2", "intercept": math.log(24), "coefficients": {"previous_gap": .2, "earlier_level": .1},
            "sigma": .35, "centers": {"previous_gap": math.log(20), "earlier_level": math.log(20)},
            "scales": {"previous_gap": .4, "earlier_level": .3}, "n_fit": 10,
            "terms": ["previous_gap", "earlier_level"], "metadata": {}}
    models = {"M2": base}
    for name in ("M3", "P3"):
        model = copy.deepcopy(base)
        model.update(name=name, coefficients={**base["coefficients"], "beta": .2},
                     terms=base["terms"] + ["beta"],
                     centers={**base["centers"], "mark": math.log(10)},
                     scales={**base["scales"], "mark": .3},
                     metadata={"mark_kind": "current" if name == "M3" else "previous", "mark_mode": "log_duration"})
        models[name] = model
    models["M0"] = dict(base, name="M0", coefficients={}, terms=[])
    return {"models": models, "r0": models["M0"], "endpoint_mode": "point", "nodes": 5,
            "mark_mode": "log_duration", "local_level": True, "directional": True,
            "joint_marks": False, "counts": {}, "metadata": {}}


def synthetic_feature(index=0):
    end = ORIGIN + 8 + index * BLOCK_DAYS
    return {"emission_index": index, "emitted_at": end + 2, "issue_time": end + 2,
            "end_t": end, "onset_t": end - 12, "duration": 12,
            "previous_gap": 22, "previous_gap_covered": True, "previous_duration": 10,
            "earlier_gaps": [math.log(19), math.log(23)]}


class ReconstructionTests(unittest.TestCase):
    def test_exact_reconstruction_including_unconfirmed_neighbor_and_aggregation(self):
        rows = light_curve() + [obs(135.6, 12, "z"), obs(140.6, 8.5, "z"), obs(145.6, 12, "z")]
        for row in light_curve():
            row = dict(row, JD=str(float(row["JD"]) + 80), obsID=row["obsID"] + "-shift")
            rows.append(row)
        rows += [obs(98.61, 11.4, "a"), obs(98.65, 11.2, "a")]
        episodes = x4_episodes(rows)
        self.assertTrue(any(not e["confirmed_event"] for e in episodes))
        result = reconstruct_onsets(rows, episodes, visits(rows))
        self.assertEqual(len(result), len(episodes))
        self.assertEqual(sum(r["confirmed_index"] is not None for r in result), sum(e["confirmed_event"] for e in episodes))
        self.assertTrue(any(r["components"] for r in result))

    def test_irregular_votes_and_limits_reconstruct_frozen_fit(self):
        rows = outburst()
        result = reconstruct_onsets(rows, x4_episodes(rows), visits(rows))
        self.assertEqual(len(result), 1)
        self.assertEqual((result[0]["clip_lo"], result[0]["clip_hi"]), (104.6, 105.7))
        self.assertIsNotNone(result[0]["components"])

    def test_corrupted_saved_boundary_is_rejected(self):
        rows = light_curve()
        episodes = x4_episodes(rows)
        episodes[0]["onset_lo"] += .1
        with self.assertRaisesRegex(ValueError, "reconstruction differs"):
            reconstruct_onsets(rows, episodes, visits(rows))


class RoutingTests(unittest.TestCase):
    def test_exact_cutoff_and_issue_boundaries(self):
        for bounds in ((18, 19), (18, 20)):
            self.assertEqual(set_route(*bounds, 10, 20)["kind"], "interval")
        self.assertEqual(set_route(18, 22, 10, 20)["censor_at"], 18)
        for bounds in ((20, 22), (21, 22)):
            self.assertEqual(set_route(*bounds, 10, 20)["censor_at"], 20)
        self.assertEqual(set_route(10, 22, 10, 20)["status"], "ambiguous_survival")
        self.assertEqual(set_route(9, 10, 10, 20)["status"], "overtaken")
        self.assertEqual(set_route(None, 22, 10, 20)["status"], "missing_clip")
        self.assertEqual(set_route(22, 22, 10, 20)["status"], "reversed_clip")
        self.assertEqual(point_route(20, 10, 20)["kind"], "point")
        self.assertEqual(point_route(10, 10, 20)["status"], "overtaken")
        self.assertEqual(point_route(21, 10, 20)["censor_at"], 20)

    def test_coverage_threshold_and_supersession_ties(self):
        ledger = [{"emission_index": 0, "issue_time": 10}, {"emission_index": 1, "issue_time": 20}]
        exact = stopping_cutoffs(ledger, [10, 17, 20, 27], stop=27)
        self.assertEqual(exact[0], {"cutoff": 20, "reason": "superseded"})
        gap = stopping_cutoffs(ledger, [10, 17.00001, 20, 27], stop=27)
        self.assertEqual(gap[0], {"cutoff": 10, "reason": "coverage"})


class NumericalTests(unittest.TestCase):
    def test_calendar_interval_matches_frozen_independent_scalar_and_density_derivative(self):
        spec, feature = synthetic_spec(), synthetic_feature()
        for selected in ("M0", "M2", "M3", "R0"):
            forecast = calendar_forecast(spec, feature, selected)
            outcome = {"emission_index": 0, "issue_time": feature["issue_time"], "kind": "interval",
                       "onset_lo": feature["issue_time"] + 14, "onset_hi": feature["issue_time"] + 17}
            self.assertAlmostEqual(forecast.score(outcome), conditional_score(feature, outcome, spec, selected), places=12)
            point, h = feature["issue_time"] + 15, 1e-3
            tiny = dict(outcome, onset_lo=point - h, onset_hi=point + h)
            self.assertAlmostEqual(forecast.score(tiny) - math.log(2 * h), forecast.logpdf(point), places=6)

    def test_normal_mass_handles_extreme_tails(self):
        self.assertAlmostEqual(normal_logmass(20, 21), float(norm.logsf(20) + math.log1p(-math.exp(norm.logsf(21) - norm.logsf(20)))), places=12)
        self.assertAlmostEqual(normal_logmass(-21, -20), normal_logmass(20, 21), places=12)

    def test_kernel_two_rules_and_independent_density_integral(self):
        forecast = CalendarForecast(0, 2, math.log(20), .35)
        comps, a, b = [(.3, 18, .2), (.7, 22, 1.3)], 17, 24
        value, diagnostics = kernel_score(forecast, comps, a, b)
        mass = sum(w * (norm.cdf((b - m) / s) - norm.cdf((a - m) / s)) for w, m, s in comps)
        expected = quad(lambda time: sum(w * norm.pdf(time, m, s) for w, m, s in comps)
                        * lognorm.pdf(time, .35, scale=20) / lognorm.sf(2, .35, scale=20), a, b,
                        epsabs=1e-13, epsrel=1e-12, points=[18, 22])[0] / mass
        self.assertAlmostEqual(value, math.log(expected), places=11)
        self.assertLess(diagnostics["adaptive_vs_gl128_log_error"], 1e-10)

    def test_kernel_tail_and_narrow_support_without_epsilon(self):
        forecast = CalendarForecast(0, 1, math.log(20), .3)
        value, _ = kernel_score(forecast, [(1, 0, 1)], 20, 21)
        expected = quad(lambda time: truncnorm.pdf(time, 20, 21)
                        * lognorm.pdf(time, .3, scale=20) / lognorm.sf(1, .3, scale=20), 20, 21)[0]
        self.assertAlmostEqual(value, math.log(expected), places=10)
        narrow, _ = kernel_score(forecast, [(1, 20, .001)], 19, 21)
        self.assertAlmostEqual(narrow, forecast.logpdf(20), places=6)
        with self.assertRaises(ValueError):
            kernel_score(forecast, [(1, 20, 1)], 0, 21)

    def test_exact_zero_weight_from_frozen_grid_is_not_an_unavailable_kernel(self):
        forecast = CalendarForecast(0, 1, math.log(20), .3)
        value, diagnostics = kernel_score(forecast, [(0, 100, .1), (1, 20, 1)], 18, 22)
        expected, _ = kernel_score(forecast, [(1, 20, 1)], 18, 22)
        self.assertEqual(value, expected)
        self.assertEqual(diagnostics["zero_weight_components"], 1)

    def test_unequal_cluster_counts_use_original_issuance_weights(self):
        rows = [{"issue_time": ORIGIN, "gain": 1}, {"issue_time": ORIGIN + 1, "gain": 2},
                {"issue_time": ORIGIN + BLOCK_DAYS, "gain": 4}]
        actual = cluster_summary(rows)
        mean = 7 / 3
        se = math.sqrt(2 * ((3 - 2 * mean) ** 2 + (4 - mean) ** 2)) / 3
        self.assertAlmostEqual(actual["estimate"], mean)
        self.assertAlmostEqual(actual["se"], se)
        self.assertEqual(actual["df"], 1)


class PopulationTests(unittest.TestCase):
    def test_identity_zero_retained_when_observation_unavailable_and_censor_promoted(self):
        spec = synthetic_spec()
        ledger = [synthetic_feature(i) for i in range(2)]
        ledger[0]["previous_gap_covered"] = False
        evidence = [{"emission_index": f["emission_index"], "issue_time": f["issue_time"],
                     "kind": "right_censored", "censor_at": f["issue_time"] + 20} for f in ledger]
        saved = DirectionalBundle.from_dict(spec).batchscore(ledger, evidence)
        episodes, recon, cutoffs = [], [], {}
        for i, f in enumerate(ledger):
            episodes.append({"confirmed_event": True, "peak_t": f["issue_time"] + 16,
                             "onset_lo": f["issue_time"] + 10, "onset_hi": f["issue_time"] + 12,
                             "onset_t": f["issue_time"] + 11})
            recon.append({"all_index": i, "confirmed_index": i, "clip_lo": None if i == 0 else f["issue_time"] + 10,
                          "clip_hi": f["issue_time"] + 12, "components": None, "clip_conflict": False})
            cutoffs[i] = {"cutoff": f["issue_time"] + 20, "reason": "coverage"}
        results, summary = score_alternatives(spec, ledger, evidence, saved, episodes, recon, cutoffs)
        identity = results["decisive_report"][0]
        self.assertEqual((identity["status"], identity["gain"], identity["scores"]), ("identical_forecast", 0, None))
        self.assertEqual(identity["observation_status"], "missing_clip")
        self.assertEqual(results["decisive_report"][1]["kind"], "interval")
        self.assertEqual(results["x4_kernel"][1]["status"], "missing_kernel")
        self.assertEqual(summary["common_usable"], 1)
        self.assertEqual(summary["variants"]["decisive_report"]["matched_primary"]["n"], 2)
        self.assertEqual(summary["variants"]["x4_kernel"]["matched_primary"]["n"], 1)


if __name__ == "__main__":
    unittest.main()
