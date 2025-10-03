"""
Core data models for the Terminal Coding Agent.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
import json


class IntentType(str, Enum):
    """Types of intents the agent can understand."""
    CREATE_FUNCTION = "create_function"
    CREATE_CLASS = "create_class"
    MODIFY_CODE = "modify_code"
    RUN_CODE = "run_code"
    CREATE_FILE = "create_file"
    DELETE_FILE = "delete_file"
    SEARCH_CODE = "search_code"
    EXPLAIN_CODE = "explain_code"
    REFACTOR_CODE = "refactor_code"
    DEBUG_CODE = "debug_code"
    TEST_CODE = "test_code"


class CodeLanguage(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    RUST = "rust"
    GO = "go"


class ExecutionStatus(str, Enum):
    """Status of code execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    MEMORY_LIMIT = "memory_limit"


class Intent(BaseModel):
    """Parsed intent from natural language input."""
    # Accept enum (preferred) or raw string (for older callers/tests)
    type: IntentType
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    original_text: str = ""
    language: Optional[CodeLanguage] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class CodeBlock(BaseModel):
    """Represents a block of generated code."""
    content: str
    language: CodeLanguage
    filename: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    """Result of code execution."""
    status: ExecutionStatus
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    execution_time: float = 0.0
    memory_used: float = 0.0
    error_message: Optional[str] = None
    traceback: Optional[str] = None


class FileOperation(BaseModel):
    """Represents a file operation."""
    operation: str  # create, modify, delete
    filepath: str
    content: Optional[str] = None
    backup_path: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversationTurn(BaseModel):
    """A single turn in the conversation."""
    user_input: str
    intent: Intent
    generated_code: List[CodeBlock] = Field(default_factory=list)
    execution_result: Optional[ExecutionResult] = None
    file_operations: List[FileOperation] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None


class ProjectState(BaseModel):
    """Current state of the project."""
    project_root: str
    active_files: List[str] = Field(default_factory=list)
    conversation_history: List[ConversationTurn] = Field(default_factory=list)
    file_backups: Dict[str, List[str]] = Field(default_factory=dict)
    last_operation: Optional[ConversationTurn] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class AgentConfig(BaseModel):
    """Configuration for the coding agent."""
    # LLM Configuration
    llm_provider: str = "openai"
    model_name: str = "gpt-4"
    # Backwards-compatible fields used in older code/tests
    model: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 2000
    
    # Execution Configuration
    max_execution_time: int = 30
    max_memory_mb: int = 512
    sandbox_timeout: int = 60
    
    # Project Configuration
    backup_enabled: bool = True
    auto_save: bool = True
    max_conversation_history: int = 50
    
    # CLI Configuration
    enable_syntax_highlighting: bool = True
    enable_autocomplete: bool = True
    history_size: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentConfig":
        """Create config from dictionary."""
        return cls(**data)
