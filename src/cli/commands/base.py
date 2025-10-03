from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from rich.console import Console

class CommandError(Exception):
    """Base exception for command execution errors."""
    pass


class ArgumentError(CommandError):
    """Exception raised when command arguments are invalid."""
    pass


class BaseCommand:
    def __init__(self, cli, console):
        self.cli = cli
        self.console = console

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass
    
    @property
    def usage(self) -> str:
        return f"/{self.name}"
    
    @abstractmethod
    def execute(self, args: List[str]) -> bool:
        """
        Execute the command with the given arguments.
        
        This is the main method that subclasses must implement to define
        the command's behavior.
        
        Args:
            args: List of arguments passed to the command (excluding the command name)
        
        Returns:
            bool: True if command executed successfully, False otherwise
        
        Raises:
            CommandError: If command execution fails
            ArgumentError: If arguments are invalid
        """
        pass

    def get_help(self) -> str:
        """
        Return detailed help text for the command.
        
        Override this in subclasses to provide comprehensive help information.
        Default returns the description.
        
        Returns:
            str: Detailed help text
        """
        return self.description
    
    def validate_args(self, args: List[str], expected_count: Optional[int] = None,
                     min_count: Optional[int] = None, max_count: Optional[int] = None) -> None:
        """
        Validate command arguments.
        
        Utility method for common argument validation patterns.
        
        Args:
            args: List of arguments to validate
            expected_count: Exact number of arguments expected
            min_count: Minimum number of arguments expected
            max_count: Maximum number of arguments expected
        
        Raises:
            ArgumentError: If validation fails
        """
        arg_count = len(args)
        
        if expected_count is not None and arg_count != expected_count:
            raise ArgumentError(
                f"Command '{self.name}' expects {expected_count} argument(s), "
                f"but {arg_count} were provided.\nUsage: {self.usage}"
            )
        
        if min_count is not None and arg_count < min_count:
            raise ArgumentError(
                f"Command '{self.name}' expects at least {min_count} argument(s), "
                f"but {arg_count} were provided.\nUsage: {self.usage}"
            )
        
        if max_count is not None and arg_count > max_count:
            raise ArgumentError(
                f"Command '{self.name}' expects at most {max_count} argument(s), "
                f"but {arg_count} were provided.\nUsage: {self.usage}"
            )
    
    def parse_args(self, args: List[str]) -> Dict[str, Any]:
        """
        Parse command arguments into a dictionary.
        
        Override this in subclasses for complex argument parsing.
        Default implementation returns empty dict.
        
        Args:
            args: List of arguments to parse
        
        Returns:
            Dict[str, Any]: Parsed arguments as key-value pairs
        """
        return {}
    
    def _print_success(self, message: str) -> None:
        """
        Print a success message.
        
        Args:
            message: Success message to display
        """
        self.console.print(f"[green]{message}[/green]")
    
    def _print_error(self, message: str) -> None:
        """
        Print an error message.
        
        Args:
            message: Error message to display
        """
        self.console.print(f"[red]{message}[/red]")
    
    def _print_warning(self, message: str) -> None:
        """
        Print a warning message.
        
        Args:
            message: Warning message to display
        """
        self.console.print(f"[yellow]{message}[/yellow]")
    
    def _print_info(self, message: str) -> None:
        """
        Print an informational message.
        
        Args:
            message: Info message to display
        """
        self.console.print(f"[cyan]{message}[/cyan]")
    
    def __repr__(self) -> str:
        """Return string representation of the command."""
        return f"<{self.__class__.__name__}(name='{self.name}')>"


