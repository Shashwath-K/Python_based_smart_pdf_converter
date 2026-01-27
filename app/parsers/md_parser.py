from app.exceptions.custom_exceptions import ParsingError
from app.enums.error_codes import AppErrorCode


def parse_md(file):
    """
    Parses a Markdown file as plain text.
    """
    try:
        with open(file.name, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        raise ParsingError(AppErrorCode.FILE_READ_ERROR.value)
