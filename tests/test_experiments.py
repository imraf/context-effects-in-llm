import pytest
from unittest.mock import patch, MagicMock
from exp1_needle import NeedleExperiment
import config


class TestNeedleExperiment:

    @patch("exp1_needle.OllamaClient")
    @patch("exp1_needle.load_english_articles")
    def test_quick_run(self, mock_load_articles, MockOllamaClient):
        # Setup mocks
        mock_client = MockOllamaClient.return_value
        mock_client.generate_with_stats.return_value = {
            "response": "BLUE-ZEBRA-99",
            "prompt_eval_count": 100,
        }

        mock_load_articles.return_value = ["Test article content."]

        # Initialize
        exp = NeedleExperiment("test-model", mode="quick")
        results = exp.run()

        # Verify
        assert "start" in results
        assert "middle" in results
        assert "end" in results
        assert results["start"]["accuracy"] == 1.0

    def test_invalid_mode(self):
        with pytest.raises(ValueError):
            NeedleExperiment("test-model", mode="invalid_mode")

    @patch("exp1_needle.OllamaClient")
    @patch("exp1_needle.load_text_from_file")
    def test_detailed_run(self, mock_load_text, MockOllamaClient):
        # Setup mocks
        mock_client = MockOllamaClient.return_value
        mock_client.generate_with_stats.return_value = {
            "response": "VRAMIEL",
            "prompt_eval_count": 100,
            "eval_count": 10,
            "eval_duration": 100,
            "load_duration": 100,
            "prompt_eval_duration": 100,
            "total_duration": 400,
        }

        mock_load_text.return_value = "Some long text content..."

        # Modify config temporarily for speed
        original_lengths = config.EXP1_DETAILED_PROMPT_LENGTHS
        config.EXP1_DETAILED_PROMPT_LENGTHS = [100]

        try:
            exp = NeedleExperiment("test-model", mode="info_retrieval")
            results = exp.run()

            assert isinstance(results, list)
            assert len(results) > 0
            assert results[0]["found_secret"] is True

        finally:
            config.EXP1_DETAILED_PROMPT_LENGTHS = original_lengths
