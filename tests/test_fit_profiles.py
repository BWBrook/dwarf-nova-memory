import copy
import json
import math
import unittest

from dnmem.directional_forecast import fit_directional
from dnmem.fit_profiles import profile_bundle

from tests.test_directional_forecast import fixture


class FitProfileTests(unittest.TestCase):
    def test_profiles_nest_frozen_fit_are_serializable_and_do_not_mutate(self):
        ledger, evidence = fixture(n=20)
        bundle = fit_directional(ledger, evidence, 10000.0)
        before = copy.deepcopy(bundle.to_dict())
        result = profile_bundle(bundle, ledger, evidence)
        self.assertEqual(bundle.to_dict(), before)
        json.dumps(result, allow_nan=False)
        self.assertEqual(result["likelihood_ratio_cutoff"], 3.841)
        for model in result["models"].values():
            self.assertLess(abs(model["objective_scalar_difference"]), 1e-8)
            for profile in model["profiles"].values():
                fitted = min(profile["evaluations"],
                             key=lambda point: abs(point["value"] - profile["estimate"]))
                self.assertLess(fitted["likelihood_ratio"], 1e-4)

    def test_identifiable_zero_bound_has_one_sided_support_and_zero_point(self):
        ledger, evidence = fixture(n=30)
        bundle = fit_directional(ledger, evidence, 10000.0)
        self.assertFalse(bundle.models["M3"].metadata["unidentifiable"])
        self.assertEqual(bundle.models["M3"].coefficients["beta"], 0.0)
        profile = profile_bundle(bundle, ledger, evidence)["models"]["M3"]["profiles"]["beta"]
        self.assertEqual(profile["status"], "profiled")
        self.assertTrue(profile["at_lower_bound"])
        self.assertEqual(profile["likelihood_support_interval"]["lower"], 0.0)
        self.assertTrue(profile["likelihood_support_interval"]["lower_clipped_to_bound"])
        zero = next(point for point in profile["evaluations"] if point["value"] == 0.0)
        self.assertEqual(zero["likelihood_ratio"], 0.0)
        self.assertGreater(profile["likelihood_support_interval"]["upper"], 0.0)
        self.assertIn("CONDITIONAL fixed-M2", profile_bundle(bundle, ledger, evidence)
                      ["models"]["M3"]["interval_scope"])

    def test_constant_predictors_are_fixed_and_labelled(self):
        ledger, evidence = fixture(n=20, constant_mark=True)
        for row in ledger:
            row["previous_gap"] = 20.0
            row["earlier_gaps"] = []
        bundle = fit_directional(ledger, evidence, 10000.0)
        result = profile_bundle(bundle, ledger, evidence)
        for name in ("previous_gap", "earlier_level"):
            profile = result["models"]["M2"]["profiles"][name]
            self.assertEqual(profile["status"], "fixed_unidentifiable")
            self.assertEqual(profile["estimate"], 0.0)
            self.assertEqual(profile["likelihood_support_interval"]["lower"], 0.0)
            self.assertEqual(profile["likelihood_support_interval"]["upper"], 0.0)
        mark = result["models"]["M3"]["profiles"]["beta"]
        self.assertEqual(mark["status"], "fixed_unidentifiable")
        self.assertIn("constant", mark["fixed_reason"])

    def test_type_within_profiles_reoptimize_only_the_other_mark_coefficient(self):
        ledger, evidence = fixture(n=24)
        bundle = fit_directional(ledger, evidence, 10000.0, mark_mode="type_within")
        result = profile_bundle(bundle, ledger, evidence)
        profiles = result["models"]["M3"]["profiles"]
        self.assertEqual(set(profiles), {"beta_type", "beta_within"})
        for name, profile in profiles.items():
            other = 1 if name == "beta_type" else 0
            for point in profile["evaluations"]:
                self.assertEqual(len(point["nuisance_optimum"]), 2)
                if profile["status"] == "profiled":
                    self.assertTrue(math.isfinite(point["nuisance_optimum"][other]))
        self.assertTrue(result["models"]["M3"]["frozen_m2_nuisance"])

    def test_row_populations_reconstruct_routing_and_joint_mark_subset(self):
        ledger, evidence = fixture(n=24)
        evidence[0] = dict(evidence[0], kind="excluded", reason="fixture")
        ledger[1] = dict(ledger[1], landmark_available=False, end_t=None,
                         end_lo=None, end_hi=None)
        ledger[2] = dict(ledger[2], previous_gap=None, previous_gap_covered=False)
        ledger[3] = dict(ledger[3], onset_t=None, duration=None)
        ledger[4] = dict(ledger[4], previous_duration=None)
        bundle = fit_directional(ledger, evidence, 10000.0, joint_marks=True)
        result = profile_bundle(bundle, ledger, evidence)
        self.assertEqual(result["models"]["R0"]["row_count"], bundle.r0.n_fit)
        self.assertEqual(result["models"]["M0"]["row_count"], bundle.models["M0"].n_fit)
        self.assertEqual(result["models"]["M2"]["row_count"], bundle.models["M2"].n_fit)
        for name in ("M3", "P3"):
            self.assertEqual(result["models"][name]["row_count"],
                             bundle.models[name].metadata["n_fit"])
        self.assertEqual(result["models"]["M3"]["row_count"],
                         result["models"]["P3"]["row_count"])

    def test_serialized_bundle_is_supported_without_mutation(self):
        ledger, evidence = fixture(n=20)
        payload = fit_directional(ledger, evidence, 10000.0).to_dict()
        before = copy.deepcopy(payload)
        result = profile_bundle(payload, ledger, evidence)
        self.assertEqual(payload, before)
        self.assertEqual(result["models"]["R0"]["row_count"], len(evidence))

    def test_profile_rejects_a_frozen_fit_with_materially_worse_optimum(self):
        ledger, evidence = fixture(n=20)
        payload = fit_directional(ledger, evidence, 10000.0).to_dict()
        payload["models"]["M2"]["intercept"] += 0.5
        payload["models"]["M3"]["intercept"] += 0.5
        payload["models"]["P3"]["intercept"] += 0.5
        with self.assertRaisesRegex(ValueError, "materially better than frozen fit"):
            profile_bundle(payload, ledger, evidence)


if __name__ == "__main__":
    unittest.main()
