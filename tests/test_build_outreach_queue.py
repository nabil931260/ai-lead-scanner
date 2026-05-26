import tempfile
import unittest
from pathlib import Path

from scripts import build_outreach_queue


class BuildOutreachQueueTests(unittest.TestCase):
    def test_builds_queue_from_explicit_scored_and_draft_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            scored = temp / "Scored Leads.md"
            drafts = temp / "Draft Messages.md"
            queue = temp / "Outreach Queue.md"
            sites = temp / "generated_sites"
            scored.write_text(
                "| Business | Niche | Website | Visible signals | Likely pain | Offer Type | Offer angle | Score /100 | Confidence | Recommended next action | Status |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| Example Painting Co | Painting services | https://example-painting.test/contact | Quote/estimate language | Lead intake may be manual. | Website + Workflow Improvement Audit | Website audit | 72 | Medium | Review | Workflow Cleanup Candidate |\n",
                encoding="utf-8",
            )
            drafts.write_text(
                "| Business | Offer Type | Draft Message Type | Contact method | Subject | Draft message | Mini-audit link/path | Review status | Gmail draft created? | Sent? | Notes |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| Example Painting Co | Website + Workflow Improvement Audit | Existing website workflow cleanup | Manual public contact path only | Quick workflow question | Hi Example team | Mini Audits.md#example-painting-co | Needs review | No | No | Review first |\n",
                encoding="utf-8",
            )
            rows = build_outreach_queue.build_queue(
                scored_path=scored,
                drafts_path=drafts,
                queue_path=queue,
                generated_sites_path=sites,
            )
            build_outreach_queue.write_queue(rows, queue)
            content = queue.read_text(encoding="utf-8")
        self.assertEqual(len(rows), 1)
        self.assertIn("Example Painting Co", content)
        self.assertIn("Missing contact email", content)
