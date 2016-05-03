# encoding:utf-8

"""
Django settings for wanglibao project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

from __future__ import absolute_import

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import json
import djcelery
from celery.schedules import crontab
import djcelery

djcelery.setup_loader()


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CERT_DIR = os.path.join(BASE_DIR, "certificate")

try:
    with open(os.path.join(BASE_DIR, 'env.json'), 'r') as config_file:
        env = json.load(config_file)
except IOError, e:
    # For dev or other env without env.py, we just ignore it
    env = {}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'w#ris1&&#_-w4oj&!eka=9sn6ou#mqla=&_wqcb+m=90!a@1k8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True

# Whether the deploy in production
ENV_DEV = 'debug'
ENV_PRODUCTION = 'production'
ENV_PREPRODUCTION = 'pre'
ENV_STAGING = 'staging'

ENV = ENV_DEV
# ENV = ENV_STAGING

if ENV != ENV_DEV:
    DEBUG = False

ADMINS = (
    ('Li Li', 'lili@wanglibank.com'),
    ('Huang bo', 'huangbo@wanglibank.com')
)

ALLOWED_HOSTS = ['*']


from registration_defaults.settings import *

# Application definition
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'wanglibao',
    'registration_defaults',
    'suit',
    'django.contrib.admin',
    'django_extensions',
    'reversion',

    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'drf_wrapper',
    'import_export',

    'south',
    'registration',

    'common',
    'marketing',
    'wanglibao_account',
    'wanglibao_p2p',
    'wanglibao_profile',
    'wanglibao_rest',
    'wanglibao_pay',
    'wanglibao_margin',
    'wanglibao_oauth2',

    'widget_tweaks',
    'mathfilters',

    'raven.contrib.django.raven_compat',
    'djcelery',  # Use django orm as the backend
    'djsupervisor',
    'adminplus',
    'daterange_filter',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'concurrency.middleware.ConcurrencyMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'marketing.middlewares.PromotionTokenMiddleWare',
)


CONCURRENCY_POLICY = 2

ROOT_URLCONF = 'wanglibao.urls'

WSGI_APPLICATION = 'wanglibao.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': os.path.join(BASE_DIR, 'wanglibao/mysql.cnf'),
        }
    },
}

# The deploy file will overwrite this based on flag local db
LOCAL_MYSQL = ENV == ENV_DEV or ENV == ENV_STAGING

if LOCAL_MYSQL:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wanglibao_channel',
        'USER': 'wanglibao',
        'PASSWORD': 'wanglibank',
        # 'HOST': '192.168.20.237',
    }

import sys

if 'test' in sys.argv:
    SOUTH_TESTS_MIGRATE = False
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/db.sqlite3'
    }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'zh-cn'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'local')
)


# Authentication backend
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

import django.contrib.auth.backends

# Template pre processor
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.csrf",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
)


STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'publish/static')

# The request rate for some apis
request_rate = '2/minute'

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
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'user': request_rate
    },
    'DEFAULT_PAGINATION_SERIALIZER_CLASS': 'wanglibao_rest.pagination.PaginationSerializer',
}

# Default login redirect url
LOGIN_REDIRECT_URL = '/'


# Logger
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wanglibao/mysite.log',
            'formatter': 'verbose'
        },
        'marketing': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wanglibao/marketing.log',
            'formatter': 'verbose'
        },
        'wanglibao_account': {  #add by yihen@20151113
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wanglibao/wanglibao_account.log',
            'formatter': 'verbose'
        },
        'wanglibao_rest': {  #add by yihen@20151028
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wanglibao/wanglibao_rest.log',
            'formatter': 'verbose'
        },
        'wanglibao_cooperation': {  #add by yihen@20150915
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wanglibao/wanglibao_cooperation.log',
            'formatter': 'verbose'
        },
        'wanglibao_oauth2': {  #add by yihen@20151028
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wanglibao/wanglibao_oauth2.log',
            'formatter': 'verbose'
        },
        'wanglibao_p2p': {  # add by chenweibin@20160328
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wanglibao/wanglibao_p2p.log',
            'formatter': 'verbose'
        },
        'wanglibao_tasks': {  # add by chenweibin@20160328
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wanglibao/wanglibao_tasks.log',
            'formatter': 'verbose'
        },
        'common': {  # add by chenweibin@20160328
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wanglibao/common.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'propagate': True,
            'level': 'INFO',
        },
        'wanglibao': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
        'wanglibao_pay': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
        'wanglibao_p2p': {
            'handlers': ['wanglibao_p2p'],
            'level': 'DEBUG',
        },
        'wanglibao_account': {
            'handlers': ['wanglibao_account', 'console'],
            'level': 'DEBUG',
        },
        'wanglibao_margin': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'marketing': {
            'handlers': ['marketing', 'console'],
            'level': 'DEBUG'
        },
        'wanglibao_rest': {  # add by yihen@20151028
            'handlers': ['wanglibao_rest', 'console'],
            'level': 'INFO'
        },
        'wanglibao_cooperation': {  # add by yihen@20150915
            'handlers': ['wanglibao_cooperation', 'console'],
            'level': 'DEBUG'
        },
        'wanglibao_profile': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG'
        },
        'wanglibao_oauth2': {  # add by yihen@20151028
            'handlers': ['wanglibao_oauth2', 'console'],
            'level': 'DEBUG'
        },
        'wanglibao_tasks': {
            'handlers': ['wanglibao_tasks', 'console'],
            'level': 'DEBUG'
        },
        'common': {
            'handlers': ['common', 'console'],
            'level': 'DEBUG'
        },
    }
}


if ENV != ENV_DEV:
    LOGGING['loggers']['django']['level'] = 'INFO'

    # secure proxy SSL header and secure cookies
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # session expire at browser close
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True

    # wsgi scheme
    os.environ['wsgi.url_scheme'] = 'https'
    os.environ['HTTPS'] = 'on'

# rest api document swagger settings
SWAGGER_SETTINGS = {
    "exclude_namespaces": [],  # List URL namespaces to ignore
    "api_version": '1.0',  # Specify your API's version
    "enabled_methods": [  # Specify which methods to enable in Swagger UI
                          'get',
                          'post',
                          'put',
                          'patch',
                          'delete'
    ],
    "api_key": '',  # An API key
    "is_authenticated": False,  # Set to True to enforce user authentication,
    "is_superuser": False,  # Set to True to enforce admin only access
}


# Celery configuration

# Now since the rabbitmq installed in localhost, we use guest
if ENV == ENV_PRODUCTION:
    # FixMe,　修改正式环境broker
    BROKER_URL = env.get('BROKER_URL', 'amqp://guest:guest@localhost//')
elif ENV == ENV_STAGING:
    BROKER_URL = env.get('BROKER_URL', 'amqp://wanglibao:wanglibank@192.168.1.242:5672/wanglibao')
else:
    # FixMe,　修改测试环境broker　URL, 如果DEBUG is False, 需添加静态文件配置，否则后台管理页面无法加载
    # BROKER_URL = env.get('BROKER_URL', 'amqp://guest:guest@localhost//')
    BROKER_URL = env.get('BROKER_URL', 'amqp://wanglibao:wanglibank@192.168.1.242:5672/wanglibao')

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_DEFAULT_QUEUE = 'coop_celery'
CELERY_QUEUES = {
    # "celery": {"exchange": "celery", "routing_key": "celery"},
    "coop_celery": {"exchange": "coop_celery", "routing_key": "coop_celery"},
}

from datetime import timedelta

CELERYBEAT_SCHEDULE = {}

# CELERYBEAT_SCHEDULE_FILENAME = "/var/log/wanglibao/celerybeat-schedule"
CELERYBEAT_SCHEDULE_FILENAME = "/tmp/celerybeat-schedule"

USE_L10N = False
DATETIME_FORMAT = 'Y-m-d H:i:s'
# Modify by hb on 2015-11-25
ADMIN_ADDRESS = 'PK7wlbQ4Q9KPs9Io_zOpac'
DATE_FORMAT = 'Y-m-d'

SUIT_CONFIG = {
    'LIST_PER_PAGE': 100
}

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = 'wanglibank_redis'

# Chanel settings
BASE_SYNC_KEY = 'jIzNGRrd2xi'


PROMO_TOKEN_QUERY_STRING = 'promo_token'
PROMO_TOKEN_USER_KEY = 'tid'
CLIENT_ID_QUERY_STRING = 'app_id'

CHANNEL_CENTER_CALL_BACK_KEY = 'jIzNGRrd2xi'
if ENV == ENV_PRODUCTION:
    BASE_OAUTH_KEY = 'd2xiOXMwZA'
    CHANNEL_CENTER_CALL_BACK_URL = ''
else:
    BASE_OAUTH_KEY = 'd2xiOXMwZA'
    CHANNEL_CENTER_CALL_BACK_URL = ''


# 八金社渠道
BAJINSHE_COOP_ID = 'wanglibao'
BAJINSHE_COOP_KEY = '3795dd52-3ad9-47cf-9fe7-67d69566c1ba'
if ENV == ENV_PRODUCTION:
    BAJINSHE_ACCESS_TOKEN_URL = 'http://test.jr360.com/json/v1/external/TokenService/getAccessToken/gzip'
    BAJINSHE_PRODUCT_PUSH_URL = 'http://test.jr360.com/json/v1/external/ProductService/publishProduct/gzip'
    BAJINSHE_ACCOUNT_PUSH_URL = 'http://test.jr360.com/json/v1/external/AccountService/pushAccount/gzip'
    BAJINSHE_TRANSACTION_PUSH_URL = 'http://test.jr360.com/json/v1/external/BusinessLogService/pushBusinessLog/gzip'
    BAJINSHE_PURCHASE_PUSH_URL = ''
else:
    BAJINSHE_ACCESS_TOKEN_URL = 'http://test.jr360.com/json/v1/external/TokenService/getAccessToken/gzip'
    BAJINSHE_PRODUCT_PUSH_URL = 'http://test.jr360.com/json/v1/external/ProductService/publishProduct/gzip'
    BAJINSHE_ACCOUNT_PUSH_URL = 'http://test.jr360.com/json/v1/external/AccountService/pushAccount/gzip'
    BAJINSHE_TRANSACTION_PUSH_URL = 'http://test.jr360.com/json/v1/external/BusinessLogService/pushBusinessLog/gzip'
    BAJINSHE_PURCHASE_PUSH_URL = 'http://test.jr360.com/json/v1/external/InvestmentService/pushInvestment/gzip'


# 人人利渠道
WLB_FOR_RENRENLI_KEY = '2007'
RENRENLI_ACCOUNT_NAME = 'zlo_RrNuG'
RENRENLI_ACCOUNT_PWD = 'zlopwd_ZAQ5bzRa'
if ENV == ENV_PRODUCTION:
    RENRENLI_PURCHASE_PUSH_URL = 'http://openapi.amoydao.com/zlo/getp2pinfo/getsubscribe/'
else:
    RENRENLI_PURCHASE_PUSH_URL = 'http://openapi.amoydao.com/zlo/getp2pinfo/getsubscribe/'


# 比搜益
if ENV == ENV_PRODUCTION:
    BISOUYI_PCODE = '10002'
    BISOUYI_CLIENT_ID = 'BSY_WLB_Test_10002'
    BISOUYI_CLIENT_SECRET = 'TOKEN_A_Test_k0t8m'
    BISOUYI_AES_KEY = 'SECRET_WLB_aes66'
    BISOUYI_PRODUCT_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/product/basice'
    BISOUYI_PRODUCT_STATUS_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/product/status'
    BISOUYI_INTEREST_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/account/money'
    BISOUYI_PURCHASE_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/trading/purchase'
    BISOUYI_PURCHASE_STATUS_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/trading/purchaseStauts'
    BISOUYI_WITHDRAW_RECHARGE_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/trading/ransom'
    BISOUYI_WITHDRAW_STATUS_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/trading/ransomStatus'
    BISOUYI_BIND_CARD_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/account/opened'
    BISOUYI_OATUH_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/account/oauth'
    BISOUYI_ORDER_RELATION_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/trading/purchaseRelation'
    BISOUYI_ON_INTEREST_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/trading/purchaseIncome'
    BISOUYI_PURCHASE_REFUND_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/trading/purchaseRefund'
else:
    BISOUYI_PCODE = '10002'
    BISOUYI_CLIENT_ID = 'BSY_WLB_Test_10002'
    BISOUYI_CLIENT_SECRET = 'TOKEN_A_Test_k0t8m'
    BISOUYI_AES_KEY = 'SECRET_WLB_aes66'
    BISOUYI_PRODUCT_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/product/basice'
    BISOUYI_PRODUCT_STATUS_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/product/status'
    BISOUYI_INTEREST_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/account/money'
    BISOUYI_PURCHASE_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/trading/purchase'
    BISOUYI_PURCHASE_STATUS_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/trading/purchaseStauts'
    BISOUYI_WITHDRAW_RECHARGE_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/trading/ransom'
    BISOUYI_WITHDRAW_STATUS_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/trading/ransomStatus'
    BISOUYI_BIND_CARD_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/account/opened'
    BISOUYI_OATUH_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/account/oauth'
    BISOUYI_ORDER_RELATION_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/trading/purchaseRelation'
    BISOUYI_ON_INTEREST_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/trading/purchaseIncome'
    BISOUYI_PURCHASE_REFUND_PUSH_URL = 'http://180.168.75.226:60000/bsy-pop-web/openapi/p2p/trading/purchaseRefund'


if ENV == ENV_PRODUCTION:
    WLB_URL = 'https://www.wanglibao.com'
else:
    WLB_URL = 'https://staging.wanglibao.com'
