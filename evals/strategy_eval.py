"""
Eval for the strategy stage. Run standalone:

    python -m evals.strategy_eval artifacts/strategy.md

Unlike the other generated stage evals, this one also verifies the
Option Evaluation scoring table parses and computes correctly (see
pipeline/option_scoring.py) - not just that the section exists.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from evals.rubric_base import (
    Rubric,
    RubricCriterion,
    CriterionResult,
    section_present,
    no_placeholder_text,
    mentions_product_name,
)
from pipeline.option_scoring import score_strategy_artifact, OptionScoringError


def option_scoring_parses(min_options=2):
    def _check(text, context):
        try:
            result = score_strategy_artifact(text)
        except OptionScoringError as e:
            return CriterionResult("option_evaluation_scored", False, 2, "could not score: {}".format(e))
        if len(result["options"]) < min_options:
            return CriterionResult(
                "option_evaluation_scored", False, 2,
                "only {} option(s) compared, need >= {}".format(len(result["options"]), min_options),
            )
        ranked_str = ", ".join("{}={:.1f}".format(o, t) for o, t in result["ranked"])
        return CriterionResult("option_evaluation_scored", True, 2, "ranked: {}".format(ranked_str))

    return _check


RUBRIC = Rubric(
    criteria=[
        RubricCriterion("strategic_options_present", 2, section_present("Strategic Options", min_words=15)),
        RubricCriterion("option_evaluation_present", 1, section_present("Option Evaluation", min_words=10)),
        RubricCriterion("option_evaluation_scored", 2, option_scoring_parses(min_options=2)),
        RubricCriterion("strategic_bets_present", 2, section_present("Strategic Bets", min_words=12)),
        RubricCriterion("success_metrics_present", 2, section_present("Success Metrics", min_words=12)),
        RubricCriterion("competitive_positioning_present", 2, section_present("Competitive Positioning", min_words=12)),
        RubricCriterion("constraints_present", 2, section_present("Constraints", min_words=12)),
        RubricCriterion("no_placeholders", 1, no_placeholder_text()),
        RubricCriterion("mentions_product_name", 1, mentions_product_name()),
    ],
    threshold=0.75,
)


def evaluate(artifact_text, context):
    return RUBRIC.score(artifact_text, context)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m evals.strategy_eval <path_to_strategy.md>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        text = f.read()
    context = {}
    ctx_path = os.path.join(os.path.dirname(__file__), "..", "artifacts", "context.json")
    if os.path.exists(ctx_path):
        import json
        context = json.load(open(ctx_path))
    result = evaluate(text, context)
    print(result.report())
    sys.exit(0 if result.passed else 1)
