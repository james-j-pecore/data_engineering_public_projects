"""Scoring functions for the eval harness — see ../README.md "The evaluation harness"."""


def recall_at_k(retrieved_sources: list[str], expected_source: str) -> float:
    """1.0 if expected_source appears anywhere among the retrieved chunks' sources, else 0.0."""
    return 1.0 if expected_source in retrieved_sources else 0.0


def precision_at_k(retrieved_sources: list[str], expected_source: str) -> float:
    """Fraction of the retrieved chunks whose source is expected_source."""
    if not retrieved_sources:
        return 0.0
    hits = sum(1 for s in retrieved_sources if s == expected_source)
    return hits / len(retrieved_sources)


def answer_correctness(answer: str, expected_keywords: list[str]) -> float:
    """Fraction of expected_keywords found as case-insensitive substrings of answer."""
    if not expected_keywords:
        return 1.0
    answer_lower = answer.lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return hits / len(expected_keywords)
