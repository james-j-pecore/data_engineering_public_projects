"""Chat interface: question in, answer + retrieved sources out.

Reads directly from whichever DuckDB index(es) src/index.py has already built — run
`python -m src.index` first if data/*.duckdb doesn't exist yet.
"""

import streamlit as st

from src.ask import ask
from src.config import CHUNK_SIZES, DEFAULT_CHUNK_SIZE, DEFAULT_K, K_VALUES

st.set_page_config(page_title="Portfolio RAG", page_icon="🔍")

st.title("Ask this portfolio a question")
st.caption(
    "Retrieval-augmented Q&A over every README in this repo — see this project's own README.md "
    "for how the retrieval + generation pipeline is built."
)

with st.sidebar:
    st.header("Retrieval settings")
    chunk_size = st.selectbox(
        "Chunk size (characters)", CHUNK_SIZES, index=CHUNK_SIZES.index(DEFAULT_CHUNK_SIZE)
    )
    k = st.selectbox("k (chunks retrieved)", K_VALUES, index=K_VALUES.index(DEFAULT_K))
    st.caption(
        "Defaults come from eval/run_eval.py's best precision@k combination — "
        "see results/eval_results.csv."
    )

question = st.text_input(
    "Question", placeholder="Why are dbt staging models materialized as views but marts as tables?"
)

if st.button("Ask", type="primary") and question:
    with st.spinner("Retrieving and generating..."):
        try:
            result = ask(question, chunk_size=chunk_size, k=k)
        except FileNotFoundError as e:
            st.error(f"{e}\n\nRun `python -m src.index` first to build the vector store(s).")
        except RuntimeError as e:
            st.error(str(e))
        else:
            st.markdown("### Answer")
            st.write(result["answer"])

            st.markdown("### Sources")
            for c in result["sources"]:
                with st.expander(f"{c['source_path']}  ·  similarity {c['similarity']:.3f}"):
                    st.text(c["chunk_text"])
