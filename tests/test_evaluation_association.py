import copy
import json
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np
from scipy.optimize import OptimizeResult


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.directional_forecast import _prepare_offset, fit_directional
from dnmem.evaluation_association import (
    _joint_association,
    _joint_offset_objective,
    _joint_rows,
    _prepare_joint_offset,
    evaluation_association,
)
from dnmem.fit_profiles import _base_model_profile, _mark_profile


def association_fixture(
    n=100,
    *,
    constant_current=False,
    collinear_marks=False,
    seed=20261108,
):
    rng = np.random.default_rng(seed)
    ledger, evidence = [], []
    cutoff = 1000.0 + 50.0 * n + 200.0
    for index in range(n):
        current_score = float(rng.normal())
        previous_score = current_score if collinear_marks else float(rng.normal())
        q_score = float(rng.normal())
        noise = float(rng.normal())
        if constant_current:
            duration = 10.0
            current_effect = 0.0
        else:
            duration = math.exp(2.30 + 0.25 * current_score)
            current_effect = 0.36 * current_score
        previous_duration = (duration if collinear_marks
                             else math.exp(2.25 + 0.27 * previous_score))
        previous_effect = (-0.28 * previous_score
                           if not constant_current or not collinear_marks else 0.0)
        previous_gap = math.exp(3.55 + 0.22 * q_score)
        following_gap = math.exp(
            3.60 + 0.18 * q_score + current_effect + previous_effect + 0.20 * noise
        )
        end = 1000.0 + 50.0 * index
        issue = end + 1.0
        onset = end - duration
        ledger.append({
            "emission_index": index,
            "issue_time": issue,
            "landmark_available": True,
            "end_t": end,
            "end_lo": end,
            "end_hi": end,
            "onset_t": onset,
            "duration": duration,
            "previous_gap": previous_gap,
            "previous_gap_covered": True,
            "previous_duration": previous_duration,
            "earlier_gaps": [],
        })
        evidence.append({
            "emission_index": index,
            "issue_time": issue,
            "kind": "interval",
            "onset_lo": end + following_gap - 0.75,
            "onset_hi": end + following_gap + 0.75,
            "computed_as_of": cutoff,
            "evidence_available_at": cutoff,
        })
    return ledger, evidence, cutoff


class EvaluationAssociationTests(unittest.TestCase):
    def test_signed_staged_and_joint_offsets_recover_opposite_signs_and_serialize(self):
        ledger, evidence, cutoff = association_fixture(n=80)
        ledger_before, evidence_before = copy.deepcopy(ledger), copy.deepcopy(evidence)
        result = evaluation_association(ledger, evidence, cutoff)

        staged = result["staged"]["bundle"]["models"]
        self.assertGreater(staged["M3"]["coefficients"]["beta"], 0.0)
        self.assertLess(staged["P3"]["coefficients"]["beta"], 0.0)
        joint = result["joint"]
        self.assertGreater(joint["coefficients"]["current_duration"], 0.0)
        self.assertLess(joint["coefficients"]["previous_duration"], 0.0)
        self.assertTrue(joint["identifiability"]["full_column_rank"])
        self.assertEqual(joint["joint_valid_count"], 80)
        self.assertEqual(result["interpretation"]["forecast_claim"], "none")
        json.dumps(result, allow_nan=False)
        self.assertEqual(ledger, ledger_before)
        self.assertEqual(evidence, evidence_before)

    def test_joint_vectorized_scalar_and_restricted_one_offset_objectives_nest(self):
        ledger, evidence, cutoff = association_fixture(n=60)
        bundle = fit_directional(ledger, evidence, cutoff, directional=False)
        _, common = _joint_rows(bundle, ledger, evidence)
        base = bundle.models["M2"]
        base_transform = bundle._base_transform()
        prepared, transforms, fixed = _prepare_joint_offset(
            common, base, base_transform, local_level=True
        )
        self.assertEqual(fixed, ())
        beta = np.array([0.17, -0.12])
        scalar = _joint_offset_objective(
            beta, common, base, base_transform, transforms, local_level=True
        )
        self.assertAlmostEqual(prepared.objective(beta), scalar, places=10)

        current = _prepare_offset(
            common, base, base_transform, transforms["current"],
            "current", "log_duration", True,
        )
        previous = _prepare_offset(
            common, base, base_transform, transforms["previous"],
            "previous", "log_duration", True,
        )
        self.assertAlmostEqual(
            prepared.objective(np.array([beta[0], 0.0])),
            current.objective(np.array([beta[0]])),
            places=11,
        )
        self.assertAlmostEqual(
            prepared.objective(np.array([0.0, beta[1]])),
            previous.objective(np.array([beta[1]])),
            places=11,
        )
        self.assertAlmostEqual(
            prepared.objective(np.zeros(2)), current.objective(np.zeros(1)), places=11
        )

    def test_association_profiles_only_required_models_and_serializes_joint(self):
        ledger, evidence, cutoff = association_fixture(n=55)
        with patch(
            "dnmem.fit_profiles._r0_profile",
            side_effect=AssertionError("R0 profile is not an S1 diagnostic"),
        ), patch(
            "dnmem.evaluation_association._base_model_profile",
            wraps=_base_model_profile,
        ) as base_profile, patch(
            "dnmem.evaluation_association._mark_profile",
            wraps=_mark_profile,
        ) as mark_profile:
            result = evaluation_association(ledger, evidence, cutoff)

        base_profile.assert_called_once()
        self.assertEqual(base_profile.call_args.args[0], "M2")
        self.assertEqual(
            [call.args[0] for call in mark_profile.call_args_list], ["M3", "P3"]
        )
        self.assertEqual(set(result["staged"]["profiles"]), {"M2", "M3", "P3"})
        self.assertEqual(result["joint"]["status"], "fitted")
        self.assertTrue(result["joint"]["identifiability"]["full_column_rank"])
        json.dumps(result, allow_nan=False)

    def test_constant_and_collinear_marks_are_not_reported_as_separately_identified(self):
        ledger, evidence, cutoff = association_fixture(n=70, constant_current=True)
        bundle = fit_directional(ledger, evidence, cutoff, directional=False)
        constant = _joint_association(bundle, ledger, evidence)
        self.assertEqual(constant["bounds"][0], [0.0, 0.0])
        self.assertEqual(constant["coefficients"]["current_duration"], 0.0)
        self.assertEqual(
            constant["identifiability"]["coefficient_status"]["current_duration"],
            "fixed_constant",
        )
        self.assertEqual(
            constant["profiles"]["current_duration"]["status"], "fixed_unidentifiable"
        )

        ledger, evidence, cutoff = association_fixture(n=70, collinear_marks=True)
        bundle = fit_directional(ledger, evidence, cutoff, directional=False)
        collinear = _joint_association(bundle, ledger, evidence)
        self.assertFalse(collinear["identifiability"]["full_column_rank"])
        self.assertEqual(collinear["identifiability"]["design_rank"], 1)
        for name in ("current_duration", "previous_duration"):
            self.assertEqual(
                collinear["identifiability"]["coefficient_status"][name],
                "not_coefficient_identified_joint_collinearity",
            )
            self.assertFalse(collinear["profiles"][name]["coefficient_identified"])

    def test_cutoff_is_strict_and_optimizer_failure_is_a_hard_error(self):
        ledger, evidence, cutoff = association_fixture(n=45)
        poisoned = [dict(row) for row in ledger]
        poisoned[0]["issue_time"] = cutoff
        with self.assertRaisesRegex(ValueError, "feature.issue_time"):
            evaluation_association(poisoned, evidence, cutoff)

        bundle = fit_directional(ledger, evidence, cutoff, directional=False)
        failed = OptimizeResult(
            success=False,
            x=np.array([0.0, 0.0]),
            fun=1e100,
            jac=np.array([np.nan, np.nan]),
            message="forced joint failure",
        )
        with patch("dnmem.evaluation_association.minimize", return_value=failed):
            with self.assertRaisesRegex(ValueError, "joint association optimization failed"):
                _joint_association(bundle, ledger, evidence)


if __name__ == "__main__":
    unittest.main()
