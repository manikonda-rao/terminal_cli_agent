"""
E2B-based secure sandboxed execution engine for safe code execution.
"""

import os
import time
import json
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

try:
    from e2b import Sandbox
    E2B_AVAILABLE = True
except ImportError:
    E2B_AVAILABLE = False
    Sandbox = None

from ..core.models import CodeBlock, ExecutionResult, ExecutionStatus, AgentConfig


class E2BExecutor:
    """E2B-based sandboxed executor for enhanced security and isolation."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.sandbox = None
        self.active_sessions = {}
        self.execution_history = []
        
        if not E2B_AVAILABLE:
            raise ImportError("E2B package not available. Install with: pip install e2b")
        
        # Initialize E2B API key
        self.api_key = os.getenv("E2B_API_KEY")
        if not self.api_key:
            raise ValueError("E2B_API_KEY environment variable not set")
    
    def execute_code(self, code_block: CodeBlock, timeout: Optional[int] = None) -> ExecutionResult:
        """
        Execute code in E2B sandbox with enhanced security.
        
        Args:
            code_block: Code to execute
            timeout: Execution timeout in seconds
            
        Returns:
            Execution result with output and status
        """
        timeout = timeout or self.config.max_execution_time
        start_time = time.time()
        
        try:
            # Create or reuse sandbox
            sandbox = self._get_or_create_sandbox()
            
            # Write code to sandbox
            file_path = self._write_code_to_sandbox(sandbox, code_block)
            
            # Execute with security checks
            result = self._execute_in_sandbox(sandbox, file_path, timeout)
            
            # Add execution metadata
            result.execution_time = time.time() - start_time
            
            # Log execution
            self._log_execution(code_block, result)
            
            return result
            
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=str(e),
                error_message=f"E2B execution error: {e}",
                execution_time=time.time() - start_time
            )
    
    def _get_or_create_sandbox(self) -> Sandbox:
        """Get existing sandbox or create new one."""
        if self.sandbox is None or not self.sandbox.is_open:
            try:
                self.sandbox = Sandbox.create(api_key=self.api_key)
                print("✓ E2B sandbox created successfully")
            except Exception as e:
                raise Exception(f"Failed to create E2B sandbox: {e}")
        
        return self.sandbox
    
    def _write_code_to_sandbox(self, sandbox: Sandbox, code_block: CodeBlock) -> str:
        """Write code block to sandbox filesystem."""
        # Determine file extension based on language
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "java": ".java",
            "cpp": ".cpp",
            "rust": ".rs",
            "go": ".go"
        }
        
        ext = extensions.get(code_block.language.value, ".py")
        file_path = f"/tmp/code{ext}"
        
        try:
            # Write code to sandbox
            sandbox.filesystem.write(file_path, code_block.content)
            return file_path
        except Exception as e:
            raise Exception(f"Failed to write code to sandbox: {e}")
    
    def _execute_in_sandbox(self, sandbox: Sandbox, file_path: str, timeout: int) -> ExecutionResult:
        """Execute code in sandbox with security controls."""
        try:
            # Determine execution command based on file type
            cmd = self._get_execution_command(file_path)
            
            # Execute with timeout and resource limits
            result = sandbox.commands.run(cmd, timeout=timeout)
            
            # Parse result
            if result.exit_code == 0:
                status = ExecutionStatus.COMPLETED
                error_message = None
            else:
                status = ExecutionStatus.FAILED
                error_message = f"Process exited with code {result.exit_code}"
            
            return ExecutionResult(
                status=status,
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.exit_code,
                error_message=error_message
            )
            
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=str(e),
                error_message=f"Sandbox execution error: {e}"
            )
    
    def _get_execution_command(self, file_path: str) -> List[str]:
        """Get execution command for the file type."""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.py':
            return ['python', file_path]
        elif ext == '.js':
            return ['node', file_path]
        elif ext == '.ts':
            return ['ts-node', file_path]
        elif ext == '.java':
            class_name = Path(file_path).stem
            return ['bash', '-c', f'javac {file_path} && java {class_name}']
        elif ext == '.cpp':
            return ['bash', '-c', f'g++ -o {file_path}.out {file_path} && ./{file_path}.out']
        elif ext == '.rs':
            return ['bash', '-c', f'rustc {file_path} && ./{Path(file_path).stem}']
        elif ext == '.go':
            return ['go', 'run', file_path]
        else:
            return ['python', file_path]
    
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
        """Clean up sandbox resources."""
        if self.sandbox and self.sandbox.is_open:
            try:
                self.sandbox.close()
                print("✓ E2B sandbox closed")
            except Exception as e:
                print(f"Warning: Error closing E2B sandbox: {e}")
        
        self.sandbox = None
    
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
            "sandbox_status": "active" if self.sandbox and self.sandbox.is_open else "inactive"
        }
    
    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup()


class E2BExecutorWithSecurity(E2BExecutor):
    """Enhanced E2B executor with additional security controls."""
    
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
