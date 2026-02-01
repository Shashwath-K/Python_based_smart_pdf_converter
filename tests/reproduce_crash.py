from app.pdf.md_complete_conversion import convert_md_complete
from app.enums.templates import PDFTemplate

def reproduce_crash():
    # Generate a code block that is definitely longer than A4 page height
    # A4 is approx 800-900 points high.
    # 100 lines * 12 pts leading = 1200 points.
    
    long_code = "\n".join([f"print('Line {i} of very long code block')" for i in range(200)])
    
    md_content = f"""
# Test Crash

This is a test.

```python
{long_code}
```

End of test.
"""
    print("Generating crash reproduction PDF...")
    try:
        convert_md_complete(md_content, "reproduce_crash.pdf", PDFTemplate.MODERN)
        print("SUCCESS: PDF generated (Crash prevented!)")
    except Exception as e:
        print(f"FAILURE: Crashed with {e}")

if __name__ == "__main__":
    reproduce_crash()
