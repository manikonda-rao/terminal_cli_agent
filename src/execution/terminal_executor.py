"""
Terminal executor for safe shell command execution with pty integration.
"""

import subprocess
import os
import time
import signal
import pty
import select
import threading
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from ..core.models import ExecutionResult, ExecutionStatus, AgentConfig, TerminalExecutionResult
from ..core.security_policy import SecurityPolicyManager, SecurityLevel


class TerminalExecutor:
    """Executes shell commands safely with security validation and pty integration."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.security_manager = SecurityPolicyManager(config.security_policy_file)
        self.active_processes = {}
        self.execution_history = []
        self.security_policy = self.security_manager.get_policy_for_level(
            SecurityLevel(config.security_level)
        )
        
        # Terminal-specific security patterns
        self.dangerous_commands = {
            'rm', 'del', 'format', 'fdisk', 'mkfs', 'dd', 'shred',
            'sudo', 'su', 'passwd', 'chmod', 'chown', 'mount', 'umount',
            'kill', 'killall', 'pkill', 'xkill', 'halt', 'shutdown', 'reboot',
            'curl', 'wget', 'nc', 'netcat', 'telnet', 'ssh', 'scp', 'rsync',
            'crontab', 'at', 'systemctl', 'service', 'initctl'
        }
        
        self.allowed_commands = {
            'ls', 'dir', 'pwd', 'cd', 'cat', 'type', 'head', 'tail', 'grep',
            'find', 'which', 'where', 'echo', 'print', 'date', 'time', 'whoami',
            'git', 'npm', 'pip', 'python', 'node', 'java', 'gcc', 'g++',
            'make', 'cmake', 'docker', 'kubectl', 'terraform', 'ansible',
            'ps', 'top', 'htop', 'df', 'du', 'free', 'uptime', 'uname',
            'mkdir', 'touch', 'cp', 'copy', 'mv', 'move', 'ln', 'link'
        }
    
    def execute_command(self, command: str, timeout: Optional[int] = None, 
                       interactive: bool = False) -> TerminalExecutionResult:
        """
        Execute shell command safely with security validation.
        
        Args:
            command: Shell command to execute
            timeout: Execution timeout in seconds
            interactive: Whether to use pty for interactive commands
            
        Returns:
            Execution result with output and status
        """
        timeout = timeout or self.security_policy.resource_limits.execution_timeout
        
        # Security validation
        security_check = self._validate_command_security(command)
        if not security_check.is_safe:
            return TerminalExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=f"Security validation failed: {security_check.reason}",
                error_message="Command blocked by security policy",
                command=command,
                interactive_mode=interactive,
                security_validated=False
            )
        
        start_time = time.time()
        
        try:
            if interactive:
                result = self._execute_interactive_command(command, timeout)
            else:
                result = self._execute_standard_command(command, timeout)
            
            # Log execution
            self._log_execution(command, result, security_check)
            
            return result
            
        except Exception as e:
            return TerminalExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=str(e),
                return_code=-1,
                execution_time=time.time() - start_time,
                error_message=f"Execution error: {e}",
                command=command,
                interactive_mode=interactive,
                security_validated=True
            )
    
    def _validate_command_security(self, command: str) -> 'SecurityCheckResult':
        """Validate command against security policy."""
        # Parse command to extract base command
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return SecurityCheckResult(False, "Empty command")
        
        base_command = cmd_parts[0].lower()
        
        # Check against dangerous commands
        if base_command in self.dangerous_commands:
            if self.security_policy.security_level == SecurityLevel.STRICT:
                return SecurityCheckResult(False, f"Dangerous command '{base_command}' blocked")
            elif self.security_policy.security_level == SecurityLevel.MODERATE:
                # Allow some dangerous commands with restrictions
                if base_command in ['sudo', 'su', 'kill']:
                    return SecurityCheckResult(False, f"Privilege escalation command '{base_command}' blocked")
        
        # Check against allowed commands (for strict mode)
        if self.security_policy.security_level == SecurityLevel.STRICT:
            if base_command not in self.allowed_commands:
                return SecurityCheckResult(False, f"Command '{base_command}' not in allowed list")
        
        # Check for dangerous patterns
        dangerous_patterns = self.security_policy.patterns.dangerous_patterns
        for pattern in dangerous_patterns:
            if pattern in command.lower():
                return SecurityCheckResult(False, f"Dangerous pattern '{pattern}' detected")
        
        # Check command length
        if len(command) > 1000:  # Reasonable limit
            return SecurityCheckResult(False, "Command too long")
        
        return SecurityCheckResult(True, "Command passed security validation")
    
    def _execute_standard_command(self, command: str, timeout: int) -> TerminalExecutionResult:
        """Execute command using standard subprocess."""
        start_time = time.time()
        
        try:
            # Set up environment with security constraints
            env = self._create_secure_environment()
            
            # Start process with security constraints
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=self._get_secure_working_directory(),
                preexec_fn=self._setup_process_security if os.name != 'nt' else None
            )
            
            # Track the process
            self.active_processes[process.pid] = process
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
                
            except subprocess.TimeoutExpired:
                # Kill the process and all its children
                self._kill_process_tree(process.pid)
                stdout, stderr = process.communicate()
                return_code = -1
                
                return TerminalExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    stdout=stdout,
                    stderr=stderr,
                    return_code=return_code,
                    execution_time=time.time() - start_time,
                    error_message=f"Command timed out after {timeout} seconds",
                    command=command,
                    interactive_mode=False,
                    security_validated=True
                )
            
            execution_time = time.time() - start_time
            
            # Determine status based on return code
            if return_code == 0:
                status = ExecutionStatus.COMPLETED
            else:
                status = ExecutionStatus.FAILED
            
            return TerminalExecutionResult(
                status=status,
                stdout=stdout,
                stderr=stderr,
                return_code=return_code,
                execution_time=execution_time,
                error_message=None if return_code == 0 else f"Command exited with code {return_code}",
                command=command,
                interactive_mode=False,
                security_validated=True
            )
            
        except Exception as e:
            return TerminalExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=str(e),
                return_code=-1,
                execution_time=time.time() - start_time,
                error_message=f"Command execution error: {e}",
                command=command,
                interactive_mode=False,
                security_validated=True
            )
        
        finally:
            # Remove from active processes
            if process.pid in self.active_processes:
                del self.active_processes[process.pid]
    
    def _execute_interactive_command(self, command: str, timeout: int) -> TerminalExecutionResult:
        """Execute command using pty for interactive support."""
        start_time = time.time()
        
        try:
            # Create master and slave file descriptors
            master_fd, slave_fd = pty.openpty()
            
            # Set up environment
            env = self._create_secure_environment()
            
            # Start process with pty
            process = subprocess.Popen(
                command,
                shell=True,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                text=True,
                env=env,
                cwd=self._get_secure_working_directory(),
                preexec_fn=self._setup_process_security if os.name != 'nt' else None
            )
            
            # Close slave fd in parent process
            os.close(slave_fd)
            
            # Track the process
            self.active_processes[process.pid] = process
            
            # Read output with timeout
            stdout_data = []
            stderr_data = []
            
            def read_output():
                """Read output from master fd."""
                try:
                    while True:
                        if select.select([master_fd], [], [], 0.1)[0]:
                            data = os.read(master_fd, 1024).decode('utf-8', errors='ignore')
                            if data:
                                stdout_data.append(data)
                            else:
                                break
                except Exception:
                    pass
            
            # Start reading thread
            read_thread = threading.Thread(target=read_output)
            read_thread.daemon = True
            read_thread.start()
            
            try:
                # Wait for process completion with timeout
                return_code = process.wait(timeout=timeout)
                
            except subprocess.TimeoutExpired:
                # Kill the process
                self._kill_process_tree(process.pid)
                return_code = -1
                
                return TerminalExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    stdout=''.join(stdout_data),
                    stderr=''.join(stderr_data),
                    return_code=return_code,
                    execution_time=time.time() - start_time,
                    error_message=f"Interactive command timed out after {timeout} seconds",
                    command=command,
                    interactive_mode=True,
                    security_validated=True
                )
            
            # Wait for read thread to finish
            read_thread.join(timeout=1.0)
            
            execution_time = time.time() - start_time
            
            # Determine status based on return code
            if return_code == 0:
                status = ExecutionStatus.COMPLETED
            else:
                status = ExecutionStatus.FAILED
            
            return TerminalExecutionResult(
                status=status,
                stdout=''.join(stdout_data),
                stderr=''.join(stderr_data),
                return_code=return_code,
                execution_time=execution_time,
                error_message=None if return_code == 0 else f"Interactive command exited with code {return_code}",
                command=command,
                interactive_mode=True,
                security_validated=True
            )
            
        except Exception as e:
            return TerminalExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=str(e),
                return_code=-1,
                execution_time=time.time() - start_time,
                error_message=f"Interactive execution error: {e}",
                command=command,
                interactive_mode=True,
                security_validated=True
            )
        
        finally:
            # Cleanup
            try:
                os.close(master_fd)
            except Exception:
                pass
            
            if process.pid in self.active_processes:
                del self.active_processes[process.pid]
    
    def _create_secure_environment(self) -> Dict[str, str]:
        """Create secure environment variables."""
        env = os.environ.copy()
        
        # Remove potentially dangerous environment variables
        dangerous_vars = [
            'PATH', 'LD_LIBRARY_PATH', 'LD_PRELOAD', 'PYTHONPATH',
            'NODE_PATH', 'JAVA_HOME', 'ANDROID_HOME'
        ]
        
        if self.security_policy.security_level == SecurityLevel.STRICT:
            # In strict mode, use minimal environment
            env = {
                'PATH': '/usr/bin:/bin',
                'HOME': '/tmp',
                'USER': 'nobody',
                'SHELL': '/bin/sh'
            }
        else:
            # In moderate/permissive mode, keep most variables but remove dangerous ones
            for var in dangerous_vars:
                if var in env and self.security_policy.security_level != SecurityLevel.PERMISSIVE:
                    del env[var]
        
        return env
    
    def _get_secure_working_directory(self) -> str:
        """Get secure working directory based on security policy."""
        if self.security_policy.security_level == SecurityLevel.STRICT:
            return '/tmp'
        else:
            return os.getcwd()
    
    def _setup_process_security(self):
        """Set up process security constraints (Unix only)."""
        try:
            # Set process group
            os.setpgrp()
            
            # Set resource limits
            import resource
            
            # Set memory limit
            memory_limit = self.security_policy.resource_limits.memory_limit_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
            
            # Set CPU time limit
            cpu_limit = self.security_policy.resource_limits.execution_timeout
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
            
            # Set file size limit
            file_size_limit = self.security_policy.file_system.max_file_size_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_FSIZE, (file_size_limit, file_size_limit))
            
            # Set process limit
            process_limit = self.security_policy.resource_limits.max_processes
            resource.setrlimit(resource.RLIMIT_NPROC, (process_limit, process_limit))
            
        except Exception as e:
            print(f"Warning: Could not set process security limits: {e}")
    
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
    
    def _log_execution(self, command: str, result: TerminalExecutionResult, security_check):
        """Log execution details for monitoring."""
        self.execution_history.append({
            "timestamp": time.time(),
            "command": command[:100],  # Truncate long commands
            "status": result.status.value,
            "execution_time": result.execution_time,
            "return_code": result.return_code,
            "stdout_length": len(result.stdout),
            "stderr_length": len(result.stderr),
            "security_passed": security_check.is_safe
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
        security_violations = sum(1 for e in self.execution_history if not e["security_passed"])
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "average_execution_time": avg_execution_time,
            "security_violations": security_violations,
            "security_violation_rate": security_violations / total_executions if total_executions > 0 else 0
        }
    
    def cleanup(self):
        """Clean up active processes."""
        for pid in list(self.active_processes.keys()):
            try:
                self._kill_process_tree(pid)
            except Exception:
                pass
        
        self.active_processes.clear()
    
    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup()


class SecurityCheckResult:
    """Result of security validation check."""
    
    def __init__(self, is_safe: bool, reason: str):
        self.is_safe = is_safe
        self.reason = reason
