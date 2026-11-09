"""R2 working interval contrasts and conditional deterministic score bounds.

The fixed-cutoff mixed functional scores density when T <= C and survival when
T > C. It is distinct from v4's lower-bound-backoff observation policy and from
an unknown event's unconditional point score. Neither helper establishes CAR,
containment, event completeness, or a valid latent risk set.
"""

from __future__ import annotations

import math

from scipy.special import log_ndtr


def _clock(clock):
    try:
        values = tuple(float(getattr(clock, key)) for key in ("anchor", "issue", "mu", "sigma"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError("clock must supply finite anchor, issue, mu and sigma") from exc
    if not all(math.isfinite(value) for value in values) or values[3] <= 0 or values[0] > values[1]:
        raise ValueError("invalid clock parameters or anchor after issue")
    if not callable(getattr(clock, "log_density", None)) or not callable(getattr(clock, "log_survival", None)):
        raise ValueError("clock must supply conditional log_density and log_survival")
    at_issue = float(clock.log_survival(values[1]))
    if not math.isfinite(at_issue) or abs(at_issue) > 1e-12:
        raise ValueError("clock log_survival must already condition on survival to issue")
    return values


def _pair(baseline, duration):
    left, right = _clock(baseline), _clock(duration)
    if left[:2] != right[:2]:
        raise ValueError("paired clocks must have exactly the same anchor and issue")
    return left, right


def _window(lower, upper, issue):
    if lower is None or upper is None:
        return {"status": "missing_window"}
    try:
        lo, hi = float(lower), float(upper)
    except (TypeError, ValueError):
        return {"status": "invalid_window"}
    if not math.isfinite(lo) or not math.isfinite(hi):
        return {"status": "nonfinite_window", "finite_latent_point_bounds_supported": False}
    if lo >= hi:
        return {"status": "reversed_window"}
    if hi <= issue:
        return {"status": "overtaken"}
    if lo <= issue:
        return {"status": "ambiguous_survival"}
    return {"status": "usable", "onset_lo": lo, "onset_hi": hi}


def _cutoff(cutoff, issue):
    if cutoff is None:
        return {"status": "missing_cutoff"}
    try:
        value = float(cutoff)
    except (TypeError, ValueError):
        return {"status": "invalid_cutoff"}
    if not math.isfinite(value):
        return {"status": "nonfinite_cutoff"}
    if value < issue:
        return {"status": "cutoff_before_issue"}
    return {"status": "usable", "cutoff": value}


def route_compatibility_window(lower, upper, issue, cutoff):
    """Route a finite working set using the prospective v4 backoff policy."""
    issue = float(issue)
    if not math.isfinite(issue):
        raise ValueError("issue must be finite")
    window, stop = _window(lower, upper, issue), _cutoff(cutoff, issue)
    if window["status"] != "usable":
        return window
    if stop["status"] != "usable":
        return stop
    lo, hi, end = window["onset_lo"], window["onset_hi"], stop["cutoff"]
    row = {**window, **stop, "policy": "v4_working_set_backoff", "censor_backoff": False,
           "censor_backoff_days": 0.0}
    if hi <= end:
        return {**row, "kind": "interval", "censor_at": None}
    backoff = lo < end
    return {**row, "kind": "right_censored", "censor_at": lo if backoff else end,
            "censor_backoff": backoff, "censor_backoff_days": end - lo if backoff else 0.0}


def _normal_log_mass(lower, upper):
    if not lower < upper:
        raise ValueError("normal interval cannot be numerically resolved")
    if lower >= 0:
        large, small, branch = float(log_ndtr(-lower)), float(log_ndtr(-upper)), "survival"
    else:
        large, small, branch = float(log_ndtr(upper)), float(log_ndtr(lower)), "cdf"
    if not math.isfinite(large) or small >= large:
        raise ValueError("normal interval probability cannot be numerically resolved")
    value = large if small == -math.inf else large + math.log(-math.expm1(small - large))
    if not math.isfinite(value):
        raise ValueError("normal interval mass is nonfinite")
    return value, branch


def interval_log_mass(clock, lower, upper):
    """Stable conditional lognormal interval mass, with explicit unsupported states."""
    anchor, issue, mu, sigma = _clock(clock)
    window = _window(lower, upper, issue)
    if window["status"] != "usable":
        return window
    try:
        lo = (math.log(window["onset_lo"] - anchor) - mu) / sigma
        hi = (math.log(window["onset_hi"] - anchor) - mu) / sigma
        if not math.isfinite(lo) or not math.isfinite(hi):
            raise ValueError("normal interval support is nonfinite")
        numerator, branch = _normal_log_mass(lo, hi)
        age = issue - anchor
        denominator = 0.0 if age <= 0 else float(log_ndtr(-(math.log(age) - mu) / sigma))
        value = numerator - denominator
        if not math.isfinite(value) or value > 0:
            raise ValueError("invalid conditional interval log mass")
    except (ValueError, OverflowError, ArithmeticError) as exc:
        return {**window, "status": "numerical_failure", "message": str(exc)}
    return {**window, "log_mass": value,
            "numerical": {"tail_branch": branch, "lower_z": lo, "upper_z": hi,
                          "unconditional_log_mass": numerator,
                          "log_survival_at_issue": denominator, "survival_conditioned_once": True}}


def right_censored_contrast(baseline, duration, cutoff):
    """Contrast conditional survival probabilities, not unknown point densities."""
    left, _ = _pair(baseline, duration)
    stop = _cutoff(cutoff, left[1])
    if stop["status"] != "usable":
        return stop
    try:
        scores = [float(clock.log_survival(stop["cutoff"])) for clock in (baseline, duration)]
        gain = scores[1] - scores[0]
        if not all(math.isfinite(value) for value in (*scores, gain)):
            raise ValueError("nonfinite survival score")
    except (ValueError, OverflowError, ArithmeticError) as exc:
        return {**stop, "status": "numerical_failure", "message": str(exc)}
    return {**stop, "kind": "right_censored", "censor_at": stop["cutoff"],
            "gain": gain, "scores": {"baseline": scores[0], "duration": scores[1]},
            "bounds_latent_point_gain": False,
            "assumed_survival_to": stop["cutoff"],
            "assumption": "the next qualifying latent onset is after censor_at"}


def working_interval_contrast(baseline, duration, lower, upper, cutoff):
    """Paired working interval probability under the v4 cutoff/backoff policy."""
    left, _ = _pair(baseline, duration)
    route = route_compatibility_window(lower, upper, left[1], cutoff)
    if route["status"] != "usable":
        return route
    if route["kind"] == "right_censored":
        scored = right_censored_contrast(baseline, duration, route["censor_at"])
        return {**scored, **route, "status": scored["status"],
                "bounds_latent_point_gain": False, "propriety_established": False}
    results = [interval_log_mass(clock, lower, upper) for clock in (baseline, duration)]
    if any(row["status"] != "usable" for row in results):
        return {**route, "status": "numerical_failure", "numerical": results}
    scores = [row["log_mass"] for row in results]
    return {**route, "gain": scores[1] - scores[0],
            "scores": {"baseline": scores[0], "duration": scores[1]},
            "numerical": {"baseline": results[0]["numerical"], "duration": results[1]["numerical"]},
            "propriety_established": False}


def latent_point_gain_bounds(baseline, duration, lower, upper):
    """Inf/sup of the finite-window point-density contrast, conditional on containment."""
    left, right = _pair(baseline, duration)
    window = _window(lower, upper, left[1])
    if window["status"] != "usable":
        return window
    anchor, _, mu_b, sigma_b = left
    mu_d, sigma_d = right[2:]
    try:
        lo, hi = math.log(window["onset_lo"] - anchor), math.log(window["onset_hi"] - anchor)
        inv_b, inv_d = 1 / sigma_b**2, 1 / sigma_d**2
        quadratic, linear = .5 * (inv_b - inv_d), mu_d * inv_d - mu_b * inv_b
        if not math.isfinite(quadratic) or not math.isfinite(linear):
            raise ValueError("log-ratio coefficients are nonfinite")
        candidates = [(window["onset_lo"], "lower_limit", False),
                      (window["onset_hi"], "upper", True)]
        stationary = -linear / (2 * quadratic) if quadratic else None
        if stationary is not None and not math.isfinite(stationary):
            raise ValueError("stationary log-wait cannot be numerically resolved")
        if stationary is not None and lo < stationary < hi:
            candidates.append((anchor + math.exp(stationary), "stationary", True))
        scored = []
        for time, location, attained in candidates:
            value = float(duration.log_density(time)) - float(baseline.log_density(time))
            if not math.isfinite(value):
                raise ValueError("nonfinite point-density contrast")
            scored.append({"time": time, "location": location, "attained": attained, "gain": value})
    except (ValueError, OverflowError, ArithmeticError) as exc:
        return {**window, "status": "numerical_failure", "message": str(exc)}
    return {**window, "policy": "finite_window_latent_point_bounds",
            "lower": min(row["gain"] for row in scored), "upper": max(row["gain"] for row in scored),
            "bounds_latent_point_gain": True,
            "numerical": {"log_wait_quadratic": quadratic, "log_wait_linear": linear,
                          "stationary_log_wait": stationary, "candidates": scored},
            "assumptions": ["valid next-event association and risk set", "latent onset contained in window"]}


def mixed_score_bounds(baseline, duration, lower, upper, cutoff):
    """Bounds for density if T <= fixed C, survival at C otherwise.

    A straddle is a union of its possible event-density scores and survival
    score at the original C. It never substitutes v4's lower-bound cutoff.
    """
    left, _ = _pair(baseline, duration)
    window, stop = _window(lower, upper, left[1]), _cutoff(cutoff, left[1])
    if window["status"] != "usable":
        return window
    if stop["status"] != "usable":
        return stop
    lo, hi, end = window["onset_lo"], window["onset_hi"], stop["cutoff"]
    base = {**window, **stop, "policy": "fixed_cutoff_mixed_density_survival",
            "functional": "event density when T<=C; survival at C when T>C",
            "bounds_latent_point_gain": False, "propriety_established": False,
            "assumptions": ["valid next-event association and risk set", "latent onset contained in window"]}
    if hi <= end:
        event = latent_point_gain_bounds(baseline, duration, lo, hi)
        if event["status"] != "usable":
            return {**base, "status": event["status"], "event_bounds": event}
        return {**base, "kind": "event", "lower": event["lower"], "upper": event["upper"],
                "event_bounds": event, "survival_gain": None}
    survival = right_censored_contrast(baseline, duration, end)
    if survival["status"] != "usable":
        return {**base, "status": survival["status"], "survival": survival}
    if lo >= end:
        return {**base, "kind": "right_censored", "lower": survival["gain"], "upper": survival["gain"],
                "event_bounds": None, "survival_gain": survival["gain"]}
    event = latent_point_gain_bounds(baseline, duration, lo, end)
    if event["status"] != "usable":
        return {**base, "status": event["status"], "event_bounds": event}
    return {**base, "kind": "straddle", "lower": min(event["lower"], survival["gain"]),
            "upper": max(event["upper"], survival["gain"]), "event_bounds": event,
            "survival_gain": survival["gain"]}
