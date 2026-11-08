# A10l: source checks, agreement on the revised estimands, and first drafts

Claude, 9 November 2026 (Hobart). **D029 is accepted in full. CM92's Table 4 checks against the
original scan. The novelty claim survives only with qualifiers. All four products now have first
full drafts.** No archive request was made. No retained-run file, outcome or 2018-onward record
was read; this turn used committed aggregates, figures and primary literature only.

## 1. Agreement on D029 and the revised estimands

Every A10k narrowing is correct. Several corrected my own A10j wording or my closing message to
Barry:

- "genuine within-period information" for the recentred contrast;
- "the information is long/short type";
- "M2 forecasts gaps 4.6% too long";
- "about five days longer";
- "survives an SE 1.43× larger". The boundary is 1.42705, so 1.43 fails.

I adopt the A10k wording in all products. I added two sections to `manuscript/estimands.md`,
covering the source-checked physical reading (§3) and the narrowed novelty wording (§4).

## 2. CM92 against the original scan (C40)

I OCR'd the ADS scan of Cannizzo & Mattei (1992, ApJ 401, 642) in the session scratchpad and
re-read Table 4 (printed p. 645) and the Fig. 5 subscript conventions from page images.

- **Table 4.** $(t_b)_i{:}(t_q)_i$ = 0.223, and $(t_q)_i$ is the quiescence *after* outburst
  $i$ (Fig. 5). The preceding quiescence $(t_q)_{i-1}$ gives 0.282. Successive durations give
  −0.400, successive quiescences 0.382 and successive cycles 0.349. Onset-to-onset cycles give
  0.475 (following) against 0.145 (preceding). End-to-end cycles give 0.093 against 0.521.
- **Abstract and §2.** 705 outbursts, 1896 Sept 27 to 1992 Apr 7, from 29,387 daily means of
  180,233 observations, with crossings of $m_v = 10$. Durations are bimodal, with 401 below 12 d and
  304 above. Quiescence has mean 38.71 d and SD 13.89 d.
- **Interpretation in the source.** CM92 call the 0.2–0.3 duration–quiescence correlations
  "probably not" significantly different. They read the positive successive-quiescence and cycle
  correlations as a hint of secular variation.

Codex's A01 extraction is confirmed. C40 becomes supported, and its value now includes the
preceding-quiescence correlation.

## 3. Cannizzo (1993, ApJ 419, 318), read in full

What it says (paraphrased):

- In the disc-instability model tuned to SS Cyg, short outbursts are sandwiched between long ones.
  A higher transfer rate gives the strict alternation most common in SS Cyg.
- At the model's default 100-point grid, long outbursts accrete about 30% of the disc and short
  ones about 3%. The fractions fall as resolution rises.
- The surface density at large radii is lower after a long outburst. That profile tends to make the
  next outburst short, and vice versa, as Smak (1984) noted. Type is set by disc mass at onset.
- Outbursts are triggered near the inner edge, so model quiescent intervals scale with the
  quiescent viscous drift time and are independent of the transfer rate.
- Moving averages of the AAVSO curve show recurrence time correlating directly with $N(L)/N(S)$.
  The model reproduces this through slow changes in the inner radius or in one viscosity parameter,
  not through transfer-rate variation.

What it does not say: my reading found no reported contrast in the following quiescence after long
versus short outbursts. So the 1993 model accounts for alternation, not for our forecast gain. Two
readings of the gain are compatible: cycle-to-cycle disc depletion, and duration as a proxy for a
slow state. The second is supported in spirit by the paper's recurrence–type-ratio covariation.
The estimands now forbid "confirms the disc instability model".

## 4. Novelty refresh (C41)

A separate Claude Sonnet subagent refreshed the search. It used about 14 web queries and 6 arXiv
or OpenAlex lookups, and found the closest precedent's full text. I verified the design from that
PDF myself.

- **Grigorievskiy, Mantere, Akusok, Eirola & Lendasse (2014),** "Forecasting the outbursts of the
  photometry light curve of star V363 Lyr", ITISE 2014 proceedings, pp. 520–531. Open PDF:
  <https://research.cs.aalto.fi/aml/Publications/Publication216.pdf>. No DOI or ISBN was found.
  - Data: Kepler photometry of KIC 7431243.
  - Split: chronological train, validation and test sets, each of the latter holding one outburst.
  - Forecasts: point forecasts of onset position from every start point before it, scored by mean
    absolute error.
  - Methods: random forest, OP-ELM, k-NN and linear models. Nothing was preregistered or
    probabilistic.

  This is a genuine held-out timing forecast for a dwarf nova. "First held-out forecast" is
  therefore false.
- No survival or hazard analysis, ML outburst forecasting, Kepler/TESS/ZTF/ASAS-SN forecasting or
  AAVSO prediction evaluation was found for dwarf novae. A recurrent-nova predictability preprint
  (arXiv:2601.02403, RS Oph) is adjacent and was not verified.
- **Limits.** No ADS query. OpenAlex forward citations of Grigorievskiy failed on a rate limit.

The wording is now: "to our knowledge, the first preregistered, frozen-parameter probabilistic
evaluation of dwarf-nova recurrence forecasts on held-out data, and the first test of whether the
completed outburst's duration adds forecast skill." The article cites Grigorievskiy et al.
explicitly. **C41 stays provisional** until an agent other than Claude checks the search,
preferably with ADS and forward citations of Grigorievskiy et al. and CM92.

## 5. Drafts

The article, supplement, brief and agent guide are written against the revised estimands. Every
quoted number is bound. One binding was added: V008, the C21 clock-scale percentage. C15 is a new
claim recording the data scope from the native audit.

- **Endpoint coupling** now appears as a limit in the article's discussion and assumptions table.
  The point comes from D020/D021: shared end-time error can create information in some
  constructions.
- **Changes beyond D029.**
  - The C33 comparison is worded so it cannot be read as exceeding a known physical size.
  - The 2018+ forecast count is labelled a planning assumption.
  - Fig. 1 is described as selected by observation time.
- **Left for Barry:**
  - authorship metadata (`authors.yaml` still lists the AI systems as a placeholder line);
  - venue and CSL;
  - Zotero entries for the two DOI-less references, Hempelmann & Kurths (1990), ADS 1990A&A...232..356H,
    and Grigorievskiy et al. (2014), cited in plain text meanwhile.

## 6. Requests to Codex

1. **Semantic review** of all four products against `manuscript/estimands.md`. Check every
   result-stating sentence, and search for each not-allowed phrasing. The numeric checker cannot see
   meaning.
2. **Independent C41 search check**, with ADS if a token is available. Otherwise use OpenAlex
   forward citations of CM92 and Grigorievskiy et al.
3. **Rendered-PDF check.** Cover tables, the supplement equations, figure references and the
   brief's two-page limit.

## 7. Checks

The claims ledger, glyph check, figure check, makedoc lint and citation audit, the full PDF build,
the brief length check, the repository validator, the unit tests and the staged secrets scan were
run before commit. Results are in the commit message and board post.
