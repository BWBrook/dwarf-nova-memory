"""Sequential Gaussian log-gap stress model, not an X5 or archive simulator."""

from __future__ import annotations

from bisect import insort
import math

import numpy as np
from scipy.stats import t as student_t


def capped_star_weights(counts, cap=.4):
    counts = np.asarray(counts, dtype=float)
    if (counts.ndim != 1 or np.any(~np.isfinite(counts)) or np.any(counts <= 0)
            or not 0 < cap <= 1 or len(counts) * cap < 1 - 1e-12):
        raise ValueError("infeasible star-weight cap or counts")
    weights, active = np.zeros(len(counts)), np.ones(len(counts), dtype=bool)
    while active.any():
        indices = np.flatnonzero(active)
        proposed = (1 - weights.sum()) * counts[indices] / counts[indices].sum()
        over = proposed > cap
        if not over.any():
            weights[indices] = proposed
            break
        weights[indices[over]] = cap
        active[indices[over]] = False
    if not np.isclose(weights.sum(), 1) or weights.max() > cap + 1e-12:
        raise ValueError("star-weight normalization failed")
    return weights


def allocate_counts(total, stars, allocation="balanced"):
    if stars < 1 or total < 6 * stars:
        raise ValueError("at least six evaluation forecasts per star required")
    proportions = np.ones(stars) / stars
    if allocation == "imbalanced":
        if stars < 2:
            raise ValueError("imbalanced allocation requires multiple stars")
        proportions = np.array([.6] + [.4 / (stars - 1)] * (stars - 1))
    elif allocation != "balanced":
        raise ValueError("unknown allocation")
    exact = total * proportions
    counts = np.floor(exact).astype(int)
    for index in np.argsort(-(exact - counts), kind="stable")[:total - counts.sum()]:
        counts[index] += 1
    if counts.min() < 6:
        raise ValueError("allocation leaves fewer than six forecasts for a star")
    return counts


def recent_mark_center(mark, development_n, window=10, minimum=3, guard=True):
    mark = np.asarray(mark, dtype=float)
    observed = np.isfinite(mark)
    training = mark[:development_n][observed[:development_n]]
    center = float(training.mean()) if len(training) else 0.
    scale = float(training.std()) if len(training) else 1.
    fixed = len(training) < 2 or scale <= 1e-10
    if fixed:
        scale = 1.
    z = np.where(observed, (mark - center) / scale, 0.)
    if not guard:
        return z, observed & (not fixed), {"center": center, "scale": scale, "fixed": fixed}
    indices = np.flatnonzero(observed)
    values = z[indices]
    sums = np.r_[0., np.cumsum(values)]
    count = np.searchsorted(indices, np.arange(len(mark)), side="left")
    first = np.maximum(0, count - window)
    retained = count - first
    average = np.divide(sums[count] - sums[first], retained,
                        out=np.zeros(len(mark)), where=retained > 0)
    usable = observed & (retained >= minimum) & (not fixed)
    return np.where(usable, z - average, 0.), usable, {"center": center, "scale": scale, "fixed": fixed}


def causal_level_shift(issue, available, residual, window=20):
    """Mean raw-base residual of the most recent available forecast snapshots."""
    issue, available, residual = map(lambda a: np.asarray(a, dtype=float), (issue, available, residual))
    if (not (issue.shape == available.shape == residual.shape) or issue.ndim != 1
            or window < 1 or np.any(~np.isfinite(issue)) or np.any(~np.isfinite(available))
            or np.any(~np.isfinite(residual)) or np.any(np.diff(issue) <= 0)
            or np.any(available <= issue)):
        raise ValueError("invalid availability or forecast snapshots")
    if np.all(np.diff(available) >= 0):
        count = np.searchsorted(available, issue, side="right")
        first = np.maximum(0, count - window)
        prefix = np.r_[0., np.cumsum(residual)]
        return np.divide(prefix[count] - prefix[first], count - first,
                         out=np.zeros(len(issue)), where=count > first), count - first
    order = np.argsort(available, kind="stable")
    active, position, shifts, counts = [], 0, np.zeros(len(issue)), np.zeros(len(issue), dtype=int)
    for i, time in enumerate(issue):
        while position < len(order) and available[order[position]] <= time:
            insort(active, int(order[position])); position += 1
        chosen = active[-window:]
        if chosen:
            shifts[i], counts[i] = residual[chosen].mean(), len(chosen)
    return shifts, counts


def _history_covariates(y, issue, available, window):
    n = len(y)
    values = np.full((n, window), np.nan)
    for lag in range(1, window + 1):
        if lag < n:
            known = available[:-lag] <= issue[lag:]
            values[lag:, lag - 1] = np.where(known, y[:-lag], np.nan)
    previous = values[:, 0]
    old = values[:, 1:]
    count = np.isfinite(old).sum(axis=1)
    mean = np.divide(np.nansum(old, axis=1), count, out=np.full(n, np.nan), where=count > 0)
    return previous, mean


def fit_star(history, *, level_window=20, mark_window=10, minimum_marks=3,
             history_window=6, recalibrate=True, guard_marks=True, oracle=False):
    y, issue, available, mark = (np.asarray(history[k], dtype=float)
                                for k in ("y", "issue", "outcome_available_at", "mark"))
    ndev = int(history["development_n"])
    if not 8 <= ndev < len(y) or any(len(a) != len(y) for a in (issue, available, mark)):
        raise ValueError("invalid development/evaluation split")
    if (np.any(~np.isfinite(y)) or np.any(np.isinf(mark)) or np.any(~np.isfinite(issue))
            or np.any(~np.isfinite(available)) or np.any(np.diff(issue) <= 0)
            or np.any(available + 1e-10 < issue + np.exp(y))):
        raise ValueError("outcome availability precedes its target or is nonfinite")
    cutoff = issue[ndev]
    previous, older = _history_covariates(y, issue, available, history_window)
    training = (np.arange(len(y)) < ndev) & (available <= cutoff)
    timed = training & np.isfinite(previous)
    if training.sum() < 8 or timed.sum() < 8:
        raise ValueError("too few genuinely available development outcomes")
    raw = np.column_stack([previous, older])
    transforms = []
    for j in range(2):
        finite = raw[timed, j]; finite = finite[np.isfinite(finite)]
        center = float(finite.mean()) if len(finite) else 0.
        sd = float(finite.std()) if len(finite) else 1.
        transforms.append((center, sd if sd > 1e-10 else 1.))
    design = np.column_stack([np.ones(len(y))] +
                              [np.where(np.isfinite(raw[:, j]), (raw[:, j] - mu) / sd, 0.)
                               for j, (mu, sd) in enumerate(transforms)])
    coefficient, _, rank, _ = np.linalg.lstsq(design[timed], y[timed], rcond=None)
    constant = float(y[training].mean())
    mean = design @ coefficient
    mean = np.where(np.isfinite(previous), mean, constant)
    variance = float(np.mean((y[timed] - mean[timed]) ** 2))
    variance = max(.03 ** 2, min(2. ** 2, variance))
    if oracle:
        mean = np.asarray(history["true_mean_without_direct_mark"], dtype=float).copy()
    variances = (np.asarray(history["innovation_variance"], dtype=float) if oracle
                 else np.full(len(y), variance))
    if np.any(~np.isfinite(variances)) or np.any(variances <= 0):
        raise ValueError("oracle reference requires positive innovation variance")
    shifts, resolved = causal_level_shift(issue, available, y - mean, level_window)
    if not recalibrate or oracle:
        shifts[:] = 0.
    baseline = mean + shifts
    z, mark_usable, transform = recent_mark_center(mark, ndev, mark_window, minimum_marks, guard_marks)
    mark_usable &= np.isfinite(previous)
    z = np.where(mark_usable, z, 0.)
    return {"history": history, "raw_mean": mean, "baseline_mean": baseline,
            "variance": variances, "z": z, "mark_usable": mark_usable,
            "training": training, "timed_training": timed, "resolved_window_counts": resolved,
            "level_shift": shifts, "model": {"coefficient": coefficient.tolist(), "rank": int(rank),
                "constant": constant, "variance": float(variances[ndev]), "fitted_gaussian_variance": variance,
                "transforms": transforms,
                "mark_transform": transform, "training_outcomes": int(training.sum()),
                "timing_training_outcomes": int(timed.sum()), "oracle": oracle,
                "recalibration_applied": recalibrate and not oracle}}


def positive_pooled_offset(stars, cap=.4):
    masks = [star["training"] & star["mark_usable"] for star in stars]
    counts = np.asarray([mask.sum() for mask in masks], dtype=int)
    active = counts > 0
    if active.sum() * cap < 1 - 1e-12:
        return 0.
    weights = capped_star_weights(counts[active], cap)
    numerator = denominator = 0.
    for position, weight in zip(np.flatnonzero(active), weights):
        star, mask, count = stars[position], masks[position], counts[position]
        z = star["z"][mask]
        residual = np.asarray(star["history"]["y"])[mask] - star["baseline_mean"][mask]
        inverse = 1 / star["variance"][mask]
        numerator += weight / count * float(np.dot(z * inverse, residual))
        denominator += weight / count * float(np.dot(z * inverse, z))
    return max(0., numerator / denominator) if denominator > 0 else 0.


def forecast_trial(histories, **options):
    fitted = [fit_star(h, **options) for h in histories]
    beta = positive_pooled_offset(fitted)
    records = {k: [] for k in ("gain", "score", "expected_gain", "expected_score", "star", "epoch", "shift")}
    for index, fit in enumerate(fitted):
        history = fit["history"]; first = int(history["development_n"])
        y = np.asarray(history["y"])[first:]
        truth = np.asarray(history["true_mean"])[first:]
        mu, z, variance = fit["baseline_mean"][first:], fit["z"][first:], fit["variance"][first:]
        shift = beta * z
        values = {"gain": shift * (y - mu) / variance - .5 * shift ** 2 / variance,
                  "score": z * (y - mu) / variance,
                  "expected_gain": shift * (truth - mu) / variance - .5 * shift ** 2 / variance,
                  "expected_score": z * (truth - mu) / variance,
                  "star": np.full(len(y), index, dtype=int),
                  "epoch": np.asarray(history["epoch"])[first:], "shift": shift}
        for key, value in values.items():
            records[key].append(value)
    return {"beta": beta, "fitted": fitted, **{k: np.concatenate(v) for k, v in records.items()}}


def weighted_cr1(values, stars, epochs, *, clustering="halves", cap=.4):
    values, stars, epochs = map(np.asarray, (values, stars, epochs))
    if values.ndim != 1 or len(stars) != len(values) or len(epochs) != len(values) or np.any(~np.isfinite(values)):
        raise ValueError("invalid statistic vectors")
    if np.any(epochs < 0) or np.any(epochs > 5) or np.any(epochs != np.floor(epochs)):
        raise ValueError("evaluation epochs must be integers zero through five")
    labels, counts = np.unique(stars, return_counts=True)
    if not np.array_equal(labels, np.arange(len(labels))):
        raise ValueError("star labels must be consecutive from zero")
    weights = capped_star_weights(counts, cap)
    row_weight = weights[stars] / counts[stars]
    estimate = float(np.dot(row_weight, values))
    if clustering == "halves":
        group = stars * 2 + (epochs // 3)
    elif clustering == "star":
        group = stars
    else:
        raise ValueError("unknown clustering; use halves or star")
    _, group_index = np.unique(group, return_inverse=True)
    groups = int(group_index.max()) + 1
    if groups < 2:
        raise ValueError("insufficient independent-cluster analogue")
    sums = np.bincount(group_index, weights=row_weight * (values - estimate))
    se = math.sqrt(groups / (groups - 1) * float(np.dot(sums, sums)))
    radius = float(student_t.ppf(.95, groups - 1)) * se
    statistic = estimate / se if se > 0 else None
    reject = statistic > float(student_t.ppf(.95, groups - 1)) if statistic is not None else estimate > 0
    return {"estimate": estimate, "se": se, "lower90": estimate - radius, "upper90": estimate + radius,
            "statistic": statistic, "reject_one_sided": bool(reject), "clusters": groups,
            "df": groups - 1, "maximum_star_weight": float(weights.max()),
            "zero_variance": se == 0., "clustering": clustering}


def _stationary_process(rng, count, phi):
    value = rng.normal(size=count)
    if phi == 0:
        return value
    for i in range(1, count):
        value[i] = phi * value[i - 1] + math.sqrt(1 - phi ** 2) * value[i]
    return value


def generate_histories(config, rng):
    stars = int(config.get("stars", 5)); total = int(config.get("test_forecasts", 1100))
    counts = allocate_counts(total, stars, config.get("allocation", "balanced"))
    ndev = int(config.get("development_per_star", 100))
    sigma = float(config.get("sigma", .35)); phi = float(config.get("block_ar", 0.))
    mark_icc = float(config.get("mark_icc", 0.)); residual_icc = float(config.get("residual_icc", 0.))
    common = float(config.get("cross_star_correlation", 0.))
    reliability = float(config.get("mark_reliability", 1.)); missing = float(config.get("missing_mark_fraction", 0.))
    residual_ar = float(config.get("residual_ar", 0.))
    if (not sigma > 0 or not abs(phi) < 1 or not abs(residual_ar) < 1 or residual_icc == 1
            or any(not 0 <= value <= 1 for value in (mark_icc, residual_icc, common, reliability, missing))):
        raise ValueError("invalid stochastic-process settings")
    delay = float(config.get("outcome_delay_days", 0.))
    delay_probability = float(config.get("outcome_delay_probability", 1.))
    if delay < 0 or not math.isfinite(delay):
        raise ValueError("invalid report availability delay")
    if not 0 <= delay_probability <= 1:
        raise ValueError("invalid report delay probability")
    effect = sigma * math.sqrt(2 * float(config.get("nominal_oracle_gain", .004)))
    multipliers = np.asarray(config.get("effect_profile", np.ones(stars)), dtype=float)
    if multipliers.shape != (stars,) or np.any(~np.isfinite(multipliers)):
        raise ValueError("effect multipliers must name every star")
    all_epochs = [np.floor((np.arange(ndev + n) - ndev) * 6 / n).astype(int) for n in counts]
    first = min(epoch.min() for epoch in all_epochs)
    block_count = 6 - first
    common_mark = _stationary_process(rng, block_count, phi)
    common_error = _stationary_process(rng, block_count, phi)
    histories = []
    for star, (n_test, epochs) in enumerate(zip(counts, all_epochs)):
        n = ndev + n_test
        mark_state = math.sqrt(common) * common_mark + math.sqrt(1 - common) * _stationary_process(rng, block_count, phi)
        error_state = math.sqrt(common) * common_error + math.sqrt(1 - common) * _stationary_process(rng, block_count, phi)
        loading = float(config.get("shared_state_loading", 0.))
        shared_ar = float(config.get("shared_state_ar", .95))
        if not abs(shared_ar) < 1:
            raise ValueError("invalid shared-state persistence")
        q = _stationary_process(rng, n, shared_ar) if loading else np.zeros(n)
        latent = (math.sqrt(mark_icc) * mark_state[epochs - first] + math.sqrt(1 - mark_icc) * rng.normal(size=n)
                  + loading * q) / math.sqrt(1 + loading ** 2)
        progress = np.maximum(0., np.arange(n) - ndev) / max(1, n_test - 1)
        test = np.arange(n) >= ndev
        latent += test * float(config.get("mark_shift", 0.)) + progress * float(config.get("mark_trend", 0.))
        y, true_mean, raw_base, issue = np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n)
        prefix = np.zeros(n + 1)
        mean = math.log(float(config.get("median_gap_days", 40.))) + .12 * star
        beta = effect * multipliers[star]
        noise = _stationary_process(rng, n, residual_ar)
        innovations = (noise - np.r_[0., residual_ar * noise[:-1]]) / math.sqrt(1 - residual_ar ** 2)
        innovations[0] = noise[0]
        innovation_sd = np.full(n, sigma * math.sqrt((1 - residual_icc) * (1 - residual_ar ** 2)))
        innovation_sd[0] = sigma * math.sqrt(1 - residual_icc)
        history_correlation = float(config.get("mark_history_correlation", 0.))
        if not -1 <= history_correlation <= 1:
            raise ValueError("invalid mark/history loading")
        development_multiplier = float(config.get("development_effect_multiplier", 1.))
        for i in range(n):
            previous = y[i - 1] - mean if i else 0.
            first_older = max(0, i - 6)
            old_count = i - 1 - first_older
            older = (prefix[i - 1] - prefix[first_older]) / old_count - mean if old_count > 0 else 0.
            latent[i] = math.sqrt(1 - history_correlation ** 2) * latent[i] + history_correlation * previous / sigma
            base = mean + float(config.get("gap_ar", .3)) * previous + float(config.get("history_effect", .2)) * older
            base += sigma * (float(config.get("level_shift", 0.)) * test[i]
                             + float(config.get("level_trend", 0.)) * progress[i]
                             + float(config.get("level_state_sd", 0.)) * error_state[epochs[i] - first])
            base += sigma * loading * q[i]
            base += sigma * math.sqrt(residual_icc) * error_state[epochs[i] - first]
            base += sigma * math.sqrt(1 - residual_icc) * (residual_ar * noise[i - 1] if i else 0.)
            raw_base[i] = base
            true_mean[i] = base + beta * (development_multiplier if i < ndev else 1.) * latent[i]
            y[i] = true_mean[i] + innovation_sd[i] * innovations[i]
            prefix[i + 1] = prefix[i] + y[i]
            if i:
                issue[i] = issue[i - 1] + math.exp(y[i - 1]) + float(config.get("bright_phase_days", 10.))
        mark = math.sqrt(reliability) * latent + math.sqrt(1 - reliability) * rng.normal(size=n)
        mark[rng.random(n) < missing] = np.nan
        delayed = rng.random(n) < delay_probability
        available = issue + np.exp(y) + delay * delayed
        histories.append({"star": star, "development_n": ndev, "issue": issue,
                          "outcome_available_at": available, "y": y, "mark": mark,
                          "true_mean": true_mean, "true_mean_without_direct_mark": raw_base,
                          "epoch": epochs, "sigma": sigma, "direct_beta": beta,
                          "innovation_variance": innovation_sd ** 2})
    return histories


def trial(config, seed, return_vectors=False):
    histories = generate_histories(config, np.random.default_rng(seed))
    fitted = forecast_trial(histories, level_window=int(config.get("level_window", 20)),
                            mark_window=int(config.get("mark_window", 10)), minimum_marks=int(config.get("minimum_marks", 3)),
                            recalibrate=bool(config.get("recalibrate", True)), guard_marks=bool(config.get("guard_marks", True)),
                            oracle=bool(config.get("oracle_base", False)))
    counts = np.bincount(fitted["star"])
    weights = capped_star_weights(counts)
    row_weight = weights[fitted["star"]] / counts[fitted["star"]]
    expected_gain = float(np.dot(row_weight, fitted["expected_gain"]))
    expected_score = float(np.dot(row_weight, fitted["expected_score"]))
    information = np.concatenate([s["z"][int(s["history"]["development_n"]):] ** 2 /
                                  s["variance"][int(s["history"]["development_n"]):] for s in fitted["fitted"]])
    mean_information = float(np.dot(row_weight, information))
    methods = {}
    for clustering in ("halves", "star"):
        gain = weighted_cr1(fitted["gain"], fitted["star"], fitted["epoch"], clustering=clustering)
        score = weighted_cr1(fitted["score"], fitted["star"], fitted["epoch"], clustering=clustering)
        gain["covers_conditional_expected_gain"] = gain["lower90"] <= expected_gain <= gain["upper90"]
        methods[clustering] = {"gain": gain, "score": score}
    result = {"methods": methods, "beta_hat": fitted["beta"], "gain_identity": bool(np.all(fitted["shift"] == 0.)),
              "conditional_expected_gain": expected_gain, "conditional_expected_score": expected_score,
              "conditional_local_signal_projection": expected_score / mean_information if mean_information > 0 else None,
              "mean_mark_information": mean_information,
              "nominal_direct_oracle_gain": float(np.dot(weights, [h["direct_beta"] ** 2 / (2 * h["sigma"] ** 2) for h in histories])),
              "expected_target": "realized-path predictable averages given generator latent state and each frozen forecast; not unconditional long-run KL",
              "test_forecasts": int(sum(counts)), "stars": len(counts), "star_counts": counts.tolist(),
              "markable_evaluation": sum(int(s["mark_usable"][int(s["history"]["development_n"]):].sum()) for s in fitted["fitted"]),
              "development_supported": sum(s["model"]["training_outcomes"] for s in fitted["fitted"]),
              "development_timing_supported": sum(s["model"]["timing_training_outcomes"] for s in fitted["fitted"]),
              "development_contributing_stars": sum(bool((s["training"] & s["mark_usable"]).any()) for s in fitted["fitted"]),
              "scientific_null_class": config.get("null_class", "unspecified"),
              "direct_effect_zero": all(h["direct_beta"] == 0 for h in histories),
              "scope": "Gaussian point-log-gap stress model; nominal equal-count epoch halves, not calendar/X5 validation",
              "limits": ["unbounded Gaussian least-squares B0 form, not original interval/survival fitting",
                         "mark_history_correlation is a standardized previous-gap loading, not a guaranteed realized correlation",
                         "oracle base knows generator latent mean and innovation variance and receives no estimated level correction",
                         "development beta uses normalized capped star weights among mark-usable contributors; fewer than three give zero offset",
                         "recalibration selects latest issuance among available outcomes, not latest report arrivals",
                         "no-direct-effect shared-state/trend cases are specificity stresses rather than strict predictive nulls"]}
    if return_vectors:
        return result, fitted
    return result
