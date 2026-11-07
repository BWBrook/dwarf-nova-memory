from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.brackets import bounds, candidate_runs, coverage_gaps, row_class


def obs(jd, mag, who, limit="0", val="V"):
    return {"JD": str(jd), "mag": str(mag), "fainterThan": limit, "val": val,
            "obsID": f"x{jd}{who}", "by": who, "obsName": who}


class BracketTests(unittest.TestCase):
    def test_limit_direction(self):
        self.assertEqual(row_class(obs(1, 11.0, "a", limit="1")), "F")
        self.assertEqual(row_class(obs(1, 9.0, "a", limit="1")), "N")
        self.assertEqual(row_class(obs(1, 10.0, "a")), "B")

    def test_bright_limit_neither_ends_run_nor_brackets_onset(self):
        rows = [obs(0.0, 12.0, "a"), obs(1.0, 9.5, "a", limit="1"), obs(2.0, 9.0, "a"),
                obs(3.0, 9.4, "b"), obs(4.0, 9.0, "c", limit="1"), obs(5.0, 9.2, "a"),
                obs(6.0, 11.8, "b"), obs(6.5, 11.9, "c")]
        (run,) = candidate_runs(rows)
        self.assertEqual(float(run["onset_earliest"]["JD"]), 0.0)
        self.assertEqual(float(run["end_earliest"]["JD"]), 5.0)
        self.assertEqual(float(run["onset_detected"]["JD"]), 3.0)
        self.assertEqual(float(run["end_confirmed"]["JD"]), 6.5)
        self.assertEqual(bounds(run)["duration_max"], 6.0)

    def test_discrepant_rows_and_single_faint_observer(self):
        rows = [obs(0.0, 12.0, "a"), obs(1.0, 9.0, "a"), obs(2.0, 12.0, "b", val="T"),
                obs(3.0, 9.1, "a"), obs(4.0, 11.9, "a"), obs(5.0, 12.0, "a"),
                obs(11.0, 12.1, "a")]
        (run,) = candidate_runs(rows)
        self.assertEqual(run["n_bright_observers"], 1)
        self.assertIsNone(run["onset_detected"])
        self.assertIsNone(run["end_confirmed"])
        self.assertEqual(coverage_gaps(rows), [(5.0, 11.0)])


if __name__ == "__main__":
    unittest.main()
