"""
Eval for the vision stage. Run standalone:

    python -m evals.vision_eval artifacts/vision.md

Or imported by pipeline/runner.py after the vision-agent generates
artifacts/vision.md, to decide whether the pipeline gates forward to
discovery.
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
    llm_judge_criterion,
)

RUBRIC = Rubric(
    criteria=[
        RubricCriterion("problem_statement_present", 2, section_present("Problem Statement", min_words=25)),
        RubricCriterion("target_users_present", 1, section_present("Target Users", min_words=10)),
        RubricCriterion("vision_statement_present", 2, section_present("Vision Statement", min_words=15)),
        RubricCriterion("north_star_metric_present", 1, section_present("North Star Metric", min_words=5)),
        RubricCriterion("non_goals_present", 1, section_present("Non-Goals", min_words=5)),
        RubricCriterion("no_placeholders", 1, no_placeholder_text()),
        RubricCriterion("mentions_product_name", 1, mentions_product_name()),
        RubricCriterion(
            "llm_judge",
            2,
            llm_judge_criterion(
                "You are grading a product vision document. PASS only if the problem "
                "statement is specific (not generic corporate-speak), the vision statement "
                "is inspiring but concrete, and the north star metric is genuinely "
                "measurable. FAIL if it's vague, buzzword-heavy, or could apply to any product."
            ),
        ),
    ],
    threshold=0.75,
)


def evaluate(artifact_text, context):
    return RUBRIC.score(artifact_text, context)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m evals.vision_eval <path_to_vision.md>")
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
