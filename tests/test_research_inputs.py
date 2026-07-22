import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from evals.rubric_base import has_evidence_citations
from pipeline import state


class TestEvidenceCitations(unittest.TestCase):
    def test_passes_with_citation(self):
        text = "## Key Insights\n- Something true [source: inputs/interviews/priya.md]\n"
        check = has_evidence_citations(min_citations=1)
        result = check(text, {})
        self.assertTrue(result.passed)

    def test_fails_without_citation(self):
        text = "## Key Insights\n- Something true, but where's the evidence\n"
        check = has_evidence_citations(min_citations=1)
        result = check(text, {})
        self.assertFalse(result.passed)

    def test_counts_multiple_citations(self):
        text = (
            "- A [source: inputs/interviews/a.md]\n"
            "- B [source: inputs/customer_feedback/b.md]\n"
        )
        check = has_evidence_citations(min_citations=2)
        result = check(text, {})
        self.assertTrue(result.passed)


class TestDomainContext(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), "_test_domain_context.json")

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_init_context_stores_domain_context(self):
        context = state.init_context("X", "one-liner", domain_context="S&OP means...", path=self.path)
        self.assertEqual(context["domain_context"], "S&OP means...")

    def test_set_domain_context_updates_existing(self):
        context = state.init_context("X", path=self.path)
        context = state.set_domain_context(context, "new domain info")
        state.save_context(context, self.path)
        loaded = state.load_context(self.path)
        self.assertEqual(loaded["domain_context"], "new domain info")


if __name__ == "__main__":
    unittest.main()


class TestShareLog(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), "_test_share_log.json")

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_init_context_has_empty_share_log(self):
        context = state.init_context("X", path=self.path)
        self.assertEqual(context["share_log"], [])

    def test_record_share_appends_entry(self):
        context = state.init_context("X", path=self.path)
        context = state.record_share(context, "artifacts/prd.md", "#product-updates", "for review")
        state.save_context(context, self.path)
        loaded = state.load_context(self.path)
        self.assertEqual(len(loaded["share_log"]), 1)
        self.assertEqual(loaded["share_log"][0]["channel"], "#product-updates")
        self.assertEqual(loaded["share_log"][0]["note"], "for review")

    def test_record_share_multiple_entries_accumulate(self):
        context = state.init_context("X", path=self.path)
        context = state.record_share(context, "artifacts/prd.md", "#eng")
        context = state.record_share(context, "artifacts/outcomes.md", "#leadership")
        self.assertEqual(len(context["share_log"]), 2)
