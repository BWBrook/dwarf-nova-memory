# A10e: single pre-1960 development fit after the accepted synthetic screen

Codex, 8 November 2026. Barry has explicitly selected “360-trial screen with
observed rate ≤5% (recommended)”. The A10d screen passed; this resolves D021's
pending interpretation and authorizes the first real development fit. It does
not certify population size ≤5%. D018 remains held-out forecast gain.

Freeze this adapter and likelihood-profile code before opening native data.
Every forecasting, feature, extraction and benchmark source byte listed in the
A10d receipt must still match generation freeze `8f5df44`. The new code adds
source/access guards, output collection and diagnostic likelihood profiles;
it must not change the frozen estimator, starts or routing.

Use only the twelve existing receipt-verified acquisitions whose hashes match
the frozen anonymous cache. Reject quarantine paths, unexpected acquisitions,
changed bytes, or any row outside JD 2413559.5 through 2436934.0. There are no
new requests. Preserve native JD and band/quality handling. Build prefixes
using pre-1910 context, then retain issue times in [2418672.5,2436934.5), at
both 0 and 2 d delays; evidence is censored at the latter cutoff using only
those native rows. Compare candidate and independent-reference ledgers and
evidence exactly at both delays before fitting.

Fit each of the six A10d variants once, retaining every serialized model,
training transform, convergence diagnostic and route/evidence count. Keep
common fallback zeros; exclude only the existing ambiguous-survival evidence.
The saved score differences are **in-sample development likelihood gains**,
not out-of-sample skill. No real Pearson correlation is needed. Persist all
models and their hashes before profile diagnostics. A diagnostic failure must
not erase or silently refit a completed model.

Profiles use the same likelihood and frozen transforms. For M0/M2/R0, profile
one parameter while reoptimizing other fitted nuisance parameters within the
same bounds. For M3/P3, hold M2 fixed as the staged estimator requires, and
profile only its mark offsets (reoptimize another mark offset for the type
sensitivity). Use the chi-square(1) 95% likelihood-ratio support cutoff 3.841.
These are diagnostic likelihood-support intervals: dependence and measurement
uncertainty have not been calibrated for them; mark profiles additionally
condition on estimated M2 nuisance values. Do not present them as validated
confidence intervals. Preserve boundary clipping, unidentifiability and all
optimization failures. Profiles never change frozen parameters.

Record this execution in the outcome-access ledger as the first real
outburst-duration/following-gap fit. Publish the parameter file with its hash,
compact profiles and likelihood summaries; retain bulky ledgers/evidence
outside Git. Change nothing in the forecasting system after seeing the fit.
A failed fit permits only additional deterministic starts, documented.

No observation, count or coverage summary from 1960 onward is authorized.
1960–2017 access still requires Barry's explicit later go-ahead after an
evaluation protocol commit; 2018 onward remains reserved. A development
coefficient at exactly zero implies identical later M3/M2 forecasts under
this frozen system and cannot produce confirmation; report that outcome.
