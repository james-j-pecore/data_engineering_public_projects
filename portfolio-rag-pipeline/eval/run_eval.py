"""Sweeps chunk_size x k against the gold set and writes results/eval_results.csv.

Indexing depends only on chunk_size (see ../README.md), so this builds len(CHUNK_SIZES)
indexes total. Query embeddings don't depend on chunk_size or k either, so each gold
question is embedded once and retrieved at the largest k once per chunk_size — every
smaller k is just a prefix of that same retrieval, not a separate vector-store query.

Answer-correctness scoring calls the Claude API (via src.generate) and is skipped, with a
warning, if ANTHROPIC_API_KEY isn't set — retrieval metrics (recall/precision@k) never
need it, so the sweep is still fully runnable without a key.
"""

import os

import pandas as pd
import yaml

from eval.metrics import answer_correctness, precision_at_k, recall_at_k
from src.config import CHUNK_SIZES, GOLD_QA_PATH, K_VALUES, RESULTS_CSV_PATH, RESULTS_DIR
from src.crawl import read_documents
from src.embed import embed_query
from src.generate import generate_answer
from src.index import build_index, query_index


def load_gold_qa() -> list[dict]:
    with open(GOLD_QA_PATH) as f:
        return yaml.safe_load(f)


def run_sweep() -> pd.DataFrame:
    gold = load_gold_qa()
    documents = read_documents()
    max_k = max(K_VALUES)

    can_generate = bool(os.environ.get("ANTHROPIC_API_KEY"))
    if not can_generate:
        print("ANTHROPIC_API_KEY not set — scoring recall/precision@k only, skipping answer_correctness.\n")

    question_embeddings = {item["question"]: embed_query(item["question"]) for item in gold}

    rows = []
    for chunk_size in CHUNK_SIZES:
        n_chunks = build_index(chunk_size, documents=documents)
        print(f"chunk_size={chunk_size}: indexed {n_chunks} chunks")

        retrieved_by_question = {
            item["question"]: query_index(chunk_size, question_embeddings[item["question"]], max_k)
            for item in gold
        }

        for k in K_VALUES:
            recalls, precisions, corrects = [], [], []
            for item in gold:
                retrieved = retrieved_by_question[item["question"]][:k]
                sources = [r["source_path"] for r in retrieved]

                recalls.append(recall_at_k(sources, item["expected_source"]))
                precisions.append(precision_at_k(sources, item["expected_source"]))

                if can_generate:
                    answer = generate_answer(item["question"], retrieved)
                    corrects.append(answer_correctness(answer, item["expected_keywords"]))

            row = {
                "chunk_size": chunk_size,
                "k": k,
                "recall_at_k": sum(recalls) / len(recalls),
                "precision_at_k": sum(precisions) / len(precisions),
                "answer_correctness": (sum(corrects) / len(corrects)) if corrects else None,
            }
            rows.append(row)
            print(f"  k={k}: recall={row['recall_at_k']:.3f}  precision={row['precision_at_k']:.3f}  "
                  f"correctness={row['answer_correctness']}")

    df = pd.DataFrame(rows)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS_CSV_PATH, index=False)
    print(f"\nWrote {RESULTS_CSV_PATH}")
    return df


if __name__ == "__main__":
    run_sweep()
