"""
Loads, saves, and updates the shared ProductContext JSON that flows through
every stage of the pipeline. This is the single source of truth the
orchestrator and every stage agent reads from and writes to.
"""

import json
import os
from datetime import datetime, timezone

CONTEXT_PATH = os.path.join(os.path.dirname(__file__), "..", "artifacts", "context.json")


def _now():
    return datetime.now(timezone.utc).isoformat()


def load_context(path=CONTEXT_PATH):
    if not os.path.exists(path):
        raise FileNotFoundError(
            "No context.json found at {}. Run `python -m pipeline.runner --init "
            "--product-name '<name>'` to create one.".format(path)
        )
    with open(path, "r") as f:
        return json.load(f)


def save_context(context, path=CONTEXT_PATH):
    context["updated_at"] = _now()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(context, f, indent=2)


def init_context(product_name, one_liner="", path=CONTEXT_PATH):
    context = {
        "product_name": product_name,
        "one_liner": one_liner,
        "created_at": _now(),
        "updated_at": _now(),
        "current_stage": "vision",
        "stage_history": [],
    }
    save_context(context, path)
    return context


def record_stage_run(context, stage, eval_score, eval_pass, attempt, artifact_path):
    context["stage_history"].append({
        "stage": stage,
        "timestamp": _now(),
        "eval_score": eval_score,
        "eval_pass": eval_pass,
        "attempt": attempt,
        "artifact_path": artifact_path,
    })
    return context
