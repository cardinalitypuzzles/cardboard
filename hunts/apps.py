from django.apps import AppConfig


class HuntsConfig(AppConfig):
    name = "hunts"

    def ready(self):
        import hunts.signals
