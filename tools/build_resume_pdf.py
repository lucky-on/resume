from html import escape
import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
)


GRAPHITE = colors.HexColor("#10191B")
SIGNAL = colors.HexColor("#168F84")
TECHNICAL_BLUE = colors.HexColor("#2E63A3")
TEXT = colors.HexColor("#172123")
MUTED = colors.HexColor("#526062")


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "name": ParagraphStyle(
            "Name",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=23,
            leading=25,
            textColor=GRAPHITE,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "headline": ParagraphStyle(
            "Headline",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.9,
            leading=10.6,
            textColor=TECHNICAL_BLUE,
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
        "contact": ParagraphStyle(
            "Contact",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.1,
            leading=9.6,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=10.6,
            textColor=TECHNICAL_BLUE,
            spaceBefore=4,
            spaceAfter=2,
        ),
        "role": ParagraphStyle(
            "Role",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=8.6,
            leading=10.0,
            textColor=GRAPHITE,
            spaceBefore=2.5,
            spaceAfter=1,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.1,
            leading=9.6,
            textColor=TEXT,
            spaceAfter=2,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.1,
            leading=9.6,
            leftIndent=10,
            firstLineIndent=-6,
            bulletIndent=0,
            textColor=TEXT,
            spaceAfter=1.25,
        ),
        "skills": ParagraphStyle(
            "Skills",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.8,
            leading=9.3,
            textColor=TEXT,
            spaceAfter=2,
        ),
    }


def bullet(text: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(text, styles["bullet"], bulletText="•")


def add_role(
    story: list,
    heading: str,
    bullets: list[str],
    styles: dict[str, ParagraphStyle],
) -> None:
    opening = [Paragraph(heading, styles["role"]), bullet(bullets[0], styles)]
    story.append(KeepTogether(opening))
    story.extend(bullet(item, styles) for item in bullets[1:])


GENERAL = "general"
HAYWARD = "hayward"

HEADLINE = {
    GENERAL: "Engineering Leader | Principal Software Architect | Leading Engineering Teams | Embedded Systems | Medical Devices | C++ Data Platforms",
    HAYWARD: "Principal Firmware &amp; Embedded Systems Engineer | C/C++ | ARM Cortex-M &amp; RTOS | Connected Products | Regulated Devices",
}

SUMMARY = {
    GENERAL: "Engineering leader and principal-level software architect with 20+ years delivering complex hardware/software products across embedded systems, Alexa-scale edge-and-cloud platforms, connected products, and regulated medical devices. Combines hands-on C/C++ architecture with leadership of distributed engineering teams, requirements and interface ownership, vendor management, verification and validation, and full software lifecycle execution. Builds scalable development systems and applies AI-assisted engineering to improve quality, productivity, and delivery speed.",
    HAYWARD: "Principal-level firmware and embedded systems engineer with 20+ years building connected hardware products. Writes production C and C++ on ESP32 and ARM Cortex-M platforms, owning RTOS threading models and task priorities, sensor and peripheral integration, wire protocols, and OTA update paths. Has led firmware architecture, HW/SW partitioning, and release readiness for regulated medical devices and Alexa-scale C++ platforms, and coordinates across hardware, QA/RA, and manufacturing teams. Builds CI/CD with automated end-to-end test on real hardware.",
}

HIGHLIGHTS = {
    GENERAL: [
        "Led and mentored engineering teams across the US, Europe, and Asia, including a six-engineer Amazon ASR core team and current process leadership with 10+ engineers.",
        "Designed and implemented the configurable C++ data-processing framework adopted by 11 Alexa engines across edge and cloud, cutting idea-to-production time for a new engine from 4-6 months to 3-4 weeks.",
        "Wrote the complete firmware from scratch in C and C++ for a connected lighting platform on ESP32/ESP32-S3, and shipped 79 device releases across two product lines.",
        "Led multiple concurrent regulated medical-device programs while modernizing how the software was built, and transitioned critical capability in-house for two projects through vendor coordination and knowledge-transfer.",
    ],
    HAYWARD: [
        "Wrote the complete firmware from scratch in C and C++ for a connected lighting platform on ESP32/ESP32-S3, owning architecture, RTOS threading model and task priorities, sensor handling, wire protocols, and OTA updates, and shipped 79 device releases across two product lines.",
        "Led firmware and embedded software across multiple regulated medical-device programs on STM32/ThreadX and Cortex-M4/M7, architecting cross-processor watchdog health monitoring and owning HW/SW partitioning, verification and validation, and release readiness.",
        "Designed and implemented a configurable C++ data-processing framework adopted by 11 engines from tiny single-core devices to multi-core cloud machines, cutting idea-to-production time for a new engine from 4-6 months to 3-4 weeks.",
        "Led and mentored engineering teams across the US, Europe, and Asia, including a six-engineer Amazon core team and current process leadership with 10+ engineers.",
    ],
}

EXPERTISE = (
    "Architecture: C, C++, Python, SOLID design principles, Clean Code, Clean Architecture, configurable frameworks, systems integration, requirements decomposition, HW/SW partitioning, backend services, database systems, q/k"
    "<br/>Embedded and connected: Embedded Linux, Yocto, QNX/RTOS, ThreadX, FreeRTOS, ESP32/ESP32-S3, STM32, ARM Cortex-M, RS-485, I2C, UART, CAN, MQTT, Wi-Fi, BLE and Bluetooth Classic, RF remote control, OTA firmware update, JTAG/SWD programming and debugging, sensor and peripheral integration, multithreaded/parallel programming"
    "<br/>Medical and leadership: IEC 62304 Class B/C, ISO 13485, ISO 14971, IEC 60601, design controls, V&amp;V, team leadership, mentoring, vendor management, recruiting, AI-assisted development"
)

# Each role is (heading, [(bullet, variants) ...]). BOTH means it appears in every variant.
BOTH = (GENERAL, HAYWARD)

ROLES = [
    (
        "Verathon | Senior Software Engineer | Jul 2026-Present",
        [
            ("Drive adoption of software-development best practices across the Airway device portfolio and 200+ repositories, including SOLID design principles, Clean Code, and Clean Architecture.", BOTH),
            ("Establish scalable development and verification processes with a 10+ engineer team, introducing a structured Agile/Kanban cadence, and lead adoption of AI-assisted engineering.", BOTH),
            ("Streamline production-grade internal tools in close collaboration with IT, aligning engineering workflows with enterprise systems and support requirements.", BOTH),
        ],
    ),
    (
        "GloMove | AI-Assisted Development &amp; Verification | May-Jul 2026",
        [
            ("Established an AI-assisted development and verification process around a custom Claude Code engineering harness, enabling a two-person team to execute the complete idea-to-production cycle.", BOTH),
            ("Developed and released shared PowerUnit and Light firmware on ESP32/ESP32-S3, delivering 49 Light and 30 PowerUnit releases through the OTA update path with every release verified on real hardware.", BOTH),
            ("Automated integration, release, and end-to-end testing into a CI pipeline that exercised physical devices ahead of every firmware release, and streamed device telemetry over MQTT into Grafana dashboards.", BOTH),
        ],
    ),
    (
        "Olympus Corporation of the Americas | Sr. Principal Software Engineer | Jul 2023-May 2026",
        [
            ("Led software engineering across multiple regulated medical-device programs spanning embedded connectivity, Linux platforms, video processing using i.MX8M and Cortex-M4/M7, and STM32/ThreadX fluid-control subsystems.", BOTH),
            ("Defined and drove the embedded software architecture for STM32/ThreadX fluid-control and Cortex-M4/M7 subsystems, owning HW/SW partitioning, interface definition, and integration strategy under IEC 62304 Class B/C.", BOTH),
            ("Served as technical lead and architect for a real-time embedded subsystem that processes streaming sensor data on-device and autonomously commands a safety shutdown within a hard deadline.", (HAYWARD,)),
            ("Translated system needs into software requirements, subsystem architecture, HW/SW partitioning, interfaces, and integration strategies with systems, hardware, QA/RA, operations, and manufacturing teams.", BOTH),
            ("Led verification and validation activities including protocol creation, results review, traceability improvements, and release readiness under IEC 62304 Class B/C processes; architected device-health monitoring via cross-processor watchdog timers.", BOTH),
            ("Managed external partners through late-phase delivery and knowledge-transfer, eliminating external-vendor reliance for two projects and establishing durable in-house ownership.", BOTH),
            ("Established development workflows, engineering standards, design-control documentation, CI/CD pipelines, repositories and coverage guardrails, technical interviewing, AI-enabled practices, Working Backwards, and the Build &amp; Learn community.", BOTH),
        ],
    ),
    (
        "GloMove | Founder &amp; Chief Systems Architect, personal venture built evenings and weekends | Dec 2021-Aug 2023",
        [
            ("Wrote the complete device firmware from scratch in C and C++ for an ESP32/ESP32-S3 connected lighting platform, owning the architecture, RTOS threading model, task priorities, sensor handling, wire protocols, and lighting effects across power-unit and light devices.", BOTH),
            ("Integrated five devices on a shared I2C bus - an AHT20 temperature/humidity sensor, two INA3221 power monitors, and a DS3231 battery-backed RTC with its AT24C32 EEPROM - drove the RS-485 link between power units and lights, and programmed and debugged custom PCBAs over JTAG/SWD alongside the hardware engineer.", BOTH),
            ("Built the OTA firmware-update path end to end, and implemented BLE provisioning to pair power units with the mobile app before consolidating on Wi-Fi-only provisioning.", BOTH),
            ("Defined end-to-end architecture for the distributed platform using custom PCBAs, motion, ambient-light and capacitive-touch sensing, RF remote control, MQTT cloud connectivity with a telemetry dashboard, and mobile-connected control.", BOTH),
            ("Built and led a cross-functional team of hardware, embedded-software, and backend engineers across architecture, prototyping, manufacturing strategy, and supplier selection.", BOTH),
        ],
    ),
    (
        "Appian Corporation | Lead Software Engineer | Dec 2021-Jan 2023",
        [
            ("Helped evolve backend database services and developed practical experience with q/k programming and database-oriented systems.", BOTH),
        ],
    ),
    (
        "Amazon | Alexa | ASR Engine | Jul 2017-Sep 2021",
        [
            ("Senior Software Development Engineer; led a six-engineer ASR core team responsible for foundational engine functionality, legacy support, new core libraries, and migration of 10+ teams.", BOTH),
            ("Designed and implemented a configurable C++ data-processing framework adopted by 11 Alexa engines from tiny single-core devices to multi-core cloud machines, improving onboarding and time to production by 4-5x.", BOTH),
            ("Drove modularization of a monolith with 60+ libraries, 50+ binaries, less than 40% coverage, and 50+ annual contributors; achieved 95%+ coverage on decoupled modules with clearer dependencies and reduced blast radius.", BOTH),
            ("Created documentation, templates, release patterns, and migration paths that improved usability, cross-team adoption, and framework scalability across the Alexa ecosystem.", (GENERAL,)),
            ("Reduced idea-to-production time for a new ASR engine from 4-6 months to 3-4 weeks, simplified monitoring and debugging, led root-cause analysis for complex distributed failures, and drove security certification for 30+ components.", BOTH),
        ],
    ),
    (
        "Amazon | Alexa | TTS Engine and Kindle | Aug 2015-Jul 2017",
        [
            ("Software Development Engineer; added the first DNN-model support to Alexa TTS and released seven engine versions, including one used for the Amazon Polly launch.", BOTH),
            ("Led design and implementation of a runtime add-on system that grew from 2 to 140 add-ons over four years and helped resolve critical launch-time runtime issues.", BOTH),
            ("Led TTS runtime-database modularization, reducing coupling and engine footprint while improving scalability across locales and languages.", (GENERAL,)),
            ("Contributed features and defect fixes to the Kindle Bird\'s Eye View reading experience.", (GENERAL,)),
        ],
    ),
    (
        "Samsung Electronics, HQ | Senior Software Engineer / Project Lead | Oct 2005-Mar 2015",
        [
            ("Progressed through Software Engineer, Remote Team Manager, XOA-E SDK Project Leader, and Senior Software Engineer in the Software Architecture Lab.", BOTH),
            ("Led SDK, common-component, simulator, and developer-experience work for the XOA-E printing platform, including requirements clarification, risk management, V&amp;V coordination, tools, samples, guides, and releases; defined the C++/Java APIs that opened the platform to third-party developers.", BOTH),
            ("Delivered firmware and platform software that shipped to high-volume manufacturing across Samsung MFP product lines, working with production and quality teams through launch.", BOTH),
            ("Managed a remote engineering team, including requirements clarification, time and resource planning, and delivery of Scan to Email through USB, SMB, and FTP, direct-printing, and job-flow capabilities.", BOTH),
            ("Designed multi-partition formatting, file defragmentation, and Immediate and On-Demand Image Overwriting algorithms for Samsung MFP platforms, earning an Excellence Award.", BOTH),
            ("Built image-transfer pipelines for TIFF, BMP, JPEG, GIF, PNG, and PDF variants, including secure and digitally signed formats.", (GENERAL,)),
        ],
    ),
    (
        "Incom Ltd | Software Developer | Mar 2000-Jun 2005",
        [
            ("Developed software for integrated vehicle-location systems, including navigation-data encoding/decoding and optimized scheduling of transmissions between central systems and vehicles over radio and satellite links.", BOTH),
            ("Integrated MapInfo geo-information capabilities with data-transfer systems for real-time navigation-data processing and analysis.", BOTH),
            ("Clarified requirements for a USAID-supported meteorological data-collection system and contributed to scientific research.", (GENERAL,)),
        ],
    ),
]

STANDARDS = {
    GENERAL: "Working knowledge of ISO 13485, ISO 14971, IEC 62304 Class B/C, IEC 60601, FDA QSR / 21 CFR Part 820, design controls, DHF-aligned documentation, traceability, verification and validation, risk review, threat-modeling collaboration, and regulated software lifecycle practices.",
    HAYWARD: "Regulated-product discipline transferable to any safety-conscious hardware program: hazard analysis, traceable requirements, formal verification and validation protocols, design controls, and release readiness, built under ISO 13485, ISO 14971, IEC 62304 Class B/C, IEC 60601, and FDA QSR / 21 CFR Part 820.",
}

VOLUNTEER = "Volunteer: C++ coach, FIRST Robotics team, Westborough High School - CAN bus control of motors and actuators."


def build_pdf(output_path: Path, variant: str = GENERAL) -> None:
    if variant not in (GENERAL, HAYWARD):
        raise ValueError(f"unknown resume variant: {variant}")
    phone = os.environ.get("SERGEY_RESUME_PHONE", "").strip()
    if not phone:
        raise RuntimeError(
            "SERGEY_RESUME_PHONE must be set when building the private-contact PDF"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    styles = make_styles()
    doc = BaseDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=0.45 * inch,
        rightMargin=0.45 * inch,
        topMargin=0.38 * inch,
        bottomMargin=0.36 * inch,
        title="Sergey Didenko Resume",
        author="Sergey Didenko",
    )
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="resume",
    )
    doc.addPageTemplates(PageTemplate(id="resume-pages", frames=[frame]))
    story = []
    story.extend(
        [
            Paragraph("Sergey Didenko, Ph.D.", styles["name"]),
            Paragraph(HEADLINE[variant], styles["headline"]),
            Paragraph(
                f"Westborough, MA | {escape(phone)} | didenkos@gmail.com | linkedin.com/in/didenkos",
                styles["contact"],
            ),
            Paragraph("SUMMARY", styles["section"]),
            Paragraph(SUMMARY[variant], styles["body"]),
            Paragraph("LEADERSHIP &amp; TECHNICAL HIGHLIGHTS", styles["section"]),
        ]
    )
    story.extend(bullet(item, styles) for item in HIGHLIGHTS[variant])
    story.extend(
        [
            Paragraph("CORE EXPERTISE", styles["section"]),
            Paragraph(EXPERTISE, styles["skills"]),
            Paragraph("PROFESSIONAL EXPERIENCE", styles["section"]),
        ]
    )
    for heading, items in ROLES:
        chosen = [text for text, variants in items if variant in variants]
        if chosen:
            add_role(story, heading, chosen, styles)
    story.extend(
        [
            Paragraph("STANDARDS &amp; QUALITY SYSTEMS", styles["section"]),
            Paragraph(STANDARDS[variant], styles["body"]),
            Paragraph("EDUCATION &amp; CREDENTIALS", styles["section"]),
            Paragraph(
                "Doctor of Philosophy (Ph.D.) in Computer Science - Tomsk Polytechnic University, 2004 | Master of Science (M.S.) in Computer Science - Tomsk Polytechnic University, 2001",
                styles["body"],
            ),
            Paragraph(
                "IEC 62304 Training (Developing Medical Device Software) | QNX Momentics IDE | Realtime Programming for QNX Neutrino RTOS | Writing Drivers for Neutrino | Designing RESTful APIs",
                styles["skills"],
            ),
            Paragraph(VOLUNTEER, styles["skills"]),
        ]
    )
    doc.build(story)


if __name__ == "__main__":
    import sys

    # Default: the general resume published with the site.
    # `python3 tools/build_resume_pdf.py hayward <out.pdf>` builds the targeted
    # variant, which is deliberately NOT published on the website.
    variant = sys.argv[1] if len(sys.argv) > 1 else GENERAL
    default = Path(__file__).resolve().parents[1] / "assets" / "Sergey_Didenko_Resume.pdf"
    destination = Path(sys.argv[2]) if len(sys.argv) > 2 else default
    build_pdf(destination, variant)
    print(f"built {variant} resume -> {destination}")
