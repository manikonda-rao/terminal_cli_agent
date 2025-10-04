"""
Static code analysis system for safety validation and code quality assessment.
"""

import ast
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

try:
    import bandit
    from bandit.core import manager
    BANDIT_AVAILABLE = True
except ImportError:
    BANDIT_AVAILABLE = False

try:
    import pylint
    from pylint import lint
    PYLINT_AVAILABLE = True
except ImportError:
    PYLINT_AVAILABLE = False


class SeverityLevel(str, Enum):
    """Severity levels for code analysis issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueType(str, Enum):
    """Types of code analysis issues."""
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    BUG = "bug"
    COMPLEXITY = "complexity"
    MAINTAINABILITY = "maintainability"


@dataclass
class CodeIssue:
    """Represents a code analysis issue."""
    type: IssueType
    severity: SeverityLevel
    message: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    file_path: Optional[str] = None
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    rule_id: Optional[str] = None


@dataclass
class AnalysisResult:
    """Result of code analysis."""
    is_safe: bool
    issues: List[CodeIssue]
    score: float  # 0-100 quality score
    complexity_score: float
    maintainability_score: float
    security_score: float
    summary: Dict[str, Any]


class StaticCodeAnalyzer:
    """Comprehensive static code analysis system."""
    
    def __init__(self):
        self.security_patterns = self._load_security_patterns()
        self.performance_patterns = self._load_performance_patterns()
        self.style_patterns = self._load_style_patterns()
        self.bug_patterns = self._load_bug_patterns()
    
    def analyze_code(self, code_block) -> AnalysisResult:
        """
        Perform comprehensive static analysis on code.
        
        Args:
            code_block: CodeBlock object to analyze
            
        Returns:
            AnalysisResult with detailed analysis
        """
        content = code_block.content
        language = code_block.language.value
        
        issues = []
        
        # Language-specific analysis
        if language == "python":
            issues.extend(self._analyze_python_code(content))
        elif language in ["javascript", "typescript"]:
            issues.extend(self._analyze_javascript_code(content))
        elif language == "java":
            issues.extend(self._analyze_java_code(content))
        elif language == "cpp":
            issues.extend(self._analyze_cpp_code(content))
        
        # Universal analysis
        issues.extend(self._analyze_security_patterns(content))
        issues.extend(self._analyze_performance_patterns(content))
        issues.extend(self._analyze_style_patterns(content))
        issues.extend(self._analyze_bug_patterns(content))
        
        # Calculate scores
        scores = self._calculate_scores(issues)
        
        # Determine if code is safe
        critical_issues = [i for i in issues if i.severity == SeverityLevel.CRITICAL]
        high_security_issues = [i for i in issues if i.type == IssueType.SECURITY and i.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]]
        
        is_safe = len(critical_issues) == 0 and len(high_security_issues) == 0
        
        return AnalysisResult(
            is_safe=is_safe,
            issues=issues,
            score=scores["overall"],
            complexity_score=scores["complexity"],
            maintainability_score=scores["maintainability"],
            security_score=scores["security"],
            summary=self._generate_summary(issues, scores)
        )
    
    def _analyze_python_code(self, content: str) -> List[CodeIssue]:
        """Analyze Python code using AST and pattern matching."""
        issues = []
        
        try:
            # Parse AST
            tree = ast.parse(content)
            
            # AST-based analysis
            issues.extend(self._analyze_python_ast(tree))
            
            # Pattern-based analysis
            issues.extend(self._analyze_python_patterns(content))
            
            # Use bandit for security analysis if available
            if BANDIT_AVAILABLE:
                issues.extend(self._analyze_with_bandit(content))
            
        except SyntaxError as e:
            issues.append(CodeIssue(
                type=IssueType.BUG,
                severity=SeverityLevel.CRITICAL,
                message=f"Syntax error: {e}",
                line_number=e.lineno,
                column_number=e.offset
            ))
        
        return issues
    
    def _analyze_python_ast(self, tree: ast.AST) -> List[CodeIssue]:
        """Analyze Python AST for issues."""
        issues = []
        
        class SecurityVisitor(ast.NodeVisitor):
            def visit_Import(self, node):
                for alias in node.names:
                    if alias.name in ['os', 'subprocess', 'shutil', 'socket', 'urllib']:
                        issues.append(CodeIssue(
                            type=IssueType.SECURITY,
                            severity=SeverityLevel.HIGH,
                            message=f"Potentially dangerous import: {alias.name}",
                            line_number=node.lineno,
                            column_number=node.col_offset,
                            suggestion="Consider if this import is necessary for the intended functionality"
                        ))
            
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', 'compile']:
                        issues.append(CodeIssue(
                            type=IssueType.SECURITY,
                            severity=SeverityLevel.CRITICAL,
                            message=f"Dangerous function call: {node.func.id}",
                            line_number=node.lineno,
                            column_number=node.col_offset,
                            suggestion="Avoid using eval/exec/compile as they can execute arbitrary code"
                        ))
                
                # Check for subprocess calls
                if isinstance(node.func, ast.Attribute):
                    if (isinstance(node.func.value, ast.Name) and 
                        node.func.value.id == 'subprocess' and
                        node.func.attr in ['run', 'call', 'Popen']):
                        issues.append(CodeIssue(
                            type=IssueType.SECURITY,
                            severity=SeverityLevel.HIGH,
                            message=f"Subprocess call detected: {node.func.attr}",
                            line_number=node.lineno,
                            column_number=node.col_offset,
                            suggestion="Ensure subprocess calls are safe and don't execute user input"
                        ))
        
        visitor = SecurityVisitor()
        visitor.visit(tree)
        return issues
    
    def _analyze_python_patterns(self, content: str) -> List[CodeIssue]:
        """Analyze Python code using regex patterns."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for hardcoded passwords/secrets
            if re.search(r'password\s*=\s*["\'][^"\']+["\']', line, re.IGNORECASE):
                issues.append(CodeIssue(
                    type=IssueType.SECURITY,
                    severity=SeverityLevel.HIGH,
                    message="Hardcoded password detected",
                    line_number=i,
                    code_snippet=line.strip(),
                    suggestion="Use environment variables or secure configuration for passwords"
                ))
            
            # Check for TODO/FIXME comments
            if re.search(r'#\s*(TODO|FIXME|HACK)', line, re.IGNORECASE):
                issues.append(CodeIssue(
                    type=IssueType.MAINTAINABILITY,
                    severity=SeverityLevel.LOW,
                    message="TODO/FIXME comment found",
                    line_number=i,
                    code_snippet=line.strip(),
                    suggestion="Address TODO/FIXME items before production deployment"
                ))
            
            # Check for long lines
            if len(line) > 120:
                issues.append(CodeIssue(
                    type=IssueType.STYLE,
                    severity=SeverityLevel.LOW,
                    message=f"Line too long ({len(line)} characters)",
                    line_number=i,
                    code_snippet=line.strip(),
                    suggestion="Break long lines for better readability"
                ))
        
        return issues
    
    def _analyze_with_bandit(self, content: str) -> List[CodeIssue]:
        """Use bandit for security analysis."""
        issues = []
        
        try:
            # Create temporary file for bandit analysis
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                temp_file = f.name
            
            # Run bandit
            b_mgr = manager.BanditManager()
            b_mgr.discover([temp_file])
            b_mgr.run_tests()
            
            # Process results
            for issue in b_mgr.get_issue_list():
                severity_map = {
                    'LOW': SeverityLevel.LOW,
                    'MEDIUM': SeverityLevel.MEDIUM,
                    'HIGH': SeverityLevel.HIGH
                }
                
                issues.append(CodeIssue(
                    type=IssueType.SECURITY,
                    severity=severity_map.get(issue.severity, SeverityLevel.MEDIUM),
                    message=issue.text,
                    line_number=issue.lineno,
                    rule_id=issue.test_id,
                    suggestion=issue.more_info
                ))
            
            # Cleanup
            os.unlink(temp_file)
            
        except Exception as e:
            # If bandit fails, continue without it
            pass
        
        return issues
    
    def _analyze_javascript_code(self, content: str) -> List[CodeIssue]:
        """Analyze JavaScript/TypeScript code."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for eval usage
            if re.search(r'eval\s*\(', line):
                issues.append(CodeIssue(
                    type=IssueType.SECURITY,
                    severity=SeverityLevel.CRITICAL,
                    message="eval() usage detected",
                    line_number=i,
                    code_snippet=line.strip(),
                    suggestion="Avoid eval() as it can execute arbitrary code"
                ))
            
            # Check for innerHTML usage
            if re.search(r'\.innerHTML\s*=', line):
                issues.append(CodeIssue(
                    type=IssueType.SECURITY,
                    severity=SeverityLevel.HIGH,
                    message="innerHTML assignment detected",
                    line_number=i,
                    code_snippet=line.strip(),
                    suggestion="Use textContent or createElement to avoid XSS vulnerabilities"
                ))
            
            # Check for console.log in production code
            if re.search(r'console\.log\s*\(', line):
                issues.append(CodeIssue(
                    type=IssueType.STYLE,
                    severity=SeverityLevel.LOW,
                    message="console.log detected",
                    line_number=i,
                    code_snippet=line.strip(),
                    suggestion="Remove console.log statements from production code"
                ))
        
        return issues
    
    def _analyze_java_code(self, content: str) -> List[CodeIssue]:
        """Analyze Java code."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for System.out.println
            if re.search(r'System\.out\.println\s*\(', line):
                issues.append(CodeIssue(
                    type=IssueType.STYLE,
                    severity=SeverityLevel.LOW,
                    message="System.out.println detected",
                    line_number=i,
                    code_snippet=line.strip(),
                    suggestion="Use proper logging framework instead of System.out.println"
                ))
            
            # Check for hardcoded strings
            if re.search(r'String\s+\w+\s*=\s*"[^"]{20,}"', line):
                issues.append(CodeIssue(
                    type=IssueType.STYLE,
                    severity=SeverityLevel.LOW,
                    message="Long hardcoded string detected",
                    line_number=i,
                    code_snippet=line.strip(),
                    suggestion="Consider using constants or external configuration"
                ))
        
        return issues
    
    def _analyze_cpp_code(self, content: str) -> List[CodeIssue]:
        """Analyze C++ code."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for printf usage
            if re.search(r'printf\s*\(', line):
                issues.append(CodeIssue(
                    type=IssueType.SECURITY,
                    severity=SeverityLevel.MEDIUM,
                    message="printf usage detected",
                    line_number=i,
                    code_snippet=line.strip(),
                    suggestion="Use std::cout or consider format string vulnerabilities"
                ))
            
            # Check for malloc without free
            if re.search(r'malloc\s*\(', line):
                issues.append(CodeIssue(
                    type=IssueType.BUG,
                    severity=SeverityLevel.HIGH,
                    message="malloc usage detected",
                    line_number=i,
                    code_snippet=line.strip(),
                    suggestion="Ensure corresponding free() call or use smart pointers"
                ))
        
        return issues
    
    def _analyze_security_patterns(self, content: str) -> List[CodeIssue]:
        """Analyze for security-related patterns."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern, severity in self.security_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        type=IssueType.SECURITY,
                        severity=severity,
                        message=f"Security pattern detected: {pattern}",
                        line_number=i,
                        code_snippet=line.strip()
                    ))
        
        return issues
    
    def _analyze_performance_patterns(self, content: str) -> List[CodeIssue]:
        """Analyze for performance-related patterns."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern, severity in self.performance_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        type=IssueType.PERFORMANCE,
                        severity=severity,
                        message=f"Performance pattern detected: {pattern}",
                        line_number=i,
                        code_snippet=line.strip()
                    ))
        
        return issues
    
    def _analyze_style_patterns(self, content: str) -> List[CodeIssue]:
        """Analyze for style-related patterns."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern, severity in self.style_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        type=IssueType.STYLE,
                        severity=severity,
                        message=f"Style pattern detected: {pattern}",
                        line_number=i,
                        code_snippet=line.strip()
                    ))
        
        return issues
    
    def _analyze_bug_patterns(self, content: str) -> List[CodeIssue]:
        """Analyze for bug-related patterns."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern, severity in self.bug_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        type=IssueType.BUG,
                        severity=severity,
                        message=f"Potential bug pattern detected: {pattern}",
                        line_number=i,
                        code_snippet=line.strip()
                    ))
        
        return issues
    
    def _calculate_scores(self, issues: List[CodeIssue]) -> Dict[str, float]:
        """Calculate quality scores based on issues."""
        if not issues:
            return {
                "overall": 100.0,
                "security": 100.0,
                "complexity": 100.0,
                "maintainability": 100.0
            }
        
        # Base score
        base_score = 100.0
        
        # Deduct points based on severity
        severity_penalties = {
            SeverityLevel.LOW: 1,
            SeverityLevel.MEDIUM: 3,
            SeverityLevel.HIGH: 7,
            SeverityLevel.CRITICAL: 15
        }
        
        # Calculate overall score
        total_penalty = sum(severity_penalties.get(issue.severity, 1) for issue in issues)
        overall_score = max(0, base_score - total_penalty)
        
        # Calculate category-specific scores
        security_issues = [i for i in issues if i.type == IssueType.SECURITY]
        security_penalty = sum(severity_penalties.get(issue.severity, 1) for issue in security_issues)
        security_score = max(0, base_score - security_penalty * 2)  # Double penalty for security issues
        
        complexity_issues = [i for i in issues if i.type == IssueType.COMPLEXITY]
        complexity_penalty = sum(severity_penalties.get(issue.severity, 1) for issue in complexity_issues)
        complexity_score = max(0, base_score - complexity_penalty)
        
        maintainability_issues = [i for i in issues if i.type == IssueType.MAINTAINABILITY]
        maintainability_penalty = sum(severity_penalties.get(issue.severity, 1) for issue in maintainability_issues)
        maintainability_score = max(0, base_score - maintainability_penalty)
        
        return {
            "overall": overall_score,
            "security": security_score,
            "complexity": complexity_score,
            "maintainability": maintainability_score
        }
    
    def _generate_summary(self, issues: List[CodeIssue], scores: Dict[str, float]) -> Dict[str, Any]:
        """Generate analysis summary."""
        issue_counts = {}
        for issue in issues:
            key = f"{issue.type.value}_{issue.severity.value}"
            issue_counts[key] = issue_counts.get(key, 0) + 1
        
        return {
            "total_issues": len(issues),
            "issue_counts": issue_counts,
            "scores": scores,
            "recommendations": self._generate_recommendations(issues)
        }
    
    def _generate_recommendations(self, issues: List[CodeIssue]) -> List[str]:
        """Generate recommendations based on issues."""
        recommendations = []
        
        # Security recommendations
        security_issues = [i for i in issues if i.type == IssueType.SECURITY]
        if security_issues:
            recommendations.append("Review and address security issues before deployment")
        
        # Performance recommendations
        performance_issues = [i for i in issues if i.type == IssueType.PERFORMANCE]
        if performance_issues:
            recommendations.append("Consider performance optimizations for better efficiency")
        
        # Style recommendations
        style_issues = [i for i in issues if i.type == IssueType.STYLE]
        if style_issues:
            recommendations.append("Follow coding style guidelines for better maintainability")
        
        return recommendations
    
    def _load_security_patterns(self) -> Dict[str, SeverityLevel]:
        """Load security-related patterns."""
        return {
            r'password\s*=\s*["\'][^"\']+["\']': SeverityLevel.HIGH,
            r'api_key\s*=\s*["\'][^"\']+["\']': SeverityLevel.HIGH,
            r'secret\s*=\s*["\'][^"\']+["\']': SeverityLevel.HIGH,
            r'eval\s*\(': SeverityLevel.CRITICAL,
            r'exec\s*\(': SeverityLevel.CRITICAL,
            r'__import__\s*\(': SeverityLevel.HIGH,
            r'os\.system\s*\(': SeverityLevel.CRITICAL,
            r'subprocess\.run\s*\(': SeverityLevel.HIGH,
        }
    
    def _load_performance_patterns(self) -> Dict[str, SeverityLevel]:
        """Load performance-related patterns."""
        return {
            r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(': SeverityLevel.MEDIUM,
            r'\.append\s*\(': SeverityLevel.LOW,
            r'global\s+\w+': SeverityLevel.MEDIUM,
        }
    
    def _load_style_patterns(self) -> Dict[str, SeverityLevel]:
        """Load style-related patterns."""
        return {
            r'print\s*\(': SeverityLevel.LOW,
            r'console\.log\s*\(': SeverityLevel.LOW,
            r'System\.out\.println\s*\(': SeverityLevel.LOW,
        }
    
    def _load_bug_patterns(self) -> Dict[str, SeverityLevel]:
        """Load bug-related patterns."""
        return {
            r'==\s*None': SeverityLevel.MEDIUM,
            r'!=\s*None': SeverityLevel.MEDIUM,
            r'if\s+\w+\s*=\s*': SeverityLevel.HIGH,  # Assignment in condition
        }
