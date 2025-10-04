from .base import BaseCommand

class RollbackCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/rollback"
    
    @property
    def description(self) -> str:
        return "Retrieves the last executed operation."
    
    @property
    def usage(self) -> str:
        return "/rollback"
    
    def execute(self, args):
        self.validate_args(args, expected_count=0)

        success = self.cli.agent.rollback_last_operation()
        if success:
            self.console.print("[green]Operation rollback completed successfully[/green]")
        else:
            self.console.print("[red]Rollback operation failed[/red]")