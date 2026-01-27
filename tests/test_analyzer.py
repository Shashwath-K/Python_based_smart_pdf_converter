from app.analyzers.content_analyzer import has_heading, normalize_content


def test_detects_existing_heading():
    content = "# Sample Heading\nThis is content"
    assert has_heading(content) is True


def test_detects_uppercase_heading():
    content = "SAMPLE TITLE\nBody text"
    assert has_heading(content) is True


def test_injects_heading_when_missing():
    content = "This is body content only"
    result = normalize_content(content, "test_file.txt")
    assert "Test File" in result


def test_does_not_duplicate_heading():
    content = "# Existing Heading\nContent"
    result = normalize_content(content, "file.txt")
    assert result.count("Heading") == 1
