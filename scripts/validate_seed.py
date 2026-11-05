#!/usr/bin/env python3
"""Offline structural checks for the research package, not scientific validation."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    problems: list[str] = []
    required = ["README.md", "AGENTS.md", "CLAUDE.md", "references/literature.bib",
                "references/evidence.csv", "references/search-log.md",
                "configs/candidate_targets.csv", "configs/study_plan.json",
                "docs/01-research-brief.md", "docs/02-literature-review.md",
                "docs/03-data-and-provenance.md", "docs/04-pilot-targets.md",
                "docs/05-statistical-design.md", "docs/06-simulation-and-validation.md",
                "docs/07-risks-and-decision-gates.md", "docs/08-implementation-roadmap.md",
                "docs/09-data-dictionary.md", "docs/10-domain-primer.md",
                "docs/11-reproducibility-and-workflow.md", "docs/12-seed-validation.md"]
    for name in required:
        if not (ROOT / name).is_file():
            problems.append(f"missing required file: {name}")
    if problems:
        raise SystemExit("\n".join(problems))
    tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    for path in (ROOT / "configs").glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    bib = (ROOT / "references/literature.bib").read_text(encoding="utf-8")
    keys = re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib)
    if len(keys) != len(set(keys)):
        problems.append("duplicate BibTeX key")
    if bib.count("{") != bib.count("}"):
        problems.append("unbalanced BibTeX braces (structural check only)")
    with (ROOT / "references/evidence.csv").open(newline="", encoding="utf-8") as handle:
        evidence = list(csv.DictReader(handle))
    evidence_keys = [row["citekey"] for row in evidence]
    if set(evidence_keys) != set(keys) or len(evidence_keys) != len(set(evidence_keys)):
        problems.append("bibliography and evidence register must match one-to-one")
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        content = path.read_text(encoding="utf-8")
        for group in re.findall(r"\[([^\]\n]*@[A-Za-z][^\]\n]*)\]", content):
            for key in re.findall(r"@([A-Za-z][\w:.-]*)", group):
                if key not in keys:
                    problems.append(f"unknown citation {key}: {path.relative_to(ROOT)}")
        for dest in re.findall(r"\[[^\]\n]+\]\(([^\s)]+)\)", content):
            if dest.startswith(("http:", "https:", "mailto:", "#")):
                continue
            target = dest.split("#", 1)[0]
            if target and not (path.parent / target).exists():
                problems.append(f"missing local link {dest}: {path.relative_to(ROOT)}")
    with (ROOT / "configs/candidate_targets.csv").open(newline="", encoding="utf-8") as handle:
        candidates = list(csv.DictReader(handle))
    ids = [r["target_id"] for r in candidates]
    if len(ids) != len(set(ids)):
        problems.append("duplicate candidate target ID")
    demo = ROOT / "outputs/seed_demo"
    summary = json.loads((demo / "summary.json").read_text(encoding="utf-8"))
    if summary.get("data_kind") != "SYNTHETIC ONLY":
        problems.append("seed demo is not labelled synthetic")
    for name, expected in summary["sha256_csv"].items():
        actual = hashlib.sha256((demo / name).read_bytes()).hexdigest()
        if actual != expected:
            problems.append(f"demo CSV hash mismatch: {name}")
    if problems:
        raise SystemExit("\n".join(problems))
    print(json.dumps({"status": "structural checks passed", "references": len(keys),
                      "candidate_targets": len(candidates), "demo_csv_hashes": len(summary["sha256_csv"]),
                      "scope": "local links, citation keys, basic config structure and seed CSV integrity; not source truth or scientific adequacy"}, indent=2))


if __name__ == "__main__":
    main()
