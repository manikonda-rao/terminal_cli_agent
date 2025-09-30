#!/usr/bin/env python3
"""
Setup script for the Terminal Coding Agent.
"""

import os
import sys
import subprocess
from pathlib import Path


def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    return True


def setup_environment():
    """Setup environment variables."""
    print("🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your API keys")
    else:
        print("ℹ️ Environment file already exists or template not found")


def run_tests():
    """Run basic tests."""
    print("🧪 Running tests...")
    
    try:
        subprocess.check_call([sys.executable, "test.py"])
        print("✅ Tests passed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        return False
    
    return True


def run_demo():
    """Run demo."""
    print("🎬 Running demo...")
    
    try:
        subprocess.check_call([sys.executable, "demo.py"])
        print("✅ Demo completed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Demo failed: {e}")
        return False
    
    return True


def main():
    """Main setup function."""
    print("🚀 Terminal Coding Agent Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Run tests
    if not run_tests():
        print("⚠️ Tests failed, but continuing with setup...")
    
    # Run demo
    if not run_demo():
        print("⚠️ Demo failed, but setup completed...")
    
    print("\n🎉 Setup completed!")
    print("\nTo run the CLI:")
    print("  python -m src.cli.main")
    print("\nTo run the demo:")
    print("  python demo.py")
    print("\nTo run tests:")
    print("  python test.py")


if __name__ == "__main__":
    main()
