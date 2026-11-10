# Claude review of the integrated second drafts (D047)

Claude (Opus 5.5), 10 November 2026. Reviewed Codex's integration at `0ed400b`: the
[integration memo](2026-11-10-r2-paper-integration.md), the C70 and C71 independent reviews, the
revised `manuscript/estimands.md`, and all four products.
- I read the article and the brief in full and inspected every rendered page.
- A Claude Sonnet subagent independently checked the supplement and agent guide against the
  estimands, the claims ledger and committed evidence. It was given the files and rules, not my
  conclusions.

No data were opened, no analysis was run and no request was made.

## Verdict

The drafts are faithful to the evidence and the estimands. Nothing in any product asserts a
"Not allowed" phrasing.
- The working-score qualification sits beside every statement of C01.
- Exploratory checks are never called confirmation.
- G3a is described as a feasibility screen, not a test of other stars.
- The subagent confirmed every quoted number it checked against `claims.csv` and the value
  bindings, and found no arithmetic errors.

I accept Codex's three corrections to my C70–C71 wording:
- the 2000–2025 inclusive projection is 247, not 238;
- the four SS Aur report clusters, one of them a single night, are not established as four physical
  outbursts;
- the 14.5-mag comparison is a selected pooled median, not a same-era quiescent level.

I also accept the estimands' rule against presenting issuance-to-peak ratios as paired conversion
probabilities.

## Changes made

| Product | Change | Reason |
|---|---|---|
| Article | Abstract rewritten (about 250 words) | It read as a list of caveats and omitted the transfer finding. It now states the qualification once, plainly, and adds the 1980s per-outburst contrast with SS Cyg (C70). The C66 aside moved out of the abstract; it remains in §3.4 |
| Article §4.2 | Added: SS Cyg shows the contract can be met (nearly one supported issuance per confirmed 1980s peak, against roughly one per five for the candidates), so a generality test needs records of comparable completeness | The discussion did not say what the contrast in §3.4 means. The wording is descriptive, not a conversion probability or sole cause |
| Article | Roles: Claude diagnosed the transfer attrition and reviewed the second drafts; Sonnet subagents ran the novelty search and the semantic check | Accuracy of the roles statement |
| Article | Removed three redundant sentences and an unclear one about the SS Aur flag | Kept the article at 13 pages; each removed statement is made elsewhere |
| Brief | Explained "nats" through C02 (about 1.7% more probability on a geometric average); added that this is a held-out test | "Score units" meant nothing to a lay reader |
| Brief | Moved the C44 citation to the sentence it supports | C44's interval excludes zero; it had been cited for "intervals included zero" |
| Brief | Added SS Cyg's 67 usable forecasts for 73 confirmed 1980s outbursts against the candidates' 102 for 485, and that most candidates are fainter between outbursts | The brief's most informative fact about why other stars failed, stated descriptively |
| Brief | Roles: Claude drafted the first versions and reviewed these; Codex prepared the second drafts | Accuracy |
| Supplement | Removed a C53 binding from a sentence it does not support; reworded "definitional, as CM92 showed" so the attribution is CM92's actual point | Subagent findings 3 and 4 |
| Agent guide | §6 names the raw inputs that two reproduction scripts read, and forbids pointing any script at SS Cyg 2018+ or candidate 1990+ records; C52 and C59 marked provisional; "an earlier held-out point forecast" singular (C41) | Subagent findings 1, 2 and 5 |

## Checks

- Claims check: 0 errors.
- Figure check and render check: pass.
- Brief: 2 pages. Article: 13 pages. Supplement: 18 pages.
- 580 unit tests pass.

## Open items for Barry before any release

- **Two works are cited inline without bibliography entries:** Hempelmann and Kurths (1990,
  *A&A* 232, 356) and Grigorievskiy et al. (2014, ITISE proceedings). Neither has a DOI on file.
  They need verified manual entries.
- **Decisions only Barry can make:** byline, venue, observer credit and co-authorship under the
  AAVSO guidelines, and any preprint or release.
- **Optional:** a third panel in Fig. 4 showing 1980s supported issuances per confirmed peak with
  SS Cyg as reference would make the transfer finding visible at a glance. I did not add it.
