from .base import BaseCommand

class ExportCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/export"
    
    @property
    def description(self) -> str:
        return "Exports the project with conversation history to the path specified."
    
    @property
    def usage(self) -> str:
        return "/export path/to/your/output/file"

    def execute(self, args: list[str]):
        self.validate_args(args, expected_count=1)
        export_path = args[0]
        
        self.cli.agent.export_project(export_path)
