"""
Resume Text & Metadata Extraction Module.
Uses PyMuPDF (fitz) for PDF documents and python-docx for Word files.
Cleans raw text and extracts structural metadata for ATS formatting analysis.
"""

import io
import re
try:
    import pymupdf as fitz
except ImportError:
    import fitz  # PyMuPDF
import docx


def clean_extracted_text(raw_text: str) -> str:
    """
    Standardize whitespace, line breaks, and eliminate excessive control characters
    while preserving paragraph and section boundaries.
    """
    if not raw_text:
        return ""
    # Standardize carriage returns to newlines
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse 3 or more consecutive newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Replace tabs with spaces
    text = text.replace("\t", " ")
    # Replace multiple horizontal spaces with a single space
    lines = []
    for line in text.split("\n"):
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(cleaned_line)
    return "\n".join(lines).strip()


def extract_from_pdf(file_bytes: bytes):
    """
    Extract readable text and document inspection metrics from PDF via PyMuPDF.
    Returns:
      (success: bool, text: str, metadata: dict, error_message: str)
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page_count = len(doc)
        if page_count == 0:
            return False, "", {}, "The uploaded PDF document appears to be empty."

        full_text = []
        image_count = 0
        has_drawings = False

        for page in doc:
            page_text = page.get_text()
            if page_text:
                full_text.append(page_text)
            # Count embedded raster images
            images = page.get_images()
            image_count += len(images)
            # Check for vector graphics / drawings
            drawings = page.get_drawings()
            if len(drawings) > 10:
                has_drawings = True

        combined_text = "\n".join(full_text)
        cleaned_text = clean_extracted_text(combined_text)

        # Transparency check: If no readable characters were extracted, it's an image-only / scanned PDF
        if len(cleaned_text.strip()) < 30:
            return (
                False,
                "",
                {},
                "Unable to read this resume. Please upload a text-based PDF or DOCX file. Scanned or image-only PDFs cannot be reliably parsed by ATS systems."
            )

        metadata = {
            "file_type": "PDF",
            "page_count": page_count,
            "image_count": image_count,
            "has_drawings": has_drawings,
            "char_count": len(cleaned_text),
            "word_count": len(cleaned_text.split())
        }

        return True, cleaned_text, metadata, ""

    except Exception as e:
        return False, "", {}, f"Error reading PDF file: {str(e)}"


def extract_from_docx(file_bytes: bytes):
    """
    Extract text and document inspection metrics from DOCX via python-docx.
    Returns:
      (success: bool, text: str, metadata: dict, error_message: str)
    """
    try:
        doc_file = io.BytesIO(file_bytes)
        doc = docx.Document(doc_file)

        paragraphs_text = []
        headings_count = 0
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                paragraphs_text.append(text)
                if p.style and "heading" in p.style.name.lower():
                    headings_count += 1

        # Extract table text
        table_text = []
        table_count = len(doc.tables)
        for table in doc.tables:
            for row in table.rows:
                row_cells = [c.text.strip() for c in row.cells if c.text.strip()]
                if row_cells:
                    table_text.append(" | ".join(row_cells))

        combined_text = "\n".join(paragraphs_text + table_text)
        cleaned_text = clean_extracted_text(combined_text)

        if len(cleaned_text.strip()) < 30:
            return (
                False,
                "",
                {},
                "Unable to read this resume. Please upload a text-based PDF or DOCX file."
            )

        metadata = {
            "file_type": "DOCX",
            "page_count": 1,  # DOCX is flow-based; estimated 1-2 pages
            "table_count": table_count,
            "headings_count": headings_count,
            "char_count": len(cleaned_text),
            "word_count": len(cleaned_text.split())
        }

        return True, cleaned_text, metadata, ""

    except Exception as e:
        return False, "", {}, f"Error reading DOCX file: {str(e)}"


def parse_resume(file_bytes: bytes, filename: str):
    """
    Dispatcher function to detect extension (.pdf, .docx) and parse accordingly.
    """
    lower_name = filename.lower().strip()
    if lower_name.endswith(".pdf"):
        return extract_from_pdf(file_bytes)
    elif lower_name.endswith(".docx"):
        return extract_from_docx(file_bytes)
    else:
        return False, "", {}, "Please upload a PDF or DOCX resume."
