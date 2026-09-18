import unittest

from src.core import PIPELINES, benchmark, run_pipeline, summary


class CorePipelineTests(unittest.TestCase):
    def test_all_pipelines_return_trace_and_evidence(self) -> None:
        for pipeline in PIPELINES:
            result = run_pipeline("Who launched Atlas?", pipeline)
            self.assertEqual(result["pipeline"], pipeline)
            self.assertTrue(result["trace"])
            self.assertTrue(result["evidence"])
            self.assertGreater(result["tokens"], 0)

    def test_agentic_pipeline_uses_multiple_methods(self) -> None:
        result = run_pipeline("Who launched Atlas and which group did Maya Chen later join?", "Agentic GraphRAG")
        self.assertGreaterEqual(len(result["methods"]), 2)
        self.assertEqual(result["steps"], len(result["trace"]))

    def test_benchmark_summary_has_three_pipelines(self) -> None:
        results = benchmark(["Who launched Atlas?"])
        rows = summary(results)
        self.assertEqual([row["pipeline"] for row in rows], list(PIPELINES))


if __name__ == "__main__":
    unittest.main()