import csv
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "publish_x3_validation", ROOT / "scripts" / "publish_x3_validation.py"
)
PUBLISH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PUBLISH)


def metric(estimate=0.5, lower=0.4, upper=0.6):
    return {"estimate": estimate, "mcse": 0.02, "lower": lower, "upper": upper, "undefined": 0}


def cell(case, stratum, phase, rule):
    names = PUBLISH.GATE_NAMES
    metrics = {name: metric() for name in names if name != "state_cadence_no_match"}
    metrics["operational_confirmation_false_per_year"] = metric(0.05, 0.02, 0.08)
    criteria = {name: "PASS" for name in names if name != "state_cadence_no_match"}
    if phase == "state":
        metrics["cadence_no_match_fraction"] = metric(0.01, 0.0, 0.02)
        criteria["state_cadence_no_match"] = "PASS"
    metrics["operational_confirmation_unsafe_per_year"] = metric(0.1, 0.05, 0.15)
    return {"case": case, "stratum": stratum, "phase": phase, "threshold": "10.0",
            "extractor": "X3", "rule": rule, "verdict": "PASS",
            "criteria": criteria, "metrics": metrics}


class PublishX3ValidationTests(TestCase):
    def fixture(self, directory):
        cells = []
        for rule in PUBLISH.RULES:
            for case in PUBLISH.DECISIVE_CASES:
                for era in PUBLISH.ERAS:
                    for phase in ("random", "state"):
                        cells.append(cell(case, era, phase, rule))
        for case in ("v1", "offset", "alternative"):
            cells.append({"case": case, "stratum": "1910_1929", "phase": "random",
                          "threshold": "10.0", "extractor": "X3", "rule": "C1_7",
                          "verdict": "INCONCLUSIVE", "criteria": {},
                          "metrics": {"recovered_r": metric(0.2, 0.1, 0.3),
                                      "oracle_r_all": metric(0.3, 0.2, 0.4)}})
        receipt = {"status": "completed", "validation_base": "a04d-validation|" + "a" * 40,
                   "freeze_commit": "a" * 40, "actual_commit": "b" * 40,
                   "runtime_source_sha256": {"runtime.py": "c" * 64},
                   "completed_histories": 7600,
                   "completed_metric_rows": 79200, "completion_count": 7600,
                   "metrics_sha256": "a" * 64,
                   "task_manifest": {"expected_histories": 7600,
                                     "expected_metric_rows": 79200,
                                     "expected_aggregate_cells": 324}}
        summary = {"run_receipt": receipt, "cells": cells,
                   "candidate_decisions": [{"rule": rule, "verdict": "PASS"}
                                            for rule in PUBLISH.RULES],
                   "selected": {"extractor": "X3", "rule": "C1_7"}}
        source = directory / "fullsummary.json"
        source.write_text(json.dumps(summary))
        (directory / "receipt.json").write_text(json.dumps(receipt))
        return source

    def test_writes_24_decisive_rows_and_unsafe_gate(self):
        with TemporaryDirectory() as temp:
            directory = Path(temp)
            source = self.fixture(directory)
            output = directory / "published"
            manifest = PUBLISH.publish(source, output)
            with (output / "public_decision.csv").open(newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 24)
            self.assertEqual(rows[0]["operational_confirmation_false_per_year_diagnostic_only"], "true")
            self.assertEqual(rows[0]["operational_confirmation_unsafe_per_year_verdict"], "PASS")
            self.assertEqual(manifest["decision_rows"], 24)
            public = json.loads((output / "public_manifest.json").read_text())
            self.assertNotIn("cells", public)
            self.assertNotIn("cell_verdicts", json.dumps(public))

    def test_undefined_outcome_is_published_as_inconclusive(self):
        with TemporaryDirectory() as temp:
            directory = Path(temp)
            source = self.fixture(directory)
            summary = json.loads(source.read_text())
            c = summary["cells"][0]
            c["metrics"]["total_bias"] = {"estimate": None, "lower": None,
                                            "upper": None, "undefined": 400}
            c["criteria"]["total_bias"] = "INCONCLUSIVE"
            c["verdict"] = "INCONCLUSIVE"
            source.write_text(json.dumps(summary))
            output = directory / "published"
            PUBLISH.publish(source, output)
            with (output / "public_decision.csv").open(newline="") as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(row["total_bias_estimate"], "")
            self.assertEqual(row["total_bias_verdict"], "INCONCLUSIVE")

    def test_refuses_overwrite(self):
        with TemporaryDirectory() as temp:
            directory = Path(temp)
            source = self.fixture(directory)
            output = directory / "published"
            PUBLISH.publish(source, output)
            with self.assertRaises(FileExistsError):
                PUBLISH.publish(source, output)

    def test_missing_unsafe_gate_refuses_publication(self):
        with TemporaryDirectory() as temp:
            directory = Path(temp)
            source = self.fixture(directory)
            summary = json.loads(source.read_text())
            del summary["cells"][0]["metrics"]["operational_confirmation_unsafe_per_year"]
            source.write_text(json.dumps(summary))
            with self.assertRaisesRegex(ValueError, "operational_confirmation_unsafe_per_year"):
                PUBLISH.publish(source, directory / "published")

    def test_missing_receipt_provenance_refuses_publication(self):
        with TemporaryDirectory() as temp:
            directory = Path(temp)
            source = self.fixture(directory)
            summary = json.loads(source.read_text())
            del summary["run_receipt"]["runtime_source_sha256"]
            source.write_text(json.dumps(summary))
            receipt = json.loads((directory / "receipt.json").read_text())
            del receipt["runtime_source_sha256"]
            (directory / "receipt.json").write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, "runtime_source_sha256"):
                PUBLISH.publish(source, directory / "published")


if __name__ == "__main__":
    import unittest
    unittest.main()
