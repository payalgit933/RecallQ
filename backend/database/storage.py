"""
Document storage and database interface for RecallQ.
Reuses and enriches the existing metadata.json database architecture to store:
- File name
- File type (extension)
- Extracted text
- Chunks
- Document metadata (word count, page count, upload date, character count)
- Document SHA-256 hash
- Search representation (keywords, token frequencies, chunk representations)
- Privacy processing status
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import tempfile
import os
import logging

logger = logging.getLogger(__name__)


class DocumentStorage:
    def __init__(self, storage_path: Path):
        self.storage_path = Path(storage_path)
        self.metadata_file = self.storage_path / "metadata.json"
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all stored documents from metadata.json.
        """
        if not self.metadata_file.exists():
            return {}

        try:
            content = self.metadata_file.read_text(encoding="utf-8")
            if not content.strip():
                return {}
            return json.loads(content)
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Error reading metadata database: {e}")
            return {}

    def save_all(self, data: Dict[str, Dict[str, Any]]) -> bool:
        """
        Atomically save all documents to metadata.json.
        Uses temporary file and replace to prevent corruption on Windows.
        """
        try:
            dumped = json.dumps(data, indent=4, ensure_ascii=False)
            temp_file = self.storage_path / f"temp_{os.getpid()}_{self.metadata_file.name}"
            temp_file.write_text(dumped, encoding="utf-8")
            
            # Replace target atomically
            temp_file.replace(self.metadata_file)
            return True
        except Exception as e:
            logger.error(f"Error saving metadata database: {e}")
            try:
                # Direct fallback write
                self.metadata_file.write_text(
                    json.dumps(data, indent=4, ensure_ascii=False),
                    encoding="utf-8"
                )
                return True
            except Exception as fe:
                logger.error(f"Fallback write also failed: {fe}")
                return False

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single document record by stored_name/id.
        """
        data = self.load_all()
        return data.get(doc_id)

    def save_document(self, doc_id: str, doc_data: Dict[str, Any]) -> bool:
        """
        Add or update a document record.
        """
        data = self.load_all()
        data[doc_id] = doc_data
        return self.save_all(data)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove a document record from the database.
        """
        data = self.load_all()
        if doc_id in data:
            del data[doc_id]
            return self.save_all(data)
        return False

    def find_by_hash(self, doc_hash: str) -> Optional[Dict[str, Any]]:
        """
        Check if a document with the same SHA-256 hash already exists.
        Prevents redundant re-indexing of duplicate files.
        """
        if not doc_hash:
            return None
        data = self.load_all()
        for doc_id, doc in data.items():
            if doc.get("document_hash") == doc_hash:
                return doc
        return None

    def list_documents(self) -> List[Dict[str, Any]]:
        """
        Return a clean list of all indexed documents for UI display.
        """
        data = self.load_all()
        documents = []
        for stored_name, doc in data.items():
            documents.append({
                "name": doc.get("name", stored_name),
                "stored_name": stored_name,
                "size": doc.get("size", 0),
                "extension": doc.get("extension", Path(doc.get("name", "")).suffix.lower()),
                "word_count": doc.get("metadata", {}).get("word_count", 0),
                "upload_time": doc.get("upload_time", ""),
                "privacy_protected": doc.get("privacy_protected", True),
                "has_text": bool(doc.get("extracted_text")),
                "chunk_count": len(doc.get("chunks", [])),
                "ocr_extracted": doc.get("metadata", {}).get("ocr_extracted", False),
            })

        documents.sort(key=lambda item: item["name"].lower())
        return documents
