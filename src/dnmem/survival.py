"""Lognormal waiting-time probabilities for the *specified* simple distribution.

These helpers do not integrate uncertain endpoints, missed events, measurement
error or latent activity. They are not a complete observational likelihood.
"""

from __future__ import annotations

import math


def _check(mu: float, sigma: float) -> None:
    if not math.isfinite(mu) or not math.isfinite(sigma) or sigma <= 0:
        raise ValueError("mu must be finite and sigma finite and positive")


def lognormal_cdf(t: float, mu: float, sigma: float) -> float:
    _check(mu, sigma)
    if math.isnan(t):
        raise ValueError("time cannot be NaN")
    if t <= 0:
        return 0.0
    return 0.5 * math.erfc(-(math.log(t) - mu) / (sigma * math.sqrt(2)))


def lognormal_survival(t: float, mu: float, sigma: float) -> float:
    _check(mu, sigma)
    if math.isnan(t):
        raise ValueError("time cannot be NaN")
    if t <= 0:
        return 1.0
    return 0.5 * math.erfc((math.log(t) - mu) / (sigma * math.sqrt(2)))


def lognormal_logpdf(t: float, mu: float, sigma: float) -> float:
    _check(mu, sigma)
    if not math.isfinite(t) or t <= 0:
        raise ValueError("an exact waiting time must be finite and positive")
    z = (math.log(t) - mu) / sigma
    return -math.log(t) - math.log(sigma) - 0.5 * math.log(2 * math.pi) - z * z / 2


def interval_probability(lower: float, upper: float, mu: float, sigma: float) -> float:
    """P(lower < Q <= upper); +inf upper gives right-censor survival.

    Q is anchored to a known end. This is not the likelihood for an arbitrary
    observation-free interval that could contain multiple unobserved outbursts.
    """
    _check(mu, sigma)
    if not math.isfinite(lower) or lower < 0 or math.isnan(upper) or upper <= lower:
        raise ValueError("require finite 0 <= lower < upper (upper may be +inf)")
    if lower > 0 and math.log(lower) >= mu:
        prob = lognormal_survival(lower, mu, sigma) - lognormal_survival(upper, mu, sigma)
    else:
        prob = lognormal_cdf(upper, mu, sigma) - lognormal_cdf(lower, mu, sigma)
    return max(0.0, prob)


def conditional_event_probability(age: float, horizon: float, mu: float, sigma: float) -> float:
    """P(Q <= age+horizon | Q > age), assuming known continuous survival."""
    _check(mu, sigma)
    if not all(math.isfinite(v) and v >= 0 for v in (age, horizon)):
        raise ValueError("age and horizon must be finite and nonnegative")
    if horizon == 0:
        return 0.0
    upper = age + horizon
    if not math.isfinite(upper) or upper == age:
        raise ValueError("age plus horizon exceeds supported floating-point resolution")
    denom = lognormal_survival(age, mu, sigma)
    if denom == 0:
        raise ValueError("conditioning survival underflow; use a stable log-survival implementation")
    return min(1.0, max(0.0, interval_probability(age, upper, mu, sigma) / denom))
