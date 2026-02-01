import json
import os

def parse_ipynb(file) -> str:
    """
    Parses an .ipynb file and converts it into a Markdown string representation.
    """
    try:
        # Read file content
        if hasattr(file, 'read'):
            content = file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
        else:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()

        nb = json.loads(content)
        
        md_output = []
        
        # Extract Cells
        cells = nb.get('cells', [])
        for cell in cells:
            cell_type = cell.get('cell_type')
            source = "".join(cell.get('source', []))
            
            if not source.strip():
                continue

            if cell_type == 'markdown':
                md_output.append(source)
                md_output.append("\n") # Spacing
                
            elif cell_type == 'code':
                # Wrap in python code fence
                md_output.append(f"```python\n{source}\n```")
                md_output.append("\n")
                
                # Note: Skipping outputs for clean "Documentation" look 
                # unless we want to parse text outputs too.
                # User asked for "python cell ... in rectangular box", implying input mainly.
                
        return "\n".join(md_output)

    except Exception as e:
        raise ValueError(f"Failed to parse IPYNB: {str(e)}")
