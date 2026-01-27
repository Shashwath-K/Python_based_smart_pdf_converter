from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from textwrap import wrap

from app.templates.pdf_templates import PDF_TEMPLATES
from app.enums.templates import PDFTemplate


def generate_pdf(content: str, template: PDFTemplate, output_path: str):
    config = PDF_TEMPLATES[template]

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    margin = config["margin"]
    max_width = width - (2 * margin)

    y = height - margin

    lines = content.splitlines()

    # ---------- TITLE ----------
    title = lines[0]
    c.setFont(config["title_font"], config["title_size"])

    title_wrapped = wrap(title, 60)
    for line in title_wrapped:
        text_width = c.stringWidth(line, config["title_font"], config["title_size"])
        c.drawString((width - text_width) / 2, y, line)
        y -= config["line_spacing"] + 4

    y -= config["line_spacing"]

    # ---------- BODY ----------
    c.setFont(config["font"], config["body_size"])

    for paragraph in lines[1:]:
        if not paragraph.strip():
            y -= config["line_spacing"]
            continue

        wrapped_lines = wrap(paragraph, 90)

        for line in wrapped_lines:
            if y < margin:
                c.showPage()
                c.setFont(config["font"], config["body_size"])
                y = height - margin

            c.drawString(margin, y, line)
            y -= config["line_spacing"]

    c.save()
