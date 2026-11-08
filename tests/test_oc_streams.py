import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem import oc_streams


def inputs():
    bounds = [(2418672.5, 2425977.5), (2425977.5, 2433282.5), (2433282.5, 2436934.0)]
    return {
        "durations": [5.0, 8.0, 12.0],
        "gaps": [20.0, 40.0, 80.0],
        "phase_profiles": [],
        "brightness_model": {},
        "strata": [
            {"stratum": era, "start": start, "stop": stop, "days": [], "schedule": []}
            for era, (start, stop) in zip(oc_streams.ERAS, bounds)
        ],
    }


class OCStreamTests(unittest.TestCase):
    def test_slow_stream_has_a7_block_artificial_timeline_and_unique_truth(self):
        def fake_block(_inputs, _config, source, seed, case):
            start = float(source["start"])
            return ([{"JD": str(start + .25), "obsID": "one"}],
                    [{"id": 0, "onset": start + 1, "end": start + 5, "peak_t": start + 2,
                      "type": "short"}],
                    {"seed_seen": seed, "case_seen": case})

        config = {"family": "v2", "pair_id": "v2-phase"}
        with patch.object(oc_streams, "_slow_observed_block", side_effect=fake_block):
            rows, truth, meta = oc_streams.development_stream(
                inputs(), config, "slow_090", 3, "fresh-base"
            )
        self.assertEqual(len(meta["blocks"]), 7)
        self.assertEqual(meta["training_cutoff"], meta["blocks"][2]["synthetic_stop"])
        self.assertEqual(meta["eval_start"], meta["blocks"][3]["synthetic_start"])
        self.assertEqual(len({row["obsID"] for row in rows}), 7)
        self.assertEqual(len({event["id"] for event in truth}), 7)
        self.assertEqual([float(row["JD"]) for row in rows], sorted(float(row["JD"]) for row in rows))
        for block in meta["blocks"]:
            self.assertAlmostEqual(
                (block["synthetic_start"] - block["source_start"]) % 1, 0.0
            )
        self.assertEqual(meta["slow_state"]["phi"], .90)

    def test_slow_state_has_positive_marginal_copula_covariance(self):
        draws = oc_streams._slow_latent_draws(6000, .90, 1234)
        d = [a for a, _ in draws]
        q = [b for _, b in draws]
        d_mean, q_mean = sum(d) / len(d), sum(q) / len(q)
        covariance = sum((a - d_mean) * (b - q_mean) for a, b in draws) / len(draws)
        self.assertGreater(covariance, .05)
        self.assertLess(abs(sum(d) / len(d)), .08)
        self.assertLess(abs(sum(q) / len(q)), .08)

    def test_slow_timing_preserves_each_declared_following_gap(self):
        timing, _ = oc_streams._slow_timing(
            (5.0, 8.0, 12.0), (20.0, 40.0, 80.0), 0.0, 400.0, 123, .90
        )
        for current, following in zip(timing, timing[1:]):
            self.assertAlmostEqual(following[0] - current[1], current[3])

    def test_reference_replays_only_eval_blocks_and_preserves_context(self):
        def fake_block(_inputs, _config, source, seed, case, _offset_seed):
            start = float(source["start"])
            return ([{"JD": str(start + .25), "obsID": "native"}],
                    [{"id": 0, "onset": start + 1, "end": start + 5, "peak_t": start + 2,
                      "type": "short"}],
                    {"seed_seen": seed, "case_seen": case})

        config = {"family": "v2", "pair_id": "v2-phase"}
        cutoff = oc_streams._block_plan(inputs())[2].synthetic_stop
        context = [
            {"JD": cutoff - 10, "obsID": "immutable-context", "mag": 11.0},
            {"JD": cutoff + 1, "obsID": "too-late", "mag": 11.0},
            {"JD": cutoff - 500, "obsID": "too-old", "mag": 11.0},
        ]
        with patch.object(oc_streams, "_old_observed_block", side_effect=fake_block) as mocked:
            rows, truth, meta = oc_streams.reference_stream(
                inputs(), config, "null", 0, "development-base", "ref-A", context
            )
        self.assertEqual(meta["eval_start"], meta["blocks"][0]["synthetic_start"])
        self.assertEqual(meta["training_cutoff"], cutoff)
        self.assertEqual(meta["training_context_rows"], 1)
        self.assertEqual(rows[0], context[0])
        self.assertEqual(len(mocked.call_args_list), 4)
        self.assertEqual(len(truth), 4)
        self.assertTrue(all(event["id"].startswith("ref-ref-A-block-") for event in truth))
        self.assertEqual(len({row["obsID"] for row in rows}), len(rows))
        first_seed = mocked.call_args_list[0].args[3]
        with patch.object(oc_streams, "_old_observed_block", side_effect=fake_block) as repeat:
            _, _, _ = oc_streams.reference_stream(
                inputs(), config, "null", 0, "development-base", "ref-A", context
            )
        with patch.object(oc_streams, "_old_observed_block", side_effect=fake_block) as changed:
            _, _, _ = oc_streams.reference_stream(
                inputs(), config, "null", 0, "other-base", "ref-A", context
            )
        self.assertEqual(first_seed, repeat.call_args_list[0].args[3])
        self.assertNotEqual(first_seed, changed.call_args_list[0].args[3])
        with patch.object(oc_streams, "_old_observed_block", side_effect=fake_block):
            with self.assertRaises(ValueError):
                oc_streams.reference_stream(
                    inputs(), config, "null", 0, "development-base", "ref-A", context,
                    {**meta, "stop": meta["stop"] + 1}
                )

    def test_slow_state_rejects_v4_and_unknown_reference_case(self):
        with self.assertRaises(ValueError):
            oc_streams.development_stream(inputs(), {"family": "v4"}, "slow_098", 0, "x")
        with self.assertRaises(ValueError):
            oc_streams.reference_stream(inputs(), {"family": "v2", "pair_id": "v2-phase"},
                                        "slow_090", 0, "x", "r", [])


if __name__ == "__main__":
    unittest.main()
