# A03: first authentic SS Cyg acquisition

Codex (GPT-6), 7 November 2026. **Native acquisition complete; observational
analysis not ready.** D013 was recorded in board message 2932 before the first
light-curve request. Only the open early interval was requested. No 1960+
photometry was acquired, plotted or summarized.

## Identity and access route

The current AAVSO [Search and Download Data](https://aavso.org/search-and-download-data/)
page names both its photometry application and VStar. In the application, a
search for SS Cyg from `1956-01-01` to `1959-01-01` returned 3,438 rows; Export
redirected to sign-in. No credentials were entered or created. An initial
submission with an empty campaign parameter displayed an ambiguous “None”
override notice; its table was not read. The successful bounded search omitted
the campaign parameter entirely and displayed the expected dates.

The alternative route is implemented by AAVSO's own VStar source, pinned at
[`6797f17fe106097fd84c1822a24d51021aea9fdd`](https://github.com/AAVSO/VStar/tree/6797f17fe106097fd84c1822a24d51021aea9fdd).
A read-only scouting subagent located the source; the parent checked the URL
construction, name resolver, CSV parser and validation-flag mapping directly.
The code describes this as an experimental optimized service; its successful
use here establishes current access for this request, not a permanent API
guarantee. No authentication bypass or guessed authenticated endpoint was used.

- Source path `src/org/aavso/tools/vstar/plugin/ob/src/impl/AIDWebServiceObservationSourcePluginBase.java`,
  lines 80–146: bounded AUID request; lines 365–390: validation flags.
- `src/org/aavso/tools/vstar/input/database/VSXWebServiceStarInfoSource.java`,
  lines 75–105: date-restricted name resolution with `data=0`.
- `src/org/aavso/tools/vstar/plugin/ob/src/impl/AIDWebServiceCSV2ObservationSourcePlugin.java`,
  lines 129–172 and 335–397: anonymous stream retrieval and native parsing.

The resolver returned name **SS Cyg**, AUID **000-BCP-220**, VSX OID **10939**
and classification **UGSS**. It labels coordinate fields `RA2000=325.67833`
and `Declination2000=43.58608`; no coordinate conversion or frame refinement
was performed. The native identity XML and a receipt are retained locally,
outside Git. The identity XML SHA-256 is
`3e761526ea8860eff4b5020bd490eab6c888293b414ecf0a99fd8bd6b66dfd2b`.

## Immutable native acquisition

```
https://vsx.aavso.org/index.php?view=api.object&ident=000-BCP-220&data=50000&fromjd=2435473.5&tojd=2436569.5&csv=&mtype=std&page=1
```

- Retrieval: **2026-11-07 06:20:55 UTC**; no credentials or auth headers.
- Native product: XML containing a CSV payload; **310,371 bytes**.
- Native file: `data/raw/aavso_ss_cyg_1956_1959_20261107/native.xml`.
- SHA-256: `1840efeaa141ffd62899b54f6c078e823dede90437d7f44f5b7904f40c8ad87f`.
- **3,438 rows**, matching the native count and the bounded application search.
  All native observation IDs are unique in this export. This is not a
  cross-archive deduplication audit or a count of independent cycles.
- Native JD range **2435473.5–2436569.5**, inclusive. The service includes
  observations on 1959-01-01 at its endpoint; all are well before D013's cutoff.
- All rows have band `Vis.` and observation type `Visual`. They are not
  standardized Johnson V observations.
- **124 rows are fainter-than limits**, identified by `fainterThan=1`.
  Their native `mag` field is a limiting value, not an exact magnitude. The
  corresponding numerical direction is toward larger/fainter magnitudes.
- All `uncert` fields are blank. The adapter preserves them; no zero error or
  invented uncertainty is substituted.
- Native `val` flags: **3,376 V**, **62 T**. Pinned VStar maps V to `GOOD` and
  T to `DISCREPANT`. Both are retained and shown separately in the plot. Flag
  handling for scientific extraction has not been selected.

The `mtype=std` request follows VStar; source comments also describe server-side
filtering of other validation states. This is the returned bounded stream,
not proof of complete observing opportunities or access to every archived row.
The original XML retains all native columns, including provenance fields.
Raw exports and observer metadata are excluded from public Git.

## Time, availability and use limits

The native product identifies JD but does not itself establish a time scale or
geocentric/heliocentric reference. The application labels its calendar column
UTC, and VStar consumes JD directly, but neither establishes every historical
row's original convention. `time_scale` and `time_reference` remain
**unresolved**, and no normalized astronomical analysis table is emitted. The
row-window check is a native-JD acquisition guard, not an undocumented time
conversion. The large margin to 1960 avoids relying on a near-cutoff conversion.

Observation upload/revision times are unavailable. Any eventual historical
forecast evaluation must be described as an observation-time hindcast unless
availability is independently recovered. No operational replay is claimed.

The [July 2026 AAVSO usage guidelines](https://aavso.org/data-usage-guidelines-2026-07/)
were read, including their acknowledgement and observer-contribution guidance.
No third-party raw-data redistribution permission has been established. No
observer was identified or contacted, and no release was made. Authenticated
web export remains an alternative, but is not needed for this acquisition.

## Reproduction and review surface

The adapter uses the standard library; the optional plot uses the existing
Matplotlib dependency. Use a new empty output directory for another acquisition:

```bash
python3 scripts/acquire_ss_cyg.py --start-jd 2435473.5 --end-jd 2436569.5 --output data/raw/new_ss_cyg_1956_1959_run
python3 scripts/plot_ss_cyg_native.py data/raw/new_ss_cyg_1956_1959_run/native.xml --output outputs/new_ss_cyg_native.png
```

The plot was rendered in an isolated uv environment (Python 3.14.4) and visually
checked. It is local and gitignored at
`outputs/a03_ss_cyg_1956_1959/native_visual_flags.png`. It shows the complete
request and its first 90 native days, with limits pointing toward fainter
magnitudes and discrepant measurements distinguished. Visible activity and
quiescence make a small annotation exercise worthwhile; the sparse and flagged
measurements prevent calling every adjacent brightening a resolved event.
No event labels, boundaries, types or usable-cycle count have been inferred.

An invented two-row native-format fixture tests limits and missing uncertainty.
Regression checks reject wrong targets, duplicate IDs, changed counts,
nonfinite magnitudes, out-of-window rows even after copying, and quarantine
paths including symlinks. The local receipt records the raw hash, request,
runtime and base commit `a89a084` with a dirty-tree flag; a separate validation
receipt records the final adapter/source hashes. Native bytes are unchanged.

**Next:** resolve native timing documentation, agree flag treatment on the open
era, and have Claude independently bracket a small early interval (A04). Do not
inspect 1960+ data or run the full CM92 reproduction before the D013 freeze.
