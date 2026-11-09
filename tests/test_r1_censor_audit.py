from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts"), str(ROOT / "tests")]
from dnmem import outcome_evidence_v4, prefix_features, prefix_reference
from r1_censor_audit import candidate, reference_v4, relation
from test_prefix_features import outbursts


def episode(lo, hi, *, peak=24.0, end=None):
    return {"confirmed_event": True, "peak_t": peak, "onset_lo": lo, "onset_hi": hi,
            "onset_t": (lo + hi) / 2, "onset_method": "injected_working_set",
            "end_lo": end, "end_hi": end, "end_t": end}


def injected(module, lo, hi, stopping, *, end=None, issue=10.0):
    times = [float(t) for t in range(0, 41, 5)]
    ledger = [{"emission_index": 0, "emitted_at": 9.0, "issue_time": issue,
               "end_lo": 6.0, "end_hi": 12.0}]
    stop = 40.0
    if stopping == "coverage":
        times.remove(25.0)
    elif stopping == "superseded":
        ledger.append({"emission_index": 1, "emitted_at": 19.0, "issue_time": 20.0,
                       "repeat_of_previous": True})
    elif stopping == "record_end":
        stop = 20.0
        times = [time for time in times if time <= stop]
    else:
        raise ValueError(stopping)
    rows = [{"JD": time} for time in times]
    episodes = [episode(lo, hi, end=end)]
    extracted_visits = [{"t": time} for time in times]
    if module is reference_v4:
        with patch.dict(reference_v4.__globals__, {"x4_episodes": lambda *args: episodes,
                                                  "visits": lambda *args: extracted_visits}):
            return reference_v4(rows, ledger, stop=stop)[0]
    with patch.object(module, "x4_episodes", return_value=episodes), \
            patch.object(module, "visits", return_value=extracted_visits):
        return module.outcome_evidence(rows, ledger, stop=stop)[0]


class R1WorkingSetCorrectionTests(unittest.TestCase):
    def test_straddle_backs_off_for_each_stopping_cause(self):
        for stopping in ("coverage", "superseded", "record_end"):
            with self.subTest(stopping=stopping):
                production = injected(outcome_evidence_v4, 18.0, 22.0, stopping)
                self.assertEqual(production, injected(reference_v4, 18.0, 22.0, stopping))
                self.assertEqual((production["kind"], production["reason"], production["censor_at"]),
                                 ("right_censored", stopping, 18.0))
                self.assertEqual((production["stopping_cutoff"], production["stopping_reason"]), (20.0, stopping))
                self.assertTrue(production["censor_backoff"])
                self.assertEqual(production["censor_backoff_days"], 2.0)
                self.assertIsNone(production["onset_lo"])

    def test_closed_upper_and_equal_lower_boundaries(self):
        for stopping in ("coverage", "superseded", "record_end"):
            for lo, hi, kind, censor in ((16.0, 18.0, "interval", None),
                                         (18.0, 20.0, "interval", None),
                                         (20.0, 22.0, "right_censored", 20.0),
                                         (22.0, 24.0, "right_censored", 20.0)):
                with self.subTest(stopping=stopping, lo=lo, hi=hi):
                    actual = injected(outcome_evidence_v4, lo, hi, stopping)
                    self.assertEqual(actual, injected(reference_v4, lo, hi, stopping))
                    self.assertEqual((actual["kind"], actual["censor_at"]), (kind, censor))
                    self.assertFalse(actual["censor_backoff"])

    def test_issue_straddle_and_overtaken_candidates_remain_excluded(self):
        for lo, hi, reason in ((9.0, 11.0, "ambiguous_survival"),
                               (10.0, 11.0, "ambiguous_survival"),
                               (9.1, 10.0, "overtaken")):
            for route in (outcome_evidence_v4, reference_v4):
                with self.subTest(lo=lo, hi=hi, route=str(route)):
                    actual = injected(route, lo, hi, "superseded")
                    self.assertEqual((actual["kind"], actual["reason"]), ("excluded", reason))
                    self.assertIsNone(actual["censor_at"])

    def test_frozen_builders_retain_the_counterexample(self):
        for module in (prefix_features, prefix_reference):
            actual = injected(module, 18.0, 22.0, "superseded")
            self.assertEqual((actual["kind"], actual["censor_at"]), ("right_censored", 20.0))
        self.assertEqual(injected(outcome_evidence_v4, 18.0, 22.0, "superseded")["censor_at"], 18.0)

    def test_end_fit_does_not_supply_an_onset_survival_bound(self):
        for route in (outcome_evidence_v4, reference_v4):
            no_end = injected(route, 18.0, 22.0, "superseded", end=None)
            late_end = injected(route, 18.0, 22.0, "superseded", end=39.0)
            self.assertEqual(no_end, late_end)
            self.assertEqual(no_end["censor_at"], 18.0)

    def test_record_end_filters_future_rows_before_extraction(self):
        seen = {}
        def extract(rows, threshold):
            seen["times"] = [float(row["JD"]) for row in rows]
            return []
        ledger = [{"emission_index": 0, "emitted_at": 9.0, "issue_time": 10.0}]
        with patch.object(outcome_evidence_v4, "x4_episodes", side_effect=extract), \
                patch.object(outcome_evidence_v4, "visits", return_value=[{"t": 5.0}, {"t": 10.0}, {"t": 15.0}, {"t": 20.0}]):
            actual = outcome_evidence_v4.outcome_evidence([{"JD": t} for t in (5.0, 10.0, 15.0, 20.0, 21.0)],
                                                          ledger, stop=20.0)[0]
        self.assertEqual(seen["times"], [5.0, 10.0, 15.0, 20.0])
        self.assertEqual((actual["reason"], actual["censor_at"]), ("record_end", 20.0))

    def test_repeat_emission_retires_first_forecast_without_reusing_onset(self):
        rows = outbursts()
        from test_extract import obs
        tail = [obs(n + .6 + .1 * k, 8.8, who) for n in (114, 115) for k, who in enumerate("ab")]
        rows = [row for row in rows if not 114 <= float(row["JD"]) < 116] + tail
        ledger = prefix_features.forecast_ledger(rows)
        self.assertTrue(ledger[1]["repeat_of_previous"])
        actual = outcome_evidence_v4.outcome_evidence(rows, ledger, stop=200.0)
        self.assertEqual(actual, reference_v4(rows, ledger, stop=200.0))
        self.assertEqual((actual[0]["kind"], actual[0]["reason"]), ("right_censored", "superseded"))
        self.assertEqual(actual[0]["censor_at"], ledger[1]["issue_time"])
        self.assertEqual(actual[1]["kind"], "interval")
        self.assertEqual(len({e["onset_index"] for e in actual if e["kind"] == "interval"}), 1)

    def test_unemitted_final_episode_is_the_candidate(self):
        rows = outbursts(events=((100.0, 112.0), (150.0, 190.0)), nights=range(60, 160))
        ledger = prefix_features.forecast_ledger(rows)
        self.assertEqual(len(ledger), 1)
        episodes = sorted((e for e in prefix_features.x4_episodes(rows) if e["confirmed_event"]), key=lambda e: e["peak_t"])
        index, chosen = candidate(episodes, ledger[0]["emitted_at"])
        self.assertEqual(index, 1)
        self.assertEqual(relation(chosen, 160.0), "before_or_at_cutoff")
        self.assertIsNone(chosen["end_hi"])
        result = outcome_evidence_v4.outcome_evidence(rows, ledger, stop=160.0)
        self.assertEqual(result, reference_v4(rows, ledger, stop=160.0))
        self.assertEqual(result[0]["kind"], "interval")


if __name__ == "__main__":
    unittest.main()
