#!/usr/bin/env python3
"""
Test script for the Terminal Coding Agent.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.models import AgentConfig, IntentType, CodeLanguage
from src.core.intent_parser import IntentParser


def test_intent_parser():
    """Test the intent parsing functionality."""
    print("🧪 Testing Intent Parser")
    print("=" * 30)
    
    parser = IntentParser()
    
    test_cases = [
        "Create a Python function for quicksort",
        "Modify the last function to handle empty lists",
        "Run the last function with test data",
        "Write a class for binary tree",
        "Search for quicksort function",
        "Explain the last function",
        "Delete the file test.py"
    ]
    
    for test_input in test_cases:
        print(f"\nInput: {test_input}")
        intent = parser.parse(test_input)
        print(f"Intent: {intent.type.value}")
        print(f"Confidence: {intent.confidence:.2f}")
        print(f"Language: {intent.language.value if intent.language else 'None'}")
        print(f"Parameters: {intent.parameters}")


def test_models():
    """Test the data models."""
    print("\n🧪 Testing Data Models")
    print("=" * 30)
    
    # Test AgentConfig
    config = AgentConfig()
    print(f"Config: {config.llm_provider}, {config.model_name}")
    
    # Test IntentType and CodeLanguage enums
    print(f"Intent types: {[t.value for t in IntentType]}")
    print(f"Languages: {[l.value for l in CodeLanguage]}")


if __name__ == "__main__":
    test_intent_parser()
    test_models()
    print("\n✅ Tests completed!")
