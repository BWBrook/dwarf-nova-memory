"""Audited development fits and fixed-baseline mark sensitivities for R2b."""

from dataclasses import dataclass, replace
import copy
import math

import numpy as np
from scipy.optimize import minimize, minimize_scalar

from dnmem.r2_models import (ConditionalClock, TimingRule, _design, _previous,
                             _standard, _transform, _validate, evidence_score,
                             filter_history, history_values)


def training_pairs(features, evidence, cutoff):
    _validate(features)
    if not math.isfinite(cutoff):
        raise ValueError("nonfinite development cutoff")
    outcomes = {e["emission_index"]: e for e in evidence}
    if len(outcomes) != len(evidence) or set(outcomes) != {r["emission_index"] for r in features}:
        raise ValueError("development feature/outcome population mismatch")
    result = []
    for row in features:
        ev = outcomes[row["emission_index"]]
        computed, available = ev["computed_as_of"], ev["evidence_available_at"]
        if (not all(math.isfinite(v) for v in (computed, available)) or row["issue_time"] >= cutoff
                or ev["issue_time"] != row["issue_time"] or max(computed, available) > cutoff):
            raise ValueError("development information exceeds cutoff")
        last = (ev.get("onset_hi") if ev["kind"] == "interval" else ev.get("onset_t")
                if ev["kind"] == "point" else ev.get("censor_at") if ev["kind"] == "right_censored" else None)
        if last is not None and (not math.isfinite(last) or last > min(computed, available)):
            raise ValueError("outcome support exceeds its availability")
        if ev["kind"] != "excluded":
            result.append((row, ev))
    return result


def optimize(objective, starts, bounds):
    def finite(theta):
        try:
            value = objective(theta)
            return value if math.isfinite(value) else 1e100
        except (ValueError, OverflowError, FloatingPointError):
            return 1e100
    records, good = [], []
    free = [i for i, (lo, hi) in enumerate(bounds) if lo != hi]
    for initial in starts:
        fit = minimize(finite, initial, method="L-BFGS-B", bounds=bounds,
                       options={"maxiter": 250, "ftol": 1e-10})
        gradient = np.asarray(fit.jac, dtype=float) if fit.jac is not None else np.array([])
        valid = bool(fit.success and np.all(np.isfinite(fit.x)) and math.isfinite(float(fit.fun))
                     and fit.fun < 1e90 and len(gradient) == len(bounds)
                     and np.all(np.isfinite(gradient[free])))
        records.append({"initial": list(initial),
                        "parameters": [float(x) if math.isfinite(x) else None for x in fit.x],
                        "objective": float(fit.fun) if math.isfinite(float(fit.fun)) else None, "successful": valid,
                        "message": str(fit.message), "iterations": int(fit.nit)})
        if valid:
            good.append(fit)
    if not good:
        raise ValueError("all development starts failed: " + str(records))
    best = min(good, key=lambda x: x.fun)
    spread = max(r.fun for r in good) - min(r.fun for r in good)
    tolerance = 1e-6 * max(1., abs(float(best.fun)))
    return best.x.tolist(), {"objective": float(best.fun), "attempts": records,
                            "successful": True, "multistart_spread": float(spread),
                            "stability_tolerance": tolerance,
                            "stable": len(good) == len(starts) and len(good) >= 2 and spread <= tolerance}


def _cadence(row):
    record = row.get("cadence_end", {})
    value = record.get("value_days")
    if value is not None:
        if (not math.isfinite(value) or value < 0 or not math.isfinite(record["available_at"])
                or record["available_at"] > row["issue_time"]):
            raise ValueError("unavailable or invalid cadence covariate")
    return value


def mark_value(row, marker):
    if marker == "duration":
        value, available = row.get("mark"), row["available_at"]
    elif marker == "flux":
        record = row["flux_proxy"]
        value, available = record["value_threshold_flux_days"], record["available_at"]
    elif marker == "rate":
        record = row["observer_rate"]
        value, available = record["value_per_day"], record["available_at"]
    else:
        raise ValueError("unknown mark")
    if value is not None:
        if not math.isfinite(value) or not math.isfinite(available) or available > row["issue_time"]:
            raise ValueError("unavailable or invalid mark")
        return value if value > 0 else None
    return None


@dataclass(frozen=True)
class R2bRule:
    timing: TimingRule
    cadence_transform: tuple | None
    cadence_beta: float
    marker: str
    mark_center: float
    mark_scale: float
    beta: float
    metadata: dict

    def predict(self, row, with_mark=False):
        clock, route = self.timing.predict(row, False)
        if route != self.timing.rung:
            return clock, route
        shift = 0.
        if self.cadence_transform is not None:
            value = _cadence(row)
            center, scale, _ = self.cadence_transform
            shift = self.cadence_beta * ((value - center) / scale if value is not None else 0.)
        base = clock if shift == 0 else ConditionalClock(clock.anchor, clock.issue, clock.mu + shift, clock.sigma)
        if not with_mark or self.beta == 0.:
            return base, route
        value = mark_value(row, self.marker)
        if value is None:
            return base, route
        shift = self.beta * (math.log(value) - self.mark_center) / self.mark_scale
        return ConditionalClock(base.anchor, base.issue, base.mu + shift, base.sigma), route + "+" + self.marker

    def to_dict(self):
        return {"timing": self.timing.to_dict(), "cadence_transform": self.cadence_transform,
                "cadence_beta": self.cadence_beta, "marker": self.marker,
                "mark_center": self.mark_center, "mark_scale": self.mark_scale,
                "beta": self.beta, "metadata": self.metadata}

    @classmethod
    def from_dict(cls, value):
        return cls(**{**value, "timing": TimingRule.from_dict(value["timing"])})


def fit_bases(features, evidence, cutoff, include_cadence=False, rungs=("B0", "B1", "B2")):
    usable = training_pairs(features, evidence, cutoff)
    anchored = [(r, e) for r, e in usable if r.get("clock_anchor") is not None]
    timed = [(r, e) for r, e in anchored if _previous(r)]
    if len(timed) < 8 or sum(e["kind"] in ("point", "interval") for _, e in timed) < 2:
        raise ValueError("insufficient resolved development information")

    def constant_fit(group, remaining):
        def objective(theta):
            return -sum(evidence_score(ConditionalClock(r["issue_time"] if remaining else r["clock_anchor"],
                         r["issue_time"], theta[0], math.exp(theta[1])), e) for r, e in group)
        theta, meta = optimize(objective, [[3.5, math.log(.4)], [3., math.log(.8)]],
                               [(-5., 8.), (math.log(.03), math.log(2.))])
        return [theta[0], math.exp(theta[1])], meta

    remaining, remaining_meta = constant_fit(usable, True)
    constant, constant_meta = constant_fit(anchored, False)
    cadence = _standard([_cadence(r) for r, _ in timed if _cadence(r) is not None]) if include_cadence else None
    result = {}
    for rung in rungs:
        if rung not in ("B0", "B1", "B2"):
            raise ValueError("unknown rung")
        choices = []
        for discount in ((0., .25, .5, .75, .9, .98) if rung == "B1" else (0.,)):
            transform = _transform([r for r, _ in timed], rung, discount) if rung != "B2" else []
            if rung == "B2":
                starts = [[3.5, p, math.log(.03), math.log(.35)] for p in (-.4, 0., .4)]
                bounds = [(-5., 8.), (-.95, .95), (math.log(1e-4), 0.), (math.log(.03), math.log(2.))]
            else:
                starts = [[mu] + [0.] * len(transform) + [math.log(sd)] for mu, sd in ((3.5, .4), (3., .8))]
                bounds = [(-5., 8.)] + [(0., 0.) if fixed else (-3., 3.) for _, _, fixed in transform]
                bounds += [(math.log(.03), math.log(2.))]
            if cadence is not None:
                starts = [initial + [0.] for initial in starts]
                bounds += [(0., 0.) if cadence[2] else (-3., 3.)]
            designs = [_design(r, rung, discount, transform) for r, _ in timed] if rung != "B2" else None
            histories = [history_values(r) for r, _ in timed]
            zs = [(_cadence(r) - cadence[0]) / cadence[1] if cadence and _cadence(r) is not None else 0.
                  for r, _ in timed]

            def objective(theta):
                core = theta[:-1] if cadence is not None else theta
                total = 0.
                for index, (row, ev) in enumerate(timed):
                    if rung == "B2":
                        location, sd = filter_history(histories[index], core[0], core[1], math.exp(core[2]), math.exp(core[3]))
                    else:
                        location, sd = float(np.dot(designs[index], core[:-1])), math.exp(core[-1])
                    if cadence is not None:
                        location += theta[-1] * zs[index]
                    total -= evidence_score(ConditionalClock(row["clock_anchor"], row["issue_time"], location, sd), ev)
                return total

            theta, meta = optimize(objective, starts, bounds)
            if designs is not None:
                matrix = np.asarray([x + ([z] if cadence is not None else []) for x, z in zip(designs, zs)])
                meta.update(design_rank=int(np.linalg.matrix_rank(matrix)), design_columns=matrix.shape[1])
            choices.append((meta["objective"], theta, meta, transform, discount))
        _, theta, meta, transform, discount = min(choices, key=lambda item: item[0])
        core = theta[:-1] if cadence is not None else theta
        timing = TimingRule(rung, core, transform, discount, constant, remaining, 0., 1., 0., {})
        result[rung] = R2bRule(timing, cadence, theta[-1] if cadence is not None else 0., "duration", 0., 1., 0.,
                              {"base_fit": meta, "remaining_fit": remaining_meta, "constant_fit": constant_meta,
                               "discount_profiles": [{"discount": choice[4], **choice[2]} for choice in choices],
                               "training_cutoff": cutoff, "training_rows": len(usable), "timing_rows": len(timed),
                               "history_policy": "windowed measured gaps, rebuilt once per issue; no mark state update",
                               "missing_cadence": "development center, standardized covariate zero",
                               "fit_is_not_identifiability_certificate": True})
    return result


def fit_mark(base, features, evidence, cutoff, marker="duration"):
    pairs = [(r, e) for r, e in training_pairs(features, evidence, cutoff)
             if r.get("clock_anchor") is not None and _previous(r) and mark_value(r, marker) is not None]
    center, scale, fixed = _standard([math.log(mark_value(r, marker)) for r, _ in pairs])
    prepared = [(base.predict(r, False)[0], (math.log(mark_value(r, marker)) - center) / scale, e) for r, e in pairs]

    def objective(beta):
        return -sum(evidence_score(ConditionalClock(c.anchor, c.issue, c.mu + beta * z, c.sigma), e)
                    for c, z, e in prepared)

    beta, meta = 0., {"status": "unidentified_or_missing", "markable_training_rows": len(pairs)}
    if prepared and not fixed:
        fit = minimize_scalar(objective, method="bounded", bounds=(0., 5.), options={"xatol": 1e-9})
        if not fit.success or not math.isfinite(float(fit.fun)):
            raise ValueError("fixed-baseline mark fit failed")
        beta = min((0., float(fit.x), 5.), key=objective)
        meta.update(status="optimized", objective=objective(beta), zero_objective=objective(0.), timing_parameters_fixed=True)
    return replace(base, marker=marker, mark_center=center, mark_scale=scale, beta=beta,
                   metadata={**base.metadata, "offset_fit": meta})


def local_lag_index(rule, row):
    """V0's one-lag Fisher planning index, explicitly not a cadence upper bound."""
    clock, route = rule.predict(row, False)
    current = row.get("cadence_end", {}).get("value_days")
    onset = row.get("cadence_on", {}).get("value_days")
    history = row.get("gap_history", [])
    previous_end = history[-1].get("left_cadence_end_days") if history else None
    if route != rule.timing.rung or any(v is None for v in (current, onset, previous_end)):
        return {"status": "unsupported", "is_upper_bound": False}
    if not all(math.isfinite(v) and v >= 0 for v in (current, onset, previous_end)):
        raise ValueError("invalid lag-index inputs")
    available = [row["cadence_end"]["available_at"], row["cadence_on"]["available_at"],
                 history[-1]["left_cadence_end_available_at"]]
    if any(value is None or not math.isfinite(value) or value > row["issue_time"] for value in available):
        raise ValueError("unavailable lag-index input")
    epsilon, locations = 1e-5, []
    for direction in (-1., 1.):
        changed = copy.deepcopy(row)
        changed["gap_history"][-1]["log_gap"] += direction * epsilon
        changed["previous_gap"] = math.exp(changed["gap_history"][-1]["log_gap"])
        locations.append(rule.predict(changed, False)[0].mu)
    median_wait = math.exp(clock.mu)
    derivative = (locations[1] - locations[0]) / (2 * epsilon)
    b = derivative * median_wait / row["previous_gap"]
    delta = current + abs(b) * (onset + previous_end)
    information = (1 + clock.sigma ** 2) * math.exp(2 * clock.sigma ** 2) / (clock.sigma ** 2 * median_wait ** 2)
    return {"status": "available", "local_index": .5 * information * delta ** 2,
            "previous_log_gap_derivative": derivative, "time_conversion_b": b,
            "lag_scale_days": delta, "unconditional_location_fisher": information,
            "issue_age_days": clock.issue - clock.anchor, "is_upper_bound": False,
            "omits": ["older-history perturbations", "survival-conditioning correction",
                      "finite-shift remainder", "shape and selection effects", "latent phase travel time"]}
