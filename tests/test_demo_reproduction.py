from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_demo_reproduction import compare_csv, compare_summary


class ReproductionTests(unittest.TestCase):
    def test_only_floating_columns_allow_roundoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            reference, actual = Path(tmp) / "reference.csv", Path(tmp) / "actual.csv"
            reference.write_text("id,value,flag\n1,10.0,True\n")
            actual.write_text("id,value,flag\n1,10.00000000000001,True\n")
            self.assertEqual(compare_csv(reference, actual, {"value"})["changed_numeric_cells"], 1)
            for row in ("1,10.01,True", "1,10.0,False", "1.0,10.0,True", "1,nan,True", "1,inf,True", "1,,True"):
                actual.write_text(f"id,value,flag\n{row}\n")
                with self.subTest(row=row), self.assertRaises(ValueError):
                    compare_csv(reference, actual, {"value"})

    def test_table_structure_and_row_order_are_exact(self):
        with tempfile.TemporaryDirectory() as tmp:
            reference, actual = Path(tmp) / "reference.csv", Path(tmp) / "actual.csv"
            reference.write_text("id,value\n1,10\n2,20\n")
            for text in ("id,value\n1,10\n", "id,other\n1,10\n2,20\n", "id,value\n2,20\n1,10\n", "id,value\n1,10,extra\n2,20\n"):
                actual.write_text(text)
                with self.subTest(text=text), self.assertRaises(ValueError):
                    compare_csv(reference, actual, {"value"})

    def test_summary_scores_and_counts_are_checked(self):
        reference = {"score": -4.2, "counts": [12, True]}
        compare_summary(reference, {"score": -4.200000000000001, "counts": [12, True]})
        for change in ({"score": -4.1, "counts": [12, True]},
                       {"score": -4.2, "counts": [13, True]},
                       {"score": -4.2, "counts": [12.0, True]},
                       {"score": -4.2, "counts": [12, False]},
                       {"score": float("nan"), "counts": [12, True]}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                compare_summary(reference, change)


if __name__ == "__main__":
    unittest.main()
