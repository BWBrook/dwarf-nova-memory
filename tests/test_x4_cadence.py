from pathlib import Path
import math
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dnmem.x4_cadence import diverse_state_schedule, observer_diversity


def day(day_number, state, observer, *, fraction=0.25, limit=None):
    when = day_number + fraction
    return {
        "day": day_number,
        "state": state,
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


class WindowHistory:
    def __init__(self, bright_start, bright_stop, reserved_stop=math.inf):
        self.bright_start = bright_start
        self.bright_stop = bright_stop
        self.reserved_stop = reserved_stop
        self.queries = []

    def evaluate(self, times):
        if any(time >= self.reserved_stop for time in times):
            raise AssertionError("future reserved data were queried")
        self.queries.extend(times)
        return [9.0 if self.bright_start <= time < self.bright_stop else 12.0 for time in times]


def emitted(jd, observer, mag, index):
    return {
        "obsID": f"r{index}",
        "JD": str(jd),
        "mag": str(mag),
        "uncert": "",
        "fainterThan": "0",
        "band": "Vis.",
        "by": observer,
        "obsName": observer,
        "val": "V",
    }


class DiverseCadenceTests(unittest.TestCase):
    def donor_and_target_days(self):
        donors = [
            day(100 + index, "B", observer, fraction=0.1 + index / 100, limit=13.0)
            for index, observer in enumerate(("a", "b", "c", "d", "e"))
        ]
        targets = [day(200 + index, "F", "quiet") for index in range(5)]
        return donors + targets

    def test_preserves_every_empty_native_day_and_never_initiates_observation(self):
        days = [day(100, "F", "a"), day(102, "F", "b"), day(104, "F", "c")]
        schedule, metadata = diverse_state_schedule(
            days, WindowHistory(300, 301), 100, 105, seed=7
        )
        self.assertEqual({math.floor(float(row["JD"])) for row in schedule}, {100, 102, 104})
        self.assertEqual(metadata["empty_days_preserved"], 2)
        self.assertEqual(metadata["observed_target_days"], 3)
        self.assertTrue(
            {
                "borrowed_days",
                "no_match_days",
                "observed_target_days",
                "empty_days_preserved",
                "boundary_rows_omitted",
                "donor_reuse",
            }.issubset(metadata)
        )

    def test_bright_run_uses_deterministic_chronological_donor_progression(self):
        days = self.donor_and_target_days()
        first, first_metadata = diverse_state_schedule(
            days, WindowHistory(200, 205), 90, 210, seed=23
        )
        second, second_metadata = diverse_state_schedule(
            days, WindowHistory(200, 205), 90, 210, seed=23
        )
        self.assertEqual(first, second)
        self.assertEqual(first_metadata, second_metadata)
        target = [row for row in first if 200 <= float(row["JD"]) < 205]
        self.assertEqual([row["observer_id"] for row in target], ["a", "b", "c", "d", "e"])
        self.assertEqual([math.floor(float(row["JD"])) for row in target], list(range(200, 205)))
        self.assertEqual(first_metadata["donor_reuse"]["bright_reused_assignments"], 0)

    def test_limits_and_observer_identity_are_retained_without_invented_ids(self):
        schedule, _ = diverse_state_schedule(
            self.donor_and_target_days(), WindowHistory(200, 205), 90.0, 205.6, seed=11
        )
        target = [row for row in schedule if 200 <= float(row["JD"]) < 205.6]
        borrowed = [row for row in target if row["observer_id"] in {"a", "b", "c", "d", "e"}]
        self.assertEqual({row["slot_limit"] for row in borrowed}, {13.0})
        self.assertTrue(all("obsID" not in row for row in schedule))
        self.assertTrue(all(90.0 <= float(row["JD"]) < 205.6 for row in schedule))

    def test_history_queries_stay_inside_reserved_window(self):
        history = WindowHistory(200, 205, reserved_stop=210)
        diverse_state_schedule(self.donor_and_target_days(), history, 90, 210, seed=3)
        self.assertTrue(history.queries)
        self.assertTrue(all(time < 210 for time in history.queries))

    def test_omits_slot_outside_window_before_querying_history(self):
        history = WindowHistory(200, 205, reserved_stop=209.2)
        schedule, metadata = diverse_state_schedule(
            [day(209, "F", "reserved")], history, 90, 209.2, seed=3
        )
        self.assertEqual(schedule, [])
        self.assertEqual(metadata["boundary_rows_omitted"], 1)
        self.assertEqual(history.queries, [])

    def test_artificial_nearest_day_failure_is_replaced_by_rotating_cast(self):
        schedule, metadata = diverse_state_schedule(
            self.donor_and_target_days(), WindowHistory(200, 205), 90, 210, seed=5
        )
        target_cast = {
            row["observer_id"] for row in schedule if 200 <= float(row["JD"]) < 205
        }
        self.assertEqual(target_cast, {"a", "b", "c", "d", "e"})
        self.assertEqual(metadata["bright_runs_matched"], 1)

    def test_too_short_episode_creates_reported_missingness_instead_of_clamping(self):
        donors = [day(100 + index, "B", observer) for index, observer in enumerate("abc")]
        targets = [day(200 + index, "F", f"q{index}") for index in range(5)]
        schedule, metadata = diverse_state_schedule(
            donors + targets, WindowHistory(200, 205), 90, 210, seed=5
        )
        target = [row for row in schedule if 200 <= float(row["JD"]) < 205]
        self.assertEqual([row["observer_id"] for row in target], list("abc"))
        self.assertEqual(metadata["additional_empty_days"], 2)
        self.assertEqual(metadata["bright_runs_matched"], 1)

    def test_whole_donor_block_retains_mixed_faint_and_missing_relative_days(self):
        donors = [
            day(100, "B", "a"),
            day(101, "mixed", "mixed-cast"),
            day(103, "F", "faint-cast"),
            day(104, "B", "b"),
        ]
        targets = [day(200 + index, "F", f"q{index}") for index in range(5)]
        schedule, metadata = diverse_state_schedule(
            donors + targets, WindowHistory(200, 205), 90, 210, seed=17
        )
        target = [row for row in schedule if 200 <= float(row["JD"]) < 205]
        self.assertEqual(
            [row["observer_id"] for row in target],
            ["a", "mixed-cast", "faint-cast", "b"],
        )
        self.assertEqual(
            [math.floor(float(row["JD"])) for row in target], [200, 201, 203, 204]
        )
        self.assertEqual(metadata["additional_empty_days"], 1)

    def test_observer_diversity_filters_peak_era_and_includes_unconfirmed(self):
        rows = []
        index = 0
        index += 1
        rows.append(emitted(-1.2, "faint", 12.0, index))
        for jd in range(5):
            index += 1
            rows.append(emitted(jd + 0.2, "solo", 9.0, index))
        index += 1
        rows.append(emitted(5.2, "faint", 12.0, index))
        for jd in range(10, 15):
            for observer in ("b", "c"):
                index += 1
                rows.append(emitted(jd + 0.2, observer, 9.0, index))
        index += 1
        rows.append(emitted(15.2, "faint", 12.0, index))
        summary = observer_diversity(rows)
        self.assertEqual(summary["counts"], [1, 2])
        self.assertEqual(summary["median_bright_observers"], 1.5)
        self.assertEqual(summary["share_le_2"], 1.0)
        self.assertEqual(summary["unconfirmed_episodes"], 1)
        self.assertEqual(summary["confirmed_episodes"], 1)
        era = observer_diversity(rows, start=9.0, stop=16.0)
        self.assertEqual(era["counts"], [2])


if __name__ == "__main__":
    unittest.main()
