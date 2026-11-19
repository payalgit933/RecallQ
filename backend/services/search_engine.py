"""
Natural Language Search Engine & Explainability Module for RecallQ.
Provides semantic embedding/vector search, keyword matching, and explainable retrieval.
"""

import re
from typing import List, Dict, Any, Tuple
import math

# Conversational stop phrases commonly used in natural language retrieval requests
QUERY_FILLER_WORDS = {
    "find", "search", "show", "get", "locate", "where", "is", "are", "which",
    "the", "a", "an", "my", "our", "me", "please", "can", "you", "about",
    "containing", "having", "with", "document", "documents", "file", "files",
    "pdf", "docx", "txt", "text", "notes", "info", "information", "details"
}

ENGLISH_STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}


def preprocess_query(query: str) -> Dict[str, Any]:
    """
    Parse a user's natural language query into clean tokens,
    identifying key search terms and removing conversational fillers.
    """
    clean_query = query.strip()
    words = re.findall(r"\b[A-Za-z0-9_%+-]+\b", clean_query.lower())

    # Content terms excluding fillers
    content_terms = [w for w in words if w not in QUERY_FILLER_WORDS and w not in ENGLISH_STOP_WORDS]
    
    # If all terms were filtered out, preserve non-stop words
    if not content_terms:
        content_terms = [w for w in words if w not in ENGLISH_STOP_WORDS]
    if not content_terms:
        content_terms = words

    # Check for document type hints in query
    type_hint = None
    if "pdf" in words:
        type_hint = ".pdf"
    elif "docx" in words or "word" in words:
        type_hint = ".docx"
    elif "txt" in words or "text" in words or "note" in words or "notes" in words:
        type_hint = ".txt"

    return {
        "raw_query": clean_query,
        "tokens": words,
        "content_terms": content_terms,
        "type_hint": type_hint
    }


def compute_keyword_score(doc: Dict[str, Any], query_info: Dict[str, Any]) -> Tuple[float, str, List[str]]:
    """
    Keyword scoring based on term frequency in filename, extracted text, and chunks.
    Returns (score [0-1], best_matching_snippet, matched_terms).
    """
    content_terms = query_info["content_terms"]
    if not content_terms:
        return 0.0, "", []

    name = doc.get("name", "").lower()
    full_text = doc.get("extracted_text", "")
    full_text_lower = full_text.lower()
    chunks = doc.get("chunks", [])

    matched_terms = []
    term_frequencies = {}

    for term in content_terms:
        # Check in filename
        in_filename = term in name
        count_in_text = full_text_lower.count(term)
        
        if in_filename or count_in_text > 0:
            matched_terms.append(term)
            term_frequencies[term] = count_in_text + (5 if in_filename else 0)

    if not matched_terms:
        return 0.0, "", []

    # Calculate coverage of query terms
    coverage = len(matched_terms) / len(content_terms)
    
    # Calculate frequency boost
    total_matches = sum(term_frequencies.values())
    frequency_factor = min(1.0, math.log(total_matches + 1, 10))

    base_score = (0.7 * coverage) + (0.3 * frequency_factor)

    # Type hint bonus
    if query_info.get("type_hint") and doc.get("extension") == query_info["type_hint"]:
        base_score = min(1.0, base_score + 0.1)

    # Find the chunk with the most matching terms
    best_chunk_text = ""
    best_chunk_score = -1

    for chunk in chunks:
        c_text = chunk.get("text", "")
        c_lower = c_text.lower()
        c_score = sum(c_lower.count(t) for t in content_terms)
        if c_score > best_chunk_score:
            best_chunk_score = c_score
            best_chunk_text = c_text

    if not best_chunk_text and full_text:
        # Fallback to first 300 characters
        best_chunk_text = full_text[:300] + ("..." if len(full_text) > 300 else "")

    return base_score, best_chunk_text, matched_terms


def semantic_search_corpus(
    documents: List[Dict[str, Any]],
    query_info: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Perform semantic vector search using TF-IDF representation across document chunks.
    Falls back gracefully to keyword matching if scikit-learn is not available or corpus is minimal.
    """
    raw_query = query_info["raw_query"]
    content_terms = query_info["content_terms"]
    search_query_str = " ".join(content_terms) if content_terms else raw_query

    use_semantic = True
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
    except ImportError:
        use_semantic = False

    # Flatten all chunks from all documents into a search index
    indexed_items = []
    chunk_texts = []

    for doc in documents:
        doc_id = doc.get("stored_name")
        doc_name = doc.get("name", "")
        full_text = doc.get("extracted_text", "")
        chunks = doc.get("chunks", [])

        if not full_text.strip():
            continue

        # Document level text (or include title multiple times for weighting)
        weighted_doc_text = f"{doc_name} {doc_name} {full_text}"
        indexed_items.append({
            "doc": doc,
            "type": "document",
            "text": weighted_doc_text,
            "sample_snippet": chunks[0]["text"] if chunks else full_text[:250]
        })
        chunk_texts.append(weighted_doc_text)

        # Individual chunks
        for chunk in chunks:
            chunk_body = chunk.get("text", "")
            if chunk_body.strip():
                indexed_items.append({
                    "doc": doc,
                    "type": "chunk",
                    "text": chunk_body,
                    "sample_snippet": chunk_body
                })
                chunk_texts.append(chunk_body)

    results = []

    # If scikit-learn is ready and we have indexed content
    if use_semantic and chunk_texts and len(chunk_texts) > 0:
        try:
            vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words="english",
                sublinear_tf=True
            )
            tfidf_matrix = vectorizer.fit_transform(chunk_texts)
            query_vec = vectorizer.transform([search_query_str])

            similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()

            # Group scores by document
            doc_scores: Dict[str, Dict[str, Any]] = {}
            for idx, sim in enumerate(similarities):
                item = indexed_items[idx]
                doc = item["doc"]
                stored_name = doc.get("stored_name")

                if stored_name not in doc_scores:
                    doc_scores[stored_name] = {
                        "doc": doc,
                        "semantic_score": 0.0,
                        "best_snippet": item["sample_snippet"],
                    }

                if sim > doc_scores[stored_name]["semantic_score"]:
                    doc_scores[stored_name]["semantic_score"] = float(sim)
                    doc_scores[stored_name]["best_snippet"] = item["sample_snippet"]

            # Merge with keyword scoring for hybrid explainability
            for stored_name, entry in doc_scores.items():
                doc = entry["doc"]
                kw_score, kw_snippet, matched_terms = compute_keyword_score(doc, query_info)
                sem_score = entry["semantic_score"]

                # Hybrid scoring: 60% semantic, 40% keyword
                if sem_score > 0 and kw_score > 0:
                    combined_score = (0.6 * sem_score) + (0.4 * kw_score)
                    search_type = "semantic"
                elif sem_score > 0:
                    combined_score = sem_score
                    search_type = "semantic"
                elif kw_score > 0:
                    combined_score = kw_score
                    search_type = "keyword"
                else:
                    continue

                best_snippet = entry["best_snippet"] or kw_snippet

                results.append({
                    "doc": doc,
                    "score": combined_score,
                    "semantic_score": sem_score,
                    "keyword_score": kw_score,
                    "best_snippet": best_snippet,
                    "matched_terms": matched_terms,
                    "search_type": search_type
                })

        except Exception as se:
            # Fallback to pure keyword search if vectorization encounters issue
            use_semantic = False

    if not use_semantic or not results:
        # Fallback pure keyword matching
        for doc in documents:
            kw_score, snippet, matched_terms = compute_keyword_score(doc, query_info)
            if kw_score > 0:
                results.append({
                    "doc": doc,
                    "score": kw_score,
                    "semantic_score": 0.0,
                    "keyword_score": kw_score,
                    "best_snippet": snippet,
                    "matched_terms": matched_terms,
                    "search_type": "keyword"
                })

    # Sort results by score descending
    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def calibrate_relevance_score(raw_score: float, matched_terms_count: int) -> int:
    """
    Calibrate raw vector/hybrid score into a natural percentage (15% - 98%).
    In vector retrieval, raw cosine similarity of 0.35+ represents strong semantic alignment.
    """
    base = raw_score * 1.35
    boost = 0.16 if matched_terms_count >= 2 else (0.08 if matched_terms_count == 1 else 0.0)
    calibrated = min(0.98, max(0.20, base + boost))
    return int(round(calibrated * 100))


def generate_explanation(
    doc: Dict[str, Any],
    query_info: Dict[str, Any],
    score_pct: int,
    search_type: str,
    matched_terms: List[str]
) -> str:
    """
    Generate a natural-language explanation explaining WHY the document matched.
    Highlighting key matching concepts, context, and retrieval type.
    """
    doc_name = doc.get("name", "Document")
    doc_ext = doc.get("extension", "").upper().replace(".", "")
    pct = score_pct

    terms_str = ", ".join(f"'{t}'" for t in matched_terms[:4]) if matched_terms else "semantic intent"

    if search_type == "semantic":
        if matched_terms:
            return (
                f"Matched with {pct}% semantic relevance. This {doc_ext} document discusses "
                f"{terms_str} matching the context of your natural language request."
            )
        else:
            return (
                f"Matched with {pct}% semantic similarity based on conceptual content "
                f"aligning with your query '{query_info['raw_query']}'."
            )
    else:
        return (
            f"Matched with {pct}% relevance based on key content terms ({terms_str}) "
            f"found directly within this {doc_ext} file."
        )


def highlight_snippet(text: str, terms: List[str], max_len: int = 280) -> str:
    """
    Produce a concise snippet focusing around the matched keywords.
    """
    if not text:
        return ""

    clean_text = " ".join(text.split())

    # Find earliest match position
    first_pos = len(clean_text)
    lower_text = clean_text.lower()
    for term in terms:
        p = lower_text.find(term.lower())
        if p != -1 and p < first_pos:
            first_pos = p

    if first_pos == len(clean_text) or first_pos < 60:
        snippet = clean_text[:max_len]
        if len(clean_text) > max_len:
            snippet += "..."
        return snippet

    start = max(0, first_pos - 40)
    end = min(len(clean_text), start + max_len)
    snippet = clean_text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(clean_text):
        snippet = snippet + "..."
    return snippet


def search_documents(
    query: str,
    documents: List[Dict[str, Any]],
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """
    Main search entry point for RecallQ.
    Retrieves, ranks, and explains matching documents.
    """
    if not query or not query.strip():
        return []

    query_info = preprocess_query(query)
    raw_results = semantic_search_corpus(documents, query_info)

    final_results = []
    for item in raw_results[:top_k]:
        doc = item["doc"]
        score = item["score"]
        search_type = item["search_type"]
        matched_terms = item["matched_terms"]
        raw_snippet = item["best_snippet"]

        score_pct = calibrate_relevance_score(score, len(matched_terms))
        explanation = generate_explanation(doc, query_info, score_pct, search_type, matched_terms)
        snippet = highlight_snippet(raw_snippet, matched_terms)

        final_results.append({
            "document_name": doc.get("name", "Unknown File"),
            "stored_name": doc.get("stored_name", ""),
            "file_type": doc.get("extension", ""),
            "size": doc.get("size", 0),
            "relevance_score": score_pct,
            "matching_content": snippet,
            "reason": explanation,
            "search_type": search_type,
            "matched_terms": matched_terms
        })

    return final_results
