from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.injection_observe import calibrate, prepare_schedule, simulate_rows


def row(jd, mag, who, *, limit="0", band="Vis.", val="V", obs_id=None):
    return {"JD": jd, "mag": mag, "fainterThan": limit, "band": band,
            "val": val, "obsID": obs_id or f"native-{jd}-{who}", "by": who,
            "obsName": who}


class InjectionObservationTests(unittest.TestCase):
    def test_leave_observer_out_calibration_collapses_repeats(self):
        rows = [row(100.1, 8.0, "a"), row(100.2, 8.2, "a"),
                row(100.3, 8.4, "b"), row(100.4, 8.4, "b"),
                row(101.1, 8.0, "a"), row(101.2, 8.0, "b")]
        model, summary = calibrate(rows)
        self.assertAlmostEqual(model["o0001"]["offset"], -0.15 * 2 / 12)
        self.assertAlmostEqual(model["o0002"]["offset"], 0.15 * 2 / 12)
        self.assertEqual(model["o0001"]["n_residuals"], 2)
        self.assertEqual(model["o0002"]["n_residuals"], 2)
        self.assertEqual(summary["calibration_bins"], 2)

    def test_former_limit_can_be_bright_detection_and_limit_direction(self):
        rows = [row(100.1, 10.0, "a", limit="1"), row(100.2, 10.0, "a")]
        schedule = prepare_schedule(rows)
        model = {"o0001": {"offset": 0.0, "sigma": 0.0, "median_limit": 10.0}}
        simulated = simulate_rows(schedule, [8.0, 12.0], model, 7)
        self.assertEqual(simulated[0]["fainterThan"], "0")
        self.assertEqual(simulated[0]["mag"], 8.0)
        self.assertEqual(simulated[1]["fainterThan"], "1")
        self.assertEqual(simulated[1]["mag"], 10.0)

    def test_emitted_limit_is_not_rounded(self):
        rows = [row(100.1, 9.95, "a", limit="1")]
        schedule = prepare_schedule(rows)
        model = {"o0001": {"offset": 0.0, "sigma": 0.0, "median_limit": None}}
        simulated = simulate_rows(schedule, [10.0], model, 7)
        self.assertEqual(simulated[0]["fainterThan"], "1")
        self.assertEqual(simulated[0]["mag"], 9.95)

    def test_determinism_and_no_source_identity_or_truth_fields(self):
        rows = [row(100.1, 8.0, "real observer"), row(100.2, 10.5, "other observer", limit="1")]
        schedule = prepare_schedule(rows)
        model, _ = calibrate(rows)
        first = simulate_rows(schedule, [8.0, 10.5], model, "seed")
        second = simulate_rows(schedule, [8.0, 10.5], model, "seed")
        changed = simulate_rows(schedule, [8.0, 10.5], model, "different")
        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)
        self.assertNotIn("real observer", repr(schedule))
        self.assertNotIn("native-100.1-real observer", repr(schedule))
        self.assertTrue(all(item["by"].startswith("o") for item in first))
        self.assertTrue(all(item["obsID"].startswith("syn") for item in first))
        self.assertFalse(any(key.startswith("truth") for key in first[0]))

    def test_schedule_filters_and_episode_padding_summary(self):
        rows = [row(100.1, 8.0, "a"), row(100.2, 8.0, "b"),
                row(101.1, 8.0, "a"), row(101.2, 8.0, "b"),
                row(110.1, 8.0, "a"), row(110.2, 8.0, "b"),
                row(111.0, 8.0, "ignored", band="R"), row(112.0, 8.0, "flagged", val="T")]
        schedule = prepare_schedule(rows)
        model, summary = calibrate(rows, [{"onset_lo": 100, "onset_hi": 101, "end_lo": 102, "end_hi": 103}])
        self.assertEqual(len(schedule), 6)
        self.assertEqual(summary["calibration_bins"], 1)
        self.assertEqual(summary["plateau_bins"], 3)
        self.assertEqual(summary["n_observers"], 2)
        self.assertNotIn("observers", summary)
        self.assertEqual(set(model), {"o0001", "o0002"})

    def test_rejects_empty_nonfinite_and_length_mismatch(self):
        with self.assertRaises(ValueError):
            prepare_schedule([])
        with self.assertRaises(ValueError):
            prepare_schedule([row(float("nan"), 8.0, "a")])
        schedule = prepare_schedule([row(100.1, 8.0, "a")])
        with self.assertRaises(ValueError):
            simulate_rows(schedule, [], None, 1)
        with self.assertRaises(ValueError):
            simulate_rows(schedule, [float("inf")], None, 1)
        with self.assertRaises(ValueError):
            simulate_rows(schedule, [8.0], {}, 1)


if __name__ == "__main__":
    unittest.main()
