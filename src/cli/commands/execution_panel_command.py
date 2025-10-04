"""
Interactive execution panel command for the Terminal CLI.
"""

from typing import Optional
from rich.console import Console

from .base import BaseCommand
from ..core.execution_panel import InteractiveExecutionPanel, ExecutionPanelConfig
from ..core.models import AgentConfig


class ExecutionPanelCommand(BaseCommand):
    """Command to launch the interactive code execution panel."""
    
    def __init__(self, cli, console: Console):
        super().__init__(cli, console)
        self.name = "execution-panel"
        self.description = "Launch interactive code execution panel"
        self.aliases = ["panel", "exec", "run-panel"]
    
    def execute(self, args: Optional[str] = None):
        """Execute the execution panel command."""
        try:
            # Create panel configuration
            panel_config = ExecutionPanelConfig(
                max_history_size=50,
                auto_clear_output=False,
                show_line_numbers=True,
                enable_syntax_highlighting=True,
                default_language="python",
                theme="auto",
                panel_height=20,
                max_output_lines=1000,
                enable_animations=True
            )
            
            # Show welcome message
            self.console.print("\n[bold blue]🚀 Launching Interactive Code Execution Panel[/bold blue]")
            self.console.print("[dim]Press Ctrl+C to exit the panel[/dim]\n")
            
            # Create and show the panel
            panel = InteractiveExecutionPanel(self.cli.agent.config, panel_config)
            
            # Set up callbacks for integration with main CLI
            panel.on_execution_start = self._on_execution_start
            panel.on_execution_complete = self._on_execution_complete
            panel.on_output_update = self._on_output_update
            
            # Show the panel
            panel.show_panel()
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Execution panel closed by user.[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Error launching execution panel: {e}[/red]")
        finally:
            if 'panel' in locals():
                panel.cleanup()
    
    def _on_execution_start(self, code_block):
        """Callback for when execution starts."""
        self.console.print(f"[cyan]Starting execution of {code_block.language.value} code...[/cyan]")
    
    def _on_execution_complete(self, result):
        """Callback for when execution completes."""
        if result.status.value == "completed":
            self.console.print("[green]✅ Execution completed successfully[/green]")
        else:
            self.console.print(f"[red]❌ Execution failed: {result.status.value}[/red]")
    
    def _on_output_update(self, text: str, prefix: str = ""):
        """Callback for output updates."""
        # This could be used to integrate with the main CLI's output system
        pass
    
    def get_help(self) -> str:
        """Get help text for this command."""
        return """
Interactive Code Execution Panel

Launches a rich, interactive interface for running code snippets with:
• Real-time output display
• Multiple language support (Python, JavaScript, TypeScript, Java, C++, Rust, Go, etc.)
• Execution history with timestamps
• Light/dark theme support
• Keyboard shortcuts for quick actions
• Secure sandboxed execution

Usage: /execution-panel or /panel

Features:
• Run code snippets directly in the interface
• View console output, logs, and errors in real-time
• Clear output, re-run snippets
• Toggle between light/dark themes
• Keyboard shortcuts (Ctrl+Enter to run, Ctrl+C to stop, etc.)
• Maintain execution history
• Collapsible/expandable terminal panel

The panel integrates with the existing secure execution infrastructure
and supports all configured execution modes (sandbox, Docker, E2B, Daytona).
        """
