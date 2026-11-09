import importlib.util
from pathlib import Path
import unittest

import numpy as np

spec = importlib.util.spec_from_file_location("r2d_precision", Path(__file__).resolve().parents[1]/"scripts/r2d_precision.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PrecisionTests(unittest.TestCase):
    def test_sign_flip_granularity_and_zero_contributions(self):
        for stars in (3, 4, 5, 8):
            vector = {"star": np.arange(stars), "score": np.ones(stars)}
            result = module.score_sign_flip(vector)
            self.assertEqual(result["p"], 2.**(-stars))
            self.assertEqual(result["reject_one_sided"], stars >= 5)
            vector["score"][:] = 0.
            self.assertEqual(module.score_sign_flip(vector)["p"], 1.)

    def test_exact_mc_interval_retains_boundary_uncertainty(self):
        self.assertEqual(module.exact_interval(0, 40)[0], 0.)
        self.assertGreater(module.exact_interval(0, 40)[1], .05)
        self.assertEqual(module.exact_interval(40, 40)[1], 1.)
        self.assertIsNone(module.exact_interval(0, 0))


if __name__ == "__main__":
    unittest.main()
