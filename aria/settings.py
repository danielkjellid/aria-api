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
LANGUAGE_CODE = "nb-NO"

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
    "aria.core.middleware.DynamicSiteDomainMiddleware",
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
    "django.contrib.sites",
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
    "aria.kitchens",
    "aria.notes",
    "aria.products",
    "aria.suppliers",
    "aria.users",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS

####################################
# Files backend: django_s3_storage #
####################################

AWS_REGION = "eu-north-1"
AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", default="")
AWS_S3_BUCKET_NAME = env.str("AWS_S3_BUCKET_NAME", default="")

AWS_S3_ADDRESSING_STYLE = "auto"
AWS_S3_BUCKET_AUTH = False
AWS_S3_MAX_AGE_SECONDS = 60 * 60 * 24 * 365  # 1 year.
AWS_S3_SIGNATURE_VERSION = None
AWS_S3_FILE_OVERWRITE = False
AWS_S3_BUCKET_AUTH_STATIC = False
AWS_S3_BUCKET_NAME_STATIC = env.str("AWS_S3_BUCKET_NAME_STATIC", default="")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_S3_BUCKET_NAME}.s3.amazonaws.com"

##########
# Files #
#########

if ENVIRONMENT == "dev":
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
else:
    DEFAULT_FILE_STORAGE = "django_s3_storage.storage.S3Storage"
    STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"

PUBLIC_ROOT_PATH = BASE_DIR / "public"

MEDIA_ROOT = str(PUBLIC_ROOT_PATH / "media")
MEDIA_URL = env.str("MEDIA_URL", default="/media/")

# Static files
STATIC_ROOT = str(PUBLIC_ROOT_PATH / "static")
STATIC_URL = env.str("STATIC_URL", default="/static/")

IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = "imagekit.cachefiles.strategies.Optimistic"

##################
# Authentication #
##################

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "aria.core.authentication.AuthBackend",
]

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
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

#############
# Databases #
#############

DATABASES = {
    "default": env.db_url(
        "DATABASE_URL", default="postgresql://aria:aria@localhost:5433/aria"
    ),
}

LOG_SQL = env.bool("LOG_SQL", default=False)

if DEBUG:
    QUERY_COUNT_WARNING_THRESHOLD = 20
    QUERY_DURATION_WARNING_THRESHOLD = 300  # in ms
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
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
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
    import django_extensions  # noqa: 401
except ImportError:
    DJANGO_EXTENSIONS_INSTALLED = False
else:
    DJANGO_EXTENSIONS_INSTALLED = True

if DJANGO_EXTENSIONS_INSTALLED:
    INSTALLED_APPS += ["django_extensions"]
