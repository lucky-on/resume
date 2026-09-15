from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "assets" / "Sergey_Didenko_Resume.pdf"
PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?1[\s.-]?)?\(?[2-9]\d{2}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)"
)


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag in {"a", "link", "script"}:
            value = values.get("href") or values.get("src")
            if value:
                self.links.append(value)


class PackageTests(unittest.TestCase):
    def test_required_package_files_exist(self):
        for path in (
            "index.html",
            "styles.css",
            "script.js",
            ".nojekyll",
            "README.md",
            "assets/Sergey_Didenko_Resume.pdf",
        ):
            self.assertTrue((ROOT / path).exists(), path)

    def test_local_links_resolve(self):
        parser = LinkCollector()
        parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
        local = [
            value
            for value in parser.links
            if not value.startswith(("#", "mailto:", "http://", "https://"))
        ]
        for value in local:
            self.assertTrue((ROOT / value).exists(), value)

    def test_readme_contains_github_pages_steps(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for value in ("GitHub Pages", "Deploy from a branch", "Download PDF"):
            self.assertIn(value, text)

    def test_local_phone_environment_files_are_ignored(self):
        ignore_lines = {
            line.strip()
            for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        }
        self.assertIn(".env", ignore_lines)
        self.assertIn(".env.*", ignore_lines)

    def test_pdf_phone_is_absent_from_public_text_sources(self):
        pdf_text = "\n".join(
            page.extract_text() or "" for page in PdfReader(PDF).pages
        )
        match = PHONE_PATTERN.search(pdf_text)
        self.assertIsNotNone(match)
        phone_digits = re.sub(r"\D", "", match.group(0))[-10:]

        public_suffixes = {".css", ".html", ".js", ".md", ".py"}
        excluded_parts = {".git", ".superpowers", "__pycache__", "tmp"}
        for path in ROOT.rglob("*"):
            if not path.is_file() or excluded_parts.intersection(path.parts):
                continue
            if path.suffix not in public_suffixes and path.name != ".gitignore":
                continue
            source_digits = re.sub(r"\D", "", path.read_text(encoding="utf-8"))
            self.assertFalse(
                phone_digits in source_digits,
                str(path.relative_to(ROOT)),
            )


if __name__ == "__main__":
    unittest.main()
