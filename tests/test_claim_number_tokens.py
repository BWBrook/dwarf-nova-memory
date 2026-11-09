import importlib.util
from decimal import Decimal
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("claims", Path(__file__).resolve().parents[1]/"tools/claims.py")
claims = importlib.util.module_from_spec(spec)
spec.loader.exec_module(claims)


class ClaimNumberTests(unittest.TestCase):
    def test_digest_prefixes_cannot_supply_numeric_claim_evidence(self):
        digest = "71e9592289c3e61db07cfe7495ade18978a445c6ebe76ae73d04ace5c719e705"
        for prose in (False, True):
            self.assertEqual(claims.numbers('"'+digest+'"', prose), [])
            self.assertEqual(claims.numbers('gain 0.818; error 7.1e-14.', prose),
                             [(False, Decimal('0.818')), (False, Decimal('7.1e-14'))])
        self.assertEqual(claims.numbers('trials 70,000; derived ~0.01.'),
                         [(False, Decimal('70000')), (True, Decimal('0.01'))])


if __name__ == "__main__":
    unittest.main()
