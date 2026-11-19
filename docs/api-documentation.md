# RecallQ — API Endpoint Documentation

This document describes all REST API routes and endpoints implemented in the RecallQ backend for Review 2.

---

## 1. Overview of Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Renders the cinematic landing page intro |
| `GET` | `/workspace` | Renders the main user workspace |
| `POST` | `/upload` | Uploads, extracts, chunks, hashes, and indexes documents |
| `GET` | `/files` | Lists all indexed documents in memory |
| `GET` / `POST` | `/search` | Natural language semantic and keyword search with explainability |
| `GET` | `/document/<stored_name>` | Retrieves detailed chunk and metadata breakdown for a document |
| `GET` | `/preview/<stored_name>` | Renders memory preview of extracted text or serves media file |
| `DELETE` | `/delete/<stored_name>` | Permanently removes an indexed document from memory |

---

## 2. Detailed Endpoint Specifications

### 2.1. Upload Documents
* **Route:** `POST /upload`
* **Content-Type:** `multipart/form-data`
* **Supported Formats:** `.pdf`, `.docx`, `.txt`, `.png`, `.jpg`, `.jpeg`
* **Payload:**
  * `files`: One or more file objects.

#### Privacy-by-Design Processing Pipeline:
1. Validates file extension and non-empty size (max 25 MB).
2. Computes SHA-256 cryptographic hash of file content.
3. Performs deduplication: if identical file is already indexed, prevents redundant reprocessing.
4. Extracts clean text via format-specific extractors (`pypdf`, `python-docx`, multi-encoding text reader).
5. Segments text into semantic passages (chunks) with configurable overlap.
6. Saves document record, metadata, chunks, and hash into `metadata.json`.
7. **Purges the original uploaded file from disk** to protect user privacy.

#### Success Response (`200 OK` or `207 Multi-Status`):
```json
{
  "message": "Successfully processed 3 file(s).",
  "files": [
    {
      "name": "Infosys_Campus_Drive_Eligibility.pdf",
      "stored_name": "a1b2c3d4e5f6.pdf",
      "size": 18452,
      "word_count": 159,
      "chunks": 2,
      "privacy_protected": true
    }
  ],
  "errors": []
}
```

#### Error Response (`400 Bad Request`):
```json
{
  "error": "Please select at least one file to upload."
}
```

---

### 2.2. List Indexed Files
* **Route:** `GET /files`
* **Description:** Retrieves all documents currently indexed in RecallQ's digital memory.

#### Success Response (`200 OK`):
```json
{
  "files": [
    {
      "name": "Infosys_Campus_Drive_Eligibility.pdf",
      "stored_name": "a1b2c3d4e5f6.pdf",
      "size": 18452,
      "extension": ".pdf",
      "word_count": 159,
      "upload_time": "2026-11-19T00:45:00.000Z",
      "privacy_protected": true,
      "has_text": true,
      "chunk_count": 2
    }
  ]
}
```

---

### 2.3. Natural Language Search & Explainability
* **Route:** `GET /search?q=<query>` OR `POST /search`
* **Parameters (GET):** `q` or `query` (string)
* **Payload (POST JSON):** `{"query": "Find the PDF containing Infosys eligibility criteria"}`

#### How it Works:
1. **Query Pre-Processing:** Removes conversational noise ("find", "my", "the", "pdf") while preserving content terms ("infosys", "eligibility", "criteria").
2. **Semantic Representation:** Generates TF-IDF bigram vectors across document chunks and evaluates cosine similarity.
3. **Keyword Boosting:** Checks term frequency in titles and body text.
4. **Hybrid Ranking:** Combines semantic and keyword scores into a calibrated relevance percentage (0%–98%).
5. **Explainability Engine:** Identifies the top matching chunk, extracts a focused snippet with highlighted keywords, and synthesizes a human-readable reason for the match.

#### Success Response (`200 OK`):
```json
{
  "query": "Find the PDF containing Infosys eligibility criteria",
  "total_results": 1,
  "results": [
    {
      "document_name": "Infosys_Campus_Drive_Eligibility.pdf",
      "stored_name": "a1b2c3d4e5f6.pdf",
      "file_type": ".pdf",
      "size": 18452,
      "relevance_score": 85,
      "matching_content": "Infosys Campus Recruitment Drive - Eligibility Criteria 1. Academic Qualification and Minimum Marks Requirements Company: Infosys Limited...",
      "reason": "Matched with 85% semantic relevance. This PDF document discusses 'infosys', 'eligibility', 'criteria' matching the context of your natural language request.",
      "search_type": "semantic",
      "matched_terms": ["infosys", "eligibility", "criteria"]
    }
  ]
}
```

---

### 2.4. Document Memory Preview
* **Route:** `GET /preview/<stored_name>`
* **Description:** 
  - For image files: serves image directly for display.
  - For privacy-processed documents (where original PDF/DOCX was purged): dynamically renders the styled `document_preview.html` displaying the full extracted readable text, semantic chunks, and privacy certification.

---

### 2.5. Document Breakdown
* **Route:** `GET /document/<stored_name>`
* **Description:** Returns JSON detailing metadata, word count, character count, SHA-256 hash, and individual chunks for deep inspection.

---

### 2.6. Delete Document
* **Route:** `DELETE /delete/<stored_name>`
* **Description:** Removes the document and all associated chunks and metadata from the database.

#### Success Response (`200 OK`):
```json
{
  "message": "Successfully deleted 'Infosys_Campus_Drive_Eligibility.pdf'."
}
```
