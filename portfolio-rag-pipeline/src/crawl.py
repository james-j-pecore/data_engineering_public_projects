"""Finds and reads every README.md in the repo, tagged with its path relative to the repo root.

That relative path is what "source" means everywhere else in this project — it's what a
retrieved chunk cites, and it's what eval/gold_qa.yaml's expected_source field points at.
"""

import os

from src.config import EXCLUDE_DIR_NAMES, EXCLUDE_DIR_PREFIXES, REPO_ROOT


def _is_excluded(dir_name: str) -> bool:
    return dir_name in EXCLUDE_DIR_NAMES or dir_name.startswith(EXCLUDE_DIR_PREFIXES)


def find_readmes(repo_root=REPO_ROOT) -> list[str]:
    """Relative (POSIX-style) paths to every README.md under repo_root, in sorted order."""
    matches = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if not _is_excluded(d)]
        if "README.md" in filenames:
            full_path = os.path.join(dirpath, "README.md")
            rel_path = os.path.relpath(full_path, repo_root)
            matches.append(rel_path.replace(os.sep, "/"))
    return sorted(matches)


def read_documents(repo_root=REPO_ROOT) -> list[dict]:
    """[{"source_path": "...", "text": "..."}, ...] for every README.md under repo_root."""
    documents = []
    for rel_path in find_readmes(repo_root):
        full_path = os.path.join(repo_root, rel_path)
        with open(full_path, "r", encoding="utf-8") as f:
            text = f.read()
        if text.strip():
            documents.append({"source_path": rel_path, "text": text})
    return documents


if __name__ == "__main__":
    docs = read_documents()
    print(f"Found {len(docs)} README.md files under {REPO_ROOT}:")
    for doc in docs:
        print(f"  {doc['source_path']}  ({len(doc['text'])} chars)")
