from .base import BaseCommand

class StatusCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "/status"