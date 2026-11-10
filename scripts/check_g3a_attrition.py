"""C70 only: independent gain-free masks and projections on opened pre-1990 inputs."""

import argparse
from collections import Counter, defaultdict
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.extract_x4 import causal_confirmations, x4_episodes
from dnmem.extract_x5 import decisive_visits, x5_episodes
from dnmem.g3a_eclipse import reduce_observer_nights, two_night_confirmations
from dnmem.r2b_features import decoupled_schedule, decisive_feature
from dnmem.r2b_scoring import outcome_evidence
from check_g3a_execution import Audit, acquire_audit

STOP = 2447892.5
START80 = date(1980, 1, 1).toordinal() + 1721424.5
SOURCES = ["src/dnmem/extract.py", "src/dnmem/extract_x3.py", "src/dnmem/extract_x4.py",
           "src/dnmem/extract_x5.py", "src/dnmem/r2_features.py", "src/dnmem/r2b_features.py",
           "src/dnmem/r2b_scoring.py", "src/dnmem/g3a_eclipse.py", "scripts/check_g3a_execution.py"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def quantiles(values):
    ordered = sorted(float(value) for value in values)
    if not ordered:
        return None
    result = []
    for p in (.1,.5,.9):
        index = p * (len(ordered)-1)
        left = math.floor(index)
        fraction = index-left
        result.append(ordered[left]*(1-fraction)+ordered[min(left+1,len(ordered)-1)]*fraction)
    return result


def decade(t):
    year = date.fromordinal(math.floor(t-1721424.5)).year
    return str((year//10)*10) if year>=1940 else "pre1940"


def count_bits(table, required):
    return sum(n for bits,n in table.items() if bits & required == required)


def summarize(rows, threshold, *, emissions=None, delay_landmarks=True):
    if any(not math.isfinite(float(row["JD"])) or float(row["JD"])>=STOP for row in rows):
        raise ValueError("pre-1990 input boundary violated before summaries")
    source_by_id={row["obsID"]:row for row in rows}
    observed=decisive_visits(rows,threshold,1.)
    identifiers={i for visit in observed if visit["available_at"]<=STOP for i in visit["ids"]}
    closed=[row for row in rows if row["obsID"] in identifiers]
    observed=decisive_visits(closed,threshold,1.)
    episodes=x5_episodes(closed,threshold,1.,episodes=x4_episodes(closed,threshold))
    confirmed=[event for event in episodes if event["confirmed_event"]]
    original=causal_confirmations(closed,threshold) if emissions is None else emissions
    schedule=decoupled_schedule(original,observed,STOP)
    schedules={s["emission_index"]:s for s in schedule}
    by_id={e["emission_index"]:e for e in original}
    times=[float(row["JD"]) for row in closed]
    features=[decisive_feature(closed,times,by_id[s["emission_index"]],s,schedules,by_id,threshold)
              for s in schedule if s["status"]=="scheduled"]
    outcomes={e["emission_index"]:e for e in outcome_evidence(closed,features,stop=STOP,threshold=threshold)}
    lattice, era_tables=Counter(),defaultdict(Counter)
    reasons=Counter();nonpositive_ids=set();status=Counter()
    gap_values,span_values,widths=[],[],[]
    delays,delays80,raw_delays,first_support_delays,closure_offsets=[],[],[],[],[]
    faint_visit_spans=[];missing_bright_support=0;peak80_supported=0;peak_before80_issue80=0
    bright_by_close=defaultdict(list)
    if delay_landmarks:
        for visit in observed:
            if visit["cls"]=="B":
                bright_by_close[visit["available_at"]].extend(float(source_by_id[i]["JD"]) for i in visit["ids"]
                     if source_by_id[i]["fainterThan"]=="0" and float(source_by_id[i]["mag"])<=threshold)
    for feature in features:
        issue=feature["issue_time"];ev=outcomes[feature["emission_index"]]
        anchor,gap,mark=feature.get("clock_anchor"),feature.get("previous_gap"),feature.get("mark")
        clock=anchor is not None and math.isfinite(float(anchor)) and float(anchor)<=issue
        previous=(gap is not None and math.isfinite(float(gap)) and float(gap)>0 and feature.get("previous_gap_covered") is True)
        marked=mark is not None and math.isfinite(float(mark)) and float(mark)>0
        if ev["kind"]=="interval":
            usable=(issue<ev["onset_lo"]<ev["onset_hi"]<=STOP)
            widths.append(ev["onset_hi"]-ev["onset_lo"])
        elif ev["kind"]=="right_censored":
            usable=issue<ev["censor_at"]<=STOP
        else:
            usable=False
        if not feature["available_at"]<=issue<STOP or any(h["available_at"]>issue for h in feature["gap_history"]):
            raise ValueError("unavailable frozen feature")
        bits=int(clock)+2*int(previous)+4*int(marked)+8*int(usable)
        lattice[bits]+=1;era_tables[decade(issue)][bits]+=1
        status[feature["status"]]+=1
        if clock:
            history=feature.get("gap_history") or []
            reason=history[-1]["reason"] if history else "empty_history"
            reasons[reason]+=1
            if reason=="nonpositive_adjacent_gap":nonpositive_ids.add(history[-1]["gap_id"])
            schedule_row=schedules[feature["emission_index"]]
            close=schedule_row["original_last_bright_at"]
            delay=schedule_row["anchor"]-close
            delays.append(delay)
            if START80<=issue<STOP:delays80.append(delay)
            if delay_landmarks:
                support=bright_by_close.get(close,[])
                if support:
                    latest_raw_bright=max(support)
                    closure_offsets.append(close-latest_raw_bright)
                    raw_delays.append(schedule_row["anchor"]-latest_raw_bright)
                    first_support_delays.append(schedule_row["anchor_first_at"]-latest_raw_bright)
                    faint_visit_spans.append(schedule_row["anchor"]-schedule_row["anchor_first_at"])
                else:missing_bright_support+=1
        if bits==15:
            gap_values.append(float(gap));span_values.append(float(mark))
            peak=feature.get("current_raw_peak_at")
            peak80_supported+=peak is not None and START80<=peak<STOP
            peak_before80_issue80+=START80<=issue<STOP and peak is not None and peak<START80
    sequential=dict(scheduled=sum(lattice.values()),clock=count_bits(lattice,1),clock_prevcovered=count_bits(lattice,3),
                    clock_prevcovered_mark=count_bits(lattice,7),supported=count_bits(lattice,15))
    eras={d:dict(scheduled=sum(table.values()),supported=count_bits(table,15),clock_and_outcome=count_bits(table,9))
          for d,table in era_tables.items()}
    return dict(confirmed=len(confirmed),confirmed_by_decade=dict(Counter(decade(e["peak_t"]) for e in confirmed)),
                sequential=sequential,by_decade=eras,previous_gap_state_given_clock=dict(reasons),
                clock_outcome_all=count_bits(lattice,9),clock_covered_outcome=count_bits(lattice,11),
                clock_mark_outcome=count_bits(lattice,13),lattice={str(k):v for k,v in sorted(lattice.items())},
                mark_losses_before_outcome=count_bits(lattice,3)-count_bits(lattice,7),
                mark_losses_among_usable_outcomes=count_bits(lattice,11)-count_bits(lattice,15),
                supported_mark_quantiles=quantiles(span_values),supported_previous_gap_quantiles=quantiles(gap_values),
                onset_window_width_quantiles=quantiles(widths),fade_confirmation_delay_quantiles=quantiles(delays),
                fade_delay_issue_1980s_quantiles=quantiles(delays80),delay_clock_population=len(delays),
                raw_bright_support_to_faint_anchor_quantiles=quantiles(raw_delays),
                raw_bright_support_to_faint_first_support_quantiles=quantiles(first_support_delays),
                last_bright_closure_minus_latest_raw_bright_quantiles=quantiles(closure_offsets),
                faint_visit_last_minus_first_quantiles=quantiles(faint_visit_spans),
                unmatched_last_bright_visit_support=missing_bright_support,
                nonpositive_latest_gap_features=reasons["nonpositive_adjacent_gap"],nonpositive_unique_latest_gap_ids=len(nonpositive_ids),
                landmark_counts=dict(supported_current_raw_peak_in_1980s=peak80_supported,
                                     supported_issue_in_1980s_with_peak_before_1980=peak_before80_issue80))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=ROOT/"outputs/g3a_attrition_audit")
    parser.add_argument("--evidence",type=Path,default=ROOT/"data/provenance/g3a_review_independent/c70.json")
    parser.add_argument("--ss-cyg",type=Path,default=ROOT/"outputs/c70_safe_input/ss_cyg_pre1990.json")
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    audit=Audit()
    review=audit.load(ROOT/"data/provenance/g3a_claude_review/checks.json")
    details=audit.load(ROOT/"data/provenance/g3a_20261110/details.json")
    config=audit.load(ROOT/"configs/g3a_feasibility.json")
    execution_receipt=audit.load(ROOT/"data/provenance/g3a_20261110/receipt.json")
    audit.sources(execution_receipt)
    before={s["name"]:s for s in details["stars"]}
    stars,holds={},{}
    for target in config["stars"]:
        name=target["name"]
        rows,_=acquire_audit(audit,ROOT/"data/raw/g3a_20261110_d827313",target,before[name])
        derived=summarize(rows,target["threshold"])
        expected=review["stars"][name]
        for key in ("confirmed","confirmed_by_decade","sequential","by_decade","previous_gap_state_given_clock"):
            audit.check(derived[key]==expected[key],name+":independent "+key)
        for key in ("fade_confirmation_delay_quantiles","onset_window_width_quantiles","supported_previous_gap_quantiles","supported_mark_quantiles"):
            audit.equal(derived[key],expected[key],name+":independent "+key)
        audit.equal(derived["clock_outcome_all"],expected["single_gate_relaxations"]["clock_and_outcome_ceiling"],name+":relaxed count")
        stars[name]=derived
        if target["eclipsing_hold"]:
            holds[name]={}
            for mode in ("median","brightest"):
                reduced=reduce_observer_nights(rows,mode)
                alternate=summarize(reduced,target["threshold"],emissions=two_night_confirmations(reduced,target["threshold"]),delay_landmarks=False)
                saved=before[name]["eclipse_ordinary_reductions"][mode]
                audit.equal(alternate["sequential"]["supported"],saved["df_outcome_supported_marked"],name+":"+mode+":frozen support")
                audit.equal(alternate["by_decade"].get("1980",{}).get("supported",0),saved["supported_last_decade_count"],name+":"+mode+":frozen1980s support")
                audit.equal(alternate["confirmed"],saved["confirmed_events"],name+":"+mode+":confirmed events")
                holds[name][mode]={k:alternate[k] for k in ("confirmed","confirmed_by_decade","sequential","by_decade","clock_outcome_all","landmark_counts")}
    safe_receipt=audit.load(args.ss_cyg.parent/"receipt.json")
    audit.equal(audit.hash(args.ss_cyg),safe_receipt["output_sha256"],"safe SS Cyg-only input hash")
    cyg_rows=json.loads(args.ss_cyg.read_text())
    if any(not math.isfinite(float(r["JD"])) or float(r["JD"])>=STOP for r in cyg_rows):
        raise ValueError("safe SS Cyg input contains a later record; stop before summaries")
    cyg_rows=sorted((r for r in cyg_rows if r["band"]=="Vis." and r["val"]=="V"),key=lambda r:(float(r["JD"]),r["obsID"]))
    cyg=summarize(cyg_rows,10.)
    for key in ("confirmed","confirmed_by_decade","sequential","by_decade","previous_gap_state_given_clock"):
        audit.check(cyg[key]==review["ss_cyg_same_chain_reference"][key],"SS Cyg:independent "+key)
    for key in ("fade_confirmation_delay_quantiles","onset_window_width_quantiles","supported_previous_gap_quantiles"):
        audit.equal(cyg[key],review["ss_cyg_same_chain_reference"][key],"SS Cyg:independent "+key)
    total=Counter();reasons=Counter()
    for r in stars.values():
        total.update(r["sequential"]);reasons.update(r["previous_gap_state_given_clock"])
    missing={k:v for k,v in reasons.items() if k!="covered_adjacent_gap"}
    audit.check(total["clock"]==822 and total["clock_prevcovered"]==280 and sum(missing.values())==542,"C70 attrition822/280/542")
    frozen80=sum(s["supported_last_decade_count"] for s in before.values())
    raw80=sum(s["by_decade"].get("1980",{}).get("supported",0) for s in stars.values())
    relaxed80=sum(s["by_decade"].get("1980",{}).get("clock_and_outcome",0) for s in stars.values())
    confirmed80=sum(s["confirmed_by_decade"].get("1980",0) for s in stars.values())
    median80_confirmed=confirmed80-sum(stars[name]["confirmed_by_decade"].get("1980",0) for name in holds)
    median80_confirmed+=sum(h["median"]["confirmed_by_decade"].get("1980",0) for h in holds.values())
    rates=dict(frozen_mixed_route_issues=frozen80,ordinary_raw_route_issues=raw80,ordinary_relaxed_clock_outcome=relaxed80,
               ordinary_raw_confirmed_peaks=confirmed80,frozen_reductions_confirmed_peaks=median80_confirmed)
    projections={str(years):{key:value*years/10 for key,value in rates.items() if "issues" in key or "clock_outcome" in key}
                 for years in (28,36)}
    five=sorted(name for name,r in stars.items() if r["clock_outcome_all"]>=40)
    audit.check((frozen80,raw80,relaxed80,confirmed80)==(102,105,201,485),"C70 epoch count identities")
    audit.equal(201/485,review["ceilings"]["conversion_1980s"]["without_history_and_mark"],"C70 relaxed201/485 arithmetic")
    audit.equal(projections["28"]["ordinary_relaxed_clock_outcome"],562.8,"C70 relaxed28-year projection")
    audit.equal(projections["36"]["ordinary_relaxed_clock_outcome"],723.6,"C70 relaxed36-year projection")
    audit.check(five==review["ceilings"]["stars_at_least_40_without_history_and_mark"],"C70 five-star forty threshold")
    for name,hashed in list(audit.hashes.items()):audit.equal(digest(ROOT/name),hashed,"input stable:"+name)
    source_hashes={name:digest(ROOT/name) for name in SOURCES}
    report=dict(status="failed" if audit.failures else "passed",scope="C70 numeric reconciliation only, no requests/later inputs/marker fitting/relation or scoring",
                checks=audit.checks,failures=audit.failures,checker_sha256=digest(__file__),analysis_base="93c48cf",
                extraction_freeze=execution_receipt["freeze_commit"],source_sha256=source_hashes,
                evidence_input_sha256={"claude_review":digest(ROOT/"data/provenance/g3a_claude_review/checks.json"),
                                      "frozen_details":digest(ROOT/"data/provenance/g3a_20261110/details.json"),
                                      "safe_ss_cyg":digest(args.ss_cyg),"safe_ss_cyg_receipt":digest(args.ss_cyg.parent/"receipt.json")},
                ordinary_raw_streams=stars,hold_frozen_reductions=holds,ss_cyg_pre1990_reference=cyg,
                attrition=dict(clock_available=total["clock"],covered_previous_gap=total["clock_prevcovered"],
                               missing_previous_gap=sum(missing.values()),partition=missing,
                               marked_after_history=total["clock_prevcovered_mark"],raw_supported=total["supported"],
                               mark_losses_before_outcome=sum(r["mark_losses_before_outcome"] for r in stars.values()),
                               mark_losses_after_outcome=sum(r["mark_losses_among_usable_outcomes"] for r in stars.values())),
                epoch_1980s=rates,ratios=dict(ss_cyg_issue_to_peak=cyg["by_decade"]["1980"]["supported"]/cyg["confirmed_by_decade"]["1980"],
                     frozen_mixed_to_raw_peaks=frozen80/confirmed80,all_raw_to_raw_peaks=raw80/confirmed80,
                     frozen_route_to_frozen_route_peaks=frozen80/median80_confirmed,relaxed_raw_to_raw_peaks=relaxed80/confirmed80),
                constant_rate_projections=projections,raw_stars_at_least40_relaxed=five,
                required_conversion_at_frozen_raw_peak_rate={str(years):1100/(confirmed80*years/10) for years in (28,36)},
                interpretation_limits=["Headline102/485 mixes hold reductions; even same-stream ratios count forecasts by issue decade and events by peak decade, not a paired event-cohort conversion probability.",
                    "822/280/542 and the partition use all pre1990 ordinary/raw routes, including the holds, not frozen hold streams or the1980s alone.",
                    "Mark costs six at the covered-history stage and four after usable-outcome support; these denominators must be named.",
                    "Fade delay is first selected decisive-faint visit LAST raw support minus last threshold-bright visit CLOSURE, pooled over clock-available pre1990 features; not a physical-end timing error.",
                    "X Leo supported gap quantiles and onset-window widths use different selected populations; their marginal medians do not decompose any particular gap.",
                    "Projections fix the particular extraction, landmarks and1980s rates. They are not upper bounds on new models, missed-event inference, later coverage or a changed split.",
                    "The same-chain SS Cyg reference demonstrates target-dependent retained yield; it does not establish that thresholds/gates are not strict or that faintness caused the difference.",
                    "Shared frozen X4/X5/DF/outcome APIs, prior independently audited loader and hold reduction/emission APIs are reused. Masks, bit-lattice counts, projections and scalar quantiles are independent; no independent extractor, physical timing annotation or causal identification.",
                    "SS Cyg safe input was supplied as an already-open pre1990-only slice; this checker never opens the broader through2017 cache."])
    output=json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n"
    (args.output/"summary.json").write_text(output)
    args.evidence.parent.mkdir(parents=True,exist_ok=True)
    if args.evidence.exists():raise FileExistsError(args.evidence)
    args.evidence.write_text(output)
    receipt=dict(checker_sha256=digest(__file__),summary_sha256=digest(args.output/"summary.json"),
                 public_aggregate_sha256=digest(args.evidence),input_sha256=audit.hashes,
                 no_new_request=True,no_later_input=True,no_marker_fit_relation_or_score=True)
    (args.output/"receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps(dict(status=report["status"],checks=audit.checks,failures=audit.failures,
                          attrition=report["attrition"],epoch=report["epoch_1980s"],five=five)))
    raise SystemExit(bool(audit.failures))


if __name__=="__main__":main()
