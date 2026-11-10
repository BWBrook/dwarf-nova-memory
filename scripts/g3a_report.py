"""Publish small gain-free G3a aggregates; never fits a model or opens an archive."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--raw',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    receipt=json.loads((args.run/'receipt.json').read_text())
    summary=json.loads((args.run/'summary.json').read_text())
    cohort=json.loads((args.run/'qualified-set.json').read_text())
    if receipt['status']!='completed' or len(summary['stars'])!=10 or receipt['failed_targets']:
        raise ValueError('report requires all ten targets complete; preserve failures separately')
    for name,digest in receipt['output_sha256'].items():
        if sha(args.run/name)!=digest:
            raise ValueError('retained run output changed: '+name)
    rows=[]
    files=[]
    for star in summary['stars']:
        name=star['name'];slug=name.lower().replace(' ','_')
        a=json.loads((args.raw/slug/'acquisition.json').read_text())
        if a['name']!=name or a['auid']!=star['acquisition']['auid']:
            raise ValueError('acquisition identity mismatch')
        for r in a['requests']:
            native=args.raw/slug/r['native_file']
            if sha(native)!=r['sha256']:
                raise ValueError('native page hash changed')
            files.append({'star':name,'path':str(native.relative_to(ROOT)) if native.is_absolute() else str(native),
                          'sha256':r['sha256'],'source_url':r['source_url'],
                          'retrieved_at_utc':r['requested_at_utc'],'bytes':r['bytes'],
                          'validated_rows':r.get('validated_rows'), 'termination':r.get('termination','metadata'),
                          'start_jd':r.get('start_jd',1.),'end_jd':r.get('end_jd')})
        reasons=[]
        if star['df_outcome_supported_marked']<40:reasons.append('fewer_than_40_supported')
        if star['x5_eligible_fraction'] is None or star['x5_eligible_fraction']<.7:reasons.append('window_fraction_below_70_percent')
        if not star['base_only_convergence']['passed']:reasons.append('base_fit_or_information_failure')
        if not star['morphology']['passed']:reasons.append('operational_long_bright_run')
        if star['eclipse_required'] and not star['eclipse_passed']:reasons.append('eclipse_guard_not_passed')
        if bool(reasons)==bool(star['qualified']):raise ValueError('qualification/reason disagreement')
        rows.append({'star':name,'validated_visual_rows':a['validated_visual_rows'],
                     'confirmed_events':star['confirmed_events'],'eligible_windows':star['x5_eligible_events'],
                     'eligible_fraction':star['x5_eligible_fraction'],
                     'feature_supported':star['df_feature_supported_marked'],
                     'outcome_supported':star['df_outcome_supported_marked'],
                     'supported_1980_1989':star['supported_last_decade_count'],
                     'base_passed':star['base_only_convergence']['passed'],
                     'morphology_passed':star['morphology']['passed'],
                     'eclipse_required':star['eclipse_required'],'eclipse_passed':star['eclipse_passed'],
                     'qualified':star['qualified'],'failure_reasons':';'.join(reasons)})
    names=[r['star'] for r in rows if r['qualified']]
    if names!=cohort['names']:raise ValueError('frozen qualifying set differs')
    rate=sum(r['supported_1980_1989'] for r in rows if r['qualified'])/10.
    all_rate=sum(r['supported_1980_1989'] for r in rows)/10.
    projections=[{'years':years,'qualifying_stars':len(names),'projected_qualified_issuances':years*rate,
                  'all_ten_ignoring_gates_diagnostic':years*all_rate,
                  'eligible_to_propose_G3b':len(names)>=6 and years*rate>=1100,
                  'cap_feasible':len(names)>=3,
                  'observed_test_count':False} for years in (28,36)]
    result={'scope':'frozen pre-1990 gain-free feasibility only','source_freeze':receipt['freeze_commit'],
            'stars':rows,'qualified_names':names,'qualified_count':len(names),
            'native_unique_rows':sum(s['acquisition']['native_unique_rows'] for s in summary['stars']),
            'validated_visual_rows':sum(r['validated_visual_rows'] for r in rows),
            'confirmed_events':sum(r['confirmed_events'] for r in rows),
            'outcome_supported':sum(r['outcome_supported'] for r in rows),
            'supported_1980_1989':sum(r['supported_1980_1989'] for r in rows),
            'projections':projections,'native_payloads':len(files),
            'no_mark_fit_or_gain':True,'no_test_data_access':True,
            'limits':['holds use derived fixed-night median streams, not identical raw timing',
                      'plateau exclusion is operational, not a subtype diagnosis',
                      'projections assume development cadence transfers and are not observed future counts',
                      'result concerns frozen transfer rules, not all possible uses of this archive']}
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'summary.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    (args.output/'native-manifest.json').write_text(json.dumps(files,indent=2,sort_keys=True)+'\n')
    with (args.output/'qualification.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    for source in ('receipt.json','qualified-set.json'):
        (args.output/source).write_bytes((args.run/source).read_bytes())
    (args.output/'details.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k in ['qualified_count','validated_visual_rows','outcome_supported','supported_1980_1989','native_payloads']}))


if __name__=='__main__':main()
