import math
import unittest

from dnmem.oc_statistics import binomial_summary, cluster_interval, coverage_screen, reference_calibration


class OperatingStatisticTests(unittest.TestCase):
    def test_routing_zeros_remain_in_the_mean_and_zero_identity_is_not_confirmed(self):
        rows = [{"issue_time": i*365.25, "gain": value} for i, value in enumerate([0., .1, 0., .1]*6)]
        interval = cluster_interval(rows, "gain", 0)
        self.assertAlmostEqual(interval["estimate"], .05)
        zero = cluster_interval([{**row, "gain": 0.} for row in rows], "gain", 0)
        self.assertFalse(zero["confirmed"])
        self.assertEqual(zero["lower"], 0)
        self.assertTrue(reference_calibration(zero, [], True)["joint_mc_covers_zero"])

    def test_zero_rejections_have_nonzero_exact_uncertainty(self):
        summary = binomial_summary(0, 40)
        self.assertAlmostEqual(summary["one_sided_upper95"], 1-.05**(1/40))
        self.assertGreater(summary["one_sided_upper95"], .05)

    def test_reference_uncertainty_is_propagated(self):
        interval = {"estimate": .006, "se": .001, "blocks": 10, "lower": .005, "upper": .007}
        reference = reference_calibration(interval, [-.01, 0., .01, -.01, 0., .01])
        self.assertFalse(reference["naive_reference_contained"])
        self.assertTrue(reference["joint_mc_covers_zero"])
        self.assertGreater(reference["reference_se"], 0)

    def test_boundary_trials_cannot_mask_interior_undercoverage(self):
        rows = [{"interior": False, "joint_mc_covers_zero": True} for _ in range(20)]
        rows += [{"interior": True, "joint_mc_covers_zero": i < 14} for i in range(20)]
        result = coverage_screen(rows)
        self.assertEqual(result["overall"]["successes"], 34)
        self.assertFalse(result["pass"])
