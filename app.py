import streamlit as st

from src.core import EVALUATION_SET, PIPELINES, benchmark, evaluate, run_pipeline, summary


GRAPH_HTML = """
<div class="scene-shell">
    <div class="scene-label"><span class="pulse"></span> live evidence map</div>
    <div class="scene-canvas"></div>
</div>
"""

GRAPH_CSS = """
:host { display: block; }
.scene-shell {
    height: 310px;
    overflow: hidden;
    position: relative;
    border-radius: 18px;
    background: radial-gradient(circle at 50% 45%, #164e63 0%, #102f42 42%, #081a29 100%);
    box-shadow: inset 0 0 0 1px rgba(160, 240, 221, .2), 0 20px 40px rgba(8, 26, 41, .16);
}
.scene-canvas { height: 100%; width: 100%; }
.scene-label {
    color: #d6fff2;
    font: 600 12px/1.2 sans-serif;
    letter-spacing: .08em;
    position: absolute;
    left: 18px;
    top: 16px;
    text-transform: uppercase;
    z-index: 2;
}
.pulse {
    background: #72f2c2;
    border-radius: 50%;
    box-shadow: 0 0 0 5px rgba(114, 242, 194, .15), 0 0 18px #72f2c2;
    display: inline-block;
    height: 7px;
    margin-right: 8px;
    vertical-align: 1px;
    width: 7px;
}
"""

GRAPH_JS = """
export default async function(component) {
    const { parentElement, data } = component
    const host = parentElement.querySelector('.scene-canvas')
    if (!host || host.dataset.ready === 'true') return
    host.dataset.ready = 'true'

    const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.171.0/build/three.module.js')
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100)
    camera.position.set(0, 0.2, 8.5)
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setClearColor(0x000000, 0)
    host.appendChild(renderer.domElement)

    const group = new THREE.Group()
    scene.add(group)
    const points = [
        { name: 'Atlas', x: 0, y: 0.2, z: 0, color: 0x72f2c2, size: 0.28 },
        { name: 'Maya', x: -2.1, y: 1.05, z: -0.2, color: 0x67d4ff, size: 0.16 },
        { name: 'Ravi', x: 2.0, y: 1.05, z: -0.4, color: 0x67d4ff, size: 0.16 },
        { name: 'Trust', x: -1.55, y: -1.25, z: 0.1, color: 0xffc470, size: 0.18 },
        { name: 'Vector', x: 1.75, y: -1.15, z: -0.25, color: 0xffc470, size: 0.18 },
    ]
    const meshes = []
    for (const point of points) {
        const mesh = new THREE.Mesh(
            new THREE.SphereGeometry(point.size, 24, 24),
            new THREE.MeshStandardMaterial({ color: point.color, emissive: point.color, emissiveIntensity: 0.22, roughness: 0.3, metalness: 0.2 })
        )
        mesh.position.set(point.x, point.y, point.z)
        group.add(mesh)
        meshes.push(mesh)
    }
    const links = [[0, 1], [0, 2], [1, 3], [2, 4], [0, 4]]
    for (const [from, to] of links) {
        const geometry = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(points[from].x, points[from].y, points[from].z),
            new THREE.Vector3(points[to].x, points[to].y, points[to].z),
        ])
        group.add(new THREE.Line(geometry, new THREE.LineBasicMaterial({ color: 0x72f2c2, transparent: true, opacity: 0.42 })))
    }
    group.add(new THREE.AmbientLight(0x9eead8, 1.8))
    const keyLight = new THREE.PointLight(0x67d4ff, 18, 12)
    keyLight.position.set(2, 3, 4)
    scene.add(keyLight)

    const resize = () => {
        const width = host.clientWidth || 600
        const height = host.clientHeight || 310
        renderer.setSize(width, height, false)
        camera.aspect = width / height
        camera.updateProjectionMatrix()
    }
    const observer = new ResizeObserver(resize)
    observer.observe(host)
    resize()
    let frame = 0
    const animate = () => {
        frame = requestAnimationFrame(animate)
        group.rotation.y += 0.0025
        group.rotation.x = Math.sin(Date.now() * 0.00035) * 0.06
        meshes.forEach((mesh, index) => { mesh.scale.setScalar(1 + Math.sin(Date.now() * 0.002 + index) * 0.06) })
        renderer.render(scene, camera)
    }
    animate()
    return () => { cancelAnimationFrame(frame); observer.disconnect(); renderer.dispose() }
}
"""

EVIDENCE_SCENE = st.components.v2.component(
        "evidence_constellation",
        html=GRAPH_HTML,
        css=GRAPH_CSS,
        js=GRAPH_JS,
)


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

scene_data = {"question": "ready", "steps": 0}
if st.session_state.get("results"):
    scene_data = {
        "question": st.session_state["results"][0]["question"],
        "steps": next(result for result in st.session_state["results"] if result["pipeline"] == "Agentic GraphRAG")["steps"],
    }
EVIDENCE_SCENE(data=scene_data, width="stretch", height=310)

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
