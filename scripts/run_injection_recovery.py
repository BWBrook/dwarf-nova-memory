#!/usr/bin/env python3
"""Run the frozen A04c conditional injection/recovery screen; raw inputs stay local."""

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics as st
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def jd(year):
    return datetime(year, 1, 1, tzinfo=timezone.utc).timestamp() / 86400 + 2440587.5


def seed_for(base, *labels):
    return int.from_bytes(hashlib.sha256("|".join(map(str, (base,) + labels)).encode()).digest()[:8], "big")


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def midpoint(event, prefix):
    a, b = event[prefix + "_lo"], event[prefix + "_hi"]
    return None if a is None or b is None else (a + b) / 2


def prepare(output):
    from dnmem.coverage import combine_acquisitions
    from dnmem.extract import visits, x1_vote_episodes, longest_quiet_gap
    from dnmem.injection_observe import prepare_schedule, calibrate

    output.mkdir(parents=True, exist_ok=False)
    paths = sorted((ROOT / "data/raw").glob("aavso_ss_cyg_*/native.xml"))
    if len(paths) != 12:
        raise ValueError("the frozen input comprises exactly 12 acquisitions")
    rows, duplicates = combine_acquisitions(paths)
    if any(float(r["JD"]) >= jd(1960) for r in rows):
        raise ValueError("reserved observations are forbidden")
    episodes = x1_vote_episodes(rows)
    times = [v["t"] for v in visits(rows)]
    durations, gaps = [], []
    for i, event in enumerate(episodes):
        onset, end = midpoint(event, "onset"), midpoint(event, "end")
        if not event["confirmed_event"] or onset is None or end is None or not jd(1910) <= onset < jd(1960):
            continue
        if 5 <= end - onset <= 40:
            durations.append(end - onset)
        if i + 1 < len(episodes):
            following = episodes[i + 1]
            nxt = midpoint(following, "onset")
            if following["confirmed_event"] and nxt is not None and 5 <= nxt - end <= 100:
                if longest_quiet_gap(times, end, nxt) <= 7:
                    gaps.append(nxt - end)
    if min(len(durations), len(gaps)) < 30:
        raise ValueError("too few open-era marginal samples")
    model, public_model = calibrate(rows, episodes)
    schedule = prepare_schedule(rows)
    windows = [("1900_1909", jd(1900), jd(1910)), ("1910_1929", jd(1910), jd(1930)),
               ("1930_1949", jd(1930), jd(1950)), ("1950_1959", jd(1950), 2436934.0)]
    strata = []
    for label, start, stop in windows:
        anchors = [midpoint(e, "onset") for e in episodes if e["confirmed_event"] and midpoint(e, "onset") is not None]
        anchors = [a for a in anchors if start <= a <= stop]
        retained = []
        for anchor in anchors:
            if not retained or anchor - retained[-1] >= 10:
                retained.append(anchor)
        dropped = len(anchors) - len(retained)
        anchors = retained
        strata.append({"stratum": label, "start": start, "stop": stop, "anchors": anchors,
                       "aligned_close_anchors_omitted": dropped,
                       "schedule": [r for r in schedule if start <= float(r["JD"]) < stop]})
    source_hashes = {p.parent.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    cache = {"strata": strata, "model": model, "durations": sorted(durations), "gaps": sorted(gaps),
             "source_sha256": source_hashes}
    write_json(output / "inputs.json", cache)
    quantiles = lambda x: {"n": len(x), "min": min(x), "median": st.median(x), "max": max(x)}
    public = {"source_sha256": source_hashes, "unique_native_rows": len(rows), "identical_overlaps": duplicates,
              "duration_marginal": quantiles(durations), "gap_marginal": quantiles(gaps),
              "observation_model": public_model,
              "strata": [{k: v for k, v in s.items() if k not in ("schedule", "anchors")} |
                         {"scheduled_rows": len(s["schedule"]), "aligned_anchors": len(s["anchors"])} for s in strata],
              "scope": "separate marginal calibration only; no empirical real duration-gap association"}
    write_json(output / "calibration_summary.json", public)
    preparation_files = [ROOT / "scripts/run_injection_recovery.py", ROOT / "src/dnmem/extract.py",
                         ROOT / "src/dnmem/coverage.py", ROOT / "src/dnmem/aavso.py",
                         ROOT / "src/dnmem/injection_observe.py"]
    write_json(output / "preparation_receipt.json", {
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": sys.version, "source_sha256": source_hashes,
        "inputs_sha256": hashlib.sha256((output / "inputs.json").read_bytes()).hexdigest(),
        "code_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in preparation_files}})
    print(json.dumps(public, indent=2))


INPUTS = None


def load_worker(cache):
    global INPUTS
    INPUTS = json.loads(Path(cache).read_text())


def run_one(task):
    from dnmem.injection_truth import generate_events, magnitudes_at, truth_catalogue
    from dnmem.injection_observe import simulate_rows
    from dnmem.injection_score import score_run
    from dnmem.extract import x1_vote_episodes, x2_median_hysteresis

    stratum_index, phase, process, replicate, base = task
    s = INPUTS["strata"][stratum_index]
    seed = seed_for(base, s["stratum"], phase, process, replicate)
    history = generate_events(INPUTS["durations"], INPUTS["gaps"], s["start"], s["stop"],
                              seed_for(seed, "truth"), process=process,
                              anchors=s["anchors"] if phase == "aligned" else None)
    schedule = s["schedule"]
    mags = magnitudes_at(history, [float(r["JD"]) for r in schedule])
    rows = simulate_rows(schedule, mags, INPUTS["model"], seed_for(seed, "measurement"))
    results = []
    for threshold in (9.5, 10.0, 10.5):
        truth = truth_catalogue(history, threshold)
        for name, extractor in (("X1", x1_vote_episodes), ("X2", x2_median_hysteresis)):
            error = ""
            try:
                if name == "X1":
                    extracted = extractor(rows, threshold=threshold)
                else:
                    extracted = extractor(rows, low=threshold - .3, high=threshold + .3, cross=threshold)
            except (ValueError, StopIteration, ZeroDivisionError) as exc:
                extracted, error = [], type(exc).__name__
            for result in score_run(rows, extracted, truth, s["start"], s["stop"], threshold):
                results.append({"stratum": s["stratum"], "phase": phase, "process": process,
                                "replicate": replicate, "seed": seed, "extractor": name,
                                "extraction_error": error, **result})
    return results


def run(args):
    if args.replicates <= 0 or not 1 <= args.workers <= 4:
        raise ValueError("positive replicate count and 1–4 local workers required")
    args.output.mkdir(parents=True, exist_ok=False)
    cache = args.inputs.resolve()
    payload = json.loads(cache.read_text())
    preparation = json.loads((cache.parent / "preparation_receipt.json").read_text())
    if preparation["inputs_sha256"] != hashlib.sha256(cache.read_bytes()).hexdigest():
        raise ValueError("prepared input cache differs from its receipt")
    tasks = [(i, phase, process, rep, args.seed)
             for i in range(len(payload["strata"])) for phase in ("random", "aligned")
             for process in ("null", "alternative") for rep in range(args.replicates)]
    files = [ROOT / "scripts/run_injection_recovery.py", ROOT / "docs/protocols/a04c-injection-recovery-v1.md",
             *sorted((ROOT / "src/dnmem").glob("injection_*.py")), ROOT / "src/dnmem/extract.py"]
    receipt = {"base_seed": args.seed, "replicates_per_cell": args.replicates, "tasks": len(tasks),
               "workers": args.workers, "inputs_sha256": hashlib.sha256(cache.read_bytes()).hexdigest(),
               "source_sha256": payload["source_sha256"], "python": sys.version,
               "preparation_receipt": preparation,
               "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
               "dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)),
               "code_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
               "scope": "conditional synthetic recovery; no real forecast scores"}
    write_json(args.output / "receipt.json", receipt)
    started = time.monotonic()
    with (args.output / "replicates.csv").open("w", newline="") as handle:
        writer = None
        with ProcessPoolExecutor(max_workers=args.workers, initializer=load_worker, initargs=(str(cache),)) as pool:
            for done, results in enumerate(pool.map(run_one, tasks), 1):
                if writer is None:
                    writer = csv.DictWriter(handle, fieldnames=list(results[0]), lineterminator="\n")
                    writer.writeheader()
                writer.writerows(results)
                handle.flush()
                if done % 20 == 0 or done == len(tasks):
                    print(f"{done}/{len(tasks)} histories; elapsed {time.monotonic()-started:.1f} s", flush=True)
    receipt["elapsed_seconds"] = time.monotonic() - started
    receipt["replicates_sha256"] = hashlib.sha256((args.output / "replicates.csv").read_bytes()).hexdigest()
    receipt["completed_histories"] = len(tasks)
    write_json(args.output / "receipt.json", receipt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--output", type=Path, required=True)
    execution = sub.add_parser("run")
    execution.add_argument("--inputs", type=Path, required=True)
    execution.add_argument("--output", type=Path, required=True)
    execution.add_argument("--replicates", type=int, default=200)
    execution.add_argument("--workers", type=int, default=4)
    execution.add_argument("--seed", type=int, default=2026110704)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.output)
    else:
        run(args)


if __name__ == "__main__":
    main()
