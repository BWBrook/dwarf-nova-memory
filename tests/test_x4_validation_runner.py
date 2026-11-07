from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_x4_validation as runner


class X4ValidationRunnerTests(unittest.TestCase):
    def test_exact_manifest_and_ledger_counts(self):
        tasks = runner.build_tasks()
        self.assertEqual(len(tasks), 16600)
        self.assertEqual(runner.manifest_counts(tasks),
                         {"histories": 16600, "metric_rows": 51800, "ledger_records": 33200})
        self.assertEqual(len(runner.expected_grid(tasks)), 51800)

    def test_family_and_case_grid_are_separate(self):
        tasks = runner.build_tasks()
        self.assertEqual(sum(t["case"] == "primary" for t in tasks), 4800)
        self.assertEqual(sum(t["case"] == "structured" for t in tasks), 4800)
        self.assertEqual(sum(t["case"] == "gross" for t in tasks), 2400)
        self.assertEqual(sum(t["case"] == "alternative" for t in tasks), 2400)
        self.assertEqual(sum(t["case"] == "early" for t in tasks), 400)
        self.assertEqual(sum(t["case"] == "v1" and t["reference_extractors"] == ("X3",)
                             for t in tasks), 525)

    def test_threshold_sensitivity_is_only_v3(self):
        tasks = runner.build_tasks()
        primary_v3 = [t for t in tasks if t["case"] == "primary" and t["family"] == "v3"]
        primary_v2 = [t for t in tasks if t["case"] == "primary" and t["family"] == "v2"]
        self.assertEqual(sum(t["thresholds"] == runner.THRESHOLDS for t in primary_v3), 1200)
        self.assertTrue(all(t["thresholds"] == (10.0,) for t in primary_v2))
        alternative_v3 = [t for t in tasks if t["case"] == "alternative" and t["family"] == "v3"]
        self.assertTrue(all(t["thresholds"] == runner.THRESHOLDS for t in alternative_v3))

    def test_candidate_source_is_frozen_at_352a09e(self):
        commit, digest = runner.candidate_source_hash()
        self.assertEqual(len(commit), 40)
        self.assertEqual(len(digest), 64)

    def test_heavy_score_arrays_are_not_csv_values(self):
        flat, ledger = runner._flatten({"rule": "C1_7", "pair_records": [{"x": 1}],
                                        "operational_confirmation_first_records": [{"x": 2}],
                                        "operational_confirmation_emissions": [{"x": 3}],
                                        "metrics": {"n": 1}})
        self.assertNotIn("pair_records", flat)
        self.assertEqual(flat["metrics"], '{"n":1}')
        self.assertEqual(ledger["pair_records"], [{"x": 1}])

    def test_cadence_metadata_is_a_stable_csv_column(self):
        fields = runner._fields([{"case": "primary", "cadence_metadata": "{}"}])
        self.assertIn("cadence_metadata", fields)
        self.assertEqual(fields.index("cadence_metadata"), 12)

    def test_qualification_rejects_wrong_stage_before_other_checks(self):
        freeze = "a" * 40
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / "receipt.json"
            receipt.write_text(json.dumps({"mode": "calibrate"}))
            with self.assertRaisesRegex(ValueError, "not a qualify"):
                runner.validate_qualification(receipt, {}, freeze, "b" * 64, "c" * 64)

    def test_qualification_accepts_producer_schema_and_separate_calibration_commit(self):
        freeze, calibration_commit = "a" * 40, "b" * 40
        inputs_hash, parameters_hash, calibration_hash = "c" * 64, "d" * 64, "e" * 64
        params = {"v2": {}, "v3": {}}
        phases = {p: {"passed": True, "mean_no_match_fraction": 0,
                      "morphology": {"passed": True},
                      "diversity": {era: {"summary": {}, "gate": {"passed": True}}
                                    for era in runner.ERAS}}
                  for p in ("random", "diverse")}
        attempts = {"v2.json": "f" * 64,
                    **{f"attempt_{i:02d}.json": "f" * 64 for i in range(27)}}
        q = {"mode": "qualify", "seed_base": "a04g-qualification|" + freeze,
             "freeze_commit": freeze, "commit": freeze, "inputs_sha256": inputs_hash,
             "parameters_sha256": parameters_hash, "configuration_count": 1,
             "replicates_per_era_phase": 32, "all_passed": True,
             "selected": {"parameters": params, "phases": phases}, "v2": phases,
             "source_sha256": {p: "f" * 64 for p in runner.QUALIFICATION_SOURCES},
             "calibration_receipt_sha256": calibration_hash,
             "calibration_attempts_sha256": attempts}
        anchor = {"prepared_inputs_sha256": inputs_hash, "parameters_sha256": parameters_hash,
                  "calibration_source_commit": calibration_commit,
                  "calibration_receipt_sha256": calibration_hash,
                  "calibration_attempts_sha256": attempts}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "configs").mkdir()
            (root / "configs/a04g_inputs.json").write_text(json.dumps(anchor))
            (root / "configs/a04g_benchmark.json").write_text(json.dumps(params))
            receipt = root / "receipt.json"
            receipt.write_text(json.dumps(q))
            with patch.object(runner, "ROOT", root), patch.object(
                    runner, "git_blob_sha256", return_value="f" * 64), patch.object(
                    runner, "git_commit", side_effect=lambda value: value):
                self.assertEqual(runner.validate_qualification(
                    receipt, params, freeze, inputs_hash, parameters_hash), runner.sha256(receipt))
                q["selected"]["phases"]["diverse"]["diversity"][runner.ERAS[0]]["gate"]["passed"] = False
                receipt.write_text(json.dumps(q))
                with self.assertRaisesRegex(ValueError, "observer-diversity"):
                    runner.validate_qualification(receipt, params, freeze, inputs_hash, parameters_hash)


if __name__ == "__main__":
    unittest.main()
