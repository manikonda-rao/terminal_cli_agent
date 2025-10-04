"""
Interactive Code Execution Panel for the Terminal CLI.
Provides a rich, interactive interface for running code snippets with real-time output.
"""

import asyncio
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.status import Status
from rich.prompt import Prompt, Confirm
from rich import box

from .models import CodeBlock, ExecutionResult, ExecutionStatus, CodeLanguage, AgentConfig
from ..execution.executor_factory import ExecutorFactory


class ExecutionState(str, Enum):
    """Current state of the execution panel."""
    IDLE = "idle"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class ThemeMode(str, Enum):
    """Theme modes for the execution panel."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


@dataclass
class ExecutionHistoryEntry:
    """Entry in the execution history."""
    timestamp: datetime
    code: str
    language: str
    result: Optional[ExecutionResult] = None
    execution_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class ExecutionPanelConfig:
    """Configuration for the execution panel."""
    max_history_size: int = 50
    auto_clear_output: bool = False
    show_line_numbers: bool = True
    enable_syntax_highlighting: bool = True
    default_language: str = "python"
    theme: ThemeMode = ThemeMode.AUTO
    panel_height: int = 20
    max_output_lines: int = 1000
    enable_animations: bool = True
    keyboard_shortcuts: Dict[str, str] = field(default_factory=lambda: {
        "run": "ctrl+enter",
        "stop": "ctrl+c",
        "clear": "ctrl+l",
        "toggle_panel": "ctrl+shift+e",
        "toggle_theme": "ctrl+shift+t"
    })


class InteractiveExecutionPanel:
    """Interactive code execution panel with rich UI."""
    
    def __init__(self, config: AgentConfig, panel_config: Optional[ExecutionPanelConfig] = None):
        self.config = config
        self.panel_config = panel_config or ExecutionPanelConfig()
        self.console = Console()
        
        # Execution state
        self.state = ExecutionState.IDLE
        self.current_executor = None
        self.execution_thread = None
        self.stop_execution = threading.Event()
        
        # History and state
        self.execution_history: List[ExecutionHistoryEntry] = []
        self.current_code = ""
        self.current_language = self.panel_config.default_language
        self.output_buffer = []
        self.is_panel_visible = True
        
        # UI components
        self.layout = None
        self.live_display = None
        
        # Executor factory
        self.executor_factory = ExecutorFactory(config)
        
        # Callbacks
        self.on_execution_start: Optional[Callable] = None
        self.on_execution_complete: Optional[Callable] = None
        self.on_output_update: Optional[Callable] = None
        
        # Initialize the panel
        self._initialize_panel()
    
    def _initialize_panel(self):
        """Initialize the execution panel layout."""
        self.layout = Layout()
        
        # Create main layout sections
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        # Split main section into code editor and output
        self.layout["main"].split_row(
            Layout(name="code_editor", ratio=1),
            Layout(name="output_panel", ratio=1)
        )
        
        # Initialize with default content
        self._update_header()
        self._update_code_editor()
        self._update_output_panel()
        self._update_footer()
    
    def _update_header(self):
        """Update the header panel."""
        header_text = Text()
        header_text.append("🚀 Interactive Code Execution Panel", style="bold blue")
        header_text.append(" | ")
        header_text.append(f"Language: {self.current_language}", style="cyan")
        header_text.append(" | ")
        header_text.append(f"State: {self.state.value}", style=self._get_state_color())
        
        if self.state == ExecutionState.RUNNING:
            header_text.append(" | ")
            header_text.append("⏳ Running...", style="yellow")
        
        self.layout["header"].update(
            Panel(
                Align.center(header_text),
                box=box.ROUNDED,
                style="blue"
            )
        )
    
    def _update_code_editor(self):
        """Update the code editor panel."""
        if not self.current_code.strip():
            placeholder = "# Enter your code here...\n# Press Ctrl+Enter to run\n# Press Ctrl+L to clear"
            syntax = Syntax(placeholder, "python", theme="monokai", line_numbers=True)
        else:
            syntax = Syntax(
                self.current_code,
                self.current_language,
                theme=self._get_theme(),
                line_numbers=self.panel_config.show_line_numbers
            )
        
        editor_panel = Panel(
            syntax,
            title="Code Editor",
            border_style="green",
            box=box.ROUNDED
        )
        
        self.layout["code_editor"].update(editor_panel)
    
    def _update_output_panel(self):
        """Update the output panel."""
        if not self.output_buffer:
            placeholder = "Output will appear here when you run code..."
            output_content = Panel(
                Align.center(Text(placeholder, style="dim")),
                title="Output",
                border_style="blue",
                box=box.ROUNDED
            )
        else:
            # Format output with proper styling
            output_text = Text()
            for line in self.output_buffer[-self.panel_config.max_output_lines:]:
                if line.startswith("ERROR:"):
                    output_text.append(line + "\n", style="red")
                elif line.startswith("WARNING:"):
                    output_text.append(line + "\n", style="yellow")
                elif line.startswith("INFO:"):
                    output_text.append(line + "\n", style="blue")
                else:
                    output_text.append(line + "\n", style="white")
            
            output_content = Panel(
                output_text,
                title=f"Output ({len(self.output_buffer)} lines)",
                border_style="blue",
                box=box.ROUNDED
            )
        
        self.layout["output_panel"].update(output_content)
    
    def _update_footer(self):
        """Update the footer with controls and shortcuts."""
        footer_text = Text()
        footer_text.append("Controls: ", style="bold")
        footer_text.append("Run (Ctrl+Enter) ", style="green")
        footer_text.append("| Stop (Ctrl+C) ", style="red")
        footer_text.append("| Clear (Ctrl+L) ", style="yellow")
        footer_text.append("| Toggle Panel (Ctrl+Shift+E) ", style="cyan")
        footer_text.append("| Theme (Ctrl+Shift+T)", style="magenta")
        
        self.layout["footer"].update(
            Panel(
                Align.center(footer_text),
                box=box.ROUNDED,
                style="dim"
            )
        )
    
    def _get_state_color(self) -> str:
        """Get color for current state."""
        colors = {
            ExecutionState.IDLE: "green",
            ExecutionState.RUNNING: "yellow",
            ExecutionState.STOPPING: "red",
            ExecutionState.ERROR: "red"
        }
        return colors.get(self.state, "white")
    
    def _get_theme(self) -> str:
        """Get syntax highlighting theme based on current theme mode."""
        if self.panel_config.theme == ThemeMode.LIGHT:
            return "default"
        elif self.panel_config.theme == ThemeMode.DARK:
            return "monokai"
        else:  # AUTO
            return "monokai"  # Default to dark theme
    
    def show_panel(self):
        """Show the interactive execution panel."""
        if not self.is_panel_visible:
            return
        
        try:
            with Live(self.layout, console=self.console, refresh_per_second=4) as live:
                self.live_display = live
                self._run_interactive_loop()
        except KeyboardInterrupt:
            self._handle_stop_execution()
        finally:
            self.live_display = None
    
    def _run_interactive_loop(self):
        """Run the main interactive loop."""
        while True:
            try:
                # Get user input
                user_input = Prompt.ask(
                    "\n[bold cyan]Enter code (or command):[/bold cyan]",
                    default=""
                ).strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.startswith("/"):
                    self._handle_command(user_input)
                    continue
                
                # Handle keyboard shortcuts
                if user_input in ["ctrl+enter", "ctrl+c", "ctrl+l", "ctrl+shift+e", "ctrl+shift+t"]:
                    self._handle_shortcut(user_input)
                    continue
                
                # Update current code and run
                self.current_code = user_input
                self._update_code_editor()
                self.run_code()
                
            except KeyboardInterrupt:
                self._handle_stop_execution()
                break
            except EOFError:
                break
    
    def _handle_command(self, command: str):
        """Handle special commands."""
        if command == "/help":
            self._show_help()
        elif command == "/clear":
            self.clear_output()
        elif command == "/history":
            self._show_history()
        elif command == "/languages":
            self._show_languages()
        elif command == "/theme":
            self._toggle_theme()
        elif command == "/quit":
            raise EOFError
        else:
            self._add_output(f"Unknown command: {command}", "ERROR:")
    
    def _handle_shortcut(self, shortcut: str):
        """Handle keyboard shortcuts."""
        if shortcut == "ctrl+enter":
            self.run_code()
        elif shortcut == "ctrl+c":
            self._handle_stop_execution()
        elif shortcut == "ctrl+l":
            self.clear_output()
        elif shortcut == "ctrl+shift+e":
            self.toggle_panel()
        elif shortcut == "ctrl+shift+t":
            self._toggle_theme()
    
    def _show_help(self):
        """Show help information."""
        help_text = """
[bold blue]Interactive Code Execution Panel Help[/bold blue]

[bold green]Commands:[/bold green]
  /help      - Show this help
  /clear     - Clear output panel
  /history   - Show execution history
  /languages - Show available languages
  /theme     - Toggle theme
  /quit      - Exit panel

[bold green]Keyboard Shortcuts:[/bold green]
  Ctrl+Enter     - Run current code
  Ctrl+C         - Stop execution
  Ctrl+L         - Clear output
  Ctrl+Shift+E   - Toggle panel visibility
  Ctrl+Shift+T   - Toggle theme

[bold green]Supported Languages:[/bold green]
  Python, JavaScript, TypeScript, Java, C++, Rust, Go, PHP, Ruby, Perl, Bash
        """
        
        self._add_output(help_text, "INFO:")
    
    def _show_history(self):
        """Show execution history."""
        if not self.execution_history:
            self._add_output("No execution history available.", "INFO:")
            return
        
        history_text = f"[bold blue]Execution History ({len(self.execution_history)} entries):[/bold blue]\n\n"
        
        for i, entry in enumerate(self.execution_history[-10:], 1):  # Show last 10
            status_icon = "✅" if entry.success else "❌"
            history_text += f"{i}. {status_icon} {entry.timestamp.strftime('%H:%M:%S')} - {entry.language}\n"
            if entry.result:
                history_text += f"   Execution time: {entry.execution_time:.3f}s\n"
            if entry.error_message:
                history_text += f"   Error: {entry.error_message}\n"
            history_text += "\n"
        
        self._add_output(history_text, "INFO:")
    
    def _show_languages(self):
        """Show available languages."""
        executor = self.executor_factory.create_executor()
        if hasattr(executor, 'get_available_languages'):
            languages = executor.get_available_languages()
        else:
            languages = ["python", "javascript", "typescript", "java", "cpp", "rust", "go"]
        
        lang_text = f"[bold blue]Available Languages:[/bold blue]\n"
        for lang in languages:
            lang_text += f"  • {lang.title()}\n"
        
        self._add_output(lang_text, "INFO:")
    
    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        if self.panel_config.theme == ThemeMode.LIGHT:
            self.panel_config.theme = ThemeMode.DARK
        elif self.panel_config.theme == ThemeMode.DARK:
            self.panel_config.theme = ThemeMode.LIGHT
        else:
            self.panel_config.theme = ThemeMode.DARK
        
        self._update_code_editor()
        self._add_output(f"Theme switched to: {self.panel_config.theme.value}", "INFO:")
    
    def run_code(self):
        """Run the current code."""
        if not self.current_code.strip():
            self._add_output("No code to execute.", "WARNING:")
            return
        
        if self.state == ExecutionState.RUNNING:
            self._add_output("Execution already in progress. Stop current execution first.", "WARNING:")
            return
        
        # Clear previous output if configured
        if self.panel_config.auto_clear_output:
            self.clear_output()
        
        # Create code block
        try:
            language = CodeLanguage(self.current_language)
        except ValueError:
            language = CodeLanguage.PYTHON
            self._add_output(f"Unknown language '{self.current_language}', defaulting to Python.", "WARNING:")
        
        code_block = CodeBlock(
            content=self.current_code,
            language=language
        )
        
        # Start execution
        self.state = ExecutionState.RUNNING
        self.stop_execution.clear()
        self._update_header()
        
        if self.on_execution_start:
            self.on_execution_start(code_block)
        
        # Run execution in separate thread
        self.execution_thread = threading.Thread(
            target=self._execute_code_thread,
            args=(code_block,)
        )
        self.execution_thread.daemon = True
        self.execution_thread.start()
    
    def _execute_code_thread(self, code_block: CodeBlock):
        """Execute code in a separate thread."""
        try:
            # Create executor
            executor = self.executor_factory.create_executor()
            
            # Add execution start message
            self._add_output(f"Running {code_block.language.value} code...", "INFO:")
            self._add_output("─" * 50, "")
            
            # Execute code
            start_time = time.time()
            result = executor.execute_code(code_block, timeout=self.config.max_execution_time)
            execution_time = time.time() - start_time
            
            # Handle result
            self._handle_execution_result(result, execution_time, code_block)
            
        except Exception as e:
            self._handle_execution_error(str(e))
        finally:
            self.state = ExecutionState.IDLE
            self._update_header()
    
    def _handle_execution_result(self, result: ExecutionResult, execution_time: float, code_block: CodeBlock):
        """Handle execution result."""
        # Add to history
        history_entry = ExecutionHistoryEntry(
            timestamp=datetime.now(),
            code=code_block.content,
            language=code_block.language.value,
            result=result,
            execution_time=execution_time,
            success=result.status == ExecutionStatus.COMPLETED,
            error_message=result.error_message
        )
        self.execution_history.append(history_entry)
        
        # Keep history size limit
        if len(self.execution_history) > self.panel_config.max_history_size:
            self.execution_history = self.execution_history[-self.panel_config.max_history_size:]
        
        # Display result
        if result.status == ExecutionStatus.COMPLETED:
            self._add_output("✅ Execution completed successfully", "INFO:")
            if result.stdout:
                self._add_output("Output:", "INFO:")
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self._add_output(line, "")
        else:
            self._add_output(f"❌ Execution failed: {result.status.value}", "ERROR:")
            if result.stderr:
                self._add_output("Error output:", "ERROR:")
                for line in result.stderr.split('\n'):
                    if line.strip():
                        self._add_output(line, "ERROR:")
        
        # Show execution time
        self._add_output(f"Execution time: {execution_time:.3f}s", "INFO:")
        self._add_output("─" * 50, "")
        
        # Update UI
        self._update_output_panel()
        
        if self.on_execution_complete:
            self.on_execution_complete(result)
    
    def _handle_execution_error(self, error_message: str):
        """Handle execution error."""
        self._add_output(f"❌ Execution error: {error_message}", "ERROR:")
        self._add_output("─" * 50, "")
        self._update_output_panel()
    
    def _add_output(self, text: str, prefix: str = ""):
        """Add text to output buffer."""
        if prefix:
            self.output_buffer.append(f"{prefix} {text}")
        else:
            self.output_buffer.append(text)
        
        if self.on_output_update:
            self.on_output_update(text, prefix)
    
    def _handle_stop_execution(self):
        """Handle stop execution request."""
        if self.state == ExecutionState.RUNNING:
            self.state = ExecutionState.STOPPING
            self.stop_execution.set()
            self._add_output("🛑 Stopping execution...", "WARNING:")
            self._update_header()
            
            # Wait for execution to stop
            if self.execution_thread and self.execution_thread.is_alive():
                self.execution_thread.join(timeout=2.0)
            
            self.state = ExecutionState.IDLE
            self._update_header()
            self._add_output("Execution stopped.", "INFO:")
    
    def clear_output(self):
        """Clear the output panel."""
        self.output_buffer.clear()
        self._update_output_panel()
        self._add_output("Output cleared.", "INFO:")
    
    def toggle_panel(self):
        """Toggle panel visibility."""
        self.is_panel_visible = not self.is_panel_visible
        if self.is_panel_visible:
            self._add_output("Panel shown.", "INFO:")
        else:
            self._add_output("Panel hidden.", "INFO:")
    
    def set_language(self, language: str):
        """Set the current programming language."""
        self.current_language = language
        self._update_header()
        self._update_code_editor()
        self._add_output(f"Language set to: {language}", "INFO:")
    
    def set_code(self, code: str):
        """Set the current code."""
        self.current_code = code
        self._update_code_editor()
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_history:
            return {"total_executions": 0}
        
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for entry in self.execution_history if entry.success)
        avg_execution_time = sum(entry.execution_time for entry in self.execution_history) / total_executions
        
        # Language distribution
        language_counts = {}
        for entry in self.execution_history:
            lang = entry.language
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "average_execution_time": avg_execution_time,
            "language_distribution": language_counts,
            "current_language": self.current_language,
            "panel_visible": self.is_panel_visible,
            "theme": self.panel_config.theme.value
        }
    
    def cleanup(self):
        """Cleanup resources."""
        if self.state == ExecutionState.RUNNING:
            self._handle_stop_execution()
        
        if self.executor_factory:
            self.executor_factory.cleanup_all_executors()


# Convenience function to create and show the panel
def show_execution_panel(config: AgentConfig, panel_config: Optional[ExecutionPanelConfig] = None):
    """Show the interactive execution panel."""
    panel = InteractiveExecutionPanel(config, panel_config)
    try:
        panel.show_panel()
    finally:
        panel.cleanup()
