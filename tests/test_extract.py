import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline import extract

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")


def _read(name):
    with open(os.path.join(EXAMPLES_DIR, name)) as f:
        return f.read()


class TestVisionExtraction(unittest.TestCase):
    def setUp(self):
        self.text = _read("sample_vision.md")
        self.result = extract.extract_stage("vision", self.text)

    def test_string_fields_extracted(self):
        self.assertIn("PulseBoard", self.result["vision_statement"])
        self.assertIn("Supply chain planners", self.result["problem_statement"])

    def test_list_fields_extracted_as_lists(self):
        self.assertEqual(len(self.result["target_users"]), 2)
        self.assertEqual(len(self.result["non_goals"]), 2)
        self.assertTrue(all(isinstance(u, str) for u in self.result["target_users"]))

    def test_missing_section_is_simply_omitted(self):
        text = "# Vision: X\n\n## Problem Statement\nSomething is wrong here badly for users today.\n"
        result = extract.extract_stage("vision", text)
        self.assertIn("problem_statement", result)
        self.assertNotIn("vision_statement", result)


class TestDiscoveryExtraction(unittest.TestCase):
    def test_personas_parsed_as_name_description_objects(self):
        text = _read("sample_discovery.md")
        result = extract.extract_stage("discovery", text)
        self.assertEqual(len(result["personas"]), 2)
        self.assertEqual(result["personas"][0]["name"], "Priya, Senior Demand Planner")
        self.assertIn("forecast accuracy", result["personas"][0]["description"])

    def test_plain_bullets_fall_back_to_text_objects(self):
        text = "# Discovery: X\n\n## Personas\n- Just a plain bullet with no colon\n"
        result = extract.extract_stage("discovery", text)
        self.assertEqual(result["personas"], [{"text": "Just a plain bullet with no colon"}])


class TestRoadmapExtraction(unittest.TestCase):
    def test_now_next_later_become_horizons(self):
        text = _read("sample_roadmap.md")
        result = extract.extract_roadmap(text)
        names = [h["name"] for h in result["horizons"]]
        self.assertEqual(names, ["Now", "Next", "Later"])
        self.assertTrue(len(result["horizons"][0]["themes"]) >= 1)

    def test_missing_horizon_omitted_not_empty(self):
        text = "# Roadmap: X\n\n## Now\n- Ship thing one\n"
        result = extract.extract_roadmap(text)
        names = [h["name"] for h in result["horizons"]]
        self.assertEqual(names, ["Now"])


class TestApplyExtraction(unittest.TestCase):
    def test_merges_into_existing_context_without_clobbering(self):
        context = {"vision": {"problem_statement": "old value", "north_star_metric": "keep me"}}
        text = "# Vision: X\n\n## Problem Statement\nA new problem statement with enough words in it now.\n"
        context, extracted = extract.apply_extraction(context, "vision", text)
        self.assertNotEqual(context["vision"]["problem_statement"], "old value")
        self.assertEqual(context["vision"]["north_star_metric"], "keep me")


if __name__ == "__main__":
    unittest.main()
