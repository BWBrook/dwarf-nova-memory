#!/usr/bin/env python3
"""A10 precision statement: how well can one star's block resolve a small duration effect?

Standardized Gaussian model of the A10 comparison. y is the log following gap and
x the log duration, both after removing the baseline model's prediction. They
correlate at r, the partial correlation that the mark adds. The models are fitted
on a development block of `--train` forecasts, then each forecast in an
evaluation stream is scored by its log predictive density. There are two
schemes: parameters frozen at the development fit, and expanding-window refits
after each outcome. Each block size is a prefix of the same evaluation stream.

Reported per r and evaluation size:
- mean paired gain (nats per forecast);
- its sampling SD across replicates;
- power of the one-sided paired score test (z > 1.645);
- power of the secondary one-sided slope test on the evaluation block alone.

Censoring, missed events and dependence are ignored, so these are optimistic.
"""

import argparse
import json
import math
from pathlib import Path
import random
import statistics as st

ROOT = Path(__file__).resolve().parents[1]
LOG2PI = math.log(2 * math.pi)


class OLS:
    def __init__(self):
        self.n = self.sx = self.sy = self.sxx = self.sxy = self.syy = 0.0

    def add(self, x, y):
        self.n += 1
        self.sx += x
        self.sy += y
        self.sxx += x * x
        self.sxy += x * y
        self.syy += y * y

    def null(self):
        mean = self.sy / self.n
        var = (self.syy - self.n * mean * mean) / (self.n - 1)
        return mean, var

    def slope(self):
        mx, my = self.sx / self.n, self.sy / self.n
        sxx = self.sxx - self.n * mx * mx
        b = (self.sxy - self.n * mx * my) / sxx
        resid = self.syy - self.n * my * my - b * (self.sxy - self.n * mx * my)
        return my - b * mx, b, resid / (self.n - 2), sxx


def logpdf(y, mean, var):
    return -0.5 * (LOG2PI + math.log(var) + (y - mean) ** 2 / var)


def replicate(rng, r, train, sizes):
    e = math.sqrt(1 - r * r)
    fit = OLS()
    for _ in range(train):
        x = rng.gauss(0, 1)
        fit.add(x, r * x + e * rng.gauss(0, 1))
    m0, v0 = fit.null()
    a1, b1, v1, _ = fit.slope()
    online = fit
    held = OLS()
    frozen_d, online_d, out = [], [], {}
    biggest = max(sizes)
    for i in range(1, biggest + 1):
        x = rng.gauss(0, 1)
        y = r * x + e * rng.gauss(0, 1)
        frozen_d.append(logpdf(y, a1 + b1 * x, v1) - logpdf(y, m0, v0))
        om, ov = online.null()
        oa, ob, ovv, _ = online.slope()
        online_d.append(logpdf(y, oa + ob * x, ovv) - logpdf(y, om, ov))
        online.add(x, y)
        held.add(x, y)
        if i in sizes:
            _, b, s2, sxx = held.slope()
            row = {"slope_t": b / math.sqrt(s2 / sxx)}
            for name, d in (("frozen", frozen_d), ("online", online_d)):
                mean = st.fmean(d)
                row[name] = mean
                row[f"{name}_z"] = mean / (st.stdev(d) / math.sqrt(i))
            out[i] = row
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=1000)
    parser.add_argument("--train", type=int, default=300)
    parser.add_argument("--sizes", default="200,390,1000,2000")
    parser.add_argument("--effects", default="0,0.06,0.09,0.12,0.13")
    parser.add_argument("--output", type=Path, default=ROOT / "data/simulations/a10_precision_20261108.json")
    args = parser.parse_args()
    sizes = [int(s) for s in args.sizes.split(",")]
    result = {"model": __doc__.strip().splitlines()[0], "seed": "a10-claude-precision-20261108",
              "train_forecasts": args.train, "replicates": args.replicates, "rows": []}
    for r in (float(v) for v in args.effects.split(",")):
        rng = random.Random(f"a10-claude-precision-20261108|{r}")
        reps = [replicate(rng, r, args.train, sizes) for _ in range(args.replicates)]
        for n in sizes:
            rows = [rep[n] for rep in reps]
            entry = {"r": r, "evaluation_forecasts": n,
                     "ideal_gain_nats": round(-0.5 * math.log(1 - r * r), 5),
                     "approx_score_z": round(r * math.sqrt(n) / 2, 3), "approx_slope_z": round(r * math.sqrt(n), 3),
                     "slope_test_power": round(sum(x["slope_t"] > 1.645 for x in rows) / len(rows), 3)}
            for name in ("frozen", "online"):
                gains = [x[name] for x in rows]
                entry[f"{name}_mean_gain_nats"] = round(st.fmean(gains), 5)
                entry[f"{name}_gain_sd"] = round(st.stdev(gains), 5)
                entry[f"{name}_p_gain_positive"] = round(sum(g > 0 for g in gains) / len(gains), 3)
                entry[f"{name}_score_test_power"] = round(sum(x[f"{name}_z"] > 1.645 for x in rows) / len(rows), 3)
            result["rows"].append(entry)
            print(json.dumps(entry))
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
