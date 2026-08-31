# Retrieval-Augmented Generation (RAG)

## Overview

RAG is a **system pattern**, not a single trainable model — it combines a **retrieval** step (finding relevant documents from an external knowledge source) with a **generation** step (an [LLM](../17.large-language-models/README.md) producing an answer conditioned on those retrieved documents), so the model's output is grounded in specific, inspectable source text rather than relying purely on whatever it memorized during pretraining.

This is the entry in this index that's least about a new learning algorithm and most about **engineering**: everything the retrieval half needs (embeddings, similarity search) reuses ideas already covered elsewhere in this index — RAG is really about how those pieces are wired together into a pipeline.

---

## Intuition

An LLM's knowledge is frozen at its training cutoff, encoded implicitly across billions of weights, with no citation trail and no way to add new information without retraining (see [LLMs: Limitations](../17.large-language-models/README.md#limitations)). If a question depends on a private document, a fast-changing fact, or something outside the model's training data entirely, the model either can't answer it or — worse — confidently hallucinates a plausible-sounding wrong answer.

RAG sidesteps this by not asking the model to *remember* the answer at all. Instead: search a document collection for whatever's actually relevant to the question, hand the model those specific passages alongside the question, and ask it to answer **using that provided context**. This turns "does the model happen to know this?" into "can the model read and reason over text it's given?" — a much more reliable capability, and one that comes with a built-in audit trail (which documents were retrieved and used).

---

## Mathematical formulation

### The pipeline

**Indexing (done once, ahead of time):**

1. Split source documents into **chunks** (paragraphs or fixed-size windows — small enough to be specific, large enough to retain context).
2. Convert each chunk into an **embedding vector** using an embedding model (conceptually similar to the token embeddings inside an LLM, see [LLMs: Intuition](../17.large-language-models/README.md#intuition), but here one vector represents an entire chunk of text, meant to be compared against other chunks/queries by similarity).
3. Store each (chunk, embedding) pair in a **vector store**, indexed for fast nearest-neighbor lookup.

**Retrieval (done per query):**

4. Embed the incoming query with the same embedding model.
5. Find the $k$ chunks whose embeddings are most similar to the query's embedding — usually via **cosine similarity**:

$$\text{sim}(q, d) = \frac{q \cdot d}{\lVert q \rVert \lVert d \rVert}$$

This is exactly [KNN](../6.k-nearest-neighbors/README.md)'s "find nearest neighbors" idea (see [KNN: Mathematical formulation](../6.k-nearest-neighbors/README.md#mathematical-formulation)), applied to text embeddings instead of raw feature vectors, with cosine similarity in place of Euclidean distance (cosine is preferred here because it measures *directional* similarity independent of vector magnitude, which tends to matter more for embeddings than raw distance does).

**Generation:**

6. Construct a prompt that includes the retrieved chunks as context, plus the original query.
7. Pass that prompt to an LLM, which generates an answer conditioned on the provided context rather than (only) its parametric memory.

### Why this is a system pattern, not a model

Every piece above — embedding, nearest-neighbor search, an LLM's forward pass — is itself something with its own architecture and training process; RAG doesn't introduce new model math so much as an **architecture for combining existing pieces**, which is why the "hyperparameters" below are mostly about pipeline design choices rather than a loss function or a model's internal parameters.

---

## Typical hyperparameters

### Chunk size and overlap

How documents are split before embedding. Too large, and a chunk mixes multiple topics, diluting its embedding's specificity; too small, and a chunk may lack enough context to be useful once retrieved. Overlapping consecutive chunks slightly (e.g., 10-20%) reduces the chance that a relevant passage gets awkwardly split across a chunk boundary.

### `k` (number of retrieved chunks)

How many chunks to retrieve per query — the same core trade-off as [KNN's $k$](../6.k-nearest-neighbors/README.md#intuition): too few risks missing relevant context; too many adds noise and consumes more of the LLM's context window (and cost) on possibly-irrelevant text.

### Embedding model choice

Determines what "similar" means in the vector store — a general-purpose text embedding model is a reasonable default, but domain-specific embeddings (e.g., trained on code, or on a specific technical domain) can noticeably improve retrieval relevance for specialized corpora.

### Similarity metric and index type

Cosine similarity (or equivalently, dot product on normalized vectors) is the common default; the underlying index structure (exact search vs. an approximate-nearest-neighbor index like HNSW) is a scalability choice — exact search is fine for small collections, approximate indexes become necessary once a collection reaches millions of chunks.

### Re-ranking

An optional extra step: retrieve a larger initial candidate set cheaply, then use a more expensive (often cross-encoder) model to re-score and re-rank just those candidates before selecting the final top-$k$ — trading some extra latency for meaningfully better retrieval precision.

### Modeling choices that matter more than any single constructor argument

- **Chunking strategy** is usually where retrieval quality is won or lost, more than the choice of embedding model or vector store — a well-chunked corpus with a mediocre embedding model often outperforms a poorly-chunked corpus with a great one.
- **Prompt construction** — how retrieved chunks are formatted into the final prompt (with or without source labels/citations, how they're ordered, how the query is framed relative to them) has a real, measurable effect on generation quality.
- Whether retrieval is even the right fix for a given failure mode — RAG addresses "the model doesn't have this information" or "the information changed since training"; it does not fix a model's general reasoning limitations, which no amount of good context resolves.

---

## Advantages

**Grounds generation in verifiable, inspectable source text** — retrieved chunks can be shown to the user alongside the answer, giving a citation trail that a purely parametric model's answer never has.

**Adds new/private/fast-changing knowledge without retraining the model** — updating the knowledge source means re-indexing documents, not fine-tuning an LLM, which is dramatically cheaper and faster.

**Reduces (though doesn't eliminate) hallucination** on questions the retrieved context actually covers, by giving the model something concrete to read and summarize rather than requiring it to generate a fact purely from parametric memory.

**Reuses off-the-shelf components** — a pretrained embedding model, an existing vector database, and an existing LLM can be combined without training anything from scratch, unlike most other entries in this index.

**Scoped, auditable knowledge base** — access to specific documents can be controlled and updated independently of the model itself, useful for enterprise settings with permissioned or frequently changing data.

---

## Limitations

**Only as good as retrieval** — if the relevant chunk is never retrieved (poor chunking, a query phrased very differently from the source text, an embedding model that doesn't capture the right notion of similarity for the domain), the generation step has nothing correct to work from, no matter how capable the underlying LLM is.

**Doesn't eliminate hallucination** — a model can still misread, misinterpret, or ignore the retrieved context and generate something inconsistent with it, especially if the retrieved chunks are irrelevant, contradictory, or the answer isn't actually present in them.

**Added system complexity** — a full pipeline (chunking, an embedding model, a vector store, retrieval logic, prompt construction, the LLM itself) has considerably more moving parts, and more places to introduce bugs or silent quality regressions, than a single model call.

**Context window and cost trade-offs** — every retrieved chunk included in the prompt consumes context length and (usually) increases per-query cost, so `k` and chunk size are real trade-offs against the practical limits described in [LLMs: Limitations](../17.large-language-models/README.md#limitations).

**No inherent notion of retrieved-passage quality or trustworthiness** — a similarity search returns whatever's *most similar*, not necessarily most *correct* or most *authoritative*, so garbage or outdated content in the knowledge base can be retrieved and confidently presented back just as readily as good content.

**Doesn't help with tasks that aren't fundamentally knowledge-lookup problems** — reasoning, multi-step calculation, or creative tasks aren't improved by retrieving relevant text, since the model's limitation there isn't "doesn't know a fact."

---

## Simple example

Three short "documents," each represented (for illustration) by a hand-chosen 2-dimensional embedding, and a query:

| Document | Embedding |
|---|---|
| doc1: "Paris is the capital of France." | $(1.0, 0.0)$ |
| doc2: "Photosynthesis converts light into chemical energy." | $(0.0, 1.0)$ |
| doc3: "The capital of France is Paris, on the Seine." | $(0.9, 0.1)$ |

Query: *"What is the capital of France?"* → embedding $(0.8, 0.2)$.

Computing cosine similarity between the query and each document:

$$\text{sim(query, doc1)} = \frac{(0.8)(1.0)+(0.2)(0.0)}{\sqrt{0.8^2+0.2^2}\cdot\sqrt{1.0^2+0.0^2}} = \frac{0.8}{(0.8246)(1.0)} = 0.9701$$

$$\text{sim(query, doc2)} = \frac{(0.8)(0.0)+(0.2)(1.0)}{(0.8246)(1.0)} = \frac{0.2}{0.8246} = 0.2425$$

$$\text{sim(query, doc3)} = \frac{(0.8)(0.9)+(0.2)(0.1)}{(0.8246)(0.9055)} = \frac{0.74}{0.7467} = 0.9910$$

**doc3** wins (0.9910), narrowly ahead of doc1 (0.9701); doc2 is far behind (0.2425), correctly reflecting that it's about an unrelated topic. Retrieval would return doc3 (and doc1, if $k=2$) as context for the generation step — the two chunks that are actually about France's capital, filtering out the unrelated photosynthesis chunk entirely.

### Python example

See [`retrieval_augmented_generation.py`](retrieval_augmented_generation.py) for the runnable version, implemented **from scratch with plain Python** for the retrieval math, plus a sketch of how the generation call would be wired on top of it:

```python
ranked = retrieve(query_embedding, documents, k=2)
for doc_id, score in ranked:
    print(f"{doc_id}: similarity={score:.4f}")

prompt = build_prompt(query="What is the capital of France?", retrieved_chunks=[doc for doc, _ in ranked])
print(prompt)
# answer = llm.generate(prompt)  # the generation step itself — see README's caveat below
```

Expected output (matches the hand computation above):

```text
doc3: similarity=0.9910
doc1: similarity=0.9701
```

**Note on scope:** unlike every other "Simple example" in this index, the *retrieval* half above is fully
hand-verified arithmetic, but the *generation* half genuinely can't be — what an LLM would actually
write from that prompt isn't something to hand-derive or fabricate a plausible-looking transcript
for. The script stops at printing the constructed prompt for exactly that reason.

---

## Resources

- [Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (2020)](https://arxiv.org/abs/2005.11401) — the paper that introduced the RAG name and architecture.
- [Anthropic's documentation on building with embeddings and retrieval](https://docs.claude.com/) — practical guidance for wiring an embedding-based retrieval step into an LLM application.
- [Pinecone, "What is Retrieval-Augmented Generation?"](https://www.pinecone.io/learn/retrieval-augmented-generation/) — a practically-oriented walkthrough of chunking, embedding, and vector-store trade-offs.
- [K-Nearest Neighbors](../6.k-nearest-neighbors/README.md) in this index — the same "find the most similar stored items" idea RAG's retrieval step is built on, just applied to text embeddings.

### Core fact to retain

> RAG doesn't teach a model anything new — it finds the most relevant text via embedding similarity search (the same idea as KNN) and hands it to an LLM as context, trading reliance on the model's frozen, unauditable parametric memory for grounding in specific, inspectable, and independently updatable source documents.
