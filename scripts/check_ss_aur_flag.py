"""Independent C71 reconstruction from retained SS Aur pre-1990 native pages.

No dnmem or Claude checker imports; observer visits and threshold-night
components are reconstructed from native rows. Public output contains only
aggregates; event times and source identities remain in ignored output.
"""

from __future__ import annotations

import argparse
import csv
from datetime import date
import hashlib
import io
import json
import math
from pathlib import Path
from statistics import median
from urllib.parse import parse_qs, urlparse
import xml.etree.ElementTree as ET

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/provenance/g3a_20261110/native-manifest.json"
STOP, THRESHOLD, VISIT = 2447892.5, 13.5, .15
EXPECTED_AUID = "000-BBK-861"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_ss_aur():
    entries = [e for e in json.loads(MANIFEST.read_text()) if e["star"] == "SS Aur"]
    if not entries:
        raise ValueError("no retained SS Aur acquisitions")
    unique, hashes = {}, {}
    for entry in entries:
        path = ROOT / entry["path"]
        digest = sha(path)
        if digest != entry["sha256"]:
            raise ValueError("retained native page differs from manifest")
        parsed = urlparse(entry["source_url"])
        query = parse_qs(parsed.query, keep_blank_values=True)
        if parsed.scheme != "https" or parsed.netloc != "vsx.aavso.org" or parsed.path != "/index.php":
            raise ValueError("unexpected source provenance")
        if query.get("ident") not in (["SS Aur"], [EXPECTED_AUID]):
            raise ValueError("unexpected source target")
        start, end = float(query["fromjd"][0]), float(query["tojd"][0])
        if not 0 < start < end < STOP:
            raise ValueError("source request crosses the authorized boundary")
        root = ET.fromstring(path.read_bytes())
        if root.findtext("Name") != "SS Aur" or root.findtext("AUID") != EXPECTED_AUID:
            raise ValueError("unexpected native target identity")
        hashes[path.name] = digest
        data = root.findtext("Data")
        if not data or not data.strip():
            continue
        for row in csv.DictReader(io.StringIO(data.strip())):
            t = float(row["JD"])
            if not math.isfinite(t) or not start <= t <= end or t >= STOP:
                raise ValueError("native report exceeds its approved window")
            if row["obsID"] in unique and unique[row["obsID"]] != row:
                raise ValueError("conflicting repeated native observation")
            unique[row["obsID"]] = row
    rows = [r for r in unique.values() if r["band"] == "Vis." and r["val"] == "V"]
    return sorted(rows, key=lambda r: (float(r["JD"]), r["obsID"])), hashes


def observer_visits(rows):
    grouped = {}
    for row in rows:
        who = (row.get("obsName") or "").strip().casefold() or row["by"]
        grouped.setdefault(who, []).append(row)
    votes = []
    for who, own in grouped.items():
        ordered = sorted(own, key=lambda r: (float(r["JD"]), r["obsID"]))
        cursor = 0
        while cursor < len(ordered):
            first = float(ordered[cursor]["JD"])
            stop = cursor + 1
            while stop < len(ordered) and float(ordered[stop]["JD"]) <= first + VISIT:
                stop += 1
            group = ordered[cursor:stop]
            cursor = stop
            positive = [float(r["mag"]) for r in group if r["fainterThan"] == "0"]
            limits = [float(r["mag"]) for r in group if r["fainterThan"] == "1"]
            if positive:
                value = median(positive)
                label = "B" if value <= THRESHOLD else "F"
            elif limits and max(limits) >= THRESHOLD:
                value, label = None, "F"
            else:
                continue
            votes.append(dict(t=median(float(r["JD"]) for r in group), value=value,
                              label=label, observer=who, source_ids=[r["obsID"] for r in group]))
    return sorted(votes, key=lambda v: (v["t"], v["source_ids"][0]))


def _components(count, links):
    parent = list(range(count))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for a, b in links:
        parent[find(b)] = find(a)
    groups = {}
    for i in range(count):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def threshold_components(votes):
    """Two graph operations: non-faint adjacency, then <=3-night bridges.

    The first graph connects adjacent observed non-faint nights only when
    their separation is <=7 days. Components without a bright-majority night
    are removed before bridging, so mixed-only islands cannot chain events.
    """
    nightly = {}
    for vote in votes:
        nightly.setdefault(math.floor(vote["t"]), []).append(vote)
    nights = sorted(nightly)
    labels = {}
    for night in nights:
        count = sum(v["label"] == "B" for v in nightly[night])
        labels[night] = np.sign(2 * count - len(nightly[night]))
    indices = [i for i, night in enumerate(nights) if labels[night] >= 0]
    links = [(j - 1, j) for j in range(1, len(indices))
             if indices[j] == indices[j - 1] + 1 and nights[indices[j]] - nights[indices[j - 1]] <= 7]
    primitive = [[nights[indices[j]] for j in component] for component in _components(len(indices), links)]
    primitive = [group for group in primitive if any(labels[night] > 0 for night in group)]
    bridges = [(i - 1, i) for i in range(1, len(primitive))
               if primitive[i][0] - primitive[i - 1][-1] <= 3]
    result = []
    for joined in _components(len(primitive), bridges):
        lo, hi = primitive[joined[0]][0], primitive[joined[-1]][-1]
        own = [v for night in nights if lo <= night <= hi for v in nightly[night]]
        bright = [v for v in own if v["label"] == "B"]
        first, last = min(v["t"] for v in bright), max(v["t"] for v in bright)
        within = sorted({v["t"] for v in own if first <= v["t"] <= last})
        hole = max((b - a for a, b in zip(within, within[1:])), default=0.)
        supported = (len({math.floor(v["t"]) for v in bright}) >= 10
                     and len({v["observer"] for v in bright}) >= 2 and hole <= 7.)
        result.append(dict(start=first, stop=last, span=last - first,
                           votes=sorted(own, key=lambda v: (v["t"], v["source_ids"][0])),
                           supported=supported, maximum_hole=hole))
    return result


def checks():
    def vote(t, label):
        return dict(t=t, label=label, value=13 if label == "B" else 14,
                    observer="synthetic", source_ids=[str(t)])
    self_case = [vote(100, "B"), vote(101, "F"), vote(102, "B"), vote(102, "F"),
                 vote(103, "F"), vote(104, "B")]
    assert len(threshold_components(self_case)) == 2
    assert len(threshold_components([vote(100, "B"), vote(103, "B")])) == 1
    assert len(threshold_components([vote(100, "B"), vote(108, "B")])) == 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--public-output", type=Path)
    args = parser.parse_args()
    if args.output.exists() or (args.public_output and args.public_output.exists()):
        parser.error("outputs must be new; existing evidence is never overwritten")
    checks()
    rows, hashes = load_ss_aur()
    votes = observer_visits(rows)
    runs = threshold_components(votes)
    supported = [run for run in runs if run["supported"]]
    flagged = max(supported, key=lambda run: run["span"])
    own = flagged["votes"]
    values = [v["value"] for v in own if v["value"] is not None]
    decisive_nights = sorted({math.floor(v["t"]) for v in own if v["value"] is not None and v["value"] <= THRESHOLD - 1})
    cuts = [i for i in range(1, len(decisive_nights)) if decisive_nights[i] - decisive_nights[i - 1] > 7]
    clusters = np.split(np.asarray(decisive_nights), cuts)
    cluster_count = len(clusters) if decisive_nights else 0
    quantiles = [float(v) for v in np.quantile(values, [.1, .5, .9])]
    near_count = sum(THRESHOLD - 1 < v <= THRESHOLD for v in values)
    proximity = near_count / len(values)
    all_faint = [float(r["mag"]) for r in rows if r["fainterThan"] == "0" and float(r["mag"]) > THRESHOLD]
    year = date.fromordinal(math.floor(flagged["start"] - 1721424.5)).year
    computed = dict(run_span_days=flagged["span"], run_votes=len(own), run_positive_votes=len(values),
                    run_bright_votes=sum(v["label"] == "B" for v in own),
                    run_faint_votes=sum(v["label"] == "F" for v in own),
                    run_decisive_bright_nights=len(decisive_nights), decisive_bright_clusters_split_7d=cluster_count,
                    decisive_night_counts_per_cluster=[len(group) for group in clusters],
                    run_positive_vote_quantiles_10_50_90=quantiles,
                    nondecisive_threshold_bright_positive_vote_count=near_count,
                    fraction_positive_votes_in_nondecisive_bright_band=proximity,
                    nondecisive_bright_band_definition="12.5 < observer-visit median magnitude <= 13.5",
                    fraction_positive_votes_in_closed_one_mag_band=sum(THRESHOLD - 1 <= v <= THRESHOLD for v in values) / len(values),
                    record_raw_positive_reports_fainter_than_threshold_median=median(all_faint),
                    reported_start_year_matches=year == 1970,
                    supported_threshold_runs=len(supported), flagged_supported_runs_at_least_60_days=sum(r["span"] >= 60 for r in supported))
    matched = dict(span=math.isclose(flagged["span"], 100.97, abs_tol=1e-8), votes=len(own) == 258,
                   decisive_clusters=cluster_count == 4, quantiles=np.allclose(quantiles, [12.5, 13.2, 13.7], atol=1e-12),
                   proximity_fraction=math.isclose(proximity, .6984126984126984, abs_tol=1e-12),
                   record_faint_median=median(all_faint) == 14.5, reported_start_year=year == 1970)
    public = dict(claim="C71", status="numerical_reproduction_with_interpretation_limits" if all(matched.values()) else "mismatch_requires_review",
                  scope="SS Aur only; retained pre-1990 validated visual reports; no new data, duration-gap fits or scores",
                  aggregates=computed, matches_reported=matched,
                  interpretation=["Four decisive-bright report clusters are not an independently annotated physical-outburst catalogue; one has a single night",
                                  "Threshold-proximate reports can bridge this operational run; the cause of those magnitudes is not identified",
                                  "Record-wide fainter reports are a descriptive comparison, not a same-era or observer-matched quiescent baseline"],
                  independence="Standard-library native parser and observer visits; graph components independently reconstruct the threshold-night rule; no dnmem or Claude checker imports",
                  source_sha256={"manifest": sha(MANIFEST), "this_script": sha(__file__), "ss_aur_native_payloads": hashes})
    args.output.mkdir(parents=True)
    private = dict(start_jd=flagged["start"], stop_jd=flagged["stop"], start_year=year,
                   decisive_clusters=[x.tolist() for x in clusters], votes=own)
    (args.output / "private-flag.json").write_text(json.dumps(private, indent=2, allow_nan=False) + "\n")
    (args.output / "summary.json").write_text(json.dumps(public, indent=2, sort_keys=True, allow_nan=False) + "\n")
    if args.public_output:
        args.public_output.parent.mkdir(parents=True, exist_ok=True)
        args.public_output.write_text(json.dumps(public, indent=2, sort_keys=True, allow_nan=False) + "\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (curve, histogram) = plt.subplots(2, 1, figsize=(9, 7), constrained_layout=True)
    first = flagged["start"]
    positive = [v for v in own if v["value"] is not None]
    curve.scatter([v["t"] - first for v in positive], [v["value"] for v in positive], s=13, color="#334155")
    for level, style in ((THRESHOLD, "-"), (THRESHOLD - 1, "--")):
        curve.axhline(level, color="#b45309", linestyle=style, linewidth=1)
    curve.set(xlabel="Days since first threshold-bright vote in flagged run", ylabel="Visual magnitude",
              title="SS Aur: independently reconstructed threshold-night flag")
    curve.invert_yaxis()
    histogram.hist(values, bins=np.arange(10, 16.01, .2), color="#64748b")
    histogram.axvspan(THRESHOLD - 1, THRESHOLD, alpha=.2, color="#b45309")
    histogram.set(xlabel="Positive observer-visit median magnitude", ylabel="Votes",
                  title="Reported proximity fraction uses 12.5 < magnitude <= 13.5")
    fig.savefig(args.output / "ss-aur-flag.png", dpi=160)
    plt.close(fig)
    print(json.dumps({"status": public["status"], "aggregates": computed, "matches_reported": matched}, sort_keys=True))


if __name__ == "__main__":
    main()
