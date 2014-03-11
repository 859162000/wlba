"""
Django settings for wanglibao project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')#@a(750mv)cn&#@c#^y%52-pof*w%)ba%w5kd1*u0k=l6znj9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Whether the deploy in production
PRODUCTION = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


from registration_defaults.settings import *

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'wanglibao',
    'registration_defaults',
    'django.contrib.admin',

    'rest_framework',
    'south',
    'registration',

    'trust',
    'wanglibao_bank_financing',
    'wanglibao_fund',
    'wanglibao_profile',
    'wanglibao_rest',
    'wanglibao_portfolio',
    'wanglibao_preorder',
    'wanglibao_hotlist',
    'wanglibao_favorite',

    'provider',
    'provider.oauth2',

    'widget_tweaks',
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'wanglibao.urls'

WSGI_APPLICATION = 'wanglibao.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join('/tmp', 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'zh-cn'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'local')
)


# Authentication backend
AUTHENTICATION_BACKENDS = (
    'wanglibao.auth_backends.EmailPhoneUsernameAuthBackend',
)

# Template loader
TEMPLATE_LOADERS = (
    ('pyjade.ext.django.Loader',(
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

# Template pre processor
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.csrf",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'publish/static')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)


# Media files path
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

if DEBUG:
    MEDIA_URL = 'http://127.0.0.1:8000/media/'
else:
    MEDIA_URL = '/media/'
    raise ImproperlyConfigured("Need to configure the media path")

# The request rate for some apis
request_rate = '1/minute'

if DEBUG:
    request_rate = '1/second'

# Django Rest Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.UnicodeJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.JSONPRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
        'wanglibao.filters.OrderingFilter',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.OAuth2Authentication',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'user': request_rate
    },
    'DEFAULT_PAGINATION_SERIALIZER_CLASS': 'wanglibao_rest.pagination.PaginationSerializer',
}

# email SMTP configuration
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'postmaster@sandbox57322.mailgun.org'
EMAIL_HOST_PASSWORD = '83x1ln8w5p64'
DEFAULT_FROM_EMAIL = 'noreply@wanglibao.com'

# sms service configuration
SMS_ACCOUNT = 'cf_zkrx'
SMS_PASSWORD = 'S8o-mHH-fcc-x8g'
SMS_URL = 'http://121.199.16.178/webservice/sms.php?method=Submit'
