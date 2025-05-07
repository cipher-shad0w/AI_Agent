#!/usr/bin/env python3
import argparse
import logging
import os
import signal
import sys
import yaml
from typing import Any, Dict, Optional

from core.agent import Agent


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
        return config
    except Exception as e:
        logging.error(f"Error loading config from {config_path}: {e}")
        sys.exit(1)


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
        
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main() -> None:
    """
    Main entry point for the AI Agent.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AI Agent')
    parser.add_argument('-c', '--config', default='config.yaml', 
                      help='Path to configuration file')
    parser.add_argument('-l', '--log-level', default=None, 
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      help='Logging level')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Setup logging
    log_level = args.log_level or config.get('log_level', 'INFO')
    setup_logging(log_level)
    
    # Create the agent
    logging.info("Starting AI Agent")
    agent = Agent(config)
    
    # Set up signal handling for graceful shutdown
    def signal_handler(sig, frame):
        logging.info("Shutdown signal received")
        agent.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize the agent
        agent.initialize()
        
        # Example of processing data through a pipeline
        # result = agent.process({"input": "example data"}, "default")
        # print(result)
        
        # In a real application, you might run a server here or process inputs in a loop
        logging.info("Agent is running. Press Ctrl+C to exit.")
        
        # Example of a simple interactive mode
        while True:
            try:
                user_input = input("Input (or 'exit' to quit): ")
                if user_input.lower() == 'exit':
                    break
                    
                result = agent.process({"user_input": user_input})
                print("Result:", result)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.error(f"Error processing input: {e}")
                
    except Exception as e:
        logging.error(f"Error during agent execution: {e}")
    finally:
        agent.shutdown()
        logging.info("AI Agent stopped")


if __name__ == "__main__":
    main()