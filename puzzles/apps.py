from django.apps import AppConfig


class PuzzlesConfig(AppConfig):
    name = "puzzles"

    def ready(self):
        import puzzles.signals.handlers
