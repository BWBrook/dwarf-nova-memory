"""Independent smooth-pulse truth for blinded extractor validation.

Event timings come unchanged from :mod:`dnmem.injection_truth`.  This module
uses an independent random stream to replace only the photometric shapes.
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
import hashlib
import math
import random
from typing import Sequence

from dnmem.injection_truth import LatentCoefficients
from dnmem.injection_truth import generate_events as _generate_timing


@dataclass(frozen=True)
class ShapeConfig:
    quiet_magnitude: float = 11.8
    rise_rate_median: float = 0.95
    rise_rate_log_sd: float = 0.65
    decline_rate_median: float = 0.4
    decline_rate_log_sd: float = 0.2
    minimum_rise_rate: float = 0.15
    minimum_decline_rate: float = 0.12
    peak_magnitude_min: float = 8.0
    peak_magnitude_max: float = 8.8
    low_amplitude_probability: float = 0.05
    low_peak_magnitude_min: float = 9.0
    low_peak_magnitude_max: float = 9.5
    reference_threshold: float = 10.0
    minimum_plateau_fraction: float = 0.08
    maximum_gap_fraction_per_flank: float = 0.45


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
    support_start_jd: float
    plateau_start_jd: float
    plateau_end_jd: float
    support_end_jd: float
    rise_width: float
    decline_width: float
    drawn_rise_slope: float
    drawn_decline_slope: float
    rise_slope_at_reference: float
    decline_slope_at_reference: float
    geometry_constraints: tuple[str, ...]
    baseline_magnitude: float = 11.8
    reference_magnitude: float = 10.0

    @property
    def peak_jd(self) -> float:
        return 0.5 * (self.plateau_start_jd + self.plateau_end_jd)

    def magnitude_at(self, jd: float, baseline_magnitude: float | None = None) -> float:
        baseline = self.baseline_magnitude if baseline_magnitude is None else float(baseline_magnitude)
        time = float(jd)
        if time == self.onset_jd or time == self.end_jd:
            return self.reference_magnitude
        if time < self.support_start_jd or time > self.support_end_jd:
            return baseline
        if time < self.plateau_start_jd:
            phase = (time - self.support_start_jd) / self.rise_width
            return self.peak_magnitude + (self.baseline_magnitude - self.peak_magnitude) * (
                1.0 + math.cos(math.pi * phase)
            ) / 2.0
        if time <= self.plateau_end_jd:
            return self.peak_magnitude
        phase = (time - self.plateau_end_jd) / self.decline_width
        return self.peak_magnitude + (self.baseline_magnitude - self.peak_magnitude) * (
            1.0 - math.cos(math.pi * phase)
        ) / 2.0

    def threshold_interval(self, threshold: float) -> tuple[float, float] | None:
        level = float(threshold)
        if not math.isfinite(level):
            raise ValueError("threshold must be finite")
        if level < self.peak_magnitude:
            return None
        if level == self.reference_magnitude:
            return self.onset_jd, self.end_jd
        if level == self.peak_magnitude:
            return self.plateau_start_jd, self.plateau_end_jd
        if level >= self.baseline_magnitude:
            return self.support_start_jd, self.support_end_jd
        phase = _crossing_phase(
            self.baseline_magnitude, self.peak_magnitude, level
        )
        return (
            self.support_start_jd + phase * self.rise_width,
            self.plateau_end_jd + (1.0 - phase) * self.decline_width,
        )


@dataclass(frozen=True)
class TruthSeries:
    mode: str
    start_jd: float
    stop_jd: float
    seed: int
    events: tuple[EventTruth, ...]
    diagnostics: dict[str, float | int | str | bool]
    baseline_magnitude: float = 11.8

    def evaluate(self, jds: Sequence[float]) -> tuple[float, ...]:
        starts = tuple(event.support_start_jd for event in self.events)
        output: list[float] = []
        for value in jds:
            jd = float(value)
            if not math.isfinite(jd):
                raise ValueError("evaluation times must be finite")
            index = bisect_right(starts, jd) - 1
            if index < 0:
                output.append(self.baseline_magnitude)
            else:
                output.append(self.events[index].magnitude_at(jd, self.baseline_magnitude))
        return tuple(output)


def generate_events(
    duration_marginal: Sequence[float],
    gap_marginal: Sequence[float],
    start: float,
    stop: float,
    seed: int,
    process: str = "null",
    coefficients: LatentCoefficients | None = None,
    shape_config: ShapeConfig = ShapeConfig(),
) -> TruthSeries:
    """Generate timings with the original process and replace only their shapes."""
    config = _validated_config(shape_config)
    timing = _generate_timing(
        duration_marginal,
        gap_marginal,
        start,
        stop,
        seed,
        process,
        coefficients=coefficients,
    )
    rng = random.Random(_stream_seed(seed, "independent-smooth-shape-v3"))
    minimum_gap = min(float(value) for value in gap_marginal)
    events = _shape_events(timing.events, minimum_gap, rng, config)
    constrained = [event for event in events if event.geometry_constraints]
    diagnostics = dict(timing.diagnostics)
    diagnostics.update(
        {
            "shape_family": "asymmetric_half_cosine_with_plateau",
            "shape_stream": "independent-smooth-shape-v3",
            "baseline_magnitude": config.quiet_magnitude,
            "reference_magnitude": config.reference_threshold,
            "shape_geometry_constrained_count": len(constrained),
            "shape_duration_constrained_count": sum(
                "duration" in event.geometry_constraints for event in events
            ),
            "shape_gap_constrained_count": sum(
                any(reason.startswith("gap_") for reason in event.geometry_constraints)
                for event in events
            ),
            "low_amplitude_count": sum(event.event_type == "low_amplitude" for event in events),
            "shape_timing_unchanged": True,
        }
    )
    return TruthSeries(
        process,
        float(start),
        float(stop),
        int(seed),
        events,
        diagnostics,
        config.quiet_magnitude,
    )


def magnitudes_at(
    history: TruthSeries | Sequence[EventTruth], times: Sequence[float]
) -> tuple[float, ...]:
    if isinstance(history, TruthSeries):
        return history.evaluate(times)
    events = tuple(history)
    baseline = events[0].baseline_magnitude if events else 11.8
    return TruthSeries("null", 0.0, 1.0, 0, events, {}, baseline).evaluate(times)


def truth_catalogue(
    history: TruthSeries | Sequence[EventTruth], threshold: float
) -> tuple[dict[str, int | float | str], ...]:
    events = history.events if isinstance(history, TruthSeries) else tuple(history)
    records: list[dict[str, int | float | str]] = []
    for event in events:
        interval = event.threshold_interval(threshold)
        if interval is None:
            continue
        onset, end = interval
        records.append(
            {
                "id": event.event_id,
                "onset": onset,
                "end": end,
                "duration": end - onset,
                "peak_t": event.peak_jd,
                "peak": event.peak_magnitude,
                "type": "short" if end - onset < 12.0 else "long",
            }
        )
    return tuple(records)


def _validated_config(config: ShapeConfig) -> ShapeConfig:
    if not isinstance(config, ShapeConfig):
        raise TypeError("shape_config must be a ShapeConfig")
    numeric = tuple(float(value) for value in config.__dict__.values())
    if any(not math.isfinite(value) for value in numeric):
        raise ValueError("all shape configuration values must be finite")
    if not config.peak_magnitude_min < config.peak_magnitude_max < config.reference_threshold:
        raise ValueError("nominal peaks must be ordered and brighter than the reference")
    if not config.low_peak_magnitude_min < config.low_peak_magnitude_max < config.reference_threshold:
        raise ValueError("low-amplitude peaks must be ordered and brighter than the reference")
    if config.quiet_magnitude <= config.reference_threshold:
        raise ValueError("baseline must be fainter than the reference magnitude")
    if not 0.0 <= config.low_amplitude_probability <= 1.0:
        raise ValueError("low_amplitude_probability must lie in [0, 1]")
    slopes = (
        config.rise_rate_median,
        config.minimum_rise_rate,
        config.decline_rate_median,
        config.minimum_decline_rate,
    )
    if any(value <= 0.0 for value in slopes):
        raise ValueError("slope medians and minima must be positive")
    if config.rise_rate_log_sd < 0.0 or config.decline_rate_log_sd < 0.0:
        raise ValueError("slope log standard deviations must be non-negative")
    if not 0.0 <= config.minimum_plateau_fraction < 1.0:
        raise ValueError("minimum_plateau_fraction must lie in [0, 1)")
    if not 0.0 < config.maximum_gap_fraction_per_flank < 0.5:
        raise ValueError("maximum_gap_fraction_per_flank must lie in (0, 0.5)")
    return config


def _stream_seed(seed: int, label: str) -> int:
    digest = hashlib.sha256(f"{int(seed)}:{label}".encode("ascii")).digest()
    return int.from_bytes(digest[:8], "big")


def _crossing_phase(baseline: float, peak: float, threshold: float) -> float:
    cosine = 2.0 * (threshold - peak) / (baseline - peak) - 1.0
    return math.acos(max(-1.0, min(1.0, cosine))) / math.pi


def _flank_constants(baseline: float, peak: float, reference: float) -> tuple[float, float, float]:
    phase = _crossing_phase(baseline, peak, reference)
    derivative_factor = (
        (baseline - peak) * math.pi * math.sin(math.pi * phase) / 2.0
    )
    return phase, derivative_factor * phase, derivative_factor * (1.0 - phase)


def _shape_events(base_events, minimum_gap: float, rng: random.Random, config: ShapeConfig) -> tuple[EventTruth, ...]:
    events: list[EventTruth] = []
    for index, base in enumerate(base_events):
        low = rng.random() < config.low_amplitude_probability
        if low:
            peak = rng.uniform(config.low_peak_magnitude_min, config.low_peak_magnitude_max)
            event_type = "low_amplitude"
        else:
            peak = rng.uniform(config.peak_magnitude_min, config.peak_magnitude_max)
            event_type = "standard"
        drawn_rise = max(
            config.minimum_rise_rate,
            math.exp(math.log(config.rise_rate_median) + config.rise_rate_log_sd * rng.gauss(0.0, 1.0)),
        )
        drawn_decline = max(
            config.minimum_decline_rate,
            math.exp(math.log(config.decline_rate_median) + config.decline_rate_log_sd * rng.gauss(0.0, 1.0)),
        )
        phase, outer_constant, inner_constant = _flank_constants(
            config.quiet_magnitude, peak, config.reference_threshold
        )
        previous_gap = base_events[index - 1].gap_after if index else None
        before_gap = float(previous_gap) if previous_gap is not None else minimum_gap
        after_gap = float(base.gap_after) if base.gap_after is not None else minimum_gap
        constraints: list[str] = []
        rise = drawn_rise
        decline = drawn_decline
        rise_gap_minimum = outer_constant / (
            config.maximum_gap_fraction_per_flank * before_gap
        )
        decline_gap_minimum = outer_constant / (
            config.maximum_gap_fraction_per_flank * after_gap
        )
        if rise < rise_gap_minimum:
            rise = rise_gap_minimum
            constraints.append("gap_before")
        if decline < decline_gap_minimum:
            decline = decline_gap_minimum
            constraints.append("gap_after")
        inner_total = inner_constant / rise + inner_constant / decline
        maximum_inner = base.duration * (1.0 - config.minimum_plateau_fraction)
        if inner_total > maximum_inner:
            factor = inner_total / maximum_inner
            rise *= factor
            decline *= factor
            constraints.append("duration")
        rise_width = (outer_constant + inner_constant) / rise
        decline_width = (outer_constant + inner_constant) / decline
        rise_inner = rise_width * (1.0 - phase)
        decline_inner = decline_width * (1.0 - phase)
        plateau_start = base.onset_jd + rise_inner
        plateau_end = base.end_jd - decline_inner
        events.append(
            EventTruth(
                base.event_id,
                base.onset_jd,
                base.end_jd,
                base.duration,
                base.gap_after,
                peak,
                event_type,
                base.latent_duration,
                base.latent_gap,
                base.onset_jd - rise_width * phase,
                plateau_start,
                plateau_end,
                base.end_jd + decline_width * phase,
                rise_width,
                decline_width,
                drawn_rise,
                drawn_decline,
                rise,
                decline,
                tuple(constraints),
                config.quiet_magnitude,
                config.reference_threshold,
            )
        )
    return tuple(events)
