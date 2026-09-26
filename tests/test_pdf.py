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
        for value in ("200+ repositories", "49 Light and 30 PowerUnit releases", "11 Alexa engines"):
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
            "root-cause analysis",
            "monitoring and debugging",
            "time and resource planning",
            "Software Architecture Lab",
            "Scan to Email",
            "Immediate and On-Demand Image Overwriting",
            "MapInfo",
        ):
            self.assertIn(value, self.normalized_text)

    def test_pdf_shows_hands_on_firmware_work(self):
        for value in (
            "Wrote the complete device firmware from scratch in C and C++",
            "RTOS threading model, task priorities",
            "five devices on a shared I2C bus",
            "AHT20",
            "INA3221",
            "DS3231",
            "JTAG/SWD alongside the hardware engineer",
            "OTA firmware-update path end to end",
            "high-volume manufacturing",
            "CAN bus control of motors and actuators",
            "Write C++ against Airway device hardware",
        ):
            self.assertIn(value, self.normalized_text)

    def test_published_pdf_withholds_confidential_material(self):
        """The general resume is published on a public site; these must never reach it."""
        for term in (
            "lithotripsy", "kidney", "Class C to Class B", "QNX hypervisor",
            "parallel recognition capacity", "50 to 150", "FPGA", "Azure DevOps",
            "ad hoc", "glass-break", "whisper detection", "9 to 20+",
        ):
            self.assertNotIn(term, self.normalized_text, term)

    def test_pdf_avoids_non_ascii_dash_characters(self):
        for forbidden in ("–", "—", "‑"):
            self.assertNotIn(forbidden, self.text)


if __name__ == "__main__":
    unittest.main()
