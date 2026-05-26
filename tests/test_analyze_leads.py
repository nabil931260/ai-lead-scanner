import tempfile
import unittest
from pathlib import Path

from scripts import analyze_leads


class AnalyzeLeadsTests(unittest.TestCase):
    def test_parse_markdown_table_finds_required_header(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "leads.md"
            path.write_text(
                "# Leads\n\n"
                "| Business | Niche | Location | Website | Source | Notes | Status | Online Presence Status | Website Quality | Offer Path |\n"
                "|---|---|---|---|---|---|---|---|---|---|\n"
                "| Example Painting Co | Painting services | Plano, TX | https://example-painting.test/contact | Manual | Quote form noted. | New | Has Website | Unknown | Website Analyzer |\n",
                encoding="utf-8",
            )
            rows = analyze_leads.parse_markdown_table(path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Business"], "Example Painting Co")

    def test_offline_analysis_scores_website_and_no_website_leads(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            input_path = temp / "Leads Input.example.md"
            output_path = temp / "Scored Leads.md"
            input_path.write_text(
                "| Business | Niche | Location | Website | Source | Notes | Status | Online Presence Status | Website Quality | Offer Path |\n"
                "|---|---|---|---|---|---|---|---|---|---|\n"
                "| Example Painting Co | Painting services | Plano, TX | https://example-painting.test/contact | Manual | Quote form asks for project details and follow-up. | New | Has Website | Unknown | Website Analyzer |\n"
                "| Example Mobile Detailer | Mobile detailing | Dallas, TX | N/A | Manual | No website found; phone/text booking. | New | No Website Found | Missing | Starter Site Offer |\n",
                encoding="utf-8",
            )
            result = analyze_leads.analyze(input_path=input_path, output_path=output_path, offline=True)
            content = output_path.read_text(encoding="utf-8")
        self.assertEqual(result, 0)
        self.assertIn("Workflow Cleanup Candidate", content)
        self.assertIn("Starter Site Candidate", content)
        self.assertIn("Evidence", content)
        self.assertIn("Pages checked", content)

    def test_candidate_page_urls_stay_on_same_domain_and_limit_pages(self):
        urls = analyze_leads.candidate_page_urls("https://example-painting.test/start", max_pages=4)
        self.assertEqual(urls[0], "https://example-painting.test/start")
        self.assertEqual(len(urls), 4)
        self.assertIn("https://example-painting.test/contact", urls)
