"""
Daytona-based secure sandboxed execution engine for safe code execution.
"""

import os
import time
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

try:
    from daytona_sdk import Daytona, DaytonaConfig, CreateSandboxParams
    DAYTONA_AVAILABLE = True
except ImportError:
    DAYTONA_AVAILABLE = False
    Daytona = None
    DaytonaConfig = None
    CreateSandboxParams = None

from ..core.models import CodeBlock, ExecutionResult, ExecutionStatus, AgentConfig


class DaytonaExecutor:
    """Daytona-based sandboxed executor for enhanced security and isolation."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.daytona_client = None
        self.active_sandboxes = {}
        self.execution_history = []
        
        if not DAYTONA_AVAILABLE:
            raise ImportError("Daytona SDK not available. Install with: pip install daytona-sdk")
        
        # Initialize Daytona API key
        self.api_key = os.getenv("DAYTONA_API_KEY")
        if not self.api_key:
            raise ValueError("DAYTONA_API_KEY environment variable not set")
        
        # Initialize Daytona client
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Daytona client with configuration."""
        try:
            daytona_config = DaytonaConfig(api_key=self.api_key)
            self.daytona_client = Daytona(daytona_config)
            print("✓ Daytona client initialized successfully")
        except Exception as e:
            raise Exception(f"Failed to initialize Daytona client: {e}")
    
    def execute_code(self, code_block: CodeBlock, timeout: Optional[int] = None) -> ExecutionResult:
        """
        Execute code in Daytona sandbox with enhanced security.
        
        Args:
            code_block: Code to execute
            timeout: Execution timeout in seconds
            
        Returns:
            Execution result with output and status
        """
        timeout = timeout or self.config.max_execution_time
        start_time = time.time()
        
        try:
            # Create sandbox for execution
            sandbox = self._create_sandbox(code_block.language)
            
            # Execute code in sandbox
            result = self._execute_in_sandbox(sandbox, code_block, timeout)
            
            # Add execution metadata
            result.execution_time = time.time() - start_time
            
            # Log execution
            self._log_execution(code_block, result)
            
            # Clean up sandbox
            self._cleanup_sandbox(sandbox)
            
            return result
            
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=str(e),
                error_message=f"Daytona execution error: {e}",
                execution_time=time.time() - start_time
            )
    
    def _create_sandbox(self, language: str) -> Any:
        """Create a new Daytona sandbox for the specified language."""
        try:
            # Map language to Daytona language identifier
            daytona_language = self._map_language_to_daytona(language)
            
            # Create sandbox parameters
            sandbox_params = CreateSandboxParams(
                language=daytona_language,
                timeout=self.config.max_execution_time,
                memory_limit=self.config.max_memory_mb
            )
            
            # Create sandbox
            sandbox = self.daytona_client.create(sandbox_params)
            
            # Track active sandbox
            sandbox_id = getattr(sandbox, 'id', f"sandbox_{len(self.active_sandboxes)}")
            self.active_sandboxes[sandbox_id] = sandbox
            
            print(f"✓ Daytona sandbox created for {language}")
            return sandbox
            
        except Exception as e:
            raise Exception(f"Failed to create Daytona sandbox: {e}")
    
    def _map_language_to_daytona(self, language: str) -> str:
        """Map internal language to Daytona language identifier."""
        language_mapping = {
            "python": "python",
            "javascript": "javascript",
            "typescript": "typescript",
            "java": "java",
            "cpp": "cpp",
            "rust": "rust",
            "go": "go",
            "php": "php",
            "ruby": "ruby",
            "perl": "perl",
            "bash": "bash",
            "powershell": "powershell"
        }
        
        return language_mapping.get(language.lower(), "python")
    
    def _execute_in_sandbox(self, sandbox: Any, code_block: CodeBlock, timeout: int) -> ExecutionResult:
        """Execute code in Daytona sandbox."""
        try:
            # Execute code using Daytona's code execution API
            response = sandbox.process.code_run(code_block.content, timeout=timeout)
            
            # Parse response
            if hasattr(response, 'result'):
                stdout = response.result if response.result else ""
                stderr = ""
                return_code = 0 if response.result else 1
            else:
                stdout = str(response) if response else ""
                stderr = ""
                return_code = 0
            
            # Determine status
            if return_code == 0:
                status = ExecutionStatus.COMPLETED
                error_message = None
            else:
                status = ExecutionStatus.FAILED
                error_message = f"Process exited with code {return_code}"
            
            return ExecutionResult(
                status=status,
                stdout=stdout,
                stderr=stderr,
                return_code=return_code,
                error_message=error_message
            )
            
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=str(e),
                error_message=f"Sandbox execution error: {e}"
            )
    
    def _cleanup_sandbox(self, sandbox: Any):
        """Clean up Daytona sandbox resources."""
        try:
            sandbox_id = getattr(sandbox, 'id', None)
            if sandbox_id and sandbox_id in self.active_sandboxes:
                del self.active_sandboxes[sandbox_id]
            
            # Remove sandbox from Daytona
            self.daytona_client.remove(sandbox)
            print("✓ Daytona sandbox cleaned up")
            
        except Exception as e:
            print(f"Warning: Error cleaning up Daytona sandbox: {e}")
    
    def _log_execution(self, code_block: CodeBlock, result: ExecutionResult):
        """Log execution details for monitoring."""
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "language": code_block.language.value,
            "status": result.status.value,
            "execution_time": result.execution_time,
            "return_code": result.return_code,
            "stdout_length": len(result.stdout),
            "stderr_length": len(result.stderr)
        })
        
        # Keep only recent history
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    def cleanup(self):
        """Clean up all Daytona resources."""
        for sandbox_id, sandbox in list(self.active_sandboxes.items()):
            try:
                self.daytona_client.remove(sandbox)
                del self.active_sandboxes[sandbox_id]
            except Exception as e:
                print(f"Warning: Error cleaning up sandbox {sandbox_id}: {e}")
        
        self.active_sandboxes.clear()
        print("✓ All Daytona sandboxes cleaned up")
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_history:
            return {"total_executions": 0}
        
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for e in self.execution_history if e["status"] == "completed")
        avg_execution_time = sum(e["execution_time"] for e in self.execution_history) / total_executions
        
        # Language distribution
        language_counts = {}
        for execution in self.execution_history:
            lang = execution["language"]
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "average_execution_time": avg_execution_time,
            "language_distribution": language_counts,
            "active_sandboxes": len(self.active_sandboxes),
            "daytona_status": "active" if self.daytona_client else "inactive"
        }
    
    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup()


class DaytonaExecutorWithSecurity(DaytonaExecutor):
    """Enhanced Daytona executor with additional security controls."""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.security_scanner = SecurityScanner()
        self.resource_monitor = ResourceMonitor(config)
    
    def execute_code(self, code_block: CodeBlock, timeout: Optional[int] = None) -> ExecutionResult:
        """Execute code with enhanced security checks."""
        # Pre-execution security scan
        security_result = self.security_scanner.scan_code(code_block)
        if not security_result.is_safe:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=security_result.reason,
                error_message=f"Security scan failed: {security_result.reason}"
            )
        
        # Execute with resource monitoring
        result = super().execute_code(code_block, timeout)
        
        # Post-execution resource check
        if self.resource_monitor.check_resource_usage(result):
            result.status = ExecutionStatus.MEMORY_LIMIT
            result.error_message = "Resource usage exceeded limits"
        
        return result


class SecurityScanner:
    """Scans code for potentially malicious patterns."""
    
    def __init__(self):
        self.dangerous_patterns = [
            # File system access
            r'import\s+os',
            r'import\s+shutil',
            r'import\s+subprocess',
            r'__import__\s*\(',
            r'exec\s*\(',
            r'eval\s*\(',
            
            # Network access
            r'import\s+socket',
            r'import\s+urllib',
            r'import\s+requests',
            r'import\s+http',
            
            # System commands
            r'os\.system\s*\(',
            r'os\.popen\s*\(',
            r'subprocess\.run\s*\(',
            r'subprocess\.call\s*\(',
            r'subprocess\.Popen\s*\(',
            
            # File operations
            r'open\s*\(',
            r'file\s*\(',
            r'with\s+open\s*\(',
            
            # Dangerous built-ins
            r'__builtins__',
            r'globals\s*\(',
            r'locals\s*\(',
            r'vars\s*\(',
            
            # Code injection
            r'compile\s*\(',
            r'getattr\s*\(',
            r'setattr\s*\(',
            r'delattr\s*\(',
        ]
        
        self.allowed_patterns = [
            # Safe imports
            r'import\s+math',
            r'import\s+random',
            r'import\s+datetime',
            r'import\s+json',
            r'import\s+collections',
            r'import\s+itertools',
            r'import\s+functools',
            r'from\s+math\s+import',
            r'from\s+random\s+import',
            r'from\s+datetime\s+import',
            r'from\s+json\s+import',
            r'from\s+collections\s+import',
            r'from\s+itertools\s+import',
            r'from\s+functools\s+import',
        ]
    
    def scan_code(self, code_block: CodeBlock) -> 'SecurityResult':
        """Scan code for security issues."""
        import re
        
        content = code_block.content
        issues = []
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Potentially dangerous pattern detected: {pattern}")
        
        # Check for allowed patterns (whitelist approach)
        has_allowed_imports = any(re.search(pattern, content, re.IGNORECASE) for pattern in self.allowed_patterns)
        
        # Additional checks
        if 'import' in content and not has_allowed_imports:
            issues.append("Unsafe import detected")
        
        if len(issues) > 0:
            return SecurityResult(
                is_safe=False,
                reason="; ".join(issues),
                issues=issues
            )
        
        return SecurityResult(is_safe=True, reason="Code passed security scan")
    
    def add_custom_pattern(self, pattern: str, is_dangerous: bool = True):
        """Add custom security pattern."""
        if is_dangerous:
            self.dangerous_patterns.append(pattern)
        else:
            self.allowed_patterns.append(pattern)


class SecurityResult:
    """Result of security scan."""
    
    def __init__(self, is_safe: bool, reason: str, issues: List[str] = None):
        self.is_safe = is_safe
        self.reason = reason
        self.issues = issues or []


class ResourceMonitor:
    """Monitors resource usage during execution."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.max_memory_mb = config.max_memory_mb
        self.max_execution_time = config.max_execution_time
    
    def check_resource_usage(self, result: ExecutionResult) -> bool:
        """Check if resource usage exceeded limits."""
        # Check execution time
        if result.execution_time > self.max_execution_time:
            return True
        
        # Check memory usage (if available)
        if hasattr(result, 'memory_used') and result.memory_used > self.max_memory_mb:
            return True
        
        # Check output size (prevent memory exhaustion via large outputs)
        max_output_size = 10 * 1024 * 1024  # 10MB
        if len(result.stdout) > max_output_size or len(result.stderr) > max_output_size:
            return True
        
        return False
