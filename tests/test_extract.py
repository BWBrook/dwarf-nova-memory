from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.extract import visits, x1_vote_episodes, x2_median_hysteresis


def obs(jd, mag, who, limit="0", val="V"):
    return {"JD": str(jd), "mag": str(mag), "fainterThan": limit, "val": val, "band": "Vis.",
            "obsID": f"{jd}-{who}-{mag}", "by": who, "obsName": who}


def outburst():
    rows = [obs(100.6 + d, 12.0, "a") for d in range(5)]
    rows += [obs(105.30, 10.0, "q"), obs(105.32, 10.1, "q"), obs(105.35, 10.0, "q"), obs(105.5, 10.4, "a"),
             obs(105.6, 9.1, "b"), obs(105.7, 8.9, "c")]
    rows += [obs(106.6 + d, 8.5 + 0.2 * d, w) for d in range(5) for w in ("a", "b")]
    rows += [obs(111.4, 10.5, "a"), obs(111.4, 9.2, "b"), obs(111.5, 9.9, "c"), obs(111.5, 10.5, "d"),
             obs(111.5, 9.8, "e"), obs(111.6, 10.2, "f"), obs(111.6, 9.9, "g"), obs(111.6, 10.5, "h"),
             obs(112.2, 10.4, "a"), obs(112.5, 10.5, "b"), obs(112.6, 9.0, "z", limit="1")]
    rows += [obs(113.6 + d, 11.8, w) for d in range(4) for w in ("a", "b")]
    return rows


class ExtractorTests(unittest.TestCase):
    def test_one_vote_per_observer_visit_and_uninformative_limit_dropped(self):
        votes = visits(outburst())
        q = [v for v in votes if v["observer"] == "q"]
        self.assertEqual(len(q), 1)
        self.assertEqual((q[0]["cls"], q[0]["value"]), ("B", 10.0))
        self.assertFalse(any(v["observer"] == "z" for v in votes))

    def test_tied_epochs_sit_inside_nonzero_intervals(self):
        (episode,) = x1_vote_episodes(outburst())
        self.assertEqual(episode["onset_lo"], 104.6)
        self.assertAlmostEqual(episode["onset_hi"], 105.6)
        self.assertEqual(episode["end_lo"], 110.6)
        self.assertEqual(episode["end_hi"], 112.2)
        self.assertLess(episode["end_lo"], episode["end_hi"])
        self.assertTrue(episode["confirmed_event"])

    def test_lone_faint_night_in_decline_tail_does_not_split(self):
        rows = [obs(200.6, 12.0, "a"), obs(201.6, 8.5, "a"), obs(201.6, 8.6, "b"), obs(202.6, 9.6, "a"),
                obs(202.6, 9.7, "b"), obs(203.6, 10.1, "a"), obs(204.6, 9.9, "a"), obs(204.6, 9.8, "b"),
                obs(205.6, 11.5, "a"), obs(205.6, 11.6, "b"), obs(220.6, 8.6, "a"), obs(220.6, 8.7, "b"),
                obs(219.6, 12.0, "a"), obs(222.6, 11.8, "a"), obs(222.6, 11.9, "b")]
        episodes = x1_vote_episodes(rows)
        self.assertEqual(len(episodes), 2)
        self.assertEqual((episodes[0]["end_lo"], episodes[0]["end_hi"]), (202.6, 205.6))

    def test_hysteresis_holds_through_threshold_scatter(self):
        episodes = x2_median_hysteresis(outburst())
        self.assertEqual(len(episodes), 1)
        self.assertLess(episodes[0]["onset_lo"], episodes[0]["onset_hi"])


if __name__ == "__main__":
    unittest.main()
