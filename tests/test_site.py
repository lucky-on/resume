from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"
PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?1[\s.-]?)?\(?[2-9]\d{2}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)"
)


class ResumeSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = HTML.read_text(encoding="utf-8")
        cls.text = re.sub(r"<[^>]+>", " ", cls.source)
        cls.text = re.sub(r"\s+", " ", cls.text)

    def test_required_sections_and_identity_are_present(self):
        for value in (
            'id="impact"',
            'id="experience"',
            'id="expertise"',
            "Engineering Leader &amp; Principal Software Architect",
            "Senior Software Engineer",
            "Verathon",
            "Olympus",
            "GloMove",
            "Appian",
            "Amazon",
            "Samsung",
            "Incom",
        ):
            self.assertIn(value, self.source)

    def test_signature_metrics_are_present(self):
        for value in (
            "20+ years",
            "11 Alexa engines",
            "4–6 months",
            "3–4 weeks",
            "Multiple medical-device programs",
        ):
            self.assertIn(value, self.text)

    def test_recent_timeline_is_correct(self):
        self.assertIn("Jul 2026–Present", self.text)
        self.assertIn("May–Jul 2026", self.text)
        self.assertIn("Jul 2023–May 2026", self.text)

    def test_approved_positioning_and_role_names_are_present(self):
        for value in (
            "Sergey Didenko, Ph.D.",
            "Leading Engineering Teams",
            "From embedded systems to Alexa-scale platforms to regulated medical devices",
            "AI-Assisted Development &amp; Verification",
            "Amazon · Alexa · ASR Engine",
            "Amazon · Alexa · TTS Engine and Kindle",
            "Doctor of Philosophy (Ph.D.) in Computer Science",
        ):
            self.assertIn(value, self.source)

    def test_impact_claims_stay_owned_and_specific(self):
        for value in (
            "Designed and implemented the C++ data-processing framework",
            "Idea to production for a new Alexa engine",
            "Modernizing how regulated software gets built",
        ):
            self.assertIn(value, self.text)

    def test_engineering_practices_are_explicit(self):
        for value in (
            "software-development best practices",
            "SOLID design principles",
            "Clean Code",
            "Clean Architecture",
        ):
            self.assertIn(value, self.text)

    def test_appian_q_k_and_database_experience_is_present(self):
        self.assertRegex(self.text, r"Appian.+q/k.+database")

    def test_public_source_does_not_contain_phone_number(self):
        self.assertIsNone(PHONE_PATTERN.search(self.source))

    def test_resume_download_is_relative(self):
        self.assertIn('href="assets/Sergey_Didenko_Resume.pdf"', self.source)

    def test_no_tracking_or_remote_assets(self):
        lowered = self.source.lower()
        for forbidden in (
            "google-analytics",
            "googletagmanager",
            "http://",
            "https://fonts.",
        ):
            self.assertNotIn(forbidden, lowered)

    def test_integrated_signal_styles_are_declared(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        for value in ("#10191b", "#f4f2eb", "#27b7a7", "#2e63a3"):
            self.assertIn(value, css.lower())
        self.assertIn(".systems-path", css)
        self.assertIn(":focus-visible", css)

    def test_responsive_and_reduced_motion_rules_exist(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn("@media (max-width: 760px)", css)
        self.assertIn("prefers-reduced-motion: reduce", css)

    def test_mobile_layout_does_not_force_viewport_overflow(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertNotIn("min-width: 320px", css)
        self.assertRegex(css, r"html\s*\{[^}]*overflow-x:\s*hidden")

    def test_no_gradients_or_remote_font_imports(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8").lower()
        self.assertNotIn("gradient(", css)
        self.assertNotIn("@import", css)

    def test_light_surface_text_and_focus_treatments_have_contrast(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertRegex(
            css,
            r"\.hero h1 span\s*\{[^}]*color:\s*var\(--technical-blue\)",
        )
        self.assertRegex(
            css,
            r"\.systems-path li::after\s*\{[^}]*color:\s*var\(--technical-blue\)",
        )
        focus_rule = re.search(r":focus-visible\s*\{([^}]+)\}", css)
        self.assertIsNotNone(focus_rule)
        self.assertIn("outline: 3px solid var(--graphite)", focus_rule.group(1))
        self.assertIn("box-shadow: 0 0 0 3px var(--surface)", focus_rule.group(1))

    def test_script_is_progressive_and_reduced_motion_aware(self):
        script = (ROOT / "script.js").read_text(encoding="utf-8")
        self.assertIn("IntersectionObserver", script)
        self.assertIn("prefers-reduced-motion: reduce", script)
        self.assertIn("data-enhanced", script)

    def test_only_enhanced_content_can_begin_hidden(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertNotIn(".reveal { opacity: 0", css)
        self.assertIn('[data-enhanced="true"] .reveal', css)

    def test_print_styles_reveal_content_and_normalize_surfaces(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn("@media print", css)
        print_css = css.split("@media print", 1)[1]
        for value in (
            '[data-enhanced="true"] .reveal',
            "opacity: 1 !important",
            "transform: none !important",
            "transition: none !important",
            "animation: none !important",
            ".site-header",
            "display: none !important",
            "background: #fff !important",
            "color: #000 !important",
        ):
            self.assertIn(value, print_css)


if __name__ == "__main__":
    unittest.main()
