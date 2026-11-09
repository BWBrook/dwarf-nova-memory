# Frozen R2a gain-free feature preparation

Freeze: `956d33c`. One execution completed without failures. Only retained, already opened through-2017 SS Cyg caches were read. No forecasting-model fit, score or correlation was computed. Source and output hashes verify.

| Period | Ledger | Rows | Anchors | Marks | Previous gaps | Flux proxies |
|---|---|---:|---:|---:|---:|---:|
| development_1910_1959 | df | 302 | 300 | 288 | 252 | 287 |
| development_1910_1959 | point_at_df | 302 | 302 | 302 | 278 | 287 |
| development_1910_1959 | point_original | 330 | 330 | 330 | 306 | 314 |
| opened_evaluation_1960_2017 | df | 307 | 307 | 304 | 293 | 303 |
| opened_evaluation_1960_2017 | point_at_df | 307 | 307 | 307 | 302 | 303 |
| opened_evaluation_1960_2017 | point_original | 441 | 441 | 441 | 436 | 436 |

Whole opened record: 828 original point rows and 663 matched DF/point rows. The pending-issue policy aborted 165 after threshold-bright closed reports. These are report-based aborts, not identified new physical outbursts. The opened evaluation retains 307 DF issues from 441 original issues, so clock comparisons require the matched 307-row population.

Issued DF delay: median 0.256 days, maximum 8.01 days; 413 of 663 delayed. By actual issue period, development median is zero (143 of 302 delayed), evaluation median 0.720 days (248 of 307 delayed). Scheduled current anchor differs from the preceding-first-postpeak X5 convention in 12 of 651 comparable cases, with maximum absolute difference seven days.

Ledger invariants pass: unique/increasing issues, available anchors/history, positive marks, unique per-feature timing observations, exact last-gap consistency and explicit missingness, nonnegative/support-limited flux proxy, matched issue populations and identical matched-point/DF proxy dictionaries. These are structural checks, not independent evidence for latent containment or predictive performance.

DF joint anchor+previous-gap+mark availability is 251 development and 292 evaluation rows; joint anchor+previous-gap+flux is 250 and 292. Available DF proxies have median seven balanced-night points and median actual support 6.8472/5.75 days by period. The proxy is restricted observed bright-span threshold excess, not complete outburst/quiescent-subtracted/bolometric fluence.

No source or policy was changed after observing these counts. Full individual feature ledgers remain ignored and unreleased.
