import logging
import time
from typing import Any, Dict, List, Optional, Union

from core.dispatcher import ModuleDispatcher


class Agent:
    """
    Core AI agent that coordinates module execution and maintains state.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the agent with configuration.
        
        Args:
            config: Configuration for the agent and its modules
        """
        self.config = config
        self.logger = logging.getLogger("Agent")
        self.dispatcher = ModuleDispatcher(config)
        self.state: Dict[str, Any] = {}
        self.running = False
        
        # Get predefined pipelines from config
        self.pipelines = config.get("pipelines", {})
    
    def initialize(self) -> None:
        """
        Initialize the agent and discover available modules.
        """
        self.logger.info("Initializing agent")
        
        # Discover available modules
        available_modules = self.dispatcher.discover_modules()
        self.logger.info(f"Discovered modules: {', '.join(available_modules) if available_modules else 'None'}")
        
        # Preload modules specified in config
        preload_modules = self.config.get("preload_modules", [])
        for module_name in preload_modules:
            try:
                self.dispatcher.load_module(module_name)
            except Exception as e:
                self.logger.error(f"Failed to preload module {module_name}: {e}")
        
        self.running = True
        self.logger.info("Agent initialized")
    
    def process(self, input_data: Dict[str, Any], pipeline_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Process input data through a specific pipeline or the default pipeline.
        
        Args:
            input_data: The input data to process
            pipeline_name: Name of the pipeline to use, or None for default
            
        Returns:
            The processed result
        """
        if not self.running:
            raise RuntimeError("Agent is not running. Call initialize() first.")
        
        # Enrich input data with agent state
        enriched_input = {
            **input_data,
            "_agent_state": self.state,
            "_timestamp": time.time()
        }
        
        # Get pipeline to use
        pipeline = []
        if pipeline_name:
            if pipeline_name not in self.pipelines:
                raise ValueError(f"Pipeline '{pipeline_name}' not found")
            pipeline = self.pipelines[pipeline_name]
        else:
            # Use default pipeline if defined
            if "default" in self.pipelines:
                pipeline = self.pipelines["default"]
            # If no pipeline specified and no default, use all available modules
            elif "auto_discover" in self.config and self.config["auto_discover"]:
                pipeline = self.dispatcher.discover_modules()
        
        # Execute the pipeline
        self.logger.info(f"Executing pipeline: {pipeline_name or 'default'}")
        result = self.dispatcher.execute_pipeline(enriched_input, pipeline)
        
        # Update agent state if the result contains state updates
        if "_agent_state_update" in result:
            self.state.update(result["_agent_state_update"])
            del result["_agent_state_update"]
        
        return result
    
    def add_module_to_pipeline(self, module_name: str, pipeline_name: str = "default") -> None:
        """
        Add a module to a pipeline.
        
        Args:
            module_name: Name of the module to add
            pipeline_name: Name of the pipeline to add to
        """
        if pipeline_name not in self.pipelines:
            self.pipelines[pipeline_name] = []
        
        if module_name not in self.pipelines[pipeline_name]:
            self.pipelines[pipeline_name].append(module_name)
            self.logger.info(f"Added module {module_name} to pipeline {pipeline_name}")
    
    def remove_module_from_pipeline(self, module_name: str, pipeline_name: str = "default") -> None:
        """
        Remove a module from a pipeline.
        
        Args:
            module_name: Name of the module to remove
            pipeline_name: Name of the pipeline to remove from
        """
        if pipeline_name in self.pipelines and module_name in self.pipelines[pipeline_name]:
            self.pipelines[pipeline_name].remove(module_name)
            self.logger.info(f"Removed module {module_name} from pipeline {pipeline_name}")
    
    def register_pipeline(self, pipeline_name: str, modules: List[str]) -> None:
        """
        Register a new pipeline with the specified modules.
        
        Args:
            pipeline_name: Name of the pipeline
            modules: List of module names in execution order
        """
        self.pipelines[pipeline_name] = modules.copy()
        self.logger.info(f"Registered pipeline {pipeline_name} with modules: {', '.join(modules)}")
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current agent state.
        
        Returns:
            The current state dictionary
        """
        return self.state.copy()
    
    def update_state(self, state_update: Dict[str, Any]) -> None:
        """
        Update the agent state.
        
        Args:
            state_update: Dictionary of state updates
        """
        self.state.update(state_update)
    
    def shutdown(self) -> None:
        """
        Shutdown the agent and clean up resources.
        """
        if self.running:
            self.logger.info("Shutting down agent")
            self.dispatcher.close()
            self.running = False