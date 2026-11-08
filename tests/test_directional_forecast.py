import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np
from scipy.optimize import OptimizeResult

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.directional_forecast import (
    _mark_transform,
    _offset_objective,
    _prepare_offset,
    fit_directional,
)


def fixture(n=30, *, constant_mark=False, missing_mark=None):
    ledger, evidence = [], []
    for i in range(n):
        end = 100.0 + 10.0 * i
        issue = end + 2.0
        duration = 10.0 if constant_mark else 8.0 + (i % 6)
        if missing_mark is not None and i in missing_mark:
            onset = None
            duration_value = None
        else:
            onset = end - duration
            duration_value = duration
        gap = 20.0 + (i % 8)
        ledger.append({
            "emission_index": i,
            "issue_time": issue,
            "end_t": end,
            "end_lo": end,
            "end_hi": end,
            "onset_t": onset,
            "duration": duration_value,
            "previous_gap": gap,
            "previous_gap_covered": True,
            "previous_duration": 11.0 + (i % 4),
            "earlier_gaps": [] if i % 3 == 0 else [math.log(18.0 + i % 3), math.log(22.0 + i % 2)],
        })
        if i % 5 == 0:
            evidence.append({"emission_index": i, "issue_time": issue,
                             "kind": "right_censored", "censor_at": end + gap + 3.0,
                             "computed_as_of": 9000.0, "evidence_available_at": 9000.0})
        else:
            onset_outcome = end + gap
            evidence.append({"emission_index": i, "issue_time": issue,
                             "kind": "interval", "onset_lo": onset_outcome - 0.1,
                             "onset_hi": onset_outcome + 0.1,
                             "computed_as_of": 9000.0, "evidence_available_at": 9000.0})
    return ledger, evidence


class DirectionalForecastTests(unittest.TestCase):
    def test_fixed_zero_offsets_nest_m2_exactly(self):
        ledger, evidence = fixture(constant_mark=True)
        bundle = fit_directional(ledger, evidence, 10000.0)
        self.assertEqual(bundle.models["M3"].coefficients["beta"], 0.0)
        self.assertEqual(bundle.models["P3"].coefficients["beta"], 0.0)
        for feature, outcome in zip(ledger, evidence):
            self.assertEqual(bundle.route(feature, "M3"), "M2")
            self.assertEqual(bundle.route(feature, "P3"), "M2")
            self.assertEqual(bundle.score(feature, outcome, "M3"),
                             bundle.score(feature, outcome, "M2"))
            self.assertEqual(bundle.score(feature, outcome, "P3"),
                             bundle.score(feature, outcome, "M2"))

    def test_directional_offsets_are_nonnegative(self):
        ledger, evidence = fixture()
        bundle = fit_directional(ledger, evidence, 10000.0)
        self.assertGreaterEqual(bundle.models["M3"].coefficients["beta"], 0.0)
        self.assertGreaterEqual(bundle.models["P3"].coefficients["beta"], 0.0)
        self.assertIn("at_bound", bundle.models["M3"].metadata)

    def test_constant_q_and_missing_local_level_are_fixed_zero(self):
        ledger, evidence = fixture()
        for row in ledger:
            row["previous_gap"] = 20.0
            row["earlier_gaps"] = []
        bundle = fit_directional(ledger, evidence, 10000.0)
        self.assertEqual(bundle.models["M2"].coefficients["previous_gap"], 0.0)
        self.assertEqual(bundle.models["M2"].coefficients["earlier_level"], 0.0)
        self.assertEqual(bundle.models["M2"].scales["previous_gap"], 1.0)
        self.assertEqual(bundle.models["M2"].scales["earlier_level"], 1.0)
        self.assertEqual(bundle.models["M2"].metadata["fixed_terms"],
                         ["previous_gap", "earlier_level"])

    def test_no_previous_gap_routes_every_mark_model_to_m0(self):
        ledger, evidence = fixture()
        bundle = fit_directional(ledger, evidence, 10000.0)
        feature = dict(ledger[4], previous_gap=None, previous_gap_covered=False)
        for name in ("M2", "M3", "P3"):
            self.assertEqual(bundle.route(feature, name), "M0")
            self.assertEqual(bundle.score(feature, evidence[4], name),
                             bundle.score(feature, evidence[4], "M0"))

    def test_missing_mark_routes_to_m2_and_training_remains_coherent(self):
        ledger, evidence = fixture(missing_mark={3, 9})
        bundle = fit_directional(ledger, evidence, 10000.0)
        self.assertGreater(bundle.models["M3"].metadata["valid_mark_count"], 0)
        self.assertEqual(bundle.route(ledger[3], "M3"), "M2")
        self.assertEqual(bundle.score(ledger[3], evidence[3], "M3"),
                         bundle.score(ledger[3], evidence[3], "M2"))

    def test_batchscore_matches_scalar_scores_and_zero_exposure_is_zero(self):
        ledger, evidence = fixture()
        bundle = fit_directional(ledger, evidence, 10000.0)
        batch = bundle.scores(ledger, evidence)
        for row, feature, outcome in zip(batch, ledger, evidence):
            for name in ("M0", "M2", "M3", "P3"):
                self.assertAlmostEqual(row[name], bundle.score(feature, outcome, name), places=12)
                self.assertEqual(row[f"{name}_route"], bundle.route(feature, name))
        zero = dict(evidence[4], kind="right_censored", censor_at=ledger[4]["issue_time"])
        for name in ("M0", "M2", "M3", "P3"):
            self.assertEqual(bundle.score(ledger[4], zero, name), 0.0)

    def test_excluded_rows_have_consistent_missing_scores(self):
        ledger, evidence = fixture()
        excluded = dict(evidence[2], kind="excluded", reason="fixture")
        bundle = fit_directional(ledger, evidence, 10000.0)
        row = bundle.scores(ledger, evidence[:2] + [excluded] + evidence[3:])[2]
        self.assertEqual(row["kind"], "excluded")
        for name in ("M0", "M2", "M3", "P3"):
            self.assertIsNone(row[name])
            self.assertIsNone(row[f"{name}_route"])

    def test_serialization_preserves_batch_scores(self):
        ledger, evidence = fixture()
        bundle = fit_directional(ledger, evidence, 10000.0)
        restored = type(bundle).from_dict(bundle.to_dict())
        self.assertEqual(bundle.scores(ledger, evidence), restored.scores(ledger, evidence))

    def test_training_availability_is_strict(self):
        ledger, evidence = fixture()
        with self.assertRaisesRegex(ValueError, "feature.issue_time"):
            fit_directional([dict(ledger[0], issue_time=10000.0)] + ledger[1:], evidence, 10000.0)
        poisoned = [dict(row) for row in evidence]
        poisoned[0]["computed_as_of"] = 10001.0
        with self.assertRaisesRegex(ValueError, "computed_as_of"):
            fit_directional(ledger, poisoned, 10000.0)

    def test_uniform_mixed_invalid_nodes_exclude_whole_mark_row(self):
        ledger, evidence = fixture()
        invalid = dict(ledger[4], onset_t=ledger[4]["end_t"] + 1.5,
                       duration=None)
        changed = ledger.copy()
        changed[4] = invalid
        bundle = fit_directional(changed, evidence, 10000.0, endpoint_mode="uniform_end")
        self.assertEqual(bundle.route(changed[4], "M3"), "M2")
        self.assertLess(bundle.models["M3"].metadata["valid_mark_count"],
                        bundle.models["M3"].metadata["baseline_training_count"])

    def test_offset_optimizer_failure_is_not_silently_replaced(self):
        ledger, evidence = fixture()
        bundle = fit_directional(ledger, evidence, 10000.0)
        rows = [{"feature": feature, "evidence": outcome,
                 "endpoints": np.array([feature["end_t"]]), "model_name": "M2"}
                for feature, outcome in zip(ledger, evidence)]
        failed = OptimizeResult(success=False, x=np.array([0.1]), fun=1e100,
                                jac=np.array([np.nan]), message="forced failure")
        with patch("dnmem.directional_forecast.minimize", return_value=failed):
            with self.assertRaisesRegex(ValueError, "offset optimization failed"):
                from dnmem.directional_forecast import _fit_offset
                _fit_offset("M3", rows, bundle.models["M2"], bundle._base_transform(),
                            "current", "log_duration", True, True, False)

    def test_batchscore_rejects_duplicate_missing_and_mismatched_rows(self):
        ledger, evidence = fixture()
        bundle = fit_directional(ledger, evidence, 10000.0)
        with self.assertRaisesRegex(ValueError, "duplicate feature"):
            bundle.scores(ledger + [ledger[0]], evidence)
        with self.assertRaisesRegex(ValueError, "same emission indices"):
            bundle.scores(ledger[:-1], evidence)
        with self.assertRaisesRegex(ValueError, "issue_time"):
            bundle.scores(ledger, evidence[:-1] + [dict(evidence[-1], issue_time=999.0)])

    def test_vectorized_offset_objective_matches_scalar_mixture(self):
        ledger, evidence = fixture()
        bundle = fit_directional(ledger, evidence, 10000.0)
        rows = []
        for i, (feature, outcome) in enumerate(zip(ledger[:6], evidence[:6])):
            endpoints = np.array([feature["end_t"]]) if i % 2 == 0 else np.array([
                feature["end_t"] - 0.5, feature["end_t"] + 0.5])
            rows.append({"feature": feature, "evidence": outcome,
                         "endpoints": endpoints, "model_name": "M2"})
        transform = bundle._base_transform()
        mark_transform, _ = _mark_transform(rows, "current", "log_duration", "uniform_end")
        prepared = _prepare_offset(rows, bundle.models["M2"], transform, mark_transform,
                                   "current", "log_duration", True)
        beta = np.array([0.17])
        scalar = _offset_objective(beta, rows, bundle.models["M2"], transform,
                                   mark_transform, "current", "log_duration", True)
        self.assertAlmostEqual(prepared.objective(beta), scalar, places=11)


if __name__ == "__main__":
    unittest.main()
