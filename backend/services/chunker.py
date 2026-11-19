"""
Chunking module for RecallQ.
Divides extracted document text into manageable, semantically coherent passages.
"""

from typing import List, Dict, Any
import re


def chunk_text(
    text: str,
    target_words_per_chunk: int = 120,
    overlap_words: int = 25
) -> List[Dict[str, Any]]:
    """
    Divide extracted text into overlapping chunks of readable passages.
    Preserves paragraph or sentence boundaries where possible.
    """
    if not text or not text.strip():
        return []

    # First, split by paragraphs
    raw_paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    # If document has multiple well-formed paragraphs
    words = text.split()
    if len(words) <= target_words_per_chunk:
        return [{
            "chunk_id": 0,
            "text": text.strip(),
            "word_count": len(words),
            "char_count": len(text.strip())
        }]

    # Build chunks by grouping paragraphs or sentences
    chunks = []
    current_chunk_words = []
    chunk_index = 0

    # Tokenize into sentences or paragraph units
    # Fallback to word-window chunking
    step = max(1, target_words_per_chunk - overlap_words)
    total_words = len(words)

    for i in range(0, total_words, step):
        chunk_words = words[i:i + target_words_per_chunk]
        chunk_str = " ".join(chunk_words).strip()
        if chunk_str:
            chunks.append({
                "chunk_id": chunk_index,
                "text": chunk_str,
                "word_count": len(chunk_words),
                "char_count": len(chunk_str)
            })
            chunk_index += 1

        if i + target_words_per_chunk >= total_words:
            break

    return chunks
