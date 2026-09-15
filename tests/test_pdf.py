from pathlib import Path
import os
import re
import sys
import tempfile
import unittest
from unittest.mock import patch
import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "assets" / "Sergey_Didenko_Resume.pdf"
PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?1[\s.-]?)?\(?[2-9]\d{2}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)"
)
sys.path.insert(0, str(ROOT))
from tools.build_resume_pdf import build_pdf


class ResumePdfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reader = PdfReader(PDF)
        cls.text = "\n".join(page.extract_text() or "" for page in cls.reader.pages)
        cls.normalized_text = re.sub(r"\s+", " ", cls.text)

    def test_pdf_has_exactly_two_pages(self):
        self.assertEqual(2, len(self.reader.pages))

    def test_both_pages_use_available_space(self):
        with pdfplumber.open(PDF) as document:
            for page_number, page in enumerate(document.pages, start=1):
                words = page.extract_words()
                self.assertTrue(words, f"page {page_number} has no text")
                self.assertGreaterEqual(
                    max(word["bottom"] for word in words),
                    600,
                    f"page {page_number} leaves excessive unused space",
                )

    def test_pdf_contains_contact_details_and_phone(self):
        self.assertIsNotNone(PHONE_PATTERN.search(self.text))
        self.assertIn("didenkos@gmail.com", self.text)
        self.assertIn("linkedin.com/in/didenkos", self.text)

    def test_builder_requires_private_phone_environment(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "resume.pdf"
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaisesRegex(RuntimeError, "SERGEY_RESUME_PHONE"):
                    build_pdf(output_path)

    def test_pdf_contains_approved_identity_and_history(self):
        for value in ("Engineering Leader", "Verathon", "GloMove", "Olympus", "Appian", "Amazon", "Samsung", "Incom", "q/k"):
            self.assertIn(value, self.normalized_text)

    def test_pdf_contains_recent_results(self):
        for value in ("200+ repositories", "49 Light-device releases", "30 PowerUnit releases", "11 Alexa engines"):
            self.assertIn(value, self.normalized_text)

    def test_pdf_contains_approved_positioning_and_credentials(self):
        for value in (
            "Sergey Didenko, Ph.D.",
            "Leading Engineering Teams",
            "GloMove | AI-Assisted Development & Verification | May-Jul 2026",
            "Amazon | Alexa | ASR Engine | Jul 2017-Sep 2021",
            "Amazon | Alexa | TTS Engine and Kindle | Aug 2015-Jul 2017",
            "Doctor of Philosophy (Ph.D.) in Computer Science",
            "SOLID design principles",
            "Clean Code",
            "Clean Architecture",
        ):
            self.assertIn(value, self.normalized_text)

    def test_pdf_restores_technical_and_leadership_evidence(self):
        for value in (
            "protocol creation",
            "knowledge-transfer",
            "documentation, templates, release patterns, and migration paths",
            "root-cause analysis",
            "monitoring and debugging",
            "time and resource planning",
            "Software Architecture Lab",
            "Scan to Email",
            "TIFF, BMP, JPEG, GIF, PNG, and PDF",
            "Immediate and On-Demand Image Overwriting",
            "Kindle Bird's Eye View",
            "MapInfo",
        ):
            self.assertIn(value, self.normalized_text)

    def test_pdf_avoids_non_ascii_dash_characters(self):
        for forbidden in ("–", "—", "‑"):
            self.assertNotIn(forbidden, self.text)


if __name__ == "__main__":
    unittest.main()
