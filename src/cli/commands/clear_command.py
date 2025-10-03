from .base import BaseCommand
from rich.prompt import Prompt

class ClearCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/clear"
    
    @property
    def description(self) -> str:
        return "Resets the project state. Cannot be undone"
    
    @property
    def usage(self) -> str:
        return "/clear"
    
    def execute(self, args: list[str]):
        self.validate_args(args, expected_count=0)
        
        confirm = Prompt.ask(
            "Confirm project state reset? (This action cannot be undone!):",
            choices=["y", "n"],
            default="n"
        )

        if(confirm.lower()=="y"):
            self.clear_project()
            self.console.print("[green]Project state reset completed[/green]")
        else:
            self.console.print("[yellow]Project reset cancelled[/yellow]")

    def clear_project(self):
        # Reset the agent memory directly
        self.cli.agent.memory.clear_memory()
        # You can add extra cleanup logic here later if needed
        self.console.print("[blue] Project cleared and reset[/blue]")
    
