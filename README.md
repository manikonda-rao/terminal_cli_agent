# 🤖 Terminal-Based Coding Agent

A sophisticated CLI tool that accepts natural language instructions and translates them into code edits and execution steps. Built with Python and designed for developers who want to code through conversation.

## ✨ Features

- **🧠 Natural Language Processing**: Parse user instructions into structured intents with high accuracy
- **⚡ Code Generation**: Generate clean, well-documented code using LLM integration (OpenAI, Anthropic)
- **🛡️ Safe Execution**: Sandboxed code execution with resource limits and process isolation
- **📁 File Management**: Create, edit, and version code files with automatic backups and rollback
- **💬 Multi-turn Conversations**: Maintain conversational memory and context across interactions
- **🎨 Interactive CLI**: Rich terminal interface with syntax highlighting, autocompletion, and progress indicators
- **🔄 Version Control**: Automatic git integration and backup management
- **📊 Project State**: Persistent project state and conversation history

## 🏗️ Architecture

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

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd terminal_cli

# Install dependencies
pip install -r requirements.txt

# Set up environment (optional)
cp env.example .env
# Edit .env with your API keys
```

### 2. Run the Agent

```bash
# Start the interactive CLI
python -m src.cli.main

# Or run with custom configuration
python -m src.cli.main --llm-provider anthropic --model claude-3-sonnet
```

### 3. Start Coding!

```
> Create a Python function for quicksort
> Modify the last function to handle empty lists
> Run the last function with [3, 1, 4, 1, 5]
> Search for "def quicksort"
> /status
```

## 📖 Usage Examples

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

## 🧪 Testing

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

## ⚙️ Configuration

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

## 🔧 Supported Languages

- **Python** (primary)
- **JavaScript/TypeScript**
- **Java**
- **C++**
- **Rust**
- **Go**

## 🎯 Intent Types

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

## 🛡️ Security Features

- **Sandboxed execution**: Code runs in isolated environment
- **Resource limits**: CPU time and memory restrictions
- **Process isolation**: Prevents system access
- **Automatic cleanup**: Temporary files and processes are cleaned up
- **Error handling**: Graceful failure with detailed error messages

## 📚 Documentation

- [EXAMPLES.md](EXAMPLES.md) - Comprehensive usage examples
- [CONTRIBUTION.md](CONTRIBUTION.md) - Contributing guidelines
- [ROADMAP.md](ROADMAP.md) - Development roadmap and stretch goals
- [requirements.txt](requirements.txt) - Dependencies
- [env.example](env.example) - Environment configuration template

## 🎯 Stretch Goals

### Phase 1: Enhanced Intelligence
- **🧠 Multi-Modal Input**: Voice commands and image-based code generation
- **📖 Advanced Code Explanation**: Detailed algorithm explanations with visualizations
- **⚡ Performance Optimization**: Automatic code optimization suggestions
- **🐛 Intelligent Bug Detection**: Pre-execution bug identification and fixes

### Phase 2: Advanced Features
- **👥 Collaborative Coding**: Multi-user real-time coding sessions
- **🔍 Automated Code Review**: AI-powered code review with suggestions
- **🔄 Smart Refactoring**: Intelligent code refactoring recommendations
- **🧪 Test Generation**: Automatic unit test generation from code analysis

### Phase 3: Ecosystem Integration
- **🔌 IDE Extensions**: VS Code, PyCharm, IntelliJ plugins
- **🚀 CI/CD Integration**: GitHub Actions, GitLab CI, Jenkins support
- **☁️ Cloud Deployment**: Deploy and run code in cloud environments
- **🌐 API Generation**: REST APIs from natural language descriptions

### Phase 4: Advanced AI Capabilities
- **🔄 Code Translation**: Multi-language code translation
- **🏗️ Architecture Design**: System architecture from requirements
- **🗄️ Database Design**: Database schemas from natural language
- **🔧 Microservices**: Microservice architecture generation

### Phase 5: Enterprise Features
- **👥 Team Management**: User roles, permissions, collaboration
- **📊 Audit Logging**: Comprehensive logging and compliance
- **🛡️ Security Compliance**: SOC2, HIPAA, industry standards
- **📈 Scalability**: Horizontal scaling and load balancing

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTION.md](CONTRIBUTION.md) for detailed guidelines.

### Quick Contribution Areas
- 🐛 **Bug Fixes**: Intent parsing, error handling, cross-platform issues
- ✨ **New Features**: Additional LLM providers, languages, intent types
- 🧪 **Testing**: Unit tests, integration tests, performance benchmarks
- 📚 **Documentation**: Tutorials, API docs, video demos
- 🔌 **Integrations**: IDE plugins, CI/CD, cloud deployment

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test them
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 🎉 What's Next?

This terminal coding agent showcases the future of AI-assisted development:

- Natural language programming interfaces
- Context-aware code generation
- Safe execution environments
- Intelligent project management
- Conversational development workflows

Try it out and experience the future of coding! 🚀
# terminal_cli_agent
