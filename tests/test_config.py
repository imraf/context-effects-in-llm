import config


class TestConfig:
    def test_paths_exist(self):
        # We can't strictly enforce they exist on all systems, but we can check format
        assert config.RESULTS_DIR.endswith("results")
        assert config.PLOTS_DIR.endswith("plots")

    def test_models_list(self):
        assert isinstance(config.MODELS, list)
        assert len(config.MODELS) > 0
        assert all(":" in model for model in config.MODELS)

    def test_experiment_config(self):
        assert isinstance(config.NEEDLE_EXPERIMENTS, dict)
        assert "quick" in config.NEEDLE_EXPERIMENTS
        assert "info_retrieval" in config.NEEDLE_EXPERIMENTS
        assert "anomaly_detection" in config.NEEDLE_EXPERIMENTS

    def test_environment_vars(self):
        # Basic check to ensure OLLAMA_HOST is set
        assert config.OLLAMA_HOST is not None
        assert config.OLLAMA_HOST.startswith("http")
