# Independent R2b saved-feature audit

independent saved-feature invariants only; no raw observations, model fits or scores

Status: **passed**; 147,696 assertions; 0 failures.
Verified all feature/source receipt hashes; 6,039 historical anchor links.
Coincident later originals retained only in the audit: 1.

Historical slots whose source emission had a fallback model clock: 91; 8 of these slots contain measured gaps. Their anchors match the immutable scheduled observed anchors in the audit, not an earlier usable model clock. Later-prefix association can be resolved even when the earlier emission's predictor fell back.

| Period | Original point | DF/matched point | DF markable | Jointly markable |
|---|---:|---:|---:|---:|
| development | 330 | 330 | 275 | 273 |
| evaluation | 441 | 440 | 418 | 417 |

No numerical forecast, model or raw-observation code was imported. No fit outputs were read.
Vector consistency does not independently rederive the raw visit construction or establish latent containment.
