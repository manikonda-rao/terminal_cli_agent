from .clear_command import ClearCommand
from .export_command import ExportCommand
from .help_command import HelpCommand
from .quit_command import QuitCommand
from .rollback_command import RollbackCommand
from .status_command import StatusCommand

class CommandRegistry:
    def __init__(self, cli, console):
        self.cli = cli
        self.console = console
        self.commands = {
            cmd.name : cmd for cmd in [
                HelpCommand(cli, console), QuitCommand(cli, console), ExportCommand(cli, console),
                RollbackCommand(cli, console), StatusCommand(cli, console), ClearCommand(cli, console)
            ]
        }

    def get_command(self, user_input: str):
        parts = user_input.split()
        cmd_name, args = parts[0], parts[1:]
        command = self.commands.get(cmd_name)
        if command:
            command.execute(args)
        else:
            self.console.print(f"[red]Unknown command: {cmd_name}[/red]")
    
    def list_commands(self):
        return self.commands.values()