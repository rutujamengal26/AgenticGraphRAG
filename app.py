import streamlit as st

from src.core import EVALUATION_SET, PIPELINES, benchmark, evaluate, run_pipeline, summary


GRAPH_HTML = """
<div class="scene-shell">
    <div class="scene-label"><span class="pulse"></span> 3D investigation architecture</div>
    <div class="scene-hint">drag to orbit · scroll to zoom</div>
    <div class="scene-canvas"></div>
    <div class="scene-detail">Click a node to inspect the flow.</div>
    <button class="reset-view" type="button">Reset view</button>
</div>
"""

GRAPH_CSS = """
:host { display: block; }
.scene-shell {
    height: 390px;
    overflow: hidden;
    position: relative;
    border-radius: 18px;
    background: radial-gradient(circle at 50% 30%, #b95f55 0%, #633747 32%, #2b2440 68%, #111827 100%);
    box-shadow: inset 0 0 0 1px rgba(160, 240, 221, .2), 0 20px 40px rgba(8, 26, 41, .16);
}
.scene-canvas { height: 100%; width: 100%; }
.scene-hint {
    color: rgba(214, 255, 242, .68);
    font: 500 11px/1.2 sans-serif;
    letter-spacing: .04em;
    position: absolute;
    right: 18px;
    top: 18px;
    z-index: 2;
}
.scene-detail {
    background: rgba(4, 18, 30, .72);
    border: 1px solid rgba(160, 240, 221, .18);
    border-radius: 10px;
    bottom: 14px;
    color: #c9eee4;
    font: 500 12px/1.35 sans-serif;
    left: 18px;
    max-width: 260px;
    padding: 8px 10px;
    position: absolute;
    z-index: 2;
}
.reset-view {
    background: rgba(114, 242, 194, .14);
    border: 1px solid rgba(114, 242, 194, .35);
    border-radius: 8px;
    bottom: 14px;
    color: #d6fff2;
    cursor: pointer;
    font: 600 12px/1.2 sans-serif;
    padding: 8px 10px;
    position: absolute;
    right: 18px;
    z-index: 2;
}
.reset-view:hover { background: rgba(114, 242, 194, .28); }
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
    const detail = parentElement.querySelector('.scene-detail')
    const reset = parentElement.querySelector('.reset-view')
    if (!host || host.dataset.ready === 'true') return
    host.dataset.ready = 'true'

    const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.171.0/build/three.module.js')
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100)
    camera.position.set(0, 0.3, 13.5)
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setClearColor(0x000000, 0)
    host.appendChild(renderer.domElement)

    const group = new THREE.Group()
    scene.add(group)
    const points = [
        { name: 'Question', description: 'The investigation starts with the user question.', x: -4.0, y: 0, z: 0, color: 0x63d9ff, label: '#baf0ff', size: 0.25 },
        { name: 'Orchestrator', description: 'The agent selects the next retrieval action.', x: -1.9, y: 0, z: 0, color: 0xff6b9a, label: '#ffd0df', size: 0.34 },
        { name: 'Vector search', description: 'Find semantically similar document evidence.', x: 0.4, y: 1.35, z: -0.3, color: 0xffd166, label: '#ffe7a3', size: 0.22 },
        { name: 'Graph traversal', description: 'Follow entities and relationships across the graph.', x: 0.4, y: 0, z: 0.2, color: 0xff9f68, label: '#ffd0ad', size: 0.22 },
        { name: 'Document retrieval', description: 'Fetch supporting source passages for citations.', x: 0.4, y: -1.35, z: -0.2, color: 0xf2a7d7, label: '#ffd9f0', size: 0.22 },
        { name: 'Evidence check', description: 'Evaluate coverage, grounding, and information gaps.', x: 2.6, y: 0, z: 0, color: 0xa78bfa, label: '#ddd2ff', size: 0.3 },
        { name: 'Answer', description: 'Return a grounded answer with trace and citations.', x: 3.9, y: 0, z: 0, color: 0xf7f3e8, label: '#fff8e8', size: 0.25 },
    ]
    const meshes = []
    const labels = []
    const makeLabel = (text, color) => {
        const canvas = document.createElement('canvas')
        canvas.width = 640
        canvas.height = 112
        const context = canvas.getContext('2d')
        context.fillStyle = 'rgba(5, 20, 31, .9)'
        context.beginPath()
        context.roundRect(4, 4, 632, 104, 18)
        context.fill()
        context.fillStyle = color
        context.fillRect(4, 4, 8, 104)
        context.font = '700 38px sans-serif'
        context.fillText(text, 28, 68)
        const texture = new THREE.CanvasTexture(canvas)
        const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true }))
        sprite.scale.set(2.25, 0.44, 1)
        return sprite
    }
    for (const point of points) {
        const mesh = new THREE.Mesh(
            new THREE.SphereGeometry(point.size, 24, 24),
            new THREE.MeshStandardMaterial({ color: point.color, emissive: point.color, emissiveIntensity: 0.22, roughness: 0.3, metalness: 0.2 })
        )
        mesh.position.set(point.x, point.y, point.z)
        group.add(mesh)
        meshes.push(mesh)
        const label = makeLabel(point.name, point.label)
        label.position.set(point.x, point.y - 0.48, point.z)
        group.add(label)
        labels.push(label)
    }
    const links = [[0, 1], [1, 2], [1, 3], [1, 4], [2, 5], [3, 5], [4, 5], [5, 6]]
    const flowParticles = []
    for (const [from, to] of links) {
        const geometry = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(points[from].x, points[from].y, points[from].z),
            new THREE.Vector3(points[to].x, points[to].y, points[to].z),
        ])
        group.add(new THREE.Line(geometry, new THREE.LineBasicMaterial({ color: 0xf8c6a8, transparent: true, opacity: 0.55 })))
        const particle = new THREE.Mesh(new THREE.SphereGeometry(0.055, 10, 10), new THREE.MeshBasicMaterial({ color: 0xffffff }))
        group.add(particle)
        flowParticles.push({ particle, from: points[from], to: points[to], offset: Math.random() })
    }
    group.add(new THREE.AmbientLight(0x9eead8, 1.8))
    const keyLight = new THREE.PointLight(0xffb36b, 24, 14)
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
    const raycaster = new THREE.Raycaster()
    const pointer = new THREE.Vector2()
    let selected = 1
    let dragging = false
    let dragMoved = false
    let lastPointer = { x: 0, y: 0 }
    let cameraGoalZ = 13.5
    let cameraGoalX = 0
    let cameraGoalY = 0.3
    let focus = new THREE.Vector3(0, 0, 0)
    renderer.domElement.style.cursor = 'pointer'
    renderer.domElement.addEventListener('pointerdown', (event) => {
        dragging = true
        dragMoved = false
        lastPointer = { x: event.clientX, y: event.clientY }
        renderer.domElement.setPointerCapture(event.pointerId)
    })
    renderer.domElement.addEventListener('pointermove', (event) => {
        if (!dragging) return
        const dx = event.clientX - lastPointer.x
        const dy = event.clientY - lastPointer.y
        if (Math.abs(dx) + Math.abs(dy) > 2) dragMoved = true
        group.rotation.y += dx * 0.008
        group.rotation.x = Math.max(-0.55, Math.min(0.55, group.rotation.x + dy * 0.005))
        lastPointer = { x: event.clientX, y: event.clientY }
    })
    renderer.domElement.addEventListener('pointerup', (event) => {
        dragging = false
        renderer.domElement.releasePointerCapture(event.pointerId)
        if (dragMoved) return
        const bounds = renderer.domElement.getBoundingClientRect()
        pointer.x = ((event.clientX - bounds.left) / bounds.width) * 2 - 1
        pointer.y = -((event.clientY - bounds.top) / bounds.height) * 2 + 1
        raycaster.setFromCamera(pointer, camera)
        const hit = raycaster.intersectObjects(meshes)[0]
        if (hit) {
            selected = meshes.indexOf(hit.object)
            cameraGoalZ = 8.8
            cameraGoalX = points[selected].x * 0.2
            cameraGoalY = points[selected].y * 0.15
            focus = new THREE.Vector3(points[selected].x, points[selected].y, points[selected].z)
            detail.textContent = `${points[selected].name}: ${points[selected].description}`
        }
    })
    renderer.domElement.addEventListener('pointerleave', () => { dragging = false })
    renderer.domElement.addEventListener('wheel', (event) => {
        event.preventDefault()
        cameraGoalZ = Math.max(7, Math.min(16, cameraGoalZ + event.deltaY * 0.012))
    }, { passive: false })
    reset.addEventListener('click', () => {
        selected = 1
        group.rotation.x = 0
        group.rotation.y = 0
        cameraGoalZ = 13.5
        cameraGoalX = 0
        cameraGoalY = 0.3
        focus = new THREE.Vector3(0, 0, 0)
        detail.textContent = 'Click a node to inspect the flow.'
    })
    let frame = 0
    const animate = () => {
        frame = requestAnimationFrame(animate)
        camera.position.z += (cameraGoalZ - camera.position.z) * 0.08
        camera.position.x += (cameraGoalX - camera.position.x) * 0.08
        camera.position.y += (cameraGoalY - camera.position.y) * 0.08
        camera.lookAt(focus)
        if (!dragging) group.rotation.y += 0.001
        meshes.forEach((mesh, index) => {
            const pulse = 1 + Math.sin(Date.now() * 0.002 + index) * 0.055
            mesh.scale.setScalar(index === selected ? pulse * 1.28 : pulse)
            mesh.material.emissiveIntensity = index === selected ? 0.65 : 0.22
        })
        flowParticles.forEach((item) => {
            const progress = (Date.now() * 0.00035 + item.offset) % 1
            item.particle.position.lerpVectors(
                new THREE.Vector3(item.from.x, item.from.y, item.from.z),
                new THREE.Vector3(item.to.x, item.to.y, item.to.z),
                progress,
            )
        })
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

st.html("""
<style>
    :root {
        --ink: #122331;
        --muted: #5f707b;
        --marine: #102f42;
        --mint: #72f2c2;
        --sky: #67d4ff;
        --amber: #ffc470;
    }
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 88% 8%, rgba(255, 183, 77, .34), transparent 24rem),
            radial-gradient(circle at 12% 18%, rgba(241, 128, 112, .2), transparent 26rem),
            linear-gradient(135deg, #fff6e7 0%, #f8e5d8 50%, #eee3f3 100%);
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #3a2031 0%, #5d3544 58%, #7f4f55 100%);
        border-right: 1px solid rgba(255, 196, 112, .24);
    }
    [data-testid="stSidebar"] * { color: #e4fff7; }
    [data-testid="stSidebar"] [data-testid="stMetricValue"] { color: var(--mint); }
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background: rgba(114, 242, 194, .1);
        border-color: rgba(114, 242, 194, .18);
    }
    h1, h2, h3 { color: var(--ink); letter-spacing: -0.02em; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, .62);
        border-color: rgba(18, 35, 49, .12);
        box-shadow: 0 16px 38px rgba(25, 61, 75, .07);
        backdrop-filter: blur(12px);
    }
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, .52);
        border-color: rgba(18, 35, 49, .12);
    }
    .stButton > button {
        background: linear-gradient(110deg, #0f766e, #17658a);
        border: 0;
        border-radius: 10px;
        box-shadow: 0 8px 18px rgba(15, 118, 110, .2);
        color: white;
        font-weight: 700;
    }
    .stButton > button:hover {
        background: linear-gradient(110deg, #0b625d, #145575);
        border: 0;
        color: white;
        transform: translateY(-1px);
    }
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, .55);
        border-color: rgba(18, 35, 49, .1);
    }
</style>
""")


with st.sidebar:
    st.markdown("## :material/hub: GraphRAG lab")
    st.caption("Round 1 investigation console")
    st.badge("Local demo corpus", icon=":material/database:", color="green")
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
EVIDENCE_SCENE(data=scene_data, width="stretch", height=390)

with st.container(border=True):
    st.markdown("**Architecture legend**")
    with st.container(horizontal=True, wrap=True):
        for label, color in [
            ("Question", "blue"),
            ("Orchestrator", "green"),
            ("Vector search", "orange"),
            ("Graph traversal", "orange"),
            ("Document retrieval", "orange"),
            ("Evidence check", "violet"),
            ("Answer", "gray"),
        ]:
            st.badge(label, color=color)

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
