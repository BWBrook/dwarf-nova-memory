# Event annotations

Annotator-judgement event tables. They cannot be regenerated without the
judgement, so they are committed. Each annotation has three parts:

- a decisions file, which records which mechanical candidates form each event
  and which rows were overruled, with notes;
- the computed table, built from the decisions and the hashed raw export by
  `scripts/a04_build_annotation.py`;
- a protocol in `docs/protocols/`.

**Second annotators working blind** (see the protocol): do not open this
directory until your own labels are committed.

| File | Content |
|---|---|
| `a04_ss_cyg_1956_1958_claude_v1_decisions.csv` | Claude's adjudication of the 58 mechanical A04-v1 candidates into 23 events |
| `a04_ss_cyg_1956_1958_claude_v1.csv` | Computed brackets, envelopes, confirmations, bounds, coverage and flags; columns defined in the A04 memo and protocol |
| `a04_ss_cyg_1957_codex_blind_v1.csv` | Independent sealed 1957 annotation, with subset-edge censoring; primary labels unchanged after comparison |
| `a04_ss_cyg_1957_codex_blind_v1_decisions.csv` | Independent candidate, gap and T-row judgements, using native observation IDs |
| `a04_ss_cyg_1957_adjudication.csv` | Claude's adjudication of the three disputed 1957 boundaries (one Claude error, two representation cases), with v2 intervals and native IDs; both sealed catalogues unchanged |
| `a04_ss_cyg_1957_codex_blind_seal.json` | Frozen inputs and original/LF-normalized output hashes; labels committed before comparison |

The input is SS Cyg, AAVSO AID native visual export
`aavso_ss_cyg_1956_1959_20261107`, with SHA-256 `1840efea…8ad87f` (full hash in
`data/manifests/acquisitions.csv`). Times are native JD, presumed UT-based and
geocentric to within 0.006 d.

The 0.006 d comparison concerns alternative timestamp conventions, not a bound
on historical record errors. The blind annotator saw only the frozen protocol
and the 1957 raw subset in a fresh context, not this directory or the board.
The [comparison](../../docs/audits/2026-11-07-a04-independent-comparison-open-era.md)
distinguishes strict overlap from post-seal episode pairing. The
[clarification](../../docs/audits/2026-11-07-a04-blind-1957-clarification.md)
resolves an alternative-boundary prose/field discrepancy without changing a
sealed primary label. The [A04b adjudication](../../docs/audits/2026-11-07-a04b-adjudication-extraction-candidates.md) settles the three disputed boundaries; there is still no reconciled consensus catalogue, by design. Candidate extractors replace hand catalogues from here on.

The tables hold native observation IDs, JDs and one peak magnitude per event.
They do not hold observer identities or raw rows. All rows predate 1960-01-01
(D013).

We gratefully acknowledge the contributions of the AAVSO observer community,
whose photometric data and metadata resources were used in this study and made
available through the AAVSO's scientific archives.
