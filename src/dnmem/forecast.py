"""Two plug-in lognormal oracle baselines, fitted on earlier complete cycles.

Only M0 and M1 are implemented. No hierarchical, latent-state, censoring-aware
fit or parameter-uncertainty integration is claimed. M1 uses duration known at
the true end in the synthetic experiment. Real endpoints need confirmation.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import NormalDist, correlation, fmean

from .simulate import Event
from .survival import lognormal_cdf, lognormal_logpdf


@dataclass(frozen=True)
class LognormalModel:
    name: str
    intercept: float
    slope: float
    training_log_duration_mean: float
    sigma: float

    def mu(self, duration: float) -> float:
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError("duration must be positive and finite")
        return self.intercept + self.slope * (math.log(duration) - self.training_log_duration_mean)


def fit_model(training: list[Event], use_duration: bool = False) -> LognormalModel:
    if len(training) < 4:
        raise ValueError("need at least four complete training cycles")
    if any(not all(math.isfinite(v) and v > 0 for v in (e.duration, e.next_quiescent_gap)) for e in training):
        raise ValueError("training durations and gaps must be positive and finite")
    x = [math.log(e.duration) for e in training]
    y = [math.log(e.next_quiescent_gap) for e in training]
    xm, ym = fmean(x), fmean(y)
    ssx = sum((v - xm) ** 2 for v in x)
    if use_duration and ssx < 1e-12:
        raise ValueError("duration predictor has no usable variation")
    slope = sum((a - xm) * (b - ym) for a, b in zip(x, y)) / ssx if use_duration else 0.0
    # Gaussian maximum likelihood residual scale. Forecasts omit parameter uncertainty.
    sigma = math.sqrt(sum((b - ym - slope * (a - xm)) ** 2 for a, b in zip(x, y)) / len(x))
    if sigma < 1e-12:
        raise ValueError("degenerate residual scale; distribution cannot be fitted")
    return LognormalModel("M1_duration" if use_duration else "M0_renewal", ym, slope, xm, sigma)


def predict_row(event: Event, model: LognormalModel) -> dict:
    mu = model.mu(event.duration)
    z = NormalDist().inv_cdf(0.95)
    lo, hi = math.exp(mu - z * model.sigma), math.exp(mu + z * model.sigma)
    q = event.next_quiescent_gap
    return {"event_id": event.event_id, "forecast_origin": event.end,
            "origin_kind": "oracle_true_end", "model": model.name,
            "observed_gap": q, "duration_available_at_origin": event.duration,
            "median_gap": math.exp(mu), "lower_90": lo, "upper_90": hi,
            "covered_90": lo <= q <= hi,
            "log_score": lognormal_logpdf(q, mu, model.sigma),
            "pit": lognormal_cdf(q, mu, model.sigma)}


def compare_complete_oracle_cycles(events: list[Event], train_fraction: float = 0.70) -> tuple[dict, list[dict]]:
    if not 0.1 <= train_fraction <= 0.9:
        raise ValueError("train_fraction must be in [0.1, 0.9]")
    if len(events) < 20 or any(b.onset <= a.onset for a, b in zip(events, events[1:])):
        raise ValueError("need at least 20 chronologically ordered events")
    split = int(len(events) * train_fraction)
    training, testing = events[:split], events[split:]
    # Last training target ends at first test onset, before first test's true end.
    if any(e.end + e.next_quiescent_gap > testing[0].end + 1e-9 for e in training):
        raise ValueError("a training target is unresolved at first forecast origin")
    models = [fit_model(training, use_duration=u) for u in (False, True)]
    rows = [predict_row(e, m) for e in testing for m in models]
    scores = {}
    for model in models:
        part = [r for r in rows if r["model"] == model.name]
        scores[model.name] = {
            "mean_log_score": fmean(r["log_score"] for r in part),
            "coverage_90": fmean(float(r["covered_90"]) for r in part),
            "mean_absolute_error_of_predictive_median_days": fmean(abs(r["median_gap"] - r["observed_gap"]) for r in part),
            "fitted_duration_slope": model.slope,
            "fitted_residual_log_sigma": model.sigma,
        }
    result = {"n_train": len(training), "n_test": len(testing),
              "evaluation": "chronological, frozen fit, complete oracle cycles only",
              "units": "gaps in relative_demo_days; natural-log predictive density averaged per held-out cycle",
              "models": scores,
              "delta_mean_log_score_M1_minus_M0": scores["M1_duration"]["mean_log_score"] - scores["M0_renewal"]["mean_log_score"],
              "correlation_duration_with_quiescent_gap": correlation([e.duration for e in events], [e.next_quiescent_gap for e in events]),
              "correlation_duration_with_onset_gap": correlation([e.duration for e in events], [e.next_onset_gap for e in events])}
    return result, rows
