from app.pdf.md_complete_conversion import convert_md_complete
from app.enums.templates import PDFTemplate

def reproduce_issues():
    # Long code line to test overflow
    long_code = "print('this is a very long line of code that should definitely wrap if the converter is working correctly otherwise it will just overflow the page and look ugly " * 3 + "')"
    
    # Long text paragraph
    long_text = "This is a very long text paragraph " * 20
    
    md_content = f"""
# Test Overlap/Overflow

{long_text}

```python
{long_code}
def normal_function():
    return True
```

{long_text}

```python
# Another block
x = 1
```

{long_text}
"""
    print("Generating reproduction PDF...")
    convert_md_complete(md_content, "reproduce_issue.pdf", PDFTemplate.MODERN)
    print("PDF generated: reproduce_issue.pdf")

if __name__ == "__main__":
    reproduce_issues()
