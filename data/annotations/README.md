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

The input is SS Cyg, AAVSO AID native visual export
`aavso_ss_cyg_1956_1959_20261107`, with SHA-256 `1840efea…8ad87f` (full hash in
`data/manifests/acquisitions.csv`). Times are native JD, presumed UT-based and
geocentric to within 0.006 d.

The tables hold native observation IDs, JDs and one peak magnitude per event.
They do not hold observer identities or raw rows. All rows predate 1960-01-01
(D013).

We gratefully acknowledge the contributions of the AAVSO observer community,
whose photometric data and metadata resources were used in this study and made
available through the AAVSO's scientific archives.
