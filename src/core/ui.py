"""
UI helpers for terminal output with Rich formatting.
Provides color-coded output, progress indicators, and structured displays.
"""

from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax
from rich.progress import (Progress, SpinnerColumn, TextColumn, BarColumn,
                           TaskProgressColumn)
from rich.prompt import Confirm
from rich.status import Status
from rich.align import Align
from rich import box


class UIManager:
    """Centralized UI manager for consistent terminal output."""
    
    def __init__(self):
        self.console = Console()
        self.session_step = 0
        self.project_name = ""
        self.current_file = ""
    
    def set_session_context(self, project_name: str, current_file: str = ""):
        """Set session context for headers."""
        self.project_name = project_name
        self.current_file = current_file
    
    def show_session_header(self):
        """Display session context header."""
        self.session_step += 1
        
        # Create context info
        context_text = f"Project: {self.project_name}"
        if self.current_file:
            context_text += f" | File: {self.current_file}"
        context_text += f" | Step: {self.session_step}"
        
        # Create header panel
        header_panel = Panel(
            Align.center(Text(context_text, style="bold cyan")),
            box=box.ROUNDED,
            style="blue",
            padding=(0, 1)
        )
        
        self.console.print(header_panel)
        self.console.print()
    
    def success(self, message: str):
        """Display success message in green."""
        self.console.print(f"✅ [green]{message}[/green]")
    
    def warning(self, message: str):
        """Display warning message in yellow."""
        self.console.print(f"⚠️  [yellow]{message}[/yellow]")
    
    def error(self, message: str):
        """Display error message in red."""
        self.console.print(f"❌ [red]{message}[/red]")
    
    def info(self, message: str):
        """Display informational message in blue/cyan."""
        self.console.print(f"ℹ️  [cyan]{message}[/cyan]")
    
    def step(self, message: str):
        """Display step information with icon."""
        self.console.print(f"🔄 [blue]{message}[/blue]")
    
    def show_code_preview(self, code: str, language: str = "python",
                          title: str = "Generated Code"):
        """Display code in a highlighted block."""
        syntax = Syntax(
            code,
            language,
            theme="monokai",
            line_numbers=True,
            background_color="default"
        )
        
        code_panel = Panel(
            syntax,
            title=f"📝 {title}",
            border_style="green",
            expand=False
        )
        
        self.console.print(code_panel)
    
    def show_execution_logs(self, steps: List[Dict[str, Any]]):
        """Display step-by-step execution logs with status icons."""
        self.console.print("[bold blue]Execution Steps:[/bold blue]")
        
        for i, step in enumerate(steps, 1):
            status = step.get('status', 'pending')
            message = step.get('message', '')
            
            # Choose icon and color based on status
            if status == 'completed':
                icon = "✅"
                style = "green"
            elif status == 'failed':
                icon = "❌"
                style = "red"
            elif status == 'in_progress':
                icon = "🔄"
                style = "blue"
            else:
                icon = "⏳"
                style = "yellow"
            
            step_text = f"  {icon} [{style}]Step {i}: {message}[/{style}]"
            self.console.print(step_text)
    
    def show_clean_error(self, error: Exception, context: str = ""):
        """Display clean error trace without raw stack dumps."""
        error_text = Text()
        error_text.append("Error Details:\n", style="bold red")
        
        if context:
            error_text.append(f"Context: {context}\n", style="red")
        
        error_text.append(f"Type: {type(error).__name__}\n", style="yellow")
        error_text.append(f"Message: {str(error)}", style="white")
        
        error_panel = Panel(
            error_text,
            title="❌ Error",
            border_style="red",
            expand=False
        )
        
        self.console.print(error_panel)
    
    def confirm_changes(self, changes_summary: str) -> bool:
        """Ask user for confirmation before applying changes."""
        self.console.print("\n[yellow]📋 Changes Summary:[/yellow]")
        self.console.print(changes_summary)
        self.console.print()
        
        return Confirm.ask(
            "[yellow]Apply changes?[/yellow]",
            default=False
        )
    
    def show_loading(self, message: str = "Processing..."):
        """Show a loading spinner with message."""
        return Status(f"🔄 {message}", console=self.console, spinner="dots")
    
    def show_progress_bar(self, tasks: List[str]):
        """Show progress bar for multiple tasks."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            
            task_ids = []
            for task in tasks:
                task_id = progress.add_task(task, total=100)
                task_ids.append(task_id)
            
            return progress, task_ids
    
    def display_file_operations(self, operations: List[Dict[str, Any]]):
        """Display file operations in a structured format."""
        if not operations:
            return
        
        self.console.print("\n[bold yellow]📁 File Operations:[/bold yellow]")
        
        for op in operations:
            operation = op.get('operation', 'unknown')
            filepath = op.get('filepath', 'unknown')
            
            # Choose icon and color based on operation
            if operation == 'create':
                icon = "📄"
                style = "green"
            elif operation == 'modify':
                icon = "✏️"
                style = "blue"
            elif operation == 'delete':
                icon = "🗑️"
                style = "red"
            elif operation == 'rollback':
                icon = "↩️"
                style = "yellow"
            else:
                icon = "📋"
                style = "white"
            
            operation_title = operation.title()
            file_op_text = f"  {icon} [{style}]{operation_title}[/{style}]:"
            file_op_text += f" {filepath}"
            self.console.print(file_op_text)
    
    def display_execution_result(self, result: Dict[str, Any]):
        """Display execution results with proper formatting."""
        status = result.get('status', 'unknown')
        
        # Status indicator
        if status == 'completed':
            success_msg = "\n✅ [green]Execution Completed Successfully[/green]"
            self.console.print(success_msg)
        elif status == 'failed':
            self.console.print("\n❌ [red]Execution Failed[/red]")
        else:
            status_msg = f"\n🔄 [yellow]Execution Status: {status}[/yellow]"
            self.console.print(status_msg)
        
        # Execution time
        if 'execution_time' in result:
            exec_time = result['execution_time']
            time_msg = f"⏱️  Execution Time: {exec_time:.3f}s"
            self.console.print(time_msg)
        
        # Output
        if result.get('stdout'):
            output_panel = Panel(
                result['stdout'],
                title="📤 Output",
                border_style="green"
            )
            self.console.print(output_panel)
        
        # Error output
        if result.get('stderr'):
            error_panel = Panel(
                result['stderr'],
                title="⚠️ Error Output",
                border_style="red"
            )
            self.console.print(error_panel)
    
    def display_project_status(self, status: Dict[str, Any]):
        """Display project status in a structured table."""
        stats = status.get("conversation_stats", {})
        
        # Create main status table
        table = Table(title="📊 Project Status", box=box.ROUNDED)
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        table.add_row("Project Root", status.get("project_root", "unknown"))
        table.add_row("Active Files", str(len(status.get("active_files", []))))
        table.add_row("Total Interactions", str(stats.get("total_turns", 0)))
        successful_count = str(stats.get("successful_turns", 0))
        table.add_row("Successful Operations", successful_count)
        table.add_row("Failed Operations", str(stats.get("failed_turns", 0)))
        
        # Calculate success rate
        total = stats.get("total_turns", 0)
        successful = stats.get("successful_turns", 0)
        success_rate = (successful / total * 100) if total > 0 else 0
        table.add_row("Success Rate", f"{success_rate:.1f}%")
        
        self.console.print(table)
        
        # Show active files
        active_files = status.get("active_files", [])
        if active_files:
            self.console.print("\n[bold cyan]📁 Recent Files:[/bold cyan]")
            for file in active_files[-5:]:  # Show last 5 files
                self.console.print(f"  📄 {file}")
            if len(active_files) > 5:
                remaining_count = len(active_files) - 5
                more_files_msg = f"  ... and {remaining_count} more files"
                self.console.print(more_files_msg)
        
        # Show intent statistics
        intent_counts = stats.get("intent_counts", {})
        if intent_counts:
            stats_header = "\n[bold cyan]🎯 Operation Statistics:[/bold cyan]"
            self.console.print(stats_header)
            for intent_type, count in intent_counts.items():
                self.console.print(f"  • {intent_type}: {count}")
    
    def display_search_results(self, results: Dict[str, List[str]],
                               query: str):
        """Display search results in a structured format."""
        if not results:
            self.warning(f"No results found for '{query}'")
            return
        
        search_prefix = "\n[bold green]🔍 Search Results for"
        search_title = f"{search_prefix} '{query}':[/bold green]"
        self.console.print(search_title)
        
        for filepath, matches in results.items():
            # File header
            self.console.print(f"\n📄 [bold cyan]{filepath}[/bold cyan]")
            
            # Show matches (limit to first 3)
            for i, match in enumerate(matches[:3], 1):
                self.console.print(f"  {i}. {match}")
            
            # Show count if more matches
            if len(matches) > 3:
                extra_count = len(matches) - 3
                more_msg = f"  ... and {extra_count} more matches"
                self.console.print(more_msg)
    
    def show_welcome_banner(self, version: str = "1.0.0"):
        """Display welcome banner with styling."""
        welcome_text = f"""
[bold blue]Terminal Coding Agent v{version}[/bold blue]

🤖 Professional AI-powered development assistant
🚀 Generate, modify, and execute code with natural language
🛡️  Safe execution in sandboxed environments
📁 Intelligent file management with version control
🧠 Persistent conversation context and project state

[dim]Enter your development requests in natural language,[/dim]
[dim]or use /help for commands.[/dim]
        """
        
        welcome_panel = Panel(
            Align.center(welcome_text),
            title="🎉 Welcome",
            border_style="blue",
            box=box.DOUBLE
        )
        
        self.console.print(welcome_panel)
        self.console.print()
    
    def show_help(self):
        """Display help information with better formatting."""
        
        # Commands section
        commands_table = Table(title="Available Commands", box=box.ROUNDED)
        commands_table.add_column("Command", style="cyan", no_wrap=True)
        commands_table.add_column("Description", style="white")
        
        commands = [
            ("Create a Python function for [description]",
             "Generate a new function"),
            ("Write a class that [description]", "Create a new class"),
            ("Modify the last function to [description]",
             "Update existing code"),
            ("Run the last function with [test data]",
             "Execute code with input"),
            ("Create a file called [filename]", "Create new file"),
            ("Delete the file [filename]", "Remove file"),
            ("Search for [query]", "Search in codebase"),
            ("Explain the last function", "Get code explanation"),
            ("Refactor the last function", "Improve code structure"),
            ("Debug the last function", "Find and fix issues"),
        ]
        
        for cmd, desc in commands:
            commands_table.add_row(cmd, desc)
        
        # Special commands section
        special_table = Table(title="Special Commands", box=box.ROUNDED)
        special_table.add_column("Command", style="yellow", no_wrap=True)
        special_table.add_column("Description", style="white")
        
        special_commands = [
            ("/help", "Show this help"),
            ("/status", "Show project status"),
            ("/rollback", "Rollback last operation"),
            ("/clear", "Clear project state"),
            ("/export [path]", "Export project"),
            ("/quit", "Exit the agent"),
        ]
        
        for cmd, desc in special_commands:
            special_table.add_row(cmd, desc)
        
        # Examples section
        examples_text = """
[bold green]Examples:[/bold green]
• [cyan]Create a Python function for quicksort[/cyan]
• [cyan]Modify the last function to handle empty lists[/cyan]
• [cyan]Run the last function with [3, 1, 4, 1, 5][/cyan]
• [cyan]Search for "def quicksort"[/cyan]
        """
        
        self.console.print(commands_table)
        self.console.print()
        self.console.print(special_table)
        self.console.print()
        examples_panel = Panel(examples_text, title="💡 Examples",
                               border_style="green")
        self.console.print(examples_panel)


# Global UI manager instance
ui = UIManager()