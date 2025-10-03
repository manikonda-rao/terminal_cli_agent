"""
Interactive CLI interface for the Terminal Coding Agent.
"""

from typing import Optional
from rich.console import Console
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter

from ..core.agent import CodingAgent
from ..core.models import AgentConfig
from ..core.ui import ui


class TerminalCLI:
    """Interactive CLI interface for the coding agent."""
    
    def __init__(self, project_root: str = ".",
                 config: Optional[AgentConfig] = None):
        self.console = Console()
        self.agent = CodingAgent(project_root, config)
        self.history = InMemoryHistory()
        self.running = True
        
        # Set session context
        ui.set_session_context(
            project_name=project_root.split('/')[-1] or "terminal_agent",
            current_file=""
        )
        
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
    
    def _show_welcome(self):
        """Show welcome message using new UI."""
        ui.show_welcome_banner("1.0.0")
        
        # Display project status
        status = self.agent.get_project_status()
        ui.info(f"Project Root: {status['project_root']}")
        total_turns = status['conversation_stats']['total_turns']
        ui.info(f"Session Interactions: {total_turns}")
        self.console.print()
    
    def run(self):
        """Main CLI loop."""
        while self.running:
            try:
                # Show session header
                ui.show_session_header()
                
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
                    self._handle_special_command(user_input)
                    continue
                
                # Process the input with loading indicator
                with ui.show_loading("Processing your request..."):
                    turn = self.agent.process_input(user_input)
                
                # Display results with rich formatting
                self._display_turn_results(turn)
                
            except KeyboardInterrupt:
                ui.warning("\nSession terminated by user.")
                break
            except EOFError:
                ui.info("\nSession terminated.")
                break
            except Exception as e:
                ui.show_clean_error(e, "CLI processing error")
    
    def _handle_special_command(self, command: str):
        """Handle special CLI commands."""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == "/help":
            ui.show_help()
        
        elif cmd == "/status":
            self._show_status()
        
        elif cmd == "/rollback":
            ui.step("Attempting to rollback last operation...")
            success = self.agent.rollback_last_operation()
            if success:
                ui.success("Operation rollback completed successfully")
            else:
                ui.error("Rollback operation failed")
        
        elif cmd == "/clear":
            changes_summary = ("This will reset all project state and "
                               "conversation history.")
            if ui.confirm_changes(changes_summary):
                self.agent.clear_project()
                ui.success("Project state reset completed")
        
        elif cmd == "/export":
            if len(parts) > 1:
                export_path = parts[1]
                ui.step(f"Exporting project to {export_path}...")
                self.agent.export_project(export_path)
                ui.success(f"Project exported to {export_path}")
            else:
                ui.error("Export path required: /export <path>")
        
        elif cmd == "/quit":
            ui.info("Terminal Coding Agent session ended.")
            self.running = False
        
        else:
            ui.error(f"Invalid command: {cmd}")
            ui.info("Use /help to view available commands")
    
    def _show_status(self):
        """Show detailed project status using new UI."""
        status = self.agent.get_project_status()
        ui.display_project_status(status)
    
    def _display_turn_results(self, turn):
        """Display conversation turn results with new UI formatting."""
        # Show generated code
        if turn.generated_code:
            ui.info("Code generation completed")
            for i, code_block in enumerate(turn.generated_code):
                title = "Generated Code"
                if len(turn.generated_code) > 1:
                    title = f"Generated Code Block {i+1}"
                
                ui.show_code_preview(
                    code_block.content,
                    code_block.language.value,
                    title
                )
        
        # Show execution results
        if turn.execution_result:
            result_dict = {
                'status': turn.execution_result.status.value,
                'execution_time': turn.execution_result.execution_time,
                'stdout': turn.execution_result.stdout,
                'stderr': turn.execution_result.stderr
            }
            ui.display_execution_result(result_dict)
        
        # Show file operations
        if turn.file_operations:
            operations = []
            for file_op in turn.file_operations:
                operations.append({
                    'operation': file_op.operation,
                    'filepath': file_op.filepath
                })
            ui.display_file_operations(operations)
        
        # Display operation status
        if turn.success:
            ui.success("Operation completed successfully")
        else:
            ui.error(f"Operation failed: {turn.error_message}")
        
        self.console.print()  # Add spacing


def main():
    """Main entry point for the CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Terminal Coding Agent")
    parser.add_argument("--project-root", default=".",
                        help="Project root directory")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--llm-provider", choices=["openai", "anthropic"],
                        default="openai")
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
