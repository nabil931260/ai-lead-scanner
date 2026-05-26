import tempfile
import unittest
from pathlib import Path

from scripts import generate_mini_audits


class GenerateMiniAuditsTests(unittest.TestCase):
    def test_generates_audits_and_drafts_to_explicit_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            scored = temp / "Scored Leads.md"
            audits = temp / "Mini Audits.md"
            drafts = temp / "Draft Messages.md"
            scored.write_text(
                "| Business | Niche | Website | Visible signals | Likely pain | Offer Type | Offer angle | Score /100 | Confidence | Recommended next action | Status |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| Example Painting Co | Painting services | https://example-painting.test/contact | Quote/estimate language | Lead intake may be manual. | Website + Workflow Improvement Audit | Website audit | 72 | Medium | Review | Workflow Cleanup Candidate |\n",
                encoding="utf-8",
            )
            result = generate_mini_audits.generate(
                input_path=scored,
                audits_output=audits,
                drafts_output=drafts,
                threshold=60,
            )
            audit_content = audits.read_text(encoding="utf-8")
            draft_content = drafts.read_text(encoding="utf-8")
        self.assertEqual(result, 0)
        self.assertIn("Example Painting Co", audit_content)
        self.assertIn("Your Name", draft_content)
