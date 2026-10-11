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
            fontSize=8.3,
            leading=11,
            spaceAfter=4,
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
        Paragraph("EXECUTIVE DECISION BRIEF &nbsp; | &nbsp; OCTOBER 2026 &nbsp; | &nbsp; USD PLANNING ESTIMATE", styles["Deck"]),
        Paragraph("Recommendation", styles["Section"]),
        Paragraph(
            "Keep a managed model API for the pilot and route eligible low-risk work to "
            "gpt-4o-mini. Preserve human review for high-risk or ambiguous cases. "
            "Defer GPU self-hosting at current modeled traffic.",
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
                "Token spend is $0.17901/1,000 at 450 input + 180 output tokens and a 2% retry "
                "allowance. Infrastructure and people/ops are disclosed planning allocations, "
                "not quotes. Verify current OpenRouter rates before budgeting.",
                styles["Compact"],
            ),
            Paragraph("Operating controls", styles["Section"]),
            Paragraph(
                "<b>Cache:</b> 5/8 public FAQ fixture requests hit (62.5%); five-minute TTL; "
                "patient-specific answers are not cached. &nbsp; <b>Batch:</b> 7 mock offline "
                "jobs grouped into 2 local batches; no provider discount claimed.",
                styles["Compact"],
            ),
            Paragraph(
                "<b>Budget:</b> proposed $1,000 monthly alert cap with 80%/100% actual and "
                "100% forecast notices; alerts do not stop spend. Apply cost-center, environment, "
                "and workload tags. Bound autoscaling by quotas; use capped retries and a circuit "
                "breaker. Local Compose and written Azure/AWS configs are the fallback; no paid "
                "cloud, GPU, Redis, Kubernetes, or live load test is claimed.",
                styles["Compact"],
            ),
            Paragraph("Trade-off and decision gate", styles["Section"]),
            Paragraph(
                "Managed API avoids fixed serving capacity and model operations, but retains "
                "provider price, quota, and availability exposure. The illustrative self-host "
                "break-even is about 15.25M requests/month ($1/hour GPU plus 40 operations "
                "hours/month); it is not a procurement result. Serverless cold starts and "
                "prompt/model A/B changes must meet p95 and quality gates. Quantization, pruning, "
                "and KV-cache tuning are self-host levers, not API savings. Validate current "
                "rates, throughput, retries, and quality at controlled 10x.",
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