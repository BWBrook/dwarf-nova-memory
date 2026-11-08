from pathlib import Path
import math
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.phase_cadence import (
    PhaseCadenceConfig,
    build_profiles,
    phase_aligned_schedule,
)


def native_row(jd, magnitude, observer, index, *, limit="0", band="Vis.", val="V"):
    return {
        "JD": str(jd),
        "mag": str(magnitude),
        "fainterThan": limit,
        "band": band,
        "val": val,
        "obsID": f"private-{index}",
        "by": observer,
        "obsName": observer,
    }


def available_day(day, observer="o0099", *, fraction=0.2, limit=None):
    when = day + fraction
    return {
        "day": day,
        "state": "F",
        "slots": [
            {
                "JD": str(when),
                "t": when,
                "band": "Vis.",
                "val": "V",
                "observer_id": observer,
                "slot_limit": limit,
            }
        ],
    }


class Event:
    def __init__(self, event_id=1, onset=100.0, end=105.0):
        self.event_id = event_id
        self.onset = onset
        self.end = end

    def threshold_interval(self, threshold):
        if threshold != 10.0:
            raise AssertionError("unexpected threshold")
        return self.onset, self.end


class PhaseHistory:
    def __init__(self, events=None, *, expose_events=True, reserved_stop=math.inf):
        if expose_events:
            self.events = tuple(events or [Event()])
        self.reserved_stop = reserved_stop
        self.queries = []

    def evaluate(self, times):
        if any(time >= self.reserved_stop for time in times):
            raise AssertionError("queried beyond reserved stop")
        self.queries.extend(times)
        output = []
        for time in times:
            if time < 100.0 or time > 105.0:
                output.append(12.0)
            elif time <= 101.0:
                output.append(10.0 - 2.0 * (time - 100.0))
            elif time <= 104.0:
                output.append(8.0)
            else:
                output.append(8.0 + 2.0 * (time - 104.0))
        return output


def profile(profile_id="p0001", cast=("o0001", "o0002", "o0003"), epoch=102.0):
    anchors = {
        "quiet_before": -2.0,
        "onset": 0.0,
        "core_rise": 0.5,
        "core_fade": 4.5,
        "end": 5.0,
        "quiet_after": 7.0,
        "robust_peak_level": 8.0,
        "core_level": 9.0,
    }
    source_times = (-1.8, 0.25, 0.75, 2.2, 3.2, 4.75, 5.25, 6.2)
    slots = []
    for index, when in enumerate(source_times):
        slots.append(
            {
                "JD": when,
                "t": when,
                "band": "Vis.",
                "val": "V",
                "observer_id": cast[index % len(cast)],
                "slot_limit": 11.3 if index == 5 else None,
                "source_slot": index,
            }
        )
    return {
        "profile_id": profile_id,
        "epoch": epoch,
        "season_anchor": 100.0,
        "duration": 5.0,
        "anchors": anchors,
        "phase_fractions": {"rise": 0.1, "core": 0.8, "decline": 0.1},
        "slots": slots,
    }


class PhaseProfileTests(unittest.TestCase):
    def source_rows(self):
        levels = [
            (0.2, 12.0),
            (1.2, 9.8),
            (2.2, 8.5),
            (3.2, 8.2),
            (4.2, 8.5),
            (5.2, 9.3),
            (6.2, 10.0),
            (7.2, 11.5),
        ]
        rows = []
        index = 0
        for jd, level in levels:
            for observer, offset in (("Zeta", 0.0), ("alpha", 0.1)):
                index += 1
                rows.append(native_row(jd + offset, level, observer, index))
        index += 1
        rows.append(native_row(20.2, 11.0, "middle", index, limit="1"))
        return rows

    def test_build_profiles_uses_full_set_mapping_and_leaks_no_identity_or_source_id(self):
        rows = self.source_rows()
        model = {
            observer_id: {"offset": 0.0, "sigma": 0.2, "median_limit": None}
            for observer_id in ("o0001", "o0002", "o0003")
        }
        result = build_profiles(rows, model=model)
        self.assertEqual(result["schema"], "dnmem.phase_profiles.v1")
        self.assertEqual(result["observer_mapping"]["n_observers"], 3)
        self.assertEqual(result["summary"]["profiles"], 1)
        observers = {
            slot["observer_id"]
            for candidate in result["profiles"]
            for slot in candidate["slots"]
        }
        self.assertEqual(observers, {"o0001", "o0003"})
        serialized = repr(result)
        for private in ("alpha", "Zeta", "middle", "private-"):
            self.assertNotIn(private, serialized)
        self.assertNotIn("mag", result["profiles"][0]["slots"][0])
        anchors = result["profiles"][0]["anchors"]
        self.assertLess(anchors["onset"], anchors["core_rise"])
        self.assertLess(anchors["core_rise"], anchors["core_fade"])
        self.assertLess(anchors["core_fade"], anchors["end"])

    def test_build_profiles_checks_model_and_accepts_explicit_existing_map(self):
        rows = self.source_rows()
        with self.assertRaisesRegex(ValueError, "model is missing"):
            build_profiles(rows, model={"o0001": {}})
        mapped = build_profiles(
            rows,
            id_map={"alpha": "o0100", "middle": "o0101", "zeta": "o0102"},
        )
        observers = {
            slot["observer_id"]
            for candidate in mapped["profiles"]
            for slot in candidate["slots"]
        }
        self.assertEqual(observers, {"o0100", "o0102"})

    def test_single_observer_x1_episode_remains_in_donor_population(self):
        levels = [12.0, 9.8, 8.5, 8.2, 8.5, 9.3, 10.0, 11.5]
        rows = [
            native_row(index + 0.2, level, "solo", index)
            for index, level in enumerate(levels)
        ]
        result = build_profiles(rows)
        self.assertEqual(result["summary"]["x1_episodes"], 1)
        self.assertEqual(result["summary"]["profiles"], 1)
        self.assertEqual(
            {slot["observer_id"] for slot in result["profiles"][0]["slots"]},
            {"o0001"},
        )

    def test_phase_transfer_preserves_empty_days_limits_cast_and_quiet_schedule(self):
        days = [available_day(day) for day in range(95, 111) if day != 103]
        schedule, metadata = phase_aligned_schedule(
            days,
            {"threshold": 10.0, "core_fraction": 0.5, "profiles": [profile()]},
            PhaseHistory(),
            95.0,
            111.0,
            seed=17,
        )
        emitted_days = {math.floor(float(row["JD"])) for row in schedule}
        self.assertNotIn(103, emitted_days)
        self.assertTrue(emitted_days <= {record["day"] for record in days})
        self.assertTrue(metadata["output_never_uses_originally_empty_day"])
        self.assertGreater(metadata["unavailable_day_drops"], 0)
        self.assertGreater(metadata["donor_missing_available_days"], 0)
        self.assertIn("o0001", {row["observer_id"] for row in schedule})
        self.assertIn(11.3, {row["slot_limit"] for row in schedule})
        self.assertTrue(any(float(row["JD"]) < 98 for row in schedule))
        self.assertTrue(all("source_slot" not in row for row in schedule))
        self.assertEqual(metadata["matched_events"], 1)
        self.assertEqual(len(metadata["events"][0]["phase_stretch"]), 5)

    def test_one_to_one_transfer_is_deterministic_and_drops_duplicate_source_slot(self):
        donor = profile()
        donor["slots"].append(dict(donor["slots"][2]))
        days = [available_day(day) for day in range(95, 111)]
        first = phase_aligned_schedule(days, [donor], PhaseHistory(), 95, 111, "fixed")
        second = phase_aligned_schedule(days, [donor], PhaseHistory(), 95, 111, "fixed")
        self.assertEqual(first, second)
        self.assertEqual(first[1]["duplicate_source_drops"], 1)
        event = first[1]["events"][0]
        self.assertEqual(event["source_visits"], 9)
        self.assertEqual(event["emitted_visits_before_collision_merge"], 8)
        transferred = [
            float(row["JD"])
            for row in first[0]
            if row["observer_id"] != "o0099"
        ]
        for actual, expected in zip(
            transferred,
            (98.2, 100.25, 100.75, 102.2, 103.2, 104.75, 105.25, 106.2),
        ):
            self.assertAlmostEqual(actual, expected, places=7)

    def test_evaluate_only_history_finds_threshold_interval_without_future_query(self):
        days = [available_day(day) for day in range(95, 111)]
        history = PhaseHistory(expose_events=False, reserved_stop=111.0)
        _, metadata = phase_aligned_schedule(
            days,
            [profile()],
            history,
            95.0,
            111.0,
            4,
            config=PhaseCadenceConfig(history_grid_days=0.5),
        )
        self.assertEqual(metadata["target_events"], 1)
        self.assertEqual(metadata["matched_events"], 1)
        self.assertTrue(history.queries)
        self.assertTrue(all(95.0 <= time < 111.0 for time in history.queries))

    def test_donor_selection_is_epoch_season_phase_based_not_cast_size(self):
        one_observer = profile("p0001", ("o0001",), epoch=102.0)
        many_observers = profile("p0002", ("o0002", "o0003", "o0004"), epoch=112.0)
        days = [available_day(day) for day in range(95, 111)]
        schedule, metadata = phase_aligned_schedule(
            days,
            [many_observers, one_observer],
            PhaseHistory(),
            95,
            111,
            6,
            config={"era_radius_days": 100.0},
        )
        self.assertEqual(metadata["events"][0]["profile_id"], "p0001")
        self.assertEqual(metadata["events"][0]["matching"]["eligible"], 1)
        transferred = [row for row in schedule if row["observer_id"] != "o0099"]
        self.assertEqual({row["observer_id"] for row in transferred}, {"o0001"})
        self.assertIn("never following gap, observer count", metadata["scope"])

    def test_rejects_nonanonymous_slots_and_unbounded_configuration(self):
        bad_days = [available_day(100, observer="real-person")]
        with self.assertRaisesRegex(ValueError, "anonymous"):
            phase_aligned_schedule(bad_days, [profile()], PhaseHistory(), 95, 111, 1)
        with self.assertRaisesRegex(ValueError, "bounded domains"):
            phase_aligned_schedule(
                [available_day(100)],
                [profile()],
                PhaseHistory(),
                95,
                111,
                1,
                config={"season_window_days": 300},
            )


if __name__ == "__main__":
    unittest.main()
