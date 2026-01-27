import re


def has_heading(content: str) -> bool:
    """
    Detects whether the content already has a heading.
    Heuristics:
    - Markdown headings (#)
    - Uppercase first-line titles
    """

    lines = [line.strip() for line in content.splitlines() if line.strip()]

    if not lines:
        return False

    first_line = lines[0]

    if first_line.startswith("#"):
        return True

    if re.match(r"^[A-Z\s]{5,}$", first_line):
        return True

    return False


def normalize_content(content: str, filename: str) -> str:
    """
    Injects a heading if missing.
    """
    if has_heading(content):
        return content

    title = filename.split("/")[-1].split(".")[0]
    title = title.replace("_", " ").replace("-", " ").title()

    return f"{title}\n\n{content}"
