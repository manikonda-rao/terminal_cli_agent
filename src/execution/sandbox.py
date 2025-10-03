"""
Sandboxed execution engine for safe code execution.
"""

import subprocess
import tempfile
import os
import time
import psutil
import signal
from typing import Optional, Dict, Any
from pathlib import Path
from ..core.models import CodeBlock, ExecutionResult, ExecutionStatus, AgentConfig
from ..analysis.code_analyzer import StaticCodeAnalyzer, SecurityScanner


class SandboxExecutor:
    """Executes code in a sandboxed environment with resource limits."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.temp_dir = None
        self.active_processes = {}
        self.code_analyzer = StaticCodeAnalyzer()
        self.security_scanner = SecurityScanner()
        self.execution_history = []
    
    def execute_code(self, code_block: CodeBlock, timeout: Optional[int] = None) -> ExecutionResult:
        """
        Execute code in a sandboxed environment with enhanced security.
        
        Args:
            code_block: Code to execute
            timeout: Execution timeout in seconds
            
        Returns:
            Execution result with output and status
        """
        timeout = timeout or self.config.max_execution_time
        
        # Pre-execution security analysis
        analysis_result = self.code_analyzer.analyze_code(code_block)
        if not analysis_result.is_safe:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=f"Code analysis failed: {analysis_result.summary}",
                error_message="Code failed security analysis"
            )
        
        # Additional security scan
        security_result = self.security_scanner.scan_code(code_block)
        if not security_result.is_safe:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=security_result.reason,
                error_message=f"Security scan failed: {security_result.reason}"
            )
        
        # Create temporary directory for execution
        self.temp_dir = tempfile.mkdtemp(prefix="coding_agent_")
        
        try:
            # Write code to temporary file
            file_path = self._write_code_file(code_block)
            
            # Execute the code
            result = self._run_code(file_path, timeout)
            
            # Log execution
            self._log_execution(code_block, result, analysis_result)
            
            return result
            
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=str(e),
                error_message=f"Execution error: {e}"
            )
        
        finally:
            # Cleanup
            self._cleanup()
    
    def _write_code_file(self, code_block: CodeBlock) -> str:
        """Write code block to a temporary file."""
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
        file_path = os.path.join(self.temp_dir, f"code{ext}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code_block.content)
        
        return file_path
    
    def _run_code(self, file_path: str, timeout: int) -> ExecutionResult:
        """Run code file with resource limits."""
        start_time = time.time()
        
        # Determine execution command based on file type
        cmd = self._get_execution_command(file_path)
        
        try:
            # Start process with resource limits
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.temp_dir,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            # Track the process
            self.active_processes[process.pid] = process
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
                
            except subprocess.TimeoutExpired:
                # Kill the process and all its children
                self._kill_process_tree(process.pid)
                stdout, stderr = process.communicate()
                return_code = -1
                
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    stdout=stdout,
                    stderr=stderr,
                    return_code=return_code,
                    execution_time=time.time() - start_time,
                    error_message=f"Execution timed out after {timeout} seconds"
                )
            
            # Calculate execution time and memory usage
            execution_time = time.time() - start_time
            
            # Determine status based on return code
            if return_code == 0:
                status = ExecutionStatus.COMPLETED
            else:
                status = ExecutionStatus.FAILED
            
            return ExecutionResult(
                status=status,
                stdout=stdout,
                stderr=stderr,
                return_code=return_code,
                execution_time=execution_time,
                memory_used=0.0,  # TODO: Implement memory tracking
                error_message=None if return_code == 0 else f"Process exited with code {return_code}"
            )
            
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=str(e),
                return_code=-1,
                execution_time=time.time() - start_time,
                error_message=f"Execution error: {e}"
            )
        
        finally:
            # Remove from active processes
            if process.pid in self.active_processes:
                del self.active_processes[process.pid]
    
    def _get_execution_command(self, file_path: str) -> list:
        """Get execution command for the file type."""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.py':
            return ['python', file_path]
        elif ext == '.js':
            return ['node', file_path]
        elif ext == '.ts':
            return ['ts-node', file_path]
        elif ext == '.java':
            # Compile first, then run
            class_name = Path(file_path).stem
            return ['bash', '-c', f'javac {file_path} && java {class_name}']
        elif ext == '.cpp':
            # Compile first, then run
            return ['bash', '-c', f'g++ -o {file_path}.out {file_path} && ./{file_path}.out']
        elif ext == '.rs':
            # Compile first, then run
            return ['bash', '-c', f'rustc {file_path} && ./{Path(file_path).stem}']
        elif ext == '.go':
            return ['go', 'run', file_path]
        else:
            # Default to Python
            return ['python', file_path]
    
    def _kill_process_tree(self, pid: int):
        """Kill process and all its children."""
        try:
            if os.name == 'nt':
                # Windows
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], 
                             capture_output=True)
            else:
                # Unix-like systems
                os.killpg(os.getpgid(pid), signal.SIGTERM)
                time.sleep(1)
                try:
                    os.killpg(os.getpgid(pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass  # Process already dead
        except Exception as e:
            print(f"Warning: Could not kill process {pid}: {e}")
    
    def _cleanup(self):
        """Clean up temporary files and processes."""
        # Kill any remaining processes
        for pid in list(self.active_processes.keys()):
            try:
                self._kill_process_tree(pid)
            except Exception:
                pass
        
        # Remove temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                print(f"Warning: Could not remove temp directory {self.temp_dir}: {e}")
        
        self.temp_dir = None
        self.active_processes.clear()
    
    def _log_execution(self, code_block: CodeBlock, result: ExecutionResult, analysis_result):
        """Log execution details for monitoring."""
        self.execution_history.append({
            "timestamp": time.time(),
            "language": code_block.language.value,
            "status": result.status.value,
            "execution_time": result.execution_time,
            "return_code": result.return_code,
            "analysis_score": analysis_result.score,
            "security_score": analysis_result.security_score,
            "stdout_length": len(result.stdout),
            "stderr_length": len(result.stderr)
        })
        
        # Keep only recent history
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_history:
            return {"total_executions": 0}
        
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for e in self.execution_history if e["status"] == "completed")
        avg_execution_time = sum(e["execution_time"] for e in self.execution_history) / total_executions
        avg_security_score = sum(e["security_score"] for e in self.execution_history) / total_executions
        
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
            "average_security_score": avg_security_score,
            "language_distribution": language_counts
        }


class DockerExecutor(SandboxExecutor):
    """Docker-based sandboxed executor for enhanced security."""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.docker_image = "python:3.11-slim"
        self.container_name = f"coding_agent_{os.getpid()}"
        self.security_policy = self._create_security_policy()
    
    def _create_security_policy(self) -> Dict[str, Any]:
        """Create Docker security policy."""
        return {
            "read_only": True,
            "no_new_privileges": True,
            "user": "nobody",
            "memory_limit": f"{self.config.max_memory_mb}m",
            "cpu_limit": "1",
            "network_disabled": True,
            "cap_drop": ["ALL"],
            "security_opt": ["no-new-privileges:true"],
            "tmpfs": {
                "/tmp": "rw,size=100m,noexec,nosuid,nodev"
            }
        }
    
    def _run_code(self, file_path: str, timeout: int) -> ExecutionResult:
        """Run code in Docker container with enhanced security."""
        start_time = time.time()
        
        try:
            # Build Docker command with security constraints
            cmd = [
                'docker', 'run', '--rm',
                '--memory', self.security_policy["memory_limit"],
                '--cpus', self.security_policy["cpu_limit"],
                '--network', 'none',
                '--read-only',
                '--user', self.security_policy["user"],
                '--cap-drop', ','.join(self.security_policy["cap_drop"]),
                '--security-opt', ','.join(self.security_policy["security_opt"]),
                '--tmpfs', ','.join([f"{k}:{v}" for k, v in self.security_policy["tmpfs"].items()]),
                '-v', f'{self.temp_dir}:/workspace:ro',
                '-w', '/workspace',
                self.docker_image,
                'python', os.path.basename(file_path)
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
                
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return_code = -1
                
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    stdout=stdout,
                    stderr=stderr,
                    return_code=return_code,
                    execution_time=time.time() - start_time,
                    error_message=f"Execution timed out after {timeout} seconds"
                )
            
            execution_time = time.time() - start_time
            
            if return_code == 0:
                status = ExecutionStatus.COMPLETED
            else:
                status = ExecutionStatus.FAILED
            
            return ExecutionResult(
                status=status,
                stdout=stdout,
                stderr=stderr,
                return_code=return_code,
                execution_time=execution_time,
                memory_used=0.0,
                error_message=None if return_code == 0 else f"Process exited with code {return_code}"
            )
            
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=str(e),
                return_code=-1,
                execution_time=time.time() - start_time,
                error_message=f"Docker execution error: {e}"
            )
