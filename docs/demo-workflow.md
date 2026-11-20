# RecallQ — Demonstration Workflow for Project Review 2

This guide outlines the step-by-step demonstration procedure for presenting RecallQ to the evaluation panel.

---

## 1. Objectives to Highlight
1. **Explainable Retrieval:** Not just returning a file, but explaining *why* it matched and displaying the relevant text excerpt with highlighted terms.
2. **Natural Language Understanding:** Users don't need exact filenames; they can describe content in everyday conversational English.
3. **Multi-Format Ingestion & OCR:** Seamless processing of **PDF**, **DOCX**, **TXT**, and **Images/Photos (PNG, JPG)** with native Optical Character Recognition (OCR).
4. **Redundancy Prevention (Deduplication):** Computes cryptographic SHA-256 hashes to prevent redundant uploads and prevent wasted storage.
5. **Smart Module Filtering:** Instant category exploration for **Documents**, **Images/Photos**, and **All Memories**.
6. **Privacy by Design:** Raw document uploads are temporarily processed for text extraction and indexing, then immediately purged from disk—eliminating long-term raw file storage vulnerabilities while retaining full searchable recall.
7. **Simple Light Theme UI:** Clean, modern, highly readable light theme designed for maximum clarity during reviews.

---

## 2. Pre-Demo Setup (1 minute)

1. Open a terminal in the project directory:
   ```powershell
   cd RecallQ
   ```
2. Activate the virtual environment:
   ```powershell
   .\backend\venv\Scripts\Activate.ps1
   ```
3. Start the Flask server:
   ```powershell
   python backend\app.py
   ```
4. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

---

## 3. Demonstration Script (5-7 minutes)

### Act 1: The Problem & Product Vision (Landing Page)
* **URL:** `http://127.0.0.1:5000/`
* **Action:**
  - Let the cinematic intro play (or click "Skip intro ↗").
  - Point out the core value proposition: *"Remember what you need. Not where you saved it."*
  - Show the animated search simulation demonstrating how digital clutter is transformed into instant recall.
  - Click to enter the Workspace: `http://127.0.0.1:5000/workspace`.

### Act 2: Multi-Format Document Ingestion & Privacy
* **URL:** `http://127.0.0.1:5000/workspace`
* **Action:**
  - Scroll down to the **Upload Section** or click the **＋ Upload Files** button.
  - Browse or drag & drop the sample documents located in the `sample_documents/` folder:
    1. `Infosys_Campus_Drive_Eligibility.pdf` (PDF)
    2. `Summer_Internship_Guidelines_2026.docx` (DOCX Word document)
    3. `Software_Engineering_Lecture_Notes.txt` (Plain text notes)
  - Click Upload.
  - **Key Explanation to the Panel:**
    > *"Notice what just happened behind the scenes: RecallQ validated each file format, computed a SHA-256 integrity hash for deduplication, extracted the readable text, segmented the text into semantic chunks, and stored the searchable index in our metadata database.*
    > *In strict adherence to our privacy policy, the original binary files were safely removed from disk. RecallQ stores zero raw files while maintaining complete semantic memory!"*
  - Observe the updated **Memory Library** table showing file names, types, sizes, word counts, and the **🔒 Privacy Processed** indicator.

### Act 3: Live Natural Language Search Queries
* Scroll to the **Search Section** at the top of the workspace.
* Test Query 1:
  > **"Find the PDF containing Infosys eligibility criteria"**
  - Press Enter or click **Search →**.
  - **Panel Attention:**
    - Notice that RecallQ returns `Infosys_Campus_Drive_Eligibility.pdf` as the top result.
    - Highlight the **85% MATCH · SEMANTIC** badge.
    - Highlight the **Matching Excerpt** displaying the exact passage mentioning 60% marks and eligible branches.
    - Highlight the **Why this matched** box:
      > *"Matched with 85% semantic relevance. This PDF document discusses 'infosys', 'eligibility', 'criteria' matching the context of your natural language request."*

* Test Query 2:
  > **"Find my internship eligibility document"**
  - Press Enter or click **Search →**.
  - Top result returned: `Summer_Internship_Guidelines_2026.docx`.
  - Highlight the **89% MATCH · SEMANTIC** badge.
  - Show the matching excerpt about the 8-week summer internship, 65% aggregate requirement, and final evaluation.
  - Explain how RecallQ understood the natural language intent ("internship eligibility") even though the file is a Word document with a longer descriptive title.

* Test Query 3:
  > **"Find my notes about software engineering"**
  - Press Enter or click **Search →**.
  - Top result returned: `Software_Engineering_Lecture_Notes.txt`.
  - Highlight the **87% MATCH · SEMANTIC** badge.
  - Show the excerpt detailing Agile methodology, MVC architecture, and automated unit testing.

* Test Query 4 (OCR Photo / Screenshot Search):
  > **"Find the placement notice with coding challenge and package"**
  - Press Enter or click **Search →**.
  - Top result returned: `Campus_Placement_Notice.png` (Photo / Screenshot).
  - Highlight the image thumbnail rendered directly in the search results!
  - Highlight the extracted OCR text snippet and explainability box:
    > *"Why this matched: Matched with high relevance based on Windows Native OCR text extraction. The image contains terms 'placement', 'notice', 'coding', 'package'."*
  - This proves to the review panel that RecallQ searches **inside photos and screenshots using OCR**!

### Act 4: Redundancy Prevention (Deduplication Demo)
* Try uploading `Software_Engineering_Lecture_Notes.txt` or `Campus_Placement_Notice.png` a second time.
* **Observe the system response:**
  - RecallQ immediately detects the duplicate SHA-256 hash.
  - Status alert: *"Redundancy prevented: File is already indexed in your memory."*
  - The redundant raw file is deleted, and no duplicate records are added to the memory library.

### Act 5: Category Module Filtering ("Docs", "Photos", "All Files")
* In the **Your Memory Library** section, click the category cards:
  - Click **Documents**: Instantly filters down to only PDF, DOCX, and TXT documents.
  - Click **Images**: Instantly filters down to only OCR-indexed screenshots and photos.
  - Click **Recently Added**: Displays the most recent uploads sorted chronologically.
  - Click **All Memories**: Returns to the complete unified digital memory.

### Act 6: Document Memory Preview
* Click the **Preview Memory** button on any search result (or in the Memory Library table).
* Explain to the panel:
  > *"Even though the original raw file was purged for privacy, clicking Preview dynamically renders RecallQ's verified memory view: the full extracted readable text, individual semantic chunks, word counts, and cryptographic hash."*

### Act 7: Verification & Automated Tests
* Open terminal and run:
  ```powershell
  python -m unittest tests/test_recallq.py -v
  ```
* Show that all 15 automated unit and integration tests pass cleanly with 100% success!

---

## 4. Key Questions & Answers for the Panel

**Q: Where is the database stored?**
> *A: RecallQ uses a JSON-based document store (`uploads/metadata.json`) designed to persist document records, metadata, word counts, SHA-256 hashes, and chunk representations without external database installation overhead, while maintaining full atomic read/write safety.*

**Q: How does semantic search work?**
> *A: RecallQ utilizes a hybrid architecture: it parses natural language queries, removes conversational carrier phrases, constructs TF-IDF bigram vectors across document chunks, and computes cosine similarity. It combines this with keyword term frequency to produce calibrated relevance scores and transparent natural language explanations.*

**Q: What happens if an unsupported or empty file is uploaded?**
> *A: The system validates file types upfront, checks for 0-byte or corrupted files, and returns specific, friendly error messages without crashing the server.*
