# Bibliography sources and generated keys

The manuscript bibliography is generated metadata. It does not change the seed
literature audit or establish that any full text has been read.

- `literature.bib` and `evidence.csv` retain the original thirty citation keys
  and their one-to-one relation. Their source, access and metadata-caution
  statuses remain unchanged.
- `dois.txt` contains thirty-four distinct active DOI identifiers, one per
  line, derived from the twenty-eight seed DOI fields and seven A01 DOI lines,
  with one unresolved retrieval separated out.
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
`manual.yaml` remains empty. The two seed records without verified DOI fields
(`SzkodyMattei1984` and `HempelmannKurths1990`) remain in the legacy audit and
are not fabricated in the generated bibliography.

Generated on 9 November 2026 (Hobart), with official metadata retrieved by
2026-11-08T14:37:07.696129+00:00. Snapshot digests:

| File | SHA-256 |
|---|---|
| `tools/refs.py` | `b12a737c6d311e26d4b54f3ba8bc0c22fd578a8ffeb4110811f1f865f58244df` |
| `dois.txt` | `507fee464d0c3f60d20604c0ccb21e4d56e1aeacda4766ed9b3c32fa3c7f0eb1` |
| `refs.yaml` | `33192e30dced13820d071d6ccbc48290adbfd44a221946c68b17b381a98d08d5` |
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
