import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from exp1_needle import NeedleExperiment
from exp2_size import ContextSizeExperiment
from exp3_rag import RagExperiment
from exp4_strategies import StrategiesExperiment
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
        
        # Mock the async method
        mock_client.generate_with_stats_async = AsyncMock(return_value={
            "response": "VRAMIEL",
            "prompt_eval_count": 100,
            "eval_count": 10,
            "eval_duration": 100,
            "load_duration": 100,
            "prompt_eval_duration": 100,
            "total_duration": 400,
        })

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


class TestContextSizeExperiment:

    @patch("exp2_size.OllamaClient")
    @patch("exp2_size.load_english_articles")
    def test_run(self, mock_load, MockClient):
        mock_load.return_value = ["doc1", "doc2", "doc3", "doc4"]
        mock_client = MockClient.return_value
        mock_client.generate.return_value = "ID-1234"  # Simulate correct answer

        # Override config doc counts to be small for test
        original_counts = config.EXP2_DOC_COUNTS
        config.EXP2_DOC_COUNTS = [2]

        try:
            exp = ContextSizeExperiment("test-model")
            results = exp.run()

            assert len(results) == 1
            assert results[0]["doc_count"] == 2
        finally:
            config.EXP2_DOC_COUNTS = original_counts


class TestRagExperiment:

    @patch("exp3_rag.OllamaClient")
    @patch("exp3_rag.load_hebrew_articles")
    @patch("exp3_rag.Chroma")
    @patch("exp3_rag.OllamaEmbeddings")
    @patch("os.path.exists")
    def test_run(self, mock_exists, MockEmbeddings, MockChroma, mock_load, MockClient):
        mock_exists.return_value = False  # Force new DB creation
        mock_load.return_value = ["hebrew doc 1", "hebrew doc 2"]
        mock_client = MockClient.return_value
        mock_client.generate.return_value = "Yes"

        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = [MagicMock(page_content="doc snippet")]
        MockChroma.from_documents.return_value.as_retriever.return_value = mock_retriever

        exp = RagExperiment("test-model")
        results = exp.run()

        assert "full_context" in results
        assert "rag" in results
        assert results["rag"]["accuracy"] == 1.0


class TestStrategiesExperiment:

    @patch("exp4_strategies.OllamaClient")
    def test_run(self, MockClient):
        mock_client = MockClient.return_value
        mock_client.generate.return_value = "Table"  # Correct answer

        exp = StrategiesExperiment("test-model")
        results = exp.run()

        assert "baseline" in results
        assert "select" in results
        assert "compress" in results
        assert "write" in results
        assert results["baseline"]["correct"] is True
