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

from .commands import CommandRegistry
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

        self.command_registry = CommandRegistry(self, self.console)
    
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
                    self.command_registry.get_command(user_input)

                    # self._handle_special_command(user_input)
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
        # Show generated responses
        if turn.generated_code:
            ui.info("Response generated")
            for i, code_block in enumerate(turn.generated_code):
                # Check if this is a direct response
                if code_block.metadata.get("type") == "direct_response":
                    # Display as text response instead of code
                    ui.show_direct_response(code_block.content, f"Response {i+1}" if len(turn.generated_code) > 1 else "Response")
                else:
                    # Display as code
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
    import os
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Terminal Coding Agent")
    parser.add_argument("--project-root", default=".",
                        help="Project root directory")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--llm-provider", choices=["openai", "anthropic"],
                        help="LLM provider (if not specified, will prompt for selection)")
    parser.add_argument("--model", help="LLM model name")
    
    args = parser.parse_args()
    
    # Determine LLM provider
    llm_provider = args.llm_provider
    if not llm_provider:
        llm_provider = _select_llm_provider()
    
    # Determine model name
    model_name = args.model
    if not model_name:
        model_name = _get_default_model(llm_provider)
    
    # Load configuration from environment
    config = AgentConfig(
        llm_provider=llm_provider,
        model_name=model_name,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_execution_time=int(os.getenv("MAX_EXECUTION_TIME", "30")),
        max_memory_mb=int(os.getenv("MAX_MEMORY_USAGE", "512")),
        sandbox_timeout=int(os.getenv("SANDBOX_TIMEOUT", "60")),
        enable_syntax_highlighting=os.getenv("ENABLE_SYNTAX_HIGHLIGHTING", "true").lower() == "true",
        enable_autocomplete=os.getenv("ENABLE_AUTOCOMPLETE", "true").lower() == "true",
        history_size=int(os.getenv("HISTORY_SIZE", "1000"))
    )
    
    # Create and run CLI
    cli = TerminalCLI(args.project_root, config)
    cli.run()


def _select_llm_provider():
    """Allow user to select LLM provider interactively."""
    import os
    from rich.prompt import Prompt
    from rich.console import Console
    
    console = Console()
    
    # Check which providers are available
    available_providers = []
    
    if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your_openai_api_key_here":
        available_providers.append("openai")
    
    if os.getenv("ANTHROPIC_API_KEY") and os.getenv("ANTHROPIC_API_KEY") != "your_anthropic_api_key_here":
        available_providers.append("anthropic")
    
    if not available_providers:
        console.print("[red]❌ No LLM providers configured![/red]")
        console.print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
        console.print("Example:")
        console.print("OPENAI_API_KEY=sk-your-key-here")
        console.print("ANTHROPIC_API_KEY=sk-ant-your-key-here")
        return None
    
    console.print("\n[bold blue]🤖 Available LLM Providers:[/bold blue]")
    for i, provider in enumerate(available_providers, 1):
        console.print(f"  {i}. {provider.title()}")
    
    while True:
        try:
            choice = Prompt.ask(
                f"\n[cyan]Select LLM provider (1-{len(available_providers)})[/cyan]",
                default="1"
            )
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(available_providers):
                selected_provider = available_providers[choice_idx]
                console.print(f"[green]✅ Selected: {selected_provider.title()}[/green]")
                return selected_provider
            else:
                console.print("[red]❌ Invalid choice. Please try again.[/red]")
        except ValueError:
            console.print("[red]❌ Please enter a valid number.[/red]")


def _get_default_model(provider):
    """Get default model for the selected provider."""
    defaults = {
        "openai": "gpt-4",
        "anthropic": "claude-3-sonnet-20240229"
    }
    return defaults.get(provider, "gpt-4")


if __name__ == "__main__":
    main()
