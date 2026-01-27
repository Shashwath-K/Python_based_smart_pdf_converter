from app.enums.file_types import SupportedFileType
from app.enums.error_codes import AppErrorCode
from app.exceptions.custom_exceptions import FileValidationError
from app.utils.constants import MAX_FILE_SIZE


def validate_file(file):
    """
    Validates uploaded file for:
    - Presence
    - Supported extension
    - Size constraint
    """

    if file is None:
        raise FileValidationError("No file uploaded")

    if not hasattr(file, "name") or not hasattr(file, "size"):
        raise FileValidationError("Invalid file object")

    if file.size == 0:
        raise FileValidationError(AppErrorCode.EMPTY_FILE.value)

    if file.size > MAX_FILE_SIZE:
        raise FileValidationError(AppErrorCode.FILE_TOO_LARGE.value)

    extension = file.name.split(".")[-1].lower()

    if extension not in SupportedFileType.list_values():
        raise FileValidationError(AppErrorCode.INVALID_FILE_TYPE.value)

    return SupportedFileType(extension)
