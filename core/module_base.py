from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ModuleBase(ABC):
    """
    Base class for all agent modules.
    All modules must inherit from this class and implement its abstract methods.
    """
    
    def __init__(self, module_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the module with configuration.
        
        Args:
            module_config: Configuration dictionary specific to this module
        """
        self.module_config = module_config or {}
        self.name = self.__class__.__name__
        self.initialize()
    
    def initialize(self) -> None:
        """
        Additional initialization that can be overridden by derived classes.
        Called after __init__.
        """
        pass
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data and return the processed result.
        
        Args:
            input_data: The input data to process
            
        Returns:
            The processed output data
        """
        pass
    
    def shutdown(self) -> None:
        """
        Clean up resources when the module is being shut down.
        Can be overridden by derived classes.
        """
        pass