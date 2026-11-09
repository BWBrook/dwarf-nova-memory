"""Prefix-history timing rules for R2 preparation, separate from frozen A10.

The state filter is a windowed working predictor of measured log gaps. Mark
offsets change forecasts only; they never alter the timing filter's updates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math

import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.special import log_ndtr


@dataclass(frozen=True)
class ConditionalClock:
    anchor: float
    issue: float
    mu: float
    sigma: float

    def __post_init__(self):
        if (not all(math.isfinite(v) for v in (self.anchor, self.issue, self.mu, self.sigma))
                or self.anchor > self.issue or self.sigma <= 0):
            raise ValueError("invalid conditional clock")

    def _logsf(self, time):
        wait = time - self.anchor
        return 0.0 if wait <= 0 else float(log_ndtr(-(math.log(wait) - self.mu) / self.sigma))

    def log_survival(self, time):
        if time < self.issue:
            raise ValueError("survival cutoff precedes issue")
        return self._logsf(time) - self._logsf(self.issue)

    def log_density(self, time):
        if time <= self.issue:
            return -math.inf
        wait = time - self.anchor
        z = (math.log(wait) - self.mu) / self.sigma
        return -.5 * z * z - math.log(wait * self.sigma) - .5 * math.log(2 * math.pi) - self._logsf(self.issue)

    def log_interval(self, lower, upper):
        from dnmem.r2_scores import interval_log_mass
        result = interval_log_mass(self, lower, upper)
        if result["status"] != "usable":
            raise ValueError("unsupported interval: " + result["status"])
        return result["log_mass"]


def history_values(row):
    history = row.get("gap_history", [])
    values = []
    for item in history:
        if (not isinstance(item, dict) or not math.isfinite(float(item["available_at"]))
                or float(item["available_at"]) > row["issue_time"]):
            raise ValueError("history is not available by issue")
        value = item.get("log_gap")
        if value is not None and not math.isfinite(float(value)):
            raise ValueError("nonfinite gap history")
        values.append(None if value is None else float(value))
    return values


def _previous(row):
    gap = row.get("previous_gap")
    return (gap is not None and math.isfinite(float(gap)) and float(gap) > 0
            and row.get("previous_gap_covered") is True)


def _mark(row):
    value = row.get("mark")
    return float(value) if value is not None and math.isfinite(float(value)) and float(value) > 0 else None


def _validate(rows):
    indices = set()
    for row in rows:
        index, issue = row["emission_index"], float(row["issue_time"])
        if (index in indices or not math.isfinite(issue) or not math.isfinite(float(row["available_at"]))
                or float(row["available_at"]) > issue):
            raise ValueError("duplicate or unavailable feature")
        indices.add(index)
        anchor = row.get("clock_anchor")
        if anchor is not None and (not math.isfinite(float(anchor)) or anchor > issue):
            raise ValueError("clock anchor after issue or nonfinite")
        values = history_values(row)
        if _previous(row):
            if not values or values[-1] is None or not math.isclose(
                    values[-1], math.log(float(row["previous_gap"])), rel_tol=0, abs_tol=1e-12):
                raise ValueError("previous gap and last history entry disagree")
        elif values and values[-1] is not None:
            raise ValueError("unavailable previous gap has a measured last history entry")


def filter_history(values, mu, phi, level_sd, ar_sd):
    """Predict the next measured log gap with a two-state Gaussian filter."""
    if (not all(math.isfinite(v) for v in (mu, phi, level_sd, ar_sd))
            or not (-.95 <= phi <= .95 and level_sd > 0 and ar_sd > 0)):
        raise ValueError("invalid state parameters")
    transition = np.diag([1.0, phi])
    process = np.diag([level_sd ** 2, ar_sd ** 2])
    mean = np.array([mu, 0.0])
    covariance = np.diag([1.0, ar_sd ** 2 / (1 - phi ** 2)])
    h = np.ones(2)
    for value in values:
        mean = transition @ mean
        covariance = transition @ covariance @ transition.T + process
        if value is not None:
            if not math.isfinite(float(value)):
                raise ValueError("nonfinite state observation")
            variance = float(h @ covariance @ h)
            if not variance > 0:
                raise ValueError("degenerate state update")
            gain = covariance @ h / variance
            mean += gain * (float(value) - float(h @ mean))
            residual = np.eye(2) - np.outer(gain, h)
            covariance = residual @ covariance @ residual.T
    mean = transition @ mean
    covariance = transition @ covariance @ transition.T + process
    variance = float(h @ covariance @ h)
    if not math.isfinite(variance) or variance <= 0:
        raise ValueError("invalid predictive state variance")
    return float(h @ mean), math.sqrt(variance)


def _standard(values):
    if not values:
        return 0.0, 1.0, True
    center, scale = float(np.mean(values)), float(np.std(values))
    return center, scale if scale > 1e-10 else 1.0, scale <= 1e-10


def _raw_covariates(row, rung, discount):
    values = history_values(row)
    previous = values[-1]
    older = values[:-1]
    observed = [v for v in older if v is not None]
    if rung == "B0":
        return [previous, float(np.mean(observed)) if observed else None]
    second = older[-1] if older else None
    pairs = [(value, discount ** position) for position, value in enumerate(reversed(older))
             if value is not None]
    total = sum(weight for _, weight in pairs)
    level = sum(value * weight for value, weight in pairs) / total if total > 0 else None
    return [previous, second, level]


def _transform(rows, rung, discount):
    raw = [_raw_covariates(row, rung, discount) for row in rows]
    return [_standard([v[j] for v in raw if v[j] is not None]) for j in range(len(raw[0]))]


def _design(row, rung, discount, transform):
    raw = _raw_covariates(row, rung, discount)
    return [1.0] + [0.0 if value is None else (value - center) / scale
                    for value, (center, scale, _) in zip(raw, transform)]


def evidence_score(clock, evidence):
    if evidence["kind"] == "interval":
        return clock.log_interval(evidence["onset_lo"], evidence["onset_hi"])
    if evidence["kind"] == "right_censored":
        return clock.log_survival(evidence["censor_at"])
    if evidence["kind"] == "point":
        value = clock.log_density(evidence["onset_t"])
        if not math.isfinite(value):
            raise ValueError("point does not follow issue")
        return value
    raise ValueError("unsupported training outcome")


def _best(results, label):
    good = [r for r in results if r.success and np.all(np.isfinite(r.x)) and math.isfinite(float(r.fun))
            and float(r.fun) < 1e90]
    if not good:
        raise ValueError(label + " optimization failed: " + "; ".join(str(r.message) for r in results))
    return min(good, key=lambda r: float(r.fun))


def _optimize(objective, starts, bounds, label):
    def finite(theta):
        try:
            value = objective(theta)
            return value if math.isfinite(value) else 1e100
        except (ValueError, OverflowError, FloatingPointError):
            return 1e100
    attempts = [minimize(finite, initial, method="L-BFGS-B", bounds=bounds,
                        options={"maxiter": 250, "ftol": 1e-10}) for initial in starts]
    free = [i for i, (lo, hi) in enumerate(bounds) if lo != hi]
    for attempt in attempts:
        if attempt.success:
            gradient = np.asarray(attempt.jac, dtype=float) if attempt.jac is not None else np.array([])
            if len(gradient) != len(bounds) or not np.all(np.isfinite(gradient[free])):
                attempt.success = False
                attempt.message = "nonfinite free-parameter gradient"
    result = _best(attempts, label)
    return result.x.tolist(), {"objective": float(result.fun), "message": str(result.message),
                               "iterations": int(result.nit), "successful": True}


@dataclass(frozen=True)
class TimingRule:
    rung: str
    parameters: list
    transform: list
    discount: float
    constant: list
    remaining: list
    mark_center: float
    mark_scale: float
    beta: float
    metadata: dict

    def predict(self, row, with_mark=False):
        _validate([row])
        anchor = row.get("clock_anchor")
        if anchor is None:
            clock = ConditionalClock(row["issue_time"], row["issue_time"], *self.remaining)
            return clock, "R0"
        if not _previous(row):
            return ConditionalClock(anchor, row["issue_time"], *self.constant), "constant"
        if self.rung == "B2":
            mu, phi, log_level, log_ar = self.parameters
            location, sigma = filter_history(history_values(row), mu, phi, math.exp(log_level), math.exp(log_ar))
        else:
            x = _design(row, self.rung, self.discount, self.transform)
            location = float(np.dot(x, self.parameters[:-1]))
            sigma = math.exp(self.parameters[-1])
        clock = ConditionalClock(anchor, row["issue_time"], location, sigma)
        if not with_mark or self.beta == 0.0:
            return clock, self.rung
        mark = _mark(row)
        if mark is None:
            return clock, self.rung
        shift = self.beta * (math.log(mark) - self.mark_center) / self.mark_scale
        return ConditionalClock(anchor, row["issue_time"], location + shift, sigma), self.rung + "+D"

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, value):
        return cls(**value)


def fit_ladder(features, evidence, cutoff):
    """Fit timing then nonnegative fixed-baseline offsets on development only."""
    if not math.isfinite(cutoff):
        raise ValueError("training cutoff must be finite")
    _validate(features)
    outcomes = {row["emission_index"]: row for row in evidence}
    if len(outcomes) != len(evidence) or set(outcomes) != {r["emission_index"] for r in features}:
        raise ValueError("training outcome/feature population mismatch")
    usable = []
    for row in features:
        ev = outcomes[row["emission_index"]]
        computed, available = float(ev["computed_as_of"]), float(ev["evidence_available_at"])
        if (not all(math.isfinite(v) for v in (computed, available)) or row["issue_time"] >= cutoff
                or ev["issue_time"] != row["issue_time"] or computed > cutoff or available > cutoff):
            raise ValueError("training information exceeds freeze")
        last_time = (ev.get("onset_hi") if ev["kind"] == "interval" else ev.get("onset_t")
                     if ev["kind"] == "point" else ev.get("censor_at") if ev["kind"] == "right_censored" else None)
        if last_time is not None and (not math.isfinite(float(last_time)) or last_time > min(computed, available)):
            raise ValueError("outcome support exceeds declared availability/freeze")
        if ev["kind"] != "excluded":
            usable.append((row, ev))
    anchored = [(r, e) for r, e in usable if r.get("clock_anchor") is not None]
    timed = [(r, e) for r, e in anchored if _previous(r)]
    if len(timed) < 8:
        raise ValueError("too few timing-available training rows")
    resolved = sum(e["kind"] in ("point", "interval") for _, e in timed)
    if resolved < 2:
        raise ValueError("too few resolved timing outcomes for model preparation")

    def fit_constant(group, remaining):
        def objective(theta):
            return -sum(evidence_score(ConditionalClock(r["issue_time"] if remaining else r["clock_anchor"],
                        r["issue_time"], theta[0], math.exp(theta[1])), e) for r, e in group)
        theta, metadata = _optimize(objective, [[3.5, math.log(.4)], [3.0, math.log(.8)]],
                                    [(-5, 8), (math.log(.03), math.log(2))], "constant")
        return [theta[0], math.exp(theta[1])], metadata

    remaining, remaining_meta = fit_constant(usable, True)
    constant, constant_meta = fit_constant(anchored, False)
    marks = [math.log(_mark(r)) for r, _ in timed if _mark(r) is not None]
    mark_center, mark_scale, mark_fixed = _standard(marks)
    result = {}
    for rung in ("B0", "B1", "B2"):
        choices = []
        for discount in ((0., .25, .5, .75, .9, .98) if rung == "B1" else (0.,)):
            transform = _transform([r for r, _ in timed], rung, discount) if rung != "B2" else []
            if rung == "B2":
                starts = [[3.5, p, math.log(.03), math.log(.35)] for p in (-.4, 0., .4)]
                bounds = [(-5, 8), (-.95, .95), (math.log(1e-4), 0.), (math.log(.03), math.log(2))]
            else:
                starts = [[loc] + [0.] * len(transform) + [math.log(sd)] for loc, sd in ((3.5, .4), (3., .8))]
                bounds = [(-5, 8)] + [(0., 0.) if fixed else (-3., 3.) for _, _, fixed in transform] + [(math.log(.03), math.log(2))]

            def objective(theta):
                total = 0.
                for row, ev in timed:
                    if rung == "B2":
                        location, sd = filter_history(history_values(row), theta[0], theta[1], math.exp(theta[2]), math.exp(theta[3]))
                    else:
                        location = float(np.dot(_design(row, rung, discount, transform), theta[:-1]))
                        sd = math.exp(theta[-1])
                    total -= evidence_score(ConditionalClock(row["clock_anchor"], row["issue_time"], location, sd), ev)
                return total

            theta, metadata = _optimize(objective, starts, bounds, rung)
            if rung != "B2":
                matrix = np.asarray([_design(row, rung, discount, transform) for row, _ in timed])
                metadata.update(design_rank=int(np.linalg.matrix_rank(matrix)), design_columns=matrix.shape[1],
                                rank_deficient=bool(np.linalg.matrix_rank(matrix) < matrix.shape[1]))
            choices.append((metadata["objective"], theta, metadata, transform, discount))
        _, theta, metadata, transform, discount = min(choices, key=lambda v: v[0])
        base = TimingRule(rung, theta, transform, discount, constant, remaining, mark_center, mark_scale, 0.,
                          {"base_fit": metadata, "constant_fit": constant_meta, "remaining_fit": remaining_meta,
                           "training_cutoff": cutoff, "training_rows": len(usable), "timing_rows": len(timed),
                           "resolved_timing_outcomes": resolved, "fit_is_not_identifiability_certificate": True,
                           "history_policy": "rebuild from declared available prefix; no mark update",
                           "discount_profile": [{"discount": item[4], **item[2]} for item in choices]})
        mark_rows = [(r, e) for r, e in timed if _mark(r) is not None]
        frozen_clocks = [(base.predict(r)[0], (math.log(_mark(r)) - mark_center) / mark_scale, e) for r, e in mark_rows]

        def offset_objective(beta):
            return -sum(evidence_score(ConditionalClock(c.anchor, c.issue, c.mu + beta * z, c.sigma), ev)
                        for c, z, ev in frozen_clocks)

        beta, offset_meta = 0., {"status": "unidentified_or_missing"}
        if frozen_clocks and not mark_fixed:
            optimum = minimize_scalar(offset_objective, method="bounded", bounds=(0., 5.), options={"xatol": 1e-9})
            if not optimum.success or not math.isfinite(float(optimum.fun)):
                raise ValueError("mark offset optimization failed")
            beta = min((0., float(optimum.x), 5.), key=offset_objective)
            offset_meta = {"status": "optimized", "objective": offset_objective(beta),
                           "zero_objective": offset_objective(0.), "timing_parameters_fixed": True}
        result[rung] = TimingRule(**{**base.to_dict(), "beta": beta,
                                    "metadata": {**base.metadata, "offset_fit": offset_meta}})
    return result
