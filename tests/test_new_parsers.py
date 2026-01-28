import unittest
import os
import tempfile
from app.parsers.csv_parser import parse_csv
from app.parsers.html_parser import parse_html

class TestNewParsers(unittest.TestCase):

    def setUp(self):
        # Create temporary files for testing
        self.csv_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w+', newline='', encoding='utf-8')
        self.csv_file.write("Name,Age,City\nAlice,30,New York\nBob,25,Los Angeles")
        self.csv_file.close()

        self.html_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w+', encoding='utf-8')
        self.html_file.write("<html><body><h1>Hello World</h1><p>This is a test.</p></body></html>")
        self.html_file.close()

    def tearDown(self):
        os.remove(self.csv_file.name)
        os.remove(self.html_file.name)

    def test_parse_csv(self):
        # Mock file object with .name attribute
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        result = parse_csv(MockFile(self.csv_file.name))
        expected = "Name, Age, City\nAlice, 30, New York\nBob, 25, Los Angeles"
        self.assertEqual(result.strip(), expected.strip())

    def test_parse_html(self):
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        result = parse_html(MockFile(self.html_file.name))
        self.assertIn("Hello World", result)
        self.assertIn("This is a test.", result)
        self.assertNotIn("<html>", result)

if __name__ == '__main__':
    unittest.main()
