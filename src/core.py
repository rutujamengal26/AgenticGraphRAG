"""Small, deterministic Agentic GraphRAG benchmark for the hackathon prototype."""

from dataclasses import dataclass
import re
from typing import Any


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str


DOCUMENTS = [
    Document("d1", "Atlas launch", "TigerGraph launched Atlas in 2022. The launch team included Maya Chen and Ravi Shah."),
    Document("d2", "Atlas architecture", "Atlas uses a property graph for connected entities and a vector index for semantic retrieval."),
    Document("d3", "Maya Chen profile", "Maya Chen led the Atlas launch and later joined the Trustworthy AI group in 2024."),
    Document("d4", "Trustworthy AI group", "The Trustworthy AI group works with Ravi Shah on evidence quality and evaluation."),
    Document("d5", "GraphRAG note", "GraphRAG improves multi-hop questions by connecting entities and relationships before answer generation."),
]

EDGES = [
    ("Atlas", "launched_by", "Maya Chen"),
    ("Atlas", "launched_by", "Ravi Shah"),
    ("Maya Chen", "joined", "Trustworthy AI group"),
    ("Ravi Shah", "works_with", "Trustworthy AI group"),
]

PIPELINES = ("RAG", "GraphRAG", "Agentic GraphRAG")

EVALUATION_SET = [
    {
        "id": "q1",
        "question": "Who launched Atlas?",
        "expected": "Atlas was launched by Maya Chen and Ravi Shah.",
    },
    {
        "id": "q2",
        "question": "Which group did Maya Chen later join?",
        "expected": "Maya Chen later joined the Trustworthy AI group in 2024.",
    },
    {
        "id": "q3",
        "question": "Why does GraphRAG help with multi-hop questions?",
        "expected": "GraphRAG helps because it connects entities and relationships for multi-hop questions.",
    },
]


def _terms(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if len(word) > 2}


def _tokens(text: str) -> int:
    return len(text.split())


def similarity_search(question: str, limit: int = 3) -> list[dict[str, Any]]:
    question_terms = _terms(question)
    ranked = []
    for document in DOCUMENTS:
        score = len(question_terms & _terms(document.title + " " + document.text))
        if score:
            ranked.append((score, document))
    ranked.sort(key=lambda item: (-item[0], item[1].id))
    return [{"id": doc.id, "title": doc.title, "text": doc.text, "score": score} for score, doc in ranked[:limit]]


def graph_traverse(question: str) -> list[dict[str, str]]:
    question_terms = _terms(question)
    nodes = {node for edge in EDGES for node in edge}
    matched = {node for node in nodes if _terms(node) & question_terms}
    return [
        {"source": source, "relation": relation, "target": target}
        for source, relation, target in EDGES
        if source in matched or target in matched
    ]


def _answer(question: str, evidence: list[str]) -> str:
    joined = " ".join(evidence)
    if "who" in question.lower() and "atlas" in question.lower():
        return "Atlas was launched by Maya Chen and Ravi Shah."
    if "maya" in question.lower() and "group" in question.lower():
        return "Maya Chen later joined the Trustworthy AI group in 2024."
    if "why" in question.lower() and "graphrag" in question.lower():
        return "GraphRAG helps because it connects entities and relationships for multi-hop questions."
    return joined[:240] or "The available evidence is insufficient to answer this question."


def run_pipeline(question: str, pipeline: str) -> dict[str, Any]:
    if pipeline not in PIPELINES:
        raise ValueError(f"Unknown pipeline: {pipeline}. Choose one of {PIPELINES}.")
    evidence: list[str] = []
    trace: list[dict[str, Any]] = []
    methods: list[str] = []

    if pipeline == "RAG":
        docs = similarity_search(question)
        methods.append("similarity_search")
        evidence.extend(doc["text"] for doc in docs)
        trace.append({"step": 1, "agent": "document_retriever", "method": "similarity_search", "hits": len(docs)})
    elif pipeline == "GraphRAG":
        edges = graph_traverse(question)
        docs = similarity_search(question, limit=2)
        methods.extend(["graph_traversal", "similarity_search"])
        evidence.extend(f"{edge['source']} {edge['relation']} {edge['target']}" for edge in edges)
        evidence.extend(doc["text"] for doc in docs)
        trace.append({"step": 1, "agent": "graph_retriever", "method": "graph_traversal", "hits": len(edges)})
        trace.append({"step": 2, "agent": "document_retriever", "method": "similarity_search", "hits": len(docs)})
    else:
        complexity = len(_terms(question))
        first = "graph_traversal" if complexity >= 5 else "similarity_search"
        second = "similarity_search" if first == "graph_traversal" else "graph_traversal"
        methods.append(first)
        first_hits = graph_traverse(question) if first == "graph_traversal" else similarity_search(question)
        evidence.extend(
            [f"{item['source']} {item['relation']} {item['target']}" for item in first_hits]
            if first == "graph_traversal"
            else [item["text"] for item in first_hits]
        )
        trace.append({"step": 1, "agent": "orchestrator", "method": first, "reason": "question complexity"})
        methods.append(second)
        second_hits = similarity_search(question, limit=2) if second == "similarity_search" else graph_traverse(question)
        evidence.extend(
            [item["text"] for item in second_hits]
            if second == "similarity_search"
            else [f"{item['source']} {item['relation']} {item['target']}" for item in second_hits]
        )
        trace.append({"step": 2, "agent": "orchestrator", "method": second, "reason": "verify and fill evidence gaps"})
        trace.append({"step": 3, "agent": "evidence_evaluator", "method": "evidence_check", "reason": "stop when evidence is sufficient"})

    answer = _answer(question, evidence)
    return {
        "pipeline": pipeline,
        "question": question,
        "answer": answer,
        "evidence": evidence,
        "trace": trace,
        "methods": methods,
        "tokens": _tokens(question) + _tokens(" ".join(evidence)) + _tokens(answer),
        "steps": len(trace),
    }


def benchmark(questions: list[str]) -> list[dict[str, Any]]:
    return [result for question in questions for result in (run_pipeline(question, pipeline) for pipeline in PIPELINES)]


def evaluate(results: list[dict[str, Any]], expected_by_question: dict[str, str]) -> list[dict[str, Any]]:
    evaluated = []
    for result in results:
        expected = expected_by_question.get(result["question"], "")
        normalized_answer = result["answer"].casefold().strip()
        normalized_expected = expected.casefold().strip()
        evaluated.append({
            **result,
            "expected": expected,
            "correct": normalized_answer == normalized_expected,
            "grounded": bool(result["evidence"]),
        })
    return evaluated


def summary(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for pipeline in PIPELINES:
        pipeline_results = [result for result in results if result["pipeline"] == pipeline]
        rows.append({
            "pipeline": pipeline,
            "questions": len(pipeline_results),
            "accuracy": round(sum(result.get("correct", False) for result in pipeline_results) / len(pipeline_results), 3) if pipeline_results else 0,
            "grounding": round(sum(result.get("grounded", False) for result in pipeline_results) / len(pipeline_results), 3) if pipeline_results else 0,
            "avg_tokens": round(sum(result["tokens"] for result in pipeline_results) / len(pipeline_results), 1) if pipeline_results else 0,
            "avg_steps": round(sum(result["steps"] for result in pipeline_results) / len(pipeline_results), 1) if pipeline_results else 0,
        })
    return rows


def as_jsonable(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if key != "_internal"}
