"""Builds and queries the DuckDB + vss vector store.

One DuckDB file per chunk_size (see ../README.md "Design decisions"): indexing only depends
on chunk_size, k is purely a query-time parameter, so chunk-size configs never get mixed up
and the eval sweep only needs len(CHUNK_SIZES) embedding passes instead of one per (size, k).
"""

import duckdb

from src.chunk import chunk_documents
from src.config import DATA_DIR, EMBEDDING_DIM, db_path
from src.embed import embed_texts


def _connect(chunk_size: int, read_only: bool = False) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(str(db_path(chunk_size)), read_only=read_only)
    con.execute("INSTALL vss")
    con.execute("LOAD vss")
    return con


def build_index(chunk_size: int, documents: list[dict] | None = None) -> int:
    """(Re)builds the chunk_size index from scratch. Returns the number of chunks written."""
    if documents is None:
        from src.crawl import read_documents

        documents = read_documents()

    rows = chunk_documents(documents, chunk_size)
    if not rows:
        raise ValueError("No chunks produced — is the repo crawl returning any documents?")

    vectors = embed_texts([r["chunk_text"] for r in rows])

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = _connect(chunk_size)
    try:
        con.execute(
            f"""
            CREATE OR REPLACE TABLE chunks (
                chunk_id INTEGER,
                source_path VARCHAR,
                chunk_index INTEGER,
                chunk_text VARCHAR,
                embedding FLOAT[{EMBEDDING_DIM}]
            )
            """
        )
        data = [
            (i, row["source_path"], row["chunk_index"], row["chunk_text"], vectors[i].tolist())
            for i, row in enumerate(rows)
        ]
        con.executemany("INSERT INTO chunks VALUES (?, ?, ?, ?, ?)", data)
    finally:
        con.close()
    return len(rows)


def query_index(chunk_size: int, query_embedding, k: int) -> list[dict]:
    """Top-k chunks by cosine similarity to query_embedding, most similar first."""
    path = db_path(chunk_size)
    if not path.exists():
        raise FileNotFoundError(f"No index built for chunk_size={chunk_size} — run build_index first.")

    con = _connect(chunk_size, read_only=True)
    try:
        result = con.execute(
            f"""
            SELECT
                source_path,
                chunk_index,
                chunk_text,
                array_cosine_similarity(embedding, ?::FLOAT[{EMBEDDING_DIM}]) AS similarity
            FROM chunks
            ORDER BY similarity DESC
            LIMIT ?
            """,
            [[float(x) for x in query_embedding], k],
        ).fetchall()
    finally:
        con.close()

    return [
        {"source_path": r[0], "chunk_index": r[1], "chunk_text": r[2], "similarity": r[3]}
        for r in result
    ]


if __name__ == "__main__":
    from src.config import CHUNK_SIZES

    for size in CHUNK_SIZES:
        n = build_index(size)
        print(f"chunk_size={size}: indexed {n} chunks -> {db_path(size)}")
