import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline import option_scoring


VALID_SNIPPET = """
# Strategy: Test

## Option Evaluation

| Criterion (weight) | Option A | Option B |
|---|---|---|
| Impact (x3) | 4 | 5 |
| Feasibility (x2, lower is better) | 2 | 4 |
| **Weighted Total** | 100 | 100 |

## Strategic Bets
- placeholder
"""


class TestParseOptionTable(unittest.TestCase):
    def test_parses_options_and_criteria(self):
        result = option_scoring.score_strategy_artifact(VALID_SNIPPET)
        self.assertEqual(result["options"], ["Option A", "Option B"])
        self.assertEqual(len(result["criteria"]), 2)

    def test_ignores_hand_typed_weighted_total_and_recomputes(self):
        result = option_scoring.score_strategy_artifact(VALID_SNIPPET)
        # Impact: A=4*3=12, B=5*3=15. Feasibility (lower is better, invert 6-x):
        # A: (6-2)*2=8, B: (6-4)*2=4. Totals: A=20, B=19
        self.assertAlmostEqual(result["totals"]["Option A"], 20.0)
        self.assertAlmostEqual(result["totals"]["Option B"], 19.0)
        self.assertEqual(result["top_option"], "Option A")
        # The hand-typed "100/100" in the artifact must NOT have been trusted
        self.assertNotEqual(result["totals"]["Option A"], 100)

    def test_missing_section_raises(self):
        with self.assertRaises(option_scoring.OptionScoringError):
            option_scoring.score_strategy_artifact("# Strategy: X\n\n## Strategic Bets\n- foo\n")

    def test_single_option_table_raises(self):
        text = """
## Option Evaluation

| Criterion (weight) | Option A |
|---|---|
| Impact (x1) | 4 |
"""
        with self.assertRaises(option_scoring.OptionScoringError):
            option_scoring.parse_option_table(text)

    def test_non_numeric_score_raises(self):
        text = """
## Option Evaluation

| Criterion (weight) | Option A | Option B |
|---|---|---|
| Impact (x1) | high | low |
"""
        with self.assertRaises(option_scoring.OptionScoringError):
            option_scoring.parse_option_table(text)

    def test_default_weight_is_one_when_unspecified(self):
        text = """
## Option Evaluation

| Criterion | Option A | Option B |
|---|---|---|
| Impact | 4 | 2 |
"""
        parsed = option_scoring.parse_option_table(text)
        self.assertEqual(parsed["criteria"][0][1], 1.0)


if __name__ == "__main__":
    unittest.main()
