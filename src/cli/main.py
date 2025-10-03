"""
Interactive CLI interface for the Terminal Coding Agent.
"""

import os
import sys
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter

from ..core.agent import CodingAgent
from ..core.models import AgentConfig

from .commands import CommandRegistry


class TerminalCLI:
    """Interactive CLI interface for the coding agent."""
    
    def __init__(self, project_root: str = ".", config: Optional[AgentConfig] = None):
        self.console = Console()
        self.agent = CodingAgent(project_root, config)
        self.history = InMemoryHistory()
        self.running = True
        
        # Setup autocompletion
        self.completer = WordCompleter([
            "create", "write", "implement", "make", "build",
            "modify", "change", "update", "edit", "fix",
            "run", "execute", "test", "call",
            "function", "class", "file",
            "python", "javascript", "typescript",
            "quicksort", "bubble sort", "binary search",
            "search", "find", "explain", "debug", "refactor",
            "/help", "/status", "/rollback", "/clear", "/export", "/quit"
        ])
        
        self._show_welcome()

        self.command_registry = CommandRegistry(self, self.console)
    
    def _show_welcome(self):
        """Show welcome message and help."""
        welcome_text = """
# Terminal Coding Agent

Professional AI-powered development assistant for modern software engineering workflows.

Core Capabilities:
- Generate production-ready code from natural language specifications
- Modify and refactor existing codebases with intelligent context awareness
- Execute code safely within enterprise-grade sandboxed environments
- Manage project files with automated version control and backup systems
- Perform intelligent codebase search and analysis operations
- Maintain persistent conversation context and project state

Enter your development requests in natural language, or use `/help` for command reference.
        """
        
        self.console.print(Panel(
            Markdown(welcome_text),
            title="Welcome",
            border_style="blue"
        ))
        
        # Display project status
        status = self.agent.get_project_status()
        self.console.print(f"Project Root: {status['project_root']}")
        self.console.print(f"Session Interactions: {status['conversation_stats']['total_turns']}")
        self.console.print()
    
    def run(self):
        """Main CLI loop."""
        while self.running:
            try:
                # Get user input with history and autocompletion
                user_input = prompt(
                    "> ",
                    history=self.history,
                    auto_suggest=AutoSuggestFromHistory(),
                    completer=self.completer,
                    complete_while_typing=True
                ).strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.startswith("/"):
                    self.command_registry.get_command(user_input)

                    # self._handle_special_command(user_input)
                    continue
                
                # Process the input
                turn = self.agent.process_input(user_input)
                
                # Display results with rich formatting
                self._display_turn_results(turn)
                
            except KeyboardInterrupt:
                self.console.print("\n\nSession terminated by user.")
                break
            except EOFError:
                self.console.print("\n\nSession terminated.")
                break
            except Exception as e:
                self.console.print(f"[red]System error: {e}[/red]")
    
    def _handle_special_command(self, command: str):
        """Handle special CLI commands."""
        parts = command.split()
        cmd = parts[0].lower()
        
        # if cmd == "/help":
        #     self.agent.show_help()
        
        # elif cmd == "/status":
        #     self._show_status()
        
        if cmd == "/rollback":
            success = self.agent.rollback_last_operation()
            if success:
                self.console.print("[green]Operation rollback completed successfully[/green]")
            else:
                self.console.print("[red]Rollback operation failed[/red]")
        
        # elif cmd == "/clear":
        #     confirm = Prompt.ask("Confirm project state reset (this action cannot be undone):", choices=["y", "n"], default="n")
        #     if confirm.lower() == "y":
        #         self.agent.clear_project()
        #         self.console.print("[green]Project state reset completed[/green]")
        
        elif cmd == "/export":
            if len(parts) > 1:
                export_path = parts[1]
                self.agent.export_project(export_path)
            else:
                self.console.print("[red]Export path required: /export <path>[/red]")
        
        # elif cmd == "/quit":
        #     self.console.print("Terminal Coding Agent session ended.")
        #     self.running = False
        
        else:
            self.console.print(f"[red]Invalid command: {cmd}[/red]")
            self.console.print("Use /help to view available commands")
    
    # def _show_status(self):
    #     """Show detailed project status."""
    #     status = self.agent.get_project_status()
    #     stats = status["conversation_stats"]
        
    #     # Create status table
    #     table = Table(title="Project Status")
    #     table.add_column("Metric", style="cyan")
    #     table.add_column("Value", style="green")
        
    #     table.add_row("Project Root", status["project_root"])
    #     table.add_row("Active Files", str(len(status["active_files"])))
    #     table.add_row("Total Turns", str(stats["total_turns"]))
    #     table.add_row("Successful Turns", str(stats["successful_turns"]))
    #     table.add_row("Failed Turns", str(stats["failed_turns"]))
    #     table.add_row("Success Rate", f"{stats['success_rate']:.1%}")
        
    #     self.console.print(table)
        
    #     # Show active files
    #     if status["active_files"]:
    #         self.console.print("\nActive Files:")
    #         for file in status["active_files"][-5:]:  # Show last 5 files
    #             self.console.print(f"  • {file}")
    #         if len(status["active_files"]) > 5:
    #             self.console.print(f"  ... and {len(status['active_files']) - 5} more")
        
    #     # Show intent statistics
    #     if stats["intent_counts"]:
    #         self.console.print("\nIntent Statistics:")
    #         for intent_type, count in stats["intent_counts"].items():
    #             self.console.print(f"  • {intent_type}: {count}")
    
    def _display_turn_results(self, turn):
        """Display conversation turn results with rich formatting."""
        # Show generated code
        if turn.generated_code:
            self.console.print("\n[bold blue]Generated Code:[/bold blue]")
            for i, code_block in enumerate(turn.generated_code):
                if len(turn.generated_code) > 1:
                    self.console.print(f"\n[bold]Code Block {i+1}:[/bold]")
                
                # Syntax highlighting
                syntax = Syntax(
                    code_block.content,
                    code_block.language.value,
                    theme="monokai",
                    line_numbers=True
                )
                self.console.print(syntax)
        
        # Show execution results
        if turn.execution_result:
            self.console.print("\n[bold green]Execution Results:[/bold green]")
            
            # Status
            status_color = "green" if turn.execution_result.status.value == "completed" else "red"
            self.console.print(f"Status: [{status_color}]{turn.execution_result.status.value}[/{status_color}]")
            
            if turn.execution_result.execution_time:
                self.console.print(f"Execution Time: {turn.execution_result.execution_time:.3f}s")
            
            # Output
            if turn.execution_result.stdout:
                self.console.print("\n[bold]Output:[/bold]")
                self.console.print(Panel(turn.execution_result.stdout, title="stdout"))
            
            if turn.execution_result.stderr:
                self.console.print("\n[bold red]Error Output:[/bold red]")
                self.console.print(Panel(turn.execution_result.stderr, title="stderr"))
        
        # Show file operations
        if turn.file_operations:
            self.console.print("\n[bold yellow]File Operations:[/bold yellow]")
            for file_op in turn.file_operations:
                operation_color = {
                    "create": "green",
                    "modify": "blue", 
                    "delete": "red",
                    "rollback": "yellow"
                }.get(file_op.operation, "white")
                
                self.console.print(f"  [{operation_color}]{file_op.operation}[/{operation_color}] {file_op.filepath}")
        
        # Display operation status
        if turn.success:
            self.console.print("\n[green]Operation completed successfully[/green]")
        else:
            self.console.print(f"\n[red]Operation failed: {turn.error_message}[/red]")
        
        self.console.print()  # Add spacing


def main():
    """Main entry point for the CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Terminal Coding Agent")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--llm-provider", choices=["openai", "anthropic"], default="openai")
    parser.add_argument("--model", default="gpt-4", help="LLM model name")
    
    args = parser.parse_args()
    
    # Load configuration
    config = AgentConfig(
        llm_provider=args.llm_provider,
        model_name=args.model
    )
    
    # Create and run CLI
    cli = TerminalCLI(args.project_root, config)
    cli.run()


if __name__ == "__main__":
    main()
