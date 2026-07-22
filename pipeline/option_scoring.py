"""
Parses the "Option Evaluation" scoring table out of a strategy artifact and
computes weighted totals per strategic option - the mechanism behind
"grade the strategy options" rather than just prose-recommending one.

Expected table format (see .claude/skills/strategy/SKILL.md for the full
spec and a worked example):

    | Criterion (weight) | Option A | Option B |
    |---|---|---|
    | Impact on North Star (x3) | 4 | 5 |
    | Feasibility (x2) | 5 | 2 |
    | Risk (x2, lower is better) | 4 | 2 |

- Each criterion row's weight is parsed from "(x<number>)" in the first
  column; defaults to 1 if not present.
- "(lower is better)" in a criterion name inverts that row's scores
  (6 - score) before weighting, so a lower raw score still contributes
  positively to a "good" total - use this for things like Risk or Cost.
- A trailing "Weighted Total" row, if present, is not treated as a
  criterion - it's informational only; this module recomputes totals
  itself rather than trusting a hand-typed one.

Run standalone:
    python -m pipeline.option_scoring artifacts/strategy.md
"""

import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.extract import get_section_body

CRITERION_WEIGHT_RE = re.compile(r"\(x\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
LOWER_IS_BETTER_RE = re.compile(r"lower is better", re.IGNORECASE)


class OptionScoringError(ValueError):
    pass


def _split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def _is_separator_row(cells):
    return all(re.fullmatch(r":?-+:?", cell.strip()) for cell in cells if cell.strip())


def parse_option_table(section_text):
    """
    Returns {"options": [...], "criteria": [(name, weight, lower_is_better), ...],
    "scores": {criterion_name: {option_name: value}}}
    """
    lines = [ln for ln in section_text.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 3:
        raise OptionScoringError("No markdown table with at least a header, separator, and one data row found")

    header_cells = _split_row(lines[0])
    if not _is_separator_row(_split_row(lines[1])):
        raise OptionScoringError("Second table row is not a valid markdown header separator")

    options = header_cells[1:]
    if len(options) < 2:
        raise OptionScoringError("Table must compare at least 2 options (found {})".format(len(options)))

    criteria = []
    scores = {}
    for row_line in lines[2:]:
        cells = _split_row(row_line)
        if not cells or not cells[0].strip():
            continue
        criterion_raw = cells[0].strip()
        if criterion_raw.lower().replace("*", "").strip() == "weighted total":
            continue  # informational row, recomputed below - not trusted verbatim

        weight_match = CRITERION_WEIGHT_RE.search(criterion_raw)
        weight = float(weight_match.group(1)) if weight_match else 1.0
        lower_is_better = bool(LOWER_IS_BETTER_RE.search(criterion_raw))
        criterion_name = re.sub(r"\(.*?\)", "", criterion_raw).strip()

        row_scores = {}
        for i, option in enumerate(options):
            cell = cells[i + 1] if i + 1 < len(cells) else ""
            try:
                row_scores[option] = float(cell.strip())
            except ValueError:
                raise OptionScoringError(
                    "Non-numeric score '{}' for criterion '{}', option '{}'".format(cell, criterion_name, option)
                )

        criteria.append((criterion_name, weight, lower_is_better))
        scores[criterion_name] = row_scores

    if not criteria:
        raise OptionScoringError("No scoring criteria rows found in the table")

    return {"options": options, "criteria": criteria, "scores": scores}


def compute_weighted_totals(parsed):
    totals = {option: 0.0 for option in parsed["options"]}
    for criterion_name, weight, lower_is_better in parsed["criteria"]:
        row = parsed["scores"][criterion_name]
        for option in parsed["options"]:
            raw = row[option]
            value = (6 - raw) if lower_is_better else raw
            totals[option] += value * weight
    return totals


def score_strategy_artifact(artifact_text):
    """
    Full pipeline: find the 'Option Evaluation' section, parse its table,
    compute weighted totals, and rank options. Raises OptionScoringError on
    any structural problem (caller decides whether that's a hard eval fail
    or just an incomplete-info message).
    """
    body = get_section_body(artifact_text, "Option Evaluation")
    if body is None:
        raise OptionScoringError("No 'Option Evaluation' section found")
    parsed = parse_option_table(body)
    totals = compute_weighted_totals(parsed)
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    return {
        "options": parsed["options"],
        "criteria": [c[0] for c in parsed["criteria"]],
        "totals": totals,
        "ranked": ranked,
        "top_option": ranked[0][0],
    }


def report(result):
    lines = ["Option scoring (higher weighted total = stronger option):"]
    for option, total in result["ranked"]:
        marker = " <- top" if option == result["top_option"] else ""
        lines.append("  {:<20} {:.1f}{}".format(option, total, marker))
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m pipeline.option_scoring <path_to_strategy.md>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        text = f.read()
    try:
        result = score_strategy_artifact(text)
        print(report(result))
    except OptionScoringError as e:
        print("Could not score options: {}".format(e))
        sys.exit(1)
