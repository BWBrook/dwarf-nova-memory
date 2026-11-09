# Independent review of dwarf-nova-memory

**For Barry W. Brook, Claude and Codex — 9 November 2026**

Start with **pro-review.md**. Its 523-word executive assessment gives the verdict; the priority table identifies essential corrections; §7 responds to Barry's preference for a more comprehensive and consequential study; §§10–11 give the ordered next round of work and the few human judgments needed.

## What is in this package?

| File or directory | Purpose |
|---|---|
| pro-review.md | Complete scientific, editorial and strategic review, with precise locations, remedies and resolution criteria |
| review-manifest.json | Reviewed commit/tree, exact manuscript hashes, reading order and staged-source identity inventory |
| new-reference-identifiers.txt | Plain-text identifiers for newly proposed references/policy, one per line |
| checks/ | Four small, reproducible arithmetic/synthetic review checks, source pins, inputs, results, dependencies and a detailed README |
| records/selected-tests.log | Result of the 52 selected existing repository tests run during review |
| records/parser-repair-comparison.json | Comparison of recorded source inventories and parameter/protocol identity across the documented parser repair |
| package-sha256.txt | SHA-256 inventory of the package files, excluding this checksum file itself |

The review covers **BWBrook/dwarf-nova-memory commit f48f0e2c728739a97fb90fb795eddb54c98c2dc3**, dated 8 November 2026 16:00:02 UTC. The branch still pointed to that commit when rechecked during review. The article is 13 pages, supplement 9 pages, and brief 2 pages. No current separately supplied snapshot was available; no later source version was mixed in.

## How to use it

1. Read the executive assessment and priorities before editing prose.
2. Give the full report to both project agents, with the existing data-access boundaries intact. Ask them to use the ordered brief and return a response matrix identifying what is resolved, narrowed or deferred.
3. Keep this package separate from the frozen analysis. Nothing here supersedes its protocol, source or results.
4. Use the supporting checks where their limited question is relevant. Their README explains exactly how to run them. They do not reproduce the real-data pipeline.

The preferred larger study connects observation/measurement validity, evolving activity state and replication across comparable systems. That strategic expansion is separate from the corrections needed for the present bounded claim. The current SS Cyg result remains an identifiable component, not a fresh confirmation of an enlarged question.

## Check dependencies and inputs

The report itself needs only a Markdown reader. The included Python checks were run with Python 3.12.14, NumPy 2.3.5 and SciPy 1.17.0; pinned versions are in checks/requirements.txt.

- The aggregate calculation uses only the bundled ten public block counts/means.
- The finite-state endpoint example runs without a project checkout.
- The landmark-mixture and censor-cutoff checks require a local copy of selected files from the reviewed commit. They verify source hashes before importing them and stop on mismatch.
- An optional endpoint-helper comparison and aggregate-input comparison also accept a local reviewed source path.

No script downloads anything, runs an archive pipeline or changes the project source. Each requires an explicit output path and rejects output within the supplied project checkout. The supplied JSON results can be read without running code. Full commands, provenance and limits are in checks/README.md.

## Limits and preservation

This is an independent review, not a full replication or certification. Public aggregation and synthetic code paths were verified; original real-event extraction and individual forecast scores were not regenerated. The onset-bracket/censoring concern is a demonstrated synthetic code path, not an established error among the six empirical censored cases.

No 2018-onward observations, counts, coverage summaries or light curves were requested or inspected. No archive acquisition was made, no original repository was modified, and no outside person or organisation was contacted. The package contains no raw archive exports, observer identities, manuscript PDFs or third-party copyrighted full texts.

All new calculations are exploratory review diagnostics. Preserve the original primary analysis and execution history. Further checks on already inspected data cannot become new confirmation.
