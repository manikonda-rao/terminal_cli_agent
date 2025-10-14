#!/usr/bin/env fish
# POGO - Terminal CLI Agent Launcher
# A fish shell script to launch the POGO Terminal Coding Agent

function pogo --description "Launch POGO - Terminal CLI Agent"
    # Default project directory (can be overridden with POGO_PROJECT_DIR)
    set project_dir $POGO_PROJECT_DIR
    if test -z "$project_dir"
        set project_dir "/Users/shraddharao/Development/code/Work/headstarter/terminal_cli"
    end
    
    # Change to the project directory
    if not test -d "$project_dir"
        echo "❌ Error: Project directory not found: $project_dir"
        echo "Please set POGO_PROJECT_DIR environment variable to the correct path"
        return 1
    end
    
    cd $project_dir
    
    # Check if Python is available
    if not command -v python3 >/dev/null 2>&1
        echo "❌ Error: Python 3 is not installed or not in PATH"
        echo "Please install Python 3.8+ to use Pogo"
        return 1
    end
    
    # Check Python version
    set python_version (python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    set major_version (echo $python_version | cut -d. -f1)
    set minor_version (echo $python_version | cut -d. -f2)
    
    if test $major_version -lt 3 -o \( $major_version -eq 3 -a $minor_version -lt 8 \)
        echo "❌ Error: Python 3.8+ is required, but found Python $python_version"
        echo "Please upgrade Python to version 3.8 or higher"
        return 1
    end
    
    # Check if virtual environment exists
    if test -d "venv" -o -d ".venv"
        echo "🐍 Activating virtual environment..."
        if test -d "venv"
            source venv/bin/activate.fish
        else if test -d ".venv"
            source .venv/bin/activate.fish
        end
    end
    
    # Check if dependencies are installed
    if not python3 -c "import rich, prompt_toolkit, openai" >/dev/null 2>&1
        echo "📦 Installing dependencies..."
        if test -f "requirements.txt"
            pip install -r requirements.txt
        else
            echo "❌ Error: requirements.txt not found"
            return 1
        end
    end
    
    # Check for .env file
    if not test -f ".env"
        if test -f "env.example"
            echo "📝 Creating .env file from template..."
            cp env.example .env
            echo "⚠️  Please edit .env file with your API keys before using Pogo"
        else
            echo "⚠️  Warning: No .env file found. You may need to set API keys manually."
        end
    end
    
    # Display welcome message
    echo ""
    echo "🐠 POGO - Launching POGO Terminal CLI Agent"
    echo "=============================================="
    echo ""
    
    # Launch the CLI agent with any passed arguments
    python3 -m src.cli.main $argv
end

# Make the function available globally
functions -e pogo