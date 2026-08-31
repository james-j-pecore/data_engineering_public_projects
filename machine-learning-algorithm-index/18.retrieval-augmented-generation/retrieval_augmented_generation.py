"""
Retrieval-augmented generation — the retrieval half, from scratch.

Companion code for README.md's "Simple example" section: three toy
documents with hand-chosen 2-D embeddings, ranked by cosine similarity to a
query embedding. The similarity scores were hand-computed in README.md
before this script was written.

Unlike every other script in this index, this one deliberately stops before
the generation step: what an LLM would actually write from the constructed
prompt isn't something to hand-derive or fabricate a transcript for (see
README.md's "Note on scope"). Wiring in a real `llm.generate(prompt)` call
is left as the one line the comment marks below.

Run:
    python retrieval_augmented_generation.py
"""

import math


def cosine_similarity(a: tuple, b: tuple) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b)


def retrieve(query_embedding: tuple, documents: dict, k: int = 2) -> list:
    """Return the top-k (doc_id, similarity) pairs, most similar first."""
    scored = [(doc_id, cosine_similarity(query_embedding, emb))
              for doc_id, (_, emb) in documents.items()]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:k]


def build_prompt(query: str, retrieved_chunks: list) -> str:
    """Construct a simple context-then-question prompt from retrieved chunk text."""
    context = "\n".join(f"- {chunk}" for chunk in retrieved_chunks)
    return f"Context:\n{context}\n\nQuestion: {query}\nAnswer using only the context above."


if __name__ == "__main__":
    # doc_id -> (text, embedding)
    documents = {
        "doc1": ("Paris is the capital of France.", (1.0, 0.0)),
        "doc2": ("Photosynthesis converts light into chemical energy.", (0.0, 1.0)),
        "doc3": ("The capital of France is Paris, on the Seine.", (0.9, 0.1)),
    }
    query = "What is the capital of France?"
    query_embedding = (0.8, 0.2)

    ranked = retrieve(query_embedding, documents, k=2)
    for doc_id, score in ranked:
        print(f"{doc_id}: similarity={score:.4f}")

    retrieved_text = [documents[doc_id][0] for doc_id, _ in ranked]
    prompt = build_prompt(query, retrieved_text)
    print("\n--- constructed prompt ---")
    print(prompt)

    # The generation step itself is intentionally not implemented here — see
    # README.md's "Note on scope". In a real system this would be:
    #     answer = llm.generate(prompt)
