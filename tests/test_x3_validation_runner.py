from __future__ import annotations

from pathlib import Path
import sys
import json
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_x3_validation as runner


class X3ValidationRunnerTests(unittest.TestCase):
    def test_fixed_manifest_has_expected_histories_and_metric_rows(self):
        tasks = runner.build_tasks()
        self.assertEqual(len(tasks), 7600)
        self.assertEqual(runner.manifest_counts(tasks),
                         {"histories": 7600, "metric_rows": 79200})

    def test_seed_stream_is_stable_and_label_sensitive(self):
        base = runner.FREEZE_BASE + "0" * 40
        self.assertEqual(runner.seed_for(base, "primary", "era1", "random", 0),
                         runner.seed_for(base, "primary", "era1", "random", 0))
        self.assertNotEqual(runner.seed_for(base, "primary", "era1", "random", 0),
                            runner.seed_for(base, "primary", "era1", "state", 0))

    def test_threshold_subsets_are_prespecified(self):
        primary = [task for task in runner.build_tasks() if task["case"] == "primary"]
        self.assertEqual(len(primary), 2400)
        self.assertTrue(all(task["thresholds"] == runner.THRESHOLDS
                            for task in primary if task["replicate"] < 200))
        self.assertTrue(all(task["thresholds"] == (10.0,)
                            for task in primary if task["replicate"] >= 200))
        alternative = [task for task in runner.build_tasks() if task["case"] == "alternative"]
        self.assertTrue(all(task["thresholds"] == runner.THRESHOLDS for task in alternative))
        structured = [task for task in runner.build_tasks() if task["case"] == "structured"]
        self.assertEqual(len(structured), 2400)
        self.assertTrue(all(task["thresholds"] == (10.0,) for task in structured))

    def test_cache_rejects_pre1960_boundary_rows(self):
        digest = "a" * 64
        cache = {
            "durations": [1.0, 2.0], "gaps": [3.0, 4.0],
            "model": {}, "brightness_model": {}, "source_sha256": {"x": digest},
            "strata": [{"stratum": "era1", "start": 1.0, "stop": 2.0,
                         "schedule": [{"JD": 2436934.5}], "days": []}],
        }
        with self.assertRaisesRegex(ValueError, "pre-1960"):
            runner.validate_cache(cache)

    def test_cache_accepts_strictly_pre1960_times(self):
        digest = "a" * 64
        cache = {
            "durations": [1.0, 2.0], "gaps": [3.0, 4.0],
            "model": {}, "brightness_model": {}, "source_sha256": {"x": digest},
            "strata": [{"stratum": "era1", "start": 1.0, "stop": 2.0,
                         "schedule": [{"JD": 2436934.4}], "days": []}],
        }
        runner.validate_cache(cache)

    def test_qualification_gate_binds_pass_seed_and_configuration(self):
        configuration = {"shape_config": {"quiet_magnitude": 11.8},
                         "noise_multiplier": 1.1}
        freeze = "b" * 40
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            path.write_text(json.dumps({"all_passed": True,
                                        "seed_base": "a04e-qualification|" + freeze,
                                        "selected": {"configuration": configuration}}))
            with self.assertRaisesRegex(ValueError, "prepared input"):
                runner.validate_qualification(path, configuration, freeze, "c" * 64)

    def test_heavy_score_arrays_are_sidecar_only(self):
        score = {"rule": "C1_7", "fallback": {"fit": 1},
                 "pair_records": [{"pair": 1}],
                 "operational_confirmation_first_records": [{"truth": 1}],
                 "operational_confirmation_emissions": [{"emission": 1}]}
        flat, sidecar = runner._flatten_score(score, ledger=False)
        self.assertEqual(flat["fallback"], '{"fit":1}')
        self.assertNotIn("pair_records", flat)
        self.assertIsNone(sidecar)
        flat, sidecar = runner._flatten_score(score, ledger=True)
        self.assertNotIn("pair_records", flat)
        self.assertEqual(sidecar["pair_records"], [{"pair": 1}])

    def test_persistent_offsets_add_to_calibrated_offsets(self):
        model = {"o0001": {"offset": 0.4, "sigma": 0.2}}
        observed = runner._fixed_offsets(model, 17)["o0001"]
        generated = runner.random.Random(runner.seed_for(17, "fixed-offset", "o0001")).gauss(0.0, 0.2)
        self.assertAlmostEqual(observed, 0.4 + generated)

    def test_candidate_commit_is_resolvable(self):
        self.assertEqual(len(runner._git_commit("c0353c0")), 40)
        commit, digest = runner._candidate_source_hash()
        self.assertEqual(len(commit), 40)
        self.assertEqual(len(digest), 64)


if __name__ == "__main__":
    unittest.main()
