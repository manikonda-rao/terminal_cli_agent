# Contributing to Terminal Coding Agent

We welcome contributions from the developer community to advance the state of AI-assisted development tools. This document outlines our contribution guidelines, development standards, and community expectations for maintaining code quality and project integrity.

## Table of Contents

- [Development Setup](#development-setup)
- [Contribution Workflow](#contribution-workflow)
- [Code Standards](#code-standards)
- [Areas for Contribution](#areas-for-contribution)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Standards](#documentation-standards)
- [Security Guidelines](#security-guidelines)
- [Community Guidelines](#community-guidelines)

## Development Setup

### Prerequisites

Before contributing, ensure your development environment meets the following requirements:

- Python 3.8 or higher
- Git version control system
- Terminal with UTF-8 support
- API credentials for LLM providers (optional for testing)

### Environment Configuration

1. **Fork and clone the repository**:
```bash
git clone https://github.com/your-username/terminal_cli.git
cd terminal_cli
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
cp env.example .env
# Configure your API credentials in .env
```

3. **Verify installation**:
```bash
python test.py
python simple_demo.py
```

### Development Environment Setup

For advanced development, consider setting up a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

## Contribution Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# Examples:
git checkout -b feature/typescript-support
git checkout -b bugfix/intent-parsing-edge-case
git checkout -b docs/api-documentation
```

### 2. Implement Changes

Follow our established coding standards and architectural patterns:

```python
# Example: Adding a new intent type
class IntentType(Enum):
    CREATE_FUNCTION = "create_function"
    CREATE_CLASS = "create_class"
    MODIFY_CODE = "modify_code"
    RUN_CODE = "run_code"
    SEARCH_CODE = "search_code"
    EXPLAIN_CODE = "explain_code"
    DEBUG_CODE = "debug_code"
    CREATE_FILE = "create_file"
    DELETE_FILE = "delete_file"
    # Add your new intent type here
    NEW_INTENT_TYPE = "new_intent_type"
```

### 3. Validate Implementation

```bash
# Run unit tests
python test.py

# Run integration tests
python simple_demo.py

# Test CLI functionality
python -m src.cli.main

# Run specific test modules
python -m pytest tests/test_intent_parser.py
```

### 4. Commit Changes

Use descriptive commit messages following conventional commits:

```bash
git add .
git commit -m "feat: add TypeScript code generation support

- Implement TypeScript language detection
- Add TypeScript-specific code generation templates
- Update intent parser to handle TypeScript syntax
- Add comprehensive test coverage

Closes #123"
```

### 5. Submit for Review

```bash
git push origin feature/your-feature-name
# Create Pull Request via GitHub interface
```

## Code Standards

### Python Code Style

Follow PEP 8 guidelines with these project-specific standards:

```python
# Good: Clear function documentation
def generate_code(intent: Intent, context: Dict[str, Any]) -> List[CodeBlock]:
    """
    Generate code blocks based on parsed intent and context.
    
    Args:
        intent: Parsed user intent with type and parameters
        context: Additional context including conversation history
        
    Returns:
        List of generated code blocks with metadata
        
    Raises:
        CodeGenerationError: When code generation fails
    """
    if not intent or not intent.type:
        raise CodeGenerationError("Invalid intent provided")
    
    # Implementation here
    return code_blocks

# Good: Type hints and error handling
def parse_intent(user_input: str, context: Optional[Dict] = None) -> Intent:
    """Parse user input into structured intent."""
    try:
        # Implementation
        return intent
    except ParseError as e:
        logger.error(f"Intent parsing failed: {e}")
        raise
```

### File Organization

```
src/
├── cli/           # CLI interface components
├── core/          # Core business logic
│   ├── agent.py   # Main agent orchestrator
│   ├── models.py  # Data models and types
│   └── ...
├── execution/     # Code execution engine
├── memory/        # Conversation and state management
└── utils/         # Utility functions
```

### Error Handling

```python
# Good: Specific exception handling
try:
    result = execute_code(code_block)
except ExecutionTimeoutError:
    logger.warning("Code execution timed out")
    return ExecutionResult(status=ExecutionStatus.TIMEOUT)
except SecurityViolationError as e:
    logger.error(f"Security violation: {e}")
    return ExecutionResult(status=ExecutionStatus.SECURITY_ERROR)
except Exception as e:
    logger.error(f"Unexpected execution error: {e}")
    return ExecutionResult(status=ExecutionStatus.ERROR, error_message=str(e))
```

## Areas for Contribution

### Bug Fixes and Improvements

- **Intent Parsing**: Improve accuracy and handle edge cases
- **Error Handling**: Enhance user feedback and error recovery
- **Cross-platform Compatibility**: Ensure consistent behavior across operating systems
- **Performance Optimization**: Reduce memory usage and improve response times

Example bug fix:

```python
# Before: Potential division by zero
def calculate_success_rate(successful: int, total: int) -> float:
    return successful / total

# After: Safe division with proper handling
def calculate_success_rate(successful: int, total: int) -> float:
    if total == 0:
        return 0.0
    return successful / total
```

### New Features

#### Core Functionality

- **Additional LLM Providers**: Add support for Cohere, Hugging Face, or local models
- **More Programming Languages**: Add support for Swift, Kotlin, C#, PHP, Ruby
- **Enhanced Intent Types**: Add new intent types for specific use cases

Example feature implementation:

```python
# Adding support for a new programming language
class CodeLanguage(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    RUST = "rust"
    GO = "go"
    # Add new language
    SWIFT = "swift"

# Language-specific code generation
def generate_swift_code(intent: Intent) -> CodeBlock:
    """Generate Swift code based on intent."""
    if intent.type == IntentType.CREATE_FUNCTION:
        return CodeBlock(
            content=f"func {intent.parameters.get('function_name', 'newFunction')}() {{\n    // Implementation\n}}",
            language=CodeLanguage.SWIFT,
            filename=f"{intent.parameters.get('function_name', 'NewFunction')}.swift"
        )
```

#### Advanced Features

- **Code Analysis**: Static analysis integration
- **Testing Framework**: Automated test generation
- **Documentation Generation**: Auto-generate API documentation

### Testing

- **Unit Tests**: Comprehensive test coverage for all modules
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Benchmark execution times and memory usage

Example test implementation:

```python
import pytest
from src.core.intent_parser import IntentParser
from src.core.models import IntentType

class TestIntentParser:
    def setup_method(self):
        self.parser = IntentParser()
    
    def test_create_function_intent(self):
        """Test function creation intent parsing."""
        result = self.parser.parse("Create a Python function for quicksort")
        
        assert result.type == IntentType.CREATE_FUNCTION
        assert result.language == CodeLanguage.PYTHON
        assert "quicksort" in result.parameters.get("description", "").lower()
        assert result.confidence > 0.8
    
    def test_modify_code_intent(self):
        """Test code modification intent parsing."""
        result = self.parser.parse("Modify the last function to handle empty lists")
        
        assert result.type == IntentType.MODIFY_CODE
        assert "empty lists" in result.parameters.get("description", "").lower()
    
    @pytest.mark.parametrize("input_text,expected_type", [
        ("Create a class for binary tree", IntentType.CREATE_CLASS),
        ("Run the function with test data", IntentType.RUN_CODE),
        ("Search for quicksort function", IntentType.SEARCH_CODE),
    ])
    def test_intent_types(self, input_text, expected_type):
        """Test various intent type parsing."""
        result = self.parser.parse(input_text)
        assert result.type == expected_type
```

### Documentation

- **API Documentation**: Comprehensive function and class documentation
- **User Guides**: Step-by-step tutorials and examples
- **Architecture Documentation**: System design and component interaction

Example documentation:

```python
class CodingAgent:
    """
    Main orchestrator for the Terminal Coding Agent.
    
    The CodingAgent coordinates all system components to process natural language
    requests and generate appropriate code responses. It manages the complete
    workflow from intent parsing to code execution.
    
    Attributes:
        config (AgentConfig): Configuration settings for the agent
        project_root (str): Root directory for the current project
        intent_parser (IntentParser): Natural language intent parser
        code_generator (CodeGenerator): Code generation engine
        file_manager (FileManager): File operations manager
        executor (SandboxExecutor): Code execution engine
        memory (ConversationMemory): Conversation state manager
    
    Example:
        >>> config = AgentConfig(llm_provider="openai", model_name="gpt-4")
        >>> agent = CodingAgent(".", config)
        >>> turn = agent.process_input("Create a Python function for quicksort")
        >>> print(turn.success)
        True
    """
    
    def process_input(self, user_input: str) -> ConversationTurn:
        """
        Process user input and generate appropriate response.
        
        This method orchestrates the complete workflow:
        1. Parse user intent from natural language
        2. Generate appropriate code based on intent
        3. Execute code if requested
        4. Manage file operations
        5. Update conversation memory
        
        Args:
            user_input: Natural language input from user
            
        Returns:
            ConversationTurn: Complete interaction result with generated code,
                             execution results, and file operations
            
        Raises:
            ProcessingError: When input processing fails
            CodeGenerationError: When code generation fails
            ExecutionError: When code execution fails
            
        Example:
            >>> agent = CodingAgent()
            >>> turn = agent.process_input("Create a function to sort a list")
            >>> if turn.success:
            ...     print(f"Generated {len(turn.generated_code)} code blocks")
            ...     for block in turn.generated_code:
            ...         print(f"File: {block.filename}")
        """
```

## Testing Guidelines

### Unit Testing

```python
# tests/test_code_generator.py
import pytest
from unittest.mock import Mock, patch
from src.core.code_generator import CodeGenerator
from src.core.models import Intent, IntentType, CodeLanguage

class TestCodeGenerator:
    def setup_method(self):
        self.generator = CodeGenerator()
    
    def test_generate_python_function(self):
        """Test Python function generation."""
        intent = Intent(
            type=IntentType.CREATE_FUNCTION,
            parameters={"function_name": "quicksort", "description": "sort a list"}
        )
        
        result = self.generator.generate_code(intent)
        
        assert len(result) == 1
        assert "def quicksort" in result[0].content
        assert result[0].language == CodeLanguage.PYTHON
        assert result[0].filename == "quicksort.py"
    
    @patch('src.core.code_generator.llm_client')
    def test_llm_integration(self, mock_llm):
        """Test LLM integration for code generation."""
        mock_llm.generate_code.return_value = "def test(): pass"
        
        intent = Intent(type=IntentType.CREATE_FUNCTION)
        result = self.generator.generate_code(intent)
        
        mock_llm.generate_code.assert_called_once()
        assert len(result) > 0
```

### Integration Testing

```python
# tests/test_integration.py
import pytest
from src.core.agent import CodingAgent
from src.core.models import AgentConfig

class TestIntegration:
    def test_full_workflow(self):
        """Test complete workflow from input to output."""
        config = AgentConfig(llm_provider="mock")
        agent = CodingAgent(".", config)
        
        # Test function creation
        turn = agent.process_input("Create a Python function for binary search")
        assert turn.success
        assert len(turn.generated_code) > 0
        
        # Test code execution
        turn = agent.process_input("Run the last function with [1, 3, 5, 7, 9]")
        assert turn.success
        assert turn.execution_result is not None
```

## Documentation Standards

### Code Documentation

```python
def complex_algorithm(data: List[int], threshold: float) -> Dict[str, Any]:
    """
    Perform complex data processing with configurable threshold.
    
    This function implements a sophisticated algorithm that processes
    numerical data according to specified parameters. It handles edge
    cases and provides comprehensive error reporting.
    
    Args:
        data: List of integers to process. Must not be empty.
        threshold: Processing threshold between 0.0 and 1.0
        
    Returns:
        Dictionary containing:
            - 'result': Processed data as list
            - 'statistics': Processing statistics
            - 'warnings': List of any warnings encountered
            
    Raises:
        ValueError: If data is empty or threshold is invalid
        ProcessingError: If algorithm fails to process data
        
    Example:
        >>> data = [1, 2, 3, 4, 5]
        >>> result = complex_algorithm(data, 0.5)
        >>> print(result['statistics']['processed_count'])
        5
    """
    if not data:
        raise ValueError("Data cannot be empty")
    
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("Threshold must be between 0.0 and 1.0")
    
    # Implementation here
    return {
        'result': processed_data,
        'statistics': stats,
        'warnings': warnings
    }
```

## Security Guidelines

### Code Execution Security

```python
# Secure code execution with resource limits
class SecureExecutor:
    def execute_code(self, code_block: CodeBlock) -> ExecutionResult:
        """Execute code with security constraints."""
        # Set resource limits
        resource_limits = {
            'cpu_time': 30,  # seconds
            'memory': 512,   # MB
            'disk': 100      # MB
        }
        
        # Validate code for security issues
        if self._contains_dangerous_operations(code_block.content):
            return ExecutionResult(
                status=ExecutionStatus.SECURITY_ERROR,
                error_message="Code contains potentially dangerous operations"
            )
        
        # Execute in sandboxed environment
        return self._execute_in_sandbox(code_block, resource_limits)
    
    def _contains_dangerous_operations(self, code: str) -> bool:
        """Check for potentially dangerous operations."""
        dangerous_patterns = [
            r'import\s+os',
            r'import\s+subprocess',
            r'import\s+sys',
            r'__import__',
            r'eval\(',
            r'exec\(',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return True
        return False
```

### Input Validation

```python
def validate_user_input(user_input: str) -> bool:
    """Validate user input for security and appropriateness."""
    if not user_input or len(user_input.strip()) == 0:
        return False
    
    if len(user_input) > 10000:  # Prevent extremely long inputs
        return False
    
    # Check for potentially malicious content
    malicious_patterns = [
        r'<script',
        r'javascript:',
        r'data:text/html',
        r'vbscript:',
    ]
    
    for pattern in malicious_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False
    
    return True
```

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive in all interactions
- Provide constructive feedback and suggestions
- Help newcomers learn and contribute effectively
- Follow professional communication standards

### Contribution Recognition

We recognize contributors through our tiered system:

- **🌱 Seedling**: First contribution
- **🌿 Sprout**: 5+ contributions
- **🌳 Tree**: 20+ contributions with significant impact
- **🌲 Forest**: 50+ contributions with leadership role

### Getting Help

- **Documentation**: Check README.md and inline documentation
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Community**: Join our community channels for real-time help

### Pull Request Guidelines

1. **Clear Description**: Provide comprehensive description of changes
2. **Small Changes**: Keep PRs focused and manageable
3. **Tests**: Include tests for new functionality
4. **Documentation**: Update documentation as needed
5. **Review**: Respond to feedback promptly and constructively

Example PR description:

```markdown
## Summary
Add TypeScript support to the code generation engine.

## Changes
- Implement TypeScript language detection in intent parser
- Add TypeScript-specific code generation templates
- Update CLI to handle TypeScript file extensions
- Add comprehensive test coverage

## Testing
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Manual testing completed
- [x] New tests added for TypeScript functionality

## Screenshots
[Include screenshots if UI changes]

## Related Issues
Closes #123
```

## Getting Started

New to the project? Here's how to make your first contribution:

1. **Choose an Issue**: Look for issues labeled `good first issue`
2. **Set Up Environment**: Follow the development setup guide
3. **Make Changes**: Implement your solution
4. **Test Thoroughly**: Ensure all tests pass
5. **Submit PR**: Create a pull request with clear description

### Example First Contribution

```python
# Adding a simple utility function
def format_code_block(code: str, language: str) -> str:
    """
    Format code block with language-specific syntax highlighting.
    
    Args:
        code: Raw code content
        language: Programming language for syntax highlighting
        
    Returns:
        Formatted code block string
    """
    if not code or not language:
        return code
    
    # Add language-specific formatting
    formatted = f"```{language}\n{code}\n```"
    return formatted
```

Thank you for contributing to the Terminal Coding Agent! Your contributions help advance the future of AI-assisted development.
