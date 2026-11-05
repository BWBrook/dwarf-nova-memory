"""Synthetic event histories and sampled toy light curves; no real observations.

The simulator encodes deliberately simple, separable alternatives. It is not a
disc-instability or mass-conservation calculation. Truth labels are for checking
algorithms and must never enter a future real-data inference adapter.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import random


SCENARIOS = ("null", "memory", "latent", "both")


@dataclass(frozen=True)
class Event:
    event_id: int
    onset: float
    end: float
    duration: float
    next_quiescent_gap: float
    latent_activity: float

    @property
    def next_onset_gap(self) -> float:
        return self.duration + self.next_quiescent_gap


def simulate_events(scenario: str, n_events: int = 240, seed: int = 1729) -> list[Event]:
    """Generate complete oracle cycles, including a following onset for each row.

    The final simulated Q predicts the onset of a sentinel event outside the
    photometry horizon. It is usable only in the explicitly oracle experiment.
    """
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario {scenario!r}")
    if not isinstance(n_events, int) or n_events < 4:
        raise ValueError("n_events must be an integer >= 4")
    rng = random.Random(seed)
    beta = {"null": 0.0, "memory": 0.8, "latent": 0.0, "both": 0.6}[scenario]
    state_effect = scenario in ("latent", "both")
    z, onset = rng.gauss(0, 1), 0.0
    events: list[Event] = []
    for index in range(n_events):
        z = 0.93 * z + math.sqrt(1 - 0.93**2) * rng.gauss(0, 1)
        log_duration_residual = 0.40 * rng.gauss(0, 1) + (0.35 * z if state_effect else 0.0)
        duration = 8.0 * math.exp(log_duration_residual)
        gap = math.exp(math.log(35) + beta * log_duration_residual
                       + (0.65 * z if state_effect else 0.0) + 0.40 * rng.gauss(0, 1))
        event = Event(index, onset, onset + duration, duration, gap, z if state_effect else 0.0)
        events.append(event)
        onset = event.end + gap
    return events


def truth_rows(events: list[Event]) -> list[dict]:
    return [dict(asdict(e), next_onset_gap=e.next_onset_gap,
                 data_kind="synthetic_oracle", time_unit="relative_demo_days") for e in events]


def sample_photometry(events: list[Event], seed: int = 1730,
                      cadence_days: float = 3.0, seasonal_gap_days: float = 95.0) -> tuple[list[dict], list[dict]]:
    """Independent scheduled observations with one annual visibility gap.

    A positive detection hits an injected event only if its *measured* magnitude
    is <= 12.8. Counting these hits uses known event membership and is therefore
    an oracle visibility diagnostic, not an outburst detector. The cadence here
    is exogenous: state-dependent amateur follow-up is NOT simulated.
    """
    if not events:
        raise ValueError("events must be nonempty")
    if not math.isfinite(cadence_days) or cadence_days <= 0:
        raise ValueError("cadence must be positive and finite")
    if not math.isfinite(seasonal_gap_days) or not 0 <= seasonal_gap_days < 365.25:
        raise ValueError("seasonal gap must be in [0, 365.25)")
    rng = random.Random(seed)
    observations: list[dict] = []
    hits = {e.event_id: 0 for e in events}
    t, j = 0.0, 0
    horizon = events[-1].end
    while t <= horizon:
        phase = t % 365.25
        if phase >= seasonal_gap_days:
            while j + 1 < len(events) and events[j + 1].onset <= t:
                j += 1
            e = events[j]
            active = e.onset <= t < e.end
            if active:
                frac = (t - e.onset) / e.duration
                # A triangular toy light curve in relative flux; positive floor.
                shape = max(0.0, min(frac / 0.15, (1 - frac) / 0.85))
                flux = 1.0 + 24.0 * shape
            else:
                flux = 1.0
            magnitude = 14.5 - 2.5 * math.log10(flux) + rng.gauss(0, 0.12)
            limit = 14.3 if len(observations) % 5 == 0 else 15.5
            is_limit = magnitude > limit
            if active and not is_limit and magnitude <= 12.8:
                hits[e.event_id] += 1
            observations.append({
                "source_row_id": f"sim-{len(observations):06d}",
                "target_id": "SYNTHETIC_DN_001", "time_value": round(t, 8),
                "time_format": "relative_demo_days", "time_scale": "synthetic", "time_reference": "simulation_origin",
                "band": "synthetic_V_like", "magnitude": "" if is_limit else round(magnitude, 6),
                "magnitude_error": "" if is_limit else 0.12,
                "is_upper_limit": "true" if is_limit else "false",
                "limit_magnitude": limit if is_limit else "", "observer_id": "SIMULATOR",
                "quality_flag": "synthetic", "provenance_id": "generated-demo",
            })
        t += cadence_days * rng.uniform(0.85, 1.15)
    visibility = [dict(event_id=e.event_id, above_threshold_hits=hits[e.event_id],
                       hit_at_least_twice=hits[e.event_id] >= 2,
                       truth_only=True) for e in events]
    return observations, visibility
