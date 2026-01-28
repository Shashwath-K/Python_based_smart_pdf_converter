import os
import re
from app.analyzers.document_model import StructuredDocument, DocBlock


def convert_inline_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    return text


def analyze_markdown(content: str, file_path: str) -> StructuredDocument:
    lines = content.splitlines()
    blocks = []

    title = None
    in_code_block = False
    code_buffer = []
    structure_buffer = []

    for line in lines:
        stripped = line.rstrip()

        # ---------- FENCED CODE BLOCK ----------
        if stripped.strip().startswith("```"):
            if in_code_block:
                blocks.append(DocBlock("code", "\n".join(code_buffer)))
                code_buffer = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_buffer.append(line)
            continue

        # ---------- PROJECT TREE / STRUCTURE ----------
        if re.match(r"^[\s│├└─]+", line):
            structure_buffer.append(line)
            continue
        else:
            if structure_buffer:
                blocks.append(DocBlock("code", "\n".join(structure_buffer)))
                structure_buffer = []

        # ---------- HEADINGS ----------
        if stripped.startswith("#"):
            level = len(stripped.split(" ")[0])
            text = stripped[level:].strip()
            text = convert_inline_markdown(text)

            if level == 1 and title is None:
                title = text

            blocks.append(DocBlock(f"h{level}", text))
            continue

        # ---------- BULLETS ----------
        if stripped.startswith("- "):
            blocks.append(
                DocBlock("bullet", convert_inline_markdown(stripped[2:]))
            )
            continue

        # ---------- BLOCKQUOTE ----------
        if stripped.startswith(">"):
            blocks.append(
                DocBlock("quote", convert_inline_markdown(stripped[1:].strip()))
            )
            continue

        # ---------- PARAGRAPH ----------
        if stripped:
            blocks.append(
                DocBlock("paragraph", convert_inline_markdown(stripped))
            )

    if structure_buffer:
        blocks.append(DocBlock("code", "\n".join(structure_buffer)))

    if not title:
        filename = os.path.basename(file_path)
        title = os.path.splitext(filename)[0].replace("_", " ").title()

    return StructuredDocument(title=title, blocks=blocks)
