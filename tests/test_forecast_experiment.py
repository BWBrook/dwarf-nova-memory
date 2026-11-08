import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"src"), str(ROOT/"scripts")]
from dnmem import forecast_experiment as experiment
import a10b_pipeline as pipeline


def inputs():
    bounds = [(2418672.5, 2425977.5), (2425977.5, 2433282.5), (2433282.5, 2436934.)]
    return {"strata": [{"stratum": e, "start": a, "stop": b, "days": [], "schedule": []}
                       for e, (a, b) in zip(experiment.ERAS, bounds)]}


class ForecastExperimentTests(unittest.TestCase):
    def test_partial_source_day_is_not_lost(self):
        s = inputs()["strata"][0]
        t = s["start"]+.1
        s["days"] = [{"day": int(t), "slots": [{"t": t}, {"t": t-.2}]}]
        s["schedule"] = [{"t": t}, {"t": t-.2}]
        c = experiment.crop_stratum(s, s["start"], s["start"]+365.25)
        self.assertEqual(c["days"][0]["slots"], [{"t": t}])
        self.assertEqual(c["schedule"], [{"t": t}])

    def test_artificial_timeline_is_chronological_and_integer_shifted(self):
        def block(inp, config, source, seed, case, offset_seed):
            a, b = source["start"], source["stop"]
            rows = [{"JD": str(a+.1), "obsID": "same"}, {"JD": str(b-.1), "obsID": "same"}]
            truth = [{"id": 0, "onset": a+1, "end": a+11, "peak_t": a+3, "type": "short"}]
            return rows, truth, {}
        with patch.object(experiment, "observed_block", side_effect=block) as mock:
            rows, truth, meta = experiment.chronological_stream(inputs(), {"pair_id": "v2-phase"}, "offset", 0, "fixture")
        self.assertEqual(len(meta["blocks"]), 7)
        self.assertEqual(meta["training_cutoff"], meta["blocks"][2]["synthetic_stop"])
        self.assertEqual(len({c.args[-1] for c in mock.call_args_list}), 1)
        self.assertEqual(len({e["id"] for e in truth}), 7)
        self.assertEqual([float(r["JD"]) for r in rows], sorted(float(r["JD"]) for r in rows))
        for a, b in zip(meta["blocks"], meta["blocks"][1:]):
            self.assertGreaterEqual(b["synthetic_start"]-a["synthetic_stop"], 30)
        for b in meta["blocks"]:
            self.assertAlmostEqual((b["synthetic_start"]-b["source_start"]) % 1, 0)
        self.assertLess(meta["stop"], 100000)

    def test_oracle_does_not_supply_an_unfinished_event(self):
        f = {"emission_index": 0, "emitted_at": 10., "issue_time": 10., "bright_first_at": 5.,
             "onset_t": 1., "end_t": 9., "duration": 8., "landmark_available": True}
        truth = [{"id": 0, "block": 0, "onset": 1., "end": 11., "peak_t": 4.}]
        with patch.object(experiment, "x4_episodes", return_value=[]):
            views, counts = experiment.predictor_views([], [f], truth)
        self.assertFalse(views["oracle"][0]["landmark_available"])
        self.assertIsNone(views["oracle"][0]["duration"])
        self.assertEqual(len(views["prefix"]), len(views["oracle"]))
        self.assertEqual(counts["oracle_unknown_or_uncompleted"], 1)

    def test_retrospective_future_merged_peak_does_not_silently_use_prefix(self):
        f = {"emission_index": 0, "emitted_at": 10., "issue_time": 10., "bright_first_at": 5.,
             "onset_t": 1., "end_t": 9., "duration": 8., "landmark_available": True}
        episode = {"peak_t": 15., "onset_t": 1., "onset_lo": .5, "onset_hi": 1.5,
                   "end_t": 17., "end_lo": 16.5, "end_hi": 17.5}
        with patch.object(experiment, "x4_episodes", return_value=[episode]):
            views, counts = experiment.predictor_views([], [f], [])
        self.assertEqual(views["retrospective"][0]["end_t"], 17.)
        self.assertFalse(views["retrospective"][0]["landmark_available"])
        self.assertEqual(counts["retrospective_matched"], 1)

    def test_fixed_full_trial_grid_has_every_required_case(self):
        tasks = pipeline.tasks_from_config()
        self.assertEqual(len(tasks), 56)
        self.assertEqual(len(tasks), len(set(tasks)))
        self.assertEqual({c for f, c, _ in tasks if f == "v2-phase"}, set(experiment.CASES))
        self.assertEqual(sum(f == "v4-phase" for f, _, _ in tasks), 8)

    def test_failed_conditions_cannot_disappear_from_summary(self):
        rows = pipeline.summarize_trials([])
        self.assertEqual(len(rows), 132)
        primary = next(r for r in rows if r["family"] == "v2-phase" and r["case"] == "null"
                       and r["variant"] == "prefix_point" and r["comparison"] == "gain_M3_M2")
        self.assertEqual(primary["expected_replicates"], 8)
        self.assertEqual(primary["failed_or_missing_replicates"], 8)
        self.assertIsNone(primary["mean_gain_nats"])
        paired = pipeline.paired_stress_contrasts([])
        self.assertEqual(len(paired), 36)
        self.assertTrue(all(r["paired_trials"] == 0 and r["stress_minus_null"] is None for r in paired))


if __name__ == "__main__":
    unittest.main()
