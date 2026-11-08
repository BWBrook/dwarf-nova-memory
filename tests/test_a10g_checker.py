import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts import check_a10g_evaluation as checker
from scripts.check_a10d_scores import conditional_score, current_durations, endpoint_nodes


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "data/fits/a10e_1910_1959/frozen_parameters.json"


class A10gCheckerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        shutil.copy2(FROZEN, self.directory / "frozen_parameters.json")
        features = [
            {
                "emission_index": 10, "issue_time": checker.START + 100.0,
                "emitted_at": checker.START + 99.9, "prefix_last_jd": checker.START + 99.8,
                "landmark_available": True, "onset_t": checker.START + 92.0,
                "end_t": checker.START + 97.0, "previous_gap": None,
                "previous_gap_covered": False, "previous_duration": None,
                "end_lo": checker.START + 96.5, "end_hi": checker.START + 97.5,
                "earlier_gaps": [],
            },
            {
                "emission_index": 20, "issue_time": checker.START + 2300.0,
                "emitted_at": checker.START + 2299.9, "prefix_last_jd": checker.START + 2299.8,
                "landmark_available": True, "onset_t": checker.START + 2290.0,
                "end_t": checker.START + 2298.0, "previous_gap": 30.0,
                "previous_gap_covered": True, "previous_duration": 9.0,
                "end_lo": checker.START + 2297.5, "end_hi": checker.START + 2298.5,
                "earlier_gaps": [3.0, 3.1],
            },
        ]
        evidence = [
            {"emission_index": 10, "issue_time": checker.START + 100.0,
             "computed_as_of": checker.END, "evidence_available_at": checker.END,
             "kind": "interval", "onset_lo": checker.START + 120.0,
             "onset_hi": checker.START + 121.0},
            {"emission_index": 20, "issue_time": checker.START + 2300.0,
             "computed_as_of": checker.END, "evidence_available_at": checker.END,
             "kind": "interval", "onset_lo": checker.START + 2320.0,
             "onset_hi": checker.START + 2321.0},
        ]
        self._write("ledger-0.0.json", features)
        self._write("evidence-0.0.json", evidence)
        delay_features = [dict(row, issue_time=row["issue_time"] + 2.0, latency=2.0) for row in features]
        delay_evidence = [dict(row, issue_time=row["issue_time"] + 2.0) for row in evidence]
        self._write("ledger-2.0.json", delay_features)
        self._write("evidence-2.0.json", delay_evidence)
        concordance = {}
        for delay, led, evs in (("0.0", features, evidence), ("2.0", delay_features, delay_evidence)):
            digest = checker.concordance_digest(led, evs)
            concordance[delay] = {"match": True, "differences": [],
                                  "candidate_sha256": digest,
                                  "reference_sha256": digest}
        self._write("concordance.json", concordance)
        frozen = json.loads((self.directory / "frozen_parameters.json").read_text())
        for variant in checker.VARIANTS:
            delay = "2.0" if variant == "delay_2" else "0.0"
            led = delay_features if delay == "2.0" else features
            evs = delay_evidence if delay == "2.0" else evidence
            rows = []
            spec = frozen[variant]
            for feature, ev in zip(led, evs):
                nodes = endpoint_nodes(feature, spec["endpoint_mode"], int(spec["nodes"]))
                current_mark = current_durations(feature, nodes) is not None
                if spec["joint_marks"] and feature["emission_index"] == 10:
                    continue
                row = {"emission_index": feature["emission_index"], "issue_time": feature["issue_time"],
                       "kind": ev["kind"]}
                for name in checker.MODELS:
                    route = checker.route_for(name, spec["models"][name], feature, True, current_mark)
                    row[f"{name}_route"] = route
                    row[name] = conditional_score(feature, ev, spec, route)
                row.update({"gain_M2_M0": row["M2"] - row["M0"],
                            "gain_M3_M2": row["M3"] - row["M2"],
                            "gain_M3_P3": row["M3"] - row["P3"],
                            "gain_P3_M2": row["P3"] - row["M2"]})
                rows.append(row)
            self._write(f"{variant}-scores.json", rows)
        primary = json.loads((self.directory / "primary-scores.json").read_text())
        summary = checker.primary_interval(primary)
        self._write("primary.json", {key: summary[key] for key in
                                      ("estimate", "se", "lower", "upper", "confirmed", "n", "blocks",
                                       "origin", "years", "interval", "reference_gain",
                                       "upper_below_reference")})
        self._receipt()

    def tearDown(self):
        self.temp.cleanup()

    def _write(self, name, value):
        (self.directory / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")

    def _receipt(self):
        files = {}
        for path in self.directory.iterdir():
            if path.name != "receipt.json":
                files[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        concordance_path = self.directory / "concordance.json"
        self._write("receipt.json", {"mode": "rehearsal", "concordance_pass": True,
                                      "concordance_sha256": hashlib.sha256(concordance_path.read_bytes()).hexdigest(),
                                      "files_sha256": files})

    def _refresh_receipt(self):
        self._receipt()

    def test_valid_rehearsal_retains_fallback_zero_and_exact_zero_p3(self):
        report = checker.audit(self.directory)
        self.assertTrue(report["complete"], report["audit_failures"])
        primary = json.loads((self.directory / "primary-scores.json").read_text())
        self.assertEqual(primary[0]["M3_route"], "M0")
        self.assertEqual(primary[0]["gain_M3_M2"], 0.0)
        self.assertEqual(primary[1]["P3_route"], "M2")
        self.assertEqual(primary[1]["P3"], primary[1]["M2"])

    def test_false_confirmed_flag_is_reported(self):
        primary_path = self.directory / "primary.json"
        primary = json.loads(primary_path.read_text())
        primary["confirmed"] = not primary["confirmed"]
        self._write("primary.json", primary)
        self._refresh_receipt()
        report = checker.audit(self.directory)
        self.assertTrue(any(f["kind"] == "primary_mismatch" and f["field"] == "confirmed"
                            for f in report["audit_failures"]))

    def test_bad_score_duplicate_id_and_hash_are_all_reported(self):
        score_path = self.directory / "primary-scores.json"
        rows = json.loads(score_path.read_text())
        rows[0]["M3"] += 0.1
        rows.append(dict(rows[0]))
        self._write("primary-scores.json", rows)
        receipt = json.loads((self.directory / "receipt.json").read_text())
        receipt["files_sha256"]["primary-scores.json"] = "bad"
        self._write("receipt.json", receipt)
        report = checker.audit(self.directory)
        kinds = {f["kind"] for f in report["audit_failures"]}
        self.assertIn("file_hash_mismatch", kinds)
        self.assertIn("duplicate_or_bad_score_id", kinds)
        self.assertIn("score_mismatch", kinds)

    def test_concordance_difference_is_pre_score_hard_stop(self):
        concordance_path = self.directory / "concordance.json"
        concordance = json.loads(concordance_path.read_text())
        concordance["2.0"]["differences"] = [{"field": "issue_time"}]
        self._write("concordance.json", concordance)
        self._refresh_receipt()
        report = checker.audit(self.directory)
        self.assertTrue(any(f["kind"] == "concordance_differences" and f["delay"] == "2.0"
                            for f in report["audit_failures"]))
        self.assertEqual(report["details"], {})
        self.assertIsNone(report["primary_calculated"])

    def test_candidate_digest_binding_rejects_tampered_ledger(self):
        ledger_path = self.directory / "ledger-0.0.json"
        ledger = json.loads(ledger_path.read_text())
        ledger[0]["prefix_last_jd"] -= 0.01
        self._write("ledger-0.0.json", ledger)
        self._refresh_receipt()
        report = checker.audit(self.directory)
        self.assertTrue(any(f["kind"] == "candidate_concordance_digest_mismatch"
                            and f["delay"] == "0.0" for f in report["audit_failures"]))
        self.assertEqual(report["details"], {})

    def test_primary_interval_accepts_zero_or_negative_gain_without_confirmation(self):
        rows = [
            {"issue_time": checker.START + 1, "M2": 0.0, "M3": 0.0},
            {"issue_time": checker.START + 2300, "M2": 0.0, "M3": -1.0},
        ]
        result = checker.primary_interval(rows)
        self.assertLessEqual(result["lower"], 0.0)
        self.assertFalse(result["confirmed"])

    def test_confirmation_and_small_upper_bound_are_independent_flags(self):
        rows = [
            {"issue_time": checker.START + 1, "M2": 0.0, "M3": 0.002},
            {"issue_time": checker.START + 2300, "M2": 0.0, "M3": 0.002},
        ]
        result = checker.primary_interval(rows)
        self.assertTrue(result["confirmed"])
        self.assertTrue(result["upper_below_reference"])

    def test_tampered_magnitude_flag_is_reported(self):
        primary_path = self.directory / "primary.json"
        primary = json.loads(primary_path.read_text())
        primary["upper_below_reference"] = not primary["upper_below_reference"]
        self._write("primary.json", primary)
        self._refresh_receipt()
        report = checker.audit(self.directory)
        self.assertTrue(any(f["kind"] == "primary_mismatch" and
                            f["field"] == "upper_below_reference"
                            for f in report["audit_failures"]))


if __name__ == "__main__":
    unittest.main()
