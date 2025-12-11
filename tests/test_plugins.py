import os

from base import ExperimentBase
from plugins import PluginRegistry


class TestPlugins:
    def test_discovery(self):
        # Force re-discovery
        PluginRegistry._discovered = False
        PluginRegistry._experiments = {}

        PluginRegistry.discover_experiments()
        experiments = PluginRegistry.get_all_experiments()

        assert len(experiments) >= 4
        assert 1 in experiments
        assert 2 in experiments
        assert 3 in experiments
        assert 4 in experiments

        assert issubclass(experiments[1], ExperimentBase)
        assert experiments[1].NAME == "Needle in Haystack"

    def test_get_class(self):
        PluginRegistry._discovered = False
        PluginRegistry._experiments = {}

        cls = PluginRegistry.get_experiment_class(1)
        assert cls is not None
        assert cls.ID == 1
