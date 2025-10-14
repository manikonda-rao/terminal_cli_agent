from typing import List
from .base import BaseCommand


class QuitCommand(BaseCommand):
    @property
    def name(self) -> str:
        """Return the command name."""
        return "/quit"
    
    @property
    def description(self) -> str:
        """Return the command description."""
        return "Exit the POGO Terminal"
    
    @property
    def aliases(self) -> List[str]:
        """Return command aliases."""
        return ["/exit", "/q"]
    
    @property
    def usage(self) -> str:
        """Return usage information."""
        return "/quit (or /exit, /q)"
    
    def execute(self, args: List[str]) -> bool:
        # Validate that no arguments were provided
        self.validate_args(args, expected_count=0)

        self.cli.running = False
        
        # Display goodbye message
        self.console.print("\n[cyan]POGO Terminal session ended.[/cyan]")
        self.console.print("Thank you for using POGO Terminal!\n")
        
        # Note: The actual termination is handled by the CLI class
        # This command just signals that termination is requested
        return True
    
    def get_help(self) -> str:
        """Return detailed help text."""
        return """Exit the POGO Terminal CLI.

                    Usage: /quit

                    Aliases: /exit, /q

                    This command terminates the current CLI session. All unsaved work
                    in the current conversation will be lost. Use /export to save your
                    project state before quitting if needed.

                    Examples:
                        /quit       - Exit the application
                        /exit       - Same as /quit
                        /q          - Same as /quit
                    """


# Example of a more complex command with arguments
class ExportCommand(BaseCommand):
    """
    Command to export project state to a directory.
    
    This command demonstrates argument parsing and validation.
    """
    
    @property
    def name(self) -> str:
        """Return the command name."""
        return "export"
    
    @property
    def description(self) -> str:
        """Return the command description."""
        return "Export project to a specified directory"
    
    @property
    def usage(self) -> str:
        """Return usage information."""
        return "/export <path>"
    
    def execute(self, args: List[str]) -> bool:
        """
        Execute the export command.
        
        Args:
            args: Command arguments [path]
        
        Returns:
            bool: True if export succeeded, False otherwise
        """
        # Validate arguments
        try:
            self.validate_args(args, expected_count=1)
        except Exception as e:
            self._print_error(str(e))
            return False
        
        export_path = args[0]
        
        # Execute export
        try:
            self.agent.export_project(export_path)
            self._print_success(f"Project exported successfully to: {export_path}")
            return True
        except Exception as e:
            self._print_error(f"Export failed: {e}")
            return False
    
    def get_help(self) -> str:
        """Return detailed help text."""
        return """Export the current project state to a directory.

Usage: /export <path>

Arguments:
    path    - Destination directory path for the export

This command exports all project files, conversation history, and
metadata to the specified directory. The directory will be created
if it doesn't exist.

Examples:
    /export ./backup              - Export to backup directory
    /export /tmp/my-project       - Export to absolute path
    /export ~/projects/export-1   - Export to home directory
"""


# Example of a command requiring confirmation
class ClearCommand(BaseCommand):
    """
    Command to clear project state.
    
    This command demonstrates confirmation handling for destructive operations.
    """
    
    @property
    def name(self) -> str:
        """Return the command name."""
        return "clear"
    
    @property
    def description(self) -> str:
        """Return the command description."""
        return "Reset project state (destructive operation)"
    
    @property
    def requires_confirmation(self) -> bool:
        """This command requires user confirmation."""
        return True
    
    @property
    def confirmation_message(self) -> str:
        """Return confirmation message."""
        return "Confirm project state reset (this action cannot be undone):"
    
    def execute(self, args: List[str]) -> bool:
        """
        Execute the clear command.
        
        Note: Confirmation is handled by the CLI before this method is called.
        
        Args:
            args: Command arguments (none expected)
        
        Returns:
            bool: True if clear succeeded, False otherwise
        """
        # Validate arguments
        try:
            self.validate_args(args, expected_count=0)
        except Exception as e:
            self._print_error(str(e))
            return False
        
        # Execute clear
        try:
            self.agent.clear_project()
            self._print_success("Project state reset completed")
            return True
        except Exception as e:
            self._print_error(f"Clear operation failed: {e}")
            return False
    
    def get_help(self) -> str:
        """Return detailed help text."""
        return """Reset the project state to initial conditions.

Usage: /clear

WARNING: This is a destructive operation that cannot be undone!

This command:
- Clears all conversation history
- Removes all generated files
- Resets project statistics
- Returns the project to initial state

You will be prompted for confirmation before the operation executes.
Consider using /export to backup your project before clearing.

Examples:
    /clear    - Reset project (will prompt for confirmation)
"""