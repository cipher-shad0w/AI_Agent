# AI Agent Framework

A modular, extensible AI agent framework that allows for easy addition of new modules.

## Overview

This framework provides a robust architecture for creating AI-driven agents with modular capabilities. The system is designed around these core components:

- **Agent**: The central component that manages state and orchestrates module execution
- **Dispatcher**: Handles dynamic loading and execution of modules
- **Modules**: Individual components that provide specific functionality

## Getting Started

### Requirements

- Python 3.6+
- PyYAML

Install requirements:

```bash
pip install pyyaml
```

### Running the Agent

1. Configure your agent in `config.yaml`
2. Run the agent:

```bash
python main.py
```

Or with a custom config file:

```bash
python main.py --config my_config.yaml
```

## Creating Modules

To create a new module, add a Python file in the `modules` directory that contains a class inheriting from `ModuleBase`. The agent will automatically discover and load your module.

Example module:

```python
from core.module_base import ModuleBase
from typing import Any, Dict

class ExampleModule(ModuleBase):
    """An example module that demonstrates the module structure."""
    
    def initialize(self) -> None:
        """Optional initialization logic."""
        self.counter = 0
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return a result."""
        # Access module configuration
        prefix = self.module_config.get('prefix', 'Result')
        
        # Access input
        user_input = input_data.get('user_input', '')
        
        # Access agent state
        agent_state = input_data.get('_agent_state', {})
        
        # Process the input
        self.counter += 1
        result = f"{prefix}: Processed '{user_input}' (count: {self.counter})"
        
        # Return processed result
        return {
            'result': result,
            # Optionally update agent state
            '_agent_state_update': {
                'last_processed_by': self.name,
                'last_input': user_input
            }
        }
```

## Configuration

The `config.yaml` file contains all the configuration for the agent and its modules:

- **log_level**: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **auto_discover**: When true, automatically use all available modules when no pipeline is specified
- **preload_modules**: List of modules to load during initialization
- **modules**: Module-specific configuration
- **pipelines**: Define processing pipelines as ordered lists of modules

## Pipelines

Pipelines define the sequence of modules to process input data:

```yaml
pipelines:
  text_processing:
    - text_tokenizer
    - sentiment_analyzer
    - response_generator
```

Use pipelines when processing data:

```python
result = agent.process({"text": "Hello, world!"}, "text_processing")
```

## Advanced Usage

### Creating Custom Pipelines at Runtime

```python
agent.register_pipeline("custom_pipeline", ["module1", "module2", "module3"])
```

### Modifying Pipelines

```python
# Add a module to a pipeline
agent.add_module_to_pipeline("new_module", "my_pipeline")

# Remove a module from a pipeline
agent.remove_module_from_pipeline("some_module", "my_pipeline")
```

### Managing Agent State

The agent maintains state that persists across module executions:

```python
# Get the current state
state = agent.get_state()

# Update the state
agent.update_state({"key": "value"})
```

## Architecture

```
AI_Agent/
├── config.yaml          # Configuration file
├── main.py              # Main entry point
├── core/
│   ├── agent.py         # Core agent class
│   ├── dispatcher.py    # Module loader and pipeline executor
│   └── module_base.py   # Base class for modules
└── modules/
    ├── module1.py       # Example module
    └── module2.py       # Example module
```

## Best Practices

1. Keep modules focused on a single responsibility
2. Use pipelines to create complex behaviors from simple modules
3. Leverage agent state to share information between modules
4. Add proper logging to modules for debugging
5. Include comprehensive documentation in module classes
