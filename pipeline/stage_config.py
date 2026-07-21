"""
Ordered definition of the AI PM OS pipeline.

Each stage maps to:
  - a Claude Code subagent (in .claude/agents/) that generates the artifact
  - a skill (in .claude/skills/) the subagent is instructed to load for methodology
  - an eval module (in evals/) that scores the generated artifact
  - a pass_threshold: eval_score >= threshold required to gate forward
  - a max_attempts: how many times the orchestrator will ask the agent to revise
    before stopping and flagging for human review
"""

STAGES = [
    {"name": "vision", "agent": "vision-agent", "skill": "vision",
     "eval_module": "evals.vision_eval", "artifact_file": "vision.md",
     "pass_threshold": 0.75, "max_attempts": 3},
    {"name": "discovery", "agent": "discovery-agent", "skill": "discovery",
     "eval_module": "evals.discovery_eval", "artifact_file": "discovery.md",
     "pass_threshold": 0.75, "max_attempts": 3},
    {"name": "strategy", "agent": "strategy-agent", "skill": "strategy",
     "eval_module": "evals.strategy_eval", "artifact_file": "strategy.md",
     "pass_threshold": 0.75, "max_attempts": 3},
    {"name": "roadmap", "agent": "roadmap-agent", "skill": "roadmap",
     "eval_module": "evals.roadmap_eval", "artifact_file": "roadmap.md",
     "pass_threshold": 0.75, "max_attempts": 3},
    {"name": "mvp", "agent": "mvp-agent", "skill": "mvp",
     "eval_module": "evals.mvp_eval", "artifact_file": "mvp.md",
     "pass_threshold": 0.75, "max_attempts": 3},
    {"name": "prd", "agent": "prd-agent", "skill": "prd",
     "eval_module": "evals.prd_eval", "artifact_file": "prd.md",
     "pass_threshold": 0.8, "max_attempts": 3},
    {"name": "validation", "agent": "validation-agent", "skill": "validation",
     "eval_module": "evals.validation_eval", "artifact_file": "validation.md",
     "pass_threshold": 0.75, "max_attempts": 3},
    {"name": "phased_rollout", "agent": "phased-rollout-agent", "skill": "phased_rollout",
     "eval_module": "evals.phased_rollout_eval", "artifact_file": "phased_rollout.md",
     "pass_threshold": 0.75, "max_attempts": 3},
    {"name": "outcomes", "agent": "outcomes-agent", "skill": "outcomes",
     "eval_module": "evals.outcomes_eval", "artifact_file": "outcomes.md",
     "pass_threshold": 0.7, "max_attempts": 3},
]

STAGE_NAMES = [s["name"] for s in STAGES]


def get_stage(name):
    for s in STAGES:
        if s["name"] == name:
            return s
    raise ValueError("Unknown stage: {}".format(name))


def next_stage(name):
    idx = STAGE_NAMES.index(name)
    if idx + 1 < len(STAGE_NAMES):
        return STAGE_NAMES[idx + 1]
    return None
