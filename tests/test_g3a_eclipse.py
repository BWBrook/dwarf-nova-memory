import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dnmem import g3a_eclipse as eclipse


def row(t, magnitude, who="a", limit=False):
    return {"JD": str(t), "mag": str(magnitude), "by": who,
            "obsID": f"{who}:{t}", "fainterThan": "1" if limit else "0",
            "band": "Vis.", "val": "V", "uncert": ""}


class EclipseGuardTests(unittest.TestCase):
    def test_full_night_reductions_wait_for_fixed_close_and_preserve_raw(self):
        source = [row(100.1, 12), row(100.8, 8), row(100.4, 15, "b", True),
                  row(100.7, 16, "b", True)]
        original = copy.deepcopy(source)
        median = eclipse.reduce_observer_nights(source, "median")
        bright = eclipse.reduce_observer_nights(list(reversed(source)), "brightest")
        self.assertEqual(source, original)
        self.assertEqual([float(r["JD"]) for r in median], [101., 101.])
        self.assertEqual([float(r["mag"]) for r in median], [10., 16.])
        self.assertEqual([float(r["mag"]) for r in bright], [8., 16.])
        self.assertEqual(median[1]["fainterThan"], "1")
        self.assertEqual(median[0]["g3a_source_last_jd"], "100.8")

    def test_postcutoff_rows_rejected_and_unclosed_last_night_not_borrowed(self):
        with self.assertRaisesRegex(ValueError, "pre-1990"):
            eclipse.reduce_observer_nights([row(eclipse.CUTOFF, 12)], "median")
        self.assertEqual(eclipse.reduce_observer_nights([row(eclipse.CUTOFF - .1, 12)], "median"), [])

    def test_end_confirmation_needs_two_nights_and_observers_and_is_delayed(self):
        bright = [row(101, 8, "a"), row(101, 8, "b")]
        first_faint = [row(110, 12, "a"), row(110, 12, "b")]
        self.assertEqual(eclipse.two_night_confirmations(bright + first_faint), [])
        result = eclipse.two_night_confirmations(bright + first_faint + [row(111, 12, "a")])
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0]["emitted_at"], 111.15)
        self.assertAlmostEqual(result[0]["faint_first_at"], 110.15)
        self.assertEqual(result[0]["faint_night_count"], 2)

    def test_bright_return_cancels_isolated_eclipse_faintness(self):
        rows = [row(101, 8, "a"), row(101, 8, "b"), row(110, 12, "a"), row(110, 12, "b"),
                row(110.5, 8, "a"), row(111, 12, "a"), row(111, 12, "b")]
        self.assertEqual(eclipse.two_night_confirmations(rows), [])
        emitted = eclipse.two_night_confirmations(rows + [row(112, 12, "a")])
        self.assertAlmostEqual(emitted[0]["emitted_at"], 112.15)
        prefix = [r for r in rows if float(r["JD"]) < 111]
        self.assertEqual(eclipse.two_night_confirmations(prefix), [])

    def test_synthetic_template_ignores_real_magnitudes_and_has_declared_truth(self):
        rows = [row(100 + i, 13 + i % 3) for i in range(200)]
        changed = [{**r, "mag": "99", "fainterThan": "1"} for r in reversed(rows)]
        a = eclipse._synthetic_template(rows, 10, "U Gem")
        b = eclipse._synthetic_template(changed, 10, "U Gem")
        np.testing.assert_array_equal(a[1], b[1])
        np.testing.assert_array_equal(a[2], b[2])
        np.testing.assert_array_equal(a[3], b[3])
        self.assertEqual(a[4], b[4])
        self.assertEqual([r["span"] for r in a[4]][:2], [9., 15.])

    def test_sparse_cadence_does_not_pass_an_untested_eclipse_envelope(self):
        result = eclipse.eclipse_sensitivity([row(100, 12), row(150, 12)], "U Gem", 10)
        self.assertFalse(result["passed"])
        self.assertEqual(result["status"], "inconclusive")
        self.assertEqual(result["cases"], 0)

    def test_known_dense_invented_cadence_recovers_trapezoids_without_early_alerts(self):
        rows = [row(2400000.1 + day + offset, 14, who)
                for day in range(1500) for who, offset in (("a", 0.), ("b", .3))]
        with patch.object(eclipse, "PHASES", (0.,)), patch.object(eclipse, "WIDTHS", (.1,)), \
                patch.object(eclipse, "DEPTHS", (1.,)), patch.object(eclipse, "JITTERS", (0.,)):
            result = eclipse.eclipse_sensitivity(rows, "U Gem", 12.)
        self.assertTrue(result["passed"])
        for mode in ("median", "brightest"):
            self.assertEqual(result["baseline"][mode]["count"], 25)
            self.assertEqual(result["baseline"][mode]["early_count"], 0)
            self.assertEqual(result["results"][0]["reductions"][mode]["relative_recovery"], 1.)

    def test_reduction_agreement_cannot_replace_ordinary_qualification(self):
        events = [dict(onset_t=100 + i * 50., peak_t=105 + i * 50., confirmed_event=True,
                       onset_report_eligible=True, bright_span=10.) for i in range(25)]
        ordinary = {"ordinary_passed": True, "df_feature_supported_marked": 40,
                    "df_outcome_supported_marked": 40}
        failed = {**ordinary, "ordinary_passed": False}
        with patch.object(eclipse, "x5_episodes", return_value=events):
            self.assertTrue(eclipse.compare_reductions([], [], 10, ordinary, ordinary)["passed"])
            self.assertFalse(eclipse.compare_reductions([], [], 10, ordinary, failed)["passed"])
            fewer = {**ordinary, "df_outcome_supported_marked": 30}
            result = eclipse.compare_reductions([], [], 10, ordinary, fewer)
            self.assertFalse(result["gates"]["supported_count_agreement"])

    def test_unmatched_events_count_against_agreement(self):
        left = [dict(onset_t=100 + i * 50., peak_t=105 + i * 50., confirmed_event=True,
                     onset_report_eligible=True, bright_span=10.) for i in range(25)]
        right = copy.deepcopy(left)
        for event in right[:3]:
            event["onset_t"] += 4
        ordinary = {"ordinary_passed": True, "df_feature_supported_marked": 40,
                    "df_outcome_supported_marked": 40}
        with patch.object(eclipse, "x5_episodes", side_effect=[left, right]):
            result = eclipse.compare_reductions([], [], 10, ordinary, ordinary)
        self.assertFalse(result["gates"]["episode_matching"])
        self.assertAlmostEqual(result["matching_fraction"], 22 / 25)


if __name__ == "__main__":
    unittest.main()
