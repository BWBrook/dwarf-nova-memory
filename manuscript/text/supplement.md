# Technical record: corrections and reproduction

<div id="authors"></div>

This record accompanies the article, whose text and appendices hold the methods and results. It
lists the analyses and readings that review superseded, and the commands that reproduce the
evidence. Every quoted number is linked to the claims ledger, `manuscript/claims.csv`, and
`manuscript/estimands.md` states what each analysis supports. Labels such as A10i and D026 refer to
the project record in `docs/audits/` and `coordination/decisions.md`.

## 1 Analyses superseded during review

Each entry records what was replaced, who found the problem, and where the record is.

| Earlier analysis or statement | Problem and finder | Replacement | Record |
|---|---|---|---|
| Duration predicts the following onset-to-onset cycle | Shared term with the cycle (CM92); confirmed in the A01 audit | Quiet-gap target only | A01 memo |
| Extractors X1, X2, X3 | Failed synthetic qualification (Codex and Claude reviews) | X4, qualified at magnitude 10 only | A04e–A04i |
| Unrestricted duration coefficient on all routes | End-time coupling and route mixing (Claude, D020) | $\beta \ge 0$, matched routing, local gap level | D020, D021 |
| Joint refit of M3 with M2 | Training loss not matched to deployment (Codex, D021) | Mark offsets fitted with M2 fixed | D021 |
| Candidate-authority concordance rule | Allowed mismatch deletion (Codex, D024) | Exact two-implementation concordance or abort | D024 |
| Strict parser for the uncertainty field | Failed on `None` after access (execution) | Exact-token repair, reviewed and rehearsed | D026 |

**Interpretation corrections checked in A10k.** Codex's independent audit narrowed several readings
from Claude's A10j review before the products were drafted. Claude accepted all of them (D030).

| Earlier reading | Corrected scope | Evidence |
|---|---|---|
| Global recentering isolates drift-free information | It defines an approximately additive descriptive score contrast; within-period drift remains possible |[]{.C20} |
| All predictive information is in outburst type | A class indicator has greater in-sample likelihood; within-class equivalence was not tested |[]{.C21} |
| The entire frozen class rule cannot shorten short-event forecasts | That restriction concerns its type component; the within-class component can shorten them |[]{.C08}[]{.C22} |
| Negative lag excludes a dominant slow driver | Alternation and a slow component can coexist; no mechanism allocation follows |[]{.C12}[]{.C13}[]{.C24} |
| A rounded SE boundary is a safe inclusive margin | The decision is strict; the rescaling boundary is exclusive and does not validate dependence |[]{.C25} |
| Frozen M2 forecasts are 4.6% too long | The best level shift reduces the untruncated clock scale by 4.57%; that is not a remaining-wait bias |[]{.C20} |
| The gap after a long outburst is about five days longer | A 14% clock-scale ratio; days need an explicitly chosen reference scale |[]{.C21} |

The original exploratory numbers are retained. These corrections do not alter the frozen primary
comparison, its outcomes or the predeclared class-rule result.

**Novelty wording narrowed in A10l.** The draft framing called this the first preregistered held-out
forecast test of dwarf-nova recurrence. The refreshed search found a held-out point-forecast study
of V363 Lyr by Grigorievskiy and colleagues, in the 2014 ITISE proceedings (pp. 520–531), with a single test
outburst. The claim now specifies preregistered, probabilistic and duration-based[]{.C41}.

**Draft corrections in A10m.** Semantic review corrected an overstatement of complete flare
recovery, distinguished an unseen-waveform qualification failure from unperformed X4 recovery,
defined the standardised timing predictors, and gave the within-class likelihood statistic its
proper class-model reference. The article's assumptions table now states calculated results and
current limits rather than attributing information exclusively to class or physical disc state.
The uniform-end lower bound is rounded directly from the full-precision evidence, and the SE
failure boundary is explicitly approximate when printed. Reproduction commands preserve committed
evidence and state their retained-input dependencies. The primary comparison is unchanged.


**Observation, baseline and transfer corrections after external review.**

| Earlier reading or implementation | Reviewed replacement | Evidence |
|---|---|---|
| X4's fitted interval is a hard observing bracket or calibrated posterior | Working crossing summary; proper latent-onset observation likelihood remains unestablished | R1 contract audit |
| The censor rule handles every interval straddle | Separately versioned lower-edge backoff; zero original outcomes changed |[]{.C43} |
| Two-sided report rescoring is available for the original full population | Missing lower clips prevent that; corrected X5 is a new construction |[]{.C45}[]{.C47} |
| An observed clock eliminates endpoint/cadence mechanisms | It removes one literal fitted end but retains report lags, selection and shared observations |[]{.C48}[]{.C53} |
| B2 is the strongest activity comparator | It was preselected; development and descriptive held-out fit were weaker |[]{.C60}[]{.C61} |
| Guards identify an era component of C01 or remove all slow covariation | They change both rules and leave other trends; no causal share of C01 was measured |[]{.C62}[]{.C63} |
| Positive score detection confirms trained forecast gain | Distinct full nulls; overshoot counterexamples and no universal sequence nesting |[]{.C66}[]{.C67} |
| Candidate/reference ratios are paired cycle-conversion probabilities | Issuance/peak descriptive rates; ordinary and derived hold streams are separate |[]{.C70} |
| SS Aur's flag establishes four outbursts or photometric contamination | Four report-night clusters and threshold-proximate medians, with no cause adjudicated |[]{.C71} |
| Frozen transfer failure excludes every later model or data source | Failure of the specified screen; stopping expansion is a scope judgment |[]{.C68}[]{.C70} |
| Adding the observing rate leaves the duration gain unchanged (third draft; Codex, D053) | Rate was fitted in place of duration; the unchanged duration gain is over an end-cadence-adjusted baseline. The two are reported separately |[]{.C56} |
| SS Cyg's record times most successive outbursts (third draft; Codex, D053) | Enough successive, well-covered cycles for the frozen test; the counts do not measure physical completeness |[]{.C70} |
| Most of SS Cyg's predictability lies in its recent rhythm (third draft; Codex, D053) | Timing history made the larger contribution among the three frozen models |[]{.C02}[]{.C10} |
| A class-indicator fit favours a cycle-level mechanism (third draft; Codex, D053) | An in-sample likelihood preference that motivates a future frozen type predictor; refilling and a changing state can both produce it |[]{.C21} |
| Doubling duration matches the short/long difference (third draft; Codex, D053) | About 9% longer untruncated median clock at fixed timing history; the evidence has no class means |[]{.C04} |

None of these reviews retunes or overwrites the original comparison. The failed protocols,
source freezes, bounded access receipts and negative/inconclusive results remain in the record.

## 2 Reproduction and navigation

From the repository root, without new archive requests, these checks use only the committed
aggregates and figure assets:

```sh
python3 manuscript/figures.py --check
make -C manuscript check
make -C manuscript
```

Recomputing scores and exploratory fits requires the retained inputs outside Git. The saved-score
checker needs the completed evaluation run. The three subsequent analyses also need the retained
1910–1959 development inputs. Outputs below go to scratch paths; committed evidence is preserved.

```sh
python3 scripts/check_a10g_evaluation.py \
  --directory outputs/a10h_live_repair_5e39aeb \
  --output outputs/a10m_reproduction/score_audit.json
uv run --frozen --extra analysis \
  python scripts/a10j_postresult_review.py \
  --output outputs/a10m_reproduction/a10j_summary.json
uv run --frozen --extra analysis \
  python scripts/a10k_exploratory_audit.py
uv run --frozen --extra analysis \
  python scripts/a10k_secondary_audit.py
```

The retained run includes raw archive replies, observer identities and per-issuance scores. Its
archive SHA-256 and manifest are in `data/provenance/a10i_evaluation_1960_2017/archive.json`.
The committed aggregates support the ledger values, but do not replace these inputs for a full
recomputation. The published protocol is at <https://doi.org/10.5281/zenodo.24053338>.

The observation/transfer reviews use the same retained early records and saved outputs.
These commands write new audit outputs and do not download data:

~~~sh
uv run --frozen --extra analysis python scripts/r1_observation_scores.py \
  --freeze-commit 0594146 --output outputs/paper_reproduction/r1_scores
uv run --frozen --extra analysis python scripts/check_r2b_execution.py \
  --run outputs/r2b_real_5fb69c6 --allow-real --output outputs/paper_reproduction/r2b_check
uv run --frozen --extra analysis python scripts/check_r2d_review.py \
  --output outputs/paper_reproduction/r2d_review
uv run --frozen --extra analysis python scripts/check_g3a_execution.py \
  --output outputs/paper_reproduction/g3a_check
uv run --frozen --extra analysis python scripts/check_ss_aur_flag.py \
  --output outputs/paper_reproduction/ss_aur_flag
~~~

The endpoint-dose and precision-grid regeneration commands, individual deterministic seeds,
source locks and recovery receipts are in the R1, R2d and G3a audit/protocol files. Full
regeneration is distinct from recounting saved trials and is unnecessary for rebuilding the
paper. Public evidence resides in data/provenance/r1_20261109, r2b_20261109,
r2d_precision, g3a_preparation, g3a_20261110 and g3a_review_independent. These aggregates
do not replace native inputs for an independent full measurement reconstruction. No command
in this guide authorises a new candidate test-period request or SS Cyg 2018+ access.

Navigation:

- `manuscript/claims.csv`: every claim, with its status, evidence, commit, reproduction command and
  limits.
- `manuscript/estimands.md`: allowed and forbidden readings.
- `coordination/decisions.md`: D013–D055.
- `docs/audits/`: every review, including A10i (the result), A10j (Claude's review), A10k (Codex's
  audit) and A10l (sources and drafts).
- `docs/outcome-access-ledger.md`: who saw which outcomes, and when.
- `manuscript/text/for-agents.md`: the agent guide.

## References
