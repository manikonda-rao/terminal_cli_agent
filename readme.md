# Terminal Coding Agent

A production-ready command-line interface that transforms natural language instructions into executable code through advanced AI integration. Engineered for professional development workflows with enterprise-grade reliability and security.

<img width="685" height="254" alt="Screenshot 2025-10-02 at 3 42 05 PM" src="https://github.com/user-attachments/assets/d01dae83-a8e4-4c68-a297-1c7006cd87c9" />


## Core Capabilities

- **Advanced Intent Recognition**: Sophisticated natural language processing engine that accurately interprets developer requirements and translates them into actionable code generation tasks
- **Intelligent Code Synthesis**: High-quality code generation powered by state-of-the-art language models with support for multiple programming languages and frameworks
- **Secure Execution Environment**: Enterprise-grade sandboxed execution with comprehensive resource management, process isolation, and security controls
- **Intelligent File Management**: Automated file operations with version control integration, backup systems, and rollback capabilities
- **Contextual Memory System**: Persistent conversation state management that maintains project context and development history across sessions
- **Professional CLI Interface**: Feature-rich terminal interface with syntax highlighting, intelligent autocompletion, and real-time progress monitoring
- **Integrated Version Control**: Seamless Git integration with automated commit management and branch operations
- **Project State Persistence**: Comprehensive project state tracking with conversation history and development context preservation

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

# Launch with Daytona sandboxing (requires DAYTONA_API_KEY)
EXECUTION_MODE=daytona python -m src.cli.main

# Launch with E2B sandboxing (requires E2B_API_KEY)
EXECUTION_MODE=e2b python -m src.cli.main

# Launch with Docker sandboxing
EXECUTION_MODE=docker python -m src.cli.main

# Launch with multi-language executor
EXECUTION_MODE=multi python -m src.cli.main

# Launch with auto-executor selection
EXECUTION_MODE=auto python -m src.cli.main
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
    enable_autocomplete=True,
    # Security Configuration
    security_level="moderate",    # strict, moderate, permissive, custom
    security_policy_file="security_policy.json",
    enable_security_scanning=True,
    enable_code_analysis=True,
    enable_resource_monitoring=True,
    # Execution Configuration
    execution_mode="auto",        # auto, sandbox, docker, e2b, daytona, multi
    preferred_executor=None      # Override auto-selection
)
```

## Security Policy Configuration

The agent supports flexible security policy configuration through JSON files:

### Security Levels

- **Strict**: Maximum security with minimal permissions
- **Moderate**: Balanced security with reasonable permissions (default)
- **Permissive**: Minimal restrictions for development
- **Custom**: User-defined security policies

### Security Policy File

Create a `security_policy.json` file to customize security settings:

```json
{
  "security_level": "moderate",
  "network_policy": "restricted",
  "file_system": {
    "read_only_dirs": ["/app/data", "/usr/lib"],
    "read_write_dirs": ["/tmp", "/app/logs"],
    "blocked_dirs": ["/etc", "/root", "/home"],
    "max_file_size_mb": 100
  },
  "resource_limits": {
    "cpu_limit": "1",
    "memory_limit_mb": 512,
    "execution_timeout": 30,
    "max_output_size_mb": 10,
    "max_processes": 5
  },
  "patterns": {
    "dangerous_patterns": ["import\\s+os", "subprocess\\.run"],
    "allowed_patterns": ["import\\s+math", "import\\s+json"],
    "custom_patterns": []
  },
  "enable_code_analysis": true,
  "enable_security_scanning": true,
  "enable_resource_monitoring": true,
  "sandbox_mode": "auto"
}
```

### Executor Selection

The agent automatically selects the best executor based on security level:

- **Strict**: Prefers Daytona → E2B → Docker
- **Moderate**: Prefers Docker → Daytona → E2B → Sandbox
- **Permissive**: Uses Multi-language executor

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

- **Sandboxed execution**: Code runs in isolated environment with multiple security layers
- **Daytona Integration**: Cloud-based sandboxing with enterprise-grade security
- **E2B Integration**: Advanced cloud-based sandboxing for maximum security
- **Docker Containers**: Process isolation with configurable security policies and resource limits
- **Configurable Security Policies**: Flexible security configuration with predefined levels (strict, moderate, permissive) and custom policies
- **Static Code Analysis**: Automated security scanning using Bandit and custom analyzers
- **Resource limits**: CPU time and memory restrictions with monitoring
- **Process isolation**: Prevents system access and malicious code execution
- **Automatic cleanup**: Temporary files and processes are cleaned up
- **Error handling**: Graceful failure with detailed error messages
- **Security Scanning**: Real-time detection of dangerous patterns and vulnerabilities

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

