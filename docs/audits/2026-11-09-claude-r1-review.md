# Claude review of R1 (C42–C46) and the cause of the missing report clips

Claude (Opus 5.5), 9 November 2026, reviewing Codex's
[R1 audit](2026-11-09-r1-observation-endpoint-diagnostics.md), D033 and D034. All checks read
retained outputs from the already opened 1896–2017 record. No archive request was made; no row,
count or coverage summary from 2018 onward was requested or inspected. Everything here is
exploratory and post-result.

Script: `scripts/r1_claude_review_checks.py`; aggregates: `data/provenance/r1_claude_review/checks.json`.
The code is separate from Codex's routes. It shares only the retained inputs and, for C43, Codex's
reconstructed episode catalogue.

## Verdicts on the provisional claims

| Claim | My check | Result | Status |
|---|---|---|---|
| C42 Figure 1 example | Same selector and frozen parameters; scipy lognormal with root finding (Codex used erfc and inverse normal) | M2 27.5749 d, 57.6727%; M3 26.7726 d, 60.2765%; identical to stated precision | supported |
| C43 censor audit | Reimplemented the builder's candidate rule (first confirmed episode peaking after emission with `onset_hi` after emission) over the 860-episode catalogue | Four coverage and one supersession candidate start after their cutoffs; the record-end case has no candidate; zero straddles | supported |
| C44 point density | CR1 with six-year blocks from JD 2436934.5 on retained paired gains | +0.0154038 [0.0034429, 0.0273648]; paired change −0.0011297 [−0.0017462, −0.0005132]; Spearman 0.993763; same-row primary reproduces C01 | supported |
| C45 clip availability | Status counts and CR1 on the eleven contrasts | 430 missing clip, 6 usable, 5 identical forecasts; −0.018101 [−0.045489, 0.009287] in 3 blocks | supported (limit amended below) |
| C46 endpoint dose | Per-history all-issued means streamed from all 80 retained score files (79 original, structured-000 from the recovery) | All ten means and MC SEs reproduce exactly; six excluded rows per history per dose carry no gain | supported |

I accept D034's reading. The working-score gain survives the censor correction and the point-density
sensitivity. The added iid end-noise mechanism does not produce a positive mean gain in either fixed
family. That experiment cannot exclude the reviewer's landmark counterexample (E2), which works
through the shared end estimate and the issue age, not through noise. R2 therefore needs a test that
removes the shared end estimate from the forecast altogether (R2 design §3).

## Why 434 forecasts have no lower clip: an X4 bug, mine

X3 and X4 are my code. In `extract_x4.py`, the onset clip is

```
first_far_b = min(far-bright reports in (previous peak, peak])
clip_on = (max(far-faint reports in (previous peak, first_far_b)), ...)
```

The first far-bright report after the previous peak is almost always in **that previous outburst's
own bright phase**, a day or two after its peak. Nothing far-faint can precede it inside the window, so
the lower clip is empty. My separate count, using positive estimates only, finds that pattern in 788
of 845 confirmed episodes with a predecessor. Codex's count, which also uses fainter-than limits,
is 793 of 860. The search window should start once quiescence is re-established, not at the
previous peak. The upper clip (the first far-bright report after the last far-faint one) was
correct.

The scored X4 intervals were therefore 99% crossing-posterior intervals clipped on the upper side
only. That does not change C01 as a working score, but it is why R1b's two-sided comparison
collapsed to eleven contrasts. C45's limit now records the cause.

**A corrected decisive bracket is almost always available and narrow (gain-free).** I defined it
as follows:

- the quiescence anchor is the first report at least 1 mag fainter than the threshold after the
  previous peak;
- U is the first report at least 1 mag brighter after that anchor;
- L is the last report at least 1 mag fainter before U.

| Quantity | Value |
|---|---|
| Confirmed episodes with a predecessor | 845 |
| Bracket available | 818 (96.8%) |
| No decisive faint report after the previous peak | 4 |
| No decisive bright report after quiescence (faint peaks) | 23 |
| Width, median (IQR) | 1.16 d (0.78–2.88) |
| Width, 90th percentile | 4.71 d |
| Share ≤ 2 d / ≤ 5 d | 68.3% / 92.2% |
| X4 saved onset interval, median width | 1.12 d |

These widths are computed over the whole opened 1896–2017 record and include no score. With
`BAND = 1` mag, a decisive bracket fails to contain the crossing only if a visual estimate errs by
at least a magnitude in the wrong direction. That makes a hard-bracket observation contract usable
for SS Cyg, which R1 could not test. R2 design §2 builds on it.

## Not checked

- I did not rerun Codex's endpoint simulator, the kernel quadrature or the v4 builder tests. I
  checked their retained outputs and aggregates.
- C43 uses Codex's reconstructed episode catalogue, so it is independent in rule and code, not in
  extraction.
- The corrected-bracket counts omit fainter-than limits. A frozen implementation (X5) must include
  them, and its counts will differ slightly.
