from app.exceptions.custom_exceptions import ParsingError
from app.enums.error_codes import AppErrorCode


def parse_txt(file):
    """
    Parses a plain text file.
    """
    try:
        with open(file.name, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        raise ParsingError(AppErrorCode.FILE_READ_ERROR.value)
