"""Offline G3a integrity, gain-free qualification and six-star trial recount."""

import argparse
from collections import Counter, defaultdict
import csv
from datetime import date
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.parse import parse_qs, urlsplit
import xml.etree.ElementTree as ET

import numpy as np
from scipy.optimize import brentq
from scipy.stats import binom, t as student_t

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.extract import visits
from dnmem.extract_x4 import causal_confirmations, x4_episodes
from dnmem.extract_x5 import decisive_visits, x5_episodes
from dnmem.r2b_features import decoupled_schedule, decisive_feature
from dnmem.r2b_scoring import outcome_evidence

STOP = 2447892.5
TARGETS = ("SS Aur", "RU Peg", "AR And", "X Leo", "TW Vir", "UU Aql", "CH UMa", "DX And", "U Gem", "IP Peg")
REQUIRED = {"obsID", "JD", "mag", "uncert", "fainterThan", "band", "by", "val"}
RECENT = date(1980, 1, 1).toordinal() + 1721424.5


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mc_interval(k, n):
    if n == 0:
        return None
    lo = brentq(lambda p: binom.sf(k - 1, n, p) - .025, 0., 1., xtol=1e-14) if k else 0.
    hi = brentq(lambda p: binom.cdf(k, n, p) - .025, 0., 1., xtol=1e-14) if k < n else 1.
    return [lo, hi]


class Audit:
    def __init__(self):
        self.failures, self.hashes, self.source_drift = [], {}, []
        self.checks = 0
        self.maximum_errors = Counter()

    def check(self, ok, label):
        self.checks += 1
        if not ok:
            self.failures.append(label)

    def equal(self, value, expected, label):
        if isinstance(value, (list, tuple)) and isinstance(expected, (list, tuple)):
            self.check(len(value) == len(expected), label + ":length")
            for left, right in zip(value, expected):
                self.equal(left, right, label)
        elif value is None or expected is None or isinstance(value, (bool, str)) or isinstance(expected, (bool, str)):
            self.check(value == expected, label)
        else:
            delta = abs(float(value) - float(expected))
            self.maximum_errors["numeric"] = max(self.maximum_errors["numeric"], delta)
            self.check(math.isfinite(delta) and delta <= 1e-9, label)

    def hash(self, path):
        hashed = digest(path)
        self.hashes[str(Path(path).relative_to(ROOT))] = hashed
        return hashed

    def load(self, path):
        self.hash(path)
        return json.loads(Path(path).read_text())

    def sources(self, receipt):
        for name, expected in receipt["source_sha256"].items():
            frozen = subprocess.check_output(["git", "show", receipt["freeze_commit"] + ":" + name], cwd=ROOT)
            self.check(hashlib.sha256(frozen).hexdigest() == expected, "frozen source:" + name)
            current = self.hash(ROOT / name)
            if current != expected:
                self.source_drift.append(dict(path=name, frozen_sha256=expected, current_sha256=current))
                if not name.startswith("tests/"):
                    raise ValueError("functional source changed since freeze: " + name)


def url_parts(url, name, auid):
    parsed = urlsplit(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    metadata = query.get("data") == ["0"]
    keys = {"view", "ident", "data", "fromjd", "tojd"}
    if not metadata:
        keys |= {"csv", "mtype", "page"}
    if ((parsed.scheme, parsed.netloc, parsed.path) != ("https", "vsx.aavso.org", "/index.php")
            or parsed.fragment or set(query) != keys
            or any(len(values) != 1 for values in query.values())):
        raise ValueError("native URL shape is outside the approved transport")
    start, end = float(query["fromjd"][0]), float(query["tojd"][0])
    page = 1 if metadata else int(query["page"][0])
    if (not all(math.isfinite(x) for x in (start, end)) or not 0 < start < end < STOP
            or not 1 <= page <= 100 or query["view"] != ["api.object"]
            or not metadata and (query["mtype"] != ["std"] or query["csv"] != [""])
            or query["data"] not in (["0"], ["50000"])
            or query["ident"] != [name if metadata else auid]):
        raise ValueError("native request exceeded target/date/transport bounds")
    return start, end, page, metadata


def native_page(path, name, auid, bounds, metadata):
    root = ET.fromstring(path.read_bytes())
    if root.findtext("Name") != name or root.findtext("AUID") != auid:
        raise ValueError("native Name/AUID differs from approved resolved target")
    node = root.find("Data")
    text = node.text.strip() if node is not None and node.text else ""
    if metadata:
        if text:
            raise ValueError("metadata returned observations; stop without interpreting them")
        return [], None, "identity"
    if text:
        reader = csv.DictReader(io.StringIO(text))
        if not REQUIRED <= set(reader.fieldnames or []) or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("native CSV header differs")
        rows = list(reader)
        # Check every date before counts, limits, brightness or visual filtering.
        for row in rows:
            jd = float(row["JD"])
            if not math.isfinite(jd) or not bounds[0] <= jd <= bounds[1] or jd >= STOP:
                raise ValueError("native row violates requested pre-1990 date boundary")
        identifiers = set()
        for row in rows:
            if None in row or any(value is None for value in row.values()) or not row["obsID"] or row["obsID"] in identifiers:
                raise ValueError("malformed or duplicate-ID native CSV row")
            identifiers.add(row["obsID"])
            if (not math.isfinite(float(row["mag"])) or row["fainterThan"] not in ("0", "1")
                    or not row["by"] or not row["band"]):
                raise ValueError("invalid native brightness/limit/observer row")
            if row["uncert"] not in ("None", "") and (not math.isfinite(float(row["uncert"])) or float(row["uncert"]) < 0):
                raise ValueError("invalid native uncertainty")
    else:
        rows = []
    count_text = root.findtext(".//Count")
    count = int(count_text) if count_text is not None else None
    if count is not None and count < 0:
        raise ValueError("negative native continuation marker")
    if not text:
        if count == 0:
            return rows, count, "explicit_zero"
        if bounds[2] > 1:
            return rows, count, "no_data_after_page"
        raise ValueError("first-page metadata cannot establish an empty window")
    if not rows and count not in (None, 0) or rows and count == 0:
        raise ValueError("native count/CSV contradiction")
    if len(rows) >= 50000 and count is None:
        return rows, count, "capped"
    return rows, count, "continuation_marker" if count is not None and rows else "explicit_zero" if count == 0 else "marker_absent"


def acquire_audit(audit, raw, config, result):
    name, directory = config["name"], raw / config["slug"]
    records = [audit.load(path) for path in sorted(directory.glob("*.json")) if path.name != "acquisition.json"]
    retained = [r for r in records if r["status"] == "retained"]
    identities = [r for r in retained if parse_qs(urlsplit(r["source_url"]).query).get("data") == ["0"]]
    if len(identities) != 1:
        raise ValueError("expected exactly one successful bounded identity resolution")
    identity_record = identities[0]
    identity_path = directory / identity_record["native_file"]
    auid = ET.fromstring(identity_path.read_bytes()).findtext("AUID")
    if name not in TARGETS or not re.fullmatch(r"\d{3}-[A-Z]{3}-\d{3}", auid or ""):
        raise ValueError("target/AUID is outside the frozen registry")
    windows = defaultdict(list)
    page_files = set()
    for record in records:
        bounds = url_parts(record["source_url"], name, auid)
        if record["status"] != "retained":
            audit.check(record["status"] == "transport_failed", name + ":known transport-attempt status")
            continue
        path = directory / record["native_file"]
        if path.resolve().parent != directory.resolve():
            raise ValueError("native receipt path escapes its target directory")
        hashed = audit.hash(path)
        audit.check(hashed == record["sha256"] and path.stat().st_size == record["bytes"], name + ":raw receipt bytes/hash")
        rows, count, terminal = native_page(path, name, auid, bounds, bounds[3])
        page_files.add(path.name)
        if not bounds[3]:
            windows[bounds[:2]].append(dict(page=bounds[2], rows=rows, terminal=terminal, file=path.name, count=count))
    audit.check(page_files == {p.name for p in directory.glob("*.xml")}, name + ":no unreceipted native files")
    if result["status"] != "completed":
        return None, dict(name=name, status=result["status"], native_pages=len(retained),
                          partial_pages_date_checked=True, complete_acquisition_not_asserted=True, auid=auid)
    acquisition = audit.load(directory / "acquisition.json")
    accepted, leaves, capped = [], [], 0
    receipts_by_file = {r["native_file"]:r for r in acquisition["requests"]}
    audit.check(set(receipts_by_file) == page_files, name + ":acquisition request inventory")
    for (start, end), pages in windows.items():
        pages.sort(key=lambda p:p["page"])
        audit.check([p["page"] for p in pages] == list(range(1,len(pages)+1)), name + ":pagination complete and unique")
        seen = set()
        for index, page in enumerate(pages):
            native_ids = {row["obsID"] for row in page["rows"]}
            audit.check(not page["rows"] or bool(native_ids - seen), name + ":pagination progress")
            seen.update(native_ids)
            if index < len(pages) - 1:
                audit.check(page["terminal"] == "continuation_marker", name + ":page follows a continuation marker")
            recorded = receipts_by_file[page["file"]]
            if page["terminal"] != "capped":
                audit.equal(recorded["validated_rows"],len(page["rows"]),name + ":page validated rows")
                audit.equal(recorded["termination"],page["terminal"],name + ":termination evidence")
                audit.equal(recorded["continue"],page["terminal"] == "continuation_marker",name + ":continuation evidence")
        if pages[-1]["terminal"] == "capped":
            capped += 1
        else:
            audit.check(pages[-1]["terminal"] != "continuation_marker",name + ":window reached native terminal")
            leaves.append((start,end))
            accepted.extend(row for page in pages for row in page["rows"])
    edges = [1.] + [date(y,1,1).toordinal()+1721424.5 for y in range(1900,1990,10)] + [math.nextafter(STOP,-math.inf)]
    for start,end in zip(edges,edges[1:]):
        own = sorted((a,b) for a,b in leaves if start <= a < b <= end)
        audit.check(bool(own) and own[0][0] == start and own[-1][1] == end
                    and all(a[1] == b[0] for a,b in zip(own,own[1:])),name + ":complete bounded date-window partition")
    unique, duplicate_count = {}, 0
    for row in accepted:
        key = row["obsID"]
        if key in unique:
            if row != unique[key]:
                raise ValueError("conflicting repeated source observation")
            duplicate_count += 1
        unique[key] = row
    selected = sorted((row for row in unique.values() if row["band"] == "Vis." and row["val"] == "V"),
                      key=lambda row:(float(row["JD"]),row["obsID"]))
    for expected in (acquisition,result["acquisition"]):
        audit.equal(expected["native_unique_rows"],len(unique),name + ":native unique rows")
        audit.equal(expected["validated_visual_rows"],len(selected),name + ":validated Vis/V rows")
        audit.equal(expected["duplicate_endpoint_rows"],duplicate_count,name + ":deduplicated endpoints")
        audit.equal(expected["auid"],auid,name + ":resolved AUID")
    return selected,dict(name=name,auid=auid,status="completed",native_pages=len(retained),
                         transport_failures=sum(r["status"] != "retained" for r in records),
                         native_unique_rows=len(unique),validated_visual_rows=len(selected),
                         duplicate_endpoint_rows=duplicate_count,capped_parent_windows=capped,terminal_windows=len(leaves))


def ordinary_counts(audit, rows, config, expected):
    name, threshold = config["name"], config["threshold"]
    visits_at_cutoff = [v for v in decisive_visits(rows,threshold,1.) if v["available_at"] <= STOP]
    support_ids = {identifier for visit in visits_at_cutoff for identifier in visit["ids"]}
    closed_rows = [row for row in rows if row["obsID"] in support_ids]
    episodes = x5_episodes(closed_rows,threshold,1.,episodes=x4_episodes(closed_rows,threshold))
    confirmed = [e for e in episodes if e["confirmed_event"]]
    counts = dict(confirmed_events=len(confirmed),x5_available_events=sum(e["onset_report_available"] for e in confirmed),
                  x5_eligible_events=sum(e["onset_report_eligible"] for e in confirmed))
    counts["x5_eligible_fraction"] = counts["x5_eligible_events"]/len(confirmed) if confirmed else None
    emissions = causal_confirmations(closed_rows,threshold)
    observed = decisive_visits(closed_rows,threshold,1.)
    schedule = decoupled_schedule(emissions,observed,STOP)
    schedule_by_id = {row["emission_index"]:row for row in schedule}
    emission_by_id = {row["emission_index"]:row for row in emissions}
    times = [float(row["JD"]) for row in closed_rows]
    features = [decisive_feature(closed_rows,times,emission_by_id[s["emission_index"]],s,
                                schedule_by_id,emission_by_id,threshold) for s in schedule if s["status"] == "scheduled"]
    evidence = outcome_evidence(closed_rows,features,stop=STOP,threshold=threshold)
    evidence_by_id = {e["emission_index"]:e for e in evidence}
    timed, marked, usable, zero, recent = [], [], [], 0, 0
    for feature in features:
        issue = feature["issue_time"]
        ev = evidence_by_id[feature["emission_index"]]
        gap = feature.get("previous_gap")
        timing = (feature.get("clock_anchor") is not None and gap is not None and math.isfinite(float(gap))
                  and float(gap)>0 and feature.get("previous_gap_covered") is True)
        mark = feature.get("mark")
        supported_mark = timing and mark is not None and math.isfinite(float(mark)) and float(mark)>0
        if ev["kind"] == "interval":
            supported_outcome = issue < ev["onset_lo"] < ev["onset_hi"] <= min(STOP,ev["computed_as_of"],ev["evidence_available_at"])
            audit.check(supported_outcome,name + ":positive finite onset support")
        elif ev["kind"] == "right_censored":
            supported_outcome = issue < ev["censor_at"] <= min(STOP,ev["computed_as_of"],ev["evidence_available_at"])
            zero += ev["censor_at"] == issue
        else:
            supported_outcome = False
            audit.check(ev["kind"] == "excluded",name + ":known gain-free evidence route")
        timed.append(timing);marked.append(supported_mark);usable.append(supported_mark and supported_outcome)
        recent += supported_mark and supported_outcome and RECENT <= issue < STOP
        audit.check(feature["available_at"] <= issue < STOP,name + ":prefix feature availability")
    counts.update(df_scheduled=len(features),df_timing_supported=sum(timed),df_feature_supported_marked=sum(marked),
                  df_outcome_supported_marked=sum(usable),df_zero_exposure_outcomes=zero,
                  supported_last_decade_count=recent,supported_last_decade_rate_per_year=recent/10.)
    for key,value in counts.items():
        audit.equal(value,expected[key],name + ":rebuilt "+key)
    audit.check(dict(Counter(row["status"] for row in schedule)) == expected["schedule_status_counts"],name + ":DF schedule routes")
    coverage = expected["coverage"]
    who = lambda row:(row.get("obsName") or "").strip().casefold() or row["by"]
    audit.equal(coverage["reports"],len(rows),name + ":raw visual coverage count")
    audit.equal(coverage["limits"],sum(row["fainterThan"]=="1" for row in rows),name + ":visual limits")
    audit.equal(coverage["observer_nights"],len({(who(row),math.floor(float(row["JD"]))) for row in rows}),name + ":observer-night coverage")
    return counts


def gate_arithmetic(audit, expected, name):
    fit, morphology = expected["base_only_convergence"],expected["morphology"]
    fit_pass = fit["all_starts_converged"] and fit["nondegenerate"]
    morphology_pass = morphology["runs_at_least_60_days"]==0 and morphology["runs_at_least_40_days"]<3
    audit.equal(fit["passed"],fit_pass,name+":saved unmarked-fit gate arithmetic")
    audit.equal(morphology["passed"],morphology_pass,name+":saved morphology gate arithmetic")
    ordinary = (expected["df_outcome_supported_marked"]>=40 and expected["x5_eligible_fraction"] is not None
                and expected["x5_eligible_fraction"]>=.7 and fit_pass and morphology_pass)
    audit.equal(expected["ordinary_passed"],ordinary,name+":ordinary conjunction")
    return ordinary


def eclipse_arithmetic(audit, expected, name):
    for mode,report in expected["eclipse_ordinary_reductions"].items():
        gate_arithmetic(audit,report,name+":"+mode)
    comparison, synthetic = expected["eclipse_reduction_comparison"],expected["eclipse_synthetic"]
    counts = comparison["supported_counts"]
    relative = abs(counts[0]-counts[1])/max(counts) if max(counts) else None
    audit.equal(relative,comparison["supported_relative_difference"],name+":reduction support agreement")
    gates = dict(ordinary_both=all(r["ordinary_passed"] for r in expected["eclipse_ordinary_reductions"].values()),
                 episode_matching=comparison["matching_fraction"] is not None and comparison["matching_fraction"]>=.9,
                 eligible_window_agreement=comparison["eligible_agreement_fraction"] is not None and comparison["eligible_agreement_fraction"]>=.9,
                 supported_count_agreement=relative is not None and relative<=.1,span_sample=comparison["matched_span_pairs"]>=20,
                 span_median=comparison["matched_span_abs_difference_median"] is not None and comparison["matched_span_abs_difference_median"]<=1.,
                 span_p90=comparison["matched_span_abs_difference_p90"] is not None and comparison["matched_span_abs_difference_p90"]<=2.)
    audit.check(gates==comparison["gates"],name+":eclipse comparison gates")
    audit.equal(all(gates.values()),comparison["passed"],name+":eclipse comparison conjunction")
    accurate = lambda r:(r["early_fraction"] is not None and r["early_fraction"]<.02
                         and r["span_error_median"] is not None and r["span_error_median"]<=1.
                         and r["span_error_p90"] is not None and r["span_error_p90"]<=2.)
    if synthetic["status"]=="inconclusive":
        audit.check(not synthetic["passed"] and synthetic["cases"]==0,name+":inconclusive does not qualify")
        if "baseline" in synthetic:
            audit.check(any(r["count"]<20 or not accurate(r) for r in synthetic["baseline"].values()),name+":inconclusive baseline inadequacy")
    else:
        failures=0
        for case in synthetic["results"]:
            passed=[]
            for result in case["reductions"].values():
                passed.append(result["relative_recovery"]>=.9 and accurate(result))
                audit.equal(result["passed"],passed[-1],name+":synthetic reduction conjunction")
            audit.equal(case["passed"],all(passed),name+":synthetic case conjunction")
            failures+=not all(passed)
        audit.equal(len(synthetic["results"]),synthetic["cases"],name+":synthetic case count")
        audit.equal(failures,synthetic["failed_cases"],name+":synthetic failed cases")
        audit.equal(synthetic["passed"],failures==0,name+":synthetic overall conjunction")
    passed=comparison["passed"] and synthetic["passed"]
    audit.equal(expected["qualified"],passed,name+":hold qualification conjunction")
    audit.equal(expected["eclipse_passed"],passed,name+":hold eclipse conjunction")
    return dict(scope="aggregate gate arithmetic only; no independent reductions/episode matching/eclipse regeneration or fits",
                comparison_passed=comparison["passed"],synthetic_status=synthetic["status"],qualified=passed)


def supplement_audit(audit, run):
    receipt,summary = audit.load(run/"receipt.json"),audit.load(run/"summary.json")
    audit.sources(receipt)
    audit.equal(audit.hash(run/"summary.json"),receipt["summary_sha256"],"six-star summary hash")
    design=audit.load(ROOT/"data/provenance/g3a_preparation/six-star-design.json")
    configured={c["id"]:c for c in design["cases"]}
    published={c["case"]:c for c in summary["cases"]}
    audit.check(set(configured)==set(published) and len(configured)==8,"eight supplemental cases")
    all_seeds,total,failed,results=set(),0,0,[]
    critical={g:float(student_t.ppf(.95,g-1)) for g in (6,12)}
    for name,config in configured.items():
        saved=published[name];path=run/(name+"-trials.jsonl")
        audit.equal(audit.hash(path),saved["trials_sha256"],name+":trial bytes")
        counters,sums,seen=Counter(),Counter(),set()
        with path.open() as stream:
            for line in stream:
                row=json.loads(line);rep=row["replicate"]
                seed=int.from_bytes(hashlib.sha256(f"{design['namespace']}|{name}|{rep}".encode()).digest()[:8],"big")
                audit.check(row["case"]==name and rep not in seen and row["seed"]==seed and seed not in all_seeds,name+":trial/seed identity")
                seen.add(rep);all_seeds.add(seed);total+=1
                if row["status"]!="passed":failed+=1;continue
                counters["completed"]+=1;counters["identity_count"]+=row["gain_identity"]
                counters["positive_score_negative_gain_count"]+=row["conditional_expected_score"]>0 and row["conditional_expected_gain"]<0
                for field,key in (("mean_beta","beta_hat"),("mean_predictable_gain","conditional_expected_gain"),
                                  ("mean_predictable_score","conditional_expected_score"),("mean_supported_marks","markable_evaluation"),
                                  ("mean_nominal_individual_oracle_gain","nominal_direct_oracle_gain")):
                    sums[field]+=row[key]
                for cl in ("star","halves"):
                    flags={}
                    for stat in ("gain","score"):
                        method=row["methods"][cl][stat];key=cl+"-"+stat;g=6 if cl=="star" else 12
                        flags[stat]=method["estimate"]>critical[g]*method["se"]
                        audit.equal(flags[stat],method["reject_one_sided"],name+":numeric rejection flag")
                        audit.equal(method["df"],g-1,name+":CR1 degrees")
                        audit.equal(method["lower90"],method["estimate"]-critical[g]*method["se"],name+":lower90")
                        audit.equal(method["upper90"],method["estimate"]+critical[g]*method["se"],name+":upper90")
                        counters[key+":rejections"]+=flags[stat];sums[key+":estimate"]+=method["estimate"]
                        counters[key+":reject_with_negative_predictable_gain"]+=flags[stat] and row["conditional_expected_gain"]<0
                        if stat=="gain":
                            covered=method["lower90"]<=row["conditional_expected_gain"]<=method["upper90"]
                            audit.equal(covered,method["covers_conditional_expected_gain"],name+":gain coverage flag")
                            counters[key+":covered"]+=covered
                            if not row["gain_identity"]:
                                counters[key+":nonidentity_count"]+=1;counters[key+":nonidentity_covered"]+=covered
                    for key,value in dict(both=flags["score"] and flags["gain"],gain_without_score=flags["gain"] and not flags["score"],
                                          score_without_gain=flags["score"] and not flags["gain"],neither=not flags["score"] and not flags["gain"]).items():
                        counters[cl+":"+key]+=value
                flip=row["score_sign_flip"]
                audit.check(flip["minimum_p"]==1/64 and 1/64<=flip["p"]<=1 and abs(flip["p"]*64-round(flip["p"]*64))<1e-10,name+":sign-flip support")
                audit.equal(flip["reject_one_sided"],flip["p"]<=.05,name+":sign-flip rejection")
                counters["star-score-sign-flip:rejections"]+=flip["p"]<=.05
        n=counters["completed"]
        audit.check(n==2000 and seen==set(range(2000)),name+":complete successful trial set")
        for field in ("identity_count","positive_score_negative_gain_count"):
            audit.equal(counters[field],saved[field],name+":"+field)
        for field in ("mean_beta","mean_predictable_gain","mean_predictable_score","mean_supported_marks","mean_nominal_individual_oracle_gain"):
            audit.equal(sums[field]/n,saved[field],name+":"+field)
        for key,method in saved["methods"].items():
            k=counters[key+":rejections"]
            audit.equal(k,method["rejections"],name+":"+key+":recount")
            audit.equal(k/n,method["rate"],name+":"+key+":rate")
            audit.equal(mc_interval(k,n),method["exact_mc95"],name+":"+key+":binomial interval")
            if key!="star-score-sign-flip":
                audit.equal(sums[key+":estimate"]/n,method["mean_estimate"],name+":"+key+":mean estimate")
                audit.equal(counters[key+":reject_with_negative_predictable_gain"],method["reject_with_negative_predictable_gain"],name+":"+key+":negative-target rejection")
            if key.endswith("gain"):
                for field in ("covered","nonidentity_count","nonidentity_covered"):
                    audit.equal(counters[key+":"+field],method[field],name+":"+key+":"+field)
                covered,ni,nic=(counters[key+":"+k] for k in ("covered","nonidentity_count","nonidentity_covered"))
                audit.equal(covered/n,method["coverage"],name+":"+key+":coverage")
                audit.equal(mc_interval(covered,n),method["coverage_mc95"],name+":"+key+":coverage MC")
                audit.equal(nic/ni if ni else None,method["nonidentity_coverage"],name+":"+key+":nonidentity coverage")
                audit.equal(mc_interval(nic,ni),method["nonidentity_coverage_mc95"],name+":"+key+":nonidentity MC")
        sequence={cl:{key:counters[cl+":"+key] for key in ("both","gain_without_score","score_without_gain","neither")} for cl in ("star","halves")}
        audit.check(sequence==saved["sequence_counts"],name+":joint sequence counts")
        results.append(dict(case=name,completed=n,sequence=sequence,
                            whole_star_score_rejections=counters["star-score:rejections"],whole_star_gain_rejections=counters["star-gain:rejections"]))
    audit.check(total==len(all_seeds)==receipt["attempted"]==16000 and failed==receipt["failures"]==0,"six-star16000 unique successful trials")
    return dict(attempted=total,unique_seeds=len(all_seeds),failures=failed,cases=results,
                scope="all saved aggregate identities and intervals; raw trial vectors/CR1 SEs/DGP not independently rebuilt")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw",type=Path,default=ROOT/"data/raw/g3a_20261110_d827313")
    parser.add_argument("--run",type=Path,default=ROOT/"outputs/g3a_20261110_d827313")
    parser.add_argument("--supplement",type=Path,default=ROOT/"outputs/g3a_sixstar_d827313")
    parser.add_argument("--output",type=Path,default=ROOT/"outputs/g3a_execution_audit")
    parser.add_argument("--wait-seconds",type=float,default=7200.)
    args=parser.parse_args();deadline=time.monotonic()+args.wait_seconds
    while True:
        path=args.run/"receipt.json"
        state=json.loads(path.read_text()) if path.exists() else {}
        if state.get("status") not in (None,"running") and (args.supplement/"receipt.json").exists():break
        if time.monotonic()>=deadline:raise TimeoutError("waiting for final G3a/supplement receipt; no archive rows inspected")
        time.sleep(5.)
    if state["status"]!="completed":raise ValueError("G3a access guard/aborted state; no raw-page audit attempted")
    args.output.mkdir(parents=True,exist_ok=False)
    audit=Audit();receipt=audit.load(args.run/"receipt.json");audit.sources(receipt)
    for name,expected in receipt["output_sha256"].items():audit.equal(audit.hash(args.run/name),expected,"execution output hash:"+name)
    summary=audit.load(args.run/"summary.json");config=audit.load(ROOT/"configs/g3a_feasibility.json")
    cohort=audit.load(args.run/"qualified-set.json")
    audit.check(tuple(s["name"] for s in config["stars"])==TARGETS and config["stop_jd_exclusive"]==STOP,"exact authorized names/date registry")
    by_name={r["name"]:r for r in summary["stars"]}
    audit.check(set(by_name)==set(TARGETS) and len(summary["stars"])==10,"ten final target dispositions")
    stars,auids=[],set()
    for star in config["stars"]:
        expected=by_name[star["name"]]
        rows,native=acquire_audit(audit,args.raw,star,expected)
        audit.check(native["auid"] not in auids,star["name"]+":distinct resolved target AUID")
        auids.add(native["auid"])
        report=dict(acquisition=native)
        if expected["status"]=="completed":
            if star["eclipsing_hold"]:
                report["eclipse"]=eclipse_arithmetic(audit,expected,star["name"])
            else:
                report["independently_rebuilt"]=ordinary_counts(audit,rows,star,expected)
                ordinary=gate_arithmetic(audit,expected,star["name"])
                audit.equal(ordinary,expected["qualified"],star["name"]+":ordinary qualification")
            audit.equal(expected["no_mark_fit_or_association_computed"],True,star["name"]+":gain-free declaration")
        stars.append(report)
    names=[r["name"] for r in summary["stars"] if r.get("qualified")]
    audit.check(cohort["names"]==names and cohort["no_mark_fit_performed"] is True,"frozen qualifying set")
    supplement=supplement_audit(audit,args.supplement)
    for name,expected in audit.hashes.items():audit.equal(digest(ROOT/name),expected,"input remained immutable:"+name)
    report=dict(status="failed" if audit.failures else "passed",scope="one offline integrity/qualification audit, no requests, effect fits, duration-gap relations or gains on observations",
                freeze_commit=receipt["freeze_commit"],checks=audit.checks,failures=audit.failures,stars=stars,
                qualified_names=names,supplement=supplement,maximum_numeric_errors=dict(audit.maximum_errors),
                current_source_drift=audit.source_drift,input_sha256=audit.hashes,checker_sha256=digest(__file__),
                limits=["Shared frozen legacy X4/X5/DF/outcome builders are reused; native parser, de-duplication and support mask are independently written. This is not independent extraction validation.",
                        "Ordinary morphology and B0 fit gates are checked from saved aggregate arithmetic; optimizer fits, all starts, ranks and morphology episode runs are not independently replayed.",
                        "Eclipse branches check saved aggregate gate arithmetic only; night reductions, episode matching and synthetic eclipse recovery are not regenerated.",
                        "Native terminal/Count conventions follow the frozen transport contract, not independent proof that the archive omitted no observations.",
                        "Historical report upload/revision availability remains unknown; reconstructed observation-time features are not operational replay.",
                        "Six-star MC intervals are per cell; their precision and size do not validate X5 scoring, real calendars or actual cohort power."])
    (args.output/"summary.json").write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    compact={k:report[k] for k in ("status","freeze_commit","checks","failures","stars","qualified_names","supplement","maximum_numeric_errors","current_source_drift","limits")}
    (args.output/"report.md").write_text("# Independent G3a execution audit\n\n"+json.dumps(compact,indent=2)+"\n")
    out_receipt=dict(status=report["status"],checker_sha256=digest(__file__),freeze_commit=receipt["freeze_commit"],
                     summary_sha256=digest(args.output/"summary.json"),report_sha256=digest(args.output/"report.md"),
                     input_sha256=audit.hashes,no_network_requests=True,no_new_simulation_trials=True,no_observed_gain_or_association=True)
    (args.output/"receipt.json").write_text(json.dumps(out_receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps(dict(status=report["status"],checks=audit.checks,failures=audit.failures,stars=len(stars),qualified_names=names,
                          supplemental_trials=supplement["attempted"])))
    raise SystemExit(bool(audit.failures))


if __name__=="__main__":main()
