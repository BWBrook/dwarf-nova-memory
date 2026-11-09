# R1d/e: illustrative forecasts and finite simulation evidence

The original date selector and feature/outcome hashes reproduce. At the prefix point end, the conditional median remaining wait is 27.5749 d for M2 and 26.7726 d for M3. Probability of onset within 30 d is 57.6727% and 60.2765%. These are one selected illustration, not an average effect, endpoint-integrated forecast, or utility result.

| Family | Setting | Mean gain | MCSE of mean | Confirmations | Exact 95% rate interval | Maximum history mean |
|---|---|---:|---:|---:|---|---:|
| v2-phase | adaptive | -0.00082186 | 0.00041635 | 0/40 | [0.0000, 0.0881] | 0.00313581 |
| v2-phase | alternative | 0.00451956 | 0.00136927 | 11/40 | [0.1460, 0.4389] | 0.02768769 |
| v2-phase | gross | 0.00045646 | 0.00042783 | 2/40 | [0.0061, 0.1692] | 0.00865115 |
| v2-phase | null | -0.00043767 | 0.00031418 | 0/40 | [0.0000, 0.0881] | 0.00403167 |
| v2-phase | offset | -0.00041774 | 0.00028527 | 0/40 | [0.0000, 0.0881] | 0.00241834 |
| v2-phase | slow_090 | 0.00190619 | 0.00119244 | 6/40 | [0.0571, 0.2984] | 0.02069503 |
| v2-phase | slow_098 | 0.00499160 | 0.00153568 | 7/40 | [0.0734, 0.3278] | 0.03956752 |
| v2-phase | structured | -0.00184642 | 0.00074589 | 1/40 | [0.0006, 0.1316] | 0.00435477 |
| v4-phase | alternative | 0.00150618 | 0.00141466 | 6/20 | [0.1189, 0.5428] | 0.00939301 |
| v4-phase | null | -0.00092086 | 0.00060478 | 0/20 | [0.0000, 0.1684] | 0.00279810 |

The real mean exceeds every scenario mean but does not exceed every individual synthetic-history mean. Scenario averages and maxima answer different questions. Confirmation-rate intervals are two-sided exact 95% Clopper–Pearson intervals, independently inverted from binomial tails; the MCSE column is for the mean gain, not for the confirmation rate.

Six-year reference coverage: null overall 37/40, interior 24/27; alternative overall 34/40, interior 31/37. Overall counts include exact-zero identity histories. Joint-Monte-Carlo coverage uses six finite matched references, not known exact expected gains. These screens do not certify a true 5% error rate or a population coverage guarantee.

All 480 committed comparison rows and A10n's numerical aggregates reproduce within tolerance. The proper real six-year block origin is JD 2436934.5; replacing A10n's JD 2436934.0 origin changes 0 of 441 assignments in this record. This check uses the proper origin throughout.

Status: passed; 0 discrepancies. Inputs are receipt-verified and hashed in summary.json. No real per-issuance table, model refit, raw observations, new star data or protected-block information is emitted.
