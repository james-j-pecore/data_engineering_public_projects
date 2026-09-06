"""Splits documents into overlapping, fixed-length character chunks.

Character length, not tokens: close enough to token count for splitting purposes at this
corpus's scale, and avoids pulling in a tokenizer dependency just to decide chunk boundaries.
"""

from src.config import CHUNK_OVERLAP_RATIO


def chunk_text(text: str, chunk_size: int, overlap_ratio: float = CHUNK_OVERLAP_RATIO) -> list[str]:
    """Slide a chunk_size-character window over text with overlap between consecutive chunks."""
    text = text.strip()
    if not text:
        return []

    overlap = int(chunk_size * overlap_ratio)
    step = chunk_size - overlap

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start += step
    return chunks


def chunk_documents(documents: list[dict], chunk_size: int) -> list[dict]:
    """documents: [{"source_path": ..., "text": ...}, ...] -> one row per chunk.

    Returns [{"source_path": ..., "chunk_index": ..., "chunk_text": ...}, ...].
    """
    rows = []
    for doc in documents:
        pieces = chunk_text(doc["text"], chunk_size)
        for i, piece in enumerate(pieces):
            rows.append({"source_path": doc["source_path"], "chunk_index": i, "chunk_text": piece})
    return rows


if __name__ == "__main__":
    from src.crawl import read_documents

    docs = read_documents()
    for size in (300, 600, 1200):
        rows = chunk_documents(docs, size)
        print(f"chunk_size={size}: {len(rows)} chunks across {len(docs)} documents")
