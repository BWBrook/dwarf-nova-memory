#!/usr/bin/env python3
"""Generate the R2/G3a numeric tables from retained public aggregate evidence."""
import argparse
import csv
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / 'figure-data' / name).open() as handle:
        return list(csv.DictReader(handle))


def rounded(value, places):
    return str(Decimal(str(value)).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP))


def span(value, claim, binding=None, places=None, scale=1):
    number = Decimal(str(value)) * Decimal(str(scale))
    shown = rounded(number, places) if places is not None else f'{int(number):,}'
    return f'[{shown.replace("-", "−")}]{{.{claim}' + (f' .V{binding:03d}' if binding else '') + '}'


def r2_table(wide=False):
    descriptions = ['H1: fitted-end clock, B2 duration', 'H2: observed clock, B2 bright span',
                    'H3: observed-clock gain minus matched fitted-end gain']
    header = '| Exploratory contrast | Scored issuances | Mean gain, nats | Six-year 90% interval |'
    rule = '|---|---:|---:|---|'
    if wide:
        header += ' Twelve-year 90% interval |'
        rule += '---|'
    result = [header, rule]
    for i, row in enumerate(rows('r2b-contrasts.csv')):
        mean = span(row['estimate'], 'C55', 9 + 4 * i, 4)
        count = span(row['n'], 'C55', 12 + 4 * i)
        interval = ' to '.join(span(row[key], 'C55', 10 + 4*i + j, 4)
                               for j, key in enumerate(['six_year_lower', 'six_year_upper']))
        line = f'| {descriptions[i]} | {count} | {mean} | {interval} |'
        if wide:
            line += ' ' + ' to '.join(span(row[key], 'C55', 21 + 2*i + j, 4)
                                      for j, key in enumerate(['twelve_year_lower', 'twelve_year_upper'])) + ' |'
        result.append(line)
    return '\n'.join(result)


def precision_table():
    cases = {r['case']: r for r in json.loads((ROOT / 'data/provenance/r2d_precision/summary.json').read_text())['cases']}
    result = ['| Stars and condition | Nominal evaluation issuances | Score-moment rejection | Frozen-gain rejection |',
              '|---|---:|---:|---:|']
    for name, title, gain in [('core-s8-n1100-effect', 'Eight, clean', True),
                              ('persistent-s8-effect', 'Eight, persistent / small development / missing marks', False),
                              ('common-delayed-s8-effect', 'Eight, noisy / delayed / common state', False)]:
        row = cases[name]
        sc = span(row['methods']['star-score']['rate'], 'C65', places=1, scale=100)
        ga = span(row['methods']['star-gain']['rate'], 'C65', places=1, scale=100)+'%' if gain else '—'
        result.append(f'| {title} | {span(row["settings"]["test_forecasts"], "C65")} | {sc}% | {ga} |')
    data = {(r['case'], r['method']): r for r in rows('six-star-precision.csv')}
    for i, (name, title) in enumerate([('core-s6-n1100-effect', 'Six, clean'), ('core-s6-n2000-effect', 'Six, clean'),
                                      ('persistent-s6-effect', 'Six, persistent / small development / missing marks'),
                                      ('common-delayed-s6-effect', 'Six, noisy / delayed / common state')]):
        row = data[name, 'star-score']; gain = data[name, 'star-gain']
        count = span(row['nominal_forecasts'], 'C69', 67 if i == 1 else 66)
        sc = span(row['rate'], 'C69', 58 + 2*i, 1, 100)
        ga = span(gain['rate'], 'C69', 59 + 2*i, 1, 100)
        result.append(f'| {title} | {count} | {sc}% | {ga}% |')
    return '\n'.join(result)


def qualification_table():
    reasons = ['Operational morphology', 'Count, windows', 'Count, windows, base information/fit',
               'Count, windows', 'Count, windows, base information/fit', 'Count',
               'Count, base information/fit', 'Count, base information/fit',
               'Count, eclipse guard inconclusive', 'Count, windows, base information/fit, eclipse guard inconclusive']
    result = ['| Candidate | Supported development issuances | Eligible onset windows | Main failed conditions |',
              '|---|---:|---:|---|']
    for i, row in enumerate(rows('g3a-stars.csv')):
        name = row['star'] + (', hold' if row['eclipse_required'] == '1' else '')
        count = span(row['outcome_supported'], 'C68', 38 + 2*i)
        pc = span(row['eligible_fraction'], 'C68', 39 + 2*i, 1, 100)
        result.append(f'| {name} | {count} | {pc}% | {reasons[i]} |')
    return '\n'.join(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    blocks = {'main.md': {'r2b': r2_table(True), 'precision': precision_table(),
                          'qualification': qualification_table()}}
    for name, tables in blocks.items():
        path = HERE / 'text' / name
        text = path.read_text()
        for key, table in tables.items():
            start, stop = f'<!-- BEGIN GENERATED {key} -->', f'<!-- END GENERATED {key} -->'
            if text.count(start) != 1 or text.count(stop) != 1:
                raise SystemExit(f'{path}: expected one marker pair for {key}')
            a, b = text.index(start) + len(start), text.index(stop)
            updated = text[:a] + '\n' + table + '\n' + text[b:]
            if args.check and updated != text:
                raise SystemExit(f'{path}: stale generated table {key}')
            text = updated
        if not args.check:
            path.write_text(text)
    print('Four aggregate-derived R2/G3a tables are current')


if __name__ == '__main__':
    main()
