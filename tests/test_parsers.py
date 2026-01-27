import tempfile
from app.parsers.txt_parser import parse_text_file
from app.parsers.bin_parser import parse_bin


class DummyFile:
    def __init__(self, name):
        self.name = name


def test_txt_parser_reads_content():
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
        f.write("Hello World")
        file = DummyFile(f.name)

    content = parse_text_file(file)
    assert "Hello World" in content


def test_bin_parser_handles_binary_data():
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".bin", delete=False) as f:
        f.write(b"\x00\x01Hello\x02")
        file = DummyFile(f.name)

    content = parse_bin(file)
    assert "Hello" in content
