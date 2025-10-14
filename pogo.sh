#!/bin/bash
# POGO - Terminal CLI Agent Launcher (Bash version)
# A bash script to launch the POGO Terminal Coding Agent

# Default project directory (can be overridden with POGO_PROJECT_DIR)
PROJECT_DIR="${POGO_PROJECT_DIR:-/Users/shraddharao/Development/code/Work/headstarter/terminal_cli}"

# Change to the project directory
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Error: Project directory not found: $PROJECT_DIR"
    echo "Please set POGO_PROJECT_DIR environment variable to the correct path"
    exit 1
fi

cd "$PROJECT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ to use POGO"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ $MAJOR_VERSION -lt 3 ] || ([ $MAJOR_VERSION -eq 3 ] && [ $MINOR_VERSION -lt 8 ]); then
    echo "❌ Error: Python 3.8+ is required, but found Python $PYTHON_VERSION"
    echo "Please upgrade Python to version 3.8 or higher"
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ] || [ -d ".venv" ]; then
    echo "🐍 Activating virtual environment..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
fi

# Check if dependencies are installed
if ! python3 -c "import rich, prompt_toolkit, openai" &> /dev/null; then
    echo "📦 Installing dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo "❌ Error: requirements.txt not found"
        exit 1
    fi
fi

# Check for .env file
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        echo "📝 Creating .env file from template..."
        cp env.example .env
        echo "⚠️  Please edit .env file with your API keys before using Pogo"
    else
        echo "⚠️  Warning: No .env file found. You may need to set API keys manually."
    fi
fi

# Display welcome message
echo ""
echo "🐠 POGO - Launching POGO Terminal CLI Agent"
echo "=============================================="
echo ""

# Launch the CLI agent with any passed arguments
python3 -m src.cli.main "$@"
