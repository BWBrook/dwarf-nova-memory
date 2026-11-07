# Native coverage profiles

`ss_cyg_open_era_profiles_20261107.csv` contains per-request diagnostics for the
12 hashed acquisitions in the manifest. Overlapping requests repeat observations;
do not sum their counts as unique data. The profiler checks receipt hashes and
windows and deduplicates identical native IDs for its combined count.

```bash
python3 scripts/profile_ss_cyg_coverage.py data/raw/aavso_ss_cyg_*/native.xml
```

Informative coverage uses V-flagged visual detections, or visual faint limits
of at least magnitude 10. Unknown/R/CR bands and T flags remain in raw data and
the native counts. JD bins are noon-to-noon native bins, not verified local
observing nights; observer-bin repeats are reported without averaging magnitudes.
These are returned-row coverage diagnostics, not completeness, detection
efficiency, quiescence or usable-cycle estimates. No event relationship is fitted.

`ss_cyg_open_era_x1_by_decade.csv` profiles candidate extractor X1 (A04b) over
the deduplicated open-era stream: episodes, confirmations, gap splits, median
boundary-interval widths and consecutive pairs whose longest informative gap in
quiescence is at most 4 or 7 d. X1 is not frozen. Pair counts are coverage
diagnostics until injection/recovery establishes detection completeness. Rebuild
with `python3 scripts/a05_compare_extractors.py --table <path>`.
