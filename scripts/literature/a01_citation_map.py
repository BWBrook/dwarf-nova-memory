"""Forward-citation and keyword map for the A01 novelty audit (OpenAlex + arXiv)."""
import csv, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "dwarf-nova-memory-literature-audit/0.1"}

SEEDS = {
    "BathVanParadijs1983": "10.1038/305033a0",
    "VanDerWoerdVanParadijs1987": "10.1093/mnras/224.2.271",
    "CannizzoMattei1992": "10.1086/172092",
    "CannizzoMattei1998": "10.1086/306165",
    "Ak2002": "10.1051/0004-6361:20020600",
    "Coppejans2016": "10.1093/mnras/stv2921",
    "OtulakowskaHypka2016": "10.1093/mnras/stw1120",
    "Simon2022": "10.1093/mnras/stab3577",
    "George2015": "10.1007/s10509-015-2516-z",
    "Kimura2021": "10.1093/pasj/psab073",
}
TITLE_SEARCH = {
    "HempelmannKurths1990": "Dynamics of the outburst series of SS Cygni",
    "SzkodyMattei1984": "Analysis of the AAVSO light curves of 21 dwarf novae",
    "CannizzoGoodings1988": "Chaos in SS Cygni",
}
QUERIES = [
    "dwarf nova outburst prediction", "dwarf nova outburst forecast",
    "predicting dwarf nova outbursts", "dwarf nova recurrence time prediction",
    "SS Cygni outburst prediction", "SS Cygni outburst correlation quiescent interval",
    "dwarf nova outburst memory", "dwarf nova outburst machine learning",
    "dwarf nova outburst neural network", "cataclysmic variable outburst forecasting",
    "dwarf nova quiescent interval outburst duration correlation",
    "dwarf nova outburst recurrence statistics AAVSO",
    "dwarf nova outburst time series nonlinear prediction",
    "U Geminorum outburst recurrence", "outburst intervals dwarf novae long-term light curves",
]
KEY = re.compile(r"predict|forecast|memory|recurren|quiescen|interval|waiting|correlat|"
                 r"machine learning|neural|chaos|nonlinear|time series|serial|cycle length|"
                 r"outburst duration|AAVSO", re.I)


def get(url, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            if k == tries - 1:
                raise
            time.sleep(2 * (k + 1))


def oa(path, **params):
    q = urllib.parse.urlencode(params)
    return json.loads(get(f"https://api.openalex.org/{path}?{q}"))


def abstract(w):
    inv = w.get("abstract_inverted_index") or {}
    pos = sorted((p, t) for t, ps in inv.items() for p in ps)
    return " ".join(t for _, t in pos)


def row(w, via):
    return {"via": via, "openalex": w["id"].rsplit("/", 1)[-1], "year": w.get("publication_year"),
            "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
            "title": (w.get("title") or "").replace("\n", " "),
            "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name", ""),
            "cited_by": w.get("cited_by_count"), "abstract": abstract(w)[:1500]}


rows, seeds_found = [], {}
for key, doi in SEEDS.items():
    try:
        w = oa(f"works/doi:{doi}")
        seeds_found[key] = (w["id"].rsplit("/", 1)[-1], w.get("cited_by_count"), w.get("title"))
    except Exception as e:  # noqa: BLE001
        seeds_found[key] = (None, None, f"lookup failed: {e}")
for key, title in TITLE_SEARCH.items():
    res = oa("works", search=title, **{"per-page": 3})["results"]
    hit = next((w for w in res if title.lower()[:25] in (w.get("title") or "").lower()), None)
    seeds_found[key] = (hit["id"].rsplit("/", 1)[-1], hit.get("cited_by_count"), hit.get("title")) if hit else (None, None, "not found")

for key, (wid, n, title) in seeds_found.items():
    if not wid:
        continue
    cursor = "*"
    while cursor:
        page = oa("works", filter=f"cites:{wid}", **{"per-page": 200, "cursor": cursor})
        rows += [row(w, f"cites:{key}") for w in page["results"]]
        cursor = page["meta"].get("next_cursor")
        if not page["results"]:
            break

for q in QUERIES:
    page = oa("works", search=q, **{"per-page": 50})
    rows += [row(w, f"search:{q}") for w in page["results"]]

ax = []
for q in ['abs:"dwarf nova" AND (abs:forecast OR abs:prediction OR abs:predict OR abs:predictability)',
          'abs:"dwarf nova" AND abs:outburst AND abs:recurrence',
          'abs:"SS Cyg" AND abs:outburst',
          'abs:"dwarf nova" AND abs:outburst AND (abs:memory OR abs:correlation)',
          'abs:"cataclysmic variable" AND abs:outburst AND (abs:"machine learning" OR abs:"neural network")']:
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"search_query": q, "max_results": 100})
    xml = get(url).decode()
    for e in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        t = re.sub(r"\s+", " ", re.search(r"<title>(.*?)</title>", e, re.S).group(1))
        s = re.sub(r"\s+", " ", re.search(r"<summary>(.*?)</summary>", e, re.S).group(1))
        i = re.search(r"<id>(.*?)</id>", e).group(1).rsplit("/", 1)[-1]
        y = re.search(r"<published>(\d{4})", e).group(1)
        ax.append({"via": f"arxiv:{q}", "openalex": "", "year": y, "doi": f"arXiv:{i}", "title": t,
                   "venue": "arXiv", "cited_by": "", "abstract": s[:1500]})
    time.sleep(3)
rows += ax

merged = {}
for r in rows:
    k = r["doi"].lower() or r["openalex"] or r["title"].lower()
    if k in merged:
        merged[k]["via"] += "; " + r["via"]
    else:
        merged[k] = dict(r)
for r in merged.values():
    r["kw_hits"] = len(set(m.lower() for m in KEY.findall(r["title"] + " " + r["abstract"])))
with open(OUT / "candidates.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(next(iter(merged.values())).keys()))
    w.writeheader()
    w.writerows(sorted(merged.values(), key=lambda r: (-r["kw_hits"], str(r["year"]))))
json.dump(seeds_found, open(OUT / "seeds.json", "w"), indent=1)
print(json.dumps(seeds_found, indent=1))
print("raw rows", len(rows), "unique", len(merged))
