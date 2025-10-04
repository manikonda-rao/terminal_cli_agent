#!/usr/bin/env python3
"""
Test script for the Interactive Code Execution Panel.
This script tests the basic functionality without requiring Flask dependencies.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.models import AgentConfig, CodeBlock, CodeLanguage
from src.core.execution_panel import InteractiveExecutionPanel, ExecutionPanelConfig


def test_execution_panel():
    """Test the execution panel functionality."""
    print("🧪 Testing Interactive Code Execution Panel")
    print("=" * 50)
    
    # Create test configuration
    config = AgentConfig(
        llm_provider="openai",
        model_name="gpt-4",
        openai_api_key="test-key",
        max_execution_time=10,
        max_memory_mb=256,
        sandbox_timeout=30,
        enable_syntax_highlighting=True,
        enable_autocomplete=True,
        security_level="moderate",
        execution_mode="sandbox"  # Use sandbox for testing
    )
    
    # Create panel configuration
    panel_config = ExecutionPanelConfig(
        max_history_size=10,
        auto_clear_output=False,
        show_line_numbers=True,
        enable_syntax_highlighting=True,
        default_language="python",
        theme="light",
        panel_height=10,
        max_output_lines=100,
        enable_animations=False  # Disable animations for testing
    )
    
    try:
        # Create execution panel
        panel = InteractiveExecutionPanel(config, panel_config)
        print("✅ Execution panel created successfully")
        
        # Test setting code
        test_code = '''print("Hello, World!")
print("Testing execution panel")'''
        panel.set_code(test_code)
        panel.set_language("python")
        print("✅ Code and language set successfully")
        
        # Test configuration
        stats = panel.get_execution_statistics()
        print(f"✅ Statistics retrieved: {stats}")
        
        # Test cleanup
        panel.cleanup()
        print("✅ Panel cleanup completed")
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_code_block():
    """Test CodeBlock creation."""
    print("\n🧪 Testing CodeBlock Creation")
    print("=" * 30)
    
    try:
        # Test Python code block
        python_code = CodeBlock(
            content='print("Hello, Python!")',
            language=CodeLanguage.PYTHON
        )
        print(f"✅ Python code block created: {python_code.language}")
        
        # Test JavaScript code block
        js_code = CodeBlock(
            content='console.log("Hello, JavaScript!");',
            language=CodeLanguage.JAVASCRIPT
        )
        print(f"✅ JavaScript code block created: {js_code.language}")
        
        return True
        
    except Exception as e:
        print(f"❌ CodeBlock test failed: {e}")
        return False


def test_configuration():
    """Test configuration creation."""
    print("\n🧪 Testing Configuration")
    print("=" * 25)
    
    try:
        # Test AgentConfig
        config = AgentConfig(
            llm_provider="openai",
            model_name="gpt-4",
            max_execution_time=30,
            security_level="moderate"
        )
        print(f"✅ AgentConfig created: {config.llm_provider}")
        
        # Test ExecutionPanelConfig
        panel_config = ExecutionPanelConfig(
            max_history_size=50,
            default_language="python",
            theme="dark"
        )
        print(f"✅ ExecutionPanelConfig created: {panel_config.theme}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Interactive Code Execution Panel Test Suite")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_configuration),
        ("CodeBlock Creation", test_code_block),
        ("Execution Panel", test_execution_panel)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The execution panel is ready to use.")
        print("\nTo try the execution panel:")
        print("1. Run the CLI: python -m src.cli.main")
        print("2. Use command: /execution-panel")
        print("3. Or try the web panel: /web-panel")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
