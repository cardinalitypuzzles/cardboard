#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import dotenv
import os
import sys


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smallboard.settings")

    if "test" in sys.argv:
        test_env_files = [".env.test.user", ".env.test"]
        for dotenv_file in test_env_files:
            if os.path.isfile(dotenv_file):
                dotenv.load_dotenv(dotenv_file)
                break
    else:
        dotenv_file = os.path.join(BASE_DIR, ".env")
        if os.path.isfile(dotenv_file):
            dotenv.load_dotenv(dotenv_file)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
