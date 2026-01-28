# PDF Converter 
#### File-to-Structured-PDF Converter using Python and Gradio

## Overview
This project is a Python-based web application built using Gradio that converts uploaded files into a well-structured PDF document.
The application emphasizes robust File Handling, Exception Handling, ENUM-based control flow, and template-driven PDF generation.

Supported input formats include
- bin
- txt
- md
- docx
- csv
- html

> The system validates file type and size, analyzes content structure, applies a predefined PDF template, and outputs a downloadable PDF.

# Core Objectives
- Demonstrate strong usage of Python file handling
- Implement clean and explicit exception handling
- Use ENUMs for file types, templates, and error control
- Apply content analysis before document generation
- Follow industry-standard project organization

## Project Structure
``` text
pdf_conversion
│
├── app
│   ├── **init**.py
│   ├── main.py
│   │   Entry point for the Gradio application
│   │   Handles UI binding and workflow orchestration
│   │
│   ├── enums
│   │   ├── **init**.py
│   │   ├── file_types.py
│   │   │   Defines supported file format ENUMs
│   │   ├── templates.py
│   │   │   Defines available PDF template ENUMs
│   │   └── error_codes.py
│   │       Defines application error ENUMs
│   │
│   ├── exceptions
│   │   ├── **init**.py
│   │   └── custom_exceptions.py
│   │       Custom exception classes for validation and parsing
│   │
│   ├── validators
│   │   ├── **init**.py
│   │   └── file_validator.py
│   │       File size and file type validation logic
│   │
│   ├── parsers
│   │   ├── **init**.py
│   │   ├── txt_parser.py
│   │   ├── md_parser.py
│   │   ├── docx_parser.py
│   │   └── bin_parser.py
│   │       Responsible for reading and extracting content
│   │
│   ├── analyzers
│   │   ├── **init**.py
│   │   └── content_analyzer.py
│   │       Detects headings and normalizes document structure
│   │
│   ├── templates
│   │   ├── **init**.py
│   │   └── pdf_templates.py
│   │       Template configuration for PDF layout and styling
│   │
│   ├── pdf
│   │   ├── **init**.py
│   │   └── pdf_generator.py
│   │       Converts structured content into PDF
│   │
│   └── utils
│       ├── **init**.py
│       └── constants.py
│           Application-wide constants such as max file size
│
├── tests
│   ├── **init**.py
│   ├── test_validators.py
│   ├── test_parsers.py
│   └── test_analyzer.py
│   Unit tests for validation and parsing logic
│
├── requirements.txt
│   Python dependencies
│
├── .gitignore
│   Git ignored files and folders
│
└── README.md
```

### Project documentation


**Separation of concerns**
Each layer handles exactly one responsibility

**Scalability**
New file formats, templates, or analyzers can be added without breaking existing logic

**Testability**
Validation, parsing, and analysis are isolated and easy to unit test

**Industry alignment**
This structure mirrors real-world Python backend and tooling projects


**Execution Flow**

- User uploads a file through Gradio
- File validator checks size and format
- Parser extracts content based on file type
- Content analyzer detects or injects headings
- Selected template is applied
- PDF is generated and returned for download