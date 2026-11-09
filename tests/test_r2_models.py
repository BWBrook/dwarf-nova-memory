import copy
import json
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np
from scipy.optimize import OptimizeResult
from scipy.stats import lognorm

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dnmem.r2_models import ConditionalClock, TimingRule, filter_history, fit_ladder, history_values


def fixture(n=35):
    rng = np.random.default_rng(6451)
    rows, evidence = [], []
    for i in range(n):
        end = 1000. + 100 * i
        history = [3.5 + .15 * math.sin(i + j) for j in range(6)]
        mark = float(math.exp(2.4 + .3 * math.sin(i)))
        wait = float(math.exp(3.5 + .13 * math.sin(i) + .3 * rng.normal()))
        rows.append({"emission_index": i, "issue_time": end + 1., "available_at": end + 1.,
                     "clock_anchor": end, "mark": mark, "previous_gap": math.exp(history[-1]),
                     "previous_gap_covered": True,
                     "gap_history": [{"log_gap": v, "available_at": end} for v in history]})
        evidence.append({"emission_index": i, "issue_time": end + 1., "kind": "point",
                         "onset_t": end + wait, "computed_as_of": 10000., "evidence_available_at": 10000.})
    return rows, evidence


class ClockTests(unittest.TestCase):
    def test_density_survival_and_interval_match_independent_scipy(self):
        clock = ConditionalClock(10., 13., 3., .5)
        den = lognorm.logsf(3., s=.5, scale=math.exp(3.))
        for t in (13., 20., 45., 100.):
            self.assertAlmostEqual(clock.log_survival(t), lognorm.logsf(t-10., s=.5, scale=math.exp(3.))-den, places=13)
            if t > 13:
                self.assertAlmostEqual(clock.log_density(t), lognorm.logpdf(t-10., s=.5, scale=math.exp(3.))-den, places=13)
        mass = lognorm.cdf(25., s=.5, scale=math.exp(3.)) - lognorm.cdf(15., s=.5, scale=math.exp(3.))
        self.assertAlmostEqual(clock.log_interval(25., 35.), math.log(mass)-den, places=13)
        self.assertEqual(clock.log_survival(13.), 0.)
        self.assertEqual(clock.log_density(13.), -math.inf)

    def test_invalid_landmark_and_score_support_are_rejected(self):
        with self.assertRaises(ValueError):
            ConditionalClock(15., 13., 3., .5)
        clock = ConditionalClock(10., 13., 3., .5)
        with self.assertRaises(ValueError):
            clock.log_survival(12.)
        with self.assertRaises(ValueError):
            clock.log_interval(12., 20.)


class SyntheticStreamTests(unittest.TestCase):
    def test_controls_separate_development_labels_and_prior_gap_history(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
        from r2a_model_controls import generate
        for case in ('stationary','drifting','duration'):
            rows,evidence,truth,meta=generate(case,0)
            training=[r for r in rows if r['issue_time']<meta['training_cutoff']]
            self.assertEqual(len(training),120)
            for i,row in enumerate(rows):
                if row['previous_gap'] is not None:
                    expected=truth[i-1]['onset_t']-(rows[i-1]['issue_time']-2.)
                    self.assertAlmostEqual(row['previous_gap'],expected,places=10)
                self.assertTrue(all(v['available_at']<=row['issue_time'] for v in row['gap_history']))
            for outcome in evidence[:120]:
                end=(outcome['onset_hi'] if outcome['kind']=='interval' else outcome['censor_at']
                     if outcome['kind']=='right_censored' else outcome['onset_t'])
                self.assertLessEqual(end,outcome['evidence_available_at'])
                self.assertLessEqual(outcome['evidence_available_at'],meta['training_cutoff'])


class FilterTests(unittest.TestCase):
    def test_filter_matches_joint_gaussian_conditioning_with_missing_values(self):
        values = [3.4, None, 3.7, 3.3]
        mu, phi, level_sd, ar_sd = 3.5, .6, .04, .3
        f = np.diag([1., phi]);q = np.diag([level_sd**2, ar_sd**2])
        p = np.diag([1., ar_sd**2/(1-phi**2)]);h = np.ones(2)
        def covariance(i, j):
            v = np.linalg.matrix_power(f, i) @ p @ np.linalg.matrix_power(f, j).T
            for k in range(1, min(i,j)+1):
                v += np.linalg.matrix_power(f, i-k) @ q @ np.linalg.matrix_power(f,j-k).T
            return float(h @ v @ h)
        indices = [i+1 for i,v in enumerate(values) if v is not None]
        target = len(values)+1
        cov = np.array([[covariance(i,j) for j in indices] for i in indices])
        cross = np.array([covariance(target,i) for i in indices])
        residual = np.array([v-mu for v in values if v is not None])
        expected_mu = mu + cross @ np.linalg.solve(cov,residual)
        expected_var = covariance(target,target)-cross @ np.linalg.solve(cov,cross)
        actual_mu, actual_sd = filter_history(values,mu,phi,level_sd,ar_sd)
        self.assertAlmostEqual(actual_mu,float(expected_mu),places=12)
        self.assertAlmostEqual(actual_sd**2,float(expected_var),places=12)

    def test_missing_updates_grow_uncertainty_and_inputs_are_unchanged(self):
        values = [3.5,3.6,3.4]
        before = list(values)
        measured = filter_history(values,3.5,.5,.04,.3)
        missing = filter_history([3.5,None,None],3.5,.5,.04,.3)
        self.assertGreater(missing[1],measured[1])
        self.assertEqual(values,before)

    def test_future_history_and_inconsistent_gap_are_rejected(self):
        rows,_ = fixture()
        row = copy.deepcopy(rows[0]);row['gap_history'][0]['available_at']=row['issue_time']+1
        with self.assertRaisesRegex(ValueError,'available'):
            history_values(row)
        row = copy.deepcopy(rows[0]);row['previous_gap']*=2
        model = TimingRule('B2',[3.5,.5,math.log(.04),math.log(.3)],[],0.,[3.5,.4],[3.5,.4],2.4,.3,0.,{})
        with self.assertRaisesRegex(ValueError,'disagree'):
            model.predict(row)


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows,cls.evidence=fixture()
        cls.models=fit_ladder(cls.rows,cls.evidence,10000.)

    def test_zero_offset_missing_mark_and_fallbacks_are_exact(self):
        for name,model in self.models.items():
            zero=TimingRule.from_dict(dict(model.to_dict(),beta=0.))
            self.assertEqual(zero.predict(self.rows[0]),zero.predict(self.rows[0],True))
            missing=dict(self.rows[0],mark=None)
            self.assertEqual(model.predict(missing),model.predict(missing,True))
            noanchor=dict(self.rows[0],clock_anchor=None)
            self.assertEqual(model.predict(noanchor),model.predict(noanchor,True))
            noq=copy.deepcopy(self.rows[0]);noq.update(previous_gap=None,previous_gap_covered=False);noq['gap_history'][-1]['log_gap']=None
            self.assertEqual(model.predict(noq),model.predict(noq,True))

    def test_mark_offset_preserves_variance_and_base_parameters(self):
        for name,model in self.models.items():
            positive=TimingRule.from_dict(dict(model.to_dict(),beta=.1))
            plain=positive.predict(self.rows[0])[0];marked=positive.predict(self.rows[0],True)[0]
            expected=.1*(math.log(self.rows[0]['mark'])-positive.mark_center)/positive.mark_scale
            self.assertEqual(plain.sigma,marked.sigma)
            self.assertAlmostEqual(marked.mu-plain.mu,expected,places=14)
            self.assertTrue(model.metadata['offset_fit']['timing_parameters_fixed'])
        self.assertEqual(len({(m.mark_center,m.mark_scale) for m in self.models.values()}),1)

    def test_json_serialization_and_future_rows_do_not_change_prediction(self):
        for model in self.models.values():
            restored=TimingRule.from_dict(json.loads(json.dumps(model.to_dict())))
            self.assertEqual(restored.predict(self.rows[3],True),model.predict(self.rows[3],True))
        original=self.models['B2'].predict(self.rows[0],True)
        changed=copy.deepcopy(self.rows);changed[-1]['mark']=1000000.
        self.assertEqual(self.models['B2'].predict(changed[0],True),original)

    def test_training_availability_and_optimizer_failure_are_explicit(self):
        with self.assertRaisesRegex(ValueError,'freeze'):
            fit_ladder(self.rows,[dict(r,computed_as_of=10001.) for r in self.evidence],10000.)
        with self.assertRaisesRegex(ValueError,'freeze'):
            fit_ladder(self.rows,[dict(r,evidence_available_at=math.nan) for r in self.evidence],10000.)
        with self.assertRaisesRegex(ValueError,'support'):
            fit_ladder(self.rows,[dict(r,onset_t=10001.) for r in self.evidence],10000.)
        failed=OptimizeResult(success=False,x=np.array([3.5,-1.]),fun=100.,message='forced failure',nit=1)
        with patch('dnmem.r2_models.minimize',return_value=failed):
            with self.assertRaisesRegex(ValueError,'optimization failed'):
                fit_ladder(self.rows,self.evidence,10000.)

    def test_duplicate_lambda_zero_terms_are_reported_not_treated_as_identified(self):
        zero=next(r for r in self.models['B1'].metadata['discount_profile'] if r['discount']==0.)
        self.assertTrue(zero['rank_deficient'])
        self.assertLess(zero['design_rank'],zero['design_columns'])

    def test_all_censored_training_is_not_accepted_as_identified(self):
        censored=[dict(r,kind='right_censored',censor_at=r['issue_time']+10.) for r in self.evidence]
        with self.assertRaisesRegex(ValueError,'resolved'):
            fit_ladder(self.rows,censored,10000.)


if __name__=='__main__':
    unittest.main()
