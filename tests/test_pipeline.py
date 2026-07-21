"""
Minimal test suite. Run with: python -m pytest tests/ -v
(or python -m unittest discover tests if pytest isn't installed)
"""

import os
import sys
import shutil
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline import state
from pipeline.stage_config import STAGES, STAGE_NAMES, get_stage, next_stage
from evals import vision_eval

TEST_ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "_test_artifacts")


class TestStageConfig(unittest.TestCase):
    def test_nine_stages_defined(self):
        self.assertEqual(len(STAGES), 9)

    def test_stage_order_matches_readme(self):
        expected = [
            "vision", "discovery", "strategy", "roadmap", "mvp",
            "prd", "validation", "phased_rollout", "outcomes",
        ]
        self.assertEqual(STAGE_NAMES, expected)

    def test_next_stage_chains_correctly(self):
        self.assertEqual(next_stage("vision"), "discovery")
        self.assertEqual(next_stage("outcomes"), None)

    def test_get_stage_unknown_raises(self):
        with self.assertRaises(ValueError):
            get_stage("not_a_real_stage")


class TestContextState(unittest.TestCase):
    def setUp(self):
        os.makedirs(TEST_ARTIFACTS_DIR, exist_ok=True)
        self.path = os.path.join(TEST_ARTIFACTS_DIR, "context.json")

    def tearDown(self):
        shutil.rmtree(TEST_ARTIFACTS_DIR, ignore_errors=True)

    def test_init_and_load_roundtrip(self):
        state.init_context("TestProduct", "A test one-liner", path=self.path)
        loaded = state.load_context(self.path)
        self.assertEqual(loaded["product_name"], "TestProduct")
        self.assertEqual(loaded["current_stage"], "vision")
        self.assertEqual(loaded["stage_history"], [])

    def test_record_stage_run_appends_history(self):
        ctx = state.init_context("TestProduct", path=self.path)
        ctx = state.record_stage_run(ctx, "vision", 0.9, True, 1, "artifacts/vision.md")
        state.save_context(ctx, self.path)
        loaded = state.load_context(self.path)
        self.assertEqual(len(loaded["stage_history"]), 1)
        self.assertTrue(loaded["stage_history"][0]["eval_pass"])

    def test_load_missing_context_raises(self):
        with self.assertRaises(FileNotFoundError):
            state.load_context(os.path.join(TEST_ARTIFACTS_DIR, "does_not_exist.json"))


class TestVisionEval(unittest.TestCase):
    def test_strong_artifact_passes(self):
        text = open(
            os.path.join(os.path.dirname(__file__), "..", "examples", "sample_vision.md")
        ).read()
        result = vision_eval.evaluate(text, {"product_name": "PulseBoard"})
        self.assertTrue(result.passed)

    def test_weak_artifact_fails(self):
        text = "# Vision\n\n## Problem Statement\nTODO\n"
        result = vision_eval.evaluate(text, {"product_name": "PulseBoard"})
        self.assertFalse(result.passed)


if __name__ == "__main__":
    unittest.main()
