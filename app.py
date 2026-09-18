import streamlit as st

from src.core import EVALUATION_SET, PIPELINES, benchmark, evaluate, run_pipeline, summary


st.set_page_config(page_title="Agentic GraphRAG Lab", page_icon="TG", layout="wide")
st.title("Agentic GraphRAG Lab")
st.caption("Round 1 benchmark console | local demo corpus")

question = st.text_input("Investigation question", "Who launched Atlas and which group did Maya Chen later join?")
if st.button("Run comparison", type="primary"):
    results = [run_pipeline(question, pipeline) for pipeline in PIPELINES]
    columns = st.columns(3)
    for column, result in zip(columns, results):
        with column:
            st.subheader(result["pipeline"])
            st.metric("Estimated tokens", result["tokens"])
            st.metric("Investigation steps", result["steps"])
            st.write(result["answer"])
            st.caption("Methods: " + " -> ".join(result["methods"]))
            with st.expander("Evidence"):
                for item in result["evidence"]:
                    st.write("- " + item)
            with st.expander("Agent trace"):
                st.json(result["trace"])

st.divider()
st.subheader("Starter benchmark")
if st.button("Run starter benchmark"):
    questions = [item["question"] for item in EVALUATION_SET]
    expected = {item["question"]: item["expected"] for item in EVALUATION_SET}
    rows = evaluate(benchmark(questions), expected)
    st.subheader("Pipeline summary")
    st.dataframe(summary(rows), use_container_width=True, hide_index=True)
    st.dataframe([
        {"question": row["question"], "pipeline": row["pipeline"], "correct": row["correct"], "grounded": row["grounded"], "tokens": row["tokens"], "answer": row["answer"]}
        for row in rows
    ], use_container_width=True, hide_index=True)
