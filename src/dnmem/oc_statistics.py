"""Predeclared forecast-gain and Monte Carlo calibration calculations."""

import math
from statistics import fmean, stdev

from scipy.stats import beta, binom, t


def cluster_interval(rows, field, origin, years=6):
    values = [(float(row["issue_time"]), float(row[field])) for row in rows
              if row.get(field) is not None]
    if not values:
        raise ValueError("no scored issuances")
    if years <= 0 or any(time < origin for time, _ in values):
        raise ValueError("invalid cluster origin or width")
    clusters = {}
    for time, value in values:
        if not math.isfinite(value):
            raise ValueError("nonfinite gain")
        clusters.setdefault(math.floor((time-origin)/(years*365.25)), []).append(value)
    mean = fmean(value for _, value in values)
    count, blocks = len(values), len(clusters)
    if blocks < 2:
        raise ValueError("at least two nonempty calendar clusters are required")
    variance = blocks/(blocks-1) * sum((sum(v)-mean*len(v))**2 for v in clusters.values()) / count**2
    se = math.sqrt(max(0., variance))
    radius = float(t.ppf(.95, blocks-1))*se
    return {"n": count, "blocks": blocks, "years": years, "origin": origin,
            "estimate": mean, "se": se, "lower": mean-radius, "upper": mean+radius,
            "confirmed": mean-radius > 0,
            "interval": "one-sided 95% lower bound / two-sided 90% interval"}


def binomial_summary(successes, count):
    if not 0 <= successes <= count or count <= 0:
        raise ValueError("invalid binomial counts")
    rate = successes/count
    return {"successes": successes, "trials": count, "rate": rate,
            "mc_se": math.sqrt(rate*(1-rate)/count),
            "exact_lower95": float(beta.ppf(.025, successes, count-successes+1)) if successes else 0.,
            "exact_upper95": float(beta.ppf(.975, successes+1, count-successes)) if successes < count else 1.,
            "one_sided_upper95": float(beta.ppf(.95, successes+1, count-successes)) if successes < count else 1.}


def reference_calibration(interval, reference_means, exact_identity=False):
    if exact_identity:
        if interval["estimate"] != 0 or interval["se"] != 0:
            raise ValueError("identity forecast must have exactly zero gain and variance")
        return {"method": "analytic_zero_identity", "reference_mean": 0., "reference_se": 0.,
                "joint_mc_covers_zero": True, "naive_reference_contained": True,
                "reference_means": [], "interior": False}
    if len(reference_means) != 6 or not all(math.isfinite(value) for value in reference_means):
        raise ValueError("six matched independent reference means are required")
    mean = fmean(reference_means)
    reference_se = stdev(reference_means)/math.sqrt(len(reference_means))
    v, u = interval["se"]**2, reference_se**2
    variance = v+u
    denominator = v*v/(interval["blocks"]-1) + u*u/(len(reference_means)-1)
    degrees = variance**2/denominator if denominator else None
    radius = float(t.ppf(.95, degrees))*math.sqrt(variance) if degrees else 0.
    difference = interval["estimate"]-mean
    return {"method": "matched_58y_replicas_joint_mc", "reference_mean": mean,
            "reference_se": reference_se, "reference_means": list(reference_means),
            "joint_mc_df": degrees, "difference": difference,
            "joint_mc_lower": difference-radius, "joint_mc_upper": difference+radius,
            "joint_mc_covers_zero": difference-radius <= 0 <= difference+radius,
            "naive_reference_contained": interval["lower"] <= mean <= interval["upper"],
            "interior": True,
            "scope": "joint Monte Carlo calibration; finite reference is not exact conditional truth"}


def coverage_screen(records):
    count = len(records)
    if count == 0:
        raise ValueError("empty calibration case")
    covered = sum(row["joint_mc_covers_zero"] for row in records)
    interior = [row for row in records if row["interior"]]
    interior_covered = sum(row["joint_mc_covers_zero"] for row in interior)
    p_all = float(binom.cdf(covered, count, .9))
    p_interior = float(binom.cdf(interior_covered, len(interior), .9)) if interior else None
    return {"overall": binomial_summary(covered, count),
            "interior": binomial_summary(interior_covered, len(interior)) if interior else None,
            "undercoverage_p": p_all, "interior_undercoverage_p": p_interior,
            "pass": p_all > .05 and (p_interior is None or p_interior > .05),
            "meaning": "no undercoverage detected by predeclared joint-MC screens; not a coverage guarantee"}
