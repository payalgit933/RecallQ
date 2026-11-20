"""
RecallQ Comprehensive Automated Test Suite.
Tests the complete end-to-end workflow:
1. Document Upload & Validation
2. Text Extraction (PDF, DOCX, TXT) & Error Handling
3. Semantic Chunking
4. Privacy Purging & SHA-256 Deduplication
5. Document Database Storage (metadata.json)
6. Natural Language Search (Semantic + Keyword)
7. Explainable Results Generation
8. Flask API Endpoints (/upload, /files, /search, /preview, /delete)
"""

import os
import sys
from pathlib import Path
import unittest
import io

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from services.extractor import extract_document_text
from services.chunker import chunk_text
from services.privacy import compute_file_hash, purge_original_upload
from services.search_engine import search_documents, preprocess_query
from database.storage import DocumentStorage
from app import app


class TestRecallQCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_dir = Path(__file__).resolve().parent.parent / "sample_documents"
        cls.test_storage_dir = backend_dir / "uploads"
        cls.storage = DocumentStorage(cls.test_storage_dir)

    def test_01_text_extraction_txt(self):
        txt_file = self.sample_dir / "Software_Engineering_Lecture_Notes.txt"
        self.assertTrue(txt_file.exists(), "Sample txt file must exist")
        res = extract_document_text(txt_file, ".txt")
        self.assertTrue(res["success"])
        self.assertGreater(res["word_count"], 50)
        self.assertIn("software engineering", res["text"].lower())
        self.assertIn("agile", res["text"].lower())

    def test_02_text_extraction_docx(self):
        docx_file = self.sample_dir / "Summer_Internship_Guidelines_2026.docx"
        self.assertTrue(docx_file.exists(), "Sample docx file must exist")
        res = extract_document_text(docx_file, ".docx")
        self.assertTrue(res["success"])
        self.assertGreater(res["word_count"], 50)
        self.assertIn("internship", res["text"].lower())
        self.assertIn("eligibility", res["text"].lower())

    def test_03_text_extraction_pdf(self):
        pdf_file = self.sample_dir / "Infosys_Campus_Drive_Eligibility.pdf"
        self.assertTrue(pdf_file.exists(), "Sample pdf file must exist")
        res = extract_document_text(pdf_file, ".pdf")
        self.assertTrue(res["success"])
        self.assertGreater(res["word_count"], 50)
        self.assertIn("infosys", res["text"].lower())
        self.assertIn("60%", res["text"].lower())

    def test_04_empty_file_handling(self):
        empty_file = self.sample_dir / "empty_test.txt"
        empty_file.write_text("", encoding="utf-8")
        res = extract_document_text(empty_file, ".txt")
        self.assertFalse(res["success"])
        self.assertIn("empty", res["error"].lower())
        empty_file.unlink(missing_ok=True)

    def test_05_chunking(self):
        sample_text = (
            "This is paragraph one about software engineering principles and design patterns. " * 10
            + "\n\n"
            + "This is paragraph two explaining microservices and unit testing techniques. " * 10
        )
        chunks = chunk_text(sample_text, target_words_per_chunk=50, overlap_words=10)
        self.assertGreater(len(chunks), 1)
        self.assertIn("chunk_id", chunks[0])
        self.assertIn("word_count", chunks[0])
        self.assertIn("text", chunks[0])

    def test_06_privacy_purge(self):
        temp_file = self.sample_dir / "temp_privacy_test.txt"
        temp_file.write_text("Confidential information to be purged", encoding="utf-8")
        file_hash = compute_file_hash(temp_file)
        self.assertTrue(len(file_hash) == 64, "SHA-256 hash must be 64 hex characters")

        success = purge_original_upload(temp_file)
        self.assertTrue(success)
        self.assertFalse(temp_file.exists(), "Temporary original file must be purged from disk")


class TestRecallQSearchAndExplainability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_dir = Path(__file__).resolve().parent.parent / "sample_documents"
        # Extract sample docs for testing search logic
        cls.docs = []
        for p in [
            cls.sample_dir / "Infosys_Campus_Drive_Eligibility.pdf",
            cls.sample_dir / "Summer_Internship_Guidelines_2026.docx",
            cls.sample_dir / "Software_Engineering_Lecture_Notes.txt",
        ]:
            ext = p.suffix.lower()
            res = extract_document_text(p, ext)
            chunks = chunk_text(res["text"])
            cls.docs.append({
                "name": p.name,
                "stored_name": f"test_{p.name}",
                "extension": ext,
                "size": p.stat().st_size,
                "extracted_text": res["text"],
                "chunks": chunks,
                "metadata": {"word_count": res["word_count"]},
                "privacy_protected": True
            })

    def test_07_query_internship_eligibility(self):
        query = "Find my internship eligibility document"
        results = search_documents(query, self.docs)
        self.assertGreater(len(results), 0)
        top_match = results[0]
        self.assertIn("Internship", top_match["document_name"])
        self.assertGreaterEqual(top_match["relevance_score"], 60)
        self.assertTrue(bool(top_match["matching_content"]))
        self.assertTrue(bool(top_match["reason"]))
        self.assertIn("internship", top_match["reason"].lower())

    def test_08_query_infosys_criteria(self):
        query = "Find the PDF containing Infosys eligibility criteria"
        results = search_documents(query, self.docs)
        self.assertGreater(len(results), 0)
        top_match = results[0]
        self.assertIn("Infosys", top_match["document_name"])
        self.assertEqual(top_match["file_type"], ".pdf")
        self.assertIn("infosys", top_match["reason"].lower())

    def test_09_query_software_engineering_notes(self):
        query = "Find my notes about software engineering"
        results = search_documents(query, self.docs)
        self.assertGreater(len(results), 0)
        top_match = results[0]
        self.assertIn("Software_Engineering", top_match["document_name"])
        self.assertIn("software", top_match["reason"].lower())


class TestRecallQFlaskAPIs(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.sample_dir = Path(__file__).resolve().parent.parent / "sample_documents"

    def test_10_landing_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Recall", response.data)

    def test_11_workspace_page(self):
        response = self.client.get("/workspace")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"What would you like to", response.data)

    def test_12_upload_and_search_workflow(self):
        # 1. Upload sample files
        pdf_path = self.sample_dir / "Infosys_Campus_Drive_Eligibility.pdf"
        docx_path = self.sample_dir / "Summer_Internship_Guidelines_2026.docx"
        txt_path = self.sample_dir / "Software_Engineering_Lecture_Notes.txt"

        with open(pdf_path, "rb") as f_pdf, \
             open(docx_path, "rb") as f_docx, \
             open(txt_path, "rb") as f_txt:
            data = {
                "files": [
                    (io.BytesIO(f_pdf.read()), pdf_path.name),
                    (io.BytesIO(f_docx.read()), docx_path.name),
                    (io.BytesIO(f_txt.read()), txt_path.name),
                ]
            }

            upload_res = self.client.post("/upload", data=data, content_type="multipart/form-data")
            self.assertIn(upload_res.status_code, [200, 207])
            upload_json = upload_res.get_json()
            self.assertIn("Successfully processed", upload_json["message"])

        # 2. Check /files list
        files_res = self.client.get("/files")
        self.assertEqual(files_res.status_code, 200)
        files_data = files_res.get_json()["files"]
        file_names = [f["name"] for f in files_data]
        self.assertIn(pdf_path.name, file_names)
        self.assertIn(docx_path.name, file_names)
        self.assertIn(txt_path.name, file_names)

        # 3. Test natural language search API
        search_res = self.client.get("/search?q=Find+my+internship+eligibility+document")
        self.assertEqual(search_res.status_code, 200)
        search_json = search_res.get_json()
        self.assertGreater(search_json["total_results"], 0)
        top_result = search_json["results"][0]
        self.assertIn("Internship", top_result["document_name"])
        self.assertIn("reason", top_result)
        self.assertIn("matching_content", top_result)

        # 4. Test preview of privacy-protected file
        stored_name = top_result["stored_name"]
        preview_res = self.client.get(f"/preview/{stored_name}")
        self.assertEqual(preview_res.status_code, 200)
        self.assertIn(b"Privacy Processed", preview_res.data)

    def test_13_image_ocr_extraction(self):
        img_path = self.sample_dir / "Campus_Placement_Notice.png"
        self.assertTrue(img_path.exists(), "Sample image file must exist")
        res = extract_document_text(img_path, ".png")
        self.assertTrue(res["success"])
        self.assertGreater(res["word_count"], 10)
        self.assertIn(res.get("engine"), ["Windows Native OCR", "Tesseract OCR", None])
        self.assertTrue(any(term in res["text"].lower() for term in ["placement", "recruitment", "eligibility", "campus"]))

    def test_14_redundancy_prevention_deduplication(self):
        txt_path = self.sample_dir / "Software_Engineering_Lecture_Notes.txt"
        with open(txt_path, "rb") as f_txt:
            data = {"files": [(io.BytesIO(f_txt.read()), "Duplicate_Notes_Copy.txt")]}
            res = self.client.post("/upload", data=data, content_type="multipart/form-data")
            self.assertIn(res.status_code, [200, 207])
            json_data = res.get_json()
            # File should have note indicating redundancy prevention
            saved_file = json_data["files"][0]
            self.assertTrue(saved_file.get("redundancy_prevented", False) or "already indexed" in saved_file.get("note", ""))

    def test_15_image_upload_and_ocr_search_workflow(self):
        img_path = self.sample_dir / "Campus_Placement_Notice.png"
        with open(img_path, "rb") as f_img:
            data = {"files": [(io.BytesIO(f_img.read()), img_path.name)]}
            upload_res = self.client.post("/upload", data=data, content_type="multipart/form-data")
            self.assertIn(upload_res.status_code, [200, 207])

        # Search for text written in the image screenshot
        search_res = self.client.get("/search?q=placement+cell+coding+challenge+package")
        self.assertEqual(search_res.status_code, 200)
        search_json = search_res.get_json()
        self.assertGreater(search_json["total_results"], 0)

        # Confirm image was returned as a match
        matched_names = [r["document_name"] for r in search_json["results"]]
        self.assertIn(img_path.name, matched_names)


if __name__ == "__main__":
    unittest.main()
