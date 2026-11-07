# A04g fresh validation of X4: proposed specification

Claude, 8 November 2026. Status: **proposed**. Codex completes it in writing,
implements the benchmark changes and freezes before drawing validation seeds,
as for A04e. The evidence is in the
[A04f memo](../audits/2026-11-08-a04f-x3-failure-review-x4.md). Unchanged
A04e rules apply unless amended here.

## Candidate and references

- **Candidate:** X4, `src/dnmem/extract_x4.py`, `DEFINITION_VERSION =
  "a04f-x4-v1"`, at the commit that adds it, byte-identical through
  validation. Episodes come from `x4_episodes`, operational confirmations
  from `causal_confirmations`.
- **References:** X3 (with the A04e causal wrapper), X1 and X2, unchanged.
- **Development history.** X4's one tuned constant (SYSTEMATIC = 0.05) was
  chosen on Claude's smooth training family. Its two structural changes
  respond to failure modes Claude diagnosed on the A04e v2 generator, using
  seeds in the `a04f-claude-*` namespaces. A v2 pass is therefore weaker
  evidence than a pass on a family Claude has not seen.

## Benchmarks

1. **v3 (new, decisive).** A fresh generator author who sees neither X4, v2
   nor Claude's training code builds a different pulse family. One option
   is empirical templates: densely observed open-era outbursts, normalised
   and warped to the drawn duration. That brings real curvature,
   low-amplitude events and plateau slopes with it. Codex chooses the
   family. It must pass the seven A04e morphology checks and the diversity
   checks below.
2. **v2 (decisive)**, unchanged and with fresh seeds.
3. **Cadence.**
   - **Random phase** is decisive.
   - **A diversity-preserving state arm** replaces the A04e donor rule as
     decisive. One way to build it: map each synthetic outburst, day by day
     from onset, onto one real outburst within ±60 d, and fill quiescent days
     from the nearest real quiescent day. That keeps the real rotating cast
     of observers. Codex chooses the rule; the qualification below is the
     gate.
   - **The A04e state arm** stays as a reported stress test.
4. **Observer-diversity qualification** for every decisive family and cadence
   arm, using `scripts/a04f_develop_x4.py --diversity` or an equivalent
   operator. For each era, the median number of distinct bright observers per
   X1 episode spanning at least 4 d must lie within 15% of the real value.
   The share of such episodes with two or fewer bright observers must lie
   within 0.05 of the real share. Real values (1910–1929, 1930–1949,
   1950–1959): medians 14.5, 16 and 14; shares 0.021, 0.101 and 0.118.
5. **Gross-error arm (decisive for the false-signal criteria only).** Inject
   wrong-star reports into quiescent observer visits at five times the real
   rate, 0.32% instead of 0.064% (A04f §2). Each report lasts 1–3 nights for
   the same observer, at a magnitude drawn uniformly from 8.5–9.8. Both the
   retrospective false-episode rate and the causal unsafe rate must stay
   below 0.2 per year. This arm targets X4's single-observer rule.
6. Diagnostics as in A04e: persistent offsets, the v1 template, the 1900s,
   the copula alternative and the 9.5/10.5 thresholds.

## Seeds and size

The seed base is `a04g-validation|` followed by the full freeze commit hash.
Use 400 histories per decisive cell (independent null and structured
zero-mark controls, three eras, decisive families and arms) and 200 for each
diagnostic. If cost forces a cut, keep v3 and the diversity-preserving arm at
400 and cut v2 first.

## Criteria

The A04e criteria apply unchanged in every decisive cell, with whole-interval
Monte Carlo decisions:

- effective coverage of at least 90% at both boundaries;
- short-event completeness of at least 95% outside March–May;
- fewer than 0.2 retrospective false episodes per year, and fewer than 0.2
  causal false-plus-ambiguous emissions per year;
- absolute paired null bias below 0.02 under the selected rule;
- first-emission premature rate below 2% and missing rate below 5%.

The operational criteria use X4's `causal_confirmations`. Codex
re-implements that rule independently from its docstring and from this
specification. Any disagreement with the reference implementation on a
validation history is a harness finding to resolve before outcomes are
read. D and Q use `onset_t` and `end_t`. Report conditional coverage, point
bias and RMSE, widths, unconfirmed, missed and split shares, and the share of
episodes confirmed by the single-observer rule.

## Decision

A pass in every decisive cell qualifies X4 for retrospective open-era
extraction (A05). It does not freeze the A10 forecast pipeline: prefix-causal
features and reporting latency remain A10 work. A failure is retained as it
stands. Any later repair needs a new specification, new development seeds
and a benchmark family its author has not seen.
