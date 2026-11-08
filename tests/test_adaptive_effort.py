import unittest

from src.dnmem.adaptive_effort import thin_adaptive


def row(jd, mag, *, limit="0", band="Vis.", val="V", observer="SIM"):
    return {
        "JD": str(jd),
        "mag": str(mag),
        "fainterThan": limit,
        "band": band,
        "val": val,
        "by": observer,
        "obsName": observer,
        "obsID": f"{jd}-{observer}",
    }


class AdaptiveEffortTests(unittest.TestCase):
    def test_deterministic_and_stable_sorting(self):
        rows = [row(102.2, 12), row(100.4, 12), row(102.1, 12), row(101.4, 12)]
        kept_a, metadata_a = thin_adaptive(rows, seed=7)
        kept_b, metadata_b = thin_adaptive(rows, seed=7)
        self.assertEqual(kept_a, kept_b)
        self.assertEqual(metadata_a, metadata_b)
        self.assertEqual([float(item["JD"]) for item in kept_a], sorted(float(item["JD"]) for item in kept_a))

    def test_current_day_values_do_not_change_its_draw(self):
        base = [row(100.2, 12), row(101.2, 12), row(102.2, 12)]
        poisoned = [row(100.2, 12), row(101.2, 8), row(102.2, 12)]
        _, base_metadata = thin_adaptive(base, seed=3, short_keep=0.0)
        _, poisoned_metadata = thin_adaptive(poisoned, seed=3, short_keep=0.0)
        # The day-level decision is made before its magnitude is available.
        self.assertEqual(base_metadata["days_kept"], poisoned_metadata["days_kept"])

    def test_all_rows_on_a_kept_day_are_retained(self):
        rows = [row(100.1, 12, observer="A"), row(100.9, 8, observer="B")]
        kept, metadata = thin_adaptive(rows, seed=1)
        self.assertEqual(kept, rows)
        self.assertEqual(metadata["rows_kept"], 2)

    def test_short_and_long_closure_control_next_day(self):
        rows = [
            row(100.1, 9),
            row(101.1, 9),
            row(102.1, 11),
            row(103.1, 11),
            row(104.1, 12),
        ]
        kept, metadata = thin_adaptive(rows, seed=4, short_keep=0.0, long_keep=1.0)
        self.assertEqual(metadata["controller_updates"], [{
            "atJD": 103.0,
            "proxy_duration": 1.0,
            "next_keep": 0.0,
        }])
        self.assertNotIn(rows[-1], kept)

        long_rows = [row(item["JD"], item["mag"]) for item in rows]
        _, long_metadata = thin_adaptive(
            long_rows, seed=4, short_keep=0.0, long_keep=1.0, split_days=1.0
        )
        self.assertEqual(long_metadata["controller_updates"][0]["next_keep"], 1.0)
        self.assertEqual(long_metadata["rows_kept"], len(long_rows))

    def test_future_rows_do_not_change_earlier_controller_prefix(self):
        prefix = [row(100.1, 9), row(101.1, 11), row(102.1, 11), row(103.1, 12)]
        extended = prefix + [row(1000.1, 8), row(1001.1, 11), row(1002.1, 11)]
        kept_prefix, metadata_prefix = thin_adaptive(prefix, seed=9, short_keep=0.0)
        kept_extended, metadata_extended = thin_adaptive(extended, seed=9, short_keep=0.0)
        self.assertEqual(kept_prefix, [r for r in kept_extended if float(r["JD"]) < 104])
        self.assertEqual(metadata_prefix["controller_updates"], metadata_extended["controller_updates"][:1])

    def test_limit_evidence_and_parameter_constraints(self):
        rows = [row(100.1, 9), row(101.1, 11, limit="1"), row(102.1, 11, limit="true")]
        _, metadata = thin_adaptive(rows, seed=1)
        self.assertEqual(len(metadata["controller_updates"]), 1)
        with self.assertRaises(ValueError):
            thin_adaptive(rows, seed=1, short_keep=1.1)
        with self.assertRaises(ValueError):
            thin_adaptive(rows, seed=1, reset_days=0)

    def test_reset_returns_to_high_cadence_one(self):
        rows = [
            row(100.1, 9), row(101.1, 11), row(102.1, 11),
            row(103.1, 12), row(163.1, 12),
        ]
        kept, metadata = thin_adaptive(
            rows, seed=2, short_keep=0.0, long_keep=0.2, reset_days=60
        )
        self.assertEqual(metadata["controller_updates"][0]["next_keep"], 0.0)
        self.assertEqual(metadata["final_settings"]["final_keep"], 1.0)
        self.assertEqual(kept[-1], rows[-1])


if __name__ == "__main__":
    unittest.main()
