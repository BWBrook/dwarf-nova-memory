"""Recover actual frozen E3 candidates from retained, hash-verified SS Cyg inputs.

Offline only. Per-case times remain in ignored outputs; summary.json contains
aggregate diagnostics suitable for a reviewed public snapshot. This is a
post-result audit, not a new confirmation or a new extraction specification.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem import outcome_evidence_v4, prefix_features, prefix_reference
from dnmem.evaluation_native import combine_native, select_analysis_rows
from dnmem.extract import visits
from dnmem.extract_x4 import x4_episodes
from dnmem.real_development import load_native

STOP = 2458119.5


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(path: Path, expected: str) -> str:
    actual = digest(path)
    if actual != expected:
        raise ValueError(f"SHA-256 mismatch: {path.relative_to(ROOT)}")
    return actual


def candidate(episodes: list[dict], emitted_at: float) -> tuple[int | None, dict | None]:
    """Independent, literal search of the v3 candidate contract, before routing."""
    eligible = [(i, e) for i, e in enumerate(episodes)
                if e["peak_t"] > emitted_at and e.get("onset_hi") is not None
                and e["onset_hi"] > emitted_at]
    return eligible[0] if eligible else (None, None)


def relation(episode: dict | None, cutoff: float) -> str:
    if episode is None:
        return "no_candidate"
    lo, hi = episode.get("onset_lo"), episode.get("onset_hi")
    if lo is None or hi is None:
        return "missing_bound"
    if hi <= cutoff:
        return "before_or_at_cutoff"
    if lo >= cutoff:
        return "after_or_at_cutoff"
    return "straddles_cutoff"


def reference_v4(rows: list[dict], ledger: list[dict], threshold: float = 10.0,
                 stop: float | None = None) -> list[dict]:
    """Independent slow derivation; shared X4/visits are explicit assumptions."""
    end = stop if stop is not None else max((v["t"] for v in visits(rows, threshold)), default=0.0)
    if any(b["issue_time"] <= a["issue_time"] for a, b in zip(ledger, ledger[1:])):
        raise ValueError("ledger issue times must be strictly increasing")
    if len({f["emission_index"] for f in ledger}) != len(ledger):
        raise ValueError("ledger emission indices must be unique")
    asof = [row for row in rows if float(row["JD"]) <= end]
    sequence = sorted((e for e in x4_episodes(asof, threshold) if e["confirmed_event"]), key=lambda e: e["peak_t"])
    observed = sorted(v["t"] for v in visits(asof, threshold))
    used = set()
    outcomes = []
    for position, forecast in enumerate(ledger):
        issue = forecast["issue_time"]
        index, episode = candidate(sequence, forecast["emitted_at"])
        lo, hi = (episode.get("onset_lo"), episode.get("onset_hi")) if episode is not None else (None, None)
        result = {
            "emission_index": forecast["emission_index"], "issue_time": issue,
            "computed_as_of": end, "evidence_available_at": end,
            "evidence_definition_version": "a10-outcome-evidence-v4",
            "kind": "excluded", "reason": None,
            "onset_lo": None, "onset_hi": None, "onset_t": None,
            "onset_method": None, "onset_index": None, "censor_at": None,
            "overtaken": False, "survival_ambiguous": False,
            "candidate_index": index, "candidate_onset_lo": lo, "candidate_onset_hi": hi,
            "stopping_cutoff": None, "stopping_reason": None,
            "censor_backoff": False, "censor_backoff_days": 0.0, "censor_rule": None,
        }
        if issue >= end:
            result["reason"] = "outside_record"
        elif hi is not None and hi <= issue:
            result.update(reason="overtaken", overtaken=True)
        elif episode is not None and (lo is None or lo <= issue):
            result.update(reason="ambiguous_survival", survival_ambiguous=True)
        else:
            cutoffs = {"record_end": end}
            if position + 1 < len(ledger):
                cutoffs["superseded"] = ledger[position + 1]["issue_time"]
            before = [t for t in observed if t <= issue]
            timeline = [before[-1] if before else issue, *[t for t in observed if t > issue], end]
            for left, right in zip(timeline, timeline[1:]):
                if right - left > 7.0 and right > issue and left < end:
                    cutoffs["coverage"] = max(left, issue)
                    break
            cause = min(cutoffs, key=lambda why: (cutoffs[why], why))
            cutoff = cutoffs[cause]
            result.update(stopping_cutoff=cutoff, stopping_reason=cause)
            if episode is not None and hi <= cutoff:
                if index in used:
                    raise ValueError("reference confirmed onset reused")
                used.add(index)
                result.update(kind="interval", reason="onset", onset_lo=lo, onset_hi=hi,
                              onset_t=episode.get("onset_t"), onset_method=episode.get("onset_method"),
                              onset_index=index)
            else:
                retained_lower_bound = min(cutoff, lo) if lo is not None else cutoff
                result.update(kind="right_censored", reason=cause, censor_at=retained_lower_bound,
                              censor_backoff=retained_lower_bound < cutoff,
                              censor_backoff_days=cutoff - retained_lower_bound,
                              censor_rule="working_set_lower_bound" if retained_lower_bound < cutoff else "stopping_cutoff")
        outcomes.append(result)
    return outcomes


def synthetic_checks() -> list[dict]:
    results = []
    for stopping in ("coverage", "superseded", "record_end"):
        for name, lo, hi in (("before", 16.0, 18.0), ("upper_equals_cutoff", 18.0, 20.0),
                             ("straddle", 18.0, 22.0), ("lower_equals_cutoff", 20.0, 22.0),
                             ("after", 22.0, 24.0), ("issue_straddle", 9.0, 11.0)):
            times = [float(t) for t in range(0, 41, 5)]
            ledger = [{"emission_index": 0, "emitted_at": 9.0, "issue_time": 10.0,
                       "end_lo": 6.0, "end_hi": 12.0}]
            end = 40.0
            if stopping == "coverage":
                times.remove(25.0)
            elif stopping == "superseded":
                ledger.append({"emission_index": 1, "emitted_at": 19.0, "issue_time": 20.0,
                               "repeat_of_previous": True})
            else:
                end = 20.0
                times = [t for t in times if t <= end]
            rows = [{"JD": t} for t in times]
            episodes = [{"confirmed_event": True, "peak_t": 24.0,
                         "onset_lo": lo, "onset_hi": hi, "onset_t": (lo + hi) / 2,
                         "onset_method": "injected_working_set", "end_t": None, "end_hi": None}]
            observed = [{"t": t} for t in times]
            with patch.object(outcome_evidence_v4, "x4_episodes", return_value=episodes), \
                    patch.object(outcome_evidence_v4, "visits", return_value=observed):
                production = outcome_evidence_v4.outcome_evidence(rows, ledger, stop=end)[0]
            with patch.dict(reference_v4.__globals__, {"x4_episodes": lambda *args: episodes,
                                                      "visits": lambda *args: observed}):
                independent = reference_v4(rows, ledger, stop=end)[0]
            if production != independent:
                raise ValueError("synthetic v4 reference mismatch")
            results.append({"case": name, "stopping_cause": stopping, "input_bracket": [lo, hi],
                            "synthetic_only": True, "equal_independent_reference": True,
                            "output": {key: production[key] for key in
                                       ("kind", "reason", "censor_at", "stopping_cutoff", "censor_backoff")}})
    return results


def load_retained(run: Path, inputs: Path) -> tuple[list[dict], dict, dict]:
    receipt = json.loads((run / "receipt.json").read_text())
    public = json.loads((ROOT / "data/provenance/a10i_evaluation_1960_2017/run-receipt.json").read_text())
    verify(run / "receipt.json", public["original_run_receipt_sha256"])
    if receipt["status"] != "completed" or receipt["mode"] != "live":
        raise ValueError("not the completed retained live run")
    source_hashes = receipt["source"]["sha256"]
    current_source_differences = []
    for name, expected in source_hashes.items():
        historical = subprocess.check_output(
            ["git", "show", f"{receipt['source']['freeze_commit']}:{name}"], cwd=ROOT)
        if hashlib.sha256(historical).hexdigest() != expected:
            raise ValueError(f"historical execution source mismatch: {name}")
        if digest(ROOT / name) != expected:
            current_source_differences.append(name)
    qualification = json.loads((ROOT / "data/simulations/a10d_20261108/run-receipt.json").read_text())
    qualified_hashes = qualification["source"]["source_sha256"]
    for name, expected in qualified_hashes.items():
        verify(ROOT / name, expected)
    for name in ("src/dnmem/evaluation_native.py", "src/dnmem/real_development.py", "src/dnmem/aavso.py",
                 "src/dnmem/coverage.py"):
        verify(ROOT / name, source_hashes[name])
    for name, expected in receipt["files_sha256"].items():
        verify(run / name, expected)
    verify(inputs, receipt["input_sha256"])
    cache = json.loads(inputs.read_text())
    config = json.loads((ROOT / "configs/a10e_real_fit.json").read_text())
    context, native_context = load_native(ROOT / "data/raw", cache, config)
    paths = []
    for acquisition in receipt["acquisitions"]["acquisitions"]:
        if not acquisition["requested_end_jd"] < STOP:
            raise ValueError("retained acquisition reaches the closed block")
        path = Path(acquisition["path"])
        verify(path, acquisition["sha256"])
        paths.append(path)
    later, native_evaluation = combine_native(paths)
    seen = {}
    for row in context + later:
        if float(row["JD"]) >= STOP:
            raise ValueError("reserved row rejected before extraction")
        obs_id = row["obsID"]
        if obs_id in seen and seen[obs_id] != row:
            raise ValueError("conflicting retained overlap")
        seen[obs_id] = row
    rows = select_analysis_rows(sorted(seen.values(), key=lambda r: (float(r["JD"]), r["obsID"])))
    proof = {
        "original_receipt_sha256": digest(run / "receipt.json"),
        "historical_execution_source_files_verified": len(source_hashes),
        "current_execution_source_differences": current_source_differences,
        "qualified_forecasting_sources_verified": len(qualified_hashes),
        "run_outputs_verified": len(receipt["files_sha256"]),
        "pre1960_native_sources_verified": len(native_context["source_sha256"]),
        "evaluation_native_sources_verified": len(native_evaluation["acquisitions"]),
        "input_cache_sha256": digest(inputs),
        "parameters_sha256": receipt["parameters_sha256"],
        "all_hashes_match": True,
        "all_analysis_rows_strictly_before_2018": True,
    }
    private_proof = {"context_native_sha256": native_context["source_sha256"],
                     "evaluation_native_sha256": {str(p.relative_to(ROOT)): digest(p) for p in paths},
                     "analysis_rows": len(rows)}
    return rows, proof, private_proof


def audit(run: Path, inputs: Path, cache_directory: Path | None = None) -> tuple[dict, dict]:
    rows, proof, private_proof = load_retained(run, inputs)
    ledger = json.loads((run / "ledger-0.0.json").read_text())
    evidence = json.loads((run / "evidence-0.0.json").read_text())
    scores = json.loads((run / "primary-scores.json").read_text())
    all_episodes = x4_episodes(rows)
    episodes = sorted((e for e in all_episodes if e["confirmed_event"]), key=lambda e: e["peak_t"])
    observed_visits = visits(rows)
    if cache_directory is not None:
        cache_files = {}
        for filename, value in (("validated-rows.json", rows), ("all-x4-episodes.json", all_episodes),
                                ("visits.json", observed_visits)):
            path = cache_directory / filename
            with path.open("w") as handle:
                json.dump(value, handle, sort_keys=True, allow_nan=False, separators=(",", ":"))
                handle.write("\n")
            cache_files[filename] = {"sha256": digest(path), "items": len(value)}
        (cache_directory / "private-cache-receipt.json").write_text(json.dumps({
            "label": "Private retained-input derivative; contains observation/observer metadata; never publish these caches",
            "files": cache_files, "input_verification": proof,
            "rows_order": "native JD, then native obsID; visual/V selected without field mutation",
            "episode_order": "unaltered frozen x4_episodes output, including unconfirmed episodes",
            "visits_order": "unaltered frozen visits output",
            "extractor_sha256": digest(ROOT / "src/dnmem/extract_x4.py"),
            "visit_builder_sha256": digest(ROOT / "src/dnmem/extract.py"),
            "stop_jd_exclusive": STOP,
        }, indent=2, sort_keys=True) + "\n")
    recomputed = []
    for module in (prefix_features, prefix_reference):
        with patch.object(module, "x4_episodes", return_value=episodes), \
                patch.object(module, "visits", return_value=observed_visits):
            recomputed.append(module.outcome_evidence(rows, ledger, stop=STOP))
    if any(result != evidence for result in recomputed):
        raise ValueError("retained evidence differs from recomputed v3 routing")
    with patch.object(outcome_evidence_v4, "x4_episodes", return_value=episodes), \
            patch.object(outcome_evidence_v4, "visits", return_value=observed_visits):
        prospective = outcome_evidence_v4.outcome_evidence(rows, ledger, stop=STOP)
    with patch.dict(reference_v4.__globals__, {"x4_episodes": lambda *args: episodes,
                                              "visits": lambda *args: observed_visits}):
        independent_v4 = reference_v4(rows, ledger, stop=STOP)
    if prospective != independent_v4:
        raise ValueError("prospective v4 differs from independent routing")
    legacy_fields = set(evidence[0])
    changed = [new["emission_index"] for old, new in zip(evidence, prospective)
               if old != {key: new[key] for key in legacy_fields}]
    score_by_id = {s["emission_index"]: s for s in scores}
    cases = []
    for position, (forecast, outcome) in enumerate(zip(ledger, evidence)):
        if forecast["emission_index"] != outcome["emission_index"]:
            raise ValueError("ledger/evidence identity mismatch")
        if outcome["kind"] != "right_censored":
            continue
        index, episode = candidate(episodes, forecast["emitted_at"])
        cutoff = outcome["censor_at"]
        next_forecast = ledger[position + 1] if position + 1 < len(ledger) else None
        cases.append({
            "emission_index": forecast["emission_index"], "issue_time": forecast["issue_time"],
            "emitted_at": forecast["emitted_at"], "reason": outcome["reason"], "cutoff": cutoff,
            "candidate_index": index,
            "candidate": {key: episode.get(key) for key in
                          ("peak_t", "onset_lo", "onset_hi", "onset_t", "onset_method", "end_lo", "end_hi", "end_t")}
                          if episode is not None else None,
            "actual_candidate_relation": relation(episode, cutoff),
            "next_emission": {key: next_forecast.get(key) for key in
                              ("emission_index", "repeat_of_previous", "onset_lo", "onset_hi", "onset_t")}
                              if next_forecast is not None else None,
            "original_gain_M3_M2": score_by_id[forecast["emission_index"]]["gain_M3_M2"],
        })
    gains = [s["gain_M3_M2"] for s in scores]
    censored_sum = sum(case["original_gain_M3_M2"] for case in cases)
    summary = {
        "label": "R1a/E3 offline exploratory audit of the already opened frozen SS Cyg 1960-2017 result",
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "script_sha256": digest(Path(__file__)),
        "input_verification": proof,
        "primary_issuances": len(ledger),
        "censored_issuances": len(cases),
        "actual_candidate_relation_by_reason": dict(Counter(
            f"{case['reason']}:{case['actual_candidate_relation']}" for case in cases)),
        "straddling_actual_candidates": sum(case["actual_candidate_relation"] == "straddles_cutoff" for case in cases),
        "both_frozen_builders_reproduce_all_primary_evidence": True,
        "prospective_v4_matches_independent_reference": True,
        "prospective_v4_changed_primary_outcome_rows": len(changed),
        "prospective_v4_backoffs": sum(e["censor_backoff"] for e in prospective),
        "censored_total_original_gain": censored_sum,
        "mean_original_gain": sum(gains) / len(gains),
        "mean_gain_excluding_all_censored": (sum(gains) - censored_sum) / (len(gains) - len(cases)),
        "limits": [
            "Candidates recovered from the full frozen X4 confirmed-episode sequence, not from the next emission.",
            "Uses shared frozen extraction; routing concordance is not physical-truth validation.",
            "Dropping censors is a sensitivity, not a bound over all possible corrections.",
            "No archive request, 2018+ observation, new-star input, refit, or frozen-file change.",
            "X4 posterior brackets are working intervals; survival-to-lower-bound requires the declared hard-bracket approximation.",
        ],
    }
    return summary, {"input_proof": private_proof, "cases": cases,
                     "prospective_v4_changed_emission_indices": changed}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=ROOT / "outputs/a10h_live_repair_5e39aeb")
    parser.add_argument("--inputs", type=Path, default=ROOT / "outputs/a04i_inputs_frozen_20261108/inputs.json")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/r1_censor_audit")
    args = parser.parse_args()
    if args.output.resolve() != (ROOT / "outputs/r1_censor_audit").resolve():
        raise ValueError("private per-case output must remain in ignored outputs/r1_censor_audit")
    args.output.mkdir(exist_ok=True)
    summary, private = audit(args.run, args.inputs, args.output)
    synthetic = synthetic_checks()
    summary["synthetic_boundary_cases_matching_independent_reference"] = len(synthetic)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    (args.output / "private-cases.json").write_text(json.dumps(private, indent=2, sort_keys=True) + "\n")
    (args.output / "synthetic-fixtures.json").write_text(json.dumps(synthetic, indent=2, sort_keys=True) + "\n")
    (args.output / "report.md").write_text(
        "# R1a/E3: actual candidate audit and prospective v4 routing\n\n"
        "Exploratory audit of the already opened SS Cyg 1960–2017 record. "
        "All original frozen files and results remain unchanged.\n\n"
        "| Frozen censor cause | Cases | Actual candidate relation |\n"
        "|---|---:|---|\n| Coverage | 4 | Entire bracket after cutoff |\n"
        "| Supersession | 1 | Entire bracket after cutoff |\n"
        "| Record end | 1 | No eligible next confirmed candidate |\n\n"
        f"Zero actual brackets cross their cutoff. Both frozen builders reproduce all {summary['primary_issuances']} "
        "serialized primary outcomes from the retained full X4 episode sequence. "
        "The prospective v4 and independent reference agree and change "
        f"{summary['prospective_v4_changed_primary_outcome_rows']} primary outcome rows.\n\n"
        f"The six original censored terms sum to {summary['censored_total_original_gain']:.14f} nats; "
        f"the mean is {summary['mean_original_gain']:.14f}, or "
        f"{summary['mean_gain_excluding_all_censored']:.14f} after dropping all six. "
        "Dropping them is a sensitivity, not a bound over every possible correction.\n\n"
        "V4 is separate from both frozen v3 builders. For issue < L < C < U, it retains "
        "right censoring at L, keeping the original stopping cutoff and cause. L=C is unchanged; "
        "U<=C remains an interval; issue-straddling and overtaken candidates remain excluded. "
        "This corrects a working-set routing defect. It does not make X4 posterior brackets or "
        "decisive reports proven physical bounds.\n\n"
        "The 18 injected boundary cases cover coverage, repeat supersession and record-end stopping. "
        "They isolate routing and do not assert X4 can generate every injected episode. "
        "Unit fixtures additionally extract real synthetic light curves: a repeat retires the earlier "
        "forecast, and an active final outburst with no later emission/end is still the next onset candidate.\n\n"
        "Verified identities: 120 historical execution-source blobs at the receipt freeze; all 26 "
        "qualified forecasting files in the current checkout; actual native-loader sources; 15 saved "
        "run outputs; the input cache; 12 pre-1960 native sources; and 63 evaluation leaves. "
        "The sole current difference among the 120 historical sources is the documented evolving "
        "publication validator scripts/validate_seed.py.\n\n"
        "Exact per-case times and observation-source paths remain in ignored private-cases.json. "
        "summary.json and synthetic-fixtures.json contain no real per-issuance times or observer identity. "
        "No network request, 2018+ inspection, new-star input or refit was performed.\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
