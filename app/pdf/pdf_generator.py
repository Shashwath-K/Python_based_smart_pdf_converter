from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.templates.pdf_templates import PDF_TEMPLATES
from app.enums.templates import PDFTemplate


ALIGNMENT_MAP = {
    "CENTER": TA_CENTER,
    "JUSTIFY": TA_JUSTIFY,
    "LEFT": TA_LEFT
}


def draw_page_border(c: canvas.Canvas, doc, border_width=1):
    width, height = A4
    margin = doc.leftMargin

    c.setLineWidth(border_width)
    c.rect(
        margin - 10,
        margin - 10,
        width - 2 * (margin - 10),
        height - 2 * (margin - 10)
    )


def generate_pdf(content: str, template: PDFTemplate, output_path: str):
    cfg = PDF_TEMPLATES[template]

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=cfg["page"]["margin"],
        rightMargin=cfg["page"]["margin"],
        topMargin=cfg["page"]["margin"],
        bottomMargin=cfg["page"]["margin"]
    )

    story = []

    lines = content.splitlines()
    title_text = lines[0]
    body_lines = lines[1:]

    # -------- Title Style --------
    title_cfg = cfg["title_style"]
    title_style = ParagraphStyle(
        name="TitleStyle",
        fontName=title_cfg["font"],
        fontSize=title_cfg["size"],
        alignment=ALIGNMENT_MAP[title_cfg["alignment"]],
        spaceAfter=title_cfg["space_after"]
    )

    story.append(Paragraph(title_text, title_style))

    # -------- Body Style --------
    body_cfg = cfg["body_style"]
    body_style = ParagraphStyle(
        name="BodyStyle",
        fontName=body_cfg["font"],
        fontSize=body_cfg["size"],
        leading=body_cfg["leading"],
        alignment=ALIGNMENT_MAP[body_cfg["alignment"]],
        spaceAfter=body_cfg["space_after"]
    )

    for line in body_lines:
        if line.strip():
            story.append(Paragraph(line, body_style))
        else:
            story.append(Spacer(1, body_cfg["leading"]))

    # -------- Page Border --------
    def on_page(canvas, doc):
        if cfg["page"].get("border"):
            draw_page_border(
                canvas,
                doc,
                cfg["page"].get("border_width", 1)
            )

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
