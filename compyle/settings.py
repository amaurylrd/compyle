import os
import sys
from urllib.parse import quote

SETTINGS_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(SETTINGS_DIR)

TESTING = sys.argv[1:2] == ["test"]

SECRET_KEY = "django-insecure-+$))w01^9gwz#7fal8+al7s4h_*wt=!tt7&eve2w039$=$oj0-"  # nosec

DEBUG = False

ALLOWED_HOSTS = ["*"]
USE_X_FORWARDED_HOST = True
APPEND_SLASH = False

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "corsheaders",
    "compyle.proxy",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "compyle.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
    "PAGE_SIZE": 20,
}

DRF_STANDARDIZED_ERRORS = {
    # enable the standardized errors when DEBUG=True for unhandled exceptions.
    # By default, this is set to False so you're able to view the traceback in
    # the terminal and get more information about the exception.
    "ENABLE_IN_DEBUG_FOR_UNHANDLED_EXCEPTIONS": True,
}

# Celery configuration
# https://docs.celeryproject.org/en/stable/userguide/configuration.html

BROKER_USER = quote(os.environ.get("CELERY_BROKER_USER", "compyle"))
BROKER_PASSWORD = quote(os.environ.get("CELERY_BROKER_PASSWORD", "compyle"))
BROKER_HOST = os.environ.get("CELERY_BROKER_HOST", "localhost")
BROKER_PORT = os.environ.get("CELERY_BROKER_PORT", "5672")
BROKER_VHOST = quote(os.environ.get("CELERY_BROKER_VHOST", "compyle"))
BROKER_PROTOCOL = os.environ.get("CELERY_BROKER_PROTOCOL", "amqp")

CELERY_BROKER_URL = f"{BROKER_PROTOCOL}://{BROKER_USER}:{BROKER_PASSWORD}@{BROKER_HOST}:{BROKER_PORT}/{BROKER_VHOST}"
CELERY_RESULT_BACKEND = "redis://localhost:6379/1"

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True
CELERY_RESULT_EXPIRES = int(os.getenv("CELERY_RESULT_EXPIRES", "3600"))
CELERY_ACKS_LATE = True
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_MAX_TASKS_PER_CHILD = int(os.getenv("CELERY_WORKER_MAX_TASKS_PER_CHILD", "100"))
CELERY_TASK_RETRY_MAX = int(os.getenv("CELERY_TASK_RETRY_MAX", "3"))
CELERY_TASK_RETRY_DELAY = int(os.getenv("CELERY_TASK_RETRY_DELAY", "60"))
CELERY_TIMEZONE = "UTC"

# Redis configuration
# https://docs.celeryproject.org/en/stable/userguide/configuration.html#std:setting-REDIS_URL

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_USER = os.getenv("REDIS_USER")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Channels configuration
# https://channels.readthedocs.io/en/stable/topics/channel_layers.html#redis-channel-layer

ASGI_APPLICATION = "compyle.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            # https://redis.readthedocs.io/en/latest/connections.html#redis.Redis
            "hosts": [
                {
                    "host": REDIS_HOST,
                    "port": REDIS_PORT,
                    "username": REDIS_USER,
                    "password": REDIS_PASSWORD,
                    "health_check_interval": 10,
                    "socket_connect_timeout": 5,
                    "socket_keepalive": True,
                    "retry_on_timeout": True,
                }
            ],
        },
    },
}

if not TESTING:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.getenv("CACHE_REDIS_URL", "redis://127.0.0.1:6379"),
            "OPTIONS": {
                "parser_class": "redis.connection.PythonParser",
                "pool_class": "redis.BlockingConnectionPool",
            },
            "TIMEOUT": int(os.getenv("CACHE_TIMEOUT", "120")),
        }
    }


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "compyle"),
        "USER": os.getenv("POSTGRES_USER", "compyle"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "compyle"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "CONN_HEALTH_CHECKS": True,
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Logging
# https://docs.djangoproject.com/en/5.1/topics/logging/#logging-from-django

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "standard": {
            "format": "[%(asctime)s][%(levelname).4s] %(message)s - %(pathname)s:%(lineno)s",
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {"handlers": ["console"], "propagate": False, "level": "INFO"},
        "django.request": {
            "handlers": ["console"],
            "propagate": False,
            "level": "INFO",
        },
        "": {"handlers": ["console"], "level": "INFO", "propagate": True},
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

MEDIA_ROOT = BASE_DIR + "/media/"
MEDIA_URL = "/media/"

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

SERVE_MEDIA = True

CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ["Content-Disposition"]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

RENDERER_MEDIA_NAME = "compyle"

globals().update(locals())
