import os
from datetime import timedelta
import django_heroku

###############
# Environment #
###############

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

#################
# Django basics #
#################

# Silenced system checks to prevent warnings about username not unique constraint
SILENCED_SYSTEM_CHECKS = ["auth.E003", "auth.W004"]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "{{ secret_key }}"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

DEFAULT_SITE_ID = 1
SITE_ID = DEFAULT_SITE_ID

ROOT_URLCONF = "aria.urls"

# Hosts/domain names that are valid for this site; required if DEBUG is False
ALLOWED_HOSTS = ["{{ allowed_hosts }}"]

CORS_ALLOWED_ORIGINS = []

APPEND_SLASH = True

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

#############
# Templates #
#############

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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


##########
# Files #
#########

STATIC_ROOT = os.path.join(f"{BASE_DIR}", "staticfiles")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

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
EMAIL_HOST_PASSWORD = "{{ SENDGRID_API_KEY }}"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
DEFAULT_FROM_EMAIL = "{{ DEFAULT_FROM_EMAIL }}"

##################
# REST framework #
##################

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DATETIME_FORMAT": "%d. %B %Y %H:%M",
    "DATETIME_INPUT_FORMATS": ["%d. %B %Y %H:%M"],
}


#####################
# Django Extensions #
#####################

try:
    import django_extensions
except ImportError:
    DJANGO_EXTENSIONS_INSTALLED = False
else:
    DJANGO_EXTENSIONS_INSTALLED = True

if DJANGO_EXTENSIONS_INSTALLED:
    INSTALLED_APPS += ["django_extensions"]

try:
    from aria.local_settings import *
except ImportError:
    pass

django_heroku.settings(locals())
