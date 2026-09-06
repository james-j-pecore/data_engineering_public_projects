"""Builds a grounded prompt from retrieved chunks and calls Claude to generate an answer.

The only networked call in this pipeline — see ../README.md "Querying: retrieval, then
generation" for why the prompt is built this way.
"""

import os

from src.config import GENERATION_MODEL

SYSTEM_PROMPT = (
    "You are answering questions about a data engineering portfolio repository, using only "
    "the retrieved documentation excerpts provided in the user message. Answer only from that "
    "context — if it doesn't contain the answer, say so explicitly rather than guessing or "
    "relying on outside knowledge. Cite which source file(s) your answer came from, using the "
    "exact source_path shown for each excerpt."
)


def build_prompt(question: str, retrieved_chunks: list[dict]) -> str:
    blocks = [
        f"[{i}] source_path: {c['source_path']}\n{c['chunk_text']}"
        for i, c in enumerate(retrieved_chunks, start=1)
    ]
    context = "\n\n---\n\n".join(blocks)
    return f"Context:\n\n{context}\n\n---\n\nQuestion: {question}"


_client = None


def _get_client():
    """An anthropic.Anthropic client, with the workspace header attached if the key needs one.

    Some API keys (e.g. org-level keys not scoped to a single workspace) require an explicit
    anthropic-workspace-id header on every request — see ../README.md and .env.example.
    """
    global _client
    if _client is None:
        import anthropic

        workspace_id = os.environ.get("ANTHROPIC_WORKSPACE_ID")
        default_headers = {"anthropic-workspace-id": workspace_id} if workspace_id else None
        _client = anthropic.Anthropic(default_headers=default_headers)
    return _client


def generate_answer(question: str, retrieved_chunks: list[dict], model: str = GENERATION_MODEL) -> str:
    if not retrieved_chunks:
        return "No relevant context was retrieved for this question."

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and fill it in, or "
            "export it directly — see the Setup section in README.md."
        )

    client = _get_client()
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt(question, retrieved_chunks)}],
    )
    # response.content can include non-text blocks (e.g. ThinkingBlock) before the answer text,
    # so find the text block rather than assuming it's content[0].
    text_blocks = [block.text for block in response.content if block.type == "text"]
    return "".join(text_blocks)


if __name__ == "__main__":
    from src.config import DEFAULT_CHUNK_SIZE, DEFAULT_K
    from src.embed import embed_query
    from src.index import query_index

    question = "Why are dbt staging models materialized as views but marts as tables?"
    chunks = query_index(DEFAULT_CHUNK_SIZE, embed_query(question), DEFAULT_K)
    print(generate_answer(question, chunks))
