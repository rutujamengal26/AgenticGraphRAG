"""MCP tools that expose the prototype's retrieval capabilities to VS Code."""

from mcp.server.mcpserver import MCPServer

try:
    from .core import graph_traverse, run_pipeline, similarity_search
except ImportError:
    from core import graph_traverse, run_pipeline, similarity_search


mcp = MCPServer("Agentic GraphRAG")


@mcp.tool()
def search_documents(question: str, limit: int = 3) -> list[dict]:
    """Find supporting documents for a question using lexical similarity."""
    return similarity_search(question, limit)


@mcp.tool()
def traverse_graph(question: str) -> list[dict]:
    """Return graph relationships relevant to a question."""
    return graph_traverse(question)


@mcp.tool()
def investigate(question: str) -> dict:
    """Run the agentic prototype and return its answer, evidence, and trace."""
    return run_pipeline(question, "Agentic GraphRAG")


if __name__ == "__main__":
    mcp.run()
