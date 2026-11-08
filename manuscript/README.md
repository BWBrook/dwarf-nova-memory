# Does the length of an outburst predict the wait for the next? A preregistered 58-year forecast test for SS Cygni

The same study is written three ways, all in `text/`, all from one evidence base:

| File | Reader | Rendered |
|---|---|---|
| `main.md` + `figures.md`, `supplement.md` + `supplement_figures.md` | scientists; the journal snapshot | `build/manuscript.pdf`, `build/supplement.pdf` |
| `brief.md` + `brief_figures.md` | anyone: two A4 pages, one sheet printed double-sided | `build/brief.pdf` |
| `for-agents.md` | an agent arriving cold: claims, provenance, traps, checks | read as Markdown |

`claims.csv` is the single claims ledger. All four renderings cite it, binding quoted numbers as
`[428.8]{.C01}` (invisible in PDF and DOCX); `value-bindings.csv` can bind a number further to one row
and field of its evidence. `estimands.md` states what each analysis bounds and which phrasings are
not allowed.

## Build

The paper builds with [makedoc](https://github.com/BWBrook/makedoc), expected at `~/work/makedoc`
(override with `MAKEDOC=...`). `makedoc.lock.json` pins its revision. TeX (xelatex), Pandoc and
poppler are system dependencies; `uv` supplies Python. From the repository root:

```sh
uv run --project manuscript --frozen python tools/refs.py build        # references/refs.yaml from references/dois.txt via Crossref
make -C manuscript check          # claims ledger, glyphs, makedoc lint and citation audit
make -C manuscript                # PDF and DOCX into build/, then the brief's two-page check
```

To cite a work, add its DOI to `references/dois.txt` (or an entry to `references/manual.yaml`),
rebuild, and cite the printed key with Pandoc citation syntax (an at-sign key in square brackets).
The structural validator accepts the legacy keys and the generated manuscript keys while preserving
the separate source-evidence register. See `references/README.md` for identifier status and provenance. Keys follow Better BibTeX's default pattern and
skip words, so a Zotero export of the same DOIs matches where the two sources' metadata agree (title casing and name
particles can still differ). Generated content is not edited by hand: marked table blocks, `figures/`,
`references/refs.yaml` and `build/`.
