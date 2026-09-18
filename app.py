import streamlit as st

from src.core import EVALUATION_SET, PIPELINES, benchmark, evaluate, run_pipeline, summary


st.set_page_config(
    page_title="Agentic GraphRAG Lab",
    page_icon=":material/hub:",
    layout="wide",
    initial_sidebar_state="expanded",
)


with st.sidebar:
    st.markdown("## :material/hub: GraphRAG lab")
    st.caption("Round 1 investigation console")
    st.badge("Local demo corpus", icon=":material/database:", color="blue")
    st.markdown("### System status")
    st.success("Pipelines ready", icon=":material/check_circle:")
    st.metric("Evidence sources", "5")
    st.metric("Graph relationships", "4")
    st.markdown("### MCP tools")
    st.caption("search_documents")
    st.caption("traverse_graph")
    st.caption("investigate")
    st.markdown("---")
    st.caption("Replace the demo corpus with the official benchmark dataset before submission.")


st.title("Investigate connected evidence", icon=":material/search_insights:")
st.caption("Compare how much reasoning each retrieval strategy needs to answer the same question.")

with st.container(border=True):
    st.markdown("**Ask the graph**")
    with st.form("investigation_form"):
        question = st.text_input(
            "Investigation question",
            "Who launched Atlas and which group did Maya Chen later join?",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Run investigation", type="primary", icon=":material/play_arrow:")

if submitted:
    st.session_state["results"] = [run_pipeline(question, pipeline) for pipeline in PIPELINES]

results = st.session_state.get("results")
if results:
    total_tokens = sum(result["tokens"] for result in results)
    agentic_result = next(result for result in results if result["pipeline"] == "Agentic GraphRAG")
    with st.container(horizontal=True):
        st.metric("Strategies compared", len(results), border=True)
        st.metric("Agentic steps", agentic_result["steps"], border=True)
        st.metric("Total estimated tokens", total_tokens, border=True)
        st.metric("Evidence items", len(agentic_result["evidence"]), border=True)

    st.header("Investigation results", icon=":material/compare_arrows:")
    result_columns = st.columns(3, border=True)
    for column, result in zip(result_columns, results):
        with column:
            st.subheader(result["pipeline"])
            st.metric("Estimated tokens", result["tokens"])
            st.caption(f"{result['steps']} investigation step(s) · " + " → ".join(result["methods"]))
            st.markdown("**Answer**")
            st.write(result["answer"])
            with st.expander("Evidence", icon=":material/format_quote:"):
                for item in result["evidence"]:
                    st.write(f"- {item}")
            with st.expander("Agent trace", icon=":material/account_tree:"):
                st.json(result["trace"])

st.header("Benchmark workspace", icon=":material/analytics:")
st.caption("Run the local evaluation set and inspect accuracy, grounding, cost, and trace depth.")
if st.button("Run benchmark", icon=":material/rocket_launch:"):
    questions = [item["question"] for item in EVALUATION_SET]
    expected = {item["question"]: item["expected"] for item in EVALUATION_SET}
    rows = evaluate(benchmark(questions), expected)
    st.session_state["benchmark_rows"] = rows

benchmark_rows = st.session_state.get("benchmark_rows")
if benchmark_rows:
    summary_rows = summary(benchmark_rows)
    summary_tab, detail_tab = st.tabs(["Pipeline summary", "Question detail"])
    with summary_tab:
        st.dataframe(summary_rows, width="stretch", hide_index=True)
    with detail_tab:
        st.dataframe([
            {
                "question": row["question"],
                "pipeline": row["pipeline"],
                "correct": row["correct"],
                "grounded": row["grounded"],
                "tokens": row["tokens"],
                "steps": row["steps"],
                "answer": row["answer"],
            }
            for row in benchmark_rows
        ], width="stretch", hide_index=True)
