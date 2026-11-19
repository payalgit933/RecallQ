"""
Text extraction module for RecallQ.
Supports PDF, DOCX, and TXT files with robust error handling and encoding detection.
"""

from pathlib import Path
import re
from typing import Dict, Any


def extract_text_from_pdf(file_path: Path) -> Dict[str, Any]:
    """
    Extract readable text from a PDF document using pypdf.
    """
    try:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError, FileNotDecryptedError
    except ImportError:
        return {
            "success": False,
            "text": "",
            "pages": 0,
            "error": "pypdf library is not installed."
        }

    try:
        reader = PdfReader(str(file_path))
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except (FileNotDecryptedError, Exception):
                return {
                    "success": False,
                    "text": "",
                    "pages": 0,
                    "error": "PDF is encrypted/password protected and cannot be processed."
                }

        page_texts = []
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text() or ""
                page_text = page_text.strip()
                if page_text:
                    page_texts.append(page_text)
            except Exception as pe:
                # Log or continue with next page
                continue

        full_text = "\n\n".join(page_texts).strip()

        if not full_text:
            return {
                "success": False,
                "text": "",
                "pages": len(reader.pages),
                "error": "PDF appears to be empty or contains only scanned images without extractable text."
            }

        return {
            "success": True,
            "text": full_text,
            "pages": len(reader.pages),
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "text": "",
            "pages": 0,
            "error": f"Failed to parse PDF document: {str(e)}"
        }


def extract_text_from_docx(file_path: Path) -> Dict[str, Any]:
    """
    Extract readable text from a Word (.docx) document using python-docx.
    Extracts text from paragraphs as well as tables.
    """
    try:
        import docx
    except ImportError:
        return {
            "success": False,
            "text": "",
            "pages": 1,
            "error": "python-docx library is not installed."
        }

    try:
        doc = docx.Document(str(file_path))
        content_parts = []

        # Extract paragraphs
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                content_parts.append(text)

        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_texts:
                    content_parts.append(" | ".join(row_texts))

        full_text = "\n\n".join(content_parts).strip()

        if not full_text:
            return {
                "success": False,
                "text": "",
                "pages": 1,
                "error": "Word document is empty or contains no readable text."
            }

        return {
            "success": True,
            "text": full_text,
            "pages": 1,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "text": "",
            "pages": 0,
            "error": f"Failed to parse Word document: {str(e)}"
        }


def extract_text_from_txt(file_path: Path) -> Dict[str, Any]:
    """
    Extract readable text from a plaintext (.txt) file with fallback encodings.
    """
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
    raw_bytes = None

    try:
        with open(file_path, "rb") as f:
            raw_bytes = f.read()
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "pages": 1,
            "error": f"Could not read text file: {str(e)}"
        }

    if not raw_bytes or len(raw_bytes.strip()) == 0:
        return {
            "success": False,
            "text": "",
            "pages": 1,
            "error": "Text file is empty (0 bytes)."
        }

    decoded_text = None
    for enc in encodings:
        try:
            decoded_text = raw_bytes.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    if decoded_text is None:
        decoded_text = raw_bytes.decode("utf-8", errors="replace")

    decoded_text = decoded_text.strip()
    if not decoded_text:
        return {
            "success": False,
            "text": "",
            "pages": 1,
            "error": "Text file contains only whitespace."
        }

    return {
        "success": True,
        "text": decoded_text,
        "pages": 1,
        "error": None
    }


def extract_document_text(file_path: Path, extension: str) -> Dict[str, Any]:
    """
    Extract readable text based on file extension.
    Returns standard dictionary with text, stats, and status.
    """
    ext = extension.lower()
    if not ext.startswith("."):
        ext = f".{ext}"

    if ext == ".pdf":
        result = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        result = extract_text_from_docx(file_path)
    elif ext in [".txt", ".text", ".md"]:
        result = extract_text_from_txt(file_path)
    else:
        return {
            "success": False,
            "text": "",
            "pages": 0,
            "word_count": 0,
            "char_count": 0,
            "error": f"Unsupported file type for text extraction: {ext}"
        }

    if result.get("success"):
        text = result["text"]
        # Normalize whitespace
        clean_text = re.sub(r"\r\n", "\n", text)
        clean_text = re.sub(r"[ \t]+", " ", clean_text)
        words = clean_text.split()

        result["text"] = clean_text
        result["word_count"] = len(words)
        result["char_count"] = len(clean_text)
    else:
        result["word_count"] = 0
        result["char_count"] = 0

    return result
