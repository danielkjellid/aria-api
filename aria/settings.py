import pathlib
import warnings
from datetime import timedelta

import django_heroku
import environ

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

ENVIRONMENT = env.str("ENVIRONMENT", default="dev")

BASE_DIR = (pathlib.Path(__file__).parent / "..").resolve()

DEBUG = env.bool("DEBUG", default=False)

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

HTTPS_ONLY = env.bool("HTTPS_ONLY", default=False)

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)

SECURE_PROXY_SSL_HEADER = env.tuple("SECURE_PROXY_SSL_HEADER")

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

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

WSGI_APPLICATION = "aria.wsgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

#############
# Templates #
#############

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR / "aria/templates")],
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
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "rest_framework_simplejwt.token_blacklist",
    "django_s3_storage",
    "imagekit",
]

PROJECT_APPS = [
    "aria.core",
    "aria.audit_logs",
    "aria.users",
    "aria.kitchens",
    "aria.products",
    "aria.product_categorization",
    "aria.suppliers",
    "aria.notes",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS

####################################
# Files backend: django_s3_storage #
####################################

AWS_REGION = "eu-north-1"
AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = env.str("AWS_S3_BUCKET_NAME")

AWS_S3_ADDRESSING_STYLE = "auto"
AWS_S3_BUCKET_AUTH = False
AWS_S3_MAX_AGE_SECONDS = 60 * 60 * 24 * 365  # 1 year.
AWS_S3_SIGNATURE_VERSION = None
AWS_S3_FILE_OVERWRITE = False
AWS_S3_BUCKET_AUTH_STATIC = False
AWS_S3_BUCKET_NAME_STATIC = env.str("AWS_S3_BUCKET_NAME_STATIC")
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
STATIC_URL = env.str("STATIC_URL")

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
    "default": env.db(),
}

##########
# Caches #
##########


##############
# Simple JWT #
##############

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("JWT",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}

#########
# Email #
#########

EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = env.str("SENDGRID_API_KEY")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL")

##################
# REST framework #
##################

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": env.list(
        "DEFAULT_AUTHENTICATION_CLASSES",
        default=["rest_framework_simplejwt.authentication.JWTAuthentication"],
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": env.list(
        "DEFAULT_RENDERER_CLASSES", default=["rest_framework.renderers.JSONRenderer"]
    ),
    "DATETIME_FORMAT": "%d. %B %Y %H:%M",
    "DATETIME_INPUT_FORMATS": ["%d. %B %Y %H:%M"],
}

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


django_heroku.settings(locals())

# django_heroku sets sslmode to required by default
# this overrides it in the dev env.
if ENVIRONMENT == "dev":
    locals()["DATABASES"]["default"]["OPTIONS"]["sslmode"] = "disable"
