"""Build the executive one-pager PDF from the capstone decision inputs."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


OUTPUT = Path(__file__).with_name("one_pager.pdf")


def build_pdf() -> None:
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="BriefTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=22,
            textColor=colors.HexColor("#17324D"),
            alignment=TA_CENTER,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Deck",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#496273"),
            alignment=TA_CENTER,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Compact",
            parent=styles["BodyText"],
            fontSize=7.8,
            leading=9.5,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading2"],
            fontSize=10,
            leading=12,
            textColor=colors.HexColor("#087E83"),
            spaceBefore=5,
            spaceAfter=3,
        )
    )

    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.42 * inch,
        bottomMargin=0.42 * inch,
        title="AfyaPlus Cost-Optimised AI Deployment",
        author="AfyaPlus Capstone",
    )
    story = [
        Paragraph("AfyaPlus | Cost-Optimised AI Deployment", styles["BriefTitle"]),
        Paragraph("EXECUTIVE DECISION BRIEF &nbsp; | &nbsp; OCTOBER 2026 &nbsp; | &nbsp; USD PLANNING ESTIMATES", styles["Deck"]),
        Paragraph("Conditional GO: human-reviewed pilot", styles["Section"]),
        Paragraph(
            "Use the managed API for a small pilot; keep high-risk/uncertain cases on human review. "
            "NO-GO for autonomous clinical decisions or production 10x until budget, current rates, "
            "latency, and safety gates are evidenced. The runnable local agent is a deterministic "
            "clinic-catalog fallback, not a live model call.",
            styles["Compact"],
        ),
        Paragraph("Monthly cost scenarios", styles["Section"]),
    ]

    table = Table(
        [
            ["Scenario", "Requests/month", "Total / 1,000", "Monthly total"],
            ["Baseline", "100,000", "$5.3790", "$537.90"],
            ["Sustained 10x", "1,000,000", "$0.9790", "$979.01"],
        ],
        colWidths=[2.5 * inch, 1.55 * inch, 1.55 * inch, 1.45 * inch],
        rowHeights=[0.28 * inch, 0.27 * inch, 0.27 * inch],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F0F5F4")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B8C7CC")),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.extend(
        [
            table,
            Spacer(1, 5),
            Paragraph(
                    "At 10x, $979.01 leaves only $20.99 under the proposed $1,000 monthly alert budget. "
                    "Costs assume 450 input + 180 output tokens and 2% retries; platform and staff "
                    "allocations are planning estimates, not quotes. Verify current API prices.",
                styles["Compact"],
            ),
            Paragraph("Operating controls", styles["Section"]),
            Paragraph(
                "<b>Cache:</b> 5/8 public FAQ fixtures hit (62.5%); estimated token cost fell "
                "<b>Cache:</b> 5/8 sample public questions were served from cache (62.5%); "
                "estimated token cost fell from $0.17901 to $0.06713 per 1,000. Cached answers "
                "expire after five minutes; never cache patient-specific triage. Fixture matches "
                "are not clinical quality evidence. &nbsp; <b>Batch:</b> 7 offline jobs grouped "
                "into 2 work groups (71.4% fewer); no bulk-pricing discount or throughput gain "
                "claimed.",
                styles["Compact"],
            ),
            Paragraph(
                "<b>Main risk:</b> a traffic/retry spike can exceed budget and slow service. Mitigate "
                "with alerts at $800 actual, $1,000 actual, and $1,000 forecast; cost tags; capped "
                "retries/concurrency; automatic stopping after repeated provider failures; and human review. These alerts notify operators; "
                "No paid cloud, Redis, GPU, or live 10x test is claimed.",
                styles["Compact"],
            ),
            Paragraph("Trade-off and decision gate", styles["Section"]),
            Paragraph(
                "Pilot gate: keep interactive p95 under 2 seconds (p95 = 95 of 100 requests "
                "finish within 2s), verify live rates, and pass controlled load and safety-quality "
                "checks before traffic expansion. Pause on projected budget breach or SLO/quality "
                "failure. Keep the local Compose/fixture fallback available.",
                styles["Compact"],
            ),
        ]
    )

    def page_footer(canvas, _document) -> None:
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#B8C7CC"))
        canvas.line(0.55 * inch, 0.34 * inch, 7.95 * inch, 0.34 * inch)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#496273"))
        canvas.drawString(0.55 * inch, 0.22 * inch, "Assumptions and reproducible calculations: cost/cost_model.md")
        canvas.drawRightString(7.95 * inch, 0.22 * inch, "Planning estimate; not a clinical or cloud-service guarantee")
        canvas.restoreState()

    document.build(story, onFirstPage=page_footer)


if __name__ == "__main__":
    build_pdf()