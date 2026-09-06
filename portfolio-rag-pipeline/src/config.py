"""Shared paths and tunable parameters for the portfolio RAG pipeline.

See ../README.md ("How this RAG pipeline works") for why these specific values were chosen.
"""

from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PROJECT_ROOT.parent

load_dotenv(PROJECT_ROOT / ".env")

DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
EVAL_DIR = PROJECT_ROOT / "eval"

GOLD_QA_PATH = EVAL_DIR / "gold_qa.yaml"
RESULTS_CSV_PATH = RESULTS_DIR / "eval_results.csv"

# Directories to skip while crawling for README.md files — vendored/generated content,
# not this repo's own documentation.
EXCLUDE_DIR_NAMES = {
    ".venv",
    "venv",
    ".git",
    "__pycache__",
    "node_modules",
    "dbt_packages",
    "target",
    ".ipynb_checkpoints",
}
EXCLUDE_DIR_PREFIXES = (".tmp_dagster_home",)

# Embeddings: local, free, no API key. Must stay the same model at index time and query time —
# embeddings from two different models aren't comparable.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# Generation: the only networked call in this pipeline.
GENERATION_MODEL = "claude-sonnet-5"

# The eval sweep. Indexing depends only on chunk_size (k is query-time only), so this is
# len(CHUNK_SIZES) index builds x len(K_VALUES) retrieval evaluations per index.
CHUNK_SIZES = [300, 600, 1200]
CHUNK_OVERLAP_RATIO = 0.15
K_VALUES = [2, 4, 6]

# Used by src/ask.py and the Streamlit app. Picked from eval/run_eval.py's full sweep, including
# live answer_correctness — see the "Evaluation results" table in ../README.md. Notably NOT the
# combo with the best precision@k (that was chunk_size=1200, k=2): once answer_correctness was
# actually scored, chunk_size=600, k=4 won on correctness (0.962 vs. 0.827) despite lower precision.
DEFAULT_CHUNK_SIZE = 600
DEFAULT_K = 4


def db_path(chunk_size: int) -> Path:
    """Path to the DuckDB file holding the index built at this chunk size."""
    return DATA_DIR / f"portfolio_rag_{chunk_size}.duckdb"
