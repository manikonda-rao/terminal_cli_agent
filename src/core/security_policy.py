"""
Configurable security policy system for code execution.
"""

import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field
from enum import Enum


class SecurityLevel(str, Enum):
    """Security levels for code execution."""
    STRICT = "strict"
    MODERATE = "moderate"
    PERMISSIVE = "permissive"
    CUSTOM = "custom"


class NetworkPolicy(str, Enum):
    """Network access policies."""
    DISABLED = "disabled"
    RESTRICTED = "restricted"
    ALLOWED = "allowed"


class FileSystemPolicy(BaseModel):
    """File system access policy."""
    read_only_dirs: List[str] = Field(default_factory=list)
    read_write_dirs: List[str] = Field(default_factory=list)
    blocked_dirs: List[str] = Field(default_factory=list)
    max_file_size_mb: int = Field(default=100)


class ResourceLimits(BaseModel):
    """Resource limits for execution."""
    cpu_limit: str = Field(default="1")
    memory_limit_mb: int = Field(default=512)
    execution_timeout: int = Field(default=30)
    max_output_size_mb: int = Field(default=10)
    max_processes: int = Field(default=5)


class SecurityPatterns(BaseModel):
    """Security patterns for code scanning."""
    dangerous_patterns: List[str] = Field(default_factory=list)
    allowed_patterns: List[str] = Field(default_factory=list)
    custom_patterns: List[str] = Field(default_factory=list)


class TerminalSecurityPolicy(BaseModel):
    """Security policy for terminal command execution."""
    dangerous_commands: List[str] = Field(default_factory=list)
    allowed_commands: List[str] = Field(default_factory=list)
    blocked_patterns: List[str] = Field(default_factory=list)
    max_command_length: int = Field(default=1000)
    enable_interactive_mode: bool = Field(default=True)
    require_command_whitelist: bool = Field(default=False)


class SecurityPolicy(BaseModel):
    """Comprehensive security policy configuration."""
    security_level: SecurityLevel = Field(default=SecurityLevel.MODERATE)
    network_policy: NetworkPolicy = Field(default=NetworkPolicy.RESTRICTED)
    file_system: FileSystemPolicy = Field(default_factory=FileSystemPolicy)
    resource_limits: ResourceLimits = Field(default_factory=ResourceLimits)
    patterns: SecurityPatterns = Field(default_factory=SecurityPatterns)
    terminal_security: TerminalSecurityPolicy = Field(default_factory=TerminalSecurityPolicy)
    enable_code_analysis: bool = Field(default=True)
    enable_security_scanning: bool = Field(default=True)
    enable_resource_monitoring: bool = Field(default=True)
    sandbox_mode: str = Field(default="docker")  # docker, e2b, daytona, sandbox, terminal


class SecurityPolicyManager:
    """Manages security policies with configuration file support."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "security_policy.json"
        self.policy = self._load_policy()
    
    def _load_policy(self) -> SecurityPolicy:
        """Load security policy from file or create default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return SecurityPolicy(**data)
            except Exception as e:
                print(f"Warning: Could not load security policy from {self.config_file}: {e}")
                print("Using default security policy")
        
        return self._create_default_policy()
    
    def _create_default_policy(self) -> SecurityPolicy:
        """Create default security policy."""
        return SecurityPolicy(
            security_level=SecurityLevel.MODERATE,
            network_policy=NetworkPolicy.RESTRICTED,
            file_system=FileSystemPolicy(
                read_only_dirs=["/app/data", "/usr/lib"],
                read_write_dirs=["/tmp", "/app/logs"],
                blocked_dirs=["/etc", "/root", "/home"],
                max_file_size_mb=100
            ),
            resource_limits=ResourceLimits(
                cpu_limit="1",
                memory_limit_mb=512,
                execution_timeout=30,
                max_output_size_mb=10,
                max_processes=5
            ),
            patterns=SecurityPatterns(
                dangerous_patterns=[
                    r'import\s+os',
                    r'import\s+subprocess',
                    r'import\s+socket',
                    r'os\.system\s*\(',
                    r'subprocess\.run\s*\(',
                    r'open\s*\(',
                    r'exec\s*\(',
                    r'eval\s*\(',
                ],
                allowed_patterns=[
                    r'import\s+math',
                    r'import\s+random',
                    r'import\s+datetime',
                    r'import\s+json',
                    r'import\s+collections',
                    r'from\s+math\s+import',
                    r'from\s+random\s+import',
                    r'from\s+datetime\s+import',
                    r'from\s+json\s+import',
                ]
            ),
            terminal_security=TerminalSecurityPolicy(
                dangerous_commands=[
                    'rm', 'del', 'format', 'fdisk', 'mkfs', 'dd', 'shred',
                    'sudo', 'su', 'passwd', 'chmod', 'chown', 'mount', 'umount',
                    'kill', 'killall', 'pkill', 'xkill', 'halt', 'shutdown', 'reboot',
                    'curl', 'wget', 'nc', 'netcat', 'telnet', 'ssh', 'scp', 'rsync',
                    'crontab', 'at', 'systemctl', 'service', 'initctl'
                ],
                allowed_commands=[
                    'ls', 'dir', 'pwd', 'cd', 'cat', 'type', 'head', 'tail', 'grep',
                    'find', 'which', 'where', 'echo', 'print', 'date', 'time', 'whoami',
                    'git', 'npm', 'pip', 'python', 'node', 'java', 'gcc', 'g++',
                    'make', 'cmake', 'docker', 'kubectl', 'terraform', 'ansible',
                    'ps', 'top', 'htop', 'df', 'du', 'free', 'uptime', 'uname',
                    'mkdir', 'touch', 'cp', 'copy', 'mv', 'move', 'ln', 'link'
                ],
                blocked_patterns=[
                    r'\|\s*rm\s+',
                    r'\|\s*del\s+',
                    r'\|\s*sudo\s+',
                    r'\|\s*su\s+',
                    r'&&\s*rm\s+',
                    r'&&\s*del\s+',
                    r'&&\s*sudo\s+',
                    r'&&\s*su\s+',
                    r';\s*rm\s+',
                    r';\s*del\s+',
                    r';\s*sudo\s+',
                    r';\s*su\s+'
                ],
                max_command_length=1000,
                enable_interactive_mode=True,
                require_command_whitelist=False
            )
        )
    
    def save_policy(self, policy: Optional[SecurityPolicy] = None) -> None:
        """Save security policy to file."""
        if policy is None:
            policy = self.policy
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(policy.model_dump(), f, indent=2, default=str)
            print(f"✓ Security policy saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving security policy: {e}")
    
    def update_policy(self, **kwargs) -> SecurityPolicy:
        """Update security policy with new values."""
        current_data = self.policy.model_dump()
        current_data.update(kwargs)
        self.policy = SecurityPolicy(**current_data)
        return self.policy
    
    def get_policy_for_level(self, level: SecurityLevel) -> SecurityPolicy:
        """Get predefined policy for security level."""
        if level == SecurityLevel.STRICT:
            return SecurityPolicy(
                security_level=SecurityLevel.STRICT,
                network_policy=NetworkPolicy.DISABLED,
                file_system=FileSystemPolicy(
                    read_only_dirs=["/usr/lib", "/lib"],
                    read_write_dirs=["/tmp"],
                    blocked_dirs=["/etc", "/root", "/home", "/var", "/opt"],
                    max_file_size_mb=50
                ),
                resource_limits=ResourceLimits(
                    cpu_limit="0.5",
                    memory_limit_mb=256,
                    execution_timeout=15,
                    max_output_size_mb=5,
                    max_processes=2
                ),
                patterns=SecurityPatterns(
                    dangerous_patterns=[
                        r'import\s+os',
                        r'import\s+subprocess',
                        r'import\s+socket',
                        r'import\s+urllib',
                        r'import\s+requests',
                        r'os\.system\s*\(',
                        r'os\.popen\s*\(',
                        r'subprocess\.run\s*\(',
                        r'subprocess\.call\s*\(',
                        r'subprocess\.Popen\s*\(',
                        r'open\s*\(',
                        r'file\s*\(',
                        r'exec\s*\(',
                        r'eval\s*\(',
                        r'__import__\s*\(',
                        r'compile\s*\(',
                    ],
                    allowed_patterns=[
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
                ),
                terminal_security=TerminalSecurityPolicy(
                    dangerous_commands=[
                        'rm', 'del', 'format', 'fdisk', 'mkfs', 'dd', 'shred',
                        'sudo', 'su', 'passwd', 'chmod', 'chown', 'mount', 'umount',
                        'kill', 'killall', 'pkill', 'xkill', 'halt', 'shutdown', 'reboot',
                        'curl', 'wget', 'nc', 'netcat', 'telnet', 'ssh', 'scp', 'rsync',
                        'crontab', 'at', 'systemctl', 'service', 'initctl', 'useradd',
                        'userdel', 'groupadd', 'groupdel', 'visudo', 'chroot'
                    ],
                    allowed_commands=[
                        'ls', 'dir', 'pwd', 'cat', 'type', 'head', 'tail', 'grep',
                        'find', 'which', 'where', 'echo', 'print', 'date', 'time',
                        'git', 'npm', 'pip', 'python', 'node', 'java', 'gcc', 'g++',
                        'make', 'cmake', 'ps', 'top', 'htop', 'df', 'du', 'free',
                        'uptime', 'uname', 'mkdir', 'touch', 'cp', 'copy', 'mv', 'move'
                    ],
                    blocked_patterns=[
                        r'\|\s*rm\s+', r'\|\s*del\s+', r'\|\s*sudo\s+', r'\|\s*su\s+',
                        r'&&\s*rm\s+', r'&&\s*del\s+', r'&&\s*sudo\s+', r'&&\s*su\s+',
                        r';\s*rm\s+', r';\s*del\s+', r';\s*sudo\s+', r';\s*su\s+',
                        r'\|\s*kill\s+', r'&&\s*kill\s+', r';\s*kill\s+'
                    ],
                    max_command_length=500,
                    enable_interactive_mode=False,
                    require_command_whitelist=True
                )
            )
        
        elif level == SecurityLevel.PERMISSIVE:
            return SecurityPolicy(
                security_level=SecurityLevel.PERMISSIVE,
                network_policy=NetworkPolicy.ALLOWED,
                file_system=FileSystemPolicy(
                    read_only_dirs=[],
                    read_write_dirs=["/tmp", "/app"],
                    blocked_dirs=["/etc/passwd", "/etc/shadow"],
                    max_file_size_mb=500
                ),
                resource_limits=ResourceLimits(
                    cpu_limit="2",
                    memory_limit_mb=1024,
                    execution_timeout=60,
                    max_output_size_mb=50,
                    max_processes=10
                ),
                patterns=SecurityPatterns(
                    dangerous_patterns=[
                        r'import\s+subprocess',
                        r'subprocess\.run\s*\(',
                        r'subprocess\.call\s*\(',
                        r'subprocess\.Popen\s*\(',
                        r'exec\s*\(',
                        r'eval\s*\(',
                    ],
                    allowed_patterns=[]
                ),
                terminal_security=TerminalSecurityPolicy(
                    dangerous_commands=[
                        'format', 'fdisk', 'mkfs', 'dd', 'shred', 'halt', 'shutdown', 'reboot'
                    ],
                    allowed_commands=[
                        'ls', 'dir', 'pwd', 'cd', 'cat', 'type', 'head', 'tail', 'grep',
                        'find', 'which', 'where', 'echo', 'print', 'date', 'time', 'whoami',
                        'git', 'npm', 'pip', 'python', 'node', 'java', 'gcc', 'g++',
                        'make', 'cmake', 'docker', 'kubectl', 'terraform', 'ansible',
                        'ps', 'top', 'htop', 'df', 'du', 'free', 'uptime', 'uname',
                        'mkdir', 'touch', 'cp', 'copy', 'mv', 'move', 'ln', 'link',
                        'rm', 'del', 'sudo', 'su', 'chmod', 'chown', 'kill', 'killall',
                        'curl', 'wget', 'ssh', 'scp', 'rsync', 'crontab', 'at'
                    ],
                    blocked_patterns=[
                        r'\|\s*format\s+', r'\|\s*fdisk\s+', r'\|\s*mkfs\s+',
                        r'&&\s*format\s+', r'&&\s*fdisk\s+', r'&&\s*mkfs\s+',
                        r';\s*format\s+', r';\s*fdisk\s+', r';\s*mkfs\s+'
                    ],
                    max_command_length=2000,
                    enable_interactive_mode=True,
                    require_command_whitelist=False
                )
            )
        
        else:  # MODERATE
            return self._create_default_policy()
    
    def validate_policy(self, policy: SecurityPolicy) -> List[str]:
        """Validate security policy configuration."""
        issues = []
        
        # Validate resource limits
        if policy.resource_limits.memory_limit_mb <= 0:
            issues.append("Memory limit must be positive")
        
        if policy.resource_limits.execution_timeout <= 0:
            issues.append("Execution timeout must be positive")
        
        if policy.resource_limits.max_output_size_mb <= 0:
            issues.append("Max output size must be positive")
        
        # Validate file system policy
        if policy.file_system.max_file_size_mb <= 0:
            issues.append("Max file size must be positive")
        
        # Validate patterns
        if not policy.patterns.dangerous_patterns and policy.security_level != SecurityLevel.PERMISSIVE:
            issues.append("Dangerous patterns should be defined for non-permissive security levels")
        
        return issues
    
    def get_docker_security_policy(self) -> Dict[str, Any]:
        """Convert security policy to Docker security configuration."""
        policy = self.policy
        
        # Build Docker security options
        security_opts = ["no-new-privileges:true"]
        
        if policy.security_level == SecurityLevel.STRICT:
            security_opts.extend([
                "seccomp:unconfined",
                "apparmor:unconfined"
            ])
        
        # Build capability drops
        cap_drops = ["ALL"]
        if policy.security_level == SecurityLevel.PERMISSIVE:
            cap_drops = ["SYS_ADMIN", "SYS_MODULE"]
        
        # Build tmpfs configuration
        tmpfs = {}
        if policy.file_system.read_write_dirs:
            for dir_path in policy.file_system.read_write_dirs:
                if dir_path.startswith("/tmp"):
                    tmpfs[dir_path] = f"rw,size={policy.resource_limits.memory_limit_mb}m,noexec,nosuid,nodev"
        
        return {
            "read_only": policy.security_level == SecurityLevel.STRICT,
            "no_new_privileges": True,
            "user": "nobody" if policy.security_level == SecurityLevel.STRICT else "root",
            "memory_limit": f"{policy.resource_limits.memory_limit_mb}m",
            "cpu_limit": policy.resource_limits.cpu_limit,
            "network_disabled": policy.network_policy == NetworkPolicy.DISABLED,
            "cap_drop": cap_drops,
            "security_opt": security_opts,
            "tmpfs": tmpfs,
            "read_only_dirs": policy.file_system.read_only_dirs,
            "blocked_dirs": policy.file_system.blocked_dirs,
            "max_file_size_mb": policy.file_system.max_file_size_mb
        }
    
    def get_e2b_security_policy(self) -> Dict[str, Any]:
        """Convert security policy to E2B security configuration."""
        policy = self.policy
        
        return {
            "timeout": policy.resource_limits.execution_timeout,
            "memory_limit": policy.resource_limits.memory_limit_mb,
            "network_access": policy.network_policy.value,
            "file_system_access": {
                "read_only": policy.file_system.read_only_dirs,
                "read_write": policy.file_system.read_write_dirs,
                "blocked": policy.file_system.blocked_dirs
            },
            "resource_limits": {
                "cpu": policy.resource_limits.cpu_limit,
                "memory_mb": policy.resource_limits.memory_limit_mb,
                "max_output_mb": policy.resource_limits.max_output_size_mb,
                "max_processes": policy.resource_limits.max_processes
            },
            "security_level": policy.security_level.value,
            "enable_scanning": policy.enable_security_scanning
        }
    
    def get_daytona_security_policy(self) -> Dict[str, Any]:
        """Convert security policy to Daytona security configuration."""
        policy = self.policy
        
        return {
            "timeout": policy.resource_limits.execution_timeout,
            "memory_limit": policy.resource_limits.memory_limit_mb,
            "network_policy": policy.network_policy.value,
            "file_system": {
                "read_only_dirs": policy.file_system.read_only_dirs,
                "read_write_dirs": policy.file_system.read_write_dirs,
                "blocked_dirs": policy.file_system.blocked_dirs,
                "max_file_size_mb": policy.file_system.max_file_size_mb
            },
            "resource_limits": {
                "cpu_limit": policy.resource_limits.cpu_limit,
                "memory_limit_mb": policy.resource_limits.memory_limit_mb,
                "execution_timeout": policy.resource_limits.execution_timeout,
                "max_output_size_mb": policy.resource_limits.max_output_size_mb,
                "max_processes": policy.resource_limits.max_processes
            },
            "security_patterns": {
                "dangerous": policy.patterns.dangerous_patterns,
                "allowed": policy.patterns.allowed_patterns,
                "custom": policy.patterns.custom_patterns
            },
            "security_level": policy.security_level.value,
            "enable_code_analysis": policy.enable_code_analysis,
            "enable_security_scanning": policy.enable_security_scanning,
            "enable_resource_monitoring": policy.enable_resource_monitoring
        }
    
    def get_terminal_security_policy(self) -> Dict[str, Any]:
        """Convert security policy to terminal security configuration."""
        policy = self.policy
        
        return {
            "dangerous_commands": policy.terminal_security.dangerous_commands,
            "allowed_commands": policy.terminal_security.allowed_commands,
            "blocked_patterns": policy.terminal_security.blocked_patterns,
            "max_command_length": policy.terminal_security.max_command_length,
            "enable_interactive_mode": policy.terminal_security.enable_interactive_mode,
            "require_command_whitelist": policy.terminal_security.require_command_whitelist,
            "security_level": policy.security_level.value,
            "execution_timeout": policy.resource_limits.execution_timeout,
            "memory_limit_mb": policy.resource_limits.memory_limit_mb,
            "max_processes": policy.resource_limits.max_processes
        }


def create_security_policy_template() -> str:
    """Create a security policy template file."""
    template = {
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
            "dangerous_patterns": [
                "import\\s+os",
                "import\\s+subprocess",
                "import\\s+socket",
                "os\\.system\\s*\\(",
                "subprocess\\.run\\s*\\(",
                "open\\s*\\(",
                "exec\\s*\\(",
                "eval\\s*\\("
            ],
            "allowed_patterns": [
                "import\\s+math",
                "import\\s+random",
                "import\\s+datetime",
                "import\\s+json",
                "import\\s+collections",
                "from\\s+math\\s+import",
                "from\\s+random\\s+import",
                "from\\s+datetime\\s+import",
                "from\\s+json\\s+import"
            ],
            "custom_patterns": []
        },
        "terminal_security": {
            "dangerous_commands": [
                "rm", "del", "format", "fdisk", "mkfs", "dd", "shred",
                "sudo", "su", "passwd", "chmod", "chown", "mount", "umount",
                "kill", "killall", "pkill", "xkill", "halt", "shutdown", "reboot",
                "curl", "wget", "nc", "netcat", "telnet", "ssh", "scp", "rsync",
                "crontab", "at", "systemctl", "service", "initctl"
            ],
            "allowed_commands": [
                "ls", "dir", "pwd", "cd", "cat", "type", "head", "tail", "grep",
                "find", "which", "where", "echo", "print", "date", "time", "whoami",
                "git", "npm", "pip", "python", "node", "java", "gcc", "g++",
                "make", "cmake", "docker", "kubectl", "terraform", "ansible",
                "ps", "top", "htop", "df", "du", "free", "uptime", "uname",
                "mkdir", "touch", "cp", "copy", "mv", "move", "ln", "link"
            ],
            "blocked_patterns": [
                "\\|\\s*rm\\s+", "\\|\\s*del\\s+", "\\|\\s*sudo\\s+", "\\|\\s*su\\s+",
                "&&\\s*rm\\s+", "&&\\s*del\\s+", "&&\\s*sudo\\s+", "&&\\s*su\\s+",
                ";\\s*rm\\s+", ";\\s*del\\s+", ";\\s*sudo\\s+", ";\\s*su\\s+"
            ],
            "max_command_length": 1000,
            "enable_interactive_mode": True,
            "require_command_whitelist": False
        },
        "enable_code_analysis": True,
        "enable_security_scanning": True,
        "enable_resource_monitoring": True,
        "sandbox_mode": "docker"
    }
    
    return json.dumps(template, indent=2)
