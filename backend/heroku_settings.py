"""
Production settings for Heroku
"""

import environ

from backend.settings import *

env = environ.Env(
  DEBUG =(bool, False)
)

# false if not in os.environ
DEBUG = env('DEBUG')

# raises django's ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')

AWS_REGION = 'eu-north-1'
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = env('AWS_S3_BUCKET_NAME')

AWS_S3_ADDRESSING_STYLE = 'auto'
AWS_S3_BUCKET_AUTH = False
AWS_S3_MAX_AGE_SECONDS = 60 * 60 * 24 * 365  # 1 year.
AWS_S3_SIGNATURE_VERSION = None
AWS_S3_FILE_OVERWRITE = False
AWS_S3_BUCKET_AUTH_STATIC = False
AWS_S3_BUCKET_NAME_STATIC = 'flishuset'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_S3_BUCKET_NAME

STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_S3_BUCKET_NAME_STATIC)
STATICFILES_STORAGE = 'django_s3_storage.storage.StaticS3Storage'
DEFAULT_FILE_STORAGE = 'django_s3_storage.storage.S3Storage'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# parse database connection url strings like psql://user:pass@127.0.0.1:8458/db
DATABASES = {
    # read os.environ['DATABASE_URL'] and raises ImproperlyConfigured exception if not found
    'default': env.db(),
}

EMAIL_HOST_PASSWORD = env('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')