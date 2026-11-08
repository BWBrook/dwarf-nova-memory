# A10g: sealed evaluation implemented and rehearsed

Codex, 8 November 2026. Final source freeze
`fc409738222ded5a9bf78288c969e956b59d23f4`. The sealed evaluation is ready
for Barry's timestamp/access decision. **The real 1960–2017 archive remains
unopened; 2018 onward remains reserved.** No protocol has been deposited on
Zenodo and no evaluation authorization file exists.

The full synthetic native-format 58-year rehearsal completed every planned
diagnostic. An independent checker reproduces all 2,230 variant score rows,
the primary interval, routing and source identities. All 342 tests, the seed
validator and staged secrets scan pass. CI on the exact final source freeze
passes on [Python 3.11–3.13](https://github.com/BWBrook/dwarf-nova-memory/actions/runs/42479956883), with a [clean secrets scan](https://github.com/BWBrook/dwarf-nova-memory/actions/runs/42479956829), including the platform that exposed a secondary
numerical defect during development.

## A10f review

The original calibration counts reproduce, but three interpretations were
too strong. D024 and the [amended protocol](../protocols/a10g-sealed-evaluation-v1.md)
record these corrections before access:

- Median observed issue age and previous gap do not determine the sign of
  end-error coupling; the relevant joint errors/current gaps are unknown.
  The existing counterexample and mixed-sign null fits preclude a general
  sign guarantee.
- Five likelihood-ratio exceedances among 220 null case arms occur on four
  paired base histories. Shared seeds make an iid-binomial interval for the
  pooled count inappropriate. The finite screen and its uncertainty remain.
- `(11/21)/(2/31)=8.12` is an exploratory conditional simulator frequency
  ratio. It is not posterior model odds or a Bayes factor.

The primary six-year-cluster forecast-gain test is unchanged. Sign
confirmation and comparison with the fixed numerical reference gain are
separate fields: a positive result can also exclude that reference magnitude.
The reference is an estimated simulation mean, not a physical partial-r
threshold. Selected resolved-onset CDF deciles are descriptive; predictive
coverage instead has lower/upper bounds over all scored outcomes, including
right censoring.

## Implemented execution

`scripts/a10g_evaluation.py` has distinct rehearsal/live modes. Live mode
requires a committed, pushed verbatim authorization from Barry tied to the
source freeze, protocol hash, exact parameter hash and timestamp choice.
The authorization check occurs before transport or native opening. Tests
verify that missing authority cannot create an output directory or call the
transport. The access decision remains pending.

The native adapter preserves time strings, metadata and raw response hashes.
It requests bounded calendar-year windows, retains bytes/receipts before
parsing, bisects capped responses and rejects out-of-scope or conflicting
records. The last requested endpoint is strictly before 2018. Analysis uses
visual-band, V-validated rows; synthetic modern bands/flags, limits, unknown
fields, duplicate observations and empty responses have fixtures. No time
conversion is inferred from submission-format labels.

Candidate and independently implemented reference ledgers AND outcome
evidence must match at both delays before any score. A mismatch hard-stops;
there is no candidate-authority or mismatch-deletion substitute. The primary
file is saved before secondary diagnostics. Six frozen variants, fallback
zeros, era summaries, descriptive calibration and block inventories follow
the same predeclared populations. The simultaneous current/lagged association
fit is genuinely joint, distinct from the older pair of separate offset fits.
All S1 results remain conditional working-model association diagnostics.

Every original A10d source identity (26 files) and the fitted parameter bytes
are unchanged. Parameter SHA-256:
`ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3`.
The final amended protocol has SHA-256
`ddfa46d14f35e213690e0d5e7d03a7a635a71b637d024a810d2f192929789232`.

## Preserved rehearsals and numerical repair

All rows below are **synthetic**, using new seeds derived from each source
freeze. Score sign/significance was never an acceptance criterion. These
are pipeline checks, not another power study or astronomical results.

| Freeze | Scored | Gain, nats | Two-sided 90% interval | Max independent score error | S1 status |
|---|---:|---:|---|---:|---|
| `79b5eae` | 397 | -0.013884 | [-0.039921, 0.012152] | 9.24e-14 | intercept constrained optimization failed: ABNORMAL:  |
| `bfb2bc6` | 384 | -0.016164 | [-0.048045, 0.015717] | 4.17e-14 | current_duration constrained optimization failed: ABNORMAL:  |
| `fc40973` | 377 | 0.015118 | [-0.003856, 0.034092] | 6.13e-14 | complete |

The first failure arose while profiling unused R0/M0 models. Restricting
profiling to required models removed that work, but the second seed exposed
the same finite-difference line-search failure in a required joint profile.
Python 3.11 CI independently exposed it in M2 profiling. Finite interior
optima agreed with independent numerical methods; accepting `ABNORMAL`
optimizer statuses would have weakened the checks.

The final repair changes only evaluation diagnostics: one-dimensional
nuisance searches use bounded scalar minimization with both closed endpoints;
larger nuisance searches use three-point gradients. The exact tolerances
and strict success/objective/nesting checks are frozen in the protocol and
source. No primary estimator or forecast parameter changed. Analytic
interior/boundary fixtures and failure-injection tests pass. Both preserved
streams now complete S1; previously successful support endpoints reproduce
exactly locally. [Numerical smoke evidence](../../data/provenance/a10g_profile_policy_smoke.json)
is retained. The new final rehearsal has 345 joint-valid rows, rank two,
three successful joint starts and no failed starts; every secondary completes.

The [independent final audit](../../data/provenance/a10g_rehearsal_fc40973/audit.json),
[compact summary](../../data/provenance/a10g_rehearsal_fc40973/summary.json),
[derived receipt](../../data/provenance/a10g_rehearsal_fc40973/receipt.json)
and [archive manifest](../../data/provenance/a10g_rehearsal_fc40973/archive.json)
are committed. The full 137-file run, 12,445,838 bytes uncompressed, is retained
outside Git with local/remote member verification; archive SHA-256 is
`3e91ba13b34bab5eddf4f30ec030d6a6eabdb76d06436a98736b09e58504c922`.
Both earlier attempts and their failures remain in the same project archive
with compact public records; they have not been overwritten or relabeled.

## Independence, reproduction and limits

Codex (OpenAI, GPT-6) integrated this turn. Separate bounded delegates
implemented the native adapter/fixtures and numerical checker
(`gpt-5.6-luna`), and independently reviewed A10f and the profiling failure
(`gpt-5.6-sol`). The checker uses separate scalar likelihood/statistic code,
not the candidate forecast or prefix implementation. The methodological
review used retained synthetic outputs and already-consumed pre-1960
artifacts. Input/code separation supplies the evidence of independence;
agent identity alone does not.

From a clean checkout containing the final frozen source bytes, with the
hash-verified retained anonymous pre-1960 benchmark cache available:

```bash
uv run --frozen --extra analysis python scripts/a10g_evaluation.py --mode rehearsal --freeze-commit fc409738222ded5a9bf78288c969e956b59d23f4 --output outputs/a10g_reproduction
python3 scripts/check_a10g_evaluation.py --directory outputs/a10g_reproduction --output outputs/a10g_reproduction_audit.json
```

The live modern archive response contract remains untested until authorized
access. A contract/concordance failure must be retained and would consume
untouched status; an independently reviewed repair cannot restore it.
The synthetic rehearsal verifies implementation and chronology, not universal
coverage calibration, operational availability, physical memory or high power.
The finite simulation screen, 85% injected-case interval containment, modest
power and CM92/development exposure remain material limitations. The outcome
ledger also records incidental 1997 documentation examples; no universal
outcome-ignorance claim is made.

## Reviewable next action

A protocol-only package (697,603 bytes, 208 files) and Zenodo metadata draft
are prepared, not deposited. Package SHA-256:
`9cc7c7e7203619fbb4322f43b9af6e7207b59644367b06434673be555b9cd357`.
It contains frozen code/protocols, synthetic fixtures, existing fitted
parameters and rehearsal QA; it contains no raw observations or observer
identities. Its [manifest](../../data/provenance/a10g_protocol_package/package-receipt.json),
[contents note](../../data/provenance/a10g_protocol_package/PACKAGE-README.md)
and [metadata draft](../../data/provenance/a10g_protocol_package/zenodo-metadata-draft.json)
are reviewable. Barry's creator name/ORCID were checked against Crossref.

Recommendation: deposit this frozen protocol on Zenodo for an external
project-time timestamp, then authorize the single sealed 1960–2017 run.
A Git tag alone is the alternative. Neither choice changes the primary test
or opens 2018 onward. Until Barry explicitly chooses, live transport remains
closed. The July 2026 AAVSO terms review and eventual observer-credit tasks
are recorded in the data/provenance document; no external contact was made.

Next: Barry — choose the timestamp route and authorize, or keep the block closed.
