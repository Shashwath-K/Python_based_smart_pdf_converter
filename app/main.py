import tempfile
import gradio as gr

from app.validators.file_validator import validate_file
from app.parsers.txt_parser import parse_txt
from app.parsers.md_parser import parse_md
from app.parsers.docx_parser import parse_docx
from app.parsers.bin_parser import parse_bin
from app.parsers.csv_parser import parse_csv
from app.parsers.html_parser import parse_html
from app.analyzers.content_analyzer import normalize_content
from app.pdf.pdf_generator import generate_pdf
from app.enums.templates import PDFTemplate
from app.enums.file_types import SupportedFileType
from app.exceptions.custom_exceptions import FileValidationError, ParsingError


def convert_file(file, template_choice):
    try:
        file_type = validate_file(file)

        if file_type == SupportedFileType.TXT:
            content = parse_txt(file)
        elif file_type == SupportedFileType.MD:
            content = parse_md(file)
        elif file_type == SupportedFileType.DOCX:
            content = parse_docx(file)
        elif file_type == SupportedFileType.CSV:
            content = parse_csv(file)
        elif file_type == SupportedFileType.HTML:
            content = parse_html(file)
        else:
            content = parse_bin(file)

        content = normalize_content(content, file.name)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            generate_pdf(
                content=content,
                template=PDFTemplate(template_choice),
                output_path=tmp.name
            )
            return tmp.name

    except (FileValidationError, ParsingError) as e:
        raise gr.Error(str(e))


def launch_app():
    interface = gr.Interface(
        fn=convert_file,
        inputs=[
            gr.File(label="Upload File"),
            gr.Dropdown(
                choices=[t.value for t in PDFTemplate],
                label="Choose PDF Template"
            )
        ],
        outputs=gr.File(label="Download PDF"),
        title="File to Structured PDF Converter",
        description="Converts TXT, MD, DOCX, BIN files into structured PDFs"
    )

    interface.launch()


if __name__ == "__main__":
    launch_app()
