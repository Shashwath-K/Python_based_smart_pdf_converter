import io
import pytest

from app.validators.file_validator import validate_file
from app.exceptions.custom_exceptions import FileValidationError
from app.utils.constants import MAX_FILE_SIZE


class DummyFile:
    def __init__(self, name, size):
        self.name = name
        self.size = size


def test_valid_file_type_and_size():
    file = DummyFile("sample.txt", 1024)
    file_type = validate_file(file)
    assert file_type.value == "txt"


def test_invalid_file_type():
    file = DummyFile("sample.exe", 1024)
    with pytest.raises(FileValidationError):
        validate_file(file)


def test_file_size_exceeded():
    file = DummyFile("sample.txt", MAX_FILE_SIZE + 1)
    with pytest.raises(FileValidationError):
        validate_file(file)
