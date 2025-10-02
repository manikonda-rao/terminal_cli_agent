#!/usr/bin/env python3
"""
Simple demo script for the Terminal Coding Agent (no external dependencies).
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.models import AgentConfig, IntentType, CodeLanguage
from src.core.intent_parser import IntentParser


def demo_intent_parsing():
    """Demonstrate natural language intent parsing capabilities."""
    print("Terminal Coding Agent - Intent Parsing Demonstration")
    print("=" * 65)
    
    parser = IntentParser()
    
    demo_scenarios = [
        "Create a Python function for quicksort",
        "Modify the last function to handle empty lists", 
        "Run the last function with [3, 1, 4, 1, 5]",
        "Write a class for binary tree node",
        "Search for 'def quicksort'",
        "Explain the last function",
        "Debug the sorting algorithm",
        "Create a file called utils.py"
    ]
    
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\nTest Case {i}: {scenario}")
        print("-" * 60)
        
        intent = parser.parse(scenario)
        
        print(f"Detected Intent: {intent.type.value}")
        print(f"Confidence Score: {intent.confidence:.2f}")
        print(f"Target Language: {intent.language.value if intent.language else 'Not specified'}")
        print(f"Extracted Parameters: {intent.parameters}")
        
        # Display intended system action
        if intent.type == IntentType.CREATE_FUNCTION:
            print("System Action: Generate Python function implementation")
        elif intent.type == IntentType.CREATE_CLASS:
            print("System Action: Generate Python class structure")
        elif intent.type == IntentType.MODIFY_CODE:
            print("System Action: Modify existing codebase")
        elif intent.type == IntentType.RUN_CODE:
            print("System Action: Execute code with provided test data")
        elif intent.type == IntentType.SEARCH_CODE:
            print("System Action: Perform codebase search operation")
        elif intent.type == IntentType.EXPLAIN_CODE:
            print("System Action: Generate comprehensive code explanation")
        elif intent.type == IntentType.DEBUG_CODE:
            print("System Action: Debug and resolve code issues")
        elif intent.type == IntentType.CREATE_FILE:
            print("System Action: Create new project file")
        else:
            print("System Action: Process development request")


def demo_configuration():
    """Demonstrate system configuration capabilities."""
    print("\n\nConfiguration Management Demonstration")
    print("=" * 45)
    
    # Default configuration
    config = AgentConfig()
    print("Default Configuration:")
    print(f"  LLM Provider: {config.llm_provider}")
    print(f"  Model: {config.model_name}")
    print(f"  Temperature: {config.temperature}")
    print(f"  Max Tokens: {config.max_tokens}")
    print(f"  Max Execution Time: {config.max_execution_time}s")
    print(f"  Max Memory: {config.max_memory_mb}MB")
    
    # Custom configuration
    custom_config = AgentConfig(
        llm_provider="anthropic",
        model_name="claude-3-sonnet",
        temperature=0.2,
        max_execution_time=60
    )
    print("\nCustom Configuration:")
    print(f"  LLM Provider: {custom_config.llm_provider}")
    print(f"  Model: {custom_config.model_name}")
    print(f"  Temperature: {custom_config.temperature}")
    print(f"  Max Execution Time: {custom_config.max_execution_time}s")


def demo_supported_features():
    """Demonstrate supported features."""
    print("\n\nSupported Features")
    print("=" * 30)
    
    print("Intent Types:")
    for intent_type in IntentType:
        print(f"  • {intent_type.value}")
    
    print("\nProgramming Languages:")
    for language in CodeLanguage:
        print(f"  • {language.value}")
    
    print("\nCore Capabilities:")
    capabilities = [
        "Natural language intent parsing",
        "Code generation with LLM integration", 
        "Sandboxed code execution",
        "File management with versioning",
        "Conversation memory and context",
        "Interactive CLI interface",
        "Rollback and recovery",
        "Project state persistence"
    ]
    
    for capability in capabilities:
        print(f"  • {capability}")


def main():
    """Main demo function."""
    demo_intent_parsing()
    demo_configuration()
    demo_supported_features()
    
    print("\n\nDemonstration completed successfully!")
    print("\nTo deploy the full system:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Configure API credentials in .env file")
    print("3. Launch interface: python -m src.cli.main")
    print("\nFor comprehensive documentation, refer to README.md")


if __name__ == "__main__":
    main()
