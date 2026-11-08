import importlib.util
import math
from pathlib import Path
import unittest

from scipy.stats import beta, t


ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'scripts'/f'{name}.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


SCORES = module('check_a10d_scores')
AGGREGATE = module('check_a10d_aggregate')


class IndependentAuditorRegressionTests(unittest.TestCase):
    def test_one_sided_upper_bound_uses_the_upper_tail_for_nonzero_counts(self):
        for count in (20, 40):
            for successes in range(count+1):
                expected = float(beta.ppf(.95, successes+1, count-successes)) if successes < count else 1.
                self.assertAlmostEqual(AGGREGATE.one_sided_binomial_upper95(successes, count), expected, places=12)

    def test_both_mark_models_honor_their_own_exact_zero_offset(self):
        feature = {'previous_gap': 20., 'previous_gap_covered': True, 'previous_duration': 8.}
        for name in ('M3', 'P3'):
            self.assertEqual(SCORES.route_for(name, feature, True, True, True), 'M2')
            self.assertEqual(SCORES.route_for(name, feature, True, True, False), name)

    def test_independent_welch_interval_and_noninteger_t_quantiles(self):
        for degrees in (2., 5.4, 9., 13.467611856, 19.):
            self.assertAlmostEqual(AGGREGATE.student_t_ppf(.95, degrees), float(t.ppf(.95, degrees)), places=9)
        original = {'estimate': .006, 'se': .001, 'blocks': 10}
        means = [-.01, 0., .01, -.01, 0., .01]
        result = AGGREGATE.reference_interval(original, means, False)
        refvar = sum(x*x for x in means)/(len(means)-1)/len(means)
        variance = original['se']**2+refvar
        df = variance**2/(original['se']**4/9+refvar**2/5)
        radius = float(t.ppf(.95, df))*math.sqrt(variance)
        self.assertAlmostEqual(result['lower'], .006-radius, places=12)
        self.assertAlmostEqual(result['upper'], .006+radius, places=12)
        self.assertTrue(result['joint_mc_covers_zero'])


if __name__ == '__main__':
    unittest.main()
