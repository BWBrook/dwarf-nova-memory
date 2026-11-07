import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dnmem.x4_benchmark import gross_errors


class GrossErrorTests(unittest.TestCase):
    def rows(self, days=1000):
        return [{"JD": str(i + .2), "mag": "11.8", "by": "observer-a",
                 "obsName": "", "fainterThan": "0", "obsID": str(i),
                 "band": "Vis.", "val": "V"} for i in range(days)]

    def test_quiet_contamination_quota_and_inputs_unchanged(self):
        rows = self.rows()
        truth = [{"onset": 100., "end": 110.}, {"onset": 111., "end": 120.}]
        modified, record = gross_errors(rows, truth, 719, fraction=.1)
        self.assertEqual(record["eligible_quiet_visits"], 974)
        self.assertIn(record["contaminated_visits"], (97, 98))
        for original, changed in zip(rows, modified):
            self.assertEqual(original["mag"], "11.8")
            if 97 <= float(changed["JD"]) <= 123:
                self.assertEqual(changed["mag"], "11.8")
        self.assertEqual((modified, record), gross_errors(rows, truth, 719, fraction=.1))
        self.assertTrue(all(1 <= length <= 3 for length in record["cluster_lengths"]))

    def test_repeat_estimates_count_as_one_observer_night(self):
        rows = self.rows(100)
        rows += [{**r, "JD": str(float(r["JD"]) + .1), "obsID": "repeat" + r["obsID"]} for r in rows]
        modified, record = gross_errors(rows, [], 414, fraction=.1)
        self.assertEqual(record["eligible_quiet_visits"], 100)
        self.assertEqual(record["contaminated_visits"], 10)
        self.assertEqual(record["contaminated_rows"], 20)
        for i in range(100):
            self.assertEqual(modified[i]["mag"], modified[i + 100]["mag"])


if __name__ == "__main__":
    unittest.main()
