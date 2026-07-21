"""
Eval for the mvp stage. Run standalone:

    python -m evals.mvp_eval artifacts/mvp.md

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
        RubricCriterion("scope_in_present", 2, section_present("Scope In", min_words=12)),
        RubricCriterion("scope_out_present", 2, section_present("Scope Out", min_words=12)),
        RubricCriterion("success_criteria_present", 2, section_present("Success Criteria", min_words=12)),
        RubricCriterion("no_placeholders", 1, no_placeholder_text()),
        RubricCriterion("mentions_product_name", 1, mentions_product_name()),
    ],
    threshold=0.75,
)


def evaluate(artifact_text, context):
    return RUBRIC.score(artifact_text, context)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m evals.mvp_eval <path_to_mvp.md>")
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
