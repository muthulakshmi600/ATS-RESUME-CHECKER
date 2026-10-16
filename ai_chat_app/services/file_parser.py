"""
File parsing service for AI Chat Application.
Extracts readable text and tabular summaries from:
- PDF (.pdf)
- DOCX (.docx)
- TXT / Markdown / Code (.txt, .md, .py, .js, .json, .html, .css, etc.)
- CSV (.csv)
- Excel (.xlsx, .xls)
- PowerPoint (.pptx)
- Images (.jpg, .jpeg, .png, .webp)
"""

import os
import io
import base64
from pathlib import Path


def extract_file_content(file_path: str, original_filename: str = "") -> dict:
    """
    Extracts text, metadata, and preview information from an uploaded file.
    Returns a dictionary:
    {
        "status": "ok" | "error",
        "text": str,
        "preview": str,
        "type_category": "document" | "spreadsheet" | "presentation" | "image" | "code" | "other",
        "details": dict,
        "error": str | None
    }
    """
    ext = Path(original_filename or file_path).suffix.lower()
    
    try:
        if ext == ".pdf":
            return _parse_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return _parse_docx(file_path)
        elif ext in [".txt", ".md", ".log", ".json", ".xml", ".html", ".css", ".js", ".ts", ".py", ".java", ".c", ".cpp", ".sql", ".sh"]:
            return _parse_text(file_path, ext)
        elif ext == ".csv":
            return _parse_csv(file_path)
        elif ext in [".xlsx", ".xls"]:
            return _parse_excel(file_path)
        elif ext in [".pptx", ".ppt"]:
            return _parse_pptx(file_path)
        elif ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"]:
            return _parse_image(file_path, ext)
        else:
            return {
                "status": "ok",
                "text": f"Uploaded file: {os.path.basename(file_path)} (Binary/unsupported text format)",
                "preview": "Binary or unrecognized file format. Direct text parsing not available.",
                "type_category": "other",
                "details": {"size": os.path.getsize(file_path)},
                "error": None
            }
    except Exception as e:
        return {
            "status": "error",
            "text": "",
            "preview": f"Error reading file: {str(e)}",
            "type_category": "other",
            "details": {},
            "error": str(e)
        }


def _parse_pdf(file_path: str) -> dict:
    """Extracts text from PDF using PyMuPDF (fitz) or PyPDF2 fallback."""
    text_content = []
    page_count = 0

    # Try pymupdf (fitz) first
    try:
        import pymupdf
        doc = pymupdf.open(file_path)
        page_count = len(doc)
        for page_idx in range(min(page_count, 50)):  # Max 50 pages for speed
            text_content.append(doc[page_idx].get_text("text"))
        doc.close()
    except Exception:
        # Fallback to PyPDF2
        try:
            import PyPDF2
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                page_count = len(reader.pages)
                for page_idx in range(min(page_count, 50)):
                    p_text = reader.pages[page_idx].extract_text()
                    if p_text:
                        text_content.append(p_text)
        except Exception as e:
            raise RuntimeError(f"Failed to extract PDF text: {e}")

    full_text = "\n\n".join(text_content).strip()
    preview = full_text[:1200] + ("..." if len(full_text) > 1200 else "")

    return {
        "status": "ok",
        "text": full_text,
        "preview": preview or "(Empty or scanned PDF with no extractable text)",
        "type_category": "document",
        "details": {"pages": page_count, "char_count": len(full_text)},
        "error": None
    }


def _parse_docx(file_path: str) -> dict:
    """Extracts text from Microsoft Word documents."""
    import docx
    doc = docx.Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    
    # Also extract tables
    table_texts = []
    for table in doc.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            table_texts.append(" | ".join(cells))
            
    full_text = "\n\n".join(paragraphs + table_texts).strip()
    preview = full_text[:1200] + ("..." if len(full_text) > 1200 else "")

    return {
        "status": "ok",
        "text": full_text,
        "preview": preview or "(Empty Word Document)",
        "type_category": "document",
        "details": {"paragraphs": len(paragraphs), "tables": len(doc.tables)},
        "error": None
    }


def _parse_text(file_path: str, ext: str) -> dict:
    """Extracts plain text with multiple encoding fallback."""
    encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252"]
    content = ""
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue

    cat = "code" if ext in [".py", ".js", ".ts", ".html", ".css", ".json", ".sql", ".sh"] else "document"
    preview = content[:1500] + ("..." if len(content) > 1500 else "")

    return {
        "status": "ok",
        "text": content,
        "preview": preview,
        "type_category": cat,
        "details": {"lines": len(content.splitlines()), "char_count": len(content)},
        "error": None
    }


def _parse_csv(file_path: str) -> dict:
    """Extracts tabular overview and structured summary of CSV."""
    import pandas as pd
    df = pd.read_csv(file_path, nrows=500)
    
    summary_lines = [
        f"CSV File Summary: {df.shape[0]} preview rows, {df.shape[1]} columns",
        f"Columns: {', '.join(df.columns.astype(str))}",
        "\nData Preview (First 10 rows):",
        df.head(10).to_string(index=False),
        "\nStatistical Summary:",
        df.describe(include='all').to_string()
    ]
    full_text = "\n".join(summary_lines)

    preview_str = df.head(15).to_string(index=False)
    try:
        if hasattr(df, "to_markdown"):
            preview_str = df.head(15).to_markdown(index=False)
    except Exception:
        pass

    return {
        "status": "ok",
        "text": full_text,
        "preview": preview_str,
        "type_category": "spreadsheet",
        "details": {
            "columns": list(df.columns),
            "rows": int(df.shape[0]),
            "cols_count": int(df.shape[1])
        },
        "error": None
    }


def _parse_excel(file_path: str) -> dict:
    """Extracts sheets and tabular data from Excel files."""
    import openpyxl
    import pandas as pd

    excel_file = pd.ExcelFile(file_path)
    sheet_names = excel_file.sheet_names
    
    all_sheet_text = [f"Excel File with {len(sheet_names)} sheet(s): {', '.join(sheet_names)}"]
    first_sheet_preview = ""

    for idx, sheet in enumerate(sheet_names[:5]):  # Process top 5 sheets
        df = pd.read_excel(file_path, sheet_name=sheet, nrows=200)
        all_sheet_text.append(f"\n--- Sheet: '{sheet}' ({df.shape[0]} rows, {df.shape[1]} columns) ---")
        all_sheet_text.append(f"Columns: {', '.join(df.columns.astype(str))}")
        all_sheet_text.append(df.head(8).to_string(index=False))
        if idx == 0:
            first_sheet_preview = df.head(15).to_string(index=False)

    full_text = "\n".join(all_sheet_text)

    return {
        "status": "ok",
        "text": full_text,
        "preview": first_sheet_preview or full_text[:1200],
        "type_category": "spreadsheet",
        "details": {"sheets": sheet_names},
        "error": None
    }


def _parse_pptx(file_path: str) -> dict:
    """Extracts slides and text from PowerPoint presentations."""
    from pptx import Presentation
    prs = Presentation(file_path)
    slides_text = []
    
    for idx, slide in enumerate(prs.slides, start=1):
        slide_parts = [f"Slide {idx}:"]
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                slide_parts.append(shape.text.strip())
        if len(slide_parts) > 1:
            slides_text.append("\n".join(slide_parts))

    full_text = "\n\n---\n\n".join(slides_text)
    preview = full_text[:1200] + ("..." if len(full_text) > 1200 else "")

    return {
        "status": "ok",
        "text": full_text,
        "preview": preview or "(PowerPoint with no extractable text shapes)",
        "type_category": "presentation",
        "details": {"slide_count": len(prs.slides)},
        "error": None
    }


def _parse_image(file_path: str, ext: str) -> dict:
    """Inspects image dimensions, format, and creates base64 encoding."""
    from PIL import Image
    with Image.open(file_path) as img:
        width, height = img.size
        img_format = img.format or ext.replace(".", "").upper()
        mode = img.mode

    # Read base64 thumbnail for quick preview
    with open(file_path, "rb") as f:
        img_data = f.read()
        b64_str = base64.b64encode(img_data).decode("utf-8")
        mime = f"image/{ext.replace('.', '').replace('jpg', 'jpeg')}"

    return {
        "status": "ok",
        "text": f"Image File: {os.path.basename(file_path)} | Dimensions: {width}x{height} | Format: {img_format} | Color Mode: {mode}",
        "preview": f"data:{mime};base64,{b64_str[:100]}... (Image)",
        "type_category": "image",
        "details": {
            "width": width,
            "height": height,
            "format": img_format,
            "base64_data": b64_str,
            "mime_type": mime
        },
        "error": None
    }
