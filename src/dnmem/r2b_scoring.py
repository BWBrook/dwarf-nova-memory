"""R2b common outcome association and exploratory paired-score diagnostics.

The outcome clock is separate from every predictor. Candidate obstructions are
retained, and neither missing evidence nor a sampling-dependent censor proves
survival of the latent target. Fixed-cutoff bounds remain conditional on the
declared association, containment and survival assumptions.
"""

from __future__ import annotations

from collections import Counter
import math
from statistics import fmean

from scipy.stats import t as student_t

from .extract import visits
from .extract_x5 import decisive_visits, x5_episodes
from .r2_scores import (mixed_score_bounds, right_censored_contrast,
                        route_compatibility_window, working_interval_contrast)

ORIGIN = 2436934.5
COVERAGE_HOLE = 7.0
DEFINITION_VERSION = "r2b-common-outcomes-v1"


def _finite(value):
    return value is not None and math.isfinite(float(value))


def _index(rows):
    indexed = {row["emission_index"]: row for row in rows}
    if len(indexed) != len(rows):
        raise ValueError("duplicate issuance identity")
    return indexed


def _coverage_loss(times, issue, stop):
    earlier = [time for time in times if time <= issue]
    anchors = [earlier[-1] if earlier else issue]
    anchors += [time for time in times if issue < time < stop]
    anchors.append(stop)
    return next((max(issue, left) for left, right in zip(anchors, anchors[1:])
                 if right - left > COVERAGE_HOLE and right > issue), None)


def outcome_evidence(rows, ledger, *, stop, threshold=10., include_flagged=False,
                     candidates=None, observation_times=None):
    """Associate the first all-candidate peak after the original bright phase.

    Candidate injection is for independently constructed synthetic checks. The
    production path reconstructs X5 from the supplied record as of ``stop``.
    Unsupported or unconfirmed candidates obstruct association; they are never
    skipped to credit a later confirmed episode. A missing candidate permits a
    working censor, under an explicit absence/survival assumption.
    """
    stop = float(stop)
    if not math.isfinite(stop):
        raise ValueError("record cutoff must be finite")
    _index(ledger)
    if any(not _finite(row["issue_time"]) for row in ledger):
        raise ValueError("nonfinite issuance time")
    if any(right["issue_time"] <= left["issue_time"] for left, right in zip(ledger, ledger[1:])):
        raise ValueError("issuances must be strictly ordered")
    observed = [row for row in rows if float(row["JD"]) < stop]
    if candidates is None:
        closed = [v for v in decisive_visits(observed, threshold) if v["available_at"] <= stop]
        identifiers = {identifier for visit in closed for identifier in visit["ids"]}
        observed = [row for row in observed if row["obsID"] in identifiers]
        episodes = x5_episodes(observed, threshold)
    else:
        episodes = candidates
        for episode in episodes:
            support = [episode.get(key) for key in ("peak_t", "onset_report_lo", "onset_report_hi", "onset_t",
                       "onset_lower_first_at", "onset_lower_last_at", "onset_upper_first_at", "onset_upper_last_at")]
            availability = episode.get("onset_upper_first_at")
            if any(value is not None and (not _finite(value) or float(value) >= stop) for value in support):
                raise ValueError("injected candidate support is not from the as-of record")
            if availability is not None and float(availability) + .15 > stop:
                raise ValueError("injected candidate visit has not closed by the as-of cutoff")
            if episode.get("computed_as_of", stop) > stop:
                raise ValueError("injected candidates use later-record information")
    if any(not _finite(e["peak_t"]) for e in episodes) or any(
            b["peak_t"] <= a["peak_t"] for a, b in zip(episodes, episodes[1:])):
        raise ValueError("all-candidate peaks must be finite and strictly ordered")
    times = (sorted(v["t"] for v in visits(observed, threshold)) if observation_times is None
             else sorted(float(time) for time in observation_times if float(time) < stop))
    if not all(math.isfinite(time) for time in times):
        raise ValueError("nonfinite coverage time")
    out, assigned = [], set()
    for position, feature in enumerate(ledger):
        issue = float(feature["issue_time"])
        reference = feature.get("original_last_bright_at")
        if not _finite(reference) or float(reference) > issue:
            raise ValueError("original bright phase must be known by issue")
        candidate = next(((j, e) for j, e in enumerate(episodes) if e["peak_t"] > reference), None)
        following_issue = ledger[position + 1]["issue_time"] if position + 1 < len(ledger) else None
        loss = _coverage_loss(times, issue, stop) if issue < stop else None
        stops = [(stop, "record_end")]
        stops += [(time, why) for time, why in ((loss, "coverage"), (following_issue, "superseded"))
                  if time is not None]
        cutoff, why = min(stops, key=lambda pair: (pair[0], pair[1]))
        evidence = {
            "definition_version": DEFINITION_VERSION, "emission_index": feature["emission_index"],
            "issue_time": issue, "computed_as_of": stop, "evidence_available_at": stop,
            "administrative_stop": stop, "fixed_cutoff": cutoff, "fixed_cutoff_kind": why,
            "cutoff_independence_established": False, "coverage_loss_at": loss,
            "superseded_at": following_issue, "kind": "excluded", "reason": None,
            "candidate_all_index": candidate[0] if candidate else None,
            "candidate_peak_at": candidate[1]["peak_t"] if candidate else None,
            "onset_lo": None, "onset_hi": None, "onset_t": None, "censor_at": None,
            "window_flags": [], "window_eligible": None,
            "censor_backoff": False, "censor_backoff_days": 0.,
            "latent_survival_verified": False,
            "association_policy": "first_all_candidate_peak_after_original_last_bright",
        }
        if issue >= stop:
            evidence["reason"] = "outside_record"
            out.append(evidence)
            continue
        if candidate is None:
            evidence.update(kind="right_censored", reason=why + ":no_candidate", censor_at=cutoff)
            out.append(evidence)
            continue
        index, episode = candidate
        evidence.update(onset_lo=episode.get("onset_report_lo"), onset_hi=episode.get("onset_report_hi"),
                        onset_t=episode.get("onset_t"), window_flags=list(episode.get("onset_flags", [])),
                        window_eligible=bool(episode.get("onset_report_eligible", False)))
        if not episode.get("confirmed_event", False):
            evidence["reason"] = "unconfirmed_adjacent_candidate"
        elif not episode.get("onset_report_available", False):
            evidence["reason"] = "unsupported_adjacent_candidate:" + episode.get("onset_status", "missing_window")
        elif not evidence["window_eligible"] and not include_flagged:
            evidence["reason"] = "flagged_adjacent_window"
        else:
            route = route_compatibility_window(evidence["onset_lo"], evidence["onset_hi"], issue, cutoff)
            if route["status"] != "usable":
                evidence["reason"] = route["status"]
            else:
                evidence.update(kind=route["kind"], censor_at=route["censor_at"],
                                censor_backoff=route["censor_backoff"],
                                censor_backoff_days=route["censor_backoff_days"],
                                reason="onset" if route["kind"] == "interval" else why + ":" +
                                ("straddle_backoff" if route["censor_backoff"] else "candidate_after_cutoff"))
                if route["kind"] == "interval":
                    if index in assigned:
                        raise ValueError("candidate onset credited to multiple forecasts")
                    assigned.add(index)
        out.append(evidence)
    return out


def _signature(evidence):
    keys = ("issue_time", "kind", "reason", "administrative_stop", "fixed_cutoff", "fixed_cutoff_kind",
            "candidate_all_index", "candidate_peak_at", "onset_lo", "onset_hi", "onset_t", "censor_at",
            "window_eligible", "censor_backoff", "censor_backoff_days")
    return {**{key: evidence.get(key) for key in keys}, "window_flags": list(evidence.get("window_flags", []))}


def score_contrast(features, evidence, rule):
    """Score base/marked forecasts from ``rule.predict(row, with_mark=...)``.

    ``gain`` uses supported observations only. ``known_contrast`` additionally
    records algebraic zero for an exactly identical forecast with unsupported
    evidence; it must never be described as another observed score.
    """
    source, outcomes = _index(features), _index(evidence)
    if source.keys() != outcomes.keys():
        raise ValueError("feature/outcome population mismatch")
    result = []
    for feature in features:
        ev = outcomes[feature["emission_index"]]
        if feature["issue_time"] != ev["issue_time"]:
            raise ValueError("feature/outcome issue mismatch")
        base, base_route = rule.predict(feature, with_mark=False)
        marked, marked_route = rule.predict(feature, with_mark=True)
        if (base.issue != feature["issue_time"] or marked.issue != base.issue or marked.anchor != base.anchor):
            raise ValueError("forecast pair has different issue or anchor")
        identity = (base.anchor, base.issue, base.mu, base.sigma) == (
            marked.anchor, marked.issue, marked.mu, marked.sigma)
        row = {"emission_index": feature["emission_index"], "issue_time": feature["issue_time"],
               "outcome_signature": _signature(ev), "status": ev["kind"], "reason": ev["reason"],
               "base_route": base_route, "marked_route": marked_route,
               "base_clock": {k: getattr(base, k) for k in ("anchor", "issue", "mu", "sigma")},
               "marked_clock": {k: getattr(marked, k) for k in ("anchor", "issue", "mu", "sigma")},
               "identical_forecasts": identity, "identity_gain": 0. if identity else None,
               "gain": None, "known_contrast": 0. if identity else None,
               "baseline_score": None, "marked_score": None, "bounds_lower": None, "bounds_upper": None,
               "point_gain": None, "point_status": "unavailable", "propriety_established": False}
        if ev["kind"] == "excluded":
            result.append(row)
            continue
        if ev["kind"] not in ("interval", "right_censored"):
            raise ValueError("unsupported outcome kind")
        has_window = ev.get("onset_lo") is not None and ev.get("onset_hi") is not None
        if has_window:
            working = working_interval_contrast(base, marked, ev["onset_lo"], ev["onset_hi"], ev["fixed_cutoff"])
            bounds = mixed_score_bounds(base, marked, ev["onset_lo"], ev["onset_hi"], ev["fixed_cutoff"])
        else:
            if ev["kind"] != "right_censored":
                raise ValueError("event evidence lacks a window")
            working = right_censored_contrast(base, marked, ev["censor_at"])
            bounds = {"status": working["status"], "lower": working.get("gain"), "upper": working.get("gain")}
        if working["status"] != "usable" or bounds["status"] != "usable":
            raise ArithmeticError("R2b score or bound failed numerically: " + repr((working, bounds)))
        if working["kind"] != ev["kind"] or working.get("censor_at") != ev.get("censor_at"):
            raise ValueError("saved outcome and working score routes disagree")
        row.update(status="scored", gain=working["gain"], known_contrast=working["gain"],
                   baseline_score=working["scores"]["baseline"], marked_score=working["scores"]["duration"],
                   bounds_lower=bounds["lower"], bounds_upper=bounds["upper"],
                   bound_scope="fixed_observation_cutoff_mixed_functional_conditional_on_A0_A1_and_survival")
        if feature.get("clock") != "point":
            row["point_status"] = "not_a_point_clock_sensitivity"
        elif ev["kind"] == "right_censored":
            row.update(point_gain=working["gain"], point_status="same_working_censor_survival")
        elif _finite(ev.get("onset_t")) and base.issue < ev["onset_t"] <= ev["fixed_cutoff"]:
            values = [clock.log_density(ev["onset_t"]) for clock in (base, marked)]
            if not all(math.isfinite(value) for value in values):
                raise ArithmeticError("nonfinite point-density sensitivity")
            row.update(point_gain=values[1] - values[0], point_status="saved_X4_point_density")
        else:
            row["point_status"] = "saved_X4_point_missing_or_outside_issue_cutoff"
        if identity and any(row[k] != 0. for k in ("gain", "bounds_lower", "bounds_upper")):
            raise ArithmeticError("identical forecasts do not nest exactly")
        result.append(row)
    return result


def paired_clock_gain(df_scores, point_scores):
    """Difference in incremental gains on precisely matched issues/outcomes."""
    left, right = _index(df_scores), _index(point_scores)
    if left.keys() != right.keys():
        raise ValueError("cross-clock issuance populations differ")
    result = []
    for a in df_scores:
        b = right[a["emission_index"]]
        if a["issue_time"] != b["issue_time"] or a["outcome_signature"] != b["outcome_signature"]:
            raise ValueError("cross-clock issue/outcome mismatch")
        both = a["gain"] is not None and b["gain"] is not None
        known = a["known_contrast"] is not None and b["known_contrast"] is not None
        bounded = a["bounds_lower"] is not None and b["bounds_lower"] is not None
        result.append({"emission_index": a["emission_index"], "issue_time": a["issue_time"],
                       "outcome_signature": a["outcome_signature"], "status": "scored" if both else "excluded",
                       "gain": a["gain"] - b["gain"] if both else None,
                       "known_contrast": a["known_contrast"] - b["known_contrast"] if known else None,
                       "bounds_lower": a["bounds_lower"] - b["bounds_upper"] if bounded else None,
                       "bounds_upper": a["bounds_upper"] - b["bounds_lower"] if bounded else None,
                       "bound_scope": "difference_of_marginal_bounds_on_common_event; conservative_sample_envelope"})
    return result


def autocorrelations(values, maximum_lag=10):
    """Biased sample ACF with original sequence slots retained when missing."""
    if maximum_lag < 0:
        raise ValueError("negative maximum lag")
    valid = [float(value) for value in values if value is not None]
    if not all(math.isfinite(value) for value in valid):
        raise ValueError("nonfinite ACF value")
    center = fmean(valid) if valid else None
    denominator = sum((value - center) ** 2 for value in valid) if valid else 0.
    rows = []
    for lag in range(1, maximum_lag + 1):
        pairs = [(float(values[i]), float(values[i + lag])) for i in range(max(0, len(values) - lag))
                 if values[i] is not None and values[i + lag] is not None]
        value = (sum((left - center) * (right - center) for left, right in pairs) / denominator
                 if denominator > 0 and pairs else None)
        rows.append({"lag": lag, "pairs": len(pairs), "acf": value})
    return {"n_slots": len(values), "n_available": len(valid), "mean": center,
            "constant_or_insufficient": denominator == 0., "lags": rows,
            "method": "global-mean biased ACF; missing original slots retained; descriptive"}


def calendar_interval(rows, field="gain", *, origin=ORIGIN, years=6, weight_field=None):
    """Weighted mean and CR1/t interval using actual nonempty calendar groups."""
    if not math.isfinite(origin) or not math.isfinite(years) or years <= 0:
        raise ValueError("invalid cluster origin/width")
    groups, ordered = {}, sorted(rows, key=lambda row: row["issue_time"])
    if any(not _finite(row["issue_time"]) for row in ordered):
        raise ValueError("nonfinite cluster time")
    for row in ordered:
        value = row.get(field)
        if value is None:
            continue
        weight = float(row[weight_field]) if weight_field else 1.
        if not _finite(value) or not math.isfinite(weight) or weight <= 0:
            raise ValueError("nonfinite score or invalid weight")
        index = math.floor((row["issue_time"] - origin) / (years * 365.25))
        groups.setdefault(index, []).append((float(value), weight))
    total = sum(weight for values in groups.values() for _, weight in values)
    count, blocks = sum(map(len, groups.values())), len(groups)
    mean = sum(value * weight for values in groups.values() for value, weight in values) / total if total else None
    records = [{"block": index, "n": len(values), "weight": sum(w for _, w in values),
                "mean": sum(v * w for v, w in values) / sum(w for _, w in values)}
               for index, values in sorted(groups.items())]
    acf_values = ([next((r["mean"] for r in records if r["block"] == j), None)
                   for j in range(min(groups), max(groups) + 1)] if groups else [])
    result = {"status": "usable" if blocks >= 2 else "insufficient_clusters", "n": count,
              "issued": len(rows), "missing": len(rows) - count, "blocks": blocks, "df": blocks - 1 if blocks else None,
              "years": years, "origin": origin, "total_weight": total, "estimate": mean,
              "se": None, "lower": None, "upper": None, "block_means": records,
              "block_mean_acf": autocorrelations(acf_values, 1),
              "interval": "exploratory CR1/t 90%; independent-cluster assumption not certified"}
    if blocks >= 2:
        variance = blocks / (blocks - 1) * sum(
            sum(weight * (value - mean) for value, weight in values) ** 2 for values in groups.values()) / total ** 2
        se = math.sqrt(max(0., variance))
        radius = float(student_t.ppf(.95, blocks - 1)) * se
        result.update(se=se, lower=mean - radius, upper=mean + radius)
    return result


def aggregate_contrast(rows, field="gain", *, origin=ORIGIN, weight_field=None):
    ordered = sorted(rows, key=lambda row: row["issue_time"])
    six = calendar_interval(ordered, field, origin=origin, years=6, weight_field=weight_field)
    twelve = calendar_interval(ordered, field, origin=origin, years=12, weight_field=weight_field)
    if six["lower"] is not None and twelve["lower"] is not None and min(six["lower"], twelve["lower"]) > 0:
        interpretation = "positive under both blockings; exploratory"
    elif six["estimate"] is not None and six["estimate"] > 0:
        interpretation = "positive estimate, dependence-sensitive"
    else:
        interpretation = "uncertain"
    return {"field": field, "six_year": six, "twelve_year": twelve,
            "forecast_acf": autocorrelations([row.get(field) for row in ordered]),
            "statuses": dict(Counter(row.get("status", "unknown") for row in rows)),
            "interpretation": interpretation, "confirmation": False}


def residual_diagnostics(features, evidence, rule, *, origin=ORIGIN, years=6):
    """Untruncated working log residuals at interval midpoints, not latent errors."""
    source, outcomes = _index(features), _index(evidence)
    if source.keys() != outcomes.keys():
        raise ValueError("residual feature/outcome population mismatch")
    residuals, reasons = [], Counter()
    for feature in sorted(features, key=lambda row: row["issue_time"]):
        ev = outcomes[feature["emission_index"]]
        if feature["issue_time"] != ev["issue_time"]:
            raise ValueError("residual issue mismatch")
        value = None
        if ev["kind"] != "interval":
            reasons[ev["kind"]] += 1
        else:
            clock, _ = rule.predict(feature, with_mark=False)
            midpoint = (ev["onset_lo"] + ev["onset_hi"]) / 2
            if midpoint <= clock.issue or midpoint <= clock.anchor:
                reasons["midpoint_outside_predictive_support"] += 1
            else:
                value = (math.log(midpoint - clock.anchor) - clock.mu) / clock.sigma
        residuals.append({"issue_time": feature["issue_time"], "residual_proxy": value})
    grouping = calendar_interval(residuals, "residual_proxy", origin=origin, years=years)
    groups = {}
    for row in residuals:
        if row["residual_proxy"] is not None:
            key = math.floor((row["issue_time"] - origin) / (years * 365.25))
            groups.setdefault(key, []).append(row["residual_proxy"])
    n, k = sum(map(len, groups.values())), len(groups)
    icc, icc_status = None, "insufficient_groups_or_within_group_degrees"
    if k >= 2 and n > k:
        mean = fmean(value for group in groups.values() for value in group)
        ms_between = sum(len(g) * (fmean(g) - mean) ** 2 for g in groups.values()) / (k - 1)
        ms_within = sum((value - fmean(g)) ** 2 for g in groups.values() for value in g) / (n - k)
        effective_size = (n - sum(len(g) ** 2 for g in groups.values()) / n) / (k - 1)
        denominator = ms_between + (effective_size - 1) * ms_within
        if denominator > 0:
            icc, icc_status = (ms_between - ms_within) / denominator, "descriptive_one_way_ANOVA"
        else:
            icc_status = "constant_residual_proxy"
    return {"scope": "interval-midpoint untruncated log-residual proxies; not latent forecast errors or calibration",
            "n": n, "excluded": dict(reasons), "block_icc": icc, "icc_status": icc_status,
            "block_summary": grouping,
            "forecast_acf": autocorrelations([r["residual_proxy"] for r in residuals]),
            "limitations": ["midpoints ignore interval uncertainty", "censored/unsupported rows have no residual proxy",
                            "survival-to-issue truncation and interval selection affect these summaries"]}
