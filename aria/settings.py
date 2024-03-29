import pathlib
import warnings
from datetime import timedelta

import environ
import sentry_sdk
import structlog.types
from sentry_sdk.integrations.django import DjangoIntegration
from structlog.types import Processor

###############
# Environment #
###############

warnings.filterwarnings("ignore", message="Error reading .env", category=UserWarning)
env = environ.Env()

# If ENV_PATH is set, load that file first, so it wins over any conflicting
# environment variables in `.env`
if "ENV_PATH" in env:
    env.read_env(env.str("ENV_PATH"))

env.read_env(".env")

# Only true in the production environment. Mostly used to guard against running
# dangerous management commands in production.
PRODUCTION = env.bool("PRODUCTION", default=False)

ENVIRONMENT = env.str("ENVIRONMENT", default="dev")

BASE_DIR = (pathlib.Path(__file__).parent / "..").resolve()
APP_DIR = pathlib.Path(__file__).parent.resolve()

DEBUG = env.bool("DEBUG", default=False)

OPENAPI_AUTO_GENERATE = env.bool("OPENAPI_AUTO_GENERATE", default=False)
OPENAPI_SCHEMA_PATH = env.str("OPENAPI_SCHEMA_PATH", default=None)

#################
# Django basics #
#################

# Silenced system checks to prevent warnings about username not unique constraint

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="dev-env-secret-9fprvf3c@7x4ur##")

SILENCED_SYSTEM_CHECKS = env.list("SILENCED_SYSTEM_CHECKS", default=[])

DEFAULT_SITE_ID = 1
SITE_ID = DEFAULT_SITE_ID

ROOT_URLCONF = "aria.urls"

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

HTTPS_ONLY = env.bool("HTTPS_ONLY", default=False)

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)

APPEND_SLASH = env.bool("APPEND_SLASH", default=True)

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Language code for this installation.
LANGUAGE_CODE = "no"

LOCALE_PATHS = (BASE_DIR / "public/translations/",)

LANGUAGES = [
    ("en", "English"),
    ("no", "Norwegian"),
]

# Local time zone for this installation.
TIME_ZONE = "Europe/Oslo"

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

DATE_FORMAT = "%d. %B %Y"

DATETIME_FORMAT = "%d. %B %Y %H:%M"
DATETIME_INPUT_FORMATS = ["%d. %B %Y %H:%M"]

WSGI_APPLICATION = "aria.wsgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

#############
# Templates #
#############

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR / "public/templates")],
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

##############
# Middleware #
##############

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "aria.core.middleware.GenericLoggingMiddleware",
]

MIDDLEWARE_CLASSES = [
    "django.middleware.locale.LocaleMiddleware",
]

########
# Apps #
########

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "django_countries",
    "django_s3_storage",
    "imagekit",
    "mptt",
    "ninja",
]

PROJECT_APPS = [
    "aria.api",
    "aria.api_auth",
    "aria.audit_logs",
    "aria.categories",
    "aria.core",
    "aria.discounts",
    "aria.employees",
    "aria.files",
    "aria.front",
    "aria.kitchens",
    "aria.notes",
    "aria.product_attributes",
    "aria.products",
    "aria.suppliers",
    "aria.users",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS

#########
# Files #
#########

DEFAULT_FILE_STORAGE = "aria.files.storage.S3Storage"
STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"

# Files auth.
AWS_REGION = env.str("AWS_REGION", default="local")
AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", default="aria")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", default="ariatestpassword")
AWS_ENDPOINT_URL = env.str("AWS_ENDPOINT_URL", default="http://localhost:9000")

# Files.
MEDIA_URL = env.str("MEDIA_URL", default="/media/")
AWS_S3_ADDRESSING_STYLE = "auto"
AWS_S3_BUCKET_AUTH = False
AWS_S3_BUCKET_NAME = env.str("AWS_S3_BUCKET_NAME", default="dev")
AWS_S3_ENDPOINT_URL = AWS_ENDPOINT_URL
AWS_S3_FILE_OVERWRITE = False
AWS_S3_MAX_AGE_SECONDS = 60 * 60 * 24 * 365  # 1 year.
AWS_S3_SIGNATURE_VERSION = None

# Static files.
STATIC_URL = env.str("STATIC_URL", default="/static/")
AWS_S3_BUCKET_AUTH_STATIC = False
AWS_S3_BUCKET_NAME_STATIC = env.str("AWS_S3_BUCKET_NAME_STATIC", default="dev")
AWS_S3_ENDPOINT_URL_STATIC = AWS_ENDPOINT_URL
AWS_S3_KEY_PREFIX_STATIC = "static"

###################
# Files: imagekit #
###################

IMAGEKIT_CACHEFILE_DIR = "media/cache"
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = "imagekit.cachefiles.strategies.Optimistic"

##################
# Authentication #
##################

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # pylint: disable=line-too-long
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

#############
# Databases #
#############

DATABASES = {
    "default": env.db_url(
        "DATABASE_URL", default="postgresql://aria:aria@localhost:5433/aria"
    ),
}

LOG_SQL = env.bool("LOG_SQL", default=False)

QUERY_COUNT_WARNING_THRESHOLD = 25
QUERY_DURATION_WARNING_THRESHOLD = 300  # in ms

if DEBUG:
    MIDDLEWARE = ["aria.core.middleware.QueryCountWarningMiddleware"] + MIDDLEWARE

###########
# Logging #
###########

log_renderer: Processor = (
    structlog.dev.ConsoleRenderer(colors=True, sort_keys=True)  # type: ignore
    if DEBUG
    else structlog.processors.JSONRenderer()
)

shared_log_processors: list[Processor] = [
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
]

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        *shared_log_processors,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": log_renderer,
            "foreign_pre_chain": shared_log_processors,
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        }
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "console": {
            "filters": ["require_debug_true"],
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

##########
# Caches #
##########

CACHES = {
    "default": env.cache("CACHE_URL", default="redis://localhost:6379/"),
}

if CACHES["default"]["BACKEND"] == "django_redis.cache.RedisCache":
    CACHES["default"]["OPTIONS"] = {
        "CLIENT_CLASS": "django_redis.client.DefaultClient",
        "PARSER_CLASS": "redis.connection.HiredisParser",
    }


##########
# Celery #
##########

CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = {"json"}
CELERY_WORKER_DISABLE_RATE_LIMITS = True
CELERY_IGNORE_RESULT = False
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True
CELERY_TIMEZONE = TIME_ZONE
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_TASK_EAGER_PROPAGATES = env.bool("CELERY_TASK_EAGER_PROPAGATES", default=False)
CELERY_TASK_SOFT_TIME_LIMIT = 300
CELERY_TASK_TIME_LIMIT = 500
CELERY_BROKER_POOL_LIMIT = 100
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", default="redis://localhost:6379/")

CELERY_TASK_DEFAULT_QUEUE = "celery"
CELERY_TASK_DEFAULT_EXCHANGE = "celery"
CELERY_TASK_DEFAULT_EXCHANGE_TYPE = "direct"
CELERY_TASK_DEFAULT_ROUTING_KEY = "celery"

# Adding new task queues? Make sure to aslo include them in render.yaml celery
# definitions for all environtments.
CELERY_TASK_QUEUE_IMPORTANT = "important"
CELERY_TASK_QUEUE_NEWSLETTER = "newsletter"

################
# API Auth JWT #
################

JWT_ISSUER = "api.flis.no"
JWT_SIGNING_KEY = SECRET_KEY
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_LIFETIME = timedelta(hours=1)
JWT_REFRESH_TOKEN_LIFETIME = timedelta(days=30)

#########
# Email #
#########

EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = env.str("SENDGRID_API_KEY", default="")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="")

##########
# Sentry #
##########

SENTRY_DSN = env.str("SENTRY_DSN", default=None)

if SENTRY_DSN is not None:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENVIRONMENT,
        integrations=[DjangoIntegration()],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )

#####################
# Django Extensions #
#####################

try:
    import django_extensions  # noqa: 401 # pylint: disable=unused-import
except ImportError:
    DJANGO_EXTENSIONS_INSTALLED = False
else:
    DJANGO_EXTENSIONS_INSTALLED = True

if DJANGO_EXTENSIONS_INSTALLED:
    INSTALLED_APPS += ["django_extensions"]
