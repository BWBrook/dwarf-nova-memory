from __future__ import annotations

import json
import copy
import random
import gzip
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_joint_recovery as runner
import summarize_joint_recovery as runner_summary


def configurations(*families: str) -> dict[str, dict]:
    return {family: {"family": family, "phase": "phase", "shape_config": {},
                     "noise_multiplier": .95, "cadence_config": {}}
            for family in families}


class JointRecoveryRunnerTests(unittest.TestCase):
    def test_actual_producer_block_contract_and_fail_closed_receipts(self):
        from a04i_pipeline import BASE_SOURCES, assess_samples
        from a04h_morphology_targets import NAMES
        rng = random.Random(90681)
        samples = [{name: rng.gauss(0, 1) for name in NAMES} for _ in range(150)]
        real = dict.fromkeys(NAMES, 0.)
        inputs = {"joint_targets": real, "joint_diversity": {
            era: {"median": 10, "share_le_2": 0.} for era in runner.ERAS}}
        samples = [{"replicate": i, "valid": True, "statistics": value,
                    "diversity": {era: [10] for era in runner.ERAS}}
                   for i, value in enumerate(samples)]
        config = {"family": "v4", "pair_id": "v4-phase", "phase": "phase",
                  "configuration_id": "v4-00", "shape_config": {},
                  "noise_multiplier": .95, "cadence_config": {}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in BASE_SOURCES:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(relative)
            selected = root / "configs/a04i_selected.json"
            selected.write_text(json.dumps({"v4-phase": config}))
            attempt = root / "v4-00.json"
            attempt.write_text(json.dumps({"configuration": config, "samples": samples}))
            source_hashes = {name: runner.sha256(root / name) for name in BASE_SOURCES}
            grid_hash = runner.sha256(root / "configs/a04i_grid.json")
            manifest = {"prepared_inputs_sha256": "1" * 64,
                        "selected_config_sha256": runner.sha256(selected),
                        "grid_sha256": grid_hash, "original_inputs_sha256": "2" * 64,
                        "preparation_receipt_sha256": "3" * 64,
                        "calibration_receipt_sha256": "4" * 64,
                        "calibration_source_commit": "a" * 40,
                        "calibration_attempts_sha256": {"v4-00.json": "5" * 64}}
            (root / "configs/a04i_inputs.json").write_text(json.dumps(manifest))
            receipt = {"stage": "a04i-qualification", "freeze_commit": "b" * 40,
                       "seed_base": runner.QUALIFICATION_BASE + "b" * 40,
                       "inputs_sha256": "1" * 64,
                       "selected_config_sha256": runner.sha256(selected),
                       "replicates_per_pair": 150, "eligible_pair_ids": ["v4-phase"],
                       "grid_sha256": grid_hash, "source_sha256": source_hashes,
                       "calibration_receipt_sha256": "4" * 64,
                       "calibration_attempts_sha256": {"v4-00.json": "5" * 64},
                       "qualification_attempts_sha256": {"v4-00.json": runner.sha256(attempt)},
                       "pairs": {"v4-phase": {"configuration": config, **assess_samples(samples, inputs)}}}
            path = root / "qualification.json"
            def validate(value):
                path.write_text(json.dumps(value))
                return runner.validate_qualification(path, {"v4-phase": config}, "b" * 40,
                                                     "1" * 64, runner.sha256(selected), inputs)
            with patch.object(runner, "ROOT", root), \
                 patch.object(runner, "git_commit", side_effect=lambda commit: commit), \
                 patch.object(runner, "git_blob_sha256", side_effect=lambda commit, name: runner.sha256(root / name)):
                self.assertEqual(validate(receipt)["eligible"], ["v4-phase"])
                for defect in ("source", "grid", "replicates", "failed_gate", "missing_records", "evidence"):
                    broken = copy.deepcopy(receipt)
                    if defect == "source":
                        broken["source_sha256"].pop(BASE_SOURCES[0])
                    elif defect == "grid":
                        broken["grid_sha256"] = "6" * 64
                    elif defect == "replicates":
                        broken["pairs"]["v4-phase"]["cadence"]["replicates"] = 149
                    elif defect == "failed_gate":
                        broken["pairs"]["v4-phase"]["waveform"]["pass"] = False
                    elif defect == "missing_records":
                        broken["pairs"]["v4-phase"]["valid_records"] = 149
                    else:
                        broken["qualification_attempts_sha256"]["v4-00.json"] = "7" * 64
                    with self.subTest(defect=defect), self.assertRaises(ValueError):
                        validate(broken)
                second = {**config, "configuration_id": "v2-00", "pair_id": "v2-phase", "family": "v2"}
                second_attempt = root / "v2-00.json"
                second_attempt.write_text(json.dumps({"configuration": second, "samples": samples}))
                broken = copy.deepcopy(receipt)
                broken["qualification_attempts_sha256"]["v2-00.json"] = runner.sha256(second_attempt)
                broken["pairs"]["v2-phase"] = {"configuration": second, **assess_samples(samples, inputs)}
                broken["pairs"]["v2-phase"]["eligible"] = False
                path.write_text(json.dumps(broken))
                with self.assertRaisesRegex(ValueError, "eligibility differs"):
                    runner.validate_qualification(path, {"v4-phase": config, "v2-phase": second},
                                                  "b" * 40, "1" * 64, runner.sha256(selected), inputs)

    def test_ledger_requires_exact_keys_rules_seeds_and_arrays(self):
        task = {"family": "v4-phase", "phase": "phase", "case": "primary",
                "stratum": "1910_1929", "replicate": 0}
        base = "a04i-validation|freeze"
        records = [{**task, "rule": rule, "threshold": 10.,
                    "seed": runner.seed_for(base, task["family"], task["case"], task["stratum"], 0),
                    **{name: [] for name in ("pair_records", "operational_confirmation_first_records",
                                             "operational_confirmation_emissions", "cadence_events")}}
                   for rule in runner.RULES]
        with tempfile.TemporaryDirectory() as directory, patch.object(runner, "build_tasks", return_value=[task]):
            path = Path(directory) / "ledger.jsonl.gz"
            def validate(values):
                with gzip.open(path, "wt") as handle:
                    for value in values:
                        handle.write(json.dumps(value) + "\n")
                runner_summary._validate_ledger(path, {"families": {}, "validation_base": base})
            validate(records)
            for defect in ("duplicate", "seed", "array", "missing"):
                broken = copy.deepcopy(records)
                if defect == "duplicate":
                    broken[1] = broken[0]
                elif defect == "seed":
                    broken[0]["seed"] += 1
                elif defect == "array":
                    broken[0].pop("pair_records")
                else:
                    broken.pop()
                with self.subTest(defect=defect), self.assertRaises(ValueError):
                    validate(broken)

    def test_exact_manifest_per_family_and_two_family_scaling(self):
        one = runner.build_tasks(configurations("v2"))
        two = runner.build_tasks(configurations("v2", "v4"))
        self.assertEqual(len(one), 4800)
        self.assertEqual(runner.manifest_counts(one),
                         {"histories": 4800, "metric_rows": 16650, "ledger_records": 9600})
        self.assertEqual(runner.manifest_counts(two),
                         {"histories": 9600, "metric_rows": 33300, "ledger_records": 19200})

    def test_threshold_subsets_and_reference_subset(self):
        tasks = runner.build_tasks(configurations("v2"))
        primary = [task for task in tasks if task["case"] == "primary"]
        alternative = [task for task in tasks if task["case"] == "alternative"]
        self.assertEqual(sum(task["thresholds"] == runner.THRESHOLDS for task in primary), 600)
        self.assertTrue(all(task["thresholds"] == runner.THRESHOLDS for task in alternative))
        self.assertEqual(sum(bool(task["reference_extractors"]) for task in tasks), 375)
        self.assertTrue(all(len(task["reference_extractors"]) == 3 for task in tasks
                            if task["replicate"] < 25))
        self.assertTrue(all(not task["reference_extractors"] for task in tasks
                            if task["replicate"] >= 25))

    def test_seed_labels_omit_phase(self):
        first = runner.seed_for("a04i-validation|freeze", "v2", "primary", "1910_1929", 0)
        second = runner.seed_for("a04i-validation|freeze", "v2", "primary", "1910_1929", 0)
        self.assertEqual(first, second)
        self.assertNotEqual(first, runner.seed_for("a04i-validation|freeze", "v2", "primary", "1930_1949", 0))

    def test_cadence_metadata_and_heavy_score_flattening(self):
        flat, ledger = runner._flatten({"rule": "C1_7", "metrics": {"n": 1},
                                        "pair_records": [{"x": 1}],
                                        "operational_confirmation_first_records": [{"x": 2}],
                                        "operational_confirmation_emissions": [{"x": 3}]})
        self.assertEqual(flat["metrics"], '{"n":1}')
        self.assertNotIn("pair_records", flat)
        self.assertEqual(ledger["operational_confirmation_emissions"], [{"x": 3}])

    def test_global_decision_requires_both_rules_and_all_qualified_pairs(self):
        cells = []
        for family in ("v2-phase", "v4-phase"):
            for rule in runner.RULES:
                for case in ("primary", "structured"):
                    for era in runner.ERAS:
                        cells.append({"family": family, "rule": rule, "extractor": "X4",
                                      "threshold": "10.0", "case": case, "verdict": "PASS"})
                for era in runner.ERAS:
                    cells.append({"family": family, "rule": rule, "extractor": "X4",
                                  "threshold": "10.0", "case": "gross", "verdict": "PASS"})
        decisions = runner_summary.candidate_decisions(cells, ["v2-phase", "v4-phase"])
        self.assertTrue(all(item["verdict"] == "PASS" for item in decisions))

    def test_qualification_uses_only_explicit_eligible_families(self):
        params = {"v2-phase": {"family": "v2", "phase": "phase", "shape_config": {},
                               "noise_multiplier": .95, "cadence_config": {}},
                  "v4-phase": {"family": "v4", "phase": "phase", "shape_config": {},
                               "noise_multiplier": .95, "cadence_config": {}}}
        receipt = {"stage": "a04i-qualification", "eligible_pair_ids": ["v4-phase"],
                   "pairs": {"v4-phase": {"configuration": params["v4-phase"]}}}
        selected = runner.qualified_configurations(params, receipt)
        self.assertEqual(set(selected), {"v4-phase"})
        self.assertEqual(json.dumps(selected["v4-phase"], sort_keys=True),
                         json.dumps({**params["v4-phase"], "pair_id": "v4-phase"}, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
