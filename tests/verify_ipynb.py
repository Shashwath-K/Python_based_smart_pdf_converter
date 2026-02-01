from app.parsers.ipynb_parser import parse_ipynb
from app.pdf.md_complete_conversion import convert_md_complete
from app.enums.templates import PDFTemplate

def verify_ipynb():
    print("Parsing Notebook...")
    with open("test_notebook.ipynb", "r") as f:
        md_content = parse_ipynb(f)
    
    print("Markdown Content Generated:")
    print(md_content)
    
    print("\nGenerating PDF...")
    convert_md_complete(md_content, "test_notebook.pdf", PDFTemplate.MODERN)
    print("SUCCESS: test_notebook.pdf generated.")

if __name__ == "__main__":
    verify_ipynb()
