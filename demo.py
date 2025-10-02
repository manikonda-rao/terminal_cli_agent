#!/usr/bin/env python3
"""
Demo script for the Terminal Coding Agent.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.agent import CodingAgent
from src.core.models import AgentConfig


def demo_basic_functionality():
    """Demonstrate basic functionality of the coding agent."""
    print("Terminal Coding Agent Demo")
    print("=" * 50)
    
    # Initialize agent
    config = AgentConfig(
        llm_provider="openai",  # Will fallback to mock if no API key
        model_name="gpt-4"
    )
    
    agent = CodingAgent(".", config)
    
    # Demo scenarios
    demo_scenarios = [
        "Create a Python function for quicksort",
        "Modify the last function to handle empty lists",
        "Run the last function with [3, 1, 4, 1, 5, 9, 2, 6]",
        "Create a class for a binary tree node",
        "Search for 'def quicksort'"
    ]
    
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\nDemo {i}: {scenario}")
        print("-" * 40)
        
        try:
            turn = agent.process_input(scenario)
            
            if turn.success:
                print("Success!")
            else:
                print(f"Failed: {turn.error_message}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    # Show final status
    print("\nFinal Project Status:")
    print("-" * 40)
    status = agent.get_project_status()
    print(f"Active files: {len(status['active_files'])}")
    print(f"Total turns: {status['conversation_stats']['total_turns']}")
    print(f"Success rate: {status['conversation_stats']['success_rate']:.1%}")


if __name__ == "__main__":
    demo_basic_functionality()
