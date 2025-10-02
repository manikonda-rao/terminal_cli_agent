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
    """Demonstrate core functionality of the Terminal Coding Agent."""
    print("Terminal Coding Agent - Core Functionality Demonstration")
    print("=" * 60)
    
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
        print(f"\nScenario {i}: {scenario}")
        print("-" * 50)
        
        try:
            turn = agent.process_input(scenario)
            
            if turn.success:
                print("Status: Operation completed successfully")
            else:
                print(f"Status: Operation failed - {turn.error_message}")
                
        except Exception as e:
            print(f"System Error: {e}")
    
    # Display final project status
    print("\nProject Status Summary:")
    print("-" * 50)
    status = agent.get_project_status()
    print(f"Active Files: {len(status['active_files'])}")
    print(f"Total Interactions: {status['conversation_stats']['total_turns']}")
    print(f"Success Rate: {status['conversation_stats']['success_rate']:.1%}")


if __name__ == "__main__":
    demo_basic_functionality()
