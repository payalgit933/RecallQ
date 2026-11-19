"""
Privacy and security module for RecallQ.
Implements the project's privacy-by-design policy:
- Computes SHA-256 document integrity hash
- Safely purges temporary raw uploaded files from disk after text extraction & indexing
- Retains only extracted text, metadata, chunks, and search representations
"""

import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def compute_file_hash(file_path: Path) -> str:
    """
    Compute SHA-256 hash of a file for integrity verification and deduplication.
    """
    hasher = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Error hashing file {file_path}: {e}")
        return ""


def purge_original_upload(file_path: Path) -> bool:
    """
    Remove temporary original uploaded file after successful extraction and indexing.
    Returns True if removed or already absent, False on error.
    """
    try:
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            logger.info(f"Privacy policy applied: original upload removed -> {file_path.name}")
            return True
        return True
    except Exception as e:
        logger.error(f"Could not purge temporary file {file_path}: {e}")
        return False
