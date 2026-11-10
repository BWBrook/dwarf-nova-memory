# G3a pre-access boundary and acquisition review

Codex delegate, 10 November 2026. Barry's authorization relayed by the root
agent is exactly: “yes, approved as proposed. Continue.” It authorizes the ten
named stars' development records, not G3b test records or SS Cyg 2018 onward.
This delegate read G3a v0, the catalogue-only cohort, current acquisition and
qualification APIs, and pinned official VStar source. No target observation,
archive count, light curve, real fit or score was requested or inspected.

## Required acquisition boundaries

- The exclusive split JD2447892.5 is 1990-01-01 00 UT. The provider's native
  `tojd` is treated as inclusive. Set the last requested endpoint strictly
  below the split, as in the existing evaluation adapter's `nextafter` rule;
  reject every returned row outside its own request or at/above the split
  before any summary. Preserve native JD strings and do not convert times.
- Freeze exactly SS Aur, RU Peg, AR And, X Leo, TW Vir, UU Aql, CH UMa,
  DX And, U Gem and IP Peg. Use exact returned identity, AUID consistency
  across responses and unique identity across stars. An independently known
  catalogue AUID map is preferable; otherwise the first strictly date-bounded
  identity response must be frozen before that star's subsequent requests.
  Do not resolve names with an unbounded metadata/count request.
- Date-limited metadata (`data=0`) is supported by the pinned VStar resolver.
  Requesting [JD1,1900-01-01] followed by ten-year inclusive-overlap windows
  through the predecessor of the split stays within the authorized native
  date range. This says nothing about the completeness of ancient records.
- Keep every raw response and request receipt immutable and hashed, including
  failed/truncated responses. Validate redirects before following them: a
  redirect that drops date/identity bounds could perform an unauthorized
  request even if the returned rows are later rejected.

## Pagination is a material contract, not a count equality

The pinned official [VStar CSV2 reader](https://github.com/AAVSO/VStar/blob/6797f17fe106097fd84c1822a24d51021aea9fdd/src/org/aavso/tools/vstar/plugin/ob/src/impl/AIDWebServiceCSV2ObservationSourcePlugin.java)
appends page numbers (lines129–172). Its continuation logic (lines199–259)
uses the presence of `Count`; absence of that element ends pagination.
Consequently, `Count == len(parsed_rows)` is not sufficient evidence that a
response is complete. The legacy local adapters should not supply that
assumption to G3a.

Use the pinned continuation contract with identical frozen date, identity and
selection parameters across pages. Detect repeated pages, no progress,
conflicting repeated observation IDs and a finite page limit. Preserve those
failures rather than report a partial star. A full 50,000-row terminal response
also deserves conservative date bisection or explicit completeness resolution.
Overlap windows intentionally, deduplicate identical obsIDs and fail on
conflicting records. Check completeness on all returned native bands/flags
before selecting visual/V rows. This establishes returned-stream completeness
under the service contract, not complete historical observing opportunities.

The official [bounded request builder and flag mapping](https://github.com/AAVSO/VStar/blob/6797f17fe106097fd84c1822a24d51021aea9fdd/src/org/aavso/tools/vstar/plugin/ob/src/impl/AIDWebServiceObservationSourcePluginBase.java)
set a 50,000-record request maximum, native `fromjd`/`tojd` and `mtype=std`.
The source maps more flags than the project's V-only analysis policy; some
other states are filtered server-side. Preserve native strings and report the
selected-stream scope. Keep `fainterThan=1` as a magnitude lower bound,
missing uncertainty as missing, and `Vis.` separate from Johnson V.

The official [name resolver](https://github.com/AAVSO/VStar/blob/6797f17fe106097fd84c1822a24d51021aea9fdd/src/org/aavso/tools/vstar/input/database/VSXWebServiceStarInfoSource.java)
has both bounded and unbounded overloads. Only the bounded route is relevant
here (lines75–101). Source was read through GitHub's contents API; no VSX
target request was made by the delegate.

## Qualification contracts before duration–gap fitting

`r2_models.fit_ladder` is not a B0-only convergence helper: it fits duration
offsets and B1/B2. Calling it before the qualifying-set freeze would violate
G3a's separation. A dedicated mark-free B0 convergence check must not compute
duration associations, offsets, forecast gains or significance statistics.
All declared starts and boundary/rank/degeneracy rules must be fixed in advance.

`r2b_features.prepare_feature_ledgers` accepts a threshold but hardcodes the
decisive margin at 1 magnitude. X5's own API accepts a margin, while X4 has
separate confirmation constants. Passing catalogue-specific margins only to
X5 would create inconsistent marks, anchors and histories. Either freeze the
common supported margin explicitly or thread a changed margin through every
relevant component with synthetic tests before access.

Morphology rules require fixed plateau duration/level/support and gap handling.
Their output is an operational screen failure, not proof of a subtype. Preserve
all failures; do not retune them to reach six qualified stars or projected
yield. Freeze the qualifying set before any pooled duration fitting.

## A bounded eclipse option

Keeping U Gem and IP Peg for an explicit feasibility guard is defensible.
Passing median and brightest-positive per-observer-night reductions alone is
insufficient: both can select the same eclipse-biased nights. Freeze numerical
gates for matched episode/window/mark agreement, not only identical overall
pass/fail. A two-night faint-confirmation rule must delay issue and availability
to the second qualifying night, never backdate them to the first.

A synthetic phase/dip stress can test this guard on development timestamps
after the implementation freeze. Fix the phase/depth/width/noise envelope and
event/mark-error gates before viewing the records. Include phase offsets,
per-night timing jitter and broader disc-eclipse profiles; a single narrow
white-dwarf eclipse profile is insufficient. Score missed/split episodes,
premature end alerts and bright-span errors against synthetic truth. Failure
is an honest hold, not permission to tune against the same benchmark.

Two primary pre-1990 sources were read for this limited purpose:
[Wood & Crawford (1986)](https://adsabs.harvard.edu/pdf/1986MNRAS.222..645W)
give IP Peg's 0.15820764-day folding period and white-dwarf eclipse-width
range 0.0863–0.0918 in phase, distinguishing it from the wider disc structure.
[Zhang & Robinson (1987)](https://adsabs.harvard.edu/pdf/1987ApJ...321..813Z)
give U Gem's 0.17690618-day ephemeris and describe its bright-spot eclipse.
These support a bounded stress envelope, not a universally valid historical
phase correction. No post-1990 target observations were opened.

Passing this guard is provisional feasibility evidence under the declared
synthetic envelope. It does not prove removal of eclipse errors or settle
G3b's physical-onset/observation assumptions. The root agent owns the final
protocol, acquisition freeze, actual execution and integration.

## Implemented hold-star guard and subsequent source check

At the root agent's request this delegate subsequently implemented
`src/dnmem/g3a_eclipse.py` and its focused synthetic tests. The wrapper
`qualify_eclipse_star` evaluates both reductions with the same ordinary
qualification helper and combines the declared agreement and synthetic gates.
No real cadence or real model was used in the delegate's checks.

Each derived observer/JD-night estimate is released at the **fixed next integer
JD**, with the existing additional .15-day visit closure; its native support
and IDs remain in derived provenance. Releasing a full-night median at its
last observed report would incorrectly assume that no later report will
arrive. A night whose fixed closure reaches the 1990 boundary is omitted.
This is a new hold-star analysis policy, not a native-time transformation.

The ordinary comparison requires 90% one-to-one onset matching within three
days, 90% window-eligibility agreement including unmatched-event penalties,
supported outcome-count differences at most 10% (feature counts also reported), and at least twenty matched
spans with median absolute difference at most one day and 90th percentile at
most two days. Both ordinary qualification results must pass independently.
Faint-end alerts require two observers **and** two distinct nights; a renewed
bright visit clears pending faint evidence. Issue time is the actual later
confirmation, never the first faint time.

Synthetic observations ignore real magnitudes and limits and use all retained
timestamps as positive reports: alternating 12/18-day threshold durations,
60-day spacing, fixed trapezoid crossings, and .22-mag Gaussian noise. The
same noise is shared by the no-eclipse and eclipse records. Sixteen global
phases, widths .10/.25 cycle, depths 1/3 mag, and uniform night-level phase
jitter bounded by 0/.03 cycle give 128 profiles. Both reductions require at
least twenty recovered baseline events, at least 90% recovery of those same
events under eclipses, fewer than 2% early/ambiguous alerts, and absolute
decisive-span errors against known truth within the one/two-day quantiles.
An inadequate baseline returns inconclusive. This conditional positive-report
construction does not certify real limiting behavior or eclipse geometry.

Nine focused unit tests pass, including an entirely invented 1,500-day dense
cadence with 25 recovered events, zero early alerts and full recovery under
one dip profile. This is a code fixture, not an operating-characteristic
estimate. The full envelope awaits the frozen authorized execution.

The root's new acquisition module and runner were inspected read-only.
The implemented inclusive-endpoint/date-limited pagination, cap subdivision,
immutable raw receipts, identity checks and refusal to follow redirects address
the earlier transport concerns. Three integration recommendations were sent
before freeze: abort globally on a scope violation rather than continue to
another target; require unique resolved AUIDs across stars; and include the
used `r2b_scoring.py` in the source freeze. The root owns their disposition.
