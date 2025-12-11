"""Context Horizons: LLM Context Window Benchmarking Suite.

A comprehensive benchmarking suite for evaluating context window
performance across multiple large language models.
"""

__version__ = "0.1.0"
__author__ = "Context Horizons Team"

from utils import OllamaClient
from exp1_needle import NeedleExperiment
from exp2_size import ContextSizeExperiment
from exp3_rag import RagExperiment
from exp4_strategies import StrategiesExperiment

__all__ = [
    "OllamaClient",
    "NeedleExperiment",
    "ContextSizeExperiment",
    "RagExperiment",
    "StrategiesExperiment",
]
