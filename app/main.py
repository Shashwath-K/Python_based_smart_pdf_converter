import tempfile
import gradio as gr

from app.validators.file_validator import validate_file
from app.parsers.txt_parser import parse_txt
from app.parsers.md_parser import parse_md
from app.parsers.docx_parser import parse_docx
from app.parsers.bin_parser import parse_bin
from app.parsers.csv_parser import parse_csv
from app.parsers.html_parser import parse_html

from app.parsers.bin_parser import parse_bin
from app.parsers.csv_parser import parse_csv
from app.parsers.html_parser import parse_html

from app.analyzers.content_analyzer import normalize_content
from app.analyzers.markdown_analyzer import analyze_markdown
from app.analyzers.plaintext_analyzer import analyze_plaintext

from app.pdf.md_complete_conversion import convert_md_complete
from app.pdf.pdf_generator import generate_pdf
from app.docx.docx_generator import generate_docx
from app.docx.md_docx_converter import convert_md_to_docx

from app.enums.templates import PDFTemplate
from app.enums.file_types import SupportedFileType
from app.exceptions.custom_exceptions import FileValidationError, ParsingError


def convert_file(file, template_choice, use_filename_as_heading, output_format="PDF"):
    try:
        file_type = validate_file(file)

        # --- MARKDOWN HANDLING ---
        if file_type == SupportedFileType.MD:
            text_content = parse_md(file)
            
            if use_filename_as_heading and not text_content.lstrip().startswith("#"):
                import os
                filename = os.path.basename(file.name)
                title = os.path.splitext(filename)[0].replace("_", " ").title()
                text_content = f"# {title}\n\n{text_content}"

            if output_format == "DOCX":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                    convert_md_to_docx(text_content, tmp.name, PDFTemplate(template_choice))
                    return tmp.name
            else:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    convert_md_complete(text_content, tmp.name, PDFTemplate(template_choice))
                    return tmp.name

        # --- OTHER FORMATS ---
        if file_type == SupportedFileType.TXT:
            content = parse_txt(file)
        elif file_type == SupportedFileType.DOCX:
            content = parse_docx(file)
        elif file_type == SupportedFileType.CSV:
            content = parse_csv(file)
        elif file_type == SupportedFileType.HTML:
            content = parse_html(file)
        else:
            content = parse_bin(file)

        content = normalize_content(content, file.name, use_filename_as_heading)
        document = analyze_plaintext(content, file.name)
        
        if output_format == "DOCX":
             with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                generate_docx(document, PDFTemplate(template_choice), tmp.name)
                return tmp.name
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                generate_pdf(
                    document=document,
                    template=PDFTemplate(template_choice),
                    output_path=tmp.name
                )
                return tmp.name

    except (FileValidationError, ParsingError) as e:
        raise gr.Error(str(e))


def launch_app():
    gr.Interface(
        fn=convert_file,
        inputs=[
            gr.File(label="Upload File"),
            gr.Dropdown(
                choices=[t.value for t in PDFTemplate],
                label="Choose PDF Template",
                value=PDFTemplate.CLASSIC.value  # Default value
            ),
            gr.Checkbox(label="Use Filename as Heading", value=True),
            gr.Radio(
                choices=["PDF", "DOCX"],
                label="Output Format",
                value="PDF"
            )
        ],
        outputs=gr.File(label="Download Document"),
        title="Semantic File to PDF Converter",
        description="Markdown-aware conversion with headings, lists, code blocks, and professional layout"
    ).launch()


if __name__ == "__main__":
    launch_app()
