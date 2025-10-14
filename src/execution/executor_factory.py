"""
Executor factory for clean execution mode selection and management.
"""

import os
from typing import Optional, Dict, Any
from ..core.models import AgentConfig
from ..core.security_policy import SecurityPolicyManager, SecurityLevel
from .sandbox import SandboxExecutor, DockerExecutor
from .e2b_executor import E2BExecutor, E2BExecutorWithSecurity
from .daytona_executor import DaytonaExecutor, DaytonaExecutorWithSecurity
from .multi_language_executor import MultiLanguageExecutor
from .terminal_executor import TerminalExecutor


class ExecutorFactory:
    """Factory for creating appropriate executors based on configuration."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.security_manager = SecurityPolicyManager(config.security_policy_file)
        self._executor_cache = {}
    
    def create_executor(self, executor_type: Optional[str] = None) -> Any:
        """
        Create an executor based on configuration and availability.
        
        Args:
            executor_type: Specific executor type to create (overrides auto-selection)
            
        Returns:
            Configured executor instance
        """
        # Use specified executor type or determine from config
        if executor_type:
            executor_mode = executor_type
        else:
            executor_mode = self._determine_executor_mode()
        
        # Check cache first
        cache_key = f"{executor_mode}_{self.config.security_level}"
        if cache_key in self._executor_cache:
            return self._executor_cache[cache_key]
        
        # Create new executor
        executor = self._create_executor_instance(executor_mode)
        
        # Cache the executor
        self._executor_cache[cache_key] = executor
        
        return executor
    
    def _determine_executor_mode(self) -> str:
        """Determine the best executor mode based on configuration and availability."""
        # Check for explicit configuration
        if self.config.execution_mode != "auto":
            return self.config.execution_mode
        
        # Check for preferred executor override
        if self.config.preferred_executor:
            return self.config.preferred_executor
        
        # Check environment variable
        env_mode = os.getenv("EXECUTION_MODE", "").lower()
        if env_mode:
            return env_mode
        
        # Auto-select based on security level and availability
        security_level = SecurityLevel(self.config.security_level)
        
        if security_level == SecurityLevel.STRICT:
            # Prefer cloud-based sandboxes for strict security
            if self._is_daytona_available():
                return "daytona"
            elif self._is_e2b_available():
                return "e2b"
            else:
                return "docker"
        
        elif security_level == SecurityLevel.MODERATE:
            # Prefer Docker for moderate security
            if self._is_docker_available():
                return "docker"
            elif self._is_daytona_available():
                return "daytona"
            elif self._is_e2b_available():
                return "e2b"
            else:
                return "sandbox"
        
        else:  # PERMISSIVE or CUSTOM
            # Use multi-language executor for permissive security
            return "multi"
    
    def _create_executor_instance(self, executor_mode: str) -> Any:
        """Create a specific executor instance."""
        security_policy = self.security_manager.get_policy_for_level(
            SecurityLevel(self.config.security_level)
        )
        
        if executor_mode == "daytona":
            return self._create_daytona_executor(security_policy)
        elif executor_mode == "e2b":
            return self._create_e2b_executor(security_policy)
        elif executor_mode == "docker":
            return self._create_docker_executor(security_policy)
        elif executor_mode == "multi":
            return self._create_multi_language_executor(security_policy)
        elif executor_mode == "terminal":
            return self._create_terminal_executor(security_policy)
        else:  # sandbox
            return self._create_sandbox_executor(security_policy)
    
    def _create_daytona_executor(self, security_policy) -> Any:
        """Create Daytona executor with security policy."""
        try:
            if self.config.enable_security_scanning:
                executor = DaytonaExecutorWithSecurity(self.config)
            else:
                executor = DaytonaExecutor(self.config)
            
            print("✓ Daytona executor created with enhanced security")
            return executor
            
        except Exception as e:
            print(f"Warning: Daytona not available, falling back to Docker: {e}")
            return self._create_docker_executor(security_policy)
    
    def _create_e2b_executor(self, security_policy) -> Any:
        """Create E2B executor with security policy."""
        try:
            if self.config.enable_security_scanning:
                executor = E2BExecutorWithSecurity(self.config)
            else:
                executor = E2BExecutor(self.config)
            
            print("✓ E2B executor created with enhanced security")
            return executor
            
        except Exception as e:
            print(f"Warning: E2B not available, falling back to Docker: {e}")
            return self._create_docker_executor(security_policy)
    
    def _create_docker_executor(self, security_policy) -> Any:
        """Create Docker executor with security policy."""
        try:
            executor = DockerExecutor(self.config)
            
            # Apply security policy to Docker executor
            docker_policy = self.security_manager.get_docker_security_policy()
            executor.security_policy.update(docker_policy)
            
            print("✓ Docker executor created with security policy")
            return executor
            
        except Exception as e:
            print(f"Warning: Docker not available, falling back to sandbox: {e}")
            return self._create_sandbox_executor(security_policy)
    
    def _create_multi_language_executor(self, security_policy) -> Any:
        """Create multi-language executor with security policy."""
        try:
            executor = MultiLanguageExecutor(self.config)
            print("✓ Multi-language executor created")
            return executor
            
        except Exception as e:
            print(f"Warning: Multi-language executor failed, falling back to sandbox: {e}")
            return self._create_sandbox_executor(security_policy)
    
    def _create_terminal_executor(self, security_policy) -> Any:
        """Create terminal executor with security policy."""
        try:
            executor = TerminalExecutor(self.config)
            print("✓ Terminal executor created with security policy")
            return executor
            
        except Exception as e:
            print(f"Warning: Terminal executor failed, falling back to sandbox: {e}")
            return self._create_sandbox_executor(security_policy)
    
    def _create_sandbox_executor(self, security_policy) -> Any:
        """Create basic sandbox executor with security policy."""
        executor = SandboxExecutor(self.config)
        print("✓ Basic sandbox executor created")
        return executor
    
    def _is_daytona_available(self) -> bool:
        """Check if Daytona is available."""
        try:
            import importlib
            importlib.import_module("daytona_sdk")
            return os.getenv("DAYTONA_API_KEY") is not None
        except ImportError:
            return False
    
    def _is_e2b_available(self) -> bool:
        """Check if E2B is available."""
        try:
            import importlib
            importlib.import_module("e2b")
            return os.getenv("E2B_API_KEY") is not None
        except ImportError:
            return False
    
    def _is_docker_available(self) -> bool:
        """Check if Docker is available."""
        try:
            import docker
            client = docker.from_env()
            client.ping()
            return True
        except Exception:
            return False
    
    def get_available_executors(self) -> Dict[str, bool]:
        """Get list of available executors."""
        return {
            "daytona": self._is_daytona_available(),
            "e2b": self._is_e2b_available(),
            "docker": self._is_docker_available(),
            "multi": True,  # Always available
            "terminal": True,  # Always available
            "sandbox": True  # Always available
        }
    
    def get_executor_info(self, executor_type: str) -> Dict[str, Any]:
        """Get information about a specific executor type."""
        info = {
            "daytona": {
                "name": "Daytona Cloud Sandbox",
                "description": "Cloud-based sandboxed execution with enterprise security",
                "security_level": "high",
                "features": ["cloud isolation", "enterprise security", "multi-language"],
                "requirements": ["DAYTONA_API_KEY", "daytona-sdk package"]
            },
            "e2b": {
                "name": "E2B Sandbox",
                "description": "Secure cloud sandbox for code execution",
                "security_level": "high",
                "features": ["cloud isolation", "secure execution", "multi-language"],
                "requirements": ["E2B_API_KEY", "e2b package"]
            },
            "docker": {
                "name": "Docker Container",
                "description": "Containerized execution with security policies",
                "security_level": "medium",
                "features": ["container isolation", "resource limits", "security policies"],
                "requirements": ["Docker", "docker package"]
            },
            "multi": {
                "name": "Multi-Language Executor",
                "description": "Native execution for multiple programming languages",
                "security_level": "low",
                "features": ["multi-language", "native execution", "fast"],
                "requirements": ["Language runtimes"]
            },
            "terminal": {
                "name": "Terminal Executor",
                "description": "Safe shell command execution with pty integration",
                "security_level": "medium",
                "features": ["shell commands", "pty support", "security validation", "interactive commands"],
                "requirements": ["pty module", "subprocess"]
            },
            "sandbox": {
                "name": "Basic Sandbox",
                "description": "Basic sandboxed execution with process isolation",
                "security_level": "low",
                "features": ["process isolation", "timeout", "basic security"],
                "requirements": ["psutil package"]
            }
        }
        
        return info.get(executor_type, {})
    
    def cleanup_all_executors(self):
        """Clean up all cached executors."""
        for executor in self._executor_cache.values():
            if hasattr(executor, 'cleanup'):
                try:
                    executor.cleanup()
                except Exception as e:
                    print(f"Warning: Error cleaning up executor: {e}")
        
        self._executor_cache.clear()
        print("✓ All executors cleaned up")
    
    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup_all_executors()
