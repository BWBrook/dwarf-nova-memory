import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("benchmark_preparation", ROOT / "scripts/calibrate_x3_benchmark.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PreparationIdentityTests(unittest.TestCase):
    def test_exact_identity_hashes_and_membership_are_required(self):
        with tempfile.TemporaryDirectory() as temp:
            paths, hashes = [], {}
            for k in range(12):
                p = Path(temp) / str(k) / "native.xml"
                p.parent.mkdir()
                p.write_bytes(str(k).encode())
                paths.append(p)
                hashes[str(k)] = hashlib.sha256(p.read_bytes()).hexdigest()
            self.assertEqual(MODULE.checked_sources(paths, hashes), hashes)
            with self.assertRaisesRegex(ValueError, "frozen"):
                MODULE.checked_sources(paths[:-1], hashes)
            paths[0].write_bytes(b"changed but still valid provider export")
            with self.assertRaisesRegex(ValueError, "frozen"):
                MODULE.checked_sources(paths, hashes)


if __name__ == "__main__":
    unittest.main()
