#!/usr/bin/env python3
"""
Example script demonstrating the Interactive Code Execution Panel.
This script shows how to use both the terminal-based and web-based execution panels.
"""

import os
import sys
import time
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.models import AgentConfig
from src.core.execution_panel import InteractiveExecutionPanel, ExecutionPanelConfig
from src.core.web_execution_panel import WebExecutionPanel


def create_demo_config():
    """Create a demo configuration for the execution panel."""
    return AgentConfig(
        llm_provider="openai",
        model_name="gpt-4",
        openai_api_key=os.getenv("OPENAI_API_KEY", "demo-key"),
        max_execution_time=30,
        max_memory_mb=512,
        sandbox_timeout=60,
        enable_syntax_highlighting=True,
        enable_autocomplete=True,
        security_level="moderate",
        execution_mode="auto"
    )


def demo_terminal_panel():
    """Demonstrate the terminal-based execution panel."""
    print("🚀 Terminal-Based Execution Panel Demo")
    print("=" * 50)
    
    config = create_demo_config()
    panel_config = ExecutionPanelConfig(
        max_history_size=20,
        auto_clear_output=False,
        show_line_numbers=True,
        enable_syntax_highlighting=True,
        default_language="python",
        theme="auto",
        panel_height=15,
        max_output_lines=500,
        enable_animations=True
    )
    
    panel = InteractiveExecutionPanel(config, panel_config)
    
    # Set some demo code
    demo_code = '''# Demo Python code
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"fibonacci({i}) = {fibonacci(i)}")'''
    
    panel.set_code(demo_code)
    panel.set_language("python")
    
    print("Demo code set. You can now interact with the panel.")
    print("Try running the code or modifying it!")
    
    try:
        panel.show_panel()
    except KeyboardInterrupt:
        print("\nDemo terminated by user.")
    finally:
        panel.cleanup()


def demo_web_panel():
    """Demonstrate the web-based execution panel."""
    print("🌐 Web-Based Execution Panel Demo")
    print("=" * 50)
    
    config = create_demo_config()
    
    print("Starting web server...")
    print("The panel will be available at http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    
    try:
        web_panel = WebExecutionPanel(config, "127.0.0.1", 5000)
        web_panel.run(debug=False)
    except KeyboardInterrupt:
        print("\nWeb panel stopped by user.")
    finally:
        web_panel.cleanup()


def demo_execution_features():
    """Demonstrate various execution features."""
    print("🔧 Execution Features Demo")
    print("=" * 50)
    
    config = create_demo_config()
    panel = InteractiveExecutionPanel(config)
    
    # Demo different languages
    demos = {
        "python": '''# Python demo
import math
print(f"π = {math.pi}")
print(f"√2 = {math.sqrt(2)}")''',
        
        "javascript": '''// JavaScript demo
function greet(name) {
    return `Hello, ${name}!`;
}
console.log(greet("World"));''',
        
        "bash": '''#!/bin/bash
# Bash demo
echo "Current directory: $(pwd)"
echo "Date: $(date)"
echo "User: $(whoami)"''',
        
        "cpp": '''// C++ demo
#include <iostream>
#include <vector>
int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    for (int n : numbers) {
        std::cout << n << " ";
    }
    std::cout << std::endl;
    return 0;
}'''
    }
    
    print("Available demo languages:")
    for i, lang in enumerate(demos.keys(), 1):
        print(f"  {i}. {lang}")
    
    print("\nSelect a language to demo (1-4), or press Enter to skip:")
    choice = input().strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(demos):
        lang = list(demos.keys())[int(choice) - 1]
        code = demos[lang]
        
        print(f"\nDemo code for {lang}:")
        print("-" * 30)
        print(code)
        print("-" * 30)
        
        panel.set_language(lang)
        panel.set_code(code)
        
        print(f"\nCode set for {lang}. You can now run it in the panel.")
        print("Press Enter to continue to the panel...")
        input()
        
        try:
            panel.show_panel()
        except KeyboardInterrupt:
            print("\nDemo terminated by user.")
        finally:
            panel.cleanup()
    else:
        print("Demo skipped.")


def main():
    """Main demo function."""
    print("🎯 Interactive Code Execution Panel Demo")
    print("=" * 60)
    print()
    
    print("Choose a demo:")
    print("1. Terminal-based execution panel")
    print("2. Web-based execution panel")
    print("3. Execution features demo")
    print("4. Exit")
    print()
    
    while True:
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            demo_terminal_panel()
            break
        elif choice == "2":
            demo_web_panel()
            break
        elif choice == "3":
            demo_execution_features()
            break
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")
    
    print("\nDemo completed!")


if __name__ == "__main__":
    main()
