# Round 1 Architecture

```mermaid
flowchart LR
    Q[Question] --> O[Orchestrator]
    O -->|simple retrieval| V[Vector / document search]
    O -->|relationship reasoning| G[Graph traversal]
    O -->|verify gaps| E[Evidence evaluator]
    V --> C[Evidence store]
    G --> C
    E -->|enough evidence| A[Answer generator]
    E -->|missing evidence| O
    A --> R[Answer + citations + trace + token metrics]
    M[MCP server] --> V
    M --> G
    M --> O
```

## Components

- **RAG** calls document similarity search once.
- **GraphRAG** combines graph relationships with document retrieval.
- **Agentic GraphRAG** chooses retrieval order, checks evidence, and records the investigation trace.
- **MCP** exposes retrieval and investigation tools to VS Code Copilot.
- **Benchmark runner** evaluates the same questions across all three pipelines and writes JSON artifacts.

The checked-in corpus is a deterministic demo corpus. The official TigerGraph corpus and 100 public questions must replace it for the actual submission run.