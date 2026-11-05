# A focused astrophysical primer

This document gives the minimum physical vocabulary for the proposed statistical
work. It is not a replacement for a domain review. Begin with
[Hameury's DIM review](https://arxiv.org/abs/1910.01852), then the more recent
[Scaringi, Knigge & de Martino “Unreview”](https://doi.org/10.1007/s11214-026-01290-x).
The latter is useful specifically for distinguishing established phenomenology
from open questions in accretion physics.

## The system and the event

A cataclysmic variable is a close interacting binary containing an accreting white
dwarf. In the disc-forming systems relevant here, material transferred by the
companion passes through an accretion disc. Dwarf-nova brightening is associated
with changes in the disc's thermal/accretion state; it should not be described
as the thermonuclear explosion of a classical nova. The disc-instability framework
is useful, but practical models involve additional effects and unresolved
transport physics.

Sources: [Coppejans et al. 2016, introduction](https://doi.org/10.1093/mnras/stv2921);
[Hameury 2020](https://arxiv.org/abs/1910.01852).

For this project, distinguish **mass supply from the companion**, **mass accretion
through the disc**, and **observed optical brightness**. They are connected but
not interchangeable measurements. Photometry is a projection of a spatially
structured, evolving system. A statistical state variable should therefore be
called “activity state” unless independent evidence identifies it with a
particular physical quantity.

## Three meanings of memory

1. **Renewal age:** the probability of an event changes with time since the last
   event. This can occur even when successive waiting times are independent.
2. **Predictive dependence:** past intervals or outburst marks improve a forecast
   beyond that renewal baseline.
3. **Physical persistence:** some property of the disc or companion carries an
   influence across events. Several physical mechanisms could produce the same
   observational predictive dependence.

These are analytical distinctions adopted for this project. The first paper can
test the second without uniquely identifying the third. It should not use an
exponential waiting-time baseline as the only meaning of “no memory”.

## Why subclasses matter

Ordinary U Gem/SS Cyg-like activity, SU UMa supercycles and superoutbursts, WZ Sge
long recurrence and Z Cam standstills pose different event-definition problems.
This motivates a restricted initial cohort and separate challenge cases rather
than pooling every brightening as the same event. Classification itself must
be verified for each target and can be complicated by changes in behaviour.

Sources: [Hameury 2020](https://arxiv.org/abs/1910.01852);
[the ZTF CV classification study, introduction](https://academic.oup.com/mnras/article/527/3/8633/7459939).

## The physical questions behind the statistical alternatives

If marks help predict recurrence, possibilities include retained disc structure,
changing supply, and the mark acting as a measurement of the current accretion
state. If timing-state models explain the gain, that motivates work on slower
state changes, but does not establish their cause. If neither helps on future
data, the inference may be weak predictability, insufficient information, or
unsuitable observation coverage; simulations distinguish some of these.

The 2026 “Unreview” identifies unresolved issues in angular-momentum transport,
neutral discs, winds and other aspects of accretion. It supports the broader
physical relevance of well-characterized variability. It does **not** establish
that this particular forecasting question is novel or that the proposed data can
discriminate those mechanisms.

Source: [Scaringi et al. 2026](https://doi.org/10.1007/s11214-026-01290-x).

## Useful reading order

Read one modern physical review, the closest historical SS Cyg recurrence study,
the multi-system Ak et al. study, then the two distinct 2016 catalogues. Read the
recent behaviour/forecast papers flagged in `02-literature-review.md` before
deciding on novelty. Finally inspect the actual archive format and a raw light
curve: many methodological choices become concrete only then.

## What to ask an astronomer after the pilot

Are the selected targets a coherent class for this question? Are the event ends
operationally meaningful? Which known behaviour changes should be represented?
Would band-specific marks reasonably track the intended physical feature? Are
the competing activity models physically plausible? What prior papers or
instrumental artefacts would a specialist immediately recognise? Bring the
actual plots and audit, not just the project idea.
