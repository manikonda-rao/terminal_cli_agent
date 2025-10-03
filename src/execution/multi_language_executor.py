"""
Multi-language execution system with comprehensive language support.
"""

import os
import subprocess
import tempfile
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from enum import Enum
from dataclasses import dataclass

from ..core.models import CodeBlock, ExecutionResult, ExecutionStatus, AgentConfig


class LanguageRuntime(str, Enum):
    """Supported language runtimes."""
    PYTHON = "python"
    NODEJS = "nodejs"
    JAVA = "java"
    GCC = "gcc"
    GPP = "gpp"
    RUSTC = "rustc"
    GO = "go"
    PHP = "php"
    RUBY = "ruby"
    PERL = "perl"
    BASH = "bash"
    POWERSHELL = "powershell"


@dataclass
class LanguageConfig:
    """Configuration for a programming language."""
    name: str
    runtime: LanguageRuntime
    file_extension: str
    compile_command: Optional[List[str]] = None
    run_command: List[str] = None
    requires_compilation: bool = False
    timeout_multiplier: float = 1.0
    memory_multiplier: float = 1.0


class MultiLanguageExecutor:
    """Executes code in multiple programming languages with proper runtime management."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.language_configs = self._initialize_language_configs()
        self.runtime_availability = self._check_runtime_availability()
        self.execution_history = []
    
    def _initialize_language_configs(self) -> Dict[str, LanguageConfig]:
        """Initialize configurations for all supported languages."""
        return {
            "python": LanguageConfig(
                name="Python",
                runtime=LanguageRuntime.PYTHON,
                file_extension=".py",
                run_command=["python", "{file}"],
                timeout_multiplier=1.0
            ),
            "javascript": LanguageConfig(
                name="JavaScript",
                runtime=LanguageRuntime.NODEJS,
                file_extension=".js",
                run_command=["node", "{file}"],
                timeout_multiplier=1.0
            ),
            "typescript": LanguageConfig(
                name="TypeScript",
                runtime=LanguageRuntime.NODEJS,
                file_extension=".ts",
                compile_command=["tsc", "{file}"],
                run_command=["node", "{file}.js"],
                requires_compilation=True,
                timeout_multiplier=1.2
            ),
            "java": LanguageConfig(
                name="Java",
                runtime=LanguageRuntime.JAVA,
                file_extension=".java",
                compile_command=["javac", "{file}"],
                run_command=["java", "{class_name}"],
                requires_compilation=True,
                timeout_multiplier=1.5,
                memory_multiplier=2.0
            ),
            "cpp": LanguageConfig(
                name="C++",
                runtime=LanguageRuntime.GPP,
                file_extension=".cpp",
                compile_command=["g++", "-o", "{output}", "{file}"],
                run_command=["./{output}"],
                requires_compilation=True,
                timeout_multiplier=1.0
            ),
            "c": LanguageConfig(
                name="C",
                runtime=LanguageRuntime.GCC,
                file_extension=".c",
                compile_command=["gcc", "-o", "{output}", "{file}"],
                run_command=["./{output}"],
                requires_compilation=True,
                timeout_multiplier=1.0
            ),
            "rust": LanguageConfig(
                name="Rust",
                runtime=LanguageRuntime.RUSTC,
                file_extension=".rs",
                compile_command=["rustc", "-o", "{output}", "{file}"],
                run_command=["./{output}"],
                requires_compilation=True,
                timeout_multiplier=2.0,
                memory_multiplier=1.5
            ),
            "go": LanguageConfig(
                name="Go",
                runtime=LanguageRuntime.GO,
                file_extension=".go",
                run_command=["go", "run", "{file}"],
                timeout_multiplier=1.0
            ),
            "php": LanguageConfig(
                name="PHP",
                runtime=LanguageRuntime.PHP,
                file_extension=".php",
                run_command=["php", "{file}"],
                timeout_multiplier=1.0
            ),
            "ruby": LanguageConfig(
                name="Ruby",
                runtime=LanguageRuntime.RUBY,
                file_extension=".rb",
                run_command=["ruby", "{file}"],
                timeout_multiplier=1.0
            ),
            "perl": LanguageConfig(
                name="Perl",
                runtime=LanguageRuntime.PERL,
                file_extension=".pl",
                run_command=["perl", "{file}"],
                timeout_multiplier=1.0
            ),
            "bash": LanguageConfig(
                name="Bash",
                runtime=LanguageRuntime.BASH,
                file_extension=".sh",
                run_command=["bash", "{file}"],
                timeout_multiplier=1.0
            ),
            "powershell": LanguageConfig(
                name="PowerShell",
                runtime=LanguageRuntime.POWERSHELL,
                file_extension=".ps1",
                run_command=["powershell", "-File", "{file}"],
                timeout_multiplier=1.0
            )
        }
    
    def _check_runtime_availability(self) -> Dict[str, bool]:
        """Check which language runtimes are available on the system."""
        availability = {}
        
        for lang, config in self.language_configs.items():
            try:
                if config.runtime == LanguageRuntime.PYTHON:
                    result = subprocess.run(["python", "--version"], 
                                          capture_output=True, timeout=5)
                    availability[lang] = result.returncode == 0
                elif config.runtime == LanguageRuntime.NODEJS:
                    result = subprocess.run(["node", "--version"], 
                                          capture_output=True, timeout=5)
                    availability[lang] = result.returncode == 0
                elif config.runtime == LanguageRuntime.JAVA:
                    result = subprocess.run(["java", "-version"], 
                                          capture_output=True, timeout=5)
                    availability[lang] = result.returncode == 0
                elif config.runtime == LanguageRuntime.GCC:
                    result = subprocess.run(["gcc", "--version"], 
                                          capture_output=True, timeout=5)
                    availability[lang] = result.returncode == 0
                elif config.runtime == LanguageRuntime.GPP:
                    result = subprocess.run(["g++", "--version"], 
                                          capture_output=True, timeout=5)
                    availability[lang] = result.returncode == 0
                elif config.runtime == LanguageRuntime.RUSTC:
                    result = subprocess.run(["rustc", "--version"], 
                                          capture_output=True, timeout=5)
                    availability[lang] = result.returncode == 0
                elif config.runtime == LanguageRuntime.GO:
                    result = subprocess.run(["go", "version"], 
                                          capture_output=True, timeout=5)
                    availability[lang] = result.returncode == 0
                elif config.runtime == LanguageRuntime.PHP:
                    result = subprocess.run(["php", "--version"], 
                                          capture_output=True, timeout=5)
                    availability[lang] = result.returncode == 0
                elif config.runtime == LanguageRuntime.RUBY:
                    result = subprocess.run(["ruby", "--version"], 
                                          capture_output=True, timeout=5)
                    availability[lang] = result.returncode == 0
                elif config.runtime == LanguageRuntime.PERL:
                    result = subprocess.run(["perl", "--version"], 
                                          capture_output=True, timeout=5)
                    availability[lang] = result.returncode == 0
                elif config.runtime == LanguageRuntime.BASH:
                    result = subprocess.run(["bash", "--version"], 
                                          capture_output=True, timeout=5)
                    availability[lang] = result.returncode == 0
                elif config.runtime == LanguageRuntime.POWERSHELL:
                    result = subprocess.run(["powershell", "--version"], 
                                          capture_output=True, timeout=5)
                    availability[lang] = result.returncode == 0
                else:
                    availability[lang] = False
                    
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                availability[lang] = False
        
        return availability
    
    def execute_code(self, code_block: CodeBlock, timeout: Optional[int] = None) -> ExecutionResult:
        """
        Execute code in the appropriate language runtime.
        
        Args:
            code_block: Code to execute
            timeout: Execution timeout in seconds
            
        Returns:
            Execution result with output and status
        """
        language = code_block.language.value
        
        # Check if language is supported and available
        if language not in self.language_configs:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=f"Unsupported language: {language}",
                error_message=f"Language {language} is not supported"
            )
        
        if not self.runtime_availability.get(language, False):
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=f"Runtime not available: {language}",
                error_message=f"{language} runtime is not installed or not available"
            )
        
        config = self.language_configs[language]
        timeout = timeout or int(self.config.max_execution_time * config.timeout_multiplier)
        
        # Create temporary directory for execution
        temp_dir = tempfile.mkdtemp(prefix=f"coding_agent_{language}_")
        
        try:
            # Write code to file
            file_path = self._write_code_file(temp_dir, code_block, config)
            
            # Compile if necessary
            if config.requires_compilation:
                compile_result = self._compile_code(file_path, config, timeout)
                if compile_result.status != ExecutionStatus.COMPLETED:
                    return compile_result
            
            # Execute the code
            result = self._run_code(file_path, config, timeout)
            
            # Log execution
            self._log_execution(code_block, result)
            
            return result
            
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=str(e),
                error_message=f"Execution error: {e}"
            )
        
        finally:
            # Cleanup
            self._cleanup_temp_dir(temp_dir)
    
    def _write_code_file(self, temp_dir: str, code_block: CodeBlock, config: LanguageConfig) -> str:
        """Write code block to a temporary file."""
        file_path = os.path.join(temp_dir, f"code{config.file_extension}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code_block.content)
        
        return file_path
    
    def _compile_code(self, file_path: str, config: LanguageConfig, timeout: int) -> ExecutionResult:
        """Compile code if compilation is required."""
        start_time = time.time()
        
        try:
            # Build compile command
            if config.compile_command:
                cmd = []
                for part in config.compile_command:
                    if "{file}" in part:
                        cmd.append(part.replace("{file}", file_path))
                    elif "{output}" in part:
                        output_name = Path(file_path).stem
                        cmd.append(part.replace("{output}", output_name))
                    else:
                        cmd.append(part)
                
                # Run compilation
                result = subprocess.run(
                    cmd,
                    cwd=os.path.dirname(file_path),
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                if result.returncode == 0:
                    return ExecutionResult(
                        status=ExecutionStatus.COMPLETED,
                        stdout=result.stdout,
                        stderr=result.stderr,
                        execution_time=time.time() - start_time
                    )
                else:
                    return ExecutionResult(
                        status=ExecutionStatus.FAILED,
                        stdout=result.stdout,
                        stderr=result.stderr,
                        execution_time=time.time() - start_time,
                        error_message=f"Compilation failed with code {result.returncode}"
                    )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.COMPLETED,
                    execution_time=time.time() - start_time
                )
                
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                execution_time=time.time() - start_time,
                error_message=f"Compilation timed out after {timeout} seconds"
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=str(e),
                execution_time=time.time() - start_time,
                error_message=f"Compilation error: {e}"
            )
    
    def _run_code(self, file_path: str, config: LanguageConfig, timeout: int) -> ExecutionResult:
        """Run the compiled or interpreted code."""
        start_time = time.time()
        
        try:
            # Build run command
            cmd = []
            for part in config.run_command:
                if "{file}" in part:
                    cmd.append(part.replace("{file}", file_path))
                elif "{class_name}" in part:
                    class_name = Path(file_path).stem
                    cmd.append(part.replace("{class_name}", class_name))
                elif "{output}" in part:
                    output_name = Path(file_path).stem
                    cmd.append(part.replace("{output}", output_name))
                else:
                    cmd.append(part)
            
            # Run the code
            result = subprocess.run(
                cmd,
                cwd=os.path.dirname(file_path),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                status = ExecutionStatus.COMPLETED
                error_message = None
            else:
                status = ExecutionStatus.FAILED
                error_message = f"Process exited with code {result.returncode}"
            
            return ExecutionResult(
                status=status,
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
                execution_time=execution_time,
                error_message=error_message
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                execution_time=time.time() - start_time,
                error_message=f"Execution timed out after {timeout} seconds"
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                stderr=str(e),
                execution_time=time.time() - start_time,
                error_message=f"Execution error: {e}"
            )
    
    def _cleanup_temp_dir(self, temp_dir: str):
        """Clean up temporary directory."""
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Warning: Could not remove temp directory {temp_dir}: {e}")
    
    def _log_execution(self, code_block: CodeBlock, result: ExecutionResult):
        """Log execution details for monitoring."""
        self.execution_history.append({
            "timestamp": time.time(),
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
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self.language_configs.keys())
    
    def get_available_languages(self) -> List[str]:
        """Get list of languages with available runtimes."""
        return [lang for lang, available in self.runtime_availability.items() if available]
    
    def get_language_info(self, language: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific language."""
        if language not in self.language_configs:
            return None
        
        config = self.language_configs[language]
        return {
            "name": config.name,
            "runtime": config.runtime.value,
            "file_extension": config.file_extension,
            "requires_compilation": config.requires_compilation,
            "timeout_multiplier": config.timeout_multiplier,
            "memory_multiplier": config.memory_multiplier,
            "available": self.runtime_availability.get(language, False)
        }
    
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
            "supported_languages": self.get_supported_languages(),
            "available_languages": self.get_available_languages()
        }
