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
BASENAMES = ("fig1-light-curve", "fig2-forecast-gain", "fig3-calibration",
             "fig4-type-exploration", "brief-forecast-gain")
DATA_NAMES = ("fig1-illustration.json", "fig2-gains.json", "fig3-coverage.json", "fig4-refits.json", "claim-values.csv")
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
    return rows


def write_claim_values(primary,summary,review):
    stream=io.StringIO(newline="")
    writer=csv.DictWriter(stream,fieldnames=("claim_id","field","value"),lineterminator="\n")
    writer.writeheader();writer.writerows(claim_values(primary,summary,review))
    (DATA/"claim-values.csv").write_text(stream.getvalue())


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
    for group in ("assets", "figure_data", "public_inputs"):
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
    print(json.dumps(dict(status="figure check passed", figures=len(BASENAMES),
                          assets=len(expected_assets), private_inputs_required=False)))


def illustration(np, log_ndtr, private_inputs):
    receipt_path, ledger_path, evidence_path = (RUN/name for name in ("receipt.json", "ledger-0.0.json", "evidence-0.0.json"))
    receipt = load(receipt_path)
    if receipt["status"] != "completed" or receipt["mode"] != "live":
        raise ValueError("illustration requires the completed authorized run")
    for path in (ledger_path, evidence_path):
        if sha(path) != receipt["files_sha256"][path.name]:
            raise ValueError("retained illustration evidence drift")
    if sha(NATIVE_CODE) != receipt["source"]["sha256"][relative(NATIVE_CODE)]:
        raise ValueError("native display adapter differs from the executed version")
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
    dump(SCRATCH/"fig1_display_points.json",dict(scope="private display aggregates; not an exported observation table",points=points))
    return public, points


def save(figure, stem):
    figure.savefig(FIGURES/(stem+".png"),dpi=170,bbox_inches="tight",pad_inches=.10,
                   metadata={"Software":"dwarf-nova-memory figures"},pil_kwargs={"compress_level":9})
    figure.savefig(FIGURES/(stem+".pdf"),bbox_inches="tight",pad_inches=.10,
                   metadata={"Creator":"dwarf-nova-memory figures","Producer":"Matplotlib",
                             "CreationDate":None,"ModDate":None})


def figure_one(plt, data, points):
    fig,(ax,cdf)=plt.subplots(2,1,figsize=(7.2,6.1),gridspec_kw={"height_ratios":[1.2,1]},layout="constrained")
    item=data["illustration"]
    for available,color,label in ((True,BLUE,"At/before issue time"),(False,GREY,"Later observation times")):
        detections=[p for p in points if p["by_issue"] == available and not p["limit"]]
        ax.scatter([p["day_from_issue"] for p in detections],[p["magnitude"] for p in detections],s=17,
                   color=color,alpha=.82,label=label,zorder=3,linewidths=0)
        limits=[p for p in points if p["by_issue"] == available and p["limit"]]
        for p in limits:
            ax.annotate("",xy=(p["day_from_issue"],p["magnitude"]+.35),xytext=(p["day_from_issue"],p["magnitude"]),
                        arrowprops=dict(arrowstyle="-|>",color=color,lw=.9),zorder=4)
        if limits:
            ax.scatter([],[],marker="$\\downarrow$",color=color,label="Fainter-than bounds" if available else "Later fainter-than bounds")
    ax.axhline(10,color=BLACK,ls=":",lw=1,label="Extraction threshold")
    ax.axvspan(*item["onset_bracket_days"],color=BLUE,alpha=.13,zorder=0)
    ax.axvspan(*item["prefix_end_bracket_days"],color=ORANGE,alpha=.16,zorder=0)
    ax.axvline(0,color=BLACK,ls="--",lw=1)
    ax.set_ylabel("Visual magnitude (fainter downward)")
    magnitudes=[p["magnitude"] for p in points]
    ax.set_ylim(max(magnitudes)+.6,min(magnitudes)-.7)
    ax.set_xlim(*item["relative_window_days"])
    top=min(magnitudes)-.53
    ax.text(sum(item["onset_bracket_days"])/2,top,"Onset\nbracket",ha="center",va="top",fontsize=8.5,color=BLUE)
    ax.text(sum(item["prefix_end_bracket_days"])/2,top,"Prefix end\nbracket",ha="center",va="top",fontsize=8.5,color=ORANGE)
    ax.text(.8,top,"Issue",ha="left",va="top",fontsize=8.5)
    ax.legend(loc="lower right",fontsize=8.2,frameon=True,framealpha=.95)
    ax.set_title("A  Observer-day medians in the fixed illustrative window",loc="left",fontsize=10.5)
    for model,color in (("M2",BLUE),("M3",ORANGE)):
        cdf.plot(data["conditional_remaining_wait_cdf"]["days_from_issue"],data["conditional_remaining_wait_cdf"]["models"][model],
                 color=color,lw=2,label="Frozen timing (M2)" if model=="M2" else "Frozen timing + duration (M3)")
    cdf.axvspan(item["relative_window_days"][0],0,color="#E7E9EB",alpha=.55)
    cdf.axvspan(*item["later_onset_bracket_days"],color="#7B5A80",alpha=.23)
    cdf.axvline(0,color=BLACK,ls="--",lw=1)
    cdf.axhline(.5,color="#BEC3C7",lw=.7)
    cdf.text(sum(item["later_onset_bracket_days"])/2,.06,"Later onset bracket\n(scoring outcome)",ha="center",va="bottom",fontsize=8.5,color="#634368")
    cdf.set(xlim=item["relative_window_days"],ylim=(0,1.02),ylabel="Probability of next onset\nwithin the stated wait",xlabel=f"Days from forecast issue (native JD {item['issue_jd']:.1f})")
    cdf.set_title("B  Saved frozen forecasts, conditioned once on survival to issue",loc="left",fontsize=10.5)
    cdf.legend(loc="lower right",fontsize=8.4)
    fig.suptitle("One date-selected 1960 illustration; not a validation test",fontsize=12,fontweight="bold")
    save(fig,"fig1-light-curve");plt.close(fig)


def figure_two(plt, data):
    fig,(blocks,pooled)=plt.subplots(2,1,figsize=(7.2,7.0),gridspec_kw={"height_ratios":[1.5,1]},layout="constrained")
    b=data["blocks"]
    for k,row in enumerate(b):
        blocks.plot(row["mean_gain"],k,"o",color=GREY,ms=5)
        blocks.text(.051,k,f"n={row['n']}",fontsize=8.5,va="center")
    blocks.axvline(data["comparisons"][0]["estimate"],color=BLUE,lw=1,ls="--")
    blocks.axvline(0,color=BLACK,lw=.9)
    blocks.set_yticks(range(len(b)),[row["nominal_year_label"] for row in b])
    blocks.invert_yaxis();blocks.set_xlim(-.025,.061)
    blocks.set_title("A  Descriptive block means; no within-block intervals",loc="left",fontsize=10.5)
    blocks.set_xlabel("M3 − M2 log-score gain (nats per issuance)")
    for k,row in enumerate(data["comparisons"]):
        color=BLUE if row["kind"]=="sole primary" else (ORANGE if row["name"]=="Type/within-type rule" else GREY)
        pooled.plot([row["lower"],row["upper"]],[k,k],color=color,lw=2.4)
        pooled.plot(row["estimate"],k,"D" if k==0 else "o",color=color,ms=6 if k==0 else 5)
    pooled.set_yticks(range(4),[f"{r['name']}  (n={r['n']})" for r in data["comparisons"]])
    pooled.invert_yaxis();pooled.axvline(0,color=BLACK,lw=.9);pooled.set_xlim(-.025,.061)
    pooled.set_title("B  Sole primary and predeclared secondary comparisons",loc="left",fontsize=10.5)
    pooled.set_xlabel("Mean gain and 90% cluster interval (nats per issuance)")
    fig.suptitle("Frozen SS Cyg forecast comparison",fontsize=12,fontweight="bold")
    fig.supxlabel("Clusters span 2191.5 days; year labels are nominal. Dashed line above: pooled mean.",fontsize=8.2)
    save(fig,"fig2-forecast-gain");plt.close(fig)


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


def brief_figure(plt, data):
    rows=[data["comparisons"][k] for k in (0,2,3)]
    labels=("Primary: 1960–2017","Later segment: 1993–2017","Type/within-type rule")
    fig,ax=plt.subplots(figsize=(7.2,3.1),layout="constrained")
    for k,(row,color) in enumerate(zip(rows,(BLUE,GREY,ORANGE))):
        ax.plot([row["lower"],row["upper"]],[k,k],color=color,lw=3.5)
        ax.plot(row["estimate"],k,"D" if k==0 else "o",color=color,ms=8)
    ax.axvline(0,color=BLACK,lw=1)
    ax.set_yticks(range(3),labels,fontsize=12);ax.invert_yaxis();ax.set_xlim(-.014,.033)
    ax.tick_params(axis="x",labelsize=11)
    ax.set_xlabel("Forecast gain (nats per forecast); 90% intervals",fontsize=12)
    ax.set_title("SS Cyg: the frozen forecast comparison",fontsize=14,fontweight="bold",pad=12)
    fig.supxlabel("Only the primary row is confirmatory. Documented post-access format repair; models unchanged.",fontsize=9)
    save(fig,"brief-forecast-gain");plt.close(fig)


def generate():
    SCRATCH.mkdir(parents=True,exist_ok=True);FIGURES.mkdir(parents=True,exist_ok=True);DATA.mkdir(parents=True,exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR",str(SCRATCH/"matplotlib"))
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import font_manager
    from matplotlib import pyplot as plt
    import scipy
    from scipy.special import log_ndtr
    matplotlib.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.labelsize":10,
                                "xtick.labelsize":9,"ytick.labelsize":9,"axes.spines.top":False,
                                "axes.spines.right":False,"pdf.fonttype":42,"ps.fonttype":42,
                                "pdf.compression":9,"figure.facecolor":"white","axes.facecolor":"white"})
    primary,summary,review=load(PRIMARY),load(SUMMARY),load(REVIEW)
    if sha(PARAMETERS) != "ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3":
        raise ValueError("the frozen model parameters changed")
    private_inputs={}
    f1,points=illustration(np,log_ndtr,private_inputs)
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
                            ("Type/within-type rule","secondary",summary["secondary"]["robustness"]["type_within"]["gain_M3_M2"])):
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
    for name,data in zip(DATA_NAMES,(f1,f2,f3,f4)):
        dump(DATA/name,data)
    write_claim_values(primary,summary,review)
    figure_one(plt,f1,points);figure_two(plt,f2);figure_three(plt,f3);figure_four(plt,f4);brief_figure(plt,f2)
    public_inputs={relative(p):dict(sha256=sha(p)) for p in (PRIMARY,SUMMARY,REVIEW,PARAMETERS,NATIVE_CODE,ROOT/"uv.lock")}
    font=Path(font_manager.findfont("DejaVu Sans"))
    manifest=dict(schema_version=1,generator=relative(__file__),generator_sha256=sha(__file__),
                  scope="five static scientific illustrations; no raw photometry/identities/event catalog/issuance scores exported",
                  source_freeze_sha1="5e39aeb772c427ef29671c1a9c80b22c05519b58",source_execution_commit_sha1="d7151e0da48ce3d3f91e38d94b8bfdc656272dd0",
                  protocol_doi="10.5281/zenodo.24053338",post_result_status="first three figures show frozen/descriptive evidence; figure4 is exploratory in-sample; fig1 is one date-selected illustration",
                  public_inputs=public_inputs,private_inputs=private_inputs,
                  runtime=dict(python=sys.version.split()[0],numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__),
                  font=dict(family="DejaVu Sans",file=font.name,sha256=sha(font),pdf_embedding="TrueType; pdf.fonttype42"),
                  output_policy=dict(raw_photometry_table=False,observer_identifiers=False,new_event_catalog=False,per_issuance_scores=False,
                                     fig1_public_data="one illustrative derived bracket set and model CDF grid; display points stay under ignored outputs"),
                  figure_data={relative(DATA/name):dict(sha256=sha(DATA/name),bytes=(DATA/name).stat().st_size) for name in DATA_NAMES},assets=asset_records())
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
