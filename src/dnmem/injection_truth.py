"""Independent synthetic event truth for extractor injection tests."""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
import hashlib
import math
import random
from statistics import NormalDist
from typing import Literal, Sequence


Mode = Literal["null", "alternative"]


@dataclass(frozen=True)
class LatentCoefficients:
    duration_persistence: float = -0.4
    duration_prior_gap: float = 0.282
    gap_persistence: float = 0.382
    partial_duration_gap: float = 0.13


@dataclass(frozen=True)
class Knot:
    jd: float
    magnitude: float


@dataclass(frozen=True)
class EventTruth:
    event_id: int
    onset_jd: float
    end_jd: float
    duration: float
    gap_after: float | None
    peak_magnitude: float
    event_type: str
    knots: tuple[Knot, ...]
    latent_duration: float | None
    latent_gap: float | None

    def magnitude_at(self, jd: float, baseline_magnitude: float = 12.2) -> float:
        if jd < self.knots[0].jd or jd > self.knots[-1].jd:
            return baseline_magnitude
        for left, right in zip(self.knots, self.knots[1:]):
            if left.jd <= jd <= right.jd:
                fraction = (jd - left.jd) / (right.jd - left.jd)
                return left.magnitude + fraction * (right.magnitude - left.magnitude)
        return baseline_magnitude

    def threshold_interval(self, threshold: float) -> tuple[float, float] | None:
        """Return first/last times at least as bright as a magnitude threshold."""
        points: list[float] = []
        for left, right in zip(self.knots, self.knots[1:]):
            left_delta = left.magnitude - threshold
            right_delta = right.magnitude - threshold
            if left_delta == 0.0:
                points.append(left.jd)
            if right_delta == 0.0:
                points.append(right.jd)
            if left_delta * right_delta < 0.0:
                fraction = -left_delta / (right_delta - left_delta)
                points.append(left.jd + fraction * (right.jd - left.jd))
        if min(knot.magnitude for knot in self.knots) > threshold or not points:
            return None
        return min(points), max(points)


@dataclass(frozen=True)
class TruthSeries:
    mode: Mode
    start_jd: float
    stop_jd: float
    seed: int
    aligned: bool
    events: tuple[EventTruth, ...]
    diagnostics: dict[str, float | int | str]
    baseline_magnitude: float = 12.2

    def evaluate(self, jds: Sequence[float]) -> tuple[float, ...]:
        """Evaluate magnitudes only; event labels are deliberately not returned."""
        starts = tuple(event.knots[0].jd for event in self.events)
        result: list[float] = []
        for jd_value in jds:
            jd = float(jd_value)
            index = bisect_right(starts, jd) - 1
            if index < 0:
                result.append(self.baseline_magnitude)
            else:
                result.append(self.events[index].magnitude_at(jd, self.baseline_magnitude))
        return tuple(result)


def generate_truth(
    duration_values: Sequence[float],
    gap_values: Sequence[float],
    start_jd: float,
    stop_jd: float,
    seed: int,
    mode: Mode = "null",
    *,
    coefficients: LatentCoefficients | None = None,
    burn_in: int = 1000,
    onset_anchors: Sequence[float] | None = None,
    calendar_warmup: float = 1000.0,
) -> TruthSeries:
    """Generate independent event truth from separated duration and gap marginals."""
    durations = _validated_marginal(duration_values, "duration_values")
    gaps = _validated_marginal(gap_values, "gap_values")
    start = float(start_jd)
    stop = float(stop_jd)
    if not math.isfinite(start) or not math.isfinite(stop) or stop <= start:
        raise ValueError("stop_jd must be finite and greater than start_jd")
    if mode not in ("null", "alternative"):
        raise ValueError("mode must be 'null' or 'alternative'")
    if burn_in < 0:
        raise ValueError("burn_in must be non-negative")
    if not math.isfinite(calendar_warmup) or calendar_warmup < 0.0:
        raise ValueError("calendar_warmup must be finite and non-negative")
    coeff = coefficients or LatentCoefficients()
    _validate_coefficients(coeff, mode)

    if onset_anchors is not None:
        timing, aligned_duration_capped_count = _aligned_timing(
            durations, gaps, onset_anchors, seed, mode, coeff, burn_in
        )
    else:
        aligned_duration_capped_count = 0
        timing = _renewal_timing(
            durations,
            gaps,
            start,
            stop,
            seed,
            mode,
            coeff,
            burn_in,
            calendar_warmup,
        )

    shape_rng = random.Random(_stream_seed(seed, "shape"))
    events = _build_events(timing, min(gaps), shape_rng)
    aligned = onset_anchors is not None
    diagnostics = _diagnostics(
        mode, aligned, events, coeff, aligned_duration_capped_count
    )
    return TruthSeries(mode, start, stop, int(seed), aligned, events, diagnostics)


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
) -> TruthSeries:
    return generate_truth(
        duration_marginal,
        gap_marginal,
        start,
        stop,
        seed,
        process,
        coefficients=coefficients,
        burn_in=burn_in,
        onset_anchors=anchors,
        calendar_warmup=calendar_warmup,
    )


def magnitudes_at(
    events: TruthSeries | Sequence[EventTruth], times: Sequence[float]
) -> tuple[float, ...]:
    if isinstance(events, TruthSeries):
        return events.evaluate(times)
    return TruthSeries("null", 0.0, 1.0, 0, False, tuple(events), {}).evaluate(times)


def truth_catalogue(
    events: TruthSeries | Sequence[EventTruth], threshold: float
) -> tuple[dict[str, int | float | str], ...]:
    records = events.events if isinstance(events, TruthSeries) else tuple(events)
    catalogue: list[dict[str, int | float | str]] = []
    for event in records:
        interval = event.threshold_interval(float(threshold))
        if interval is None:
            continue
        catalogue.append(
            {
                "id": event.event_id,
                "onset": interval[0],
                "end": interval[1],
                "peak_t": event.knots[2].jd,
                "type": "short" if interval[1] - interval[0] < 12.0 else "long",
            }
        )
    return tuple(catalogue)


def _validated_marginal(values: Sequence[float], name: str) -> tuple[float, ...]:
    result = tuple(sorted(float(value) for value in values))
    if len(result) < 2:
        raise ValueError(f"{name} must contain at least two values")
    if any(not math.isfinite(value) or value <= 0.0 for value in result):
        raise ValueError(f"{name} must contain only finite positive values")
    return result


def _validate_coefficients(coeff: LatentCoefficients, mode: Mode) -> None:
    values = (
        coeff.duration_persistence,
        coeff.duration_prior_gap,
        coeff.gap_persistence,
        coeff.partial_duration_gap,
    )
    if any(not math.isfinite(value) or abs(value) >= 1.0 for value in values):
        raise ValueError("all latent coefficients must be finite and strictly between -1 and 1")
    if mode != "alternative":
        return
    _alternative_parameters(coeff)


def _stream_seed(seed: int, stream: str) -> int:
    digest = hashlib.sha256(f"{int(seed)}:{stream}".encode("ascii")).digest()
    return int.from_bytes(digest[:8], "big")


def _empirical_quantile(values: tuple[float, ...], latent: float) -> float:
    probability = NormalDist().cdf(latent)
    position = probability * (len(values) - 1)
    lower = int(math.floor(position))
    upper = min(lower + 1, len(values) - 1)
    fraction = position - lower
    return values[lower] + fraction * (values[upper] - values[lower])


def _alternative_parameters(coeff: LatentCoefficients) -> tuple[float, float, float, float]:
    a = coeff.duration_persistence
    d_prior_q = coeff.duration_prior_gap
    c = coeff.gap_persistence
    partial = coeff.partial_duration_gap
    r = d_prior_q * c + partial * math.sqrt((1.0 - d_prior_q**2) * (1.0 - c**2))
    b = d_prior_q - a * r
    variance = 1.0 - a * a - b * b - 2.0 * a * b * r
    if variance <= 0.0:
        raise ValueError("latent coefficients do not define a positive duration innovation variance")
    sd_duration = math.sqrt(variance)
    theta = (r - c * d_prior_q) / (sd_duration * math.sqrt(1.0 - c * c))
    if abs(theta) > 1.0 + 1e-12:
        raise ValueError("latent coefficients imply an invalid innovation correlation")
    theta = max(-1.0, min(1.0, theta))
    return r, b, sd_duration, theta


def _latent_draws(
    count: int,
    rng: random.Random,
    mode: Literal["null", "alternative"],
    coeff: LatentCoefficients,
    state: tuple[float, float],
) -> tuple[list[tuple[float, float]], tuple[float, float]]:
    duration_previous, gap_previous = state
    draws: list[tuple[float, float]] = []
    if mode == "alternative":
        _, b, sd_duration, theta = _alternative_parameters(coeff)
    for _ in range(count):
        epsilon_duration = rng.gauss(0.0, 1.0)
        epsilon_gap = rng.gauss(0.0, 1.0)
        if mode == "null":
            duration = (
                coeff.duration_persistence * duration_previous
                + math.sqrt(1.0 - coeff.duration_persistence**2) * epsilon_duration
            )
            gap = epsilon_gap
        else:
            duration = (
                coeff.duration_persistence * duration_previous
                + b * gap_previous
                + sd_duration * epsilon_duration
            )
            gap = (
                coeff.gap_persistence * gap_previous
                + math.sqrt(1.0 - coeff.gap_persistence**2)
                * (theta * epsilon_duration + math.sqrt(1.0 - theta**2) * epsilon_gap)
            )
        draws.append((duration, gap))
        duration_previous, gap_previous = duration, gap
    return draws, (duration_previous, gap_previous)


def _renewal_timing(
    durations: tuple[float, ...],
    gaps: tuple[float, ...],
    start: float,
    stop: float,
    seed: int,
    mode: Literal["null", "alternative"],
    coeff: LatentCoefficients,
    burn_in: int,
    calendar_warmup: float,
) -> list[tuple[float, float, float, float, float, float]]:
    rng = random.Random(_stream_seed(seed, "latent"))
    state = (0.0, 0.0)
    if burn_in:
        _, state = _latent_draws(burn_in, rng, mode, coeff, state)
    first, state = _latent_draws(1, rng, mode, coeff, state)
    latent_duration, latent_gap = first[0]
    duration = _empirical_quantile(durations, latent_duration)
    gap = _empirical_quantile(gaps, latent_gap)
    phase_rng = random.Random(_stream_seed(seed, "phase"))
    phase = phase_rng.random()
    if phase == 0.0:
        phase = 0.5
    onset = start - calendar_warmup - phase * (duration + gap)
    retain_after = start - (max(durations) + max(gaps))
    rows: list[tuple[float, float, float, float, float, float]] = []
    while True:
        end = onset + duration
        if onset >= retain_after:
            rows.append((onset, end, duration, gap, latent_duration, latent_gap))
        if onset > stop:
            break
        onset = end + gap
        draw, state = _latent_draws(1, rng, mode, coeff, state)
        latent_duration, latent_gap = draw[0]
        duration = _empirical_quantile(durations, latent_duration)
        gap = _empirical_quantile(gaps, latent_gap)
    return rows


def _aligned_timing(
    durations: tuple[float, ...],
    gaps: tuple[float, ...],
    onset_anchors: Sequence[float],
    seed: int,
    mode: Mode,
    coeff: LatentCoefficients,
    burn_in: int,
) -> tuple[list[tuple[float, float, float, float | None, float, float]], int]:
    anchors = tuple(float(anchor) for anchor in onset_anchors)
    if not anchors or any(not math.isfinite(anchor) for anchor in anchors):
        raise ValueError("onset_anchors must contain finite values")
    if any(right <= left for left, right in zip(anchors, anchors[1:])):
        raise ValueError("onset_anchors must be strictly increasing")
    rng = random.Random(_stream_seed(seed, "latent"))
    state = (0.0, 0.0)
    if burn_in:
        _, state = _latent_draws(burn_in, rng, mode, coeff, state)
    latent_draws, _ = _latent_draws(len(anchors), rng, mode, coeff, state)
    minimum_gap = min(5.0, min(gaps))
    capped_count = 0
    rows: list[tuple[float, float, float, float | None, float, float]] = []
    for index, (onset, latent) in enumerate(zip(anchors, latent_draws)):
        latent_duration, latent_gap = latent
        duration = _empirical_quantile(durations, latent_duration)
        gap: float | None = None
        if index + 1 < len(anchors):
            cycle = anchors[index + 1] - onset
            maximum_duration = cycle - minimum_gap
            if maximum_duration <= 0.0:
                raise ValueError("anchor spacing must exceed the minimum input gap")
            if duration > maximum_duration:
                duration = maximum_duration
                capped_count += 1
            gap = cycle - duration
        rows.append((onset, onset + duration, duration, gap, latent_duration, latent_gap))
    return rows, capped_count


def _build_events(
    timing: Sequence[tuple[float, float, float, float | None, float | None, float | None]],
    minimum_gap: float,
    rng: random.Random,
) -> tuple[EventTruth, ...]:
    events: list[EventTruth] = []
    for index, (onset, end, duration, gap, latent_duration, latent_gap) in enumerate(timing):
        previous_gap = timing[index - 1][3] if index else gap
        flank_before_gap = previous_gap if previous_gap is not None else minimum_gap
        flank_after_gap = gap if gap is not None else minimum_gap
        pre_duration = min(rng.uniform(0.5, 2.0), 0.45 * flank_before_gap)
        post_duration = min(rng.uniform(0.5, 2.0), 0.45 * flank_after_gap)
        rise_draw = rng.uniform(2.0, 4.0) if rng.random() < 0.15 else rng.uniform(0.5, 1.5)
        rise_duration = min(rise_draw, 0.4 * duration)
        peak = rng.uniform(9.0, 9.5) if rng.random() < 0.05 else rng.uniform(8.0, 8.8)
        event_type = "low_amplitude" if peak >= 9.0 else "standard"
        peak_time = onset + rise_duration
        decline_start = onset + max(0.65 * duration, rise_duration)
        knots = (
            Knot(onset - pre_duration, 12.2),
            Knot(onset, 10.0),
            Knot(peak_time, peak),
            Knot(decline_start, peak),
            Knot(end, 10.0),
            Knot(end + post_duration, 12.2),
        )
        events.append(
            EventTruth(
                index,
                onset,
                end,
                duration,
                gap,
                peak,
                event_type,
                knots,
                latent_duration,
                latent_gap,
            )
        )
    return tuple(events)


def _pearson(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        return math.nan
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    cross = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right))
    left_ss = sum((x - left_mean) ** 2 for x in left)
    right_ss = sum((y - right_mean) ** 2 for y in right)
    if left_ss == 0.0 or right_ss == 0.0:
        return math.nan
    return cross / math.sqrt(left_ss * right_ss)


def _partial_correlation(x: Sequence[float], y: Sequence[float], z: Sequence[float]) -> float:
    xy = _pearson(x, y)
    xz = _pearson(x, z)
    yz = _pearson(y, z)
    denominator = math.sqrt((1.0 - xz * xz) * (1.0 - yz * yz))
    if denominator == 0.0 or any(math.isnan(value) for value in (xy, xz, yz)):
        return math.nan
    return (xy - xz * yz) / denominator


def _diagnostics(
    mode: Mode,
    aligned: bool,
    events: Sequence[EventTruth],
    coeff: LatentCoefficients,
    aligned_duration_capped_count: int,
) -> dict[str, float | int | str]:
    duration = [event.duration for event in events]
    valid = [event for event in events if event.gap_after is not None]
    gap = [float(event.gap_after) for event in valid]
    paired_duration = [event.duration for event in valid]
    current_duration = duration[1 : len(gap)]
    current_gap = gap[1:]
    prior_gap = gap[:-1]
    diagnostics: dict[str, float | int | str] = {
        "mode": mode,
        "phase": "aligned" if aligned else "random",
        "independent_null": mode == "null" and not aligned,
        "aligned_duration_capped_count": aligned_duration_capped_count,
        "n_events": len(events),
        "raw_duration_gap_correlation": _pearson(paired_duration, gap),
        "raw_gap_serial_correlation": _pearson(gap[1:], gap[:-1]),
        "raw_duration_prior_gap_correlation": _pearson(current_duration, prior_gap),
        "raw_duration_gap_partial_prior_gap": _partial_correlation(
            current_duration, current_gap, prior_gap
        ),
        "raw_duration_serial_correlation": _pearson(duration[1:], duration[:-1]),
        "latent_duration_persistence": coeff.duration_persistence,
        "initialization": (
            "fixed calendar warm-up before the retained random-phase window; "
            "not an exact equilibrium renewal sample"
            if not aligned
            else "fixed supplied onset anchors"
        ),
    }
    if mode == "alternative" and not aligned:
        latent_r, _, _, _ = _alternative_parameters(coeff)
        diagnostics.update(
            {
                "latent_duration_prior_gap_target": coeff.duration_prior_gap,
                "latent_gap_serial_target": coeff.gap_persistence,
                "latent_duration_gap_partial_target": coeff.partial_duration_gap,
                "latent_duration_gap_correlation_target": latent_r,
            }
        )
    elif mode == "null" and not aligned:
        diagnostics["latent_duration_gap_correlation_target"] = 0.0
        diagnostics["latent_gap_serial_target"] = 0.0
    elif aligned:
        diagnostics["aligned_warning"] = "realized gap equals anchor cycle minus duration; not an independent null"
    return diagnostics
