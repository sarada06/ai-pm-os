"""
Structured-field extraction: after a stage's artifact passes its eval, pull
the content out of its markdown sections and write it into the matching
per-stage object in context.json (schemas/product_context.schema.json),
so downstream stages can reference structured data (e.g.
context["vision"]["north_star_metric"]) instead of re-reading prose.

This is deterministic markdown parsing - no LLM call, no API key needed.
It runs automatically at the end of `python -m pipeline.runner eval <stage>`
when the gate passes. You can also run it standalone:

    python -m pipeline.extract vision examples/sample_vision.md
"""

import re
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# Maps: stage -> { "Exact Heading Text": (context_field_name, parser_kind) }
# parser_kind is one of: "string", "list", "objects"
FIELD_MAPS = {
    "vision": {
        "Problem Statement": ("problem_statement", "string"),
        "Target Users": ("target_users", "list"),
        "Vision Statement": ("vision_statement", "string"),
        "North Star Metric": ("north_star_metric", "string"),
        "Non-Goals": ("non_goals", "list"),
    },
    "discovery": {
        "Research Questions": ("research_questions", "list"),
        "Key Insights": ("insights", "list"),
        "Personas": ("personas", "objects"),
        "Opportunity Areas": ("opportunity_areas", "list"),
    },
    "strategy": {
        "Strategic Options": ("options", "objects"),
        "Strategic Bets": ("strategic_bets", "list"),
        "Success Metrics": ("success_metrics", "list"),
        "Competitive Positioning": ("competitive_positioning", "string"),
        "Constraints": ("constraints", "list"),
    },
    "mvp": {
        "Scope In": ("scope_in", "list"),
        "Scope Out": ("scope_out", "list"),
        "Success Criteria": ("success_criteria", "list"),
    },
    "prd": {
        "Requirements": ("requirements", "objects"),
        "User Stories": ("user_stories", "list"),
        "Edge Cases": ("edge_cases", "list"),
        "Open Questions": ("open_questions", "list"),
    },
    "validation": {
        "Hypotheses": ("hypotheses", "list"),
        "Test Plan": ("test_plan", "string"),
        "Results": ("results", "list"),
    },
    "phased_rollout": {
        "Rollout Phases": ("phases", "objects"),
        "Rollback Plan": ("rollback_plan", "string"),
        "Guardrail Metrics": ("guardrail_metrics", "list"),
    },
    "outcomes": {
        "Results vs North Star": ("results_vs_north_star", "string"),
        "Learnings": ("learnings", "list"),
        "Next Bets": ("next_bets", "list"),
    },
    # "roadmap" is handled separately below - its headings (Now/Next/Later)
    # map to array *items* (horizons), not to fixed field names.
}

BULLET_PREFIX = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+")
BULLET_KV = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+\*{0,2}([^:*]+?)\*{0,2}\s*:\s*(.+)$")


def get_section_body(text, heading):
    """Returns the raw text under a markdown heading, up to the next heading, or None."""
    pattern = re.compile(
        r"^#{1,3}\s*" + re.escape(heading) + r"\s*$(.*?)(?=^#{1,3}\s|\Z)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        return None
    return match.group(1).strip()


def parse_string(body):
    # Collapse multiple blank lines/paragraphs into a single clean string.
    return " ".join(line.strip() for line in body.splitlines() if line.strip())


def parse_list(body):
    items = []
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        cleaned = BULLET_PREFIX.sub("", line).strip()
        if cleaned:
            items.append(cleaned)
    return items


def parse_objects(body):
    """
    Parses bullet lines into small dicts. Recognizes '- **Key**: value' or
    '- Key: value' as {"name": Key, "description": value}; any bullet line
    that doesn't match that shape is kept as {"text": line}.
    """
    objects = []
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        kv_match = BULLET_KV.match(line)
        if kv_match:
            name, desc = kv_match.group(1).strip(), kv_match.group(2).strip()
            objects.append({"name": name, "description": desc})
        else:
            cleaned = BULLET_PREFIX.sub("", line).strip()
            if cleaned:
                objects.append({"text": cleaned})
    return objects


PARSERS = {
    "string": parse_string,
    "list": parse_list,
    "objects": parse_objects,
}


def extract_roadmap(text):
    """Roadmap is special-cased: Now/Next/Later headings become horizon objects."""
    horizons = []
    for heading in ["Now", "Next", "Later"]:
        body = get_section_body(text, heading)
        if body is None:
            continue
        horizons.append({
            "name": heading,
            "themes": parse_list(body),
            "timeframe": "",
        })
    return {"horizons": horizons}


def extract_stage(stage, artifact_text):
    """
    Returns a dict suitable for merging into context[stage]. Missing
    sections are simply omitted (not set to null/empty), so a partial
    re-run never clobbers previously-extracted fields for sections that
    happen to be absent this time.
    """
    if stage == "roadmap":
        return extract_roadmap(artifact_text)

    field_map = FIELD_MAPS.get(stage)
    if field_map is None:
        raise ValueError("No field map defined for stage: {}".format(stage))

    extracted = {}
    for heading, (field_name, kind) in field_map.items():
        body = get_section_body(artifact_text, heading)
        if body is None or not body.strip():
            continue
        parser = PARSERS[kind]
        extracted[field_name] = parser(body)
    return extracted


def apply_extraction(context, stage, artifact_text):
    """Merges extracted fields into context[stage], creating the key if needed."""
    extracted = extract_stage(stage, artifact_text)
    existing = context.get(stage, {})
    if not isinstance(existing, dict):
        existing = {}
    existing.update(extracted)
    context[stage] = existing
    return context, extracted


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m pipeline.extract <stage> <path_to_artifact.md>")
        sys.exit(1)
    stage_arg, path_arg = sys.argv[1], sys.argv[2]
    with open(path_arg) as f:
        artifact_text = f.read()
    result = extract_stage(stage_arg, artifact_text)
    print(json.dumps(result, indent=2))
