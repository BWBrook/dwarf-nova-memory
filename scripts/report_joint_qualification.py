from pathlib import Path
import json, csv, math, sys, hashlib, argparse
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'),str(ROOT/'src')]
import a04i_pipeline as pipeline
from a04h_morphology_targets import WAVEFORM, CADENCE
OUTPUT = None

def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def prepare_public():
    qdir=ROOT/'outputs/a04i_qualification_20261108'
    q=json.loads((qdir/'receipt.json').read_text())
    inp=json.loads((ROOT/'outputs/a04i_inputs_frozen_20261108/inputs.json').read_text())
    vectors={}; metadata={}; counter=0
    for key,entry in q['pairs'].items():
        config=entry['configuration'];name=config['configuration_id']+'.json';p=qdir/name
        if digest(p)!=q['qualification_attempts_sha256'][name]:raise ValueError('attempt hash differs')
        attempt=json.loads(p.read_text())
        if pipeline.assess_samples(attempt['samples'],inp)!={k:v for k,v in entry.items() if k!='configuration'}:raise ValueError('gate rederivation differs')
        vectors[key]=[{'replicate':s['replicate'],'valid':s['valid'],'statistics':s.get('statistics')} for s in attempt['samples']]
        metadata[key]={}
        for era in pipeline.ERAS:
            ms=[s['metadata'][era]['cadence'] for s in attempt['samples']]
            sums={k:sum(m[k] for m in ms) for k in ('input_observed_days','output_observed_days','target_events','target_events_with_anchors','target_anchor_failures','matched_events','unmatched_events','source_visits_considered','unavailable_day_drops','boundary_drops','duplicate_source_drops','overlap_collision_drops')}
            sums['masked_visit_fraction']=sums['unavailable_day_drops']/sums['source_visits_considered']
            sums['additional_empty_day_fraction']=1-sums['output_observed_days']/sums['input_observed_days']
            sums['all_preserved_original_empty_days']=all(m['output_never_uses_originally_empty_day'] for m in ms)
            metadata[key][era]=sums
        counter+=3*len(attempt['samples'])
    public={'scope':'A04i fresh joint benchmark qualification, not X4 recovery or a real-star result','qualification_receipt_sha256':digest(qdir/'receipt.json'),'receipt':q,'real_targets':inp['joint_targets'],'real_counts':inp['joint_target_counts'],'raw_feature_vectors':vectors,'cadence_diagnostics':metadata,'era_histories':counter,'x4_recovery_in_this_artifact':False}
    out=OUTPUT/'a04i_qualification_20261108.json'
    out.write_text(json.dumps(public,sort_keys=True,allow_nan=False,separators=(',',':'))+'\n')
    with (OUTPUT/'a04i_qualification_20261108.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['pair','block','feature','real','synthetic_mean','synthetic_sd','z_raw','prediction_p_raw','block_pass','pair_eligible'],lineterminator='\n');w.writeheader()
        for key,entry in q['pairs'].items():
            for block,names in [('waveform',WAVEFORM),('cadence',CADENCE)]:
                b=entry[block]
                for n in names:
                    w.writerow({'pair':key,'block':block,'feature':n,'real':inp['joint_targets'][n],'synthetic_mean':b['synthetic_mean'][n],'synthetic_sd':b['synthetic_sd'][n],'z_raw':b['z_raw'][n],'prediction_p_raw':b['prediction_p_raw'],'block_pass':b['pass'],'pair_eligible':entry['eligible']})
    return public

def plot(public):
    import matplotlib
    matplotlib.use('Agg')
    matplotlib.rcParams['svg.hashsalt']='a04i-939ea77'
    matplotlib.rcParams['svg.fonttype']='none'
    import matplotlib.pyplot as plt
    names=tuple(WAVEFORM)+tuple(CADENCE)
    labels={'core_level_mean':'Middle-third brightness','rise_slope_median':'Rising speed','end_slope_median':'Fading speed','end_residual_sd_median':'Observer scatter','log_below_above_slope_ratio':'Slope change at magnitude 10','rho_duration_end_slope':'Duration / fading-speed association','rho_duration_rise_slope':'Duration / rising-speed association','rho_duration_core_level':'Duration / middle-third brightness','episodes_per_year':'Outbursts per year','duration_median':'Median measured duration','above_fit_fraction':'Fades measurable above threshold','below_fit_fraction':'Fades measurable below threshold'}
    pairs=public['receipt']['pairs'];fig,axs=plt.subplots(1,len(pairs),figsize=(10.8,6),sharey=True,squeeze=False)
    extent=max(4,max(abs(b['z_raw'][n]) for e in pairs.values() for block,ns in [('waveform',WAVEFORM),('cadence',CADENCE)] for b in [e[block]] for n in ns)+.7)
    for ax,(key,e) in zip(axs[0],pairs.items()):
        zs=[e['waveform' if n in WAVEFORM else 'cadence']['z_raw'][n] for n in names]
        ax.axvspan(-3.3,3.3,color='#edf1f4',zorder=0)
        ax.axvline(0,color='#666666',lw=.8)
        ax.axvline(-3.3,color='#777777',lw=.8,ls='--');ax.axvline(3.3,color='#777777',lw=.8,ls='--')
        ax.scatter(zs,range(len(names)),c=['#23638b']*len(WAVEFORM)+['#b75e25']*len(CADENCE),s=33,zorder=3)
        ax.axhline(len(WAVEFORM)-.5,color='#aaaaaa',lw=.6)
        ax.set_title(key+'\nwaveform p = '+format(e['waveform']['prediction_p_raw'],'.3g')+'; cadence p = '+format(e['cadence']['prediction_p_raw'],'.3g'),fontsize=10)
        ax.set_xlim(-extent,extent);ax.set_ylim(len(names)-.5,-.5);ax.set_yticks(range(len(names)),[labels[n] for n in names],fontsize=9)
        ax.set_xlabel('(real target − synthetic mean) / predictive SD',fontsize=9);ax.grid(axis='x',alpha=.15)
        ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Fresh A04i benchmark compatibility: 150 real-sized records per pair',fontsize=12)
    fig.text(.02,.025,'Blue: waveform; orange: cadence. Shading marks the marginal |z| ≤ 3.3 cap.\nJoint block decisions also use the full covariance; points inside the cap do not establish a pass.',fontsize=8)
    fig.tight_layout(rect=(0,.08,1,.95))
    svg=OUTPUT/'a04i_qualification_20261108.svg';fig.savefig(svg,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    fig.savefig(ROOT/'outputs/a04i_qualification_20261108.png',dpi=150);plt.close(fig)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Reconcile A04i raw qualification vectors and export compact public evidence.')
    parser.add_argument('--output',type=Path,default=ROOT/'data/simulations')
    parser.add_argument('--plot',action='store_true')
    args=parser.parse_args();OUTPUT=args.output;OUTPUT.mkdir(parents=True,exist_ok=True)
    public=prepare_public()
    if args.plot:plot(public)
    print(json.dumps({'histories':public['era_histories'],'eligible':public['receipt']['eligible_pair_ids']}))
