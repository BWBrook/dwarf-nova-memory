from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.extract import x1_vote_episodes, x2_median_hysteresis
from dnmem.injection_score import score_run
from dnmem.injection_truth import generate_events, magnitudes_at, truth_catalogue


class InjectionPipelineTests(unittest.TestCase):
    def test_dense_noiseless_control_recovers_every_interior_crossing(self):
        start, stop = 2451544.5, 2452544.5
        history = generate_events([7, 9, 13, 17], [20, 30, 40, 50], start, stop, 101)
        times = [start + i / 4 for i in range(4001)]
        rows = [{"JD": str(t), "mag": str(m), "band": "Vis.", "val": "V", "fainterThan": "0",
                 "obsName": observer, "by": observer, "obsID": f"{i}-{observer}"}
                for i, (t, m) in enumerate(zip(times, magnitudes_at(history, times))) for observer in ("a", "b")]
        for extractor in (x1_vote_episodes, x2_median_hysteresis):
            result = score_run(rows, extractor(rows), truth_catalogue(history, 10), start, stop)[0]
            self.assertGreater(result["reference_event_count"], 15)
            self.assertEqual(result["completeness_count"], result["reference_event_count"])
            self.assertEqual(result["onset_effective_coverage"], 1)
            self.assertEqual(result["end_effective_coverage"], 1)
            self.assertEqual(result["false_confirmed_count"], 0)


if __name__ == "__main__":
    unittest.main()
