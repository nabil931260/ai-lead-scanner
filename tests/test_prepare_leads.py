import tempfile
import unittest
from pathlib import Path

from scripts import prepare_leads


class PrepareLeadsTests(unittest.TestCase):
    def test_converts_simple_rows_to_leads_input_table(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "raw.txt"
            output = temp / "Leads Input.md"
            source.write_text(
                "Example Painting Co | Painting services | Plano, TX | https://example-painting.test/contact | Quote form noted\n"
                "Example Mobile Detailer, Mobile detailing, Dallas TX, N/A, No website found\n",
                encoding="utf-8",
            )
            count = prepare_leads.prepare(source, output)
            content = output.read_text(encoding="utf-8")
        self.assertEqual(count, 2)
        self.assertIn("| Example Painting Co | Painting services | Plano, TX | https://example-painting.test/contact |", content)
        self.assertIn("| Example Mobile Detailer | Mobile detailing | Dallas TX | N/A |", content)
