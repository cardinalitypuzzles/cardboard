import os
import sys

import dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEST_ENV_FILES = [".env.test.user", ".env.test"]
DEFAULT_ENV_FILE = ".env"

_loaded = False


def is_test_run():
    return "test" in sys.argv


def load_env():
    """Load environment variables from the right dotenv file for this process.

    Test runs load the first of .env.test.user / .env.test that exists and
    never .env, so a developer's real credentials can't leak into tests.
    Everything else loads .env.

    Every entry point (manage.py, and celery/gunicorn via the cardboard
    package) calls this. Only the first call does anything, so whichever entry
    point runs first can't be undone by a later one loading a different file.
    """
    global _loaded
    if _loaded:
        return
    _loaded = True

    candidates = TEST_ENV_FILES if is_test_run() else [DEFAULT_ENV_FILE]
    for name in candidates:
        path = os.path.join(BASE_DIR, name)
        if os.path.isfile(path):
            dotenv.load_dotenv(path)
            return
