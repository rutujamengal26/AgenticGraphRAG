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


hero_left, hero_right = st.columns([3, 1], vertical_alignment="center")
with hero_left:
    st.title("Investigate connected evidence", icon=":material/search_insights:")
    st.caption("A compact lab for seeing when graph structure and agentic reasoning actually help.")
    st.badge("RAG", color="gray")
    st.badge("GraphRAG", color="blue")
    st.badge("Agentic GraphRAG", color="green")
with hero_right:
    st.metric("Round 1 mode", "Live demo", border=True)

with st.container(border=True):
    st.markdown("**How the investigation works**")
    flow_columns = st.columns(3)
    flow_steps = [
        (":material/search:", "Retrieve", "Find relevant documents or graph relationships."),
        (":material/account_tree:", "Connect", "Join entities across multiple evidence sources."),
        (":material/fact_check:", "Evaluate", "Check evidence quality and stop when it is enough."),
    ]
    for column, (icon, label, description) in zip(flow_columns, flow_steps):
        with column:
            st.markdown(f"### {icon} {label}")
            st.caption(description)

with st.container(border=True):
    st.markdown("**Ask the graph**")
    scenario = st.selectbox(
        "Start with a scenario",
        [item["question"] for item in EVALUATION_SET],
        label_visibility="collapsed",
    )
    with st.form("investigation_form"):
        question = st.text_input(
            "Investigation question",
            scenario,
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
