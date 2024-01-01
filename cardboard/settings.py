"""
Django settings for cardboard project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import logging
import os
from distutils.util import strtobool

from django.core.management.utils import get_random_secret_key

logger = logging.getLogger(__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    logger.warn("No DJANGO_SECRET_KEY set. Generating random secret key")
    SECRET_KEY = get_random_secret_key()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(strtobool(os.environ.get("DEBUG", "false")))

# Hosts/domain names that are valid for this site.
# "*" matches anything, ".example.com" matches example.com and all subdomains
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "smallboard.herokuapp.com",
    ".smallboard.app",
    "cardinality-cardboard.herokuapp.com",
]

CSRF_TRUSTED_ORIGINS = ['chrome-extension://cahmppnjflkbimomgndbcmbdoafdegbi']

# This should be turned on in production to redirect HTTP to HTTPS
# The development web server doesn't support HTTPS, however, so do not
# turn this on in dev.
SECURE_SSL_REDIRECT = bool(strtobool(os.environ.get("SECURE_SSL_REDIRECT", "False")))

# Pass along the original protocol (Heroku does SSL termination)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_beat",
    "puzzles",
    "accounts",
    "chat",
    "hunts",
    "answers",
    "social_django",
    "taggit",
    "rest_framework",
    "corsheaders",
]
# 
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
]

if DEBUG:
    INSTALLED_APPS += ["silk"]
    MIDDLEWARE = ["silk.middleware.SilkyMiddleware"] + MIDDLEWARE

ROOT_URLCONF = "cardboard.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["cardboard/templates/"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "cardboard.context_processors.google_auth",
                "cardboard.context_processors.app_info",
            ],
        },
    },
]

WSGI_APPLICATION = "cardboard.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "cardboard/static"),
    os.path.join(BASE_DIR, "hunts/static"),
]
STATICFILES_STORAGE = "whitenoise.django.CompressedManifestStaticFilesStorage"

# User login
AUTH_USER_MODEL = "accounts.Puzzler"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_ERROR_URL = "/"

# REST API config
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# Configure Django App for Heroku.
import django_heroku

django_heroku.settings(locals(), test_runner=False)

import dj_database_url

DATABASES = {}
DATABASES["default"] = dj_database_url.config(conn_max_age=600, ssl_require=False)
DATABASES["default"]["TEST"] = {"NAME": "test_cardboard"}

# App title
APP_TITLE = os.environ.get("APP_TITLE", "Cardinality Cardboard")
APP_SHORT_TITLE = os.environ.get("APP_SHORT_TITLE", "Cardboard")

# Contact info
CONTACT_AUTHOR_NAME = os.environ.get("CONTACT_AUTHOR_NAME", "Cardinality")
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "FIXME@FIXME.COM")

# Discord API. See
# https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-
DISCORD_API_TOKEN = os.environ.get("DISCORD_API_TOKEN", None)

# Discord Bot settings

# TODO(akirabaruah): This is a hack. Find a better way to set the bot's hunt.
BOT_ACTIVE_HUNT = os.environ.get("BOT_ACTIVE_HUNT", None)

# Google Drive API
GOOGLE_DRIVE_HUNT_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_HUNT_FOLDER_ID", None)
GOOGLE_SHEETS_TEMPLATE_FILE_ID = os.environ.get("GOOGLE_SHEETS_TEMPLATE_FILE_ID", None)
try:
    GOOGLE_API_AUTHN_INFO = {
        "type": "service_account",
        "project_id": os.environ["GOOGLE_API_PROJECT_ID"],
        "private_key_id": os.environ["GOOGLE_API_PRIVATE_KEY_ID"],
        "private_key": os.environ["GOOGLE_API_PRIVATE_KEY"].replace("\\n", "\n"),
        "client_email": os.environ["GOOGLE_API_CLIENT_EMAIL"],
        "client_id": os.environ["GOOGLE_API_CLIENT_ID"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ["GOOGLE_API_X509_CERT_URL"],
    }
    GOOGLE_DRIVE_PERMISSIONS_SCOPES = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.activity",
        "https://www.googleapis.com/auth/contacts",
        "https://www.googleapis.com/auth/directory.readonly",
    ]
except KeyError as e:
    GOOGLE_API_AUTHN_INFO = None
    logger.warn(
        f"No {e.args[0]} found in environment. Automatic sheets creation disabled."
    )


AUTHENTICATION_BACKENDS = [
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
]

SOCIAL_AUTH_URL_NAMESPACE = "social"

# Cardboard client id
try:
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ["SOCIAL_AUTH_GOOGLE_OAUTH2_KEY"]
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ["SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET"]
    # store google UID, so it can be used in lookups for sheet activity.
    SOCIAL_AUTH_GOOGLE_OAUTH2_USE_UNIQUE_USER_ID = True
except KeyError as e:
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = None
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = None
    logger.warn(
        f"No {e.args[0]} environment variable set. Google login will be disabled."
    )

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    # custom auth_allowed check in lieu of default one
    "google_api_lib.sync_tasks.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)

# Taggit Overrides
TAGGIT_TAGS_FROM_STRING = "puzzles.tag_utils.to_tag"


# Chat app settings.

import discord_lib

if not "DISCORD_API_TOKEN" in os.environ:
    logger.warn(
        "No Discord API token found in environment. Automatic Discord channel creation disabled."
    )
    CHAT_DEFAULT_SERVICE = None
    CHAT_SERVICES = {}
else:
    CHAT_DEFAULT_SERVICE = "DISCORD"
    CHAT_SERVICES = {
        "DISCORD": discord_lib.DiscordChatService,
    }


# Celery settings
from enum import Enum


class TaskPriority(Enum):
    HIGH = 9
    MED = 5
    LOW = 0


CELERY_IGNORE_RESULT = True
CELERY_TASK_TIME_LIMIT = 60
CELERY_TASK_TRACK_STARTED = True
CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://")
CELERY_BROKER_TRANSPORT_OPTIONS = {"max_retries": 5, "queue_order_strategy": "priority"}
CELERY_BROKER_POOL_LIMIT = 1
CELERY_REDIS_MAX_CONNECTIONS = 1  # Only for sending results, not enqueueing tasks
CELERY_TASK_DEFAULT_PRIORITY = TaskPriority.MED.value
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        },
    },
}

# Redis settings

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://"),
    }
}

# Use 64 bit primary keys
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
