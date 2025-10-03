from .base import BaseCommand

class RollbackCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/rollback"