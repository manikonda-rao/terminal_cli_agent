# POGO Terminal CLI Agent

A production-ready command-line interface that transforms natural language instructions into executable code through advanced AI integration.

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🐠  ██████╗  ██████╗  ██████╗  ██████╗   🐠           ║
║       ██╔══██╗██╔═══██╗██╔═══██╗██╔═══██╗                  ║
║       ██████╔╝██║   ██║██║   ██║██║   ██║                  ║
║       ██╔═══╝ ██║   ██║██║ ██╗██║██║   ██║                  ║
║       ██║     ╚██████╔╝╚██████╔╝╚██████╔╝                  ║
║       ╚═╝      ╚═════╝  ╚═════╝  ╚═════╝                   ║
║                                                              ║
║              AI-Powered Terminal Coding Assistant            ║
║      Generate, modify, and execute code with natural language║
║          Safe execution in sandboxed environments            ║
║        Intelligent file management with version control      ║
║        Persistent conversation context and project state     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

## Quick Start

### Installation

```bash
# Clone and setup
git clone https://github.com/your-org/terminal_cli.git
cd terminal_cli
pip install -r requirements.txt

# Configure API keys (optional)
cp env.example .env
# Edit .env with your OpenAI or Anthropic API keys

# Launch POGO
python -m src.cli.main
```

### Using POGO Launcher Scripts

**Fish Shell:**
```bash
fish install_pogo.fish  # Install globally
pogo                    # Launch POGO
```

**Bash/Zsh:**
```bash
./pogo.sh              # Launch POGO
```

## Usage Examples

```bash
# Create code
> Create a Python function for quicksort
> Write a class for a linked list node
> Implement a stack data structure

# Modify existing code
> Modify the last function to handle edge cases
> Change the sorting algorithm to use merge sort

# Execute and test
> Run the last function with test data
> Test the binary search with [1, 3, 5, 7, 9]

# File management
> Create a file called utils.py
> Search for "def quicksort"

# Special commands
> /help          # Show help
> /status        # Show project status
> /execution-panel  # Interactive code execution
> /web-panel      # Web-based execution panel
> /quit          # Exit
```

## Interactive Code Execution

POGO includes powerful execution panels for running code directly:

```bash
# Terminal-based panel
/execution-panel

# Web-based panel (localhost:5000)
/web-panel
```

**Supported Languages:** Python, JavaScript, TypeScript, Java, C++, Rust, Go, PHP, Ruby, Perl, Bash

**Features:**
- Real-time output streaming
- Secure sandboxed execution
- Multi-language support
- Resource limits and timeout protection
- Execution history

## Configuration

```python
from src.core.models import AgentConfig

config = AgentConfig(
    llm_provider="openai",        # or "anthropic"
    model_name="gpt-4",          # or "claude-3-sonnet"
    max_execution_time=30,       # Execution timeout
    max_memory_mb=512,           # Memory limit
    enable_syntax_highlighting=True,
    enable_autocomplete=True
)
```

## Architecture

```
terminal_cli/
├── src/
│   ├── cli/           # Interactive CLI interface
│   ├── core/          # Core agent logic and models
│   ├── execution/     # Sandboxed execution engine
│   └── memory/        # Conversation and project state
├── pogo.fish          # Fish shell launcher
├── pogo.sh            # Bash shell launcher
├── install_pogo.fish  # Installation script
└── requirements.txt   # Dependencies
```

## Security Features

- **Sandboxed execution**: Code runs in isolated environments
- **Resource limits**: CPU time and memory restrictions
- **Process isolation**: Prevents system access
- **Automatic cleanup**: Temporary files and processes cleaned up

## Documentation

- [EXAMPLES.md](EXAMPLES.md) - Comprehensive usage examples
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines
- [ROADMAP.md](ROADMAP.md) - Development roadmap

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.