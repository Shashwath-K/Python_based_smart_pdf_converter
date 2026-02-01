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
    # Use a soft, modern theme
    theme = gr.themes.Soft(
        primary_hue="blue",
        neutral_hue="slate",
    )

    with gr.Blocks(theme=theme, title="Semantic File to PDF Converter") as app:
        # --- Header ---
        with gr.Row():
            gr.Markdown(
                """
                # 📄 Semantic File to PDF Converter
                **Professional, Markdown-aware document conversion for modern workflows.**  
                *Supports: Markdown (`.md`), Jupyter Notebooks (`.ipynb`), Word (`.docx`), Text (`.txt`), HTML, CSV*
                """
            )

        # --- Main Content ---
        with gr.Row():
            # Left Column: Inputs
            with gr.Column(scale=1):
                file_input = gr.File(label="📂 Upload File", file_count="single", height=300)
            
            # Right Column: Configuration
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Conversion Settings")
                
                with gr.Group():
                    template_dropdown = gr.Dropdown(
                        choices=[t.value for t in PDFTemplate],
                        label="🎨 PDF Template",
                        value=PDFTemplate.CLASSIC.value,
                        interactive=True
                    )
                    output_format = gr.Radio(
                        choices=["PDF", "DOCX"],
                        label="💾 Output Format",
                        value="PDF",
                        interactive=True
                    )

                # Advanced Settings Accordion
                with gr.Accordion("🛠️ Advanced Options", open=False):
                    use_heading = gr.Checkbox(
                        label="Use Filename as Title",
                        value=True,
                        info="Adds a formatted title to the document based on the filename."
                    )
                    
                    # Dynamic Options (Hidden by default)
                    auto_structure = gr.Checkbox(
                        label="Auto-Structure (TXT only)", 
                        value=False, 
                        visible=False,
                        info="Detects headings (UPPERCASE) and lists in plain text files."
                    )
                    bulletize = gr.Checkbox(
                        label="Bulletize All Paragraphs (TXT only)", 
                        value=False, 
                        visible=False,
                        info="Converts every paragraph into a bullet point."
                    )

                # Action Button
                convert_btn = gr.Button("🚀 Convert Document", variant="primary", size="lg")

        # --- Output Section ---
        with gr.Row():
            output_file = gr.File(label="✅ Download Result", interactive=False)

        # --- Footer ---
        with gr.Row():
            gr.Markdown(
                """
                ---
                <div style="text-align: center; color: gray; font-size: 0.9em;">
                    Built with 💙 using <b>Gradio</b>, <b>ReportLab</b>, and <b>Python</b>. | 
                    <a href="https://github.com/Shashwath-K/Python_based_smart_pdf_converter" target="_blank" style="text-decoration: none; color: #4F46E5;">GitHub Repository</a>
                </div>
                """
            )

        # --- Event Listeners ---
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
