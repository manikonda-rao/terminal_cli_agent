from typing import List
from .base import BaseCommand

class HelpCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/help"
    
    @property
    def description(self) -> str:
        """Return the command description."""
        return "Shows a list of all the available commands."
    
    @property
    def usage(self) -> str:
        """Return usage information."""
        return "/help"
    
    def execute(self, args:list[str]):
        self.validate_args(args, expected_count=0)
        
        """Show help information."""
        help_text = """
        Terminal Coding Agent Help

        Available Commands:
        • Create a Python function for [description]
        • Write a class that [description]
        • Modify the last function to [description]
        • Run the last function with [test data]
        • Create a file called [filename]
        • Delete the file [filename]
        • Search for [query]
        • Explain the last function
        • Refactor the last function
        • Debug the last function
        • Test the last function

        Special Commands:
        • /help - Show this help
        • /status - Show project status
        • /export [path] - Export project
        • /quit - Exit the agent

        Examples:
        > Create a Python function for quicksort
        > Modify the last function to handle empty lists
        > Run the last function with [3, 1, 4, 1, 5]
        > Search for "def quicksort"
        """
        self.console.print(help_text)