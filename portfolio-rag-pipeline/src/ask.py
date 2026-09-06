"""End-to-end: question -> retrieve -> generate. Importable (ask()) and runnable as a CLI."""

import sys

from src.config import DEFAULT_CHUNK_SIZE, DEFAULT_K
from src.embed import embed_query
from src.generate import generate_answer
from src.index import query_index


def ask(question: str, chunk_size: int = DEFAULT_CHUNK_SIZE, k: int = DEFAULT_K) -> dict:
    chunks = query_index(chunk_size, embed_query(question), k)
    answer = generate_answer(question, chunks)
    return {"question": question, "answer": answer, "sources": chunks}


def _print_result(result: dict) -> None:
    print(result["answer"])
    print()
    print("Sources:")
    for c in result["sources"]:
        print(f"  {c['source_path']} (similarity: {c['similarity']:.3f})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python -m src.ask "your question here"')
        sys.exit(1)
    _print_result(ask(" ".join(sys.argv[1:])))
