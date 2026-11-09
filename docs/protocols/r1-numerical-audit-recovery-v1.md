# R1 numerical-audit recovery, before structured000 is scored

Codex, 9 November 2026. The original `0594146` grid remains unchanged while
running. Its structured000 task stopped in preparation, before model fitting
or dose scoring, because its ledger was not bit-for-bit equal to the retained
Linux A10d ledger. Preserve that failure and the initial batch receipt.

## Diagnosis

All 735 feature rows have identical IDs, event/issue times, boundaries, marks,
previous gaps, coverage and eligibility fields. Eight `earlier_gaps` entries
carry two distinct `math.log` results differing by exactly one adjacent float
(4.440892098500626e−16). Their raw gaps and onset/end boundaries occur exactly
in other retained features. High-precision Decimal logarithms place one retained
value and one regenerated value at the correctly rounded answer: this is
platform-dependent log evaluation, not lost JSON precision or a scientific
generation mismatch.

The current regeneration also agrees bit-for-bit with the unchanged original
`development_stream` generator path, including block metadata and the trimmed
truth subset. A10d did not retain historical raw synthetic rows, so this is
not a direct comparison with their historical row bytes. The complete gain-free
diagnosis and source hashes are retained in
`outputs/r1_structured000_diagnosis/`.

## Bounded comparison repair and same-seed recovery

After the initial batch finishes and its hashes are preserved, replace only
the overstrict retained-ledger comparison:

- Require identical row counts, dictionary keys, every other feature value and type,
  and `earlier_gaps` list types and lengths.
- Permit an unequal history entry only when both values are finite floats and
  `math.nextafter(reference, regenerated) == regenerated`. Report every accepted
  difference. Reject two steps, nonfinite values, schema changes, or any changed
  time, raw gap, mark, membership or eligibility field.
- Do not round or replace predictor values. The locally generated values still
  enter the unchanged models. Retained-parameter replay retains its existing
  numerical check; refit differences stay separate.
- Commit the comparison-only repair and regression tests before rerunning the
  same structured000 seed in a new output directory. Verify that every other
  generation, anchor, fitting, jitter, scoring and summary function is unchanged
  from `0594146`. No seed replacement, data selection or model/score tuning.
- Combine the 79 successful initial histories and the one recovered history
  only after task identities, seed bases, input/configuration and unchanged
  scientific sources agree. Retain both execution receipts and the pre-scoring
  failure; the final aggregate must contain all original 80 tasks exactly once.

This is a disclosed numerical audit amendment after the initial batch started,
before the failed history's dose gains exist. It changes an equality check,
not an observation, fit, score or inferential rule. The R1 conclusions remain
exploratory and bounded by the original diagnostic protocol.
