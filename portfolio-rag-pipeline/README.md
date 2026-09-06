# Portfolio RAG Pipeline

A working Retrieval-Augmented Generation system built over this repository's own documentation —
every README across every project — plus an evaluation harness that empirically measures how
chunk size and retrieval depth (`k`) actually affect retrieval and answer quality on that corpus.

**Theme:** don't just build a RAG demo — measure it. The theoretical write-up in
[`machine-learning-algorithm-index/18.retrieval-augmented-generation`](../machine-learning-algorithm-index/18.retrieval-augmented-generation/README.md)
claims chunk size and `k` are the hyperparameters that matter most; this project is that claim,
tested against real data instead of asserted.

Everything below is real and run end-to-end, including live Claude generation: 40 READMEs indexed,
26 hand-written gold questions, a full 3×3 chunk-size/`k` sweep (234 live Claude calls), and a
working Streamlit chat interface over the result. The one thing not exercised in a real browser is
the Streamlit UI itself — it's been verified to serve without server-side errors, not click-tested.

---

## Architecture

**Indexing** (run once, rebuilt whenever the corpus or chunk-size config changes):

```
repo root
     │  src/crawl.py    walks every project directory, reads every README.md,
     │                   tags each with its relative path as source_path
     ▼
raw documents (path, full markdown text)
     │  src/chunk.py     splits each document into overlapping chunks
     ▼
chunks (source_path, chunk_index, chunk_text)
     │  src/embed.py     sentence-transformers, local, no API call
     ▼
chunks + embedding vectors
     │  src/index.py     writes to DuckDB (vss extension) — one table, one file per chunk-size config
     ▼
data/portfolio_rag_{chunk_size}.duckdb
```

**Querying** (run per question, either from `src/ask.py` or the Streamlit app):

```
question (plain text)
     │  src/embed.py     same embedding model as indexing — must match, or similarity is meaningless
     ▼
question embedding
     │  src/index.py     cosine similarity against every stored chunk, return top k
     ▼
top-k chunks (source_path, chunk_text, similarity score)
     │  src/generate.py  builds a prompt: question + retrieved chunks, instructs Claude to answer
     │                   only from the provided context and to cite which source_path it used
     ▼
Claude API (anthropic SDK)
     ▼
answer + the sources it was grounded in
```

---

## Tech stack

Python · `sentence-transformers` (local embeddings) · DuckDB + `vss` extension (vector store) ·
Anthropic API (`anthropic` SDK, generation) · Streamlit · PyYAML (gold Q&A set) · pandas (eval
results)

Only one API key is needed (`ANTHROPIC_API_KEY`) — embeddings never leave the machine.

---

## Project structure

```
portfolio-rag-pipeline/
├── src/
│   ├── config.py       repo root path, embedding model name, chunk-size/k sweep values
│   ├── crawl.py         find + read every README.md in the repo
│   ├── chunk.py         split a document into overlapping chunks
│   ├── embed.py         sentence-transformers wrapper (shared by indexing and querying)
│   ├── index.py         build/query the DuckDB + vss vector store
│   ├── generate.py      Claude API call: prompt construction + answer
│   └── ask.py           end-to-end: question -> retrieve -> generate (importable + CLI)
├── eval/
│   ├── gold_qa.yaml      hand-written question -> expected source + expected keywords
│   ├── metrics.py        precision@k, recall@k, answer-correctness scoring
│   └── run_eval.py       sweeps chunk_size x k, writes results/eval_results.csv
├── analysis/
│   └── streamlit_app.py  chat interface: question in, answer + sources out
├── data/                  gitignored — one .duckdb file per chunk_size config, built by src/index.py
└── results/
    └── eval_results.csv   checked in — feeds the "Evaluation results" table below
```

---

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY
```

No Spotify-style OAuth dance here — the entire corpus is already sitting in this repo. The only
external call at runtime is to the Claude API, and only for the generation step. If your key isn't
scoped to a single workspace, the API returns a 400 telling you so — add `ANTHROPIC_WORKSPACE_ID`
to `.env` too in that case (see `.env.example` for where to find it).

## Running the pipeline

```bash
python -m src.index          # crawl -> chunk -> embed -> write vector store(s)
python -m src.ask "why are staging models materialized as views but marts as tables?"
python -m eval.run_eval      # sweep chunk_size x k against the gold set, write results/eval_results.csv
streamlit run analysis/streamlit_app.py
```

---

## How this RAG pipeline works

### Indexing: turning READMEs into searchable chunks

`src/crawl.py` walks the repo and reads every `README.md` it finds — the top-level README, each of
the ~19 `machine-learning-algorithm-index` entries, each of the 15 `cloud-platform-tool-index`
entries, and the three pipeline projects' READMEs (including this one, once it's indexed alongside
the rest). Each document is tagged with its path relative to the repo root — that path is what
"source" means everywhere else in this project: it's what a retrieved chunk cites, and it's what the
gold Q&A set's `expected_source` field points at.

`src/chunk.py` then splits each document into overlapping chunks of a configurable **character**
length (not tokens — avoids pulling in a tokenizer dependency just for chunk boundaries, and
character count is close enough to token count for splitting purposes at this corpus's scale). A
chunk boundary that falls mid-sentence is an accepted trade-off for a fixed overlap between
consecutive chunks (about 15% of chunk size), which reduces the chance that a relevant passage gets
split awkwardly across two chunks with neither half retrievable on its own.

`src/embed.py` converts each chunk's text into a fixed-length vector using a local
`sentence-transformers` model (`all-MiniLM-L6-v2` — small, fast, 384-dimensional, no GPU required,
no API key). This is the same model used at query time; embeddings from two different models aren't
comparable, so this wrapper is shared code, not two separate implementations that could drift apart.

`src/index.py` writes `(source_path, chunk_index, chunk_text, embedding)` rows into a DuckDB table
using the `vss` extension. **Indexing depends only on chunk size** — `k` never affects what gets
stored, only how many results a query asks for — so one DuckDB file gets built per chunk-size
setting in the sweep, and `k` is purely a query-time parameter evaluated against whichever index is
already built. This is why the sweep in the eval harness (below) only needs 3 index builds instead
of 9.

### Querying: retrieval, then generation

Given a question, `src/ask.py` embeds it with the same `sentence-transformers` model, then
`src/index.py` computes cosine similarity between that one query vector and every stored chunk
vector, returning the top `k`. At this corpus's scale (a few hundred chunks total, not millions),
**brute-force cosine similarity over every row is fast enough** — the `vss` extension's approximate
HNSW index exists for when a linear scan stops being viable, which isn't this project's problem to
solve.

`src/generate.py` then builds a prompt containing the question and the retrieved chunks (each
labeled with its `source_path`), with an explicit instruction to answer only from the provided
context and to name which source(s) the answer came from — the same "ground the model in retrieved
text and make retrieval auditable" pattern described in the
[RAG theory write-up](../machine-learning-algorithm-index/18.retrieval-augmented-generation/README.md#intuition),
here actually wired up to a real LLM call rather than stopping at the constructed prompt the way that
entry's worked example deliberately does.

### The evaluation harness: measuring "good," without grading circularity

The theory write-up asserts that chunk size and `k` are the two hyperparameters that matter most for
retrieval quality. This project tests that claim directly, using a hand-written gold set rather than
an LLM-as-judge — deliberately, so the eval harness isn't using the same model family to generate,
answer, *and* grade its own homework.

**`eval/gold_qa.yaml`** — 26 hand-written entries across 21 of the 40 source documents, each shaped
like:

```yaml
- question: "Why are staging models materialized as views but marts as tables in the Spotify project?"
  expected_source: spotify-dbt-analytics-pipeline/README.md
  expected_keywords:
    - "recompute"
    - "persisted"
```

`expected_source` is the one document that should be retrieved for that question — mostly drawn
from the "key differences" and "why" sections of the READMEs already written, since those are the
sentences a generic keyword search wouldn't reliably surface but semantic embedding similarity
should. `expected_keywords` are short phrases that a correct answer has to contain, pulled from the
actual source text — not model-graded, just checked as case-insensitive substrings.

**`eval/metrics.py`** defines three numbers per `(chunk_size, k)` combination, each averaged across
every gold question:

- **Recall@k** — fraction of questions where at least one of the top-`k` retrieved chunks comes from
  `expected_source`. (1 if found, 0 if not, averaged.)
- **Precision@k** — for each question, `(top-k chunks whose source is expected_source) / k`,
  averaged. Meaningful here specifically because a single document contributes multiple chunks, so
  more than one of the `k` retrieved slots can legitimately belong to the right source.
- **Answer correctness** — for each question, `(expected_keywords found in the generated answer) /
  (total expected_keywords)`, averaged. A deliberately simple, deterministic proxy for "did the
  answer actually contain the right information" — not a semantic judgment call, which is the point.

**`eval/run_eval.py`** sweeps chunk sizes `[300, 600, 1200]` (characters) against retrieval depths
`k = [2, 4, 6]` — building 3 indexes total, then evaluating all 9 `(chunk_size, k)` combinations
against each of those 3 indexes — and writes one row per combination to `results/eval_results.csv`.
Whichever combination scores best becomes the default config `src/ask.py` and the Streamlit app use.

---

## Evaluation results

Run against all 26 gold questions, all 3 chunk sizes, all 3 values of `k` (9 combinations, 3 index
builds, 234 live Claude calls for `answer_correctness`).

| chunk_size | k | Recall@k | Precision@k | Answer correctness |
|---|---|---|---|---|
| 300  | 2 | 1.000 | 0.846 | 0.750 |
| 300  | 4 | 1.000 | 0.817 | 0.808 |
| 300  | 6 | 1.000 | 0.769 | 0.808 |
| 600  | 2 | 1.000 | 0.865 | 0.788 |
| 600  | 4 | 1.000 | 0.846 | **0.962** |
| 600  | 6 | 1.000 | 0.808 | **0.962** |
| 1200 | 2 | 1.000 | **0.923** | 0.827 |
| 1200 | 4 | 1.000 | 0.798 | 0.904 |
| 1200 | 6 | 1.000 | 0.641 | 0.942 |

**Recall@k is 1.0 across every single combination** — for this corpus and this gold set, semantic
similarity search always surfaces the right document somewhere in the top 6, regardless of chunk
size. That's a weaker result than it sounds: the gold questions were written by paraphrasing each
source document's own distinctive language, so this mostly confirms the embedding model can match
close paraphrases — not that retrieval is bulletproof against very differently-phrased questions.

**Precision@k is not monotonic in chunk size.** Larger chunks (1200 chars) win decisively at `k=2`
(0.923 — most of what's retrieved is from the right doc) but fall the furthest by `k=6` (0.641 —
the worst of all nine combinations). The explanation is structural: bigger chunks mean fewer
chunks per document, so a document runs out of genuinely relevant chunks sooner as `k` grows, and
the remaining slots get backfilled from unrelated documents. Smaller chunks (300 chars) are
steadier across `k` (0.846 → 0.769) for the same reason in reverse.

**The best-precision combo is not the best-answer combo — this is the headline result.**
`chunk_size=1200, k=2` had the best precision@k (0.923) of the whole sweep, but its answer
correctness (0.827) is mediocre. `chunk_size=600, k=4` wins on correctness (0.962) despite
noticeably lower precision (0.846). The gap makes sense once you look at what changes: at `k=2`,
Claude sometimes only sees one truly relevant chunk plus one near-miss, which is enough for
retrieval to count as a "hit" but not always enough surrounding context to fully answer the
question; `k=4` at `chunk_size=600` gives Claude more relevant surface area to work with, and the
extra chunks that aren't a precision hit apparently cost less than the extra context helps. A
lower-precision, higher-`k` combination beating a high-precision, low-`k` one is precisely the kind
of result that picking a config by precision@k *alone* would have gotten wrong. That's the
empirical case for why this project measures `answer_correctness` separately rather than
optimizing retrieval metrics in isolation, and it's a real instance of the chunk-size/`k`
interaction the
[RAG theory write-up](../machine-learning-algorithm-index/18.retrieval-augmented-generation/README.md#typical-hyperparameters)
describes in the abstract.

**Current default: `chunk_size=600, k=4`** (see `src/config.py`) — the best `answer_correctness` in
the sweep (tied with `k=6` at the same chunk size, but `k=4` has better precision and costs less
context per query for the same result).

---

## Design decisions & simplifications

These are intentional choices, matching the rest of this portfolio's stated preference for
explaining trade-offs rather than hiding them:

- **Local embeddings, API-based generation** — avoids a second vendor/API key purely for embeddings,
  and keeps the retrieval half fully free and offline; only the generation call costs anything or
  needs network access.
- **Character-based chunking, not token-based** — close enough to token count for splitting purposes
  here, and avoids adding a tokenizer dependency solely to decide where a chunk boundary falls.
- **Brute-force cosine similarity, no HNSW index** — the corpus is a few hundred chunks, not
  millions; an approximate nearest-neighbor index would add complexity this scale doesn't need (see
  the equivalent note on exact-vs-approximate search in
  [`cloud-platform-tool-index/1.object-storage`](../cloud-platform-tool-index/1.object-storage/README.md#key-differences)).
- **Keyword-coverage answer scoring, not LLM-as-judge** — a deliberate rigor choice: it can't detect
  a fluent-but-subtly-wrong answer the way a judge model might, but it also can't be gamed by a judge
  model and generator model sharing the same blind spots.
- **One DuckDB file per chunk-size config, not one file with a config column** — keeps each sweep
  point fully isolated and avoids ever accidentally comparing `k` against the wrong chunk size's
  index.
- **No Dagster** — the interesting engineering here is retrieval quality and evaluation, not pipeline
  orchestration, which the Spotify project already demonstrates.
- **The eval sweep degrades gracefully without an API key** — `eval/run_eval.py` checks for
  `ANTHROPIC_API_KEY` once up front and simply skips `answer_correctness` scoring (leaving it blank
  in the CSV) rather than failing the whole sweep, since recall@k and precision@k never need a live
  LLM call. This is also exactly the state this project's own results were generated in.
- **Query embeddings are computed once per gold question, not once per (chunk_size, k)
  combination** — and each chunk_size's retrieval is done once at the largest `k` in the sweep, with
  every smaller `k` taken as a prefix of that same result rather than a separate vector-store query.
  Chunk size and `k` don't actually require re-embedding or re-querying for every combination in the
  sweep; only re-indexing depends on chunk_size.

Two real bugs surfaced running the full live sweep, worth keeping visible rather than quietly
fixing and forgetting:

- **`generate_answer` extracts the first text block from the response, not `content[0]`** — the
  Messages API response can include non-text content blocks (e.g. a `ThinkingBlock`) ahead of the
  actual answer text, which the initial implementation didn't account for and which surfaced as a
  real `AttributeError` partway through the first live eval sweep. Fixed by filtering
  `response.content` for blocks where `.type == "text"` instead of assuming position 0.
- **The API key needed an explicit `anthropic-workspace-id` header** — an org-level key not scoped
  to one workspace gets a 400 from the Messages API until that header is set. `src/generate.py`
  reads an optional `ANTHROPIC_WORKSPACE_ID` env var for this rather than requiring everyone to
  generate a workspace-scoped key instead.

## Known limitations

- The gold Q&A set is small (26 questions) and hand-written — enough to compare configurations
  meaningfully relative to each other, not enough to make strong absolute claims about
  production-scale retrieval quality.
- `expected_keywords` substring matching will miss a correct answer that's phrased entirely
  differently from the source text's wording — a real false negative this method accepts in exchange
  for not needing a judge model.
- Corpus is this repo's own READMEs only — nothing here demonstrates behavior on a larger or messier
  real-world document collection.
