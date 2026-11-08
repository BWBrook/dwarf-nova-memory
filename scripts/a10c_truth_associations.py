#!/usr/bin/env python3
"""A10c: duration-gap associations in the synthetic truth at the magnitude-10 threshold.

The A04i/A10b timing processes are defined on latent ranks. This script measures, in the
threshold-10 truth catalogue that the oracle view uses, the correlations between log duration
and the following and preceding log quiet gap, and the lag-1 gap autocorrelation, for each
process. Development namespace `a10c-claude-truth-*`; no observation model, extraction or
real data are involved.
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
BASE = "a10c-claude-truth-20261108"
STATE = {}


def init():
    STATE["inputs"] = json.loads((ROOT / "outputs/a04i_inputs_frozen_20261108/inputs.json").read_text())
    STATE["configs"] = json.loads((ROOT / "configs/a04i_selected.json").read_text())


def pearson(x, y):
    mx, my = st.fmean(x), st.fmean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy / math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))


def run(task):
    from dnmem.injection_truth import LatentCoefficients
    from dnmem.x4_benchmark import seed_for
    family, process, replicate = task
    config = STATE["configs"][family]
    generator = __import__(f"dnmem.injection_truth_{config['family']}", fromlist=["x"])
    kwargs = {"shape_config": generator.ShapeConfig(**config["shape_config"]),
              "process": "alternative" if process != "null" else "null"}
    if process == "structured":
        kwargs["coefficients"] = LatentCoefficients(partial_duration_gap=0)
    start, stop = 2418672.5, 2418672.5 + 400 * 365.25
    seed = seed_for(BASE, family, process, replicate)
    history = generator.generate_events(STATE["inputs"]["durations"], STATE["inputs"]["gaps"], start, stop,
                                        seed_for(seed, "truth"), **kwargs)
    cat = sorted(generator.truth_catalogue(history, 10.0), key=lambda e: e["onset"])
    latent = [(e.latent_duration, e.latent_gap) for e in history.events] if hasattr(history, "events") else None
    rows = []
    for prev, cur, nxt in zip(cat, cat[1:], cat[2:]):
        d, q, qp = cur["end"] - cur["onset"], nxt["onset"] - cur["end"], cur["onset"] - prev["end"]
        if d > 0 and q > 0 and qp > 0:
            rows.append((math.log(d), math.log(q), math.log(qp), math.log(prev["end"] - prev["onset"]) if prev["end"] > prev["onset"] else None))
    return {"family": family, "process": process, "replicate": replicate, "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=6)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--output", type=Path, default=ROOT / "data/simulations/a10c_truth_associations_20261108.json")
    args = parser.parse_args()
    tasks = [(f, p, r) for f in ("v2-phase", "v4-phase") for p in ("null", "structured", "alternative")
             for r in range(args.replicates)]
    with ProcessPoolExecutor(args.workers, initializer=init) as pool:
        done = list(pool.map(run, tasks))
    out = {"seed_base": BASE, "years_per_history": 400, "threshold": 10.0, "groups": []}
    for f in ("v2-phase", "v4-phase"):
        for p in ("null", "structured", "alternative"):
            per = [d for d in done if d["family"] == f and p == d["process"]]
            def stat(fn):
                vals = [fn(d["rows"]) for d in per]
                return {"mean": round(st.fmean(vals), 4), "sd_across_histories": round(st.stdev(vals), 4)}
            g = {"family": f, "process": p, "histories": len(per), "events": sum(len(d["rows"]) for d in per),
                 "r_logD_logQ_following": stat(lambda rs: pearson([r[0] for r in rs], [r[1] for r in rs])),
                 "r_logD_logQ_preceding": stat(lambda rs: pearson([r[0] for r in rs], [r[2] for r in rs])),
                 "r_logQ_lag1": stat(lambda rs: pearson([r[2] for r in rs], [r[1] for r in rs])),
                 "r_logD_previous_logQ_following": stat(lambda rs: pearson([r[3] for r in rs if r[3] is not None], [r[1] for r in rs if r[3] is not None]))}
            out["groups"].append(g)
            print(json.dumps(g))
    args.output.write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()
