# Bibliography sources and generated keys

The manuscript bibliography is generated metadata. It does not change the seed
literature audit or establish that any full text has been read.

- `literature.bib` and `evidence.csv` retain the original thirty citation keys
  and their one-to-one relation. Their source, access and metadata-caution
  statuses remain unchanged.
- `dois.txt` contains thirty-nine distinct active DOI identifiers, one per
  line: thirty-four derived from the twenty-eight seed DOI fields and seven A01
  DOI lines (one unresolved retrieval separated out), and five added in step 4
  of the reconstruction (D055) after Crossref checks: Heitjan and Rubin (1991),
  Nosek et al. (2018), and the NumPy, SciPy and Matplotlib papers.
- `refs.yaml` is generated from that active ledger by `tools/refs.py`, using
  Crossref's CSL-JSON transform and DOI content negotiation as its fallback.
  Each active DOI returned one record with the same DOI. Cite the generated
  `id` in manuscript profiles; the legacy short keys are not aliases in this
  file. No duplicate compatibility records were added.
- `unresolved-identifiers.txt` retains `10.7868/S3034518926080062`, the DOI
  associated with legacy key `Tsuranova2026`. Both configured metadata routes
  returned HTTP 404 during this build. This is unresolved retrieval, not
  evidence that the identifier is invalid or that the paper is absent. Its
  legacy metadata-caution status is preserved; no manual CSL entry was made.
- `a01-new-identifiers.txt` is unchanged, including `arXiv:2301.08579`. Bare
  arXiv identifiers do not enter the DOI-only ledger. A registered DOI such as
  `10.48550/arxiv.1804.06788` remains a DOI.

## Rebuild and inspect

From the repository root, using the isolated locked manuscript environment:

```bash
uv run --project manuscript --frozen python tools/refs.py build
python3 scripts/validate_seed.py
```

The generator prints each manuscript key beside its DOI. It fetches citation
metadata only; it does not request papers or archive observations. The current
`manual.yaml` holds three entries written from verified sources, each with its
provenance in a comment: Hempelmann and Kurths (1990), confirmed against the ADS
bibcode and J. Kurths's institutional bibliography; Grigorievskiy et al. (2014),
from the paper's title page and the authors' group publication list; and Cameron
and Miller (2015), whose Crossref record splits the first author's name. The seed
record `SzkodyMattei1984` remains in the legacy audit only. The manuscript uses
the AAS-style `the-astrophysical-journal.csl`, modified locally to print
publishers only for books and reports.

First generated on 9 November 2026 (Hobart); regenerated on 11 November 2026
after the step-4 additions, with metadata retrieved from Crossref that day.
Snapshot digests:

| File | SHA-256 |
|---|---|
| `tools/refs.py` | `b90ff7a7b516e4bb3a70370a4f41979bb1703f5e62222dcf200f8f79ca764372` |
| `dois.txt` | `c06b7b378c3798be42da44754a155ebe7d57418fb49e961cc003bf5c72293057` |
| `refs.yaml` | `b1264ebef72399263fdb2275f7ed5fc94e8e5dd1edfa1bd76665de3d151a948e` |
| `unresolved-identifiers.txt` | `38edfecaeaff16ab887e311d771fd8f654f018cc51e64ce31630c47420f331c4` |
| unchanged A01 identifier list | `ae373659c1ebd04caa5e4d20ef8b995e7bde37b816b51a534d0d9212b1913097` |

The stdlib seed validator retains its BibTeX/evidence one-to-one test and
recognizes the union of legacy keys and generated manuscript IDs. Its CSL-YAML
ID reader intentionally accepts the controlled top-level `- id: CiteKey`
format emitted here, including the empty scaffold mapping; it rejects duplicate
or shadowed IDs and unsupported layouts. It is not a general YAML validator.
makedoc/Pandoc performs the full manuscript bibliography load. The root validator
also excludes dependency/build-cache Markdown, keeping it independent of the
manuscript PyYAML environment.
