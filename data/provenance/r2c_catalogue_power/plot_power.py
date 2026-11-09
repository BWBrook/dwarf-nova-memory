"""Render the aggregate score-level planning curves; never access observations."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE=Path(__file__).resolve().parent
rows=json.loads((HERE/'power-summary.json').read_text())
fig,axes=plt.subplots(1,2,figsize=(11.4,4.7),gridspec_kw={'width_ratios':[1.05,1.2]})
for gain,color in ((.008,'#4477AA'),(.010,'#228833'),(.0165,'#AA3377')):
 own=sorted((r for r in rows if r['id'].startswith('core-') and r['rule']=='fitted_rule' and r['nominal_oracle_gain']==gain),key=lambda r:r['test_forecasts'])
 x=np.array([r['test_forecasts'] for r in own]);y=np.array([r['confirmation']['rate'] for r in own]);lo=np.array([r['confirmation']['lower95'] for r in own]);hi=np.array([r['confirmation']['upper95'] for r in own])
 axes[0].errorbar(x,y,yerr=[y-lo,hi-y],color=color,marker='o',capsize=2,label=f'Fitted; nominal gain {gain:g}')
own=sorted((r for r in rows if r['id'].startswith('core-') and r['rule']=='known_rule' and r['nominal_oracle_gain']==.010),key=lambda r:r['test_forecasts'])
axes[0].plot([r['test_forecasts'] for r in own],[r['confirmation']['rate'] for r in own],'--',color='black',label='Known rule; nominal gain 0.010')
axes[0].set(xlabel='Synthetic test forecasts',ylabel='Confirmation probability',title='Five stars; independent observations',ylim=(0,1.02));axes[0].axhline(.8,color='.6',lw=.8);axes[0].legend(fontsize=7,loc='lower right')
choices=[('core-g0.0100-n1100','Reference'),('robust-stars3','Three stars'),('robust-stars7','Seven stars'),('robust-development40','40 development forecasts / star'),('robust-reliability08','Mark reliability 0.8'),('robust-heterogeneous05','Effect heterogeneity CV 0.5'),('robust-correlated-blocks','Within-block dependence'),('robust-serial-blocks','Serial blocks (coverage 73%)'),('robust-imbalanced','Unequal counts; 40% cap')]
for i,(key,label) in enumerate(choices):
 r=next(r for r in rows if r['id']==key and r['rule']=='fitted_rule');v=r['confirmation'];axes[1].errorbar(v['rate'],i,xerr=[[v['rate']-v['lower95']],[v['upper95']-v['rate']]],fmt='o',color='#4477AA',capsize=3)
axes[1].set(yticks=range(len(choices)),yticklabels=[p[1] for p in choices],xlabel='Confirmation probability',title='Nominal gain 0.010; 1,100 test forecasts',xlim=(0,1));axes[1].invert_yaxis();axes[1].axvline(.8,color='.6',lw=.8);axes[1].yaxis.tick_right();axes[1].tick_params(axis='y',labelsize=8)
fig.suptitle('Score-level planning: exact 95% binomial intervals; not an X5 calibration',fontsize=11)
fig.tight_layout();fig.savefig(HERE/'power-curves.png',dpi=180);fig.savefig(HERE/'power-curves.pdf');plt.close(fig)
