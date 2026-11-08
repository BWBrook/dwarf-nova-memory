import math
import unittest
from scipy.special import ndtr
from dnmem.directional_forecast import fit_directional
from dnmem.forecast_calibration import predictive_cdf,predictive_quantile,coverage_class,calibration_summary
from test_directional_forecast import fixture


class FrozenCalibrationTests(unittest.TestCase):
    def test_cdf_and_quantiles_condition_on_survival_exactly_once(self):
        features,outcomes=fixture()
        bundle=fit_directional(features,outcomes,10000.)
        f=features[1];m=bundle.models['M0'];age=f['issue_time']-f['end_t'];h=13.
        sf=lambda x:float(ndtr(-(math.log(x)-m.intercept)/m.sigma))
        expected=1-sf(age+h)/sf(age)
        self.assertAlmostEqual(predictive_cdf(bundle,f,'M0',h),expected,places=11)
        for p in (.05,.25,.75,.95):
            q=predictive_quantile(bundle,f,'M0',p)
            self.assertAlmostEqual(predictive_cdf(bundle,f,'M0',q),p,places=10)

    def test_censoring_and_overlapping_intervals_are_not_assumed_covered(self):
        interval=lambda lo,hi:{'kind':'interval','issue_time':100.,'onset_lo':100+lo,'onset_hi':100+hi}
        self.assertEqual(coverage_class(interval(3,4),2,6),'covered')
        self.assertEqual(coverage_class(interval(0,1),2,6),'not_covered')
        self.assertEqual(coverage_class(interval(1,3),2,6),'undetermined')
        censor=lambda at:{'kind':'right_censored','issue_time':100.,'censor_at':100+at}
        self.assertEqual(coverage_class(censor(6),2,6),'not_covered')
        self.assertEqual(coverage_class(censor(5),2,6),'undetermined')

    def test_pit_population_and_coverage_bounds_include_censored_issuances(self):
        features,outcomes=fixture(n=12)
        bundle=fit_directional(features,outcomes,10000.)
        result=calibration_summary(bundle,features,outcomes)
        for row in result['models'].values():
            self.assertEqual(row['scored'],12)
            self.assertEqual(sum(row['resolved_onset_mid_cdf_deciles']),row['resolved_onsets'])
            self.assertEqual(row['resolved_onsets']+row['right_censored'],12)
            for v in row['central_intervals'].values():
                self.assertLessEqual(v['coverage_lower_bound'],v['coverage_upper_bound'])
                self.assertEqual(sum(v[k] for k in ('covered','not_covered','undetermined')),12)


if __name__=='__main__':unittest.main()
