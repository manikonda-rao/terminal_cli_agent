# Terminal Coding Agent

A production-ready command-line interface that transforms natural language instructions into executable code through advanced AI integration. Engineered for professional development workflows with enterprise-grade reliability and security.

## Terminal Interface

The CLI features a clean, professional ASCII art interface with the distinctive "SUTRO" branding:

```
╔══════════════════════════════════════════════════════════════╗
║  ███████╗██╗   ██╗███████╗████████╗ ██████╗ ██████╗ ██╗     ║
║  ██╔════╝██║   ██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██║     ║
║  ███████╗██║   ██║█████╗     ██║   ██║   ██║██████╔╝██║     ║
║  ╚════██║██║   ██║██╔══╝     ██║   ██║   ██║██╔══██╗██║     ║
║  ███████║╚██████╔╝███████╗   ██║   ╚██████╔╝██║  ██║███████╗║
║  ╚══════╝ ╚═════╝ ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝║
║                                                              ║
║  AI-Powered Terminal Coding Assistant                        ║
║  Generate, modify, and execute code with natural language    ║
║  Safe execution in sandboxed environments                    ║
║  Intelligent file management with version control           ║
║  Persistent conversation context and project state          ║
╚══════════════════════════════════════════════════════════════╝
```

The interface provides a streamlined, emoji-free experience with:
- Clean ASCII art branding
- Professional terminal aesthetics
- Real-time streaming responses
- Intelligent autocompletion
- Syntax highlighting

## Interactive Code Execution Panel

The Terminal Coding Agent now includes a powerful interactive code execution panel that allows you to run code snippets directly within the interface with real-time output display.

### Features

- **Multi-Language Support**: Execute code in Python, JavaScript, TypeScript, Java, C++, Rust, Go, PHP, Ruby, Perl, and Bash
- **Real-Time Output**: See console output, logs, and errors as they happen
- **Secure Execution**: All code runs in sandboxed environments with resource limits
- **Execution History**: Maintain a history of executed commands with timestamps
- **Theme Support**: Toggle between light and dark themes for better readability
- **Keyboard Shortcuts**: Quick execution with Ctrl+Enter, stop with Ctrl+C, clear with Ctrl+L
- **Responsive Design**: Collapsible panels and resizable interface elements

### Two Interface Options

#### 1. Terminal-Based Panel (`/execution-panel`)
A rich terminal interface using the Rich library for beautiful formatting:

```bash
# Launch the terminal execution panel
/execution-panel
```

Features:
- Rich terminal UI with syntax highlighting
- Real-time output streaming
- Interactive command interface
- Execution history with timestamps
- Theme switching (light/dark)

#### 2. Web-Based Panel (`/web-panel`)
A modern web interface accessible through your browser:

```bash
# Launch the web execution panel
/web-panel
```

Features:
- Modern web UI with CodeMirror editor
- Real-time WebSocket communication
- Responsive design for desktop and mobile
- Copy/paste functionality
- Toast notifications
- Loading indicators
- Collapsible panels

### Usage Examples

```bash
# Terminal panel
/execution-panel

# Web panel (default: localhost:5000)
/web-panel

# Web panel on custom host/port
/web-panel 0.0.0.0 8080
```

### Supported Languages

The execution panel supports multiple programming languages with proper syntax highlighting and execution:

- **Python**: Full Python 3.x support with standard library
- **JavaScript**: Node.js runtime with ES6+ features
- **TypeScript**: Compiled to JavaScript before execution
- **Java**: Full Java compilation and execution
- **C++**: GCC compilation and execution
- **Rust**: Rustc compilation and execution
- **Go**: Go runtime execution
- **PHP**: PHP interpreter execution
- **Ruby**: Ruby interpreter execution
- **Perl**: Perl interpreter execution
- **Bash**: Shell script execution

### Security Features

- **Sandboxed Execution**: All code runs in isolated environments
- **Resource Limits**: Memory and CPU usage limits prevent system overload
- **Timeout Protection**: Automatic termination of long-running processes
- **Security Scanning**: Code analysis for potentially dangerous operations
- **Process Isolation**: Complete separation from the host system

### Keyboard Shortcuts

- `Ctrl+Enter`: Run current code
- `Ctrl+C`: Stop execution
- `Ctrl+L`: Clear output
- `Ctrl+Shift+T`: Toggle theme
- `Ctrl+Shift+E`: Toggle panel size (web panel)

### Demo

Try the interactive demo to see the execution panel in action:

```bash
python demo_execution_panel.py
```

This will launch an interactive demo showing both terminal and web-based execution panels with sample code in multiple languages.

## Architecture

```
terminal_cli/
├── src/
│   ├── cli/           # Interactive CLI interface
│   ├── core/          # Core agent logic and models
│   ├── execution/     # Sandboxed execution engine
│   ├── memory/        # Conversation and project state management
│   └── utils/         # Utilities and helpers
├── tests/             # Test suite
├── examples/          # Example usage scenarios
├── requirements.txt   # Python dependencies
├── setup.py          # Setup script
└── README.md         # This file
```

## Installation and Setup

### Prerequisites

Ensure your system meets the following requirements:
- Python 3.8 or higher
- Git (for version control integration)
- Terminal with UTF-8 support

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/terminal_cli.git
cd terminal_cli

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp env.example .env
# Edit .env with your API credentials
```

### Advanced Configuration

```bash
# Launch with specific model provider
python -m src.cli.main --llm-provider anthropic --model claude-3-sonnet

# Launch with OpenAI GPT-4
python -m src.cli.main --llm-provider openai --model gpt-4
```

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment (optional)
cp env.example .env
# Edit .env file with your API keys if you want to use real LLM providers

# 3. Run the application
python -m src.cli.main
```

### Basic Usage Examples

```
> Create a Python function for quicksort
> Modify the last function to handle empty lists
> Run the last function with [3, 1, 4, 1, 5]
> Search for "def quicksort"
> /status
```

### Demo Scripts

```bash
# Run basic demo
python demo.py

# Run intent parsing demo
python simple_demo.py

# Run tests
python test.py
```

## Usage Examples

### Basic Commands

```bash
# Create functions and classes
> Create a Python function for binary search
> Write a class for a linked list node
> Implement a stack data structure

# Modify existing code
> Modify the last function to handle edge cases
> Change the sorting algorithm to use merge sort
> Add error handling to the last function

# Execute and test
> Run the last function with test data
> Test the binary search with [1, 3, 5, 7, 9]
> Execute the stack with push/pop operations

# File management
> Create a file called utils.py
> Delete the file test.py
> Search for "def quicksort"

# Special commands
> /help          # Show help
> /status        # Show project status
> /rollback      # Rollback last operation
> /clear         # Clear project
> /export path   # Export project
> /quit          # Exit
```

### Advanced Features

- **Multi-turn conversations**: Reference "the last function" for modifications
- **Context awareness**: Agent remembers previous interactions
- **Automatic versioning**: Files are backed up before modifications
- **Safe execution**: Code runs in isolated environment with resource limits
- **Rich output**: Syntax highlighting, progress indicators, and formatted results

## Testing

```bash
# Run basic tests
python test.py

# Run simple demo (no external dependencies)
python simple_demo.py

# Run full demo (requires API keys)
python demo.py

# Run setup script
python setup.py
```

## Configuration

The agent supports extensive configuration options:

```python
from src.core.models import AgentConfig

config = AgentConfig(
    llm_provider="openai",        # or "anthropic"
    model_name="gpt-4",          # or "claude-3-sonnet"
    temperature=0.1,             # LLM creativity
    max_tokens=2000,             # Max response length
    max_execution_time=30,       # Execution timeout
    max_memory_mb=512,           # Memory limit
    enable_syntax_highlighting=True,
    enable_autocomplete=True
)
```

## Supported Languages

- **Python** (primary)
- **JavaScript/TypeScript**
- **Java**
- **C++**
- **Rust**
- **Go**

## Intent Types

The agent understands these types of requests:

- `create_function` - Generate new functions
- `create_class` - Generate new classes
- `modify_code` - Modify existing code
- `run_code` - Execute code with test data
- `create_file` - Create new files
- `delete_file` - Delete files
- `search_code` - Search through codebase
- `explain_code` - Explain existing code
- `refactor_code` - Refactor and optimize code
- `debug_code` - Debug and fix issues
- `test_code` - Generate test cases

## Security Features

- **Sandboxed execution**: Code runs in isolated environment
- **Resource limits**: CPU time and memory restrictions
- **Process isolation**: Prevents system access
- **Automatic cleanup**: Temporary files and processes are cleaned up
- **Error handling**: Graceful failure with detailed error messages

## Documentation

- [EXAMPLES.md](EXAMPLES.md) - Comprehensive usage examples
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines
- [ROADMAP.md](ROADMAP.md) - Development roadmap and stretch goals
- [requirements.txt](requirements.txt) - Dependencies
- [env.example](env.example) - Environment configuration template


## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines and development setup instructions.

## Roadmap

For our development roadmap, future features, and strategic vision, see [ROADMAP.md](ROADMAP.md).