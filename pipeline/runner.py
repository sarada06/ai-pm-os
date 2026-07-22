"""
CLI driver for the AI PM OS pipeline. This is the tool the orchestrator
subagent (.claude/agents/orchestrator.md) shells out to via Bash after each
stage subagent generates an artifact - it does NOT call the LLM itself.

Usage:
    python -m pipeline.runner init --product-name "Foo" --one-liner "Bar"
    python -m pipeline.runner eval vision
    python -m pipeline.runner eval vision --artifact artifacts/vision.md --attempt 2
    python -m pipeline.runner status
"""

import argparse
import importlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline import state, extract, option_scoring
from pipeline.stage_config import get_stage, next_stage, STAGE_NAMES

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")


def cmd_init(args):
    domain_context = ""
    if args.domain_context_file:
        with open(args.domain_context_file) as f:
            domain_context = f.read()
    context = state.init_context(args.product_name, args.one_liner, domain_context)
    print("Initialized context.json for '{}'. Current stage: {}".format(
        args.product_name, context["current_stage"]
    ))
    if domain_context:
        print("Loaded domain context from {} ({} chars)".format(
            args.domain_context_file, len(domain_context)
        ))


def cmd_set_domain_context(args):
    context = state.load_context()
    with open(args.file) as f:
        domain_context = f.read()
    context = state.set_domain_context(context, domain_context)
    state.save_context(context)
    print("Updated domain context from {} ({} chars)".format(args.file, len(domain_context)))


def cmd_eval(args):
    stage_cfg = get_stage(args.stage)
    artifact_path = args.artifact or os.path.join(ARTIFACTS_DIR, stage_cfg["artifact_file"])
    if not os.path.exists(artifact_path):
        print("Artifact not found: {}".format(artifact_path))
        print("The {} subagent must write this file before eval can run.".format(stage_cfg["agent"]))
        sys.exit(1)

    with open(artifact_path) as f:
        artifact_text = f.read()

    context = state.load_context()
    eval_module = importlib.import_module(stage_cfg["eval_module"])
    result = eval_module.evaluate(artifact_text, context)
    print(result.report())

    context = state.record_stage_run(
        context,
        stage=args.stage,
        eval_score=result.score,
        eval_pass=result.passed,
        attempt=args.attempt,
        artifact_path=artifact_path,
    )

    if result.passed:
        context, extracted_fields = extract.apply_extraction(context, args.stage, artifact_text)
        if extracted_fields:
            print("\nExtracted into context['{}']: {}".format(
                args.stage, ", ".join(extracted_fields.keys())
            ))
        if args.stage == "strategy":
            try:
                scoring = option_scoring.score_strategy_artifact(artifact_text)
                context["strategy"]["option_scores"] = {
                    "totals": scoring["totals"],
                    "ranked": scoring["ranked"],
                    "top_option": scoring["top_option"],
                }
                print(option_scoring.report(scoring))
            except option_scoring.OptionScoringError as e:
                print("Note: option scoring not stored in context ({})".format(e))
        nxt = next_stage(args.stage)
        context["current_stage"] = nxt if nxt else "complete"
        print("\nGATE: PASSED. Pipeline advances to stage: {}".format(context["current_stage"]))
    else:
        if args.attempt >= stage_cfg["max_attempts"]:
            print("\nGATE: FAILED after {} attempts (max reached). Flagging for human review.".format(
                args.attempt
            ))
        else:
            print("\nGATE: FAILED (attempt {}/{}). Revise {} and re-run eval.".format(
                args.attempt, stage_cfg["max_attempts"], artifact_path
            ))

    state.save_context(context)
    sys.exit(0 if result.passed else 1)


def cmd_extract(args):
    stage_cfg = get_stage(args.stage)
    artifact_path = args.artifact or os.path.join(ARTIFACTS_DIR, stage_cfg["artifact_file"])
    if not os.path.exists(artifact_path):
        print("Artifact not found: {}".format(artifact_path))
        sys.exit(1)
    with open(artifact_path) as f:
        artifact_text = f.read()
    context = state.load_context()
    context, extracted_fields = extract.apply_extraction(context, args.stage, artifact_text)
    state.save_context(context)
    print("Extracted into context['{}']:".format(args.stage))
    print(json.dumps(extracted_fields, indent=2))


def cmd_status(args):
    context = state.load_context()
    print("Product: {}".format(context.get("product_name")))
    print("Current stage: {}".format(context.get("current_stage")))
    print("\nStage history:")
    for run in context.get("stage_history", []):
        mark = "PASS" if run["eval_pass"] else "FAIL"
        print("  [{}] {} (attempt {}, score {:.2f}) -> {}".format(
            mark, run["stage"], run["attempt"], run.get("eval_score", 0.0), run["artifact_path"]
        ))
    print("\nFull pipeline: {}".format(" -> ".join(STAGE_NAMES)))


def main():
    parser = argparse.ArgumentParser(description="AI PM OS pipeline runner")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create a new context.json")
    p_init.add_argument("--product-name", required=True)
    p_init.add_argument("--one-liner", default="")
    p_init.add_argument("--domain-context-file", default=None,
                         help="Path to an SME notes file whose content seeds context.json's domain_context")
    p_init.set_defaults(func=cmd_init)

    p_domain = sub.add_parser("set-domain-context", help="Update domain_context on an existing context.json")
    p_domain.add_argument("--file", required=True)
    p_domain.set_defaults(func=cmd_set_domain_context)

    p_eval = sub.add_parser("eval", help="Run the eval for a stage's artifact")
    p_eval.add_argument("stage", choices=STAGE_NAMES)
    p_eval.add_argument("--artifact", default=None)
    p_eval.add_argument("--attempt", type=int, default=1)
    p_eval.set_defaults(func=cmd_eval)

    p_status = sub.add_parser("status", help="Show pipeline status and history")
    p_status.set_defaults(func=cmd_status)

    p_extract = sub.add_parser(
        "extract", help="Re-run structured-field extraction for a stage without re-running its eval"
    )
    p_extract.add_argument("stage", choices=STAGE_NAMES)
    p_extract.add_argument("--artifact", default=None)
    p_extract.set_defaults(func=cmd_extract)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
