from django.test import override_settings
from django.test.runner import DiscoverRunner

from cardboard.celery import app as celery_app

# Settings that would let tests talk to real external services. They are read
# from the environment, so a developer with a complete .env (e.g. inside the
# docker container) would otherwise run tests against live Google/Discord.
# Tests that need an integration should opt in with override_settings and mock
# the API calls.
ISOLATED_SETTINGS = {
    "GOOGLE_API_AUTHN_INFO": None,
    "GOOGLE_DRIVE_HUNT_FOLDER_ID": None,
    "GOOGLE_SHEETS_TEMPLATE_FILE_ID": None,
    "DISCORD_API_TOKEN": None,
    "CHAT_DEFAULT_SERVICE": None,
    "CHAT_SERVICES": {},
}


class UnmockedCeleryTaskError(AssertionError):
    pass


def _refuse_to_send_task(name, *args, **kwargs):
    raise UnmockedCeleryTaskError(
        f"Test tried to enqueue Celery task {name!r}. Tests must not send real "
        "tasks: patch the task's .delay/.apply_async, or avoid triggering it."
    )


class IsolatedTestRunner(DiscoverRunner):
    """Test runner that keeps tests from reaching external services.

    It disables the Google and Discord integrations, and makes sending a Celery
    task raise UnmockedCeleryTaskError. Otherwise any task a test enqueues lands
    in the real Redis queue, where a running worker picks it up and executes it
    against the *development* database (not the test database) and the real
    APIs. Tests that exercise code which enqueues tasks must patch them.
    """

    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        self._settings_override = override_settings(**ISOLATED_SETTINGS)
        self._settings_override.enable()
        # Every Task.delay/apply_async goes through app.send_task.
        celery_app.send_task = _refuse_to_send_task

    def teardown_test_environment(self, **kwargs):
        del celery_app.send_task  # restore the class method
        self._settings_override.disable()
        super().teardown_test_environment(**kwargs)
