from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
from dnmem.extract_x4 import causal_confirmations, x4_episodes
from dnmem.prefix_features import forecast_ledger, outcome_evidence
from test_extract import obs


def outbursts(events=((100.0, 112.0), (150.0, 160.0)), nights=range(60, 200), skip=(), observers="abc",
              extra=()):
    def mag(t):
        for onset, end in events:
            if onset - 2.2 <= t <= end + 6.6:
                if t < onset + 1.5:
                    return max(8.5, 10 - (t - onset))
                if t < end - 4.5:
                    return 8.5
                return min(12.2, 10 + 0.33 * (t - end))
        return 12.2
    rows = [obs(round(n + 0.6 + 0.1 * k, 2), round(mag(n + 0.6 + 0.1 * k), 1), who)
            for n in nights if n not in skip for k, who in enumerate(observers)]
    return rows + list(extra)


class PrefixCausalityTests(unittest.TestCase):
    def test_no_later_row_can_change_a_forecast(self):
        rows = outbursts()
        first = forecast_ledger(rows)[0]
        cutoff = first["emitted_at"]
        poisoned = [r if float(r["JD"]) <= cutoff else {**r, "mag": str(float(r["mag"]) - 1.3)} for r in rows]
        poisoned += [obs(cutoff + 0.01, 8.0, "x"), obs(cutoff + 0.02, 8.1, "y"), obs(cutoff + 1.0, 8.0, "x")]
        self.assertEqual(forecast_ledger(poisoned)[0], first)
        self.assertNotEqual(x4_episodes(poisoned)[0]["end_t"], x4_episodes(rows)[0]["end_t"])

    def test_prefix_end_fit_excludes_estimates_after_the_emission(self):
        rows = outbursts()
        first = forecast_ledger(rows)[0]
        retro = x4_episodes(rows)[0]
        self.assertTrue(first["episode_found"])
        self.assertLess(first["n_end_fit"], retro["n_end_fit"])
        self.assertAlmostEqual(first["end_t"], 112.0, delta=1.0)
        self.assertAlmostEqual(first["duration"], 12.0, delta=1.5)
        self.assertGreater(first["age_at_issue"], 0.0)

    def test_latency_delays_issue_but_not_the_information_set(self):
        rows = outbursts()
        zero, late = forecast_ledger(rows)[0], forecast_ledger(rows, latency=2.0)[0]
        self.assertEqual(late["issue_time"], zero["issue_time"] + 2.0)
        self.assertEqual(late["duration"], zero["duration"])
        self.assertAlmostEqual(late["age_at_issue"], zero["age_at_issue"] + 2.0)

    def test_previous_gap_comes_from_the_same_prefix(self):
        rows = outbursts(events=((80.0, 90.0), (120.0, 131.0), (170.0, 180.0)), nights=range(20, 220))
        ledger = forecast_ledger(rows)
        self.assertIsNone(ledger[0]["previous_gap"])
        self.assertAlmostEqual(ledger[1]["previous_gap"], 30.0, delta=1.5)
        self.assertTrue(ledger[1]["previous_gap_covered"])


class OutcomeEvidenceTests(unittest.TestCase):
    def test_outcome_is_the_next_confirmed_onset(self):
        rows = outbursts()
        ledger = forecast_ledger(rows)
        first, second = outcome_evidence(rows, ledger, stop=200.0)
        self.assertEqual(first["kind"], "interval")
        self.assertLessEqual(first["onset_lo"], 150.0)
        self.assertGreaterEqual(first["onset_hi"], 150.0)
        self.assertEqual((second["kind"], second["reason"]), ("right_censored", "record_end"))

    def test_monitoring_hole_censors_at_its_start(self):
        rows = outbursts(skip=range(125, 140))
        (first, _) = outcome_evidence(rows, forecast_ledger(rows), stop=200.0)
        self.assertEqual((first["kind"], first["reason"]), ("right_censored", "coverage"))
        self.assertAlmostEqual(first["censor_at"], 124.8, delta=0.2)

    def test_rebrightening_supersedes_the_live_forecast_without_truth(self):
        tail = [obs(n + 0.6 + 0.1 * k, 8.8, who) for n in (114, 115) for k, who in enumerate("ab")]
        rows = [r for r in outbursts() if not 114 <= float(r["JD"]) < 116] + tail
        ledger = forecast_ledger(rows)
        self.assertEqual(len(causal_confirmations(rows)), 3)
        self.assertEqual(len([e for e in x4_episodes(rows) if e["confirmed_event"]]), 2)
        first, second, third = outcome_evidence(rows, ledger, stop=200.0)
        self.assertEqual((first["kind"], first["reason"]), ("right_censored", "superseded"))
        self.assertEqual(first["censor_at"], ledger[1]["issue_time"])
        self.assertEqual(second["kind"], "interval")
        self.assertTrue(ledger[1]["episode_found"])
        self.assertTrue(ledger[1]["repeat_of_previous"])
        self.assertFalse(ledger[2]["repeat_of_previous"])
        self.assertGreater(ledger[1]["age_at_issue"], ledger[0]["age_at_issue"])
        self.assertEqual(third["kind"], "right_censored")

    def test_emission_without_a_prefix_episode_is_kept(self):
        night = [obs(130.61, 8.8, "x"), obs(130.63, 8.9, "y")]
        rows = outbursts(events=((100.0, 112.0),), extra=night)
        ledger = forecast_ledger(rows)
        lone = next(f for f in ledger if 130 < f["emitted_at"] < 131)
        self.assertFalse(lone["episode_found"])
        self.assertIsNone(lone["duration"])
        self.assertEqual(len(outcome_evidence(rows, ledger)), len(ledger))


if __name__ == "__main__":
    unittest.main()
