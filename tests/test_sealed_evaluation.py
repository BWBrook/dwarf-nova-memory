import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dnmem.evaluation import evaluate_frozen
from dnmem.evaluation_acquire import acquire
from dnmem.evaluation_native import RowCapError,parse_native_bytes,select_analysis_rows
from dnmem.evaluation_rehearsal import native_payload
from dnmem.prefix_features import forecast_ledger,outcome_evidence
from test_prefix_features import outbursts

ROOT=Path(__file__).resolve().parents[1]


class SealedEvaluationTests(unittest.TestCase):
    def test_mismatch_stops_before_scoring_and_primary_file(self):
        feature={'emission_index':0,'issue_time':2437000.}
        other={**feature,'duration':99.}
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)
            with patch('dnmem.evaluation.prefix_features.forecast_ledger',return_value=[feature]),\
                 patch('dnmem.evaluation.prefix_reference.forecast_ledger',return_value=[other]),\
                 patch('dnmem.evaluation.prefix_features.outcome_evidence',return_value=[]),\
                 patch('dnmem.evaluation.prefix_reference.outcome_evidence',return_value=[]):
                with self.assertRaisesRegex(ValueError,'mismatch'):
                    evaluate_frozen([],ROOT/'data/fits/a10e_1910_1959/frozen_parameters.json',path)
            self.assertFalse((path/'primary.json').exists())
            self.assertFalse(json.loads((path/'concordance.json').read_text())['0.0']['match'])

    def test_modern_nonanalysis_rows_change_no_predictor_or_evidence(self):
        rows=outbursts()
        extras=[{**row,'band':'V','mag':'1.0','obsID':'ccd-'+row['obsID']} for row in rows]
        extras += [{**row,'val':'D','mag':'1.0','obsID':'bad-'+row['obsID']} for row in rows]
        raw=rows+extras;filtered=select_analysis_rows(raw)
        a=forecast_ledger(raw);b=forecast_ledger(filtered)
        for x,y in zip(a,b):
            x.pop('prefix_rows');y.pop('prefix_rows')
            x.pop('prefix_last_jd');y.pop('prefix_last_jd')
        self.assertEqual(a,b)
        self.assertEqual(outcome_evidence(raw,a,stop=200.),outcome_evidence(filtered,b,stop=200.))

    def test_missing_uncertainty_sentinel_changes_no_forecast_or_outcome(self):
        from dnmem.directional_forecast import DirectionalBundle
        start,stop=2436935.,2437135.
        blank=[{**r,'JD':str(float(r['JD'])+start),'uncert':''} for r in outbursts()]
        absent=[{**r,'uncert':'None'} for r in blank]
        left,_=parse_native_bytes(native_payload(blank),start_jd=start,end_jd=stop)
        right,_=parse_native_bytes(native_payload(absent),start_jd=start,end_jd=stop)
        a,b=forecast_ledger(left),forecast_ledger(right)
        ea,eb=outcome_evidence(left,a,stop=stop),outcome_evidence(right,b,stop=stop)
        self.assertTrue(a)
        self.assertEqual(a,b)
        self.assertEqual(ea,eb)
        params=json.loads((ROOT/'data/fits/a10e_1910_1959/frozen_parameters.json').read_text())
        model=DirectionalBundle.from_dict(params['primary'])
        self.assertEqual(model.scores(a,ea),model.scores(b,eb))

    def test_response_is_receipted_before_parse_and_cap_parents_are_retained(self):
        row={'obsID':'synthetic','JD':'2436934.5','mag':'12','uncert':'','fainterThan':'0','band':'Vis.','by':'SIM','val':'V'}
        transport=lambda lo,hi,url:(native_payload([row]),{})
        states=[]
        def callback(record):states.append(record['status'])
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'raw'
            with patch('dnmem.evaluation_acquire.calendar_windows',return_value=[(2436934.,2436935.)]),\
                 patch('dnmem.evaluation_acquire.parse_native_bytes',side_effect=[RowCapError('cap'),([],{}),([],{})]):
                paths,manifest=acquire(root,transport,mode='rehearsal',receipt_callback=callback)
            self.assertEqual(states,['retained_before_parsing']*3)
            self.assertEqual(len(paths),2)
            self.assertEqual(len(manifest),3)
            self.assertEqual(manifest[0]['status'],'split_parent_row_cap')
            self.assertEqual(len(list(root.glob('*/native.xml'))),3)

    def test_live_transport_never_runs_without_committed_authority(self):
        spec=importlib.util.spec_from_file_location('sealed_driver',ROOT/'scripts/a10g_evaluation.py')
        driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as folder:
            args=SimpleNamespace(mode='live',freeze_commit='synthetic',output=Path(folder)/'unopened')
            with patch.object(driver,'source_proof',return_value={}),\
                 patch.object(driver,'live_transport') as network,\
                 patch.object(driver,'require_authorization',side_effect=PermissionError('not authorized')):
                with self.assertRaises(PermissionError):driver.run(args)
                network.assert_not_called()
                self.assertFalse(args.output.exists())


if __name__=='__main__':unittest.main()
