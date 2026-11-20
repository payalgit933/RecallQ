from pathlib import Path
from uuid import uuid4
import datetime
import json
import logging

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_from_directory,
    abort,
)
from werkzeug.utils import secure_filename

from database.storage import DocumentStorage
from services.extractor import extract_document_text
from services.chunker import chunk_text
from services.privacy import compute_file_hash, purge_original_upload
from services.search_engine import search_documents

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RecallQ")

app = Flask(__name__)

# Application paths
UPLOAD_FOLDER = Path(app.root_path) / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Initialize document storage database
storage = DocumentStorage(UPLOAD_FOLDER)
METADATA_FILE = storage.metadata_file

# Max upload limit: 25 MB
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

# Supported document and media extensions
DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".docx",
}

MEDIA_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
}

ALLOWED_EXTENSIONS = DOCUMENT_EXTENSIONS | MEDIA_EXTENSIONS

PREVIEW_EXTENSIONS = ALLOWED_EXTENSIONS


# -------------------------------
# Metadata helpers (backward compatibility)
# -------------------------------

def load_metadata():
    return storage.load_all()


def save_metadata(metadata):
    return storage.save_all(metadata)


# -------------------------------
# Landing page with cinematic intro
# -------------------------------

@app.route("/")
def home():
    return render_template("landing.html")


# -------------------------------
# Workspace
# -------------------------------

@app.route("/workspace")
def workspace():
    return render_template("workspace.html")


# -------------------------------
# Upload and Process Files
# -------------------------------

@app.route("/upload", methods=["POST"])
def upload_files():
    files = request.files.getlist("files")

    if not files or all(not file.filename for file in files):
        return jsonify({
            "error": "Please select at least one file to upload."
        }), 400

    saved_files = []
    errors = []

    for file in files:
        if not file or not file.filename:
            continue

        original_name = secure_filename(file.filename)
        extension = Path(original_name).suffix.lower()

        if not original_name:
            errors.append("A file has an invalid or empty filename.")
            continue

        if extension not in ALLOWED_EXTENSIONS:
            errors.append(
                f"{original_name}: File type '{extension}' is not supported. Please upload PDF, DOCX, or TXT documents."
            )
            continue

        unique_name = f"{uuid4().hex}{extension}"
        destination = UPLOAD_FOLDER / unique_name

        try:
            # 1. Save temporary upload to disk
            file.save(destination)
            file_size = destination.stat().st_size

            # Check 0-byte files
            if file_size == 0:
                destination.unlink(missing_ok=True)
                errors.append(f"{original_name}: File is empty (0 bytes).")
                continue

            # 2. Compute SHA-256 document integrity hash
            doc_hash = compute_file_hash(destination)

            # Check for duplicate document / redundancy prevention
            existing_doc = storage.find_by_hash(doc_hash)
            if existing_doc:
                destination.unlink(missing_ok=True)
                saved_files.append({
                    "name": original_name,
                    "stored_name": existing_doc.get("stored_name"),
                    "size": file_size,
                    "word_count": existing_doc.get("metadata", {}).get("word_count", 0),
                    "chunks": len(existing_doc.get("chunks", [])),
                    "privacy_protected": existing_doc.get("privacy_protected", True),
                    "redundancy_prevented": True,
                    "note": f"Redundancy prevented: '{original_name}' is already indexed in RecallQ memory."
                })
                continue

            # 3. Text extraction, OCR & semantic chunking
            if extension in DOCUMENT_EXTENSIONS:
                extraction = extract_document_text(destination, extension)

                if not extraction.get("success"):
                    destination.unlink(missing_ok=True)
                    errors.append(f"{original_name}: {extraction.get('error', 'Text extraction failed.')}")
                    continue

                full_text = extraction["text"]
                chunks = chunk_text(full_text)
                word_count = extraction.get("word_count", len(full_text.split()))

                doc_record = {
                    "name": original_name,
                    "stored_name": unique_name,
                    "extension": extension,
                    "size": file_size,
                    "document_hash": doc_hash,
                    "upload_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "extracted_text": full_text,
                    "chunks": chunks,
                    "metadata": {
                        "word_count": word_count,
                        "char_count": extraction.get("char_count", len(full_text)),
                        "pages": extraction.get("pages", 1),
                        "chunk_count": len(chunks)
                    },
                    "privacy_protected": True
                }

                # Save indexed document record
                storage.save_document(unique_name, doc_record)

                # 4. Enforce Privacy Policy: purge temporary raw upload from disk
                purge_original_upload(destination)

                saved_files.append({
                    "name": original_name,
                    "stored_name": unique_name,
                    "size": file_size,
                    "word_count": word_count,
                    "chunks": len(chunks),
                    "privacy_protected": True
                })

            else:
                # Media file (photo/screenshot) - run OCR text extraction
                extraction = extract_document_text(destination, extension)
                ocr_text = extraction.get("text", "").strip() if extraction.get("success") else ""
                
                if ocr_text:
                    full_text = ocr_text
                    chunks = chunk_text(full_text)
                    word_count = len(full_text.split())
                    ocr_extracted = True
                else:
                    # Clean filename as baseline search representation if photo has no OCR text
                    stem_clean = Path(original_name).stem.replace("_", " ").replace("-", " ")
                    full_text = f"Image file: {original_name}. {stem_clean}"
                    chunks = [full_text]
                    word_count = len(stem_clean.split())
                    ocr_extracted = False

                media_record = {
                    "name": original_name,
                    "stored_name": unique_name,
                    "extension": extension,
                    "size": file_size,
                    "document_hash": doc_hash,
                    "upload_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "extracted_text": full_text,
                    "chunks": chunks,
                    "metadata": {
                        "word_count": word_count,
                        "char_count": len(full_text),
                        "pages": 1,
                        "chunk_count": len(chunks),
                        "ocr_extracted": ocr_extracted,
                        "ocr_engine": extraction.get("engine", "None")
                    },
                    "privacy_protected": False  # Image preserved for visual recall & preview
                }

                storage.save_document(unique_name, media_record)

                saved_files.append({
                    "name": original_name,
                    "stored_name": unique_name,
                    "size": file_size,
                    "word_count": word_count,
                    "chunks": len(chunks),
                    "ocr_extracted": ocr_extracted,
                    "privacy_protected": False
                })

        except OSError as e:
            destination.unlink(missing_ok=True)
            logger.error(f"Error handling upload for {original_name}: {e}")
            errors.append(f"{original_name}: Could not save or process the file ({str(e)}).")

    status_code = 207 if saved_files and errors else (
        400 if errors and not saved_files else 200
    )

    return jsonify({
        "message": f"Successfully processed {len(saved_files)} file(s).",
        "files": saved_files,
        "errors": errors,
    }), status_code


# -------------------------------
# List Indexed Files
# -------------------------------

@app.route("/files", methods=["GET"])
def get_files():
    documents = storage.list_documents()
    return jsonify({
        "files": documents
    })


# -------------------------------
# Preview Files
# -------------------------------

@app.route("/preview/<stored_name>", methods=["GET"])
def preview_file(stored_name):
    doc = storage.get_document(stored_name)

    if not doc:
        abort(404)

    file_path = UPLOAD_FOLDER / stored_name

    # If binary file exists on disk (e.g. image files or retained files)
    if file_path.is_file():
        return send_from_directory(
            UPLOAD_FOLDER,
            stored_name,
            as_attachment=False,
        )

    # If original binary was purged for privacy (documents), render memory preview
    if doc.get("privacy_protected") or doc.get("extracted_text"):
        return render_template("document_preview.html", document=doc)

    abort(404)


# -------------------------------
# Inspect Document Details
# -------------------------------

@app.route("/document/<stored_name>", methods=["GET"])
def get_document_details(stored_name):
    doc = storage.get_document(stored_name)
    if not doc:
        return jsonify({"error": "Document not found."}), 404

    return jsonify({
        "name": doc.get("name"),
        "stored_name": stored_name,
        "extension": doc.get("extension"),
        "size": doc.get("size"),
        "upload_time": doc.get("upload_time"),
        "document_hash": doc.get("document_hash"),
        "metadata": doc.get("metadata"),
        "privacy_protected": doc.get("privacy_protected"),
        "extracted_text": doc.get("extracted_text"),
        "chunks": doc.get("chunks", [])
    })


# -------------------------------
# Natural Language Search API
# -------------------------------

@app.route("/search", methods=["GET", "POST"])
def search_api():
    query = ""

    if request.method == "POST":
        if request.is_json and request.json:
            query = request.json.get("query", "")
        else:
            query = request.form.get("query", "")
    else:
        query = request.args.get("q", "") or request.args.get("query", "")

    query = query.strip()
    if not query:
        return jsonify({
            "query": "",
            "total_results": 0,
            "results": []
        })

    all_docs = list(storage.load_all().values())
    ranked_results = search_documents(query, all_docs)

    return jsonify({
        "query": query,
        "total_results": len(ranked_results),
        "results": ranked_results
    })


# -------------------------------
# Delete Files
# -------------------------------

@app.route("/delete/<stored_name>", methods=["DELETE"])
def delete_file(stored_name):
    doc = storage.get_document(stored_name)

    if not doc:
        return jsonify({
            "error": "File not found."
        }), 404

    file_path = UPLOAD_FOLDER / stored_name

    try:
        if file_path.exists():
            file_path.unlink()

        storage.delete_document(stored_name)

        return jsonify({
            "message": f"Successfully deleted '{doc.get('name', stored_name)}'."
        })

    except OSError as e:
        logger.error(f"Error deleting file {stored_name}: {e}")
        return jsonify({
            "error": "Could not delete the file."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
