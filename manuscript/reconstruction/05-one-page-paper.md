# Step 2: the one-page paper

Reconciled version, 10 November 2026: Claude's cold-read draft merged with Codex's proposal
(`07-one-page-proposal.md`); dispositions in `08-reconciliation.md`. Numbers carry claim bindings.

## The length of an SS Cygni outburst helps forecast the next: a preregistered test on a century of amateur observations

**Introduction.** SS Cygni is a dwarf nova: a white dwarf draws gas from a companion star into a
disc, which every seven weeks or so heats up and brightens the star many times over for a week or
two. Longer outbursts tend to be followed by longer quiet intervals (Cannizzo & Mattei 1992). We
asked whether an outburst's length improves forecasts of when the next begins, beyond what recent
quiet intervals tell us. Two hypotheses predict that it should: a long outburst drains more of the
disc, which then takes longer to refill at a similar supply rate (the *depletion hypothesis*); or
duration tracks a slowly changing gas supply that recent intervals capture incompletely (the *state
hypothesis*).

**Methods.** We used visual brightness estimates of SS Cyg reported by amateur observers to the
American Association of Variable Star Observers (AAVSO) since 1910. An algorithm identified
outbursts and estimated when each began and ended. Once reports confirmed a fade, we forecast the
next onset from reports dated up to then, as a lognormal distribution for the quiet interval
conditioned on the quiet time already elapsed. A timing model used the previous quiet interval and
the mean of up to six earlier ones (log scale); a duration model added log duration. We fitted both
to 1910–1959, froze them, published the protocol on Zenodo, and only then opened 1960–2017. A
forecast's *working score* is the log probability it gave to the window in which the algorithm
placed the next onset (or to no onset yet, if observations ended first), in natural-log units
(nats). The preregistered criterion required the mean gain from duration to have a 90% interval,
over six-year blocks, wholly above zero. Afterwards we rescored with other outburst timings, and a
separately frozen screen asked whether ten other dwarf novae had records before 1990 that could
repeat the test.

**Results.** The duration model forecast longer waits after longer outbursts. Duration raised the
working score by [0.0165]{.C01 .V001} nats per forecast (90% interval
[0.0049]{.C01 .V002}–[0.0281]{.C01 .V003}; [441]{.C01 .V004} forecasts), meeting the criterion: a
[1.7]{.C02}% higher geometric-mean probability for the scored outcomes, beside [0.117]{.C10} nats
from recent timing over a constant forecast. The gain was positive in eight of ten blocks.[]{.C25}
Two redesigned timings gave smaller gains ([0.0075]{.C55 .V009} and [0.0043]{.C55 .V013} nats) with
intervals spanning zero, as did the two preregistered secondaries (later years alone; a
long/short-outburst rule).[]{.C07}[]{.C08} None of the ten other stars passed the screen; nine
yielded fewer than the forty forecasts required.[]{.C68} In the 1980s SS Cyg yielded [67]{.C70}
usable forecasts against [73]{.C70} confirmed outbursts; the ten candidates together, [102]{.C70}
against [485]{.C70}.

**Discussion.** The depletion and state hypotheses both predict this gain; measuring the disc and
gas supply alongside recurrence forecasts could separate them. The test needs a record that times
successive outbursts, and SS Cyg's record does so far more often than the candidates'.

**Limitations.** The working score treats the algorithm's onset windows as true; linking it to
physical onsets needs a validated model of how observations record outbursts. Duration and the next
quiet interval share one estimated end, so measurement error can couple them, and observers may
watch more closely when the star is active. A richer timing model could absorb part of the gain.
Recalibrating after the result for drift in the typical quiet interval reduced an analogous gain.
The follow-up analyses reused opened data and are exploratory. A parser error in an unused field,
exposed at first data access, was repaired before scoring.[]{.C05} Upload and revision dates of
historical reports are unknown. The result concerns one star.

**Conclusion.** A century of amateur observations supported a preregistered test showing that the
length of an SS Cygni outburst improved forecasts of the next. The frozen-forecast design suits
other long, irregular records of recurrent events, such as eruptions or outbreaks. Code, protocols
and aggregate evidence are public.
