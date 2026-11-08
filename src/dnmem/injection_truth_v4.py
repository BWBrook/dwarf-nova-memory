"""Candidate-blind smooth injection truth with duration-coupled amplitude.

The timing process is inherited unchanged from :mod:`dnmem.injection_truth`.
Shape randomness uses a separate named seed stream.  Each flank is one rounded
power curve through the 10-mag crossing, so there is no join at the extraction
threshold and the independently drawn tangent rate is preserved there.
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
import hashlib
import math
import random
from statistics import median
from typing import Sequence

from .injection_truth import LatentCoefficients, Mode, generate_events as _generate_timing


_BASELINE_MAGNITUDE = 12.2
_THRESHOLD_MAGNITUDE = 10.0
_MINIMUM_TURNOVER_POWER = 1.15
_MINIMUM_AMPLITUDE = 0.15
_MAXIMUM_AMPLITUDE = 3.0


@dataclass(frozen=True)
class ShapeConfig:
    """Predeclared nuisance parameters for the single v4 waveform family.

    Rate spreads and peak scatter are log-scale and magnitude-scale standard
    deviations, respectively.  ``peak_duration_coupling`` is the change in
    peak magnitude per day relative to the input duration median; a negative
    value makes longer events brighter.
    """

    rise_rate_median: float = 0.667
    rise_rate_log_spread: float = 0.30
    decline_rate_median: float = 0.333
    decline_rate_log_spread: float = 0.53
    peak_level: float = 8.37
    peak_duration_coupling: float = -0.055
    peak_scatter: float = 0.25


@dataclass(frozen=True)
class EventTruth:
    event_id: int
    onset_jd: float
    end_jd: float
    duration: float
    gap_after: float | None
    peak_jd: float
    peak_magnitude: float
    event_type: str
    rise_rate: float
    decline_rate: float
    turnover_power: float
    support_start_jd: float
    support_end_jd: float
    latent_duration: float | None
    latent_gap: float | None
    interventions: tuple[str, ...]

    def magnitude_at(self, jd: float, baseline_magnitude: float = _BASELINE_MAGNITUDE) -> float:
        time = float(jd)
        if time <= self.support_start_jd or time >= self.support_end_jd:
            return baseline_magnitude
        amplitude = _THRESHOLD_MAGNITUDE - self.peak_magnitude
        if time <= self.peak_jd:
            scale = self.peak_jd - self.onset_jd
            distance = (self.peak_jd - time) / scale
        else:
            scale = self.end_jd - self.peak_jd
            distance = (time - self.peak_jd) / scale
        value = self.peak_magnitude + amplitude * distance**self.turnover_power
        return min(baseline_magnitude, value)

    def threshold_interval(self, level: float) -> tuple[float, float] | None:
        threshold = float(level)
        if not math.isfinite(threshold):
            raise ValueError("threshold must be finite")
        if threshold < self.peak_magnitude:
            return None
        if threshold >= _BASELINE_MAGNITUDE:
            return self.support_start_jd, self.support_end_jd
        amplitude = _THRESHOLD_MAGNITUDE - self.peak_magnitude
        distance = ((threshold - self.peak_magnitude) / amplitude) ** (
            1.0 / self.turnover_power
        )
        rise_span = self.peak_jd - self.onset_jd
        decline_span = self.end_jd - self.peak_jd
        return self.peak_jd - distance * rise_span, self.peak_jd + distance * decline_span


@dataclass(frozen=True)
class TruthSeries:
    mode: Mode
    start_jd: float
    stop_jd: float
    seed: int
    aligned: bool
    events: tuple[EventTruth, ...]
    diagnostics: dict[str, float | int | str]
    baseline_magnitude: float = _BASELINE_MAGNITUDE

    def evaluate(self, jds: Sequence[float]) -> tuple[float, ...]:
        """Evaluate an arbitrary, unsorted batch without returning event labels."""
        starts = tuple(event.support_start_jd for event in self.events)
        result: list[float] = []
        for value in jds:
            jd = float(value)
            index = bisect_right(starts, jd) - 1
            if index < 0:
                result.append(self.baseline_magnitude)
            else:
                result.append(self.events[index].magnitude_at(jd, self.baseline_magnitude))
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
    shape_config: ShapeConfig | None = None,
    burn_in: int = 1000,
    calendar_warmup: float = 1000.0,
) -> TruthSeries:
    """Generate timing-identical events with independent smooth morphology."""
    config = shape_config or ShapeConfig()
    _validate_shape_config(config)
    timing = _generate_timing(
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
    duration_centre = median(float(value) for value in duration_marginal)
    rng = random.Random(_shape_seed(seed))
    events = _build_events(timing.events, duration_centre, config, rng)
    intervention_counts: dict[str, int] = {}
    for event in events:
        for intervention in event.interventions:
            intervention_counts[intervention] = intervention_counts.get(intervention, 0) + 1
    diagnostics = dict(timing.diagnostics)
    diagnostics.update(
        {
            "waveform_family": "v4_asymmetric_rounded_power",
            "shape_seed_stream": "sha256(seed:injection-truth-v4-shape)",
            "shape_timing_independent": 1,
            "amplitude_turnover_reductions": intervention_counts.get(
                "amplitude_reduced_for_smooth_turnover", 0
            ),
            "amplitude_tail_reductions": intervention_counts.get(
                "amplitude_reduced_for_tail_separation", 0
            ),
            "amplitude_lower_clamps": intervention_counts.get("amplitude_lower_clamped", 0),
            "amplitude_upper_clamps": intervention_counts.get("amplitude_upper_clamped", 0),
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
    )


def magnitudes_at(
    history: TruthSeries | Sequence[EventTruth], times: Sequence[float]
) -> tuple[float, ...]:
    if isinstance(history, TruthSeries):
        return history.evaluate(times)
    records = tuple(history)
    if not records:
        return tuple(_BASELINE_MAGNITUDE for _ in times)
    temporary = TruthSeries("null", 0.0, 1.0, 0, False, records, {})
    return temporary.evaluate(times)


def truth_catalogue(
    history: TruthSeries | Sequence[EventTruth], level: float
) -> tuple[dict[str, int | float | str], ...]:
    records = history.events if isinstance(history, TruthSeries) else tuple(history)
    catalogue: list[dict[str, int | float | str]] = []
    for event in records:
        interval = event.threshold_interval(level)
        if interval is None:
            continue
        duration = interval[1] - interval[0]
        catalogue.append(
            {
                "id": event.event_id,
                "onset": interval[0],
                "end": interval[1],
                "duration": duration,
                "peak_t": event.peak_jd,
                "type": "short" if duration < 12.0 else "long",
                "peak": event.peak_magnitude,
            }
        )
    return tuple(catalogue)


def _shape_seed(seed: int) -> int:
    digest = hashlib.sha256(f"{int(seed)}:injection-truth-v4-shape".encode("ascii")).digest()
    return int.from_bytes(digest[:8], "big")


def _validate_shape_config(config: ShapeConfig) -> None:
    positive = (
        config.rise_rate_median,
        config.decline_rate_median,
    )
    nonnegative = (
        config.rise_rate_log_spread,
        config.decline_rate_log_spread,
        config.peak_scatter,
    )
    finite = positive + nonnegative + (config.peak_level, config.peak_duration_coupling)
    if any(not math.isfinite(value) for value in finite):
        raise ValueError("all shape parameters must be finite")
    if any(value <= 0.0 for value in positive):
        raise ValueError("median flank rates must be positive")
    if any(value < 0.0 for value in nonnegative):
        raise ValueError("shape spreads must be non-negative")
    if not 7.0 < config.peak_level < _THRESHOLD_MAGNITUDE:
        raise ValueError("peak_level must lie between 7 and 10 magnitudes")


def _build_events(base_events, duration_centre, config, rng):
    built: list[EventTruth] = []
    minimum_gap = min(
        (float(event.gap_after) for event in base_events if event.gap_after is not None),
        default=5.0,
    )
    for index, base in enumerate(base_events):
        rise_rate = config.rise_rate_median * math.exp(
            rng.gauss(0.0, config.rise_rate_log_spread)
        )
        decline_rate = config.decline_rate_median * math.exp(
            rng.gauss(0.0, config.decline_rate_log_spread)
        )
        peak = (
            config.peak_level
            + config.peak_duration_coupling * (base.duration - duration_centre)
            + rng.gauss(0.0, config.peak_scatter)
        )
        amplitude = _THRESHOLD_MAGNITUDE - peak
        interventions: list[str] = []
        if amplitude < _MINIMUM_AMPLITUDE:
            amplitude = _MINIMUM_AMPLITUDE
            interventions.append("amplitude_lower_clamped")
        if amplitude > _MAXIMUM_AMPLITUDE:
            amplitude = _MAXIMUM_AMPLITUDE
            interventions.append("amplitude_upper_clamped")

        reciprocal_rate_sum = 1.0 / rise_rate + 1.0 / decline_rate
        maximum_smooth_amplitude = base.duration / (
            _MINIMUM_TURNOVER_POWER * reciprocal_rate_sum
        )
        if amplitude > maximum_smooth_amplitude:
            amplitude = maximum_smooth_amplitude
            interventions.append("amplitude_reduced_for_smooth_turnover")

        prior_gap = base_events[index - 1].gap_after if index else base.gap_after
        before = float(prior_gap) if prior_gap is not None else minimum_gap
        after = float(base.gap_after) if base.gap_after is not None else minimum_gap
        tail_limit_before = 0.45 * before
        tail_limit_after = 0.45 * after
        if not _tails_fit(
            base.duration,
            amplitude,
            rise_rate,
            decline_rate,
            tail_limit_before,
            tail_limit_after,
        ):
            lower = 1e-6
            upper = amplitude
            for _ in range(60):
                candidate = (lower + upper) / 2.0
                if _tails_fit(
                    base.duration,
                    candidate,
                    rise_rate,
                    decline_rate,
                    tail_limit_before,
                    tail_limit_after,
                ):
                    lower = candidate
                else:
                    upper = candidate
            amplitude = lower
            interventions.append("amplitude_reduced_for_tail_separation")

        power = base.duration / (amplitude * reciprocal_rate_sum)
        rise_span = amplitude * power / rise_rate
        decline_span = amplitude * power / decline_rate
        peak_jd = base.onset_jd + rise_span
        baseline_distance = ((_BASELINE_MAGNITUDE - (_THRESHOLD_MAGNITUDE - amplitude)) / amplitude) ** (
            1.0 / power
        )
        support_start = peak_jd - baseline_distance * rise_span
        support_end = peak_jd + baseline_distance * decline_span
        peak_magnitude = _THRESHOLD_MAGNITUDE - amplitude
        built.append(
            EventTruth(
                base.event_id,
                base.onset_jd,
                base.end_jd,
                base.duration,
                base.gap_after,
                peak_jd,
                peak_magnitude,
                "low_amplitude" if peak_magnitude >= 9.0 else "standard",
                rise_rate,
                decline_rate,
                power,
                support_start,
                support_end,
                base.latent_duration,
                base.latent_gap,
                tuple(interventions),
            )
        )
    return tuple(built)


def _tails_fit(duration, amplitude, rise_rate, decline_rate, before, after):
    reciprocal_rate_sum = 1.0 / rise_rate + 1.0 / decline_rate
    power = duration / (amplitude * reciprocal_rate_sum)
    rise_span = duration * decline_rate / (rise_rate + decline_rate)
    decline_span = duration * rise_rate / (rise_rate + decline_rate)
    peak = _THRESHOLD_MAGNITUDE - amplitude
    distance = ((_BASELINE_MAGNITUDE - peak) / amplitude) ** (1.0 / power)
    return rise_span * (distance - 1.0) <= before and decline_span * (distance - 1.0) <= after
