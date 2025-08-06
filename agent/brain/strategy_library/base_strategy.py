from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseStrategy(ABC):
    """
    Abstract base class for all mission strategies.
    Defines the interface for how a strategy should be executed.
    """

    def __init__(self, runtime: Any, mission_data: Dict[str, Any]):
        self.runtime = runtime  # AgentRuntime instance
        self.mission_data = mission_data # Data related to the current mission

    @abstractmethod
    async def execute(self) -> Dict[str, Any]:
        """
        Executes the specific strategy.
        Returns a dictionary containing the result of the strategy execution.
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the name of the strategy.
        """
        pass


