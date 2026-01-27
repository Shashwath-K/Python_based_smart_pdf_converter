from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.templates.pdf_templates import PDF_TEMPLATES
from app.enums.templates import PDFTemplate


def generate_pdf(content: str, template: PDFTemplate, output_path: str):
    """
    Generates a structured PDF using ReportLab.
    """

    config = PDF_TEMPLATES[template]
    c = canvas.Canvas(output_path, pagesize=A4)

    width, height = A4
    x_margin = config["margin"]
    y = height - x_margin

    lines = content.splitlines()

    for index, line in enumerate(lines):
        if index == 0:
            c.setFont(config["title_font"], config["title_size"])
        else:
            c.setFont(config["font"], config["body_size"])

        c.drawString(x_margin, y, line)
        y -= config["line_spacing"]

        if y < x_margin:
            c.showPage()
            y = height - x_margin

    c.save()
