# Step 2: the one-page paper

About 640 words of text; revised after a cold read by a non-specialist reader (Claude Sonnet
subagent), 10 November 2026.

## The length of an SS Cygni outburst helps forecast the next one: a preregistered test on a century of amateur observations

**Introduction.** SS Cygni is a dwarf nova: a white dwarf drawing gas from a companion star into a
surrounding disc. Every seven weeks or so the disc heats into a bright state, and the star brightens
many times over for one to two weeks. Longer outbursts tend to be followed by longer quiet intervals
(Cannizzo & Mattei 1992). A forecast test asks whether that information holds on data a model has
never seen. We asked whether knowing how long the last outburst lasted improves forecasts of the
next onset beyond what recent quiet intervals tell us. Two accounts predict that it should: a long
outburst drains more of the disc, so the next quiet interval lengthens (H1); or duration tracks a
slowly changing gas supply that recent intervals miss (H2).

**Methods.** We used amateur observers' visual brightness estimates of SS Cyg, reported to the
American Association of Variable Star Observers (AAVSO) since 1910. An algorithm marked each
outburst and estimated when it began and ended. When an outburst ended, we forecast the next onset
as a lognormal distribution of the coming quiet interval. A timing model used the previous quiet
interval and the average of earlier ones; a duration model added the length of the outburst just
completed. We fitted both to 1910–1959, froze them, published the protocol on Zenodo, and only then
opened 1960–2017. Each forecast was scored by the logarithm of the probability it gave to the next
outburst's estimated onset interval: a "working score", since it treats that estimate as the true
onset, in natural-log units (nats), higher being better. The preregistered test required the mean
gain from duration to have a 90% interval, with six-year blocks as units, wholly above zero. We then
rescored the evaluation in other ways, and checked whether ten other dwarf novae had enough
well-timed cycles before 1990 to repeat the test.

**Results.** Longer outbursts predicted longer quiet intervals. Duration raised the working score by
0.0165 nats per forecast (90% interval 0.0049–0.0281; 441 forecasts), meeting the criterion: on a
geometric average, about 1.7% more probability placed on what happened. The gain is small beside the
0.117 nats that recent timing adds to a constant forecast, and it was positive in eight of ten
six-year blocks. Scoring against single estimated onsets gave a similar gain (0.0154 nats).
Redesigned comparisons that timed outbursts directly from the bracketing reports, with a different
baseline model, gave smaller gains (0.0043–0.0075 nats) with intervals spanning zero, as did both
preregistered secondary comparisons (the later years alone; a long/short rule). None of the ten
other stars qualified, chiefly for lack of 40 usable forecasts. In the 1980s, SS Cyg's record
supplied 67 usable forecasts for its 73 confirmed outbursts; the ten candidates together supplied
102 for 485.

**Discussion.** A completed outburst carries information about when the next will begin, beyond what
recent timing provides. Disc depletion (H1) and a changing gas supply (H2) both predict this, so
separating them needs another design.

**Limitations.** The score treats estimated onset intervals as true, so it measures skill for those
estimates; linking it to the physical onset needs a validated observation model. Duration and the
next quiet interval share one estimated end, so measurement error can couple them, and observers may
watch more closely when the star is active. The typical quiet interval drifted between eras;
adjusting for that drift shrank a comparable duration gain by about a quarter. The follow-up checks
reused opened data and are exploratory. A documented data-reading fix preceded the evaluation. The
result concerns one star.

**Conclusion.** A century of amateur observations supported a preregistered test of a long-standing
question: the length of an SS Cygni outburst helps forecast the next. The same frozen-forecast
design suits other long, irregular records of recurrent events, such as eruptions or outbreaks,
wherever coverage can time successive events. Data, code and protocol are public.
