"""Smooth synthetic event truth for independent extractor validation."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import heapq
import math
import random
from typing import Literal, Sequence

from . import injection_truth as _timing


Mode = Literal["null", "alternative"]
LatentCoefficients = _timing.LatentCoefficients
TAIL_MAGNITUDE_TOLERANCE = 1e-12
_SUPPORT_CUTOFF = 0.5 * TAIL_MAGNITUDE_TOLERANCE


@dataclass(frozen=True)
class ShapeConfig:
    quiet_magnitude: float = 11.8
    rise_rate_median: float = 0.8
    rise_rate_log_sd: float = 0.65
    decline_rate_median: float = 0.38
    decline_rate_log_sd: float = 0.25
    minimum_rise_rate: float = 0.15
    minimum_decline_rate: float = 0.12
    peak_magnitude_min: float = 8.0
    peak_magnitude_max: float = 8.8
    low_amplitude_probability: float = 0.05
    low_peak_magnitude_min: float = 9.0
    low_peak_magnitude_max: float = 9.5
    reference_threshold: float = 10.0


@dataclass(frozen=True)
class EventTruth:
    event_id: int
    onset_jd: float
    end_jd: float
    duration: float
    gap_after: float | None
    peak_magnitude: float
    event_type: str
    latent_duration: float | None
    latent_gap: float | None
    rise_rate: float
    decline_rate: float
    rise_centre_jd: float
    decline_centre_jd: float
    rise_tau: float
    decline_tau: float
    requested_peak_magnitude: float
    quiet_magnitude: float

    @property
    def peak_jd(self) -> float:
        return 0.5 * (self.rise_centre_jd + self.decline_centre_jd)

    def magnitude_at(self, jd: float, baseline_magnitude: float | None = None) -> float:
        quiet = (
            float(baseline_magnitude)
            if baseline_magnitude is not None
            else self.quiet_magnitude
        )
        amplitude = quiet - self.peak_magnitude
        time = float(jd)
        if time < self.rise_centre_jd:
            scaled = (time - self.rise_centre_jd) / self.rise_tau
            return quiet - amplitude * math.exp(-0.5 * scaled * scaled)
        if time <= self.decline_centre_jd:
            return self.peak_magnitude
        scaled = (time - self.decline_centre_jd) / self.decline_tau
        return quiet - amplitude * math.exp(-0.5 * scaled * scaled)

    def threshold_interval(
        self, threshold: float, quiet_magnitude: float | None = None
    ) -> tuple[float, float] | None:
        level = float(threshold)
        quiet = (
            float(quiet_magnitude)
            if quiet_magnitude is not None
            else self.quiet_magnitude
        )
        if not math.isfinite(level):
            raise ValueError("threshold must be finite")
        if level >= quiet:
            raise ValueError("threshold must be brighter than the quiet magnitude")
        if level <= self.peak_magnitude:
            return None
        left = _crossing_root(
            self,
            level,
            quiet,
            self.rise_centre_jd,
            self.rise_tau,
            rising=True,
        )
        right = _crossing_root(
            self,
            level,
            quiet,
            self.decline_centre_jd,
            self.decline_tau,
            rising=False,
        )
        return left, right


@dataclass(frozen=True)
class TruthSeries:
    mode: Mode
    start_jd: float
    stop_jd: float
    seed: int
    aligned: bool
    events: tuple[EventTruth, ...]
    diagnostics: dict[str, float | int | str]
    baseline_magnitude: float = 11.8

    def evaluate(self, jds: Sequence[float]) -> tuple[float, ...]:
        """Evaluate the event envelope with at most 1e-12 mag tail truncation.

        Gaussian tails are retained until their individual contribution from
        the quiet magnitude is below the numerical tolerance. This truncation
        is many orders of magnitude below the precision relevant to the tested
        9.5--10.5 magnitude thresholds.
        """
        indexed_times = sorted(
            (float(value), index) for index, value in enumerate(jds)
        )
        if not indexed_times:
            return ()
        supports = sorted(
            (_event_support(event), index, event)
            for index, event in enumerate(self.events)
        )
        result = [self.baseline_magnitude] * len(indexed_times)
        active: dict[int, EventTruth] = {}
        expiry: list[tuple[float, int]] = []
        next_support = 0
        for jd, original_index in indexed_times:
            while next_support < len(supports) and supports[next_support][0][0] <= jd:
                (left, right), event_index, event = supports[next_support]
                if right >= jd:
                    active[event_index] = event
                    heapq.heappush(expiry, (right, event_index))
                next_support += 1
            while expiry and expiry[0][0] < jd:
                _, event_index = heapq.heappop(expiry)
                active.pop(event_index, None)
            magnitude = self.baseline_magnitude
            for event in active.values():
                magnitude = min(magnitude, event.magnitude_at(jd))
            result[original_index] = magnitude
        return tuple(result)


def generate_events(
    duration_marginal: Sequence[float],
    gap_marginal: Sequence[float],
    start: float,
    stop: float,
    seed: int,
    process: Mode = "null",
    anchors: Sequence[float] | None = None,
    *,
    coefficients: LatentCoefficients | None = None,
    burn_in: int = 1000,
    calendar_warmup: float = 1000.0,
    shape_config: ShapeConfig | None = None,
) -> TruthSeries:
    """Generate smooth events while preserving the established timing streams."""
    config = shape_config or ShapeConfig()
    _validate_shape_config(config)
    timing = _timing.generate_events(
        duration_marginal,
        gap_marginal,
        start,
        stop,
        seed,
        process,
        anchors,
        coefficients=coefficients,
        burn_in=burn_in,
        calendar_warmup=calendar_warmup,
    )
    rng = random.Random(_shape_seed(seed))
    events = tuple(_smooth_event(event, rng, config) for event in timing.events)
    adjusted = sum(
        event.peak_magnitude > event.requested_peak_magnitude + 1e-12
        for event in events
    )
    diagnostics = dict(timing.diagnostics)
    diagnostics.update(
        {
            "shape_family": "asymmetric_half_gaussian_flat_peak_v2",
            "quiet_magnitude": config.quiet_magnitude,
            "reference_threshold": config.reference_threshold,
            "geometry_adjusted_count": adjusted,
        }
    )
    return TruthSeries(
        timing.mode,
        timing.start_jd,
        timing.stop_jd,
        timing.seed,
        timing.aligned,
        events,
        diagnostics,
        config.quiet_magnitude,
    )


def magnitudes_at(
    events: TruthSeries | Sequence[EventTruth], times: Sequence[float]
) -> tuple[float, ...]:
    if isinstance(events, TruthSeries):
        return events.evaluate(times)
    records = tuple(events)
    quiet = records[0].quiet_magnitude if records else 11.8
    if any(event.quiet_magnitude != quiet for event in records):
        raise ValueError("all events must use the same quiet magnitude")
    return TruthSeries(
        "null", 0.0, 1.0, 0, False, records, {}, quiet
    ).evaluate(times)


def truth_catalogue(
    events: TruthSeries | Sequence[EventTruth], threshold: float
) -> tuple[dict[str, int | float | str], ...]:
    if isinstance(events, TruthSeries):
        records = events.events
        quiet = events.baseline_magnitude
    else:
        records = tuple(events)
        quiet = None
    intervals: list[tuple[float, float, EventTruth]] = []
    for event in records:
        interval = event.threshold_interval(float(threshold), quiet)
        if interval is not None:
            intervals.append((interval[0], interval[1], event))
    intervals.sort(key=lambda item: (item[0], item[1], item[2].event_id))

    groups: list[list[tuple[float, float, EventTruth]]] = []
    for interval in intervals:
        if not groups or interval[0] > max(item[1] for item in groups[-1]):
            groups.append([interval])
        else:
            groups[-1].append(interval)

    catalogue: list[dict[str, int | float | str]] = []
    for group in groups:
        onset = min(item[0] for item in group)
        end = max(item[1] for item in group)
        peak_event = min(group, key=lambda item: item[2].peak_magnitude)[2]
        if len(group) == 1:
            identifier: int | str = group[0][2].event_id
            event_type = "short" if end - onset < 12.0 else "long"
        else:
            identifier = "+".join(str(item[2].event_id) for item in group)
            event_type = "merged"
        catalogue.append(
            {
                "id": identifier,
                "onset": onset,
                "end": end,
                "peak_t": peak_event.peak_jd,
                "type": event_type,
            }
        )
    return tuple(catalogue)


def _shape_seed(seed: int) -> int:
    digest = hashlib.sha256(f"{int(seed)}:smooth-shape-v2".encode("ascii")).digest()
    return int.from_bytes(digest[:8], "big")


def _event_support(event: EventTruth) -> tuple[float, float]:
    amplitude = event.quiet_magnitude - event.peak_magnitude
    scaled_radius = math.sqrt(2.0 * math.log(amplitude / _SUPPORT_CUTOFF))
    return (
        event.rise_centre_jd - event.rise_tau * scaled_radius,
        event.decline_centre_jd + event.decline_tau * scaled_radius,
    )


def _validate_shape_config(config: ShapeConfig) -> None:
    numeric = (
        config.quiet_magnitude,
        config.rise_rate_median,
        config.rise_rate_log_sd,
        config.decline_rate_median,
        config.decline_rate_log_sd,
        config.minimum_rise_rate,
        config.minimum_decline_rate,
        config.peak_magnitude_min,
        config.peak_magnitude_max,
        config.low_amplitude_probability,
        config.low_peak_magnitude_min,
        config.low_peak_magnitude_max,
        config.reference_threshold,
    )
    if any(not math.isfinite(value) for value in numeric):
        raise ValueError("all shape configuration values must be finite")
    if config.rise_rate_median <= 0.0 or config.decline_rate_median <= 0.0:
        raise ValueError("rate medians must be positive")
    if config.minimum_rise_rate <= 0.0 or config.minimum_decline_rate <= 0.0:
        raise ValueError("minimum rates must be positive")
    if config.rise_rate_log_sd < 0.0 or config.decline_rate_log_sd < 0.0:
        raise ValueError("rate log standard deviations must be non-negative")
    if not 0.0 <= config.low_amplitude_probability <= 1.0:
        raise ValueError("low_amplitude_probability must lie in [0, 1]")
    if not config.peak_magnitude_min <= config.peak_magnitude_max:
        raise ValueError("standard peak magnitude bounds are reversed")
    if not config.low_peak_magnitude_min <= config.low_peak_magnitude_max:
        raise ValueError("low-amplitude peak magnitude bounds are reversed")
    faintest_peak = max(config.peak_magnitude_max, config.low_peak_magnitude_max)
    if faintest_peak >= config.reference_threshold:
        raise ValueError("all configured peaks must be brighter than the reference threshold")
    if config.reference_threshold >= config.quiet_magnitude:
        raise ValueError("reference threshold must be brighter than quiet magnitude")


def _smooth_event(
    source: _timing.EventTruth, rng: random.Random, config: ShapeConfig
) -> EventTruth:
    rise_rate = max(
        config.minimum_rise_rate,
        rng.lognormvariate(math.log(config.rise_rate_median), config.rise_rate_log_sd),
    )
    decline_rate = max(
        config.minimum_decline_rate,
        rng.lognormvariate(
            math.log(config.decline_rate_median), config.decline_rate_log_sd
        ),
    )
    low_amplitude = rng.random() < config.low_amplitude_probability
    if low_amplitude:
        requested_peak = rng.uniform(
            config.low_peak_magnitude_min, config.low_peak_magnitude_max
        )
        event_type = "low_amplitude"
    else:
        requested_peak = rng.uniform(
            config.peak_magnitude_min, config.peak_magnitude_max
        )
        event_type = "standard"

    quiet = config.quiet_magnitude
    threshold = config.reference_threshold
    threshold_amplitude = quiet - threshold
    amplitude = quiet - requested_peak
    inverse_rates = 1.0 / rise_rate + 1.0 / decline_rate
    c_squared = 2.0 * math.log(amplitude / threshold_amplitude)
    transition_duration = threshold_amplitude * c_squared * inverse_rates
    if transition_duration > source.duration:
        c_squared = source.duration / (threshold_amplitude * inverse_rates)
        amplitude = threshold_amplitude * math.exp(0.5 * c_squared)
    peak = quiet - amplitude
    c = math.sqrt(c_squared)
    rise_tau = threshold_amplitude * c / rise_rate
    decline_tau = threshold_amplitude * c / decline_rate
    rise_centre = source.onset_jd + rise_tau * c
    decline_centre = source.end_jd - decline_tau * c
    if decline_centre < rise_centre and rise_centre - decline_centre < 1e-10:
        midpoint = 0.5 * (rise_centre + decline_centre)
        rise_centre = midpoint
        decline_centre = midpoint
    return EventTruth(
        source.event_id,
        source.onset_jd,
        source.end_jd,
        source.duration,
        source.gap_after,
        peak,
        event_type,
        source.latent_duration,
        source.latent_gap,
        rise_rate,
        decline_rate,
        rise_centre,
        decline_centre,
        rise_tau,
        decline_tau,
        requested_peak,
        quiet,
    )


def _crossing_root(
    event: EventTruth,
    threshold: float,
    quiet: float,
    centre: float,
    tau: float,
    *,
    rising: bool,
) -> float:
    inside = centre
    distance = tau
    outside = centre - distance if rising else centre + distance
    while event.magnitude_at(outside, quiet) <= threshold:
        distance *= 2.0
        outside = centre - distance if rising else centre + distance
    left, right = (outside, inside) if rising else (inside, outside)
    for _ in range(80):
        midpoint = 0.5 * (left + right)
        value = event.magnitude_at(midpoint, quiet) - threshold
        if rising:
            if value > 0.0:
                left = midpoint
            else:
                right = midpoint
        elif value <= 0.0:
            left = midpoint
        else:
            right = midpoint
    return 0.5 * (left + right)
