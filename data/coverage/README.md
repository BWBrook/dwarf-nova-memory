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
