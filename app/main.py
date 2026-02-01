import os
import tempfile
import gradio as gr

from app.validators.file_validator import validate_file
from app.parsers.txt_parser import parse_txt
from app.parsers.md_parser import parse_md
from app.parsers.docx_parser import parse_docx
from app.parsers.bin_parser import parse_bin
from app.parsers.csv_parser import parse_csv
from app.parsers.html_parser import parse_html
from app.parsers.ipynb_parser import parse_ipynb

from app.parsers.bin_parser import parse_bin
from app.parsers.csv_parser import parse_csv
from app.parsers.html_parser import parse_html

from app.analyzers.content_analyzer import normalize_content
from app.analyzers.markdown_analyzer import analyze_markdown
from app.analyzers.plaintext_analyzer import analyze_plaintext
from app.analyzers.structure_scanner import scan_structure, bulletize_text

from app.pdf.md_complete_conversion import convert_md_complete
from app.pdf.pdf_generator import generate_pdf
from app.docx.docx_generator import generate_docx
from app.docx.md_docx_converter import convert_md_to_docx

from app.enums.templates import PDFTemplate
from app.enums.file_types import SupportedFileType
from app.exceptions.custom_exceptions import FileValidationError, ParsingError


def convert_file(file, template_choice, use_filename_as_heading, output_format="PDF", auto_structure=False, bulletize=False):
    try:
        file_type = validate_file(file)

        # --- MARKDOWN / IPYNB HANDLING ---
        if file_type == SupportedFileType.MD or file_type == SupportedFileType.IPYNB:
            if file_type == SupportedFileType.IPYNB:
                 text_content = parse_ipynb(file)
            else:
                 text_content = parse_md(file)
            
            # Apply heading ONLY if requested
            if use_filename_as_heading and not text_content.lstrip().startswith("#"):
                filename = os.path.basename(file.name)
                title = os.path.splitext(filename)[0].replace("_", " ").title()
                text_content = f"# {title}\n\n{text_content}"

            # Prepare Output Filename
            original_name = os.path.splitext(os.path.basename(file.name))[0]
            temp_dir = tempfile.mkdtemp()
            
            if output_format == "DOCX":
                output_path = os.path.join(temp_dir, f"{original_name}.docx")
                convert_md_to_docx(text_content, output_path, PDFTemplate(template_choice))
                return output_path
            else:
                output_path = os.path.join(temp_dir, f"{original_name}.pdf")
                convert_md_complete(text_content, output_path, PDFTemplate(template_choice))
                return output_path

        # --- OTHER FORMATS ---
        if file_type == SupportedFileType.TXT:
            content = parse_txt(file)
            # normalize_content removed to prevent double-heading (Title + Body Text)
            # The Title is handled via document.title in the Analyzer.
            
            if bulletize:
                 document = bulletize_text(content, file.name)
            elif auto_structure:
                 document = scan_structure(content, file.name)
            else:
                 document = analyze_plaintext(content, file.name)
                 
        elif file_type == SupportedFileType.DOCX:
            content = parse_docx(file)
            document = analyze_plaintext(content, file.name)
        elif file_type == SupportedFileType.CSV:
            content = parse_csv(file)
            document = analyze_plaintext(content, file.name)
        elif file_type == SupportedFileType.HTML:
            content = parse_html(file)
            document = analyze_plaintext(content, file.name)
        else:
            content = parse_bin(file)
            document = analyze_plaintext(content, file.name)
        
        # Remove title from StructuredDocument if toggle is OFF
        if not use_filename_as_heading:
            document.title = ""
        
        # Prepare Output Filename for other formats
        original_name = os.path.splitext(os.path.basename(file.name))[0]
        temp_dir = tempfile.mkdtemp()

        if output_format == "DOCX":
             output_path = os.path.join(temp_dir, f"{original_name}.docx")
             generate_docx(document, PDFTemplate(template_choice), output_path)
             return output_path
        else:
            output_path = os.path.join(temp_dir, f"{original_name}.pdf")
            generate_pdf(
                document=document,
                template=PDFTemplate(template_choice),
                output_path=output_path
            )
            return output_path

    except (FileValidationError, ParsingError) as e:
        raise gr.Error(str(e))


def update_txt_visibility(file):
    """
    Callback to update visibility of TXT-specific options.
    """
    if file is None:
        return gr.update(visible=False), gr.update(visible=False)
    
    filename = file.name if hasattr(file, 'name') else ""
    if filename.lower().endswith('.txt'):
        return gr.update(visible=True), gr.update(visible=True)
    
    return gr.update(visible=False), gr.update(visible=False)


def launch_app():
    with gr.Blocks(title="Semantic File to PDF Converter") as app:
        gr.Markdown("# Semantic File to PDF Converter")
        gr.Markdown("Markdown-aware conversion with headings, lists, code blocks, and professional layout.")
        
        with gr.Row():
            file_input = gr.File(label="Upload File", file_count="single")
            
        with gr.Row():
            with gr.Column():
                template_dropdown = gr.Dropdown(
                    choices=[t.value for t in PDFTemplate],
                    label="Choose PDF Template",
                    value=PDFTemplate.CLASSIC.value
                )
                output_format = gr.Radio(
                    choices=["PDF", "DOCX"],
                    label="Output Format",
                    value="PDF"
                )
            with gr.Column():
                use_heading = gr.Checkbox(label="Use Filename as Heading", value=True)
                
                # Dynamic Options (Hidden by default)
                auto_structure = gr.Checkbox(label="Auto-Structure (TXT only)", value=False, visible=False)
                bulletize = gr.Checkbox(label="Bulletize All Paragraphs (TXT only)", value=False, visible=False)

        convert_btn = gr.Button("Convert Document", variant="primary")
        output_file = gr.File(label="Download Document")

        # Event Listeners
        file_input.change(
            fn=update_txt_visibility,
            inputs=file_input,
            outputs=[auto_structure, bulletize]
        )

        convert_btn.click(
            fn=convert_file,
            inputs=[
                file_input, 
                template_dropdown, 
                use_heading, 
                output_format, 
                auto_structure, 
                bulletize
            ],
            outputs=output_file
        )

    app.launch()



if __name__ == "__main__":
    launch_app()
