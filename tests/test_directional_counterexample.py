import importlib.util
from pathlib import Path
import unittest


class DirectionalCounterexampleTests(unittest.TestCase):
    def test_positive_mark_information_can_be_generated_by_end_error(self):
        path = Path(__file__).resolve().parents[1]/"scripts/a10d_design_calculations.py"
        spec = importlib.util.spec_from_file_location("design_calculation", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        exact = module.counterexample()
        offset = module.offset_counterexample(exact["states"])
        self.assertGreater(exact["mean_remaining_wait_at_ahat_2"]["Dhat_16"],
                           exact["mean_remaining_wait_at_ahat_2"]["Dhat_10"])
        self.assertGreater(offset["beta_standardized_log_duration"], .1)
        self.assertGreater(offset["gain_nats_per_retained_anchor"], .01)
