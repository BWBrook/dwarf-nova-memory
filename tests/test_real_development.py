import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dnmem.real_development import require_gate, load_native, collect_ledgers, digest, fit_variant
from test_directional_forecast import fixture


class RealDevelopmentBoundaryTests(unittest.TestCase):
    def gate_fixture(self, root, *, pass_screen=True, coverage=True):
        cases = [('v2-phase', c) for c in ('null', 'structured', 'gross', 'offset', 'adaptive')]+[('v4-phase', 'null')]
        summary = {'complete':True, 'screen_pass':pass_screen,
                   'null_rate_checks':[{'family':f, 'case':c, 'successes':0, 'trials':20 if f=='v4-phase' else 40, 'screen_pass':True} for f,c in cases],
                   'calibration':[{'case':c,'cluster_years':6,'pass':coverage} for c in ('null','alternative')]}
        (root/'summary.json').write_text(json.dumps(summary))
        (root/'records.json').write_text('[]')
        receipt = {'status':'completed','trials':360,'successful_trials':360,'failed_trials':0,
                   'source':{'head':'synthetic-freeze'},
                   'files_sha256':{name:digest(root/name) for name in ('summary.json','records.json')}}
        (root/'receipt.json').write_text(json.dumps(receipt))
        return {'simulation_receipt_sha256':digest(root/'receipt.json'),'simulation_source':'synthetic-freeze'}

    def test_failed_or_changed_simulation_gate_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for screen,coverage in ((False,True),(True,False)):
                config=self.gate_fixture(root,pass_screen=screen,coverage=coverage)
                with self.assertRaises(ValueError):require_gate(root,config)
            config=self.gate_fixture(root)
            require_gate(root,config)
            (root/'summary.json').write_text('{}')
            with self.assertRaises(ValueError):require_gate(root,config)

    def test_hash_mismatch_and_reserved_path_precede_native_parsing(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            p=root/'aavso_ss_cyg_fixture'/'native.xml';p.parent.mkdir();p.write_text('synthetic')
            config={'expected_acquisitions':1,'native_start_jd':1.,'native_stop_jd':10.}
            with patch('dnmem.real_development.combine_acquisitions') as parse:
                with self.assertRaises(ValueError):load_native(root,{'source_sha256':{p.parent.name:'wrong'}},config)
                parse.assert_not_called()
            quarantine=root/'quarantine';quarantine.mkdir()
            with patch('dnmem.real_development.combine_acquisitions') as parse:
                with self.assertRaises(ValueError):load_native(quarantine,{},config)
                parse.assert_not_called()
            with patch('dnmem.real_development.combine_acquisitions',return_value=([{'JD':'11'}],0)):
                with self.assertRaises(ValueError):load_native(root,{'source_sha256':{p.parent.name:digest(p)}},config)

    def test_evaluation_rows_are_rejected_before_prefix_construction(self):
        with patch('dnmem.real_development.prefix_features.forecast_ledger') as extract:
            with self.assertRaises(ValueError):collect_ledgers([{'JD':'20'}],{'start_jd':1.,'stop_jd':20.})
            extract.assert_not_called()

    def test_fixture_fit_is_labeled_in_sample_and_keeps_nesting(self):
        ledger,evidence=fixture(constant_mark=True)
        for row in evidence:row['reason']='fixture'
        bundle,scores,summary=fit_variant(ledger,evidence,10000.,('primary','point',True,'log_duration',0.,False))
        self.assertEqual(summary['scored'],len(ledger))
        self.assertEqual(summary['mean_in_sample_gain']['M3_M2'],0.)
        self.assertEqual(summary['log_likelihood']['M3'],summary['log_likelihood']['M2'])
        self.assertIn('not held-out',summary['interpretation'])


if __name__=='__main__':unittest.main()
