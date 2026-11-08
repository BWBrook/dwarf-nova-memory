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


_CSL_ID = re.compile(r"^- id: ([A-Za-z][A-Za-z0-9_:.-]*)$")
_CITATION_GROUP = re.compile(r"\[([^\]\n]*@[A-Za-z][^\]\n]*)\]")
_CITATION_KEY = re.compile(r"@([A-Za-z][\w:.-]*)")


def csl_yaml_keys(content: str) -> set[str]:
    """Read the controlled top-level ID form emitted by tools/refs.py."""
    lines = [line for line in content.splitlines()
             if line.strip() and line.strip() not in {"---", "..."}
             and not line.lstrip().startswith("#")]
    if not lines or lines[0] not in {"references:", "references: []"}:
        raise ValueError("CSL-YAML must start with the generated references mapping")
    if lines[0] == "references: []":
        if len(lines) != 1:
            raise ValueError("CSL-YAML empty references mapping has trailing records")
        return set()
    keys: set[str] = set()
    for line in lines[1:]:
        if line.startswith("- "):
            match = _CSL_ID.fullmatch(line)
            if match is None:
                raise ValueError("unsupported CSL-YAML record header; expected '- id: CiteKey'")
            key = match.group(1)
            if key in keys:
                raise ValueError(f"duplicate CSL-YAML ID: {key}")
            keys.add(key)
        elif re.match(r"^\s+(?:-\s+)?id\s*:", line):
            raise ValueError("unsupported or duplicate indented CSL-YAML ID")
        elif not line.startswith(" ") or not keys:
            raise ValueError("unsupported CSL-YAML structure outside a generated record")
    if not keys:
        raise ValueError("CSL-YAML references mapping has no generated records")
    return keys


def unknown_citations(content: str, known_keys: set[str]) -> list[str]:
    return sorted({key for group in _CITATION_GROUP.findall(content)
                   for key in _CITATION_KEY.findall(group) if key not in known_keys})


def main() -> None:
    problems: list[str] = []
    required = ["README.md", "AGENTS.md", "CLAUDE.md", "references/literature.bib",
                "references/refs.yaml",
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
    manuscript_keys: set[str] = set()
    try:
        manuscript_keys = csl_yaml_keys((ROOT / "references/refs.yaml").read_text(encoding="utf-8"))
    except ValueError as exc:
        problems.append(f"references/refs.yaml: {exc}")
    known_keys = set(keys) | manuscript_keys
    for path in ROOT.rglob("*.md"):
        if any(part in {".git", ".venv", ".cache", "__pycache__"} for part in path.parts):
            continue
        content = path.read_text(encoding="utf-8")
        for key in unknown_citations(content, known_keys):
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
                      "manuscript_references": len(manuscript_keys),
                      "candidate_targets": len(candidates), "demo_csv_hashes": len(summary["sha256_csv"]),
                      "scope": "local links, citation keys, basic config structure and seed CSV integrity; not source truth or scientific adequacy"}, indent=2))


if __name__ == "__main__":
    main()
