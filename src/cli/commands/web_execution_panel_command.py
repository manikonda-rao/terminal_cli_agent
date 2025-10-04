"""
Web-based execution panel command for the Terminal CLI.
"""

from typing import Optional
from rich.console import Console
import webbrowser
import threading
import time

from .base import BaseCommand
from ...core.web_execution_panel import WebExecutionPanel
from ...core.models import AgentConfig


class WebExecutionPanelCommand(BaseCommand):
    """Command to launch the web-based interactive code execution panel."""
    
    def __init__(self, cli, console: Console):
        super().__init__(cli, console)
        self.aliases = ["web", "browser-panel", "web-exec"]
    
    @property
    def name(self) -> str:
        return "web-panel"
    
    @property
    def description(self) -> str:
        return "Launch web-based interactive code execution panel"
    
    @property
    def usage(self) -> str:
        return "/web-panel [host] [port]"
    
    def execute(self, args: list[str]):
        """Execute the web execution panel command."""
        try:
            # Parse arguments for host and port
            host = "127.0.0.1"
            port = 5000
            
            if args:
                if len(args) >= 1:
                    host = args[0]
                if len(args) >= 2:
                    try:
                        port = int(args[1])
                    except ValueError:
                        self.console.print(f"[red]Invalid port: {args[1]}[/red]")
                        return
            
            # Show welcome message
            self.console.print("\n[bold blue]🌐 Launching Web-Based Code Execution Panel[/bold blue]")
            self.console.print(f"[dim]Server will start at http://{host}:{port}[/dim]")
            self.console.print("[dim]Press Ctrl+C to stop the server[/dim]\n")
            
            # Create web panel
            web_panel = WebExecutionPanel(self.cli.agent.config, host, port)
            
            # Open browser after a short delay
            def open_browser():
                time.sleep(2)  # Wait for server to start
                try:
                    webbrowser.open(f"http://{host}:{port}")
                    self.console.print(f"[green]✅ Browser opened at http://{host}:{port}[/green]")
                except Exception as e:
                    self.console.print(f"[yellow]⚠️ Could not open browser automatically: {e}[/yellow]")
                    self.console.print(f"[cyan]Please open http://{host}:{port} in your browser[/cyan]")
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            # Run the web panel
            web_panel.run(debug=False)
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Web execution panel stopped by user.[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Error launching web execution panel: {e}[/red]")
    
    def get_help(self) -> str:
        """Get help text for this command."""
        return """
Web-Based Interactive Code Execution Panel

Launches a modern web interface for running code snippets with:
• Real-time output display via WebSocket
• Multiple language support (Python, JavaScript, TypeScript, Java, C++, Rust, Go, etc.)
• Execution history with timestamps
• Light/dark theme support
• Responsive design for desktop and mobile
• Keyboard shortcuts for quick actions
• Secure sandboxed execution
• Copy/paste functionality
• Collapsible panels

Usage: /web-panel [host] [port]
  host: Server host (default: 127.0.0.1)
  port: Server port (default: 5000)

Examples:
  /web-panel                    # Start on localhost:5000
  /web-panel 0.0.0.0 8080      # Start on all interfaces:8080

Features:
• Modern web UI with syntax highlighting
• Real-time code execution with live output
• Execution history with click-to-load functionality
• Theme switching (light/dark)
• Responsive design
• Keyboard shortcuts (Ctrl+Enter to run, Ctrl+C to stop, etc.)
• Copy output to clipboard
• Resizable panels
• Toast notifications
• Loading indicators

The web panel integrates with the existing secure execution infrastructure
and supports all configured execution modes (sandbox, Docker, E2B, Daytona).

Access the panel by opening the URL shown in your terminal in a web browser.
        """
