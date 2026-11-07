from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dnmem.x3_observation import labelled_days, state_compatible_schedule


class History:
    def evaluate(self, times):
        return [9 if 100 <= t < 102 else 12 for t in times]


def obs(t, mag, observer="a", limit="0"):
    return {"JD": str(t), "mag": str(mag), "by": observer, "obsName": observer,
            "band": "Vis.", "val": "V", "fainterThan": limit, "obsID": str(t)+observer}


class StateScheduleTests(unittest.TestCase):
    def test_preserves_empty_days_and_shifts_donor_fractional_time(self):
        days = labelled_days([obs(100.7, 12), obs(102.8, 9), obs(103.6, 12)])
        schedule, counts = state_compatible_schedule(days, History(), 100, 105)
        self.assertEqual({int(float(r["JD"])) for r in schedule}, {100, 102, 103})
        self.assertAlmostEqual(schedule[0]["JD"], 100.8)
        self.assertEqual(counts["borrowed_days"], 2)
        self.assertEqual(counts["empty_days_preserved"], 2)

    def test_uninformative_limit_is_unknown_and_no_donor_falls_back_explicitly(self):
        days = labelled_days([obs(100.7, 9.5, limit="1")])
        self.assertEqual(days[0]["state"], "unknown")
        schedule, counts = state_compatible_schedule(days, History(), 100, 102)
        self.assertEqual(len(schedule), 1)
        self.assertEqual(counts["no_match_fraction"], 1)


if __name__ == "__main__":
    unittest.main()
