from unittest.mock import patch, mock_open
import analyze_results
import config
import os

# Sample Data
STANDARD_RESULT = {
    "model": "test-model",
    "exp1_needle": {
        "start": {"accuracy": 1.0},
        "middle": {"accuracy": 0.5},
        "end": {"accuracy": 0.0}
    },
    "exp2_size": [
        {"token_count": 100, "accuracy": 1.0, "latency": 0.1},
        {"token_count": 1000, "accuracy": 0.8, "latency": 1.0}
    ],
    "exp3_rag": {
        "rag": {"accuracy": 0.9, "latency": 0.2},
        "full_context": {"accuracy": 1.0, "latency": 2.0}
    },
    "exp4_strategies": {
        "write": {"correct": True}
    }
}

DETAILED_RESULT = {
    "experiment_metadata": {
        "experiment_name": "test-exp",
        "models": ["test-model"]
    },
    "results": [
        {
            "model": "test-model",
            "message_position": "start",
            "target_prompt_length": 1000,
            "found_secret": True,
            "query_time_seconds": 0.5
        },
        {
            "model": "test-model",
            "message_position": "middle",
            "target_prompt_length": 1000,
            "found_secret": False,
            "query_time_seconds": 0.6
        }
    ]
}


class TestAnalyzeResults:

    @patch("glob.glob")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    def test_load_results(self, mock_json, mock_file, mock_glob):
        # Setup
        mock_glob.return_value = ["res1.json", "res2.json"]
        mock_json.side_effect = [STANDARD_RESULT, DETAILED_RESULT]

        # Execute
        results = analyze_results.load_results()

        # Verify
        assert len(results) == 2
        assert results[0]["type"] == "standard"
        assert results[1]["type"] == "detailed_needle"

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.figure")
    @patch("seaborn.heatmap")
    def test_plot_exp1_needle(self, mock_heatmap, mock_figure, mock_savefig):
        results = [{"type": "standard", "data": STANDARD_RESULT}]
        analyze_results.plot_exp1_needle(results)

        mock_heatmap.assert_called()
        mock_savefig.assert_called_with(
            os.path.join(config.PLOTS_DIR, "exp1_heatmap.png"), dpi=300
        )

    @patch("matplotlib.pyplot.savefig")
    @patch("seaborn.lineplot")
    def test_plot_exp2_size(self, mock_lineplot, mock_savefig):
        results = [{"type": "standard", "data": STANDARD_RESULT}]
        analyze_results.plot_exp2_size(results)

        assert mock_lineplot.call_count == 2  # Accuracy and Latency
        mock_savefig.assert_called()

    @patch("matplotlib.pyplot.savefig")
    @patch("seaborn.barplot")
    def test_plot_exp3_rag(self, mock_barplot, mock_savefig):
        results = [{"type": "standard", "data": STANDARD_RESULT}]
        analyze_results.plot_exp3_rag(results)

        assert mock_barplot.call_count == 2
        mock_savefig.assert_called()

    @patch("matplotlib.pyplot.savefig")
    def test_plot_radar_summary(self, mock_savefig):
        results = [{"type": "standard", "data": STANDARD_RESULT}]
        analyze_results.plot_radar_summary(results)
        mock_savefig.assert_called()

    @patch("matplotlib.pyplot.savefig")
    def test_plot_detailed_needle_experiments(self, mock_savefig):
        results = [{
            "type": "detailed_needle",
            "metadata": DETAILED_RESULT["experiment_metadata"],
            "results": DETAILED_RESULT["results"]
        }]
        analyze_results.plot_detailed_needle_experiments(results)
        mock_savefig.assert_called()

    @patch("analyze_results.load_results")
    @patch("analyze_results.plot_exp1_needle")
    @patch("analyze_results.plot_exp2_size")
    @patch("analyze_results.plot_exp3_rag")
    @patch("analyze_results.plot_radar_summary")
    @patch("analyze_results.plot_detailed_needle_experiments")
    def test_main(self, mock_detailed, mock_radar, mock_rag, mock_size, mock_needle, mock_load):
        mock_load.return_value = ["some data"]
        analyze_results.main()

        mock_needle.assert_called()
        mock_size.assert_called()
        mock_rag.assert_called()
        mock_radar.assert_called()
        mock_detailed.assert_called()
