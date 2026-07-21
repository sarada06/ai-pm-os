"""
Eval for the outcomes stage. Run standalone:

    python -m evals.outcomes_eval artifacts/outcomes.md

This is a structural rubric (same engine as vision_eval.py) checking that
required sections exist and are substantive. Tighten the per-section
word minimums or add an llm_judge_criterion (see vision_eval.py for the
pattern) as this stage matures.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from evals.rubric_base import (
    Rubric,
    RubricCriterion,
    section_present,
    no_placeholder_text,
    mentions_product_name,
)

RUBRIC = Rubric(
    criteria=[
        RubricCriterion("results_vs_north_star_present", 2, section_present("Results vs North Star", min_words=12)),
        RubricCriterion("learnings_present", 2, section_present("Learnings", min_words=12)),
        RubricCriterion("next_bets_present", 2, section_present("Next Bets", min_words=12)),
        RubricCriterion("no_placeholders", 1, no_placeholder_text()),
        RubricCriterion("mentions_product_name", 1, mentions_product_name()),
    ],
    threshold=0.7,
)


def evaluate(artifact_text, context):
    return RUBRIC.score(artifact_text, context)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m evals.outcomes_eval <path_to_outcomes.md>")
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
