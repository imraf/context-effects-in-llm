from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class ExperimentBase(ABC):
    """Abstract base class for all experiments."""
    
    ID: int
    NAME: str

    def __init__(self, model: str, **kwargs):
        self.model = model
        self.kwargs = kwargs

    @abstractmethod
    def run(self) -> Any:
        """Run the experiment and return results."""
        pass
