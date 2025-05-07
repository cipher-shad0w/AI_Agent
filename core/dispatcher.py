import importlib
import os
from typing import Any, Dict, List, Optional, Type
import logging

from core.module_base import ModuleBase


class ModuleDispatcher:
    """
    Manages module loading, execution, and data flow between modules.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the dispatcher with configuration.
        
        Args:
            config: Configuration for the dispatcher and modules
        """
        self.config = config
        self.modules: Dict[str, ModuleBase] = {}
        self.logger = logging.getLogger("ModuleDispatcher")
        
        # Set up logging
        log_level = getattr(logging, config.get("log_level", "INFO").upper())
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    def discover_modules(self) -> List[str]:
        """
        Discover available modules in the modules directory.
        
        Returns:
            List of module names (without .py extension)
        """
        modules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "modules")
        module_files = [
            f[:-3] for f in os.listdir(modules_dir) 
            if f.endswith(".py") and not f.startswith("__")
        ]
        return module_files
    
    def load_module(self, module_name: str) -> ModuleBase:
        """
        Dynamically load a module by name.
        
        Args:
            module_name: Name of the module to load

        Returns:
            Instantiated module
        
        Raises:
            ImportError: If the module cannot be imported
            TypeError: If the module doesn't have the expected class
        """
        if module_name in self.modules:
            return self.modules[module_name]
        
        # Import the module
        try:
            module_path = f"modules.{module_name}"
            module = importlib.import_module(module_path)
            
            # Find the class that inherits from ModuleBase
            module_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type) and 
                    issubclass(attr, ModuleBase) and 
                    attr is not ModuleBase
                ):
                    module_class = attr
                    break
            
            if not module_class:
                raise TypeError(f"No ModuleBase subclass found in {module_path}")
            
            # Get module-specific config
            module_config = self.config.get("modules", {}).get(module_name, {})
            
            # Instantiate the module
            module_instance = module_class(module_config)
            self.modules[module_name] = module_instance
            self.logger.info(f"Loaded module: {module_name}")
            
            return module_instance
            
        except Exception as e:
            self.logger.error(f"Error loading module {module_name}: {e}")
            raise
    
    def unload_module(self, module_name: str) -> None:
        """
        Unload a module and clean up its resources.
        
        Args:
            module_name: Name of the module to unload
        """
        if module_name in self.modules:
            self.modules[module_name].shutdown()
            del self.modules[module_name]
            self.logger.info(f"Unloaded module: {module_name}")
    
    def execute_pipeline(self, input_data: Dict[str, Any], pipeline: List[str]) -> Dict[str, Any]:
        """
        Execute a series of modules in sequence, passing output from one to the next.
        
        Args:
            input_data: Initial input data
            pipeline: List of module names to execute in sequence
            
        Returns:
            Processed data after passing through all modules
        """
        current_data = input_data.copy()
        
        for module_name in pipeline:
            module = self.load_module(module_name)
            self.logger.debug(f"Executing module: {module_name}")
            current_data = module.process(current_data)
            
        return current_data
    
    def close(self) -> None:
        """
        Clean up resources for all loaded modules.
        """
        for module_name in list(self.modules.keys()):
            self.unload_module(module_name)
        self.logger.info("All modules unloaded")