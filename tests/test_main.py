from unittest.mock import patch, MagicMock
import main


class TestMain:

    @patch("main.NeedleExperiment")
    @patch("main.ContextSizeExperiment")
    @patch("main.RagExperiment")
    @patch("main.StrategiesExperiment")
    @patch("builtins.open", new_callable=MagicMock)
    @patch("json.dump")
    def test_run_single_model(self, mock_json_dump, mock_open, MockStrategies, MockRag, MockSize, MockNeedle):
        # Setup mocks
        MockNeedle.return_value.run.return_value = {"needle": "results"}
        MockSize.return_value.run.return_value = ["size_results"]
        MockRag.return_value.run.return_value = {"rag": "results"}
        MockStrategies.return_value.run.return_value = {"strat": "results"}

        # Execute
        results = main.run_single_model("test-model", experiments=[1, 2, 3, 4], exp1_mode="quick")

        # Verify
        assert results["model"] == "test-model"
        assert results["exp1_needle"] == {"needle": "results"}
        assert results["exp2_size"] == ["size_results"]
        assert results["exp3_rag"] == {"rag": "results"}
        assert results["exp4_strategies"] == {"strat": "results"}

        # Check if saved
        mock_json_dump.assert_called()

    @patch("main.NeedleExperiment")
    def test_run_single_model_detailed_exp1(self, MockNeedle):
        # Setup
        mock_exp1 = MockNeedle.return_value
        mock_exp1.run.return_value = [{"detailed": "result"}]

        # Execute
        main.run_single_model("test-model", experiments=[1], exp1_mode="info_retrieval")

        # Verify
        mock_exp1.save_detailed_results.assert_called()

    @patch("main.run_single_model")
    def test_run_benchmark_sequential(self, mock_run_single):
        models = ["model1", "model2"]
        main.run_benchmark(models=models, experiments=[1], parallel=False)

        assert mock_run_single.call_count == 2

    @patch("main.Pool")
    @patch("main.cpu_count")
    def test_run_benchmark_parallel(self, mock_cpu, mock_pool):
        mock_cpu.return_value = 4
        models = ["model1", "model2"]

        # Mock pool instance
        pool_instance = mock_pool.return_value
        pool_instance.__enter__.return_value = pool_instance

        main.run_benchmark(models=models, experiments=[1], parallel=True)

        pool_instance.map.assert_called()
