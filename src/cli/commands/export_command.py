from .base import BaseCommand

class ExportCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/export"
    
    @property
    def description(self) -> str:
        pass

    def execute(self, args):
        pass
