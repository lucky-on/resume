from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
JOURNEY = ROOT / "journey"
HTML = JOURNEY / "index.html"
CSS = JOURNEY / "journey.css"
PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?1[\s.-]?)?\(?[2-9]\d{2}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)"
)
CITIES = ("tomsk", "suwon", "gdansk", "boston")


class ReferenceCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag in {"a", "link", "script", "img"}:
            value = values.get("href") or values.get("src")
            if value:
                self.references.append(value)
        if tag == "source" and values.get("srcset"):
            for candidate in values["srcset"].split(","):
                self.references.append(candidate.strip().split()[0])
        if tag == "img":
            self.images.append(values)


class JourneyPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = HTML.read_text(encoding="utf-8")
        cls.css = CSS.read_text(encoding="utf-8")
        cls.parser = ReferenceCollector()
        cls.parser.feed(cls.source)

    def test_page_files_exist(self):
        self.assertTrue(HTML.exists())
        self.assertTrue(CSS.exists())

    def test_local_references_resolve(self):
        local = [
            value
            for value in self.parser.references
            if not value.startswith(("#", "mailto:", "http://", "https://"))
        ]
        self.assertTrue(local)
        for value in local:
            self.assertTrue((JOURNEY / value).exists(), value)

    def test_shared_stylesheet_and_script_are_reused(self):
        self.assertIn('href="../styles.css"', self.source)
        self.assertIn('src="../script.js"', self.source)

    def test_no_phone_number_in_public_sources(self):
        self.assertIsNone(PHONE_PATTERN.search(self.source))
        self.assertIsNone(PHONE_PATTERN.search(self.css))

    def test_no_tracking_or_remote_assets(self):
        lowered = self.source.lower()
        for forbidden in ("google-analytics", "googletagmanager", "http://", "https://fonts."):
            self.assertNotIn(forbidden, lowered)
        self.assertNotIn("@import", self.css)
        self.assertNotIn("url(", self.css)

    def test_every_chapter_has_a_local_responsive_illustration(self):
        self.assertEqual(len(self.parser.images), len(CITIES))
        for city in CITIES:
            for width in (640, 1024, 1536):
                self.assertIn(f"../assets/journey/{city}-{width}.webp {width}w", self.source)
            self.assertIn(f'src="../assets/journey/{city}-1024.jpg"', self.source)
            self.assertIn(f'id="{city}"', self.source)
        for image in self.parser.images:
            self.assertTrue(image.get("alt"), image.get("src"))
            self.assertEqual(image.get("width"), "1536")
            self.assertEqual(image.get("height"), "1024")
            self.assertIn(image.get("loading"), {"eager", "lazy"})

    def test_illustrations_stay_reasonably_small(self):
        for path in (ROOT / "assets" / "journey").iterdir():
            self.assertLess(path.stat().st_size, 450_000, path.name)

    def test_timeline_and_skills_grid_are_present(self):
        for value in (
            'class="timeline"',
            'class="timeline-now"',
            'class="timeline-start"',
            'class="chapter-marker"',
            'class="skills-grid"',
            'data-level="started"',
            'data-level="deepened"',
        ):
            self.assertIn(value, self.source)
        self.assertEqual(self.source.count('class="chapter-marker"'), len(CITIES))
        self.assertIn(".timeline::before", self.css)

    def test_timeline_runs_newest_first(self):
        positions = [self.source.index(f'id="{city}"') for city in ("boston", "gdansk", "suwon", "tomsk")]
        self.assertEqual(positions, sorted(positions))
        rows = re.findall(r'<th scope="row">(\w+)', self.source)
        self.assertEqual(rows, ["Boston", "Gdańsk", "Suwon", "Tomsk"])

    def test_illustrations_are_feathered_into_the_page(self):
        for prefix in ("-webkit-mask-image", "mask-image"):
            self.assertIn(f"{prefix}:", self.css)
        self.assertIn("-webkit-mask-composite: source-in", self.css)
        self.assertIn("mask-composite: intersect", self.css)
        self.assertNotIn("border: ", self.css.split(".chapter-figure img")[1].split("}")[0])

    def test_resume_links_back_and_forth(self):
        self.assertIn('href="../"', self.source)
        self.assertIn('href="../assets/Sergey_Didenko_Resume.pdf"', self.source)
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="journey/"', home)


if __name__ == "__main__":
    unittest.main()
