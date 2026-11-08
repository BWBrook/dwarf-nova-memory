#!/usr/bin/env python3
"""A04h joint morphology targets (Claude): a predictive check of benchmark families against the open era.

One operator runs on real 1910-1959 rows and on synthetic "real-sized" replicates
(one history per era, pooled, like the real record). It measures twelve joint
statistics of X1-selected episodes in two blocks. The waveform block holds the
core (mid-outburst) level, rise and decline slopes at 10.0, scatter about the
decline, slope symmetry about the threshold, and rank correlations of slopes
and core level with duration. The cadence block holds event rate, median
duration and the fractions of episodes with enough estimates near the
decline to fit a slope. A family
passes a block when the real vector is typical of its replicate distribution:
Hotelling T^2 within the 99% prediction region, and no single statistic beyond
|z| = 3.3.
Tolerances therefore come from sampling variability at the real sample size,
not fixed margins. No duration-gap association is computed. Needs the
gitignored A04g input cache and native exports.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import math
from pathlib import Path
import statistics as st
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

J1910, J1960, THR = 2418672.5, 2436934.5, 10.0
BASE = "a04h-claude-morphology-targets-20261108"
STRATA = ("1910_1929", "1930_1949", "1950_1959")
CONFIGS = (("v2", "random"), ("v2", "diverse"), ("v3", "random"), ("v3", "diverse"))
WAVEFORM = ("core_level_mean", "rise_slope_median", "end_slope_median", "end_residual_sd_median",
            "log_below_above_slope_ratio", "rho_duration_end_slope", "rho_duration_rise_slope", "rho_duration_core_level")
CADENCE = ("episodes_per_year", "duration_median", "above_fit_fraction", "below_fit_fraction")
NAMES = WAVEFORM + CADENCE
Z_MAX = 3.3
STATE = {}


def theil_sen(points):
    if len(points) < 4 or max(x for x, _ in points) - min(x for x, _ in points) < 0.4:
        return None
    slopes = [(y2 - y1) / (x2 - x1) for i, (x1, y1) in enumerate(points) for x2, y2 in points[i + 1:] if x2 - x1 > 0.05]
    if len(slopes) < 3:
        return None
    s = st.median(slopes)
    a = st.median(y - s * x for x, y in points)
    return s, 1.4826 * st.median(abs(y - a - s * x) for x, y in points)


def features(rows):
    """Codex's A04d/A04e operator (validation_morphology.records) plus peak level and rise slope."""
    from dnmem.extract import visits, x1_vote_episodes
    votes = [v for v in visits(rows, THR) if v["value"] is not None]
    out = []
    for e in x1_vote_episodes(rows, threshold=THR):
        if not e["confirmed_event"] or e["gap_split"] or None in (e["onset_lo"], e["onset_hi"], e["end_lo"], e["end_hi"]):
            continue
        if not J1910 <= e["peak_t"] < J1960:
            continue
        on = [(v["t"] - e["onset_lo"], v["value"]) for v in votes if e["onset_lo"] - 1 <= v["t"] <= e["onset_hi"] + 1
              and v["t"] < e["peak_t"] and abs(v["value"] - THR) <= 1.0]
        end = [(v["t"] - e["end_lo"], v["value"]) for v in votes if e["end_lo"] - 2 <= v["t"] <= e["end_hi"] + 2
               and v["t"] > e["peak_t"] and abs(v["value"] - THR) <= 1.0]
        wide = [(v["t"] - e["end_lo"], v["value"]) for v in votes if e["end_lo"] - 3 <= v["t"] <= e["end_hi"] + 3
                and v["t"] > e["peak_t"]]
        third = (e["end_lo"] - e["onset_hi"]) / 3
        nightly = {}
        for v in votes:
            if e["onset_hi"] + third <= v["t"] <= e["end_lo"] - third:
                nightly.setdefault((v["observer"], math.floor(v["t"])), []).append(v["value"])
        levels = [st.median(x) for x in nightly.values()]
        out.append({"duration": (e["end_lo"] + e["end_hi"] - e["onset_lo"] - e["onset_hi"]) / 2,
                    "onset": theil_sen(on), "end": theil_sen(end),
                    "above": theil_sen([p for p in wide if THR - 1 <= p[1] <= THR]),
                    "below": theil_sen([p for p in wide if THR < p[1] <= THR + 1]),
                    "core": st.median(levels) if len(levels) >= 3 else None})
    return out


def ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    r = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(pairs):
    x, y = ranks([p[0] for p in pairs]), ranks([p[1] for p in pairs])
    mx, my = st.mean(x), st.mean(y)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / math.sqrt(
        sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))


def statistics(records, years):
    ends = [(r["duration"], r["end"]) for r in records if r["end"] and r["end"][0] > 0]
    rises = [(r["duration"], -r["onset"][0]) for r in records if r["onset"] and r["onset"][0] < 0]
    cores = [(r["duration"], r["core"]) for r in records if r["core"] is not None]
    above = [r["above"][0] for r in records if r["above"] and r["above"][0] > 0]
    below = [r["below"][0] for r in records if r["below"] and r["below"][0] > 0]
    return {"episodes_per_year": len(records) / years,
            "duration_median": st.median(r["duration"] for r in records),
            "core_level_mean": st.mean(c for _, c in cores),
            "rise_slope_median": st.median(s for _, s in rises),
            "end_slope_median": st.median(f[0] for _, f in ends),
            "end_residual_sd_median": st.median(f[1] for _, f in ends),
            "log_below_above_slope_ratio": math.log(st.median(below) / st.median(above)),
            "above_fit_fraction": len(above) / len(records),
            "below_fit_fraction": len(below) / len(records),
            "rho_duration_end_slope": spearman([(d, f[0]) for d, f in ends]),
            "rho_duration_rise_slope": spearman(rises),
            "rho_duration_core_level": spearman(cores)}


def init():
    STATE["inputs"] = json.loads((ROOT / "outputs/a04g_inputs_20261108/inputs.json").read_text())
    STATE["params"] = json.loads((ROOT / "configs/a04g_benchmark.json").read_text())


def replicate(task):
    """One real-sized synthetic record: one history per era, pooled."""
    from dnmem.x4_benchmark import observed_history
    family, phase, rep = task
    records, years = [], 0.0
    for stratum in STRATA:
        rows, _, _, s, _, _, _ = observed_history(STATE["inputs"], STATE["params"],
                                                  {"family": family, "case": "primary", "stratum": stratum,
                                                   "phase": phase, "replicate": rep}, BASE)
        records += features(rows)
        years += (min(float(s["stop"]), J1960) - max(float(s["start"]), J1910)) / 365.25
    return task, statistics(records, years)


def solve(matrix, vector):
    n = len(vector)
    a = [row[:] + [vector[i]] for i, row in enumerate(matrix)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(a[r][c]))
        a[c], a[p] = a[p], a[c]
        for r in range(n):
            if r != c:
                f = a[r][c] / a[c][c]
                a[r] = [x - f * y for x, y in zip(a[r], a[c])]
    return [a[i][n] / a[i][i] for i in range(n)]


def betainc(a, b, x):
    """Regularized incomplete beta by continued fraction (Numerical Recipes 6.4)."""
    if x <= 0 or x >= 1:
        return 0.0 if x <= 0 else 1.0
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x > (a + 1) / (a + b + 2):
        return 1.0 - betainc(b, a, 1 - x)
    c, d = 1.0, 1.0 - (a + b) * x / (a + 1)
    d = 1.0 / d
    f = d
    for m in range(1, 300):
        for numerator in (m * (b - m) * x / ((a + 2 * m - 1) * (a + 2 * m)),
                          -(a + m) * (a + b + m) * x / ((a + 2 * m) * (a + 2 * m + 1))):
            d = 1.0 + numerator * d
            c = 1.0 + numerator / c
            d = 1.0 / d
            f *= c * d
    return front * f / a


def f_sf(value, d1, d2):
    return 1.0 - betainc(d1 / 2, d2 / 2, d1 * value / (d1 * value + d2))


def check(real, reps, names=NAMES):
    n, k = len(reps), len(names)
    if n <= k + 5:
        raise ValueError(f"need more than {k + 5} replicates for a stable prediction region")
    mean = [st.mean(r[name] for r in reps) for name in names]
    sd = [st.stdev(r[name] for r in reps) for name in names]
    cov = [[sum((r[a] - mean[i]) * (r[b] - mean[j]) for r in reps) / (n - 1) for j, b in enumerate(names)]
           for i, a in enumerate(names)]
    delta = [real[name] - mean[i] for i, name in enumerate(names)]
    t2 = sum(x * y for x, y in zip(delta, solve(cov, delta)))
    f_value = t2 * n * (n - k) / (k * (n - 1) * (n + 1))
    p = f_sf(f_value, k, n - k)
    z = {name: round(delta[i] / sd[i], 2) for i, name in enumerate(names)}
    return {"replicates": n, "synthetic_mean": {name: round(mean[i], 4) for i, name in enumerate(names)},
            "synthetic_sd": {name: round(sd[i], 4) for i, name in enumerate(names)}, "z_real_minus_synthetic": z,
            "hotelling_t2": round(t2, 2), "prediction_p": round(p, 5),
            "worst_statistic": max(z, key=lambda name: abs(z[name])),
            "joint_pass": p >= 0.01, "marginal_pass": all(abs(v) <= Z_MAX for v in z.values()),
            "pass": p >= 0.01 and all(abs(v) <= Z_MAX for v in z.values())}


def geometry(histories=6):
    """Noiseless decline slope across 9-11 mag and peak magnitude against duration, per family."""
    from run_x3_validation import seed_for, select_strata
    out = {}
    for family in ("v2", "v3"):
        module = __import__(f"dnmem.injection_truth_{family}", fromlist=["ShapeConfig"])
        triples = []
        for era, s in select_strata(STATE["inputs"])[0].items():
            for rep in range(histories):
                h = module.generate_events(STATE["inputs"]["durations"], STATE["inputs"]["gaps"], float(s["start"]),
                                           float(s["stop"]), seed_for(BASE + "-geometry", family, era, rep), process="null",
                                           shape_config=module.ShapeConfig(**STATE["params"][family]["shape_config"]))
                peaks = {e.event_id: e.peak_magnitude for e in h.events}
                for t in module.truth_catalogue(h, THR):
                    times = [t["end"] - 4 + 0.02 * k for k in range(400)]
                    pts = [(x, m) for x, m in zip(times, h.evaluate(times)) if 9.0 <= m <= 11.0]
                    if len(pts) < 5:
                        continue
                    tb, mb = st.mean(x for x, _ in pts), st.mean(m for _, m in pts)
                    slope = sum((x - tb) * (m - mb) for x, m in pts) / sum((x - tb) ** 2 for x, _ in pts)
                    if slope > 0:
                        triples.append((t["end"] - t["onset"], slope, peaks[t["id"]]))
        short, long_ = [x for x in triples if x[0] < 11], [x for x in triples if x[0] >= 11]
        out[family] = {"events": len(triples), "histories": 3 * histories,
                       "rho_duration_band_slope": round(spearman([(d, s) for d, s, _ in triples]), 3),
                       "band_slope_median_short_long": [round(st.median(x[1] for x in short), 3), round(st.median(x[1] for x in long_), 3)],
                       "rho_duration_peak": round(spearman([(d, p) for d, _, p in triples]), 3),
                       "peak_median_short_long": [round(st.median(x[2] for x in short), 2), round(st.median(x[2] for x in long_), 2)]}
    return out


def main():
    from dnmem.coverage import combine_acquisitions
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=100)
    parser.add_argument("--workers", type=int, default=7)
    parser.add_argument("--output", type=Path, default=ROOT / "data/simulations/a04h_morphology_targets_20261108.json")
    parser.add_argument("--geometry", type=Path, help="instead, write the noiseless geometry check here")
    args = parser.parse_args()
    init()
    if args.geometry:
        result = geometry()
        args.geometry.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        return
    rows, _ = combine_acquisitions(sorted((ROOT / "data/raw").glob("aavso_ss_cyg_*/native.xml")))
    rows = [r for r in rows if float(r["JD"]) < J1960]
    real = statistics(features(rows), (J1960 - J1910) / 365.25)
    tasks = [(f, p, r) for f, p in CONFIGS for r in range(args.replicates)]
    with ProcessPoolExecutor(args.workers, initializer=init) as pool:
        done = list(pool.map(replicate, tasks, chunksize=2))
    result = {"operator": __doc__.strip().splitlines()[0], "seed_base": BASE,
              "waveform_statistics": list(WAVEFORM), "cadence_statistics": list(CADENCE),
              "gate": {"joint": "Hotelling prediction p >= 0.01", "marginal": f"|z| <= {Z_MAX}"},
              "real_1910_1959": {k: round(v, 4) for k, v in real.items()}}
    for family, phase in CONFIGS:
        reps = [s for (f, p, _), s in done if f == family and p == phase]
        result[f"{family}_{phase}"] = {"waveform": check(real, reps, WAVEFORM), "cadence": check(real, reps, CADENCE),
                                       "all": check(real, reps)}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for family, phase in CONFIGS:
        for block in ("waveform", "cadence", "all"):
            c = result[f"{family}_{phase}"][block]
            print(family, phase, block, "T2", c["hotelling_t2"], "p", c["prediction_p"], "pass", c["pass"],
                  "worst", c["worst_statistic"], c["z_real_minus_synthetic"][c["worst_statistic"]])
        print("   z:", result[f"{family}_{phase}"]["all"]["z_real_minus_synthetic"])
    print("real:", result["real_1910_1959"])


if __name__ == "__main__":
    main()
