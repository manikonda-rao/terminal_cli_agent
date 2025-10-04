from .base import BaseCommand
from typing import Dict, Any
from rich.table import Table

class StatusCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/status"
    
    @property
    def description(self) -> str:
        """Return the command description."""
        return "Displays the current detailed project status."
    
    @property
    def usage(self) -> str:
        """Return usage information."""
        return "/status"
    
    def execute(self, args: list[str]):
        self.validate_args(args, expected_count=0)

        status = self.get_project_status()

        # Create status table
        table = Table(title="Project Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Project Root", status["project_root"])
        table.add_row("Active Files", str(len(status["active_files"])))
        
        self.console.print(table)


    def get_project_status(self) -> Dict[str, Any]:
        """Get current project status."""
        project_state = self.cli.agent.file_manager.get_project_state()
    
        return {
            "project_root": self.cli.agent.project_root,
            "active_files": project_state.active_files,
            "config": self.cli.agent.config.to_dict()
        }
