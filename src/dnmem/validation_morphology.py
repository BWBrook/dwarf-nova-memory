"""Independent morphology measurements and qualification gates for A04d v2."""

from __future__ import annotations

import math
from statistics import mean, median
from typing import Any, Iterable, Sequence

from dnmem.extract import visits, x1_vote_episodes


J1910 = 2418672.5
J1960 = 2436934.5


def _theil_sen(points: Sequence[tuple[float, float]]) -> tuple[float, float] | None:
    if len(points) < 4 or max(x for x, _ in points) - min(x for x, _ in points) < 0.4:
        return None
    slopes = [
        (y2 - y1) / (x2 - x1)
        for index, (x1, y1) in enumerate(points)
        for x2, y2 in points[index + 1 :]
        if x2 - x1 > 0.05
    ]
    if len(slopes) < 3:
        return None
    slope = median(slopes)
    intercept = median(y - slope * x for x, y in points)
    residual_sd = 1.4826 * median(abs(y - intercept - slope * x) for x, y in points)
    return slope, residual_sd


def records(rows: Iterable[dict[str, Any]], threshold: float = 10.0) -> list[dict[str, Any]]:
    """Apply the A04d measurement operator to eligible 1910--1959 X1 episodes."""
    source_rows = list(rows)
    threshold = float(threshold)
    usable_visits = [visit for visit in visits(source_rows, threshold) if visit["value"] is not None]
    output = []
    for episode in x1_vote_episodes(source_rows, threshold=threshold):
        boundaries = ("onset_lo", "onset_hi", "end_lo", "end_hi")
        if (
            not episode["confirmed_event"]
            or episode["gap_split"]
            or any(episode[key] is None for key in boundaries)
            or not J1910 <= episode["peak_t"] < J1960
        ):
            continue
        onset = [
            (visit["t"] - episode["onset_lo"], visit["value"])
            for visit in usable_visits
            if episode["onset_lo"] - 1 <= visit["t"] <= episode["onset_hi"] + 1
            and visit["t"] < episode["peak_t"]
            and abs(visit["value"] - threshold) <= 1.0
        ]
        end = [
            (visit["t"] - episode["end_lo"], visit["value"])
            for visit in usable_visits
            if episode["end_lo"] - 2 <= visit["t"] <= episode["end_hi"] + 2
            and visit["t"] > episode["peak_t"]
            and abs(visit["value"] - threshold) <= 1.0
        ]
        wide = [
            (visit["t"] - episode["end_lo"], visit["value"])
            for visit in usable_visits
            if episode["end_lo"] - 3 <= visit["t"] <= episode["end_hi"] + 3
            and visit["t"] > episode["peak_t"]
        ]
        output.append(
            {
                "duration": (
                    episode["end_lo"]
                    + episode["end_hi"]
                    - episode["onset_lo"]
                    - episode["onset_hi"]
                )
                / 2,
                "onset": _theil_sen(onset),
                "end": _theil_sen(end),
                "n_onset": len(onset),
                "n_end": len(end),
                "above": _theil_sen(
                    [point for point in wide if threshold - 1 <= point[1] <= threshold]
                ),
                "below": _theil_sen(
                    [point for point in wide if threshold < point[1] <= threshold + 1]
                ),
            }
        )
    return output


def _quantiles(values: Iterable[float]) -> dict[str, int | float]:
    ordered = sorted(values)
    if not ordered:
        return {}
    result = {
        f"q{int(100 * fraction)}": round(
            ordered[int(fraction * (len(ordered) - 1))], 3
        )
        for fraction in (0.1, 0.25, 0.5, 0.75, 0.9)
    }
    result["n"] = len(ordered)
    return result


def _average_ranks(values: Sequence[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        stop = start + 1
        while stop < len(order) and values[order[stop]] == values[order[start]]:
            stop += 1
        average_rank = (start + stop - 1) / 2.0
        for position in order[start:stop]:
            ranks[position] = average_rank
        start = stop
    return ranks


def _spearman(left: Sequence[float], right: Sequence[float]) -> tuple[float | None, str]:
    if len(left) != len(right) or len(left) < 2:
        return None, "insufficient"
    left_ranks = _average_ranks(left)
    right_ranks = _average_ranks(right)
    left_mean = mean(left_ranks)
    right_mean = mean(right_ranks)
    left_ss = sum((value - left_mean) ** 2 for value in left_ranks)
    right_ss = sum((value - right_mean) ** 2 for value in right_ranks)
    if left_ss == 0.0 or right_ss == 0.0:
        return None, "constant"
    correlation = sum(
        (x - left_mean) * (y - right_mean)
        for x, y in zip(left_ranks, right_ranks)
    ) / math.sqrt(left_ss * right_ss)
    return correlation, "ok"


def _fit_diagnostic(records_: Sequence[dict[str, Any]], key: str, sign: int) -> dict[str, Any]:
    fitted = [record[key] for record in records_ if record[key] is not None]
    positive = [fit for fit in fitted if fit[0] * sign > 0]
    return {
        "fit_count": len(fitted),
        "positive_fit_count": len(positive),
        "wrong_sign_fit_count": len(fitted) - len(positive),
        "positive_fit_fraction": len(positive) / len(records_) if records_ else None,
    }


def _median_or_none(values: Iterable[float]) -> float | None:
    values = list(values)
    return round(median(values), 3) if values else None


def summary(records_: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Summarize morphology records with the committed A04d keys and diagnostics."""
    records_ = list(records_)
    output: dict[str, Any] = {"episodes": len(records_)}
    fit_diagnostics = {}
    for side, sign in (("onset", -1), ("end", 1)):
        fits = [record[side] for record in records_ if record[side] and record[side][0] * sign > 0]
        output[side] = {
            "abs_slope_mag_per_d": _quantiles(abs(fit[0]) for fit in fits),
            "residual_sd_mag": _quantiles(fit[1] for fit in fits),
            "estimates_in_window": _quantiles(record["n_" + side] for record in records_),
        }
        fit_diagnostics[side] = _fit_diagnostic(records_, side, sign)

    pairs = [
        (record["duration"], record["end"][0])
        for record in records_
        if record["end"] and record["end"][0] > 0
    ]
    correlation, correlation_status = _spearman(
        [pair[0] for pair in pairs], [pair[1] for pair in pairs]
    )
    output["end_slope_vs_duration_spearman"] = (
        round(correlation, 3) if correlation is not None else None
    )
    output["end_slope_vs_duration_n"] = len(pairs)
    output["end_slope_vs_duration_status"] = correlation_status
    output["end_slope_median_short_lt11d"] = _median_or_none(
        slope for duration, slope in pairs if duration < 11
    )
    output["end_slope_median_long_ge11d"] = _median_or_none(
        slope for duration, slope in pairs if duration >= 11
    )

    for part in ("above", "below"):
        fits = [record[part] for record in records_ if record[part] and record[part][0] > 0]
        output[f"decline_slope_{part}_threshold"] = _quantiles(fit[0] for fit in fits)
        fit_diagnostics[f"{part}_threshold"] = _fit_diagnostic(records_, part, 1)
    output["fit_diagnostics"] = fit_diagnostics
    return output


def _number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _nested(summary_: dict[str, Any], *keys: str) -> float | None:
    value: Any = summary_
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return _number(value)


def _positive_fit_fraction(summary_: dict[str, Any], side: str) -> float | None:
    diagnostic = summary_.get("fit_diagnostics", {}).get(f"{side}_threshold", {})
    fraction = _number(diagnostic.get("positive_fit_fraction"))
    if fraction is not None:
        return fraction
    count = _nested(summary_, f"decline_slope_{side}_threshold", "n")
    episodes = _number(summary_.get("episodes"))
    if count is None or episodes is None or episodes <= 0:
        return None
    return count / episodes


def _relative_comparison(real: float | None, synthetic: float | None, tolerance: float) -> dict[str, Any]:
    passed = real is not None and synthetic is not None and real > 0 and synthetic > 0
    relative_error = None
    if passed:
        relative_error = abs(synthetic - real) / real
        passed = relative_error <= tolerance
    return {
        "passed": passed,
        "real": real,
        "synthetic": synthetic,
        "relative_error": relative_error,
        "tolerance": tolerance,
    }


def qualify(real_summary: dict[str, Any], synthetic_summary: dict[str, Any]) -> dict[str, Any]:
    """Apply the prespecified magnitude-10 morphology qualification gates."""
    comparisons: dict[str, dict[str, Any]] = {}
    comparisons["onset_slope_median"] = _relative_comparison(
        _nested(real_summary, "onset", "abs_slope_mag_per_d", "q50"),
        _nested(synthetic_summary, "onset", "abs_slope_mag_per_d", "q50"),
        0.15,
    )
    comparisons["end_slope_median"] = _relative_comparison(
        _nested(real_summary, "end", "abs_slope_mag_per_d", "q50"),
        _nested(synthetic_summary, "end", "abs_slope_mag_per_d", "q50"),
        0.15,
    )
    comparisons["end_residual_sd_median"] = _relative_comparison(
        _nested(real_summary, "end", "residual_sd_mag", "q50"),
        _nested(synthetic_summary, "end", "residual_sd_mag", "q50"),
        0.15,
    )

    real_rho = _number(real_summary.get("end_slope_vs_duration_spearman"))
    synthetic_rho = _number(synthetic_summary.get("end_slope_vs_duration_spearman"))
    rho_difference = (
        abs(synthetic_rho - real_rho)
        if real_rho is not None and synthetic_rho is not None
        else None
    )
    comparisons["end_slope_duration_spearman"] = {
        "passed": rho_difference is not None and rho_difference <= 0.15,
        "real": real_rho,
        "synthetic": synthetic_rho,
        "absolute_difference": rho_difference,
        "tolerance": 0.15,
    }

    real_above = _nested(real_summary, "decline_slope_above_threshold", "q50")
    real_below = _nested(real_summary, "decline_slope_below_threshold", "q50")
    synthetic_above = _nested(synthetic_summary, "decline_slope_above_threshold", "q50")
    synthetic_below = _nested(synthetic_summary, "decline_slope_below_threshold", "q50")
    valid_ratio = all(
        value is not None and value > 0
        for value in (real_above, real_below, synthetic_above, synthetic_below)
    )
    real_ratio = real_below / real_above if valid_ratio else None
    synthetic_ratio = synthetic_below / synthetic_above if valid_ratio else None
    ratio_factor = (
        max(synthetic_ratio / real_ratio, real_ratio / synthetic_ratio)
        if valid_ratio and real_ratio > 0 and synthetic_ratio > 0
        else None
    )
    comparisons["decline_side_slope_ratio"] = {
        "passed": ratio_factor is not None and ratio_factor <= 1.5,
        "real": real_ratio,
        "synthetic": synthetic_ratio,
        "factor": ratio_factor,
        "maximum_factor": 1.5,
    }

    for side in ("above", "below"):
        real_fraction = _positive_fit_fraction(real_summary, side)
        synthetic_fraction = _positive_fit_fraction(synthetic_summary, side)
        difference = (
            abs(synthetic_fraction - real_fraction)
            if real_fraction is not None and synthetic_fraction is not None
            else None
        )
        comparisons[f"{side}_positive_fit_fraction"] = {
            "passed": difference is not None and difference <= 0.15,
            "real": real_fraction,
            "synthetic": synthetic_fraction,
            "absolute_difference": difference,
            "tolerance": 0.15,
        }

    gates = {name: comparison["passed"] for name, comparison in comparisons.items()}
    return {"passed": all(gates.values()), "gates": gates, "comparisons": comparisons}


__all__ = ["records", "summary", "qualify"]
