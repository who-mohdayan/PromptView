import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.models import PromptBreakdown

client = TestClient(app)


class TestPromptViewAPI(unittest.TestCase):
    def test_health_endpoint(self):
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("api_key_configured", data)
        self.assertIn("model", data)

    def test_examples_endpoint(self):
        response = client.get("/api/examples")
        self.assertEqual(response.status_code, 200)
        examples = response.json()
        self.assertIsInstance(examples, list)
        self.assertGreaterEqual(len(examples), 4)
        for example in examples:
            self.assertIn("id", example)
            self.assertIn("title", example)
            self.assertIn("category", example)
            self.assertIn("prompt", example)
            self.assertGreater(len(example["prompt"]), 10)

    def test_empty_prompt_validation(self):
        # Empty string
        response = client.post("/api/analyze", json={"prompt": ""})
        self.assertEqual(response.status_code, 422)

        # Whitespace only string
        response = client.post("/api/analyze", json={"prompt": "   \n\t  "})
        self.assertEqual(response.status_code, 400)
        self.assertIn("empty", response.json()["detail"].lower())

    def test_missing_prompt_field(self):
        response = client.post("/api/analyze", json={})
        self.assertEqual(response.status_code, 422)

    @patch("app.main.analyze_prompt_with_gemini")
    def test_successful_prompt_analysis_mock(self, mock_analyze):
        mock_breakdown = PromptBreakdown(
            role="Principal Python Architect",
            task="Refactor legacy synchronous data processing script to modern async code",
            context="Legacy script needs to utilize asyncio and httpx for performance improvements",
            constraints=[
                "Keep memory usage strictly below 250MB",
                "Do not use third-party libraries outside httpx",
                "Adhere to PEP 8 standards",
            ],
            expected_output="Final refactored code with explanatory docstrings followed by a markdown table of complexity improvements",
            summary="Refactor a synchronous Python data processing script to high-performance async code under strict memory and dependency constraints.",
            completeness_score=94,
            suggestions=[
                "Specify the maximum timeout thresholds for async HTTP calls",
                "Define how errors from upstream external services should be handled",
            ],
        )
        mock_analyze.return_value = mock_breakdown

        payload = {
            "prompt": "Act as a Principal Python Architect. Refactor this script into async code."
        }
        response = client.post("/api/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data["success"])
        data = json_data["data"]
        self.assertEqual(data["role"], "Principal Python Architect")
        self.assertTrue(data["task"].startswith("Refactor"))
        self.assertEqual(len(data["constraints"]), 3)
        self.assertEqual(data["completeness_score"], 94)
        self.assertEqual(len(data["suggestions"]), 2)

    @patch("app.main.analyze_prompt_with_gemini")
    def test_api_error_handling(self, mock_analyze):
        mock_analyze.side_effect = RuntimeError("Gemini API rate limit or quota exceeded.")
        response = client.post(
            "/api/analyze", json={"prompt": "Write a summary of this document."}
        )
        self.assertEqual(response.status_code, 502)
        self.assertIn("rate limit", response.json()["detail"].lower())


if __name__ == "__main__":
    unittest.main()
