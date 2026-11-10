# Can an outburst help predict the next one?

Barry W. Brook (University of Tasmania), with Claude Opus 5.5 (Anthropic) and GPT-6 Codex (OpenAI). Draft of 2026-11-10; a summary of <https://github.com/BWBrook/dwarf-nova-memory>.

## A century of observations, a small forecasting gain

SS Cygni is a pair of stars in which a white dwarf pulls gas from its companion into a disc.
The disc flares irregularly, then fades. Amateur astronomers have followed these outbursts by
eye for more than a century. Short and long flares tend to alternate. Earlier work found that
longer flares are followed by longer quiet spells; our question was whether knowing a flare's
length improves a forecast beyond what recent quiet spells already tell us.

We fitted two forecasters using 1910–1959 observations from the American Association of Variable
Star Observers (AAVSO). Both knew the recent timing history; one also knew the completed flare's
length. We froze the rules, published the protocol and then opened 1960–2017. The duration-aware
forecast gained [0.0165]{.C01 .V001} nats of log score per forecast (90% interval
[0.0049]{.C01 .V002} to [0.0281]{.C01 .V003}), over [441]{.C01 .V004} forecasts: on a geometric
average, about [1.7]{.C02}% more probability given to the outcomes as scored. This met the success
rule set beforehand. The gain is small, but it is a held-out test, not a fit to known data.

**The qualification matters.** We scored probabilities assigned to intervals estimated by the
flare-finding software. Those intervals are not known bounds on the true onset. The gain is
therefore a result for this *working score*, not yet a clean measure of predicting the physical
start. A formatting problem also required a documented reader repair after first access; it
changed no observation or forecasting rule[]{.C05}. The later years alone and the frozen
long/short rule were inconclusive[]{.C07}[]{.C08}.

<div id="figures"></div>

*Figure. The original working-score gain and its interval are above zero. The later-period and
long/short comparisons are inconclusive. None identifies physical memory.*

## What survived closer checking

The dates when people looked, the software's estimated start and end, and changes in the star's
typical quiet interval can all affect the score. An error in the estimated end simultaneously
makes one flare longer and the following quiet spell shorter. Observers may also watch harder
when the star is active.

After external review we kept the frozen result and tested different measurements. Scoring at a
single estimated start still favoured duration[]{.C44}. New comparisons used report-based onset
windows, different timing models and a clock starting at an observed faint report rather than an
estimated end. Their duration gains were positive but their intervals included zero[]{.C55}.
Adjustments for changing typical gaps also reduced an analogous gain. These checks were designed
after the original result: they expose its limits, and cannot count as fresh confirmation.

\newpage

## Could we test other stars?

We froze a feasibility screen before opening the early visual records of [10]{.C68 .V030}
other dwarf novae. [None]{.C68} passed every rule for a later forecasting test. Under the same
rules, SS Cyg's 1980s record gave [67]{.C70} usable forecasts for [73]{.C70} confirmed outbursts;
the ten candidates together gave [102]{.C70} for [485]{.C70}. Their largest loss was missing
coverage of the previous quiet gap. Most of these stars are fainter than SS Cyg between outbursts,
which makes continuous coverage by eye harder. A long bright-run
flag excluded SS Aur; inspecting that flag found separated bright-report groups, not evidence
for one continuous plateau or a particular cause[]{.C70}[]{.C71}.

The measured early-record rates fell well short of the planned sample. We stopped this expansion
without fitting duration effects for these stars or opening their later test records. This says
what the chosen rules could support, not that other dwarf novae lack the effect or that another
archive or method could never work.

## What we can say

Measured flare length improved the original frozen working score for SS Cyg, a test that rests on
how closely amateur observers have watched this one star for a century. The observation
model, baseline and measurement choices limit the inference. We have neither identified a
physical memory mechanism nor demonstrated a general forecasting gain across dwarf novae.
SS Cyg's records from 2018 onward and the candidates' records from 1990 onward remain closed.

## How this work was done

Barry Brook set the direction and access boundaries and decides release. Claude reviewed the
literature, built the flare finder, drafted the first versions and reviewed these. Codex built and
ran the forecasts, independently checked the results and later diagnostics, and prepared these
second drafts. GPT-6 Pro supplied the initial ideas
and an external review. The public repository preserves the frozen calculation, corrections,
failed transfer and evidence behind each claim. These are second drafts for review.

## Sources

@cannizzo1992LongtermBehaviorSS analysed the historical duration–gap relation;
@cannizzo1993AccretionDiskLimit modelled the disc cycle. The protocol is archived at
<https://doi.org/10.5281/zenodo.24053338>.
