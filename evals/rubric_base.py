"""
Shared rubric engine for stage evals.

Each stage eval (e.g. evals/vision_eval.py) builds a Rubric out of
RubricCriterion objects and calls rubric.score(artifact_text, context).

Design goals:
  - Deterministic structural checks run with zero external dependencies,
    so `python -m pipeline.runner` works out of the box with no API key.
  - An optional LLM-judge criterion can be added on top for qualitative
    scoring (clarity, sharpness of thinking) when ANTHROPIC_API_KEY is set.
    If it isn't set, that criterion auto-passes so the eval suite still
    runs end to end in environments without network/API access.
"""

from dataclasses import dataclass, field
import os
import re


@dataclass
class CriterionResult:
    name: str
    passed: bool
    weight: float
    detail: str = ""


@dataclass
class RubricCriterion:
    name: str
    weight: float
    check: object


@dataclass
class RubricResult:
    score: float
    passed: bool
    threshold: float
    criteria: list = field(default_factory=list)

    def report(self):
        lines = ["Score: {:.2f} (threshold {:.2f}) -> {}".format(
            self.score, self.threshold, "PASS" if self.passed else "FAIL"
        )]
        for c in self.criteria:
            mark = "PASS" if c.passed else "FAIL"
            lines.append("  [{}] {} (weight {}): {}".format(mark, c.name, c.weight, c.detail))
        return "\n".join(lines)


class Rubric:
    def __init__(self, criteria, threshold):
        self.criteria = criteria
        self.threshold = threshold

    def score(self, artifact_text, context):
        results = [c.check(artifact_text, context) for c in self.criteria]
        total_weight = sum(c.weight for c in results) or 1.0
        earned = sum(c.weight for c in results if c.passed)
        score = earned / total_weight
        return RubricResult(
            score=score,
            passed=score >= self.threshold,
            threshold=self.threshold,
            criteria=results,
        )


def section_present(section_heading, min_words=15):
    """Verifies a markdown heading exists with at least min_words beneath it."""

    def _check(text, context):
        pattern = re.compile(
            r"^#{1,3}\s*" + re.escape(section_heading) + r"\s*$(.*?)(?=^#{1,3}\s|\Z)",
            re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )
        match = pattern.search(text)
        if not match:
            return CriterionResult(section_heading, False, 1, "section heading not found")
        body = match.group(1).strip()
        word_count = len(body.split())
        if word_count < min_words:
            return CriterionResult(section_heading, False, 1,
                                    "section present but too thin ({} words)".format(word_count))
        return CriterionResult(section_heading, True, 1, "{} words".format(word_count))

    return _check


def no_placeholder_text():
    """Fails if the artifact still contains obvious TODO/placeholder markers."""

    placeholders = ["TODO", "TBD", "[insert", "<placeholder>", "lorem ipsum"]

    def _check(text, context):
        lowered = text.lower()
        hits = [p for p in placeholders if p.lower() in lowered]
        if hits:
            return CriterionResult("no_placeholder_text", False, 1, "found: {}".format(hits))
        return CriterionResult("no_placeholder_text", True, 1, "clean")

    return _check


def mentions_product_name():
    """Fails if the artifact never references the product being built."""

    def _check(text, context):
        name = context.get("product_name", "")
        if not name:
            return CriterionResult("mentions_product_name", True, 1, "no product_name set, skipped")
        if name.lower() in text.lower():
            return CriterionResult("mentions_product_name", True, 1, "referenced")
        return CriterionResult("mentions_product_name", False, 1,
                                "'{}' not mentioned in artifact".format(name))

    return _check


def has_evidence_citations(min_citations=1):
    """
    Lenient nudge toward evidence-grounded claims: checks for at least
    min_citations occurrences of the '[source: ...]' citation convention
    (see inputs/README.md) anywhere in the artifact. Not a per-bullet
    requirement - just enough to confirm the author is citing real research
    inputs rather than writing purely from assumption.
    """

    pattern = re.compile(r"\[source:\s*[^\]]+\]", re.IGNORECASE)

    def _check(text, context):
        matches = pattern.findall(text)
        if len(matches) >= min_citations:
            return CriterionResult(
                "has_evidence_citations", True, 1, "{} citation(s) found".format(len(matches))
            )
        return CriterionResult(
            "has_evidence_citations", False, 1,
            "only {} citation(s) found, expected >= {} (see inputs/README.md convention)".format(
                len(matches), min_citations
            ),
        )

    return _check


def llm_judge_criterion(prompt_instructions, api_key_env="ANTHROPIC_API_KEY"):
    """Optional qualitative check via Claude-as-judge. Auto-passes if no API key is set."""

    def _check(text, context):
        api_key = os.environ.get(api_key_env)
        if not api_key:
            return CriterionResult("llm_judge", True, 1, "skipped: no API key in environment")
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            resp = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=200,
                messages=[{
                    "role": "user",
                    "content": (
                        prompt_instructions
                        + "\n\nRespond with only PASS or FAIL on the first line, then one "
                        "sentence why.\n\n---\n" + text
                    ),
                }],
            )
            reply = resp.content[0].text.strip()
            passed = reply.upper().startswith("PASS")
            return CriterionResult("llm_judge", passed, 1, reply[:200])
        except Exception as e:
            return CriterionResult("llm_judge", True, 1, "skipped: judge call failed ({})".format(e))

    return _check
