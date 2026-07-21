"""
Eval for the phased_rollout stage. Run standalone:

    python -m evals.phased_rollout_eval artifacts/phased_rollout.md

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
        RubricCriterion("rollout_phases_present", 2, section_present("Rollout Phases", min_words=12)),
        RubricCriterion("rollback_plan_present", 2, section_present("Rollback Plan", min_words=12)),
        RubricCriterion("guardrail_metrics_present", 2, section_present("Guardrail Metrics", min_words=12)),
        RubricCriterion("no_placeholders", 1, no_placeholder_text()),
        RubricCriterion("mentions_product_name", 1, mentions_product_name()),
    ],
    threshold=0.75,
)


def evaluate(artifact_text, context):
    return RUBRIC.score(artifact_text, context)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m evals.phased_rollout_eval <path_to_phased_rollout.md>")
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
