from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import lightgrey
from reportlab.pdfgen import canvas

from app.templates.pdf_templates import PDF_TEMPLATES
from app.enums.templates import PDFTemplate
from app.analyzers.document_model import StructuredDocument


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


def generate_pdf(document: StructuredDocument, template: PDFTemplate, output_path: str):
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

    # ---------- TITLE ----------
    title_style = ParagraphStyle(
        name="Title",
        fontName=cfg["title_style"]["font"],
        fontSize=cfg["title_style"]["size"],
        alignment=TA_CENTER,
        spaceAfter=cfg["title_style"]["space_after"]
    )

    story.append(Paragraph(document.title, title_style))

    # ---------- STYLES ----------
    body_cfg = cfg["body_style"]

    body_style = ParagraphStyle(
        name="Body",
        fontName=body_cfg["font"],
        fontSize=body_cfg["size"],
        leading=body_cfg["leading"],
        alignment=TA_JUSTIFY,
        spaceBefore=6,
        spaceAfter=10
    )

    h_styles = {
        "h1": ParagraphStyle("H1", fontSize=16, spaceBefore=18, spaceAfter=14),
        "h2": ParagraphStyle("H2", fontSize=14, spaceBefore=16, spaceAfter=12),
        "h3": ParagraphStyle("H3", fontSize=12, spaceBefore=14, spaceAfter=10),
    }

    quote_style = ParagraphStyle(
        name="Quote",
        leftIndent=20,
        italic=True,
        textColor="grey",
        spaceBefore=8,
        spaceAfter=8
    )

    for block in document.blocks:
        if block.type in h_styles:
            story.append(Paragraph(block.content, h_styles[block.type]))

        elif block.type == "paragraph":
            story.append(Paragraph(block.content, body_style))

        elif block.type == "bullet":
            story.append(Paragraph(f"• {block.content}", body_style))

        elif block.type == "quote":
            story.append(Paragraph(block.content, quote_style))

        elif block.type == "code":
            story.append(
                Preformatted(
                    block.content,
                    style=ParagraphStyle(
                        name="Code",
                        fontName="Courier",
                        fontSize=9,
                        leading=12,
                        backColor=lightgrey,
                        leftIndent=12,
                        rightIndent=12,
                        spaceBefore=12,
                        spaceAfter=12
                    )
                )
            )

    def on_page(c, d):
        if cfg["page"].get("border"):
            draw_page_border(c, d, cfg["page"].get("border_width", 1))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
