"""Local sentence-transformers embeddings — shared by indexing and querying.

Must stay the same model for both: embeddings from two different models aren't comparable,
so this wrapper is the one place that decides which model is in use.
"""

import numpy as np

from src.config import EMBEDDING_MODEL

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """texts -> (len(texts), EMBEDDING_DIM) array of unit-normalized vectors."""
    model = _get_model()
    return model.encode(texts, normalize_embeddings=True, show_progress_bar=False)


def embed_query(text: str) -> np.ndarray:
    """A single query string -> a (EMBEDDING_DIM,) unit-normalized vector."""
    return embed_texts([text])[0]


if __name__ == "__main__":
    vecs = embed_texts(["Data warehouses store structured analytical data.", "Cats are mammals."])
    query_vec = embed_query("What is BigQuery used for?")
    sims = vecs @ query_vec
    print(f"embedding shape: {vecs.shape}")
    print(f"similarity to warehouse sentence: {sims[0]:.4f}")
    print(f"similarity to cats sentence:      {sims[1]:.4f}")
