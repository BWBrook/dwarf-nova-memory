import csv
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ANNOTATION = ROOT / "data/annotations/a04_ss_cyg_1956_1958_claude_v1.csv"


class AnnotationIntegrityTests(unittest.TestCase):
    def test_brackets_ordered_within_and_between_events(self):
        with open(ANNOTATION, newline="") as handle:
            rows = list(csv.DictReader(handle))
        previous_end = None
        for row in rows:
            v = {k: float(row[k]) for k in ("onset_earliest_jd", "onset_latest_jd", "onset_envelope_end_jd",
                                            "end_envelope_start_jd", "end_earliest_jd", "end_latest_jd")}
            with self.subTest(event=row["event_id"]):
                self.assertLess(v["onset_earliest_jd"], v["onset_latest_jd"])
                self.assertLessEqual(v["onset_latest_jd"], v["onset_envelope_end_jd"])
                self.assertLessEqual(v["onset_envelope_end_jd"], v["end_envelope_start_jd"])
                self.assertLessEqual(v["end_envelope_start_jd"], v["end_earliest_jd"])
                self.assertLessEqual(v["end_earliest_jd"], v["end_latest_jd"])
                self.assertLess(v["end_latest_jd"], 2436934.5)
                if previous_end is not None:
                    self.assertLessEqual(previous_end, v["onset_earliest_jd"])
                previous_end = v["end_latest_jd"]


if __name__ == "__main__":
    unittest.main()
