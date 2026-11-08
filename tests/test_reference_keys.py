import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("seed_reference_validation", ROOT / "scripts/validate_seed.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ReferenceKeyTests(unittest.TestCase):
    def test_generator_id_form_and_empty_placeholder_are_recognized(self):
        content = """---
references:
- id: cannizzo1992LongTermBehavior
  citation-key: cannizzo1992LongTermBehavior
  type: article-journal
  title: On the long-term behavior of SS Cygni
  author:
  - family: Cannizzo
    given: John K.
- id: gneiting2007StrictlyProperScoring
  citation-key: gneiting2007StrictlyProperScoring
  type: article-journal
...
"""
        self.assertEqual(VALIDATOR.csl_yaml_keys(content), {
            "cannizzo1992LongTermBehavior", "gneiting2007StrictlyProperScoring"
        })
        self.assertEqual(VALIDATOR.csl_yaml_keys("---\nreferences: []\n...\n"), set())

    def test_duplicate_and_shadowed_ids_fail(self):
        for content in (
            "references:\n- id: same2026Paper\n- id: same2026Paper\n",
            "references:\n- id: first2026Paper\n  id: second2026Paper\n",
        ):
            with self.subTest(content=content), self.assertRaisesRegex(ValueError, "duplicate"):
                VALIDATOR.csl_yaml_keys(content)

    def test_unsupported_structure_and_id_forms_fail(self):
        for content in (
            "- id: first2026Paper\n",
            "references:\n  - id: first2026Paper\n",
            "references:\n- title: Not an ID\n",
            "references:\n- id: bad key\n",
            "references:\n- id: 'quoted2026Key'\n",
            "references: []\n- id: extra2026Paper\n",
            "references:\n",
        ):
            with self.subTest(content=content), self.assertRaises(ValueError):
                VALIDATOR.csl_yaml_keys(content)

    def test_both_citation_namespaces_are_known_but_unknown_keys_fail(self):
        keys = {"CannizzoMattei1992", "cannizzo1992LongTermBehavior"}
        content = "Legacy [@CannizzoMattei1992]; generated [@cannizzo1992LongTermBehavior]."
        self.assertEqual(VALIDATOR.unknown_citations(content, keys), [])
        self.assertEqual(VALIDATOR.unknown_citations(content + " [@missing2026Paper; @missing2026Paper]", keys),
                         ["missing2026Paper"])


if __name__ == "__main__":
    unittest.main()
