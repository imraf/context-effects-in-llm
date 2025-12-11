import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import config
from main import run_single_model


class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for results
        self.test_dir = tempfile.mkdtemp()
        self.original_results_dir = config.RESULTS_DIR
        config.RESULTS_DIR = self.test_dir

    def tearDown(self):
        # Cleanup
        shutil.rmtree(self.test_dir)
        config.RESULTS_DIR = self.original_results_dir

    @patch("exp1_needle.OllamaClient")
    @patch("exp2_size.OllamaClient")
    @patch("exp3_rag.OllamaClient")
    @patch("exp4_strategies.OllamaClient")
    @patch("exp1_needle.load_english_articles")
    @patch("exp2_size.load_english_articles")
    @patch("exp3_rag.load_hebrew_articles")
    def test_run_single_model_end_to_end(
        self,
        mock_load_hebrew_articles,
        mock_load_articles_exp2,
        mock_load_articles_exp1,
        mock_client_exp4,
        mock_client_exp3,
        mock_client_exp2,
        mock_client_exp1,
    ):
        # Setup mocks
        mock_articles = ["Article 1 content.", "Article 2 content.", "Article 3 content."]
        mock_load_articles_exp1.return_value = mock_articles
        mock_load_articles_exp2.return_value = mock_articles
        mock_load_hebrew_articles.return_value = mock_articles

        # Mock generate responses
        mock_client_instance = MagicMock()
        mock_client_instance.generate.return_value = "Mocked Response BLUE-ZEBRA-99"
        mock_client_instance.generate_with_stats.return_value = {
            "response": "Mocked Response",
            "prompt_eval_count": 100,
            "eval_count": 50,
            "total_duration": 1000,
        }
        mock_client_instance.embed.return_value = [0.1, 0.2, 0.3]

        mock_client_exp1.return_value = mock_client_instance
        mock_client_exp2.return_value = mock_client_instance
        mock_client_exp3.return_value = mock_client_instance
        mock_client_exp4.return_value = mock_client_instance

        # Run with a single experiment (e.g., Exp 2) to be fast
        original_doc_counts = config.EXP2_DOC_COUNTS
        config.EXP2_DOC_COUNTS = [2]

        try:
            model_name = "test-model"
            # Run all experiments to verify integration
            results = run_single_model(model_name, experiments=[2], exp1_mode="quick")

            # Assertions
            self.assertEqual(results["model"], model_name)
            self.assertIn("exp2_size", results)
            self.assertTrue(len(results["exp2_size"]) > 0)
            self.assertEqual(results["exp2_size"][0]["doc_count"], 2)

            # Check if file was created
            safe_model_name = model_name.replace(":", "_")
            expected_file = os.path.join(self.test_dir, f"{safe_model_name}_results.json")
            self.assertTrue(os.path.exists(expected_file))

            with open(expected_file, "r") as f:
                saved_data = json.load(f)
                self.assertEqual(saved_data["model"], model_name)

        finally:
            config.EXP2_DOC_COUNTS = original_doc_counts


if __name__ == "__main__":
    unittest.main()
