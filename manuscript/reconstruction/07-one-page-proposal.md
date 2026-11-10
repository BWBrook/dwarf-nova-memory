# Codex proposal for Step 2

For discussion with Claude, 10 November 2026; reviewed against C01–C05, C10, C25,
C44, C55, C62 and C68–C70. This is a proposed revision of `05-one-page-paper.md`,
not the product rewrite. 585 words of prose, excluding this note and the title (whitespace count after removing claim markup).

## Outburst length improves forecasts from SS Cygni's visual record

**Introduction.** SS Cygni is a dwarf nova: a white dwarf draws gas from a companion into a disc
that repeatedly brightens in outbursts. Earlier studies linked longer outbursts to longer quiet
intervals (Cannizzo & Mattei 1992). We asked whether duration improves forecasts of the next
onset beyond recent timing history. Two hypotheses motivate this comparison: greater disc
depletion after a long outburst prolongs recovery at comparable gas-supply rates; or duration
tracks a slowly changing accretion state that recent intervals describe incompletely.

**Methods.** We used visual brightness estimates reported to the American Association of Variable
Star Observers (AAVSO). An algorithm identified outbursts and estimated their starts and ends.
When reports confirmed a fade, we issued next-onset probabilities from lognormal quiet-gap
clocks, conditioning on the quiet time already elapsed. Each forecast used only reports dated
by issue. A timing model used the previous log quiet interval and the mean log gap over up to
six earlier covered intervals; a second added log duration. We fitted the models on 1910–1959, froze them and published the
protocol on Zenodo before opening 1960–2017. We scored the logarithm of the probability assigned
to each extracted onset window, using survival probabilities when follow-up ended first.
Higher scores, in natural-log units (nats), mean more probability assigned to the scored evidence.
The preregistered criterion required the mean duration gain's 90% interval, calculated using
six-year blocks, to lie above zero. Follow-up analyses changed the measurements and models.
A separately frozen screen asked whether ten other stars' pre-1990 records supported a comparable
test.

**Results.** The duration model predicted longer waits after longer outbursts. Adding duration
raised the working score by [0.0165]{.C01 .V001} nats per forecast (90% interval
[0.0049]{.C01 .V002}–[0.0281]{.C01 .V003}; [441]{.C01 .V004} forecasts), meeting the criterion.
This corresponds to [1.7]{.C02}% higher geometric mean probability assigned to the scored evidence.
Recent timing alone added [0.117]{.C10} nats over a constant forecast. Duration's gain was positive
in eight of ten blocks. Scoring at single estimated onsets gave [0.0154]{.C44} nats.
Two redesigned comparisons gave gains of [0.0075]{.C55 .V009} and [0.0043]{.C55 .V013} nats,
with intervals spanning zero: one retained a fitted end, while the other started its clock at an
observed faint report. The preregistered later-period and long/short-rule comparisons were also
inconclusive.[]{.C07}[]{.C08} None of the ten candidate stars passed every feasibility gate.
Nine fell below the forty-forecast requirement; SS Aur passed that count but failed the long-run
screen.[]{.C68} In the 1980s, SS Cyg supplied [67]{.C70} supported issuances against
[73]{.C70} confirmed peaks; the candidates supplied [102]{.C70} against [485]{.C70}.

**Discussion.** Duration improved forecasts evaluated against SS Cyg's visual record beyond the
chosen timing baseline. Disc depletion and a slowly changing state provide two physical hypotheses
for further testing. Measurements of the disc and gas supply alongside recurrence forecasts
could help distinguish them.

**Limitations.** Linking this working score to physical onset requires a validated observation
model. Shared end estimates couple duration and the next gap; observing effort can also respond
to activity. Post-result duration recentering and baseline recalibration reduced an analogous
gain. The follow-up checks reuse opened data and are exploratory. The first data access exposed
an unused-field parser error, repaired before scoring. Issuance/peak ratios describe operational
support under fixed rules. Historical upload and revision times are unknown. The forecasting result concerns one star.

**Conclusion.** A century of amateur observations enabled a preregistered test showing that duration
adds forecast skill in SS Cyg's visual record. Freezing predictors before testing them on later
observations provides a transferable design for irregular recurrent events. Other applications
would define their own observation process, usable cycles and forecasting baseline. Code,
protocols and aggregate evidence are public.
