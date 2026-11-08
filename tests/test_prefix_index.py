import random
import unittest
from unittest.mock import patch

from dnmem import prefix_features as candidate


class PrefixIndexTests(unittest.TestCase):
    def test_coverage_index_matches_whole_gap_reference(self):
        rng = random.Random(88314)
        for _ in range(100):
            times = sorted(rng.choices(range(-20, 100), k=rng.randrange(0, 60)))
            stop = 100.0
            indexed = candidate._coverage_index(times, stop)
            for issue in [*range(-25, 100), 99.99]:
                self.assertEqual(indexed(issue), candidate._coverage_loss(times, issue, stop))

    def test_prefix_slices_preserve_edges_ties_and_repeat_context(self):
        rows = [{"JD": str(t), "source": i} for i, t in enumerate([0., 11., 10., 10., 6., 4., 12.])]
        emissions = [{"emitted_at": t, "emission_index": i} for i, t in enumerate([10., 11., 12.])]

        def features(data, emission, threshold, latency, lookback):
            window = sorted(candidate.prefix_rows(data, emission["emitted_at"], lookback),
                            key=lambda r: float(r["JD"]))
            return {"issue_time": emission["emitted_at"]+latency, "onset_t": 8., "window": window}

        expected = []
        for e in emissions:
            record = features(rows, e, 10., 0., 6.)
            record["repeat_of_previous"] = bool(expected)
            expected.append(record)
        with patch.object(candidate, "causal_confirmations", return_value=emissions), \
                patch.object(candidate, "forecast_features", side_effect=features):
            actual = candidate.forecast_ledger(rows, lookback=6., start=11.)
        self.assertEqual(actual, expected[1:])
