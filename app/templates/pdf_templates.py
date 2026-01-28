from app.enums.templates import PDFTemplate

PDF_TEMPLATES = {
    PDFTemplate.CLASSIC: {
        "font": "Times-Roman",
        "title_font": "Times-Bold",
        "title_size": 18,
        "body_size": 11,
        "line_spacing": 14,
        "margin": 60
    },
    PDFTemplate.MODERN: {
        "font": "Helvetica",
        "title_font": "Helvetica-Bold",
        "title_size": 20,
        "body_size": 12,
        "line_spacing": 16,
        "margin": 50
    },
    PDFTemplate.MINIMAL: {
        "font": "Courier",
        "title_font": "Courier-Bold",
        "title_size": 16,
        "body_size": 10,
        "line_spacing": 12,
        "margin": 40
    }
}
