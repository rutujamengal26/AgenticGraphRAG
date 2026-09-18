# Agentic GraphRAG Round 1 Prototype

This Round 1 package implements the core experiment from the TigerGraph guidebook: answer the same questions with RAG, GraphRAG, and Agentic GraphRAG, then compare accuracy, grounding, evidence, investigation trace, and estimated token cost.

## 1. Create the VS Code environment

Open this folder in VS Code, then run these commands in the integrated PowerShell terminal:

```powershell
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Select `.venv` with `Python: Select Interpreter`.

## 2. Run the prototype

```powershell
streamlit run app.py
```

Use the browser view to ask a question, compare all three pipelines, inspect evidence, and run the starter benchmark. The corpus is intentionally small and deterministic so the architecture is easy to replace with the hackathon dataset.

## 3. Add MCP to VS Code

The MCP server is already configured in `.vscode/mcp.json`. Restart or reload VS Code after installing dependencies. In Copilot Chat, switch to Agent mode and inspect the available tools from `agentic-graphrag`.

The server exposes:

- `search_documents(question, limit)`
- `traverse_graph(question)`
- `investigate(question)`


To inspect it independently:

```powershell
python src/mcp_server.py
```

For the MCP Inspector, use:

```powershell
mcp dev src/mcp_server.py
```

## 4. Generate submission artifacts

Run the reproducible local benchmark:

```powershell
python benchmark.py
python -m unittest discover -s tests -v
```

This writes `artifacts/benchmark_results.json` with per-question traces and pipeline summaries. It is labeled `local-demo` until the official dataset is loaded.

## 5. Replace the demo corpus

Edit `DOCUMENTS` and `EDGES` in `src/core.py`, or create a loader for the provided dataset. Keep the same `run_pipeline` return shape so the metrics view and MCP tools continue to work.

## 6. Round 1 completion checklist

1. Load the 100 public questions and corpus.
2. Replace lexical search with TigerGraph vector and graph queries.
3. Add an LLM-backed orchestrator that chooses the next tool from the question and prior evidence.
4. Add answer grading for accuracy, completeness, and citation grounding.
5. Save raw outputs, trace events, and token counts for the 50 hidden questions.
6. Publish the GitHub repository, architecture diagram, demo video, and metrics dashboard.

The hackathon guidebook lists Sep 24, 2026 as the Round 1 submission deadline.
