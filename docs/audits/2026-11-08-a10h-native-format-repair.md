# A10h: native-format repair after a pre-primary failure

Codex, 8 November 2026. This memo is committed before the repaired live
continuation. D025 authorized Zenodo first, then the single 1960–2017 run.
The exact protocol was published as [10.5281/zenodo.24053338](https://doi.org/10.5281/zenodo.24053338)
at 12:34:47 UTC; public package bytes match the approved SHA-256. Authority
`6e26eba` was pushed before acquisition at 12:38:28 UTC.

The first attempt stopped at 12:39:51 UTC on literal `None` in a native
uncertainty field. No ledger or primary score file was written. Native bytes,
receipts and log remain retained, including the failing response. The
[failed receipt](../../data/provenance/a10h_failed_fc40973/receipt.json) and
[internal archive manifest](../../data/provenance/a10h_failed_fc40973/archive.json)
record it. The raw archive is not released. The evaluation block's untouched
status is consumed; a repair cannot restore it.

The narrow change accepts exact blank or exact `None` as missing uncertainty
metadata and preserves the raw string. Zero stays numeric zero; nonfinite,
negative, malformed and padded strings still fail. No observation is dropped
or modified. The missing-value interpretation is inferred from the field's
literal representation, rather than a pinned provider schema statement.

An independent methodological reviewer inspected the code path and synthetic
fixtures: uncertainty is unused by analysis selection, X4, causal emissions,
both feature/evidence implementations, routing or scores. The persistent
regression parses otherwise identical synthetic inputs with blank versus
`None`, and verifies identical forecasts, outcomes and frozen model scores.
Native adapter owner and methodological reviewer inspected no real magnitudes,
outcomes, event counts or coverage summaries. Those did not inform the fix.

Repair freeze `5e39aeb772c427ef29671c1a9c80b22c05519b58` changes only the
adapter validation and synthetic tests; all 26 original forecasting sources,
parameter bytes and protocol bytes remain unchanged. The complete 344-test
suite, validator, staged scan and [Python 3.11–3.13 CI](https://github.com/BWBrook/dwarf-nova-memory/actions/runs/42481798983)
pass. A new commit-seeded full synthetic rehearsal completes all secondaries,
with [independent numerical audit](../../data/provenance/a10g_rehearsal_5e39aeb/audit.json)
passing every score/interval and max score difference2.94e-14.

The existing protocol explicitly permits a minimal outcome-independent,
independently reviewed repair after a retained contract failure. D026 exercises
that clause; it does not retune the model, target population or confirmatory
test. [Updated authority](../../coordination/evaluation_access.json) records
both source freezes, the original approval/DOI, failed attempt and consumed
status. It is committed/pushed before continuation. The original DOI timestamps
the original protocol; it is not claimed to timestamp this later repair.

The next execution is the frozen test after a post-access native-format repair.
A resulting primary still requires exact independent ledger/evidence concordance
and numerical verification. No primary result currently exists. Data from
2018 onward remain closed; no raw-data or manuscript release is authorized.
