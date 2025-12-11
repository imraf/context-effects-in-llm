import glob
import importlib
import inspect
import logging
import os
import sys
from typing import Dict, Optional, Type

from base import ExperimentBase

logger = logging.getLogger(__name__)


class PluginRegistry:
    _experiments: Dict[int, Type[ExperimentBase]] = {}
    _discovered = False

    @classmethod
    def discover_experiments(cls):
        """Discover and register experiments from local files."""
        if cls._discovered:
            return

        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Look for files matching exp*.py
        files = glob.glob(os.path.join(current_dir, "exp*.py"))

        # Ensure current dir is in path
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        for file_path in files:
            module_name = os.path.basename(file_path).replace(".py", "")
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, ExperimentBase) and obj is not ExperimentBase:
                        if hasattr(obj, "ID") and isinstance(obj.ID, int):
                            cls._experiments[obj.ID] = obj
                            logger.info(f"Registered Experiment {obj.ID}: {obj.NAME} ({name})")
                        else:
                            logger.warning(f"Skipping {name}: Missing ID or NAME class attributes.")

            except Exception as e:
                logger.error(f"Failed to load plugin {module_name}: {e}")

        cls._discovered = True

    @classmethod
    def get_experiment_class(cls, exp_id: int) -> Optional[Type[ExperimentBase]]:
        if not cls._discovered:
            cls.discover_experiments()
        return cls._experiments.get(exp_id)

    @classmethod
    def get_all_experiments(cls) -> Dict[int, Type[ExperimentBase]]:
        if not cls._discovered:
            cls.discover_experiments()
        return cls._experiments
