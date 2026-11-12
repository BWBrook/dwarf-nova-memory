#!/usr/bin/env python3
"""Generate the SS Cyg paper figures, or check their public hashes offline.

--check uses only the standard library and committed public files. --generate
uses retained, already opened inputs; it never requests archive observations.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import io
import hashlib
import json
import math
import os
from pathlib import Path
from statistics import median
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "manuscript/figures"
DATA = ROOT / "manuscript/figure-data"
SCRATCH = ROOT / "outputs/a10k_figures"
RUN = ROOT / "outputs/a10h_live_repair_5e39aeb"
START, STOP = 2436934.5, 2458119.5
PARAMETERS = ROOT / "data/fits/a10e_1910_1959/frozen_parameters.json"
PRIMARY = ROOT / "data/provenance/a10i_evaluation_1960_2017/primary.json"
SUMMARY = ROOT / "data/provenance/a10i_evaluation_1960_2017/summary.json"
REVIEW = ROOT / "data/provenance/a10j_postresult_review/summary.json"
NATIVE_CODE = ROOT / "src/dnmem/evaluation_native.py"
R2B = ROOT / "data/provenance/r2b_20261109/headline.json"
G3A = ROOT / "data/provenance/g3a_20261110/summary.json"
G3A_DETAILS = ROOT / "data/provenance/g3a_20261110/details.json"
PRECISION = ROOT / "data/provenance/g3a_preparation/six-star-summary.json"
R1_SCORES = ROOT / "data/provenance/r1_20261109/observation-scores.json"
R2B_CHECK = ROOT / "data/provenance/r2b_claude_review/checks.json"
R2D = ROOT / "data/provenance/r2d_review_audit/summary.json"
G3A_CHECK = ROOT / "data/provenance/g3a_claude_review/checks.json"
C70 = ROOT / "data/provenance/g3a_review_independent/c70.json"
R1_EXAMPLE = ROOT / "data/provenance/r1_20261109/example-and-simulation-table.json"
BASENAMES = ("fig1-context", "fig2-forecast", "fig3-robustness", "fig4-transfer", "fig3-calibration",
             "fig4-type-exploration", "graphical-abstract", "fig6-g3a-feasibility")
ORIGINAL_DATA_NAMES = ("fig1-illustration.json", "fig2-gains.json", "fig3-coverage.json", "fig4-refits.json")
AGGREGATE_CSV_NAMES = ("r2b-contrasts.csv", "g3a-stars.csv", "g3a-totals.csv", "six-star-precision.csv")
CONTEXT_DATA_NAMES = ("fig1-lightcurve-nights.csv", "fig1-timelines.json", "fig3-forest.csv", "fig4-transfer.csv")
DATA_NAMES = ORIGINAL_DATA_NAMES + ("claim-values.csv",) + AGGREGATE_CSV_NAMES + CONTEXT_DATA_NAMES
LIGHT_CURVE_WINDOW = (START, START + 731.0)
BLUE, ORANGE, GREY, BLACK = "#0072B2", "#D55E00", "#808990", "#25292D"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT))


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def derived_units(primary, summary):
    gain = primary["estimate"]
    baseline = summary["secondary"]["robustness"]["primary"]["gain_M2_M0"]["estimate"]
    return dict(geometric_mean_likelihood_ratio=math.exp(gain),
                geometric_mean_likelihood_change_percent=100*math.expm1(gain),
                gain_ratio_to_timing_percent=100*gain/baseline,
                interpretation="geometric-mean evidence likelihood and log-score-gain ratio; neither accuracy nor variance explained")


def r2b_rows():
    source = load(R2B)["contrasts"]
    definitions = {
        "H1": ("fitted-end", "P-orig; duration gain"),
        "H2": ("observed DF", "P-DF; decisive-bright-span gain"),
        "H3": ("paired clock contrast", "P-DF gain minus P-match fitted-end gain"),
    }
    rows = []
    for name, (clock, population) in definitions.items():
        six, twelve = (source[name]["working"][key] for key in ("six_year", "twelve_year"))
        if any(six[key] != twelve[key] for key in ("estimate", "n", "issued")):
            raise ValueError("R2b intervals describe different contrast populations")
        rows.append(dict(claim_id="C55", contrast=name, clock=clock, population=population,
                         n=six["n"], issued=six["issued"], estimate=six["estimate"],
                         six_year_lower=six["lower"], six_year_upper=six["upper"],
                         six_year_blocks=six["blocks"], twelve_year_lower=twelve["lower"],
                         twelve_year_upper=twelve["upper"], twelve_year_blocks=twelve["blocks"]))
    return rows


def g3a_rows():
    summary, details = load(G3A), load(G3A_DETAILS)
    by_star = {row["star"]: row for row in details["stars"]}
    if len(by_star) != len(details["stars"]) or set(by_star) != {row["star"] for row in summary["stars"]}:
        raise ValueError("G3a aggregate populations disagree")
    rows = []
    for source in summary["stars"]:
        morphology = by_star[source["star"]]["morphology"]
        if morphology["passed"] != source["morphology_passed"]:
            raise ValueError("G3a morphology gates disagree")
        rows.append(dict(claim_id="C68", star=source["star"],
                         eligible_fraction=source["eligible_fraction"], eligible_windows=source["eligible_windows"],
                         confirmed_events=source["confirmed_events"], outcome_supported=source["outcome_supported"],
                         feature_supported=source["feature_supported"], supported_1980_1989=source["supported_1980_1989"],
                         base_passed=int(source["base_passed"]), morphology_passed=int(source["morphology_passed"]),
                         eclipse_required=int(source["eclipse_required"]), eclipse_passed=int(source["eclipse_passed"]),
                         qualified=int(source["qualified"]),
                         longest_supported_bright_span_days=morphology["longest_supported_bright_span_days"],
                         stream="derived fixed-night median" if source["eclipse_required"] else "native visual visits"))
    totals = [dict(claim_id="C68", field="targets", value=len(rows))]
    for field in ("native_payloads", "native_unique_rows", "validated_visual_rows", "confirmed_events",
                  "qualified_count", "outcome_supported", "supported_1980_1989"):
        totals.append(dict(claim_id="C68", field=field, value=summary[field]))
    totals.extend(dict(claim_id="C68", field=field, value=value) for field, value in (
        ("eligible_fraction_gate", .7), ("supported_count_gate", 40)))
    for projection in summary["projections"]:
        prefix = "projection_" + str(projection["years"]) + "yr_"
        for field in ("all_ten_ignoring_gates_diagnostic", "projected_qualified_issuances", "qualifying_stars"):
            name = "all_ten_ignoring_gates" if field == "all_ten_ignoring_gates_diagnostic" else field
            totals.append(dict(claim_id="C68", field=prefix + name, value=projection[field]))
    return rows, totals


def precision_rows():
    rows = []
    for case in load(PRECISION)["cases"]:
        settings = case["settings"]
        for method in ("star-score", "star-gain", "star-score-sign-flip"):
            result = case["methods"][method]
            rows.append(dict(claim_id="C69", case=case["case"], method=method,
                             nominal_forecasts=settings["test_forecasts"], stars=settings["stars"],
                             nominal_oracle_gain=settings["nominal_oracle_gain"],
                             attempted=case["attempted"], completed=case["completed"], failures=case["failures"],
                             rejections=result["rejections"], rate=result["rate"],
                             mc95_lower=result["exact_mc95"][0], mc95_upper=result["exact_mc95"][1],
                             mean_supported_marks=case["mean_supported_marks"],
                             gain_without_score=case["sequence_counts"]["star"]["gain_without_score"]))
    return rows


def forest_rows():
    primary, summary = load(PRIMARY), load(SUMMARY)
    r1 = load(R1_SCORES)["variants"]["saved_point"]["alternative"]
    guarded, scored = load(R2D)["comparisons"], load(R2B_CHECK)["contrasts"]
    r2b = {row["contrast"]: row for row in r2b_rows()}
    rows = []
    def add(claim, label, group, clock, baseline, n, estimate, lower, upper, interval, evidence):
        rows.append(dict(claim_id=claim, row=label, group=group, clock=clock, baseline=baseline, n=n,
                         estimate=estimate, lower=lower, upper=upper, interval=interval,
                         interval_source="saved in evidence", evidence=relative(evidence)))
    era = summary["secondary"]["era_split"]
    two_sided = "two-sided 90%, six-year clusters"
    add("C01", "Primary 1960–2017", "reference", "fitted-end", "M2 frozen", primary["n"], primary["estimate"],
        primary["lower"], primary["upper"], two_sided, PRIMARY)
    for claim, key, label in (("C06", "1960_1992", "1960–1992 segment"), ("C07", "1993_2017", "1993–2017 segment")):
        v = era[key]
        add(claim, label, "a", "fitted-end", "M2 frozen", v["n"], v["estimate"], v["lower"], v["upper"], two_sided, SUMMARY)
    v = summary["secondary"]["robustness"]["type_within"]["gain_M3_M2"]
    add("C08", "Long/short rule", "a", "fitted-end, type + within-type duration", "M2 frozen",
        v["n"], v["estimate"], v["lower"], v["upper"], two_sided, SUMMARY)
    add("C44", "Point-onset rescoring", "b", "fitted-end, saved-point score", "M2 frozen", r1["n"], r1["estimate"],
        r1["lower90"], r1["upper90"], two_sided, R1_SCORES)
    for claim, name, label, clock in (("C55", "H1", "Report windows, fitted-end clock", "fitted-end"),
                                      ("C55", "H2", "Report windows, decisive-faint clock", "observed decisive-faint")):
        v = r2b[name]
        add(claim, label, "b", clock, "B2", v["n"], v["estimate"], v["six_year_lower"], v["six_year_upper"],
            "exploratory CR1/t 90%, six-year clusters", R2B)
    for claim, key, label, clock, baseline in (
            ("C62", "point_original:B0.duration", "Fitted-end clock, B0 recalibrated", "fitted-end", "B0 drift-recalibrated"),
            ("C63", "df:B0.duration", "Decisive-faint, B0 recalibrated", "observed decisive-faint", "B0 drift-recalibrated"),
            ("C63", "df:B1.duration", "Decisive-faint, B1 recalibrated", "observed decisive-faint", "B1 drift-recalibrated"),
            ("C63", "df:B2.duration", "Decisive-faint, B2 recalibrated", "observed decisive-faint", "B2 drift-recalibrated")):
        v = guarded[key]["guarded_gain"]
        add(claim, label, "c", clock, baseline, scored[key]["scored"], v["mean"], v["lower90"], v["upper90"],
            "exploratory CR1/t 90%, six-year clusters", R2D)
    return rows


def transfer_rows():
    stars, _ = g3a_rows()
    c70 = load(C70)
    raw, hold = c70["ordinary_raw_streams"], c70["hold_frozen_reductions"]
    rows = []
    for star in stars:
        name = star["star"]
        if star["eclipse_required"]:
            peaks = hold[name]["median"]["confirmed_by_decade"]["1980"]
            numerator = hold[name]["median"]["by_decade"]["1980"]["supported"]
        else:
            peaks = raw[name]["confirmed_by_decade"]["1980"]
            numerator = raw[name]["by_decade"].get("1980", {}).get("supported", 0)
        if numerator != star["supported_1980_1989"]:
            raise ValueError("C70 and G3a numerators disagree for " + name)
        rows.append(dict(row_type="candidate", star=name, supported_development=star["outcome_supported"],
                         morphology_passed=star["morphology_passed"],
                         longest_supported_bright_span_days=star["longest_supported_bright_span_days"],
                         supported_1980_1989=numerator, confirmed_peaks_1980_1989=peaks, ratio=numerator/peaks,
                         stream=star["stream"], evidence=relative(G3A) + "; " + relative(C70)))
    if (sum(r["supported_1980_1989"] for r in rows), sum(r["confirmed_peaks_1980_1989"] for r in rows)) != (102, 485):
        raise ValueError("candidate 1980s totals differ from 102/485")
    ref, ceilings = c70["ss_cyg_pre1990_reference"], load(G3A_CHECK)["ceilings"]["ss_cyg_1980s"]
    numerator, peaks = ref["by_decade"]["1980"]["supported"], ref["confirmed_by_decade"]["1980"]
    if (numerator, peaks) != (ceilings["supported"], ceilings["confirmed"]) or (numerator, peaks) != (67, 73):
        raise ValueError("SS Cyg 1980s reference differs from saved evidence")
    rows.append(dict(row_type="reference", star="SS Cyg", supported_development=ref["sequential"]["supported"],
                     morphology_passed="", longest_supported_bright_span_days="", supported_1980_1989=numerator,
                     confirmed_peaks_1980_1989=peaks, ratio=numerator/peaks, stream="native visual visits",
                     evidence=relative(C70) + "; " + relative(G3A_CHECK)))
    return rows


def aggregate_tables():
    stars, totals = g3a_rows()
    tables = dict(zip(AGGREGATE_CSV_NAMES, (r2b_rows(), stars, totals, precision_rows())))
    tables["fig3-forest.csv"] = forest_rows()
    tables["fig4-transfer.csv"] = transfer_rows()
    return tables


TIMELINES = dict(
    scope="dates for the paper's context figure; no observation data",
    observation_years=[
        dict(label="Development fit", start=1910, end=1959, star="SS Cyg"),
        dict(label="Held-out test", start=1960, end=2017, star="SS Cyg"),
        dict(label="Closed", start=2018, end=None, star="SS Cyg"),
        dict(label="Candidate stars: pre-1990 only", start=None, end=1989, star="candidates")],
    analysis_sequence=dict(
        time_basis="UTC; timestamps are from the saved chronology and Git commit times",
        events=[
            dict(label="Protocol frozen; Zenodo deposit 10.5281/zenodo.24053338", at="2026-11-08T12:34:47Z",
                 source="coordination/decisions.md D025"),
            dict(label="First data access; fails on a parser error", start="2026-11-08T12:38:28Z", end="2026-11-08T12:39:51Z",
                 source="docs/audits/2026-11-08-a10h-native-format-repair.md"),
            dict(label="Parser repair (outcome-independent)", start="2026-11-08T12:39:51Z", end="2026-11-08T12:51:18Z",
                 source="coordination/decisions.md D026; end is the start of repaired acquisition"),
            dict(label="Repaired data access", start="2026-11-08T12:51:18Z", end="2026-11-08T13:00:33Z",
                 source="docs/audits/2026-11-09-a10i-sealed-evaluation.md"),
            dict(label="Primary result scored", at="2026-11-08T13:06:58Z",
                 source="docs/audits/2026-11-09-a10i-sealed-evaluation.md"),
            dict(label="Post-result checks", start="2026-11-08T13:57:28Z", end="2026-11-09T12:36:07Z",
                 source="commit f1aa2ae (A10j review) to commit cdd5ac8 (R2d review, D044)"),
            dict(label="Frozen transfer screen", start="2026-11-10T02:21:46Z", end="2026-11-10T04:00:55Z",
                 source="commit d827313 (G3a freeze) to commit e0924ca (G3a review, D046)")]))


def csv_text(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]), lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    return stream.getvalue()


def aggregate_claim_values():
    rows = []
    def add(identifier, field, value):
        rows.append(dict(claim_id=identifier, field=field, value=value))
    for row in r2b_rows():
        for field in ("n", "issued", "estimate", "six_year_lower", "six_year_upper", "six_year_blocks",
                      "twelve_year_lower", "twelve_year_upper", "twelve_year_blocks"):
            add("C55", row["contrast"] + "_" + field, row[field])
    stars, totals = g3a_rows()
    for row in stars:
        for field in ("eligible_fraction", "eligible_windows", "confirmed_events", "outcome_supported",
                      "feature_supported", "supported_1980_1989", "base_passed", "morphology_passed",
                      "eclipse_required", "eclipse_passed", "qualified", "longest_supported_bright_span_days"):
            if row[field] is not None:
                add("C68", row["star"].replace(" ", "_") + "_" + field, row[field])
    rows.extend(totals)
    cases = load(PRECISION)["cases"]
    add("C69", "cases", len(cases))
    for name, field in (("trials", "completed"), ("failed_trials", "failures")):
        add("C69", name, sum(case[field] for case in cases))
    add("C69", "gain_without_score_rejections", sum(case["sequence_counts"]["star"]["gain_without_score"] for case in cases))
    for row in precision_rows():
        prefix = row["case"].replace("-", "_") + "_" + row["method"].replace("-", "_") + "_"
        for field in ("rate", "rejections", "completed", "mc95_lower", "mc95_upper", "mean_supported_marks"):
            add("C69", prefix + field, row[field])
    return rows


def claim_values(primary, summary, review):
    rows=[]
    def add(identifier, field, value):
        rows.append(dict(claim_id=identifier,field=field,value=value))
    for field in ("estimate","lower","upper","n","blocks"):
        add("C01",field,primary[field])
    for field,value in derived_units(primary,summary).items():
        if field != "interpretation":add("C02",field,value)
    for identifier,key in (("C06","1960_1992"),("C07","1993_2017")):
        for field in ("estimate","lower","upper","n"):
            add(identifier,field,summary["secondary"]["era_split"][key][field])
    for field in ("estimate","lower","upper","n"):
        add("C08",field,summary["secondary"]["robustness"]["type_within"]["gain_M3_M2"][field])
    coverage=summary["secondary"]["calibration"]["models"]["M3"]["central_intervals"]
    for key,label in (("0.5","50"),("0.9","90")):
        for bound in ("lower","upper"):
            value=coverage[key]["coverage_"+bound+"_bound"]
            add("C11","coverage_"+label+"_"+bound,value)
            add("C11","coverage_"+label+"_"+bound+"_percent",100*value)
    ti=review["type_information"]
    fits=[("C21","evaluation",ti["refits_frozen_M2_nuisance_free_level"]["1960-2017"]),
          ("C21","development",ti["development_refits_in_sample"]["1910-1959"]),
          ("C23","early",ti["refits_frozen_M2_nuisance_free_level"]["1960-1992"]),
          ("C23","late",ti["refits_frozen_M2_nuisance_free_level"]["1993-2017"])]
    for identifier,prefix,fit in fits:
        values=dict(type_lr=fit["type_only"]["lr_vs_level_only"],
                    continuous_lr=fit["raw_log_duration"]["lr_vs_level_only"],
                    within_given_type_lr=fit["type_plus_within"]["lr_within_given_type"],
                    type_contrast=fit["type_only"]["beta_type_long_minus_short"],
                    clock_scale_ratio=math.exp(fit["type_only"]["beta_type_long_minus_short"]),
                    clock_scale_change_percent=100*math.expm1(fit["type_only"]["beta_type_long_minus_short"]),
                    n_timing=fit["n_timing"])
        for field,value in values.items():add(identifier,prefix+"_"+field,value)
    add("C25","positive_blocks",review["interval_recomputation"]["blocks_positive"])
    add("C25","block_count",len(review["interval_recomputation"]["blocks"]))
    add("C25","cluster_days",2191.5)
    return rows + aggregate_claim_values()


def write_claim_values(primary,summary,review):
    with (DATA/"claim-values.csv").open("w", newline="") as handle:
        handle.write(csv_text(claim_values(primary,summary,review)))


def asset_records():
    records = {}
    for stem in BASENAMES:
        for extension in ("png", "pdf"):
            path = FIGURES / (stem + "." + extension)
            item = dict(sha256=sha(path), bytes=path.stat().st_size)
            if extension == "png":
                item["pixel_dimensions"] = list(struct.unpack(">II", path.read_bytes()[16:24]))
            records[relative(path)] = item
    return records


def check():
    manifest = load(FIGURES / "manifest.json")
    if manifest["generator_sha256"] != sha(__file__):
        raise ValueError("figure generator changed; run --generate explicitly")
    expected_assets = {relative(FIGURES/(stem+"."+ext)) for stem in BASENAMES for ext in ("png", "pdf")}
    expected_data = {relative(DATA/name) for name in DATA_NAMES}
    if set(manifest["assets"]) != expected_assets or set(manifest["figure_data"]) != expected_data:
        raise ValueError("figure manifest does not contain the complete expected asset/data set")
    for group in ("assets", "figure_data", "public_inputs", "aggregate_inputs"):
        for name, record in manifest[group].items():
            path = ROOT/name
            if not path.is_file() or sha(path) != record["sha256"]:
                raise ValueError("figure hash mismatch: " + name)
            if group == "assets":
                data = path.read_bytes()
                if path.suffix == ".png" and not data.startswith(b"\x89PNG\r\n\x1a\n"):
                    raise ValueError("invalid PNG: " + name)
                if path.suffix == ".pdf":
                    if not data.startswith(b"%PDF-") or b"/FontFile2" not in data:
                        raise ValueError("PDF lacks embedded TrueType fonts: " + name)
                    if b"/CreationDate" in data or b"/ModDate" in data:
                        raise ValueError("unstable PDF date metadata: " + name)
    primary, summary, review = load(PRIMARY), load(SUMMARY), load(REVIEW)
    f2, f3, f4 = load(DATA/DATA_NAMES[1]), load(DATA/DATA_NAMES[2]), load(DATA/DATA_NAMES[3])
    if any(f2["comparisons"][0][field] != primary[field] for field in ("estimate","lower","upper","n")):
        raise ValueError("primary figure comparison differs from the saved result")
    expected_units=derived_units(primary,summary)
    if f2["derived_units"] != expected_units:
        raise ValueError("derived likelihood/gain units differ from their public evidence")
    with (DATA/"claim-values.csv").open(newline="") as handle:
        flat=list(csv.DictReader(handle))
    actual={(r["claim_id"],r["field"]):float(r["value"]) for r in flat}
    expected={(r["claim_id"],r["field"]):float(r["value"]) for r in claim_values(primary,summary,review)}
    if len(actual)!=len(flat) or actual.keys()!=expected.keys() or any(not math.isclose(actual[k],v,rel_tol=1e-13,abs_tol=1e-14) for k,v in expected.items()):
        raise ValueError("flattened figure claim values differ from their public evidence")
    for actual, expected in zip(f2["blocks"], review["interval_recomputation"]["blocks"]):
        if actual["mean_gain"] != expected["mean_gain"] or actual["n"] != expected["n"]:
            raise ValueError("descriptive block data differ from their public evidence")
    for model, values in f3["models"].items():
        if values != summary["secondary"]["calibration"]["models"][model]["central_intervals"]:
            raise ValueError("coverage data differ from their public evidence")
    if f4["evaluation_refits"] != review["type_information"]["refits_frozen_M2_nuisance_free_level"]:
        raise ValueError("exploratory refit data differ from their public evidence")
    f1 = load(DATA/DATA_NAMES[0])
    if f1["illustration"]["issue_jd"] >= STOP or f1["illustration"]["window_jd"][1] >= STOP:
        raise ValueError("illustration crosses the protected boundary")
    if not f1["scope"].startswith("ILLUSTRATION"):
        raise ValueError("the selected record is not labelled as an illustration")
    for name, rows in aggregate_tables().items():
        if (DATA/name).read_text() != csv_text(rows):
            raise ValueError("normalized aggregate table differs from its committed evidence: " + name)
    if load(DATA/"fig1-timelines.json") != TIMELINES:
        raise ValueError("timeline data differ from the generator")
    with (DATA/"fig1-lightcurve-nights.csv").open(newline="") as handle:
        nights = list(csv.DictReader(handle))
    if not nights or not all(math.floor(LIGHT_CURVE_WINDOW[0]) <= float(r["jd_floor"]) <= LIGHT_CURVE_WINDOW[1] < STOP for r in nights):
        raise ValueError("light-curve summaries lie outside the fixed opened window")
    if set(nights[0]) != {"jd_floor", "median_magnitude", "detection_observer_days", "faintest_limit", "limit_observer_days"}:
        raise ValueError("light-curve summaries must contain nightly aggregates only")
    print(json.dumps(dict(status="figure check passed", figures=len(BASENAMES),
                          assets=len(expected_assets), private_inputs_required=False)))


def native_window_rows(receipt, window, private_inputs):
    sys.path.insert(0, str(ROOT/"src"))
    from dnmem.evaluation_native import parse_native_bytes, select_analysis_rows
    native_rows = {}
    raw_namespace = ROOT/"data/raw"/("a10g_evaluation_"+receipt["source"]["freeze_commit"][:12])
    for acquisition in receipt["acquisitions"]["acquisitions"]:
        lo, hi = acquisition["requested_start_jd"], acquisition["requested_end_jd"]
        if hi < window[0] or lo > window[1]:
            continue
        if hi >= STOP:
            raise ValueError("raw illustration request reaches the protected boundary")
        path = raw_namespace/Path(acquisition["path"]).parent.name/"native.xml"
        if sha(path) != acquisition["sha256"]:
            raise ValueError("native illustration input drift")
        private_inputs[relative(path)] = dict(sha256=sha(path), purpose="selected-window native leaf")
        rows, _ = parse_native_bytes(path.read_bytes(), start_jd=lo, end_jd=hi)
        for row in select_analysis_rows(rows):
            if window[0] <= float(row["JD"]) <= window[1]:
                previous = native_rows.setdefault(row["obsID"], row)
                if previous != row:
                    raise ValueError("conflicting native IDs in illustration")
    return native_rows


def retained_receipt():
    receipt_path, ledger_path, evidence_path = (RUN/name for name in ("receipt.json", "ledger-0.0.json", "evidence-0.0.json"))
    receipt = load(receipt_path)
    if receipt["status"] != "completed" or receipt["mode"] != "live":
        raise ValueError("illustration requires the completed authorized run")
    for path in (ledger_path, evidence_path):
        if sha(path) != receipt["files_sha256"][path.name]:
            raise ValueError("retained illustration evidence drift")
    if sha(NATIVE_CODE) != receipt["source"]["sha256"][relative(NATIVE_CODE)]:
        raise ValueError("native display adapter differs from the executed version")
    return receipt, receipt_path, ledger_path, evidence_path


def lightcurve_nights(private_inputs):
    receipt, receipt_path, _, _ = retained_receipt()
    window = LIGHT_CURVE_WINDOW
    if not START <= window[0] < window[1] < STOP:
        raise ValueError("light-curve window lies outside the opened data")
    private_inputs[relative(receipt_path)] = dict(sha256=sha(receipt_path), purpose="native leaf hashes for the light-curve window")
    groups = defaultdict(list)
    for row in native_window_rows(receipt, window, private_inputs).values():
        time = float(row["JD"])
        identity = (row.get("obsName") or "").strip().casefold() or row["by"]
        groups[(identity, math.floor(time), row["fainterThan"] == "1")].append(float(row["mag"]))
    nights = defaultdict(lambda: dict(detections=[], limits=[]))
    for (_, night, limit), magnitudes in groups.items():
        if limit:
            nights[night]["limits"].append(max(magnitudes))
        else:
            nights[night]["detections"].append(median(magnitudes))
    rows = []
    for night in sorted(nights):
        detections, limits = nights[night]["detections"], nights[night]["limits"]
        rows.append(dict(jd_floor=night, median_magnitude=round(median(detections), 3) if detections else "",
                         detection_observer_days=len(detections),
                         faintest_limit=round(max(limits), 3) if limits else "", limit_observer_days=len(limits)))
    return rows


def illustration(np, log_ndtr, private_inputs):
    receipt, receipt_path, ledger_path, evidence_path = retained_receipt()
    features = load(ledger_path)
    if any(not START <= f["issue_time"] < STOP for f in features):
        raise ValueError("ledger extends beyond the opened evaluation period")
    eligible = [f for f in features if START <= f["issue_time"] < START+366
                and f.get("onset_t") is not None and f["onset_t"] > START]
    feature = min(eligible, key=lambda f: (f["issue_time"], f["emission_index"]))
    outcome = next(e for e in load(evidence_path) if e["emission_index"] == feature["emission_index"])
    if outcome["kind"] != "interval" or feature.get("end_t") is None:
        raise ValueError("the deterministic illustrative record cannot support the requested illustration")
    issue = feature["issue_time"]
    window = [feature["onset_t"]-4.0, issue+70.0]
    if not START <= window[0] < window[1] < STOP:
        raise ValueError("illustration window lies outside the opened data")
    native_rows = native_window_rows(receipt, window, private_inputs)
    groups = defaultdict(list)
    for row in native_rows.values():
        time = float(row["JD"])
        identity = (row.get("obsName") or "").strip().casefold() or row["by"]
        groups[(identity, math.floor(time), time <= issue, row["fainterThan"] == "1")].append((time,float(row["mag"])))
    points = []
    for (_, _, by_issue, limit), rows in groups.items():
        magnitude = max(m for _,m in rows) if limit else median(m for _,m in rows)
        times = [t for t,m in rows if m == magnitude] if limit else [t for t,_ in rows]
        points.append(dict(day_from_issue=median(times)-issue, magnitude=magnitude,
                           by_issue=by_issue, limit=limit))
    points.sort(key=lambda x:(x["day_from_issue"],x["magnitude"],x["limit"]))
    if not points:
        raise ValueError("the selected illustration window has no visual observations")
    spec = load(PARAMETERS)["primary"]
    timing_available = feature.get("previous_gap_covered") is True and (feature.get("previous_gap") or 0) > 0
    baseline = spec["models"]["M2" if timing_available else "M0"]
    mu = baseline["intercept"]
    if timing_available:
        q = (math.log(feature["previous_gap"])-baseline["centers"]["previous_gap"])/baseline["scales"]["previous_gap"]
        earlier = feature.get("earlier_gaps") or []
        level = sum(earlier)/len(earlier) if earlier else baseline["centers"]["earlier_level"]
        level = (level-baseline["centers"]["earlier_level"])/baseline["scales"]["earlier_level"]
        mu += baseline["coefficients"]["previous_gap"]*q+baseline["coefficients"]["earlier_level"]*level
    added = 0.0
    if timing_available:
        mark = spec["models"]["M3"]
        x = (math.log(feature["end_t"]-feature["onset_t"])-mark["centers"]["mark"])/mark["scales"]["mark"]
        added = mark["coefficients"]["beta"]*x
    age = issue-feature["end_t"]
    grid = np.linspace(0,70,281)
    curves = {}
    for name, location in (("M2",mu),("M3",mu+added)):
        with np.errstate(divide="ignore"):
            sf_age = log_ndtr(-(np.log(age)-location)/baseline["sigma"])
            sf_after = log_ndtr(-(np.log(age+grid)-location)/baseline["sigma"])
        cdf = np.clip(-np.expm1(sf_after-sf_age),0,1)
        cdf[0] = 0.0
        curves[name] = [float(x) for x in cdf]
    counts = {name:sum(bool(p["by_issue"]) == flag and bool(p["limit"]) == limit for p in points)
              for name,flag,limit in (("by_issue_detections",True,False),("later_detections",False,False),
                                      ("by_issue_limits",True,True),("later_limits",False,True))}
    public = dict(scope="ILLUSTRATION selected by observation time, not score/outcome; no new validation",
                  illustration=dict(selector="first 1960 issuance with extracted onset after JD2436934.5; minimum issue time, then emission index",
                                    source_feature_sha256=canonical_digest(feature), source_outcome_sha256=canonical_digest(outcome),
                                    issue_jd=issue, window_jd=window, relative_window_days=[window[0]-issue,70.0],
                                    threshold_magnitude=10.0,
                                    onset_bracket_days=[feature["onset_lo"]-issue,feature["onset_hi"]-issue],
                                    prefix_end_bracket_days=[feature["end_lo"]-issue,feature["end_hi"]-issue],
                                    later_onset_bracket_days=[outcome["onset_lo"]-issue,outcome["onset_hi"]-issue],
                                    observation_time_basis="reported JD only; historical upload/revision availability unknown",
                                    display_aggregation="one median per observer, floor(JD), detection/limit kind and side of issue; limits use strongest bound at its reported time",
                                    display_counts=counts,
                                    raw_display_points_public=False),
                  conditional_remaining_wait_cdf=dict(days_from_issue=grid.tolist(),models=curves,
                                                      baseline_route="M2" if timing_available else "M0 fallback"),
                  claim_ids=["C01","C05"])
    for path in (receipt_path,ledger_path,evidence_path):
        private_inputs[relative(path)] = dict(sha256=sha(path),purpose="saved illustrative feature/evidence selection")
    return public


def save(figure, stem, dpi=170):
    figure.savefig(FIGURES/(stem+".png"),dpi=dpi,bbox_inches="tight",pad_inches=.10,
                   metadata={"Software":"dwarf-nova-memory figures"},pil_kwargs={"compress_level":9})
    figure.savefig(FIGURES/(stem+".pdf"),bbox_inches="tight",pad_inches=.10,
                   metadata={"Creator":"dwarf-nova-memory figures","Producer":"Matplotlib",
                             "CreationDate":None,"ModDate":None})


def figure_three(plt, data):
    from matplotlib.ticker import PercentFormatter
    fig,axes=plt.subplots(1,2,figsize=(7.2,3.45),sharey=True,layout="constrained")
    names=("M0","M2","M3");labels=("Constant (M0)","Timing (M2)","Timing + duration (M3)")
    for ax,nominal,lim in zip(axes,(.5,.9),((.45,.66),(.85,1.005))):
        key=str(nominal)
        for k,(model,color) in enumerate(zip(names,(GREY,BLUE,ORANGE))):
            c=data["models"][model][key]
            lo,hi=c["coverage_lower_bound"],c["coverage_upper_bound"]
            ax.plot([lo,hi],[k,k],color=color,lw=3)
            ax.plot(lo,k,"o",color=color,ms=6)
            ax.plot(hi,k,"o",markerfacecolor="white",markeredgecolor=color,ms=6)
        ax.axvline(nominal,color=BLACK,ls="--",lw=1)
        ax.set_xlim(*lim);ax.set_yticks(range(3),labels);ax.set_title(f"Nominal {nominal:.0%} central interval",fontsize=10.5)
        ax.xaxis.set_major_formatter(PercentFormatter(1,decimals=0));ax.set_xlabel("Empirical coverage bounds")
    axes[0].invert_yaxis()
    fig.suptitle("All 441 outcomes, including right censoring",fontsize=12,fontweight="bold")
    fig.supxlabel("Filled/open ends: definite/possible coverage. Ranges are not sampling confidence intervals.",fontsize=8.1)
    save(fig,"fig3-calibration");plt.close(fig)


def figure_four(plt, data):
    fig=plt.figure(figsize=(7.2,7.0),layout="constrained")
    grid=fig.add_gridspec(2,2,height_ratios=[1.15,1])
    top=fig.add_subplot(grid[0,:]);within=fig.add_subplot(grid[1,0]);ratio=fig.add_subplot(grid[1,1])
    periods=data["periods"];labels=[x["label"] for x in periods]
    for k,p in enumerate(periods):
        top.barh(k-.14,p["type_lr"],height=.25,color=BLUE,label="12-day type indicator" if k==0 else None)
        top.barh(k+.14,p["continuous_lr"],height=.25,color=GREY,label="Continuous log duration" if k==0 else None)
        top.text(max(p["type_lr"],p["continuous_lr"])+.23,k,f"n={p['n_timing']}",fontsize=8.2,va="center")
        within.barh(k,p["within_given_type_lr"],height=.42,color=ORANGE)
        within.text(max(.012,p["within_given_type_lr"]+.008),k,f"{p['within_given_type_lr']:.3f}",va="center",fontsize=8)
        ratio.plot(p["clock_scale_ratio"],k,"o",color=BLUE,ms=5)
        ratio.text(p["clock_scale_ratio"]+.007,k,f"+{100*(p['clock_scale_ratio']-1):.1f}%",va="center",fontsize=8)
    top.set_yticks(range(4),labels);top.invert_yaxis();top.set_xlim(0,17.1)
    top.legend(loc="lower right",fontsize=8.4)
    top.set_title("A  Equal-dimension fitted alternatives",loc="left",fontsize=10.5)
    top.set_xlabel("2 × log-likelihood gain over level-only model")
    within.set_yticks(range(4),labels);within.invert_yaxis();within.set_xlim(0,.44)
    within.set_title("B  Adding within-type duration",loc="left",fontsize=10.5)
    within.set_xlabel("Additional 2 × log-likelihood gain")
    ratio.set_yticks(range(4),[""]*4);ratio.invert_yaxis();ratio.set_xlim(1.0,1.25)
    ratio.axvline(1,color=BLACK,ls="--",lw=.8)
    ratio.set_title("C  Conditional model-based contrast",loc="left",fontsize=10.5)
    ratio.set_xlabel("Long / short clock-scale ratio")
    fig.suptitle("Exploratory in-sample refits; no additional confirmation",fontsize=11.6,fontweight="bold")
    fig.supxlabel("A common level is re-fitted within each period; historical M2 nuisance is fixed.\nPeriods overlap. Ratios concern the untruncated working clock, not observed mean waits.",fontsize=8.1)
    save(fig,"fig4-type-exploration");plt.close(fig)


def illustrated_episodes(nights, lo=150, hi=250):
    """Outbursts in a fixed 1960 window, from nightly medians brighter than the threshold."""
    days = sorted(float(n["jd_floor"]) + 0.5 - START for n in nights
                  if n["median_magnitude"] and float(n["median_magnitude"]) <= 10 and lo <= float(n["jd_floor"]) + 0.5 - START <= hi)
    runs, run = [], [days[0]]
    for day in days[1:]:
        if day - run[-1] > 3:
            runs.append(run); run = []
        run.append(day)
    runs.append(run)
    complete = [(a[0], a[-1], b[0]) for a, b in zip(runs, runs[1:]) if a[0] > lo]
    if len(complete) < 2 or not (complete[1][1] - complete[1][0] > complete[0][1] - complete[0][0]):
        raise ValueError("the illustration window no longer shows a short then a long outburst")
    return complete[:2]


def graphical_abstract(plt, nights, gains):
    import numpy as np
    import matplotlib.colors as mcolors
    from matplotlib.patches import FancyBboxPatch, Ellipse, Circle, Rectangle, Arc, Polygon
    ink, muted, card_fill = "#22272B", "#4F5A61", "#F2F5F8"
    orange_text, slate, built = "#B34700", "#3B4750", "#D9E0E5"
    primary, blocks = gains["comparisons"][0], gains["blocks"]
    better_blocks = sum(block["mean_gain"] > 0 for block in blocks)
    if primary["lower"] <= 0 or (better_blocks, len(blocks), primary["n"]) != (8, 10, 441):
        raise ValueError("graphical-abstract statements differ from their evidence")
    W, H = 183.0, 104.0
    fig = plt.figure(figsize=(W / 25.4, H / 25.4))
    bg = fig.add_axes([0, 0, 1, 1]); bg.set_xlim(0, W); bg.set_ylim(0, H); bg.axis("off")
    note, body, title = 8.0, 8.4, 8.8

    def mm_axes(x0, y0, x1, y1):
        return fig.add_axes([x0 / W, y0 / H, (x1 - x0) / W, (y1 - y0) / H])

    def card(x0, y0, x1, y1):
        bg.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=2.6",
                                    facecolor=card_fill, edgecolor="none", zorder=0))

    def heading(x, y, text):
        bg.text(x, y, text, fontsize=8.6, fontweight="bold", color=muted, va="center", ha="left")

    def gradient(patch, cmap, extent, center=(0.5, 0.5)):
        bg.add_patch(patch)
        yy, xx = np.mgrid[0:1:300j, 0:1:300j]
        image = bg.imshow(np.hypot(xx - center[0], yy - center[1]), extent=extent, origin="lower", cmap=cmap,
                          interpolation="bicubic", zorder=patch.get_zorder(), aspect="auto")
        image.set_clip_path(patch)
        patch.set_facecolor("none")

    bg.text(4, H - 5.8, "How long an outburst lasts helps forecast when the next one begins",
            fontsize=13.2, fontweight="bold", color=ink, va="center")
    bg.text(4, H - 11.8, "SS Cygni and a century of amateur observations", fontsize=9.0, color=muted, va="center")

    # (1) the star: a sketch of the binary and real nightly data
    L0, L1, B0, B1 = 4, 63, 11, 86
    card(L0, B0, L1, B1); heading(L0 + 4, B1 - 4.6, "①  THE STAR")
    cx, cy, r = 15.5, 71.0, 6.0
    t = np.linspace(0, 2 * np.pi, 400)
    rx = r * (1 + 0.32 * np.clip(np.cos(t), 0, None) ** 3)
    star = Polygon(np.c_[cx + rx * np.cos(t), cy + 0.92 * r * np.sin(t)], closed=True, zorder=3)
    gradient(star, mcolors.LinearSegmentedColormap.from_list("star", ["#FFE0A3", "#F7A541", "#E0631B", "#B83E12"]),
             (cx - r, cx + 1.35 * r, cy - r, cy + r), center=(0.38, 0.62))
    dx, dy, dw, dh = 43.5, 70.5, 26.0, 8.0
    gradient(Ellipse((dx, dy), dw, dh, zorder=3),
             mcolors.LinearSegmentedColormap.from_list("disc", ["#FFFFFF", "#EAF4FA", "#C9E3F2", "#A9D2EA", "#8BBFDF"]),
             (dx - dw / 2, dx + dw / 2, dy - dh / 2, dy + dh / 2))
    bg.add_patch(Ellipse((dx, dy), dw, dh, facecolor="none", edgecolor="#7FAFCB", lw=0.6, zorder=4))
    for k in (0.72, 0.46):
        bg.add_patch(Ellipse((dx, dy), dw * k, dh * k, facecolor="none", edgecolor="white", lw=0.5, alpha=0.9, zorder=4))
    bg.add_patch(Circle((dx, dy), 1.4, facecolor="white", edgecolor="#9AA5AD", lw=0.6, zorder=5))
    p0, p1, p2 = np.array([cx + 1.30 * r, cy + 0.2]), np.array([27.0, 75.0]), np.array([dx - dw / 2 + 2.0, dy + 2.4])
    s = np.linspace(0, 1, 60)[:, None]
    stream = (1 - s) ** 2 * p0 + 2 * (1 - s) * s * p1 + s ** 2 * p2
    for i in range(len(stream) - 1):
        bg.plot(stream[i:i + 2, 0], stream[i:i + 2, 1], color=AMBER, lw=2.2 - 1.5 * i / len(stream),
                solid_capstyle="round", zorder=4)
    bg.add_patch(Circle(tuple(p2), 0.85, facecolor="#FFC857", edgecolor="none", zorder=5))
    bg.text(cx + 1, cy - r - 1.0, "companion\nstar", fontsize=note, color=muted, ha="center", va="top", linespacing=1.1)
    bg.text(dx, dy - dh / 2 - 1.0, "disc around\na white dwarf", fontsize=note, color=muted, ha="center", va="top",
            linespacing=1.1)
    bg.text((L0 + L1) / 2, 50.5, "Outbursts about every seven weeks", fontsize=body, color=ink, ha="center", va="center")

    lc = mm_axes(L0 + 7.0, 20.5, L1 - 2.5, 46.5)
    lo, hi = 150, 250
    points = [(float(n["jd_floor"]) + 0.5 - START, float(n["median_magnitude"])) for n in nights if n["median_magnitude"]]
    x, m = np.array([p for p in points if lo <= p[0] <= hi]).T
    breaks = np.flatnonzero(np.diff(x) > 3) + 1
    for run_x, run_m in zip(np.split(x, breaks), np.split(m, breaks)):
        lc.plot(run_x, run_m, color="#4D5A63", lw=0.8, zorder=3)
    lc.scatter(x, m, s=4, color="#4D5A63", lw=0, zorder=4)
    for (a, b, nxt), word in zip(illustrated_episodes(nights, lo, hi), ("short", "long")):
        lc.axvspan(a, b, color=ORANGE, alpha=0.16, lw=0, zorder=0)
        lc.plot([a, b], [7.7, 7.7], color=ORANGE, lw=1.6, solid_capstyle="butt")
        lc.text((a + b) / 2, 7.35, word, color=orange_text, fontsize=note, ha="center", va="bottom", fontweight="bold")
        lc.annotate("", xy=(nxt, 12.75), xytext=(b, 12.75), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.1,
                    mutation_scale=6, shrinkA=0, shrinkB=0))
        lc.text((b + nxt) / 2, 13.0, f"{round((nxt - b) / 7)}-week\nwait", color=BLUE, fontsize=note, ha="center",
                va="top", fontweight="bold", linespacing=1.05)
    lc.set_xlim(lo, hi); lc.set_ylim(15.2, 6.7); lc.axis("off")
    bg.text(L0 + 3.8, 33.5, "brighter", rotation=90, fontsize=note, color=muted, ha="center", va="center")
    bg.annotate("", xy=(L0 + 3.8, 43.5), xytext=(L0 + 3.8, 39.6), arrowprops=dict(arrowstyle="-|>", color=muted, lw=0.7,
                mutation_scale=5))
    bg.text((L0 + L1) / 2 + 2, 15.6, "Illustrative cycles from\n1960 nightly data", fontsize=note, color=muted,
            ha="center", va="center", linespacing=1.15)
    bg.add_patch(Polygon([[63.7, 51], [65.6, 48], [63.7, 45]], closed=True, facecolor="#C9D2D9", edgecolor="none"))

    # (2) the test and (3) the answer share one axis of observation years
    R0, R1 = 66.5, 179
    card(R0, B0, R1, B1)
    X0, X1 = 1908, 2028
    gx0, gx1 = R0 + 4.5, R1 - 17.0

    def xmm(year):
        return gx0 + (year - X0) / (X1 - X0) * (gx1 - gx0)

    heading(xmm(1910), B1 - 4.6, "②  THE TEST")
    heading(xmm(1960) - 0.6, B1 - 4.6, "③  THE ANSWER")

    def chip(y, lines, edge, fill, color):
        w, h = xmm(1956) - xmm(1910), 3.8 + 3.3 * len(lines)
        bg.add_patch(FancyBboxPatch((xmm(1910), y - h / 2), w, h, boxstyle="round,pad=0,rounding_size=2.4", facecolor=fill,
                                    edgecolor=edge, lw=0.9, zorder=4))
        bg.text(xmm(1910) + w / 2, y, "\n".join(lines), fontsize=body, color=color, ha="center", va="center", zorder=5,
                linespacing=1.15)

    bg.text(xmm(1910), 74.6, "Two forecasters", fontsize=title, color=ink, fontweight="bold", ha="left", va="center")
    chip(67.4, ["recent quiet spells"], "#7F8C95", "white", ink)
    chip(58.4, ["recent quiet spells", "+ outburst length"], ORANGE, "#FFF1E8", orange_text)

    ty, th = 20.5, 6.6
    bg.add_patch(FancyBboxPatch((xmm(1910), ty), xmm(1960) - xmm(1910), th, boxstyle="round,pad=0,rounding_size=1.2",
                                facecolor=built, edgecolor="none", zorder=2))
    bg.add_patch(Rectangle((xmm(1960), ty), xmm(2018) - xmm(1960), th, facecolor=slate, edgecolor="none", zorder=2))
    bg.add_patch(Rectangle((xmm(2018), ty), xmm(2027) - xmm(2018), th, facecolor="white", edgecolor="#9AA5AD", lw=0.6,
                           hatch="////", zorder=2))
    bg.text((xmm(1910) + xmm(1960)) / 2, ty + th / 2, "used for fitting", fontsize=body, color=ink, ha="center",
            va="center", zorder=3)
    bg.text((xmm(1960) + xmm(2018)) / 2, ty + th / 2, f"{primary['n']} forecasts scored", fontsize=body, color="white",
            ha="center", va="center", fontweight="bold", zorder=3)
    bg.text(xmm(2027) + 1.2, ty + th / 2, "unopened", fontsize=note, color=muted, ha="left", va="center")
    for year in (1910, 1960, 2018):
        bg.text(xmm(year), ty - 1.3, str(year), fontsize=note, color=muted, ha="center", va="top")
    bg.text((xmm(1910) + xmm(2027)) / 2, ty - 5.4, "years of observations", fontsize=note, color=muted,
            ha="center", va="top", style="italic")

    lx, ly = xmm(1960), 37.0
    bg.add_patch(FancyBboxPatch((lx - 2.1, ly - 1.9), 4.2, 3.4, boxstyle="round,pad=0,rounding_size=0.6", facecolor=ink,
                                edgecolor="none", zorder=6))
    bg.add_patch(Arc((lx, ly + 1.5), 2.9, 3.4, theta1=0, theta2=180, color=ink, lw=1.4, zorder=6))
    bg.add_patch(Circle((lx, ly - 0.3), 0.42, facecolor="white", edgecolor="none", zorder=7))
    bg.plot([lx, lx], [ty + th, ly - 1.9], color=ink, lw=0.7, zorder=5)
    bg.text(lx - 3.2, ly + 0.2, "Frozen and published\nin 2026, before the\ntest records were opened", fontsize=note,
            color=ink, ha="right", va="center", linespacing=1.15, fontweight="bold")

    y_lo, y_hi, gy0, gy1 = -0.018, 0.048, 36.0, 59.5

    def ymm(v):
        return gy0 + (v - y_lo) / (y_hi - y_lo) * (gy1 - gy0)

    gain = mm_axes(xmm(1960), gy0, xmm(2018), gy1)
    gain.set_xlim(1960, 2018); gain.set_ylim(y_lo, y_hi); gain.axis("off")
    gain.fill_between([1960, 2018], primary["lower"], primary["upper"], color=BLUE, alpha=0.14, lw=0, zorder=1)
    gain.plot([1960, 2018], [primary["estimate"]] * 2, color=BLUE, lw=1.6, zorder=2)
    gain.plot([1960, 2018], [0, 0], color="#8A959D", lw=0.8, zorder=1)
    for block in blocks:
        year = 1960 + ((block["start_jd"] + block["end_jd"]) / 2 - START) / 365.25
        better = block["mean_gain"] > 0
        gain.plot(year, block["mean_gain"], "o", ms=5.0, color=ORANGE if better else "white", mec=ORANGE, mew=1.1,
                  zorder=4)
    side = xmm(2018) + 1.2
    bg.text(side, ymm(primary["estimate"]) + 1.6, "overall", fontsize=note, color=BLUE, ha="left", va="center",
            fontweight="bold")
    bg.text(side, ymm(primary["estimate"]) - 1.8, "90% interval", fontsize=note, color=BLUE, ha="left", va="center")
    bg.text(side, ymm(0), "no gain", fontsize=note, color=muted, ha="left", va="center")
    bg.annotate("", xy=(side + 1.0, ymm(0.047)), xytext=(side + 1.0, ymm(0.033)),
                arrowprops=dict(arrowstyle="-|>", color=muted, lw=0.7, mutation_scale=5))
    bg.text(side + 2.6, ymm(0.040), "score\ngain", fontsize=note, color=muted, ha="left", va="center", linespacing=1.05)
    bg.text(xmm(1960) - 0.6, 73.4, f"Better overall, and in\n{better_blocks} of {len(blocks)} periods", fontsize=title,
            color=ink, fontweight="bold", ha="left", va="center", linespacing=1.15)
    bg.text(xmm(1960) - 0.6, 64.6, "Small gain; 90% interval above zero,\nmeeting the pre-set criterion", fontsize=note,
            color=muted, ha="left", va="center", linespacing=1.15)
    bg.text(xmm(1960) + 3.2, 31.4, "Six-year periods (last: four years);\nopen dots: worse", fontsize=note, color=muted,
            ha="left", va="center", linespacing=1.15)

    bg.text(4, 4.6, "Other stars", fontsize=body, color=ink, fontweight="bold", ha="left", va="center")
    bg.text(24.5, 4.6, "None of ten other dwarf novae passed the pre-set early-record checks.", fontsize=body,
            color=muted, ha="left", va="center")
    return fig


def g3a_figure(plt, rows):
    from matplotlib.ticker import PercentFormatter
    fig, (eligible, supported) = plt.subplots(1, 2, figsize=(7.2, 6.0), sharey=True,
                                             gridspec_kw={"width_ratios": [1.1, 1]}, layout="constrained")
    labels = []
    for index, row in enumerate(rows):
        held = bool(row["eclipse_required"])
        morphology_failed = not row["morphology_passed"]
        color = ORANGE if morphology_failed else GREY if held else BLUE
        marker = "D" if held else "X" if morphology_failed else "o"
        labels.append(row["star"] + (" †" if held else " *" if morphology_failed else ""))
        eligible.plot([0, row["eligible_fraction"]], [index, index], color=color, lw=1.8, alpha=.45)
        eligible.plot(row["eligible_fraction"], index, marker, color=color, ms=6,
                      markerfacecolor="white" if held else color)
        eligible.text(row["eligible_fraction"] + .035, index, f"{row['eligible_fraction']:.1%}",
                      va="center", fontsize=8.4, color=BLACK, bbox=dict(facecolor="white", edgecolor="none", pad=.3))
        supported.barh(index, row["outcome_supported"], height=.42, color=color, alpha=.8,
                       hatch="///" if held else None)
        supported.text(row["outcome_supported"] + 2, index, str(row["outcome_supported"]),
                       va="center", fontsize=8.5, color=BLACK, bbox=dict(facecolor="white", edgecolor="none", pad=.3))
    eligible.axvline(.7, color=BLACK, lw=1, ls="--")
    supported.axvline(40, color=BLACK, lw=1, ls="--")
    eligible.set_yticks(range(len(rows)), labels)
    eligible.set_ylim(len(rows) - .45, -.8)
    eligible.set_xlim(0, 1.08); eligible.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    supported.set_xlim(0, 128)
    eligible.set_title("A  Eligible onset windows", loc="left", fontsize=10.3)
    supported.set_title("B  Supported development issues", loc="left", fontsize=10.3)
    eligible.set_xlabel("Eligible / confirmed events\nDashed gate: 70%")
    supported.set_xlabel("Outcome-supported marked DF issues\nDashed gate: 40")
    eligible.set_xticks((0, .25, .5, .7, 1.))
    supported.set_xticks((0, 40, 80, 120))
    fig.suptitle("Frozen pre-1990 transfer screen: no star qualifies", fontsize=12, fontweight="bold")
    fig.supxlabel("* SS Aur fails the operational long-bright-run gate; this is not a subtype diagnosis.\n† U Gem / IP Peg use derived fixed-night streams; the eclipse guard did not pass.\nCount and window gates are necessary; base convergence, morphology and eclipse gates also apply.", fontsize=7.9)
    save(fig, "fig6-g3a-feasibility"); plt.close(fig)


PURPLE, GREEN, SKY, AMBER = "#7B5A80", "#009E73", "#56B4E9", "#E69F00"


def bracket(ax, x0, x1, y, text, *, below=False, color=BLACK, size=8.3):
    tick = -.06 if below else .06
    ax.plot([x0, x0, x1, x1], [y+tick, y, y, y+tick], color=color, lw=1, clip_on=False)
    ax.text((x0+x1)/2, y+(-.09 if below else .09), text, ha="center", va="top" if below else "bottom",
            fontsize=size, color=color)


def context_figure(plt, nights):
    import numpy as np
    from matplotlib.patches import Rectangle
    sigma = load(PARAMETERS)["primary"]["models"]["M2"]["sigma"]
    assert sigma == load(PARAMETERS)["primary"]["models"]["M3"]["sigma"]
    fig = plt.figure(figsize=(7.2, 7.7), layout="constrained")
    grid = fig.add_gridspec(4, 2, height_ratios=[1.2, 1.75, .66, .88], width_ratios=[1, 1.25])

    ax = fig.add_subplot(grid[0, :])
    year = lambda jd: 1960 + (jd - START)/365.25
    det = [r for r in nights if r["median_magnitude"] != ""]
    lim = [r for r in nights if r["median_magnitude"] == "" and r["faintest_limit"] != ""]
    run, runs = [], []
    for r in det:
        if run and float(r["jd_floor"])-float(run[-1]["jd_floor"]) > 3:
            runs.append(run); run = []
        run.append(r)
    runs.append(run)
    for run in runs:
        ax.plot([year(float(r["jd_floor"])+.5) for r in run], [float(r["median_magnitude"]) for r in run], color=BLUE, lw=.6, alpha=.5, zorder=2)
    ax.scatter([year(float(r["jd_floor"])+.5) for r in det], [float(r["median_magnitude"]) for r in det],
               s=10, color=BLUE, alpha=.9, linewidths=0, zorder=3, label="Nightly median of detections")
    for r in lim:
        x, y = year(float(r["jd_floor"])+.5), float(r["faintest_limit"])
        ax.annotate("", xy=(x, y+.3), xytext=(x, y), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=.8, mutation_scale=6), zorder=2)
    ax.scatter([], [], marker="$\\downarrow$", color=GREY, label="Fainter-than bound (night without a detection)")
    ax.axhline(10, color=BLACK, ls=":", lw=1, label="Extraction threshold (magnitude 10)")
    mags = [float(r["median_magnitude"]) for r in det] + [float(r["faintest_limit"]) for r in lim]
    ax.set_ylim(max(mags)+.5, min(mags)-.4)
    ax.set_xlim(year(LIGHT_CURVE_WINDOW[0]), year(LIGHT_CURVE_WINDOW[1]))
    ax.set_xticks((1960, 1961, 1962))
    ax.set_xlabel("Year (first two years of the held-out period)")
    ax.set_ylabel("Visual magnitude\n(fainter downward)")
    ax.legend(loc="lower center", bbox_to_anchor=(.5, 1.0), ncol=3, fontsize=7.4, frameon=False, handletextpad=.3, columnspacing=1.2)
    ax.set_title("A  SS Cyg, 1960–1961: one summary value per night", loc="left", fontsize=10.5, pad=24)

    sub = grid[1, :].subgridspec(2, 1, height_ratios=[1.35, 1], hspace=.04)
    curve, dens = fig.add_subplot(sub[0]), fig.add_subplot(sub[1], sharex=None)
    t = np.linspace(0, 124, 2000)
    def burst(t0, d):
        return 1/(1+np.exp(-(t-t0)/.7))*1/(1+np.exp((t-(t0+d))/1.1))*(1-.12*np.clip(t-t0, 0, d)/d)
    seen = burst(6, 5)+burst(36, 15)
    issue, end2, onset3 = 54., 51., 86.
    curve.plot(t[t <= issue], seen[t <= issue], color=BLACK, lw=1.8)
    curve.plot(t[t >= issue], (seen+burst(onset3, 9))[t >= issue], color=BLACK, lw=1.4, ls=(0, (3, 2)), alpha=.55)
    bracket(curve, 36, 51, 1.12, "outburst duration")
    bracket(curve, 11, 36, -.2, "previous quiet\ninterval", below=True)
    bracket(curve, 51, onset3, -.2, "quiet interval\n(the forecast target)", below=True)
    curve.text(21, 1.12, "earlier outburst", ha="center", va="bottom", fontsize=8.3, color=GREY)
    curve.text(110, .72, "next outburst\n(not yet seen)", ha="center", va="center", fontsize=8.3, color=GREY)
    curve.set(xlim=(0, 124), ylim=(-.95, 1.75), ylabel="Brightness", yticks=[], xticks=[])
    for a in (curve, dens):
        a.axvline(issue, color=BLACK, ls="--", lw=1)
        a.axvspan(onset3-1.2, onset3+1.2, color=PURPLE, alpha=.25, lw=0)
    curve.text(issue+1.2, 1.45, "issue time: reports\nconfirm the fade", ha="left", va="center", fontsize=8.3)
    curve.text(onset3+2.5, 1.45, "scored\nonset window", ha="left", va="center", fontsize=8.3, color=PURPLE)
    curve.spines["bottom"].set_visible(False)
    gap = np.clip(t-end2, 0, None)
    def density(median, sigma):
        g = np.where(gap > 3, gap, np.nan)
        pdf = np.exp(-(np.log(g)-np.log(median))**2/(2*sigma**2))/(g*sigma*np.sqrt(2*np.pi))
        pdf = np.where(t >= issue, pdf, np.nan)
        return pdf/np.nansum(pdf)/(t[1]-t[0])
    for median_gap, color, label in ((30, BLUE, "Timing-only forecast"), (35, ORANGE, "Timing + duration forecast")):
        pdf = density(median_gap, sigma)
        dens.plot(t, pdf, color=color, lw=2, label=label)
        dens.fill_between(t, 0, np.nan_to_num(pdf), color=color, alpha=.14, lw=0)
    dens.set(xlim=(0, 124), yticks=[], xticks=[], xlabel="Time (schematic; not to scale)", ylabel="Forecast\ndensity")
    dens.set_ylim(0, None)
    dens.legend(loc="upper left", bbox_to_anchor=(0, 1.0), fontsize=8.2, frameon=False)
    curve.set_title("B  Schematic of one cycle (illustration, not data)", loc="left", fontsize=10.5)

    years = fig.add_subplot(grid[2, :])
    rows = {row["label"]: row for row in TIMELINES["observation_years"]}
    spans = ((1, 1910, 1959+1, SKY, "Development fit\n1910–1959"), (1, 1960, 2017+1, BLUE, "Held-out test\n1960–2017"))
    for y, x0, x1, color, text in spans:
        years.barh(y, x1-x0, left=x0, height=.62, color=color)
        years.text((x0+x1)/2, y, text, ha="center", va="center", fontsize=8, color="white" if color == BLUE else BLACK)
    years.barh(1, 2030-2018, left=2018, height=.62, facecolor="white", edgecolor=GREY, hatch="///", lw=1)
    years.text(2024, 1, "Closed\n2018 →", ha="center", va="center", fontsize=8, bbox=dict(facecolor="white", edgecolor="none", pad=1))
    years.barh(0, 1990-1900, left=1900, height=.62, color=AMBER, alpha=.85)
    years.text(1945, 0, "Candidate stars: pre-1990 records only", ha="center", va="center", fontsize=8)
    years.set(xlim=(1900, 2030), ylim=(-.6, 1.6), yticks=(0, 1), xlabel="Year of observation")
    years.set_yticklabels(("Ten other\ndwarf novae", "SS Cyg"))
    years.set_title("C  Which years were used, and when the analysis was done", loc="left", fontsize=10.5)

    left, right = fig.add_subplot(grid[3, 0]), fig.add_subplot(grid[3, 1])
    minutes = lambda stamp: (int(stamp[11:13])-12)*60+int(stamp[14:16])-30+int(stamp[17:19])/60
    events = {e["label"]: e for e in TIMELINES["analysis_sequence"]["events"]}
    freeze = minutes(events["Protocol frozen; Zenodo deposit 10.5281/zenodo.24053338"]["at"])
    scored = minutes(events["Primary result scored"]["at"])
    for label, color, text in (("First data access; fails on a parser error", ORANGE, ""), ("Parser repair (outcome-independent)", GREY, "repair"),
                               ("Repaired data access", BLUE, "")):
        e = events[label]
        left.barh(0, minutes(e["end"])-minutes(e["start"]), left=minutes(e["start"]), height=.8, color=color)
    left.plot([freeze], [0], "*", color=BLACK, ms=11, zorder=4)
    left.plot([scored], [0], "D", color=BLACK, ms=6, zorder=4)
    left.annotate("Protocol frozen;\nZenodo deposit\n10.5281/zenodo.24053338", xy=(freeze, .1), xytext=(freeze-3.8, 1.0), fontsize=7.4, va="bottom", ha="left",
                  arrowprops=dict(arrowstyle="-", lw=.7))
    left.annotate("first access\nfails (parser)", xy=(9.2, -.4), xytext=(9.2, -.95), fontsize=7.4, va="top", ha="center", color=BLACK,
                  arrowprops=dict(arrowstyle="-", lw=.7))
    left.text(15.6, 0, "repair", ha="center", va="center", fontsize=7.4, color="white")
    left.annotate("repaired\naccess", xy=(25.9, -.4), xytext=(26.8, -.95), fontsize=7.4, va="top", ha="center", color=BLACK,
                  arrowprops=dict(arrowstyle="-", lw=.7))
    left.annotate("primary result\nscored", xy=(scored, .1), xytext=(scored+.4, .75), fontsize=7.4, va="bottom", ha="center",
                  arrowprops=dict(arrowstyle="-", lw=.7))
    left.set(xlim=(0, 40), ylim=(-1.9, 2.2), yticks=[], xticks=(0, 10, 20, 30, 40))
    left.set_xticklabels(("12:30", "12:40", "12:50", "13:00", "13:10"))
    left.set_xlabel("8 November, UTC", fontsize=8.6)
    left.spines["right"].set_visible(False)
    hours = lambda stamp: (int(stamp[8:10])-8)*24+int(stamp[11:13])+int(stamp[14:16])/60+int(stamp[17:19])/3600
    for label, color in (("Post-result checks", GREY), ("Frozen transfer screen", PURPLE)):
        e = events[label]
        right.barh(0, hours(e["end"])-hours(e["start"]), left=hours(e["start"]), height=.8, color=color)
    checks, screen = events["Post-result checks"], events["Frozen transfer screen"]
    right.text((hours(checks["start"])+hours(checks["end"]))/2, 0, "SS Cyg post-result checks", ha="center", va="center", fontsize=7.4, color="white")
    right.annotate("frozen transfer\nscreen", xy=(hours(screen["start"])+.8, .4), xytext=(hours(screen["start"])+.8, .95), fontsize=7.4,
                   va="bottom", ha="center", arrowprops=dict(arrowstyle="-", lw=.7))
    right.set(xlim=(13.2, 56), ylim=(-1.9, 2.2), yticks=[], xticks=(24, 48))
    right.set_xticklabels(("9 Nov 00:00", "10 Nov 00:00"))
    right.set_xlabel("UTC", fontsize=8.6)
    right.spines["left"].set_visible(False)
    for ax_, x in ((left, 1), (right, 0)):
        ax_.plot([x-.02, x+.02], [-.02, .02], transform=ax_.transAxes, color=BLACK, lw=1, clip_on=False)
    left.set_title("Analysis sequence, November 2026 (a separate clock; the axis breaks after 13:10 UTC on 8 November)", loc="left", fontsize=8.6, x=0)
    save(fig, "fig1-context"); plt.close(fig)


def forecast_figure(plt, f1, f2):
    fig, (ax, blocks) = plt.subplots(2, 1, figsize=(7.2, 6.9), gridspec_kw={"height_ratios": [1, 1.05]}, layout="constrained")
    item, cdf = f1["illustration"], f1["conditional_remaining_wait_cdf"]
    example = load(R1_EXAMPLE)["figure1"]["models"]
    days = cdf["days_from_issue"]
    for model, color, label in (("M2", BLUE, "Frozen timing-only (M2)"), ("M3", ORANGE, "Frozen timing + duration (M3)")):
        ax.plot(days, cdf["models"][model], color=color, lw=2, label=label)
        value = example[model]["public_grid_probability_within_30_days"]
        ax.plot(30, value, "o", color=color, ms=5, zorder=4)
        x, y, align = (32, .52, "left") if model == "M2" else (28.8, .69, "right")
        ax.text(x, y, f"{value:.3f}", color=color, fontsize=8.4, va="center", ha=align)
    ax.axvline(30, color=GREY, ls=":", lw=1)
    ax.axvspan(*item["later_onset_bracket_days"], color=PURPLE, alpha=.28, lw=0)
    ax.text(item["later_onset_bracket_days"][1]+1.2, .1, "onset interval that\nscored the forecast", ha="left", va="bottom", fontsize=8.4, color=PURPLE)
    ax.text(30.6, .02, "30 days", fontsize=8, color=GREY, va="bottom", ha="left")
    ax.set(xlim=(0, 70), ylim=(0, 1.02), xlabel="Days from forecast issue (JD %.1f)" % item["issue_jd"],
           ylabel="Probability that the next onset\nhas occurred by this wait")
    ax.legend(loc="upper left", fontsize=8.4, frameon=False)
    ax.set_title("A  One example forecast: frozen distributions, conditioned once on survival to issue", loc="left", fontsize=10.2)
    for k, row in enumerate(f2["blocks"]):
        blocks.plot(row["mean_gain"], k, "o", color=GREY, ms=5.5, zorder=3)
    primary = f2["comparisons"][0]
    blocks.axvspan(primary["lower"], primary["upper"], color=BLUE, alpha=.16, lw=0)
    blocks.axvline(primary["estimate"], color=BLUE, lw=1.4)
    blocks.axvline(0, color=BLACK, lw=.9)
    blocks.set_yticks(range(len(f2["blocks"])), [f"{row['nominal_year_label']}  (n={row['n']})" for row in f2["blocks"]])
    blocks.invert_yaxis(); blocks.set_xlim(-.022, .06)
    blocks.text(.0305, 8.5, f"pooled mean {primary['estimate']:.4f}\n90% interval {primary['lower']:.4f} to {primary['upper']:.4f}",
                color=BLUE, fontsize=8.4, va="center", ha="left")
    blocks.set_xlabel("Mean gain, timing + duration minus timing-only (nats per forecast)")
    blocks.set_ylabel("Six-year block")
    blocks.set_title("B  Gain in each six-year block of the held-out period (441 forecasts)", loc="left", fontsize=10.2)
    save(fig, "fig2-forecast"); plt.close(fig)


def robustness_figure(plt, rows):
    fig = plt.figure(figsize=(7.2, 5.9), layout="constrained")
    grid = fig.add_gridspec(1, 3, width_ratios=[2.35, 2.9, 1.3])
    names, ax, values = fig.add_subplot(grid[0]), fig.add_subplot(grid[1], sharey=None), fig.add_subplot(grid[2])
    heads = dict(a="(a) Preregistered secondaries", b="(b) Measurement checks", c="(c) Drift-recalibrated diagnostics (exploratory)")
    style = dict(a=(BLUE, "o"), b=(ORANGE, "s"), c=(GREEN, "^"))
    position, y = [], 0.
    last = None
    reference = next(r for r in rows if r["group"] == "reference")
    for row in rows:
        if row["group"] == "reference":
            continue
        if row["group"] != last:
            y += .5 if last else 0
            names.text(0, y, heads[row["group"]], ha="left", va="center", fontsize=8.6, fontweight="bold")
            y += .85
            last = row["group"]
        position.append((y, row))
        y += 1.0
    for y, row in position:
        color, marker = style[row["group"]]
        names.text(0, y-.17, f"{row['row']}", ha="left", va="center", fontsize=8.3)
        baseline = row["baseline"].replace(" drift-recalibrated", " (recal.)")
        names.text(0, y+.2, f"{row['clock']}; {baseline}; n={row['n']}", ha="left", va="center", fontsize=7.1, color="#555B61")
        ax.plot([row["lower"], row["upper"]], [y, y], color=color, lw=2.4, solid_capstyle="butt")
        ax.plot(row["estimate"], y, marker, color=color, ms=6.5)
        values.text(0, y, f"{row['estimate']:.4f}  [{row['lower']:.4f}, {row['upper']:.4f}]".replace("-", "−"), ha="left", va="center", fontsize=7.6)
    top, bottom = -.6, y-.3+.8
    for a in (names, ax, values):
        a.set_ylim(bottom, top)
    ax.axvline(0, color=BLACK, lw=.9)
    ax.axvline(reference["estimate"], color=BLUE, ls="--", lw=1.2)
    ax.text(reference["estimate"]+.0007, top+.1, f"primary, {reference['estimate']:.4f}", color=BLUE, fontsize=8, va="top", ha="left")
    ax.set_xlim(-.016, .042)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Gain from adding duration (nats per forecast)")
    names.set_xlim(0, 1); values.set_xlim(0, 1)
    names.set_title("Row, clock; baseline; scored n", loc="left", fontsize=8.3, fontweight="normal")
    values.set_title("Estimate [90% interval]", loc="left", fontsize=8.3, fontweight="normal")
    for a in (names, values):
        a.axis("off")
    save(fig, "fig3-robustness"); plt.close(fig)


def transfer_figure(plt, rows):
    candidates = sorted((r for r in rows if r["row_type"] == "candidate"), key=lambda r: (-r["supported_development"], r["star"]))
    reference = next(r for r in rows if r["row_type"] == "reference")
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 5.2), sharey=True, gridspec_kw={"width_ratios": [.9, 1.15]}, layout="constrained")
    labels, held = [], lambda r: r["stream"].startswith("derived")
    ypos = list(range(len(candidates)))
    ref_y = len(candidates)+.6
    def color(r):
        return ORANGE if not r["morphology_passed"] else BLUE
    for y, r in zip(ypos, candidates):
        labels.append(r["star"] + (" *" if not r["morphology_passed"] else "") + (" †" if held(r) else ""))
        a.barh(y, r["supported_development"], height=.55, color=color(r), alpha=.85, hatch="///" if held(r) else None,
               edgecolor="white" if held(r) else None)
        a.text(r["supported_development"]+2, y, str(r["supported_development"]), va="center", fontsize=8.4)
        b.plot(r["ratio"], y, "o", color=color(r), ms=6.5, markerfacecolor="white" if held(r) else color(r), markeredgewidth=1.5)
        b.text(r["ratio"]+.03, y, f"{r['supported_1980_1989']}/{r['confirmed_peaks_1980_1989']}", va="center", fontsize=8.2)
    a.barh(ref_y, 128, height=.55, color="#BEC3C7")
    a.text(64, ref_y, f"{reference['supported_development']} (axis truncated) →", ha="center", va="center", fontsize=8.2)
    b.plot(reference["ratio"], ref_y, "D", color=BLACK, ms=6.5)
    b.text(reference["ratio"]+.03, ref_y, f"{reference['supported_1980_1989']}/{reference['confirmed_peaks_1980_1989']}", va="center", fontsize=8.2)
    pooled = sum(r["supported_1980_1989"] for r in candidates)/sum(r["confirmed_peaks_1980_1989"] for r in candidates)
    b.axvline(pooled, color=GREY, ls=":", lw=1.2)
    b.text(pooled+.015, len(candidates)-1.15, f"all ten: {sum(r['supported_1980_1989'] for r in candidates)}/{sum(r['confirmed_peaks_1980_1989'] for r in candidates)}",
           color="#555B61", fontsize=8, va="bottom", ha="left", rotation=0)
    a.axvline(40, color=BLACK, ls="--", lw=1)
    a.text(41.5, -.62, "gate: 40", fontsize=8, va="center")
    labels.append("SS Cyg (reference)")
    a.set_yticks(ypos+[ref_y], labels)
    a.set_ylim(ref_y+.6, -1.0)
    a.set_xlim(0, 132)
    b.set_xlim(0, 1.12)
    b.set_xticks((0, .25, .5, .75, 1.0))
    a.set_xlabel("Supported forecasts in\navailable pre-1990 records", fontsize=9)
    b.set_xlabel("Supported issuances /\nconfirmed episode peaks (1980–1989)", fontsize=9)
    a.set_title("A  Forecast count per star", loc="left", fontsize=10.4)
    b.set_title("B  Operational yield, 1980–1989", loc="left", fontsize=10.4)
    from matplotlib.patches import Patch
    a.legend(handles=[Patch(color=ORANGE, alpha=.85, label="* SS Aur: passes the count,\nfails the long-run gate"),
                      Patch(facecolor=BLUE, hatch="///", edgecolor="white", label="† derived fixed-night stream")],
             loc="lower right", bbox_to_anchor=(1.0, .1), fontsize=7.8, frameon=False)
    save(fig, "fig4-transfer"); plt.close(fig)


def plotting():
    SCRATCH.mkdir(parents=True,exist_ok=True);FIGURES.mkdir(parents=True,exist_ok=True);DATA.mkdir(parents=True,exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR",str(SCRATCH/"matplotlib"))
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import font_manager
    from matplotlib import pyplot as plt
    import scipy
    matplotlib.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.labelsize":10,
                                "xtick.labelsize":9,"ytick.labelsize":9,"axes.spines.top":False,
                                "axes.spines.right":False,"pdf.fonttype":42,"ps.fonttype":42,
                                "pdf.compression":9,"figure.facecolor":"white","axes.facecolor":"white"})
    return np, plt, scipy, matplotlib, font_manager


def write_aggregate_data():
    for name, rows in aggregate_tables().items():
        with (DATA/name).open("w", newline="") as handle:
            handle.write(csv_text(rows))
    write_claim_values(load(PRIMARY), load(SUMMARY), load(REVIEW))


def manifest_for(np, scipy, matplotlib, font_manager, private_inputs):
    public_inputs={relative(p):dict(sha256=sha(p)) for p in (PRIMARY,SUMMARY,REVIEW,PARAMETERS,NATIVE_CODE,ROOT/"uv.lock")}
    aggregate_inputs={relative(p):dict(sha256=sha(p)) for p in (R2B,G3A,G3A_DETAILS,PRECISION,R1_SCORES,R2B_CHECK,R2D,G3A_CHECK,C70,R1_EXAMPLE)}
    font=Path(font_manager.findfont("DejaVu Sans"))
    return dict(schema_version=2,generator=relative(__file__),generator_sha256=sha(__file__),
                scope="seven static scientific figures (four main-text, three appendix) and the graphical abstract used in the brief",
                source_freeze_sha1="5e39aeb772c427ef29671c1a9c80b22c05519b58",source_execution_commit_sha1="d7151e0da48ce3d3f91e38d94b8bfdc656272dd0",
                protocol_doi="10.5281/zenodo.24053338",
                post_result_status="frozen comparison and illustration retained; R2b exploratory working-score contrasts; G3a gain-free development feasibility; precision rows are point-Gaussian simulations",
                public_inputs=public_inputs,aggregate_inputs=aggregate_inputs,private_inputs=private_inputs,
                runtime=dict(python=sys.version.split()[0],numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__),
                font=dict(family="DejaVu Sans",file=font.name,sha256=sha(font),pdf_embedding="TrueType; pdf.fonttype42"),
                output_policy=dict(raw_photometry_table=False,observer_identifiers=False,new_event_catalog=False,per_issuance_scores=False,
                                   fig1_public_data="nightly light-curve aggregates for a fixed 1960-1961 window; fig2 example from one derived bracket set and model CDF grid; no observation rows, observer identifiers or event times"),
                figure_data={relative(DATA/name):dict(sha256=sha(DATA/name),bytes=(DATA/name).stat().st_size) for name in DATA_NAMES},assets=asset_records())


def generate():
    np, plt, scipy, matplotlib, font_manager = plotting()
    from scipy.special import log_ndtr
    primary,summary,review=load(PRIMARY),load(SUMMARY),load(REVIEW)
    if sha(PARAMETERS) != "ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3":
        raise ValueError("the frozen model parameters changed")
    private_inputs={}
    f1=illustration(np,log_ndtr,private_inputs)
    nights=lightcurve_nights(private_inputs)
    blocks=[]
    for b in review["interval_recomputation"]["blocks"]:
        k=b["block"]
        blocks.append(dict(block=k,n=b["n"],mean_gain=b["mean_gain"],
                           start_jd=START+k*2191.5,end_jd=min(STOP,START+(k+1)*2191.5),
                           nominal_year_label=f"{1960+6*k}–{min(2017,1965+6*k)}",interval="none; descriptive means only"))
    comparisons=[]
    for name,kind,value in (("Primary 1960–2017","sole primary",primary),
                            ("1960–1992 segment","secondary",summary["secondary"]["era_split"]["1960_1992"]),
                            ("1993–2017 segment","secondary",summary["secondary"]["era_split"]["1993_2017"]),
                            ("Long/short rule","secondary",summary["secondary"]["robustness"]["type_within"]["gain_M3_M2"])):
        comparisons.append(dict(name=name,kind=kind,**{k:value[k] for k in ("n","estimate","lower","upper")}))
    f2=dict(scope="one pooled primary comparison; all block means and other contrasts descriptive/secondary",blocks=blocks,comparisons=comparisons,
            cluster_days=2191.5,year_labels="nominal; exact boundaries are in JD",derived_units=derived_units(primary,summary),claim_ids=["C01","C06","C07","C08","C25"])
    f3=dict(scope="empirical partial-identification coverage bounds, not sampling confidence intervals; all scored outcomes",
            n=primary["n"],models={m:x["central_intervals"] for m,x in summary["secondary"]["calibration"]["models"].items()},claim_ids=["C11"])
    ti=review["type_information"]
    periods=[]
    all_periods=[("Development\n1910–1959",ti["development_refits_in_sample"]["1910-1959"]),
                 ("All evaluation\n1960–2017",ti["refits_frozen_M2_nuisance_free_level"]["1960-2017"]),
                 ("Early segment\n1960–1992",ti["refits_frozen_M2_nuisance_free_level"]["1960-1992"]),
                 ("Later segment\n1993–2017",ti["refits_frozen_M2_nuisance_free_level"]["1993-2017"])]
    for label,p in all_periods:
        periods.append(dict(label=label,n_timing=p["n_timing"],type_lr=p["type_only"]["lr_vs_level_only"],
                            continuous_lr=p["raw_log_duration"]["lr_vs_level_only"],
                            within_given_type_lr=p["type_plus_within"]["lr_within_given_type"],
                            type_contrast=p["type_only"]["beta_type_long_minus_short"],
                            clock_scale_ratio=math.exp(p["type_only"]["beta_type_long_minus_short"])))
    f4=dict(scope="EXPLORATORY in-sample refits; nonnested type/continuous comparison, not exclusive attribution or validated type forecasting",
            periods=periods,evaluation_refits=ti["refits_frozen_M2_nuisance_free_level"],
            nuisance="historical M2 coefficients and sigma fixed; a free common level is re-estimated on each period",
            clock_ratio="untruncated working lognormal location-scale ratio, not empirical mean gap or conditional remaining-wait ratio",claim_ids=["C21","C23"])
    for name,data in zip(ORIGINAL_DATA_NAMES,(f1,f2,f3,f4)):
        dump(DATA/name,data)
    dump(DATA/"fig1-timelines.json",TIMELINES)
    with (DATA/"fig1-lightcurve-nights.csv").open("w",newline="") as handle:
        handle.write(csv_text(nights))
    write_aggregate_data()
    tables=aggregate_tables()
    context_figure(plt,nights);forecast_figure(plt,f1,f2);robustness_figure(plt,tables["fig3-forest.csv"])
    transfer_figure(plt,tables["fig4-transfer.csv"])
    figure_three(plt,f3);figure_four(plt,f4);save(graphical_abstract(plt,nights,f2),"graphical-abstract",dpi=300);plt.close("all");g3a_figure(plt,g3a_rows()[0])
    manifest = manifest_for(np, scipy, matplotlib, font_manager, private_inputs)
    dump(FIGURES/"manifest.json",manifest)
    check()
    print(json.dumps(dict(status="generated",figures=len(BASENAMES),asset_bytes=sum(x["bytes"] for x in manifest["assets"].values()),
                          public_data_bytes=sum(x["bytes"] for x in manifest["figure_data"].values()))))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--generate",action="store_true")
    modes.add_argument("--check",action="store_true")
    args=parser.parse_args()
    generate() if args.generate else check()


if __name__ == "__main__":
    main()
