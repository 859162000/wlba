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
from celery.schedules import crontab
from Crypto.PublicKey import RSA

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

try:
    with open(os.path.join(BASE_DIR, 'env.json'), 'r') as config_file:
        env = json.load(config_file)
except IOError, e:
    # For dev or other env without env.py, we just ignore it
    env = {}

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')#@a(750mv)cn&#@c#^y%52-pof*w%)ba%w5kd1*u0k=l6znj9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True

# Whether the deploy in production
ENV_DEV = 'debug'
ENV_PRODUCTION = 'production'
ENV_PREPRODUCTION = 'pre'
ENV_STAGING = 'staging'

ENV = ENV_DEV

if ENV != ENV_DEV:
    DEBUG = False

ADMINS = (
    ('Shuo Li', 'lishuo@wanglibank.com'),
    ('Zhang Ding Liang', 'zhangdingliang@wanglibank.com')
)

ALLOWED_HOSTS = ['*']

from registration_defaults.settings import *

# Application definition
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
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

    'marketing',

    'trust',
    'wanglibao_account',
    'wanglibao_announcement',
    'wanglibao_sms',
    'wanglibao_bank_financing',
    'wanglibao_fund',
    'wanglibao_cash',
    'wanglibao_p2p',
    'wanglibao_profile',
    'wanglibao_rest',
    'wanglibao_portfolio',
    'wanglibao_preorder',
    'wanglibao_hotlist',
    'wanglibao_favorite',
    'wanglibao_robot',
    'shumi_backend',
    'wanglibao_page',
    'wanglibao_feedback',
    'wanglibao_buy',
    'wanglibao_banner',
    'wanglibao_fake',
    'wanglibao_pay',
    'order',
    'wanglibao_margin',
    'wanglibao_redpack',
    'wanglibao_help',
    'wanglibao_activity',
    'wanglibao_mobile',
    'weixin',

    'report',
    'misc',

    'provider',
    'provider.oauth2',

    'widget_tweaks',
    'mathfilters',
    #'test_without_migrations',

    'raven.contrib.django.raven_compat',
    'ckeditor',
    'captcha',
    'djcelery',  # Use django orm as the backend
    'djsupervisor',
    'adminplus',
    'file_storage'
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

#if LOCAL_MYSQL:
#    DATABASES['default'] = {
#        'ENGINE': 'django.db.backends.mysql',
#        'NAME': 'wanglibao',
#        'USER': 'wanglibao',
#        'PASSWORD': 'wanglibank',
#    }

import sys

if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/db.sqlite3'
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
    'wanglibao_account.auth_backends.EmailPhoneUsernameAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Template loader
TEMPLATE_LOADERS = (
    ('pyjade.ext.django.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'publish/static')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
    os.path.join('wanglibao_mobile/static'),
)


# Media files path
MEDIA_ROOT = '/var/media/wanglibao/'
MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'file_storage.storages.DatabaseStorage'

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

# email SMTP configuration
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'postmaster@sandbox57322.mailgun.org'
EMAIL_HOST_PASSWORD = '83x1ln8w5p64'
DEFAULT_FROM_EMAIL = 'noreply@wanglibao.com'

# ManDao sms service
SMS_MANDAO_URL = 'http://sdk.entinfo.cn:8061/mdgxsend.ashx'
SMS_MANDAO_MULTICAST_URL = 'http://sdk2.entinfo.cn:8061/mdsmssend.ashx'
SMS_MANDAO_SN = 'SDK-BBX-010-20599'
SMS_MANDAO_MD5_PWD = '4A4080BB5FCCC3422E14EA8247D1062C'

SMS_BACKEND = 'wanglibao_sms.backends.ManDaoSMSBackEnd'

SMS_EMAY_SN = "6SDK-EMY-6688-KEZSM"
SMS_EMAY_KEY = "wanglibao"
SMS_EMAY_PWD = "660687"
SMS_EMAY_URL = "http://sdk4report.eucp.b2m.cn:8080/sdk/SDKService?wsdl"

# Default login redirect url
LOGIN_REDIRECT_URL = '/'

#ckeditor setting
CKEDITOR_UPLOAD_PATH = "uploads/"

# Sentry maven client configuration
# Set your DSN value

#RAVEN_CONFIG = {
#    'dsn': 'https://efd164e25b604da7b2f38b88d0594ff5:4b1fb0cd10774161a51e33be79e88e84@app.getsentry.com/22349',
#}

#if ENV != ENV_PRODUCTION:
#    RAVEN_CONFIG = {}

import mimetypes

mimetypes.add_type("text/x-component", ".htc")

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
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wanglibao/mysite.log',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'wanglibao_sms': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'shumi': {
            'handlers': ['file'],
            'level': 'DEBUG'
        },
        'wanglibao_pay': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'wanglibao_activity': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'p2p': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'rest': {
            'handlers': ['file'],
            'level': 'DEBUG',
        }
    }
}

if ENV != ENV_DEV:
    LOGGING['loggers']['django']['level'] = 'INFO'
    LOGGING['loggers']['wanglibao_sms']['level'] = 'INFO'

    # secure proxy SSL header and secure cookies
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # session expire at browser close
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True

    # wsgi scheme
    os.environ['wsgi.url_scheme'] = 'https'

# starting shumi_backend config
SM_CONSUMER_KEY = 'SM_SDK_WLB'
SM_CONSUMER_SECRET = 'B9871687A8F3487E9370E78851F338CE'
SM_API_BASE_URL = 'https://trade.fund123.cn/openapi/get.json/'
SM_AUTO_LOGIN_URL = 'https://account.fund123.cn/oauth/Partner/AutoLogin.aspx?'
SM_REQUEST_TOKEN_URL = 'https://account.fund123.cn/oauth/request_token.ashx'
SM_AUTHORIZE_BASE_URL = 'https://account.fund123.cn/oauth/Partner/Authorize.aspx'
SM_ACCESS_TOKEN_URL = 'https://account.fund123.cn/oauth/access_token.ashx'
SM_PURCHASE_TEMPLATE = 'https://trade.fund123.cn/Trading/Do/Purchase?fundcode={fund_code}'
SM_REDEEM_TEMPLATE = 'https://trade.fund123.cn/Trading/Do/Redeem?tradeAccount={trade_account}' \
                     '&fundCode={fund_code}&sharetype={share_type}&UsableRemainShare={usable_remain_share}'
SM_MONETARY_FUND_NET_VALUE = 'http://funddata.smbserver.fund123.cn/' \
                             'monetary_fund_net_value?format=json&date={date}'
SM_FUND_DETAILS_API_BASE = 'http://funddata.smbserver.fund123.cn/'
SM_FUND_ALL = 'http://jrsj1.data.fund123.cn/ShumiData/FundNav.ashx?applyrecordno=10000&sort=C1'


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

# Captcha setting
CAPTCHA_IMAGE_BEFORE_FIELD = False

# Celery configuration

# Now since the rabbitmq installed in localhost, we use guest
BROKER_URL = env.get('BROKER_URL', 'amqp://guest:guest@localhost//')

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'

from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'p2p-watchdog-1-minutes': {
        'task': 'wanglibao_p2p.tasks.p2p_watchdog',
        'schedule': timedelta(minutes=1),
    },
    'report-generate': {
        'task': 'report.tasks.generate_report',
        'schedule': crontab(minute=0, hour=16),
    },
    'generate_site_data': {
        'task': 'marketing.tasks.generate_site_data',
        'schedule': crontab(minute=15, hour=16)
    },
    # 'post_product_cjdao': {
    #     'task': 'wanglibao_account.tasks.post_product_half_hour',
    #     'schedule': timedelta(minutes=30)
    # }
}

CELERYBEAT_SCHEDULE_FILENAME = "/var/log/wanglibao/celerybeat-schedule"

ID_VERIFY_USERNAME = 'wljr_admin'
ID_VERIFY_PASSWORD = 'wljr888'

if ENV == ENV_PRODUCTION:
    CALLBACK_HOST = 'https://www.wanglibao.com'
    MER_ID = '872724'
    CUSTOM_ID = '000007522683'
    SIGN_HOST = '10.171.17.243'
    #SIGN_HOST = '10.160.18.243'
    SIGN_PORT = 8733
    PAY_URL = 'https://mas.chinapnr.com'
    WITHDRAW_URL = 'https://lab.chinapnr.com/buser'

    YEE_PAY_URL = "https://ok.yeepay.com/paymobile/api/pay/request"
    YEE_MER_ID = "10012413099"
    YEE_MER_PRIV_KEY = RSA.importKey(open(os.path.join(BASE_DIR, 'yeepay_mer_pri_key.pem'), 'r').read())
    YEE_MER_PUB_KEY = RSA.importKey(open(os.path.join(BASE_DIR, 'yeepay_mer_pub_key.pem'), 'r').read())
    YEE_PUB_KEY = RSA.importKey(open(os.path.join(BASE_DIR, "yeepay_pub_key.pem"), "r").read())

    KUAI_PAY_URL = "https://mas.99bill.com:443/cnp/purchase"
    KUAI_QUERY_URL = "https://mas.99bill.com:443/cnp/pci_query"
    KUAI_DEL_URL = "https://mas.99bill.com:443/cnp/pci_del"
    KUAI_DYNNUM_URL = "https://mas.99bill.com:443/cnp/getDynNum"
    KUAI_PEM_PATH = os.path.join(BASE_DIR, "81231006011001390.pem")
    KUAI_MER_ID = "812310060110013"
    KUAI_MER_PASS = "vpos123"
    KUAI_TERM_ID = "00004559"

    YTX_API_URL = "https://app.cloopen.com:8883/2013-12-26"
    YTX_APPID = "8a48b55149896cfd0149adab1d9a1a93"
elif ENV == ENV_PREPRODUCTION:
    CALLBACK_HOST = 'https://pre.wanglibao.com'
    MER_ID = '872724'
    CUSTOM_ID = '000007522683'
    #SIGN_HOST = 'www.wanglibao.com'
    SIGN_HOST = '10.171.17.243'
    SIGN_PORT = 8733
    PAY_URL = 'https://mas.chinapnr.com'
    WITHDRAW_URL = 'https://lab.chinapnr.com/buser'

    YEE_PAY_URL = "https://ok.yeepay.com/paymobile/api/pay/request"
    YEE_MER_ID = "10012413099"
    YEE_MER_PRIV_KEY = RSA.importKey(open(os.path.join(BASE_DIR, 'yeepay_mer_pri_key.pem'), 'r').read())
    YEE_MER_PUB_KEY = RSA.importKey(open(os.path.join(BASE_DIR, 'yeepay_mer_pub_key.pem'), 'r').read())
    YEE_PUB_KEY = RSA.importKey(open(os.path.join(BASE_DIR, "yeepay_pub_key.pem"), "r").read())

    KUAI_PAY_URL = "https://mas.99bill.com:443/cnp/purchase"
    KUAI_QUERY_URL = "https://mas.99bill.com:443/cnp/pci_query"
    KUAI_DEL_URL = "https://mas.99bill.com:443/cnp/pci_del"
    KUAI_DYNNUM_URL = "https://mas.99bill.com:443/cnp/getDynNum"
    KUAI_PEM_PATH = os.path.join(BASE_DIR, "81231006011001390.pem")
    KUAI_MER_ID = "812310060110013"
    KUAI_MER_PASS = "vpos123"
    KUAI_TERM_ID = "00004559"

    YTX_API_URL = "https://app.cloopen.com:8883/2013-12-26"
    YTX_APPID = "8a48b55149896cfd0149adab1d9a1a93"
else:
    CALLBACK_HOST = 'https://staging.wanglibao.com'
    MER_ID = '510743'
    CUSTOM_ID = '000010124821'
    SIGN_HOST = '127.0.0.1'
    SIGN_PORT = 8733
    PAY_URL = 'http://test.chinapnr.com'
    WITHDRAW_URL = 'http://test.chinapnr.com/buser'

    YEE_PAY_URL = "http://mobiletest.yeepay.com/paymobile/api/pay/request"
    YEE_MER_ID = "YB01000000144"
    YEE_MER_PRIV_KEY = RSA.importKey(open(os.path.join(BASE_DIR, 'pkcs8_rsa_private_key144.pem'), 'r').read())
    YEE_PUB_KEY = RSA.importKey(open(os.path.join(BASE_DIR, "rsa_public_key144.pem"), "r").read())

    KUAI_PAY_URL = "https://sandbox.99bill.com:9445/cnp/purchase"
    KUAI_QUERY_URL = "https://sandbox.99bill.com:9445/cnp/pci_query"
    KUAI_DEL_URL = "https://sandbox.99bill.com:9445/cnp/pci_del"
    KUAI_DYNNUM_URL = "https://sandbox.99bill.com:9445/cnp/getDynNum"
    KUAI_PEM_PATH = os.path.join(BASE_DIR, "10411004511201290.pem")
    KUAI_MER_ID = "104110045112012"
    KUAI_MER_PASS = "vpos123"
    KUAI_TERM_ID = "00002012"

    YTX_API_URL = "https://sandboxapp.cloopen.com:8883/2013-12-26"
    YTX_APPID = "8a48b55149896cfd0149ac6a77e41962"

PAY_BACK_RETURN_URL = CALLBACK_HOST + '/pay/deposit/callback/'
PAY_RET_URL = CALLBACK_HOST + '/pay/deposit/complete/'
WITHDRAW_BACK_RETURN_URL = CALLBACK_HOST + '/pay/withdraw/callback/'

#易宝支付回调地址
YEE_PAY_RETURN_URL = CALLBACK_HOST + '/api/pay/yee/app/deposit/complete/'
YEE_PAY_BACK_RETURN_URL = CALLBACK_HOST + '/api/pay/yee/app/deposit/callback/'
#YEE_MER_SECRET_KEY = "418oFDp0384T5p236690c27Qp0893s8RZSG09VLy06A218ZCIi674V0h77M8"

#快钱回调地址
KUAI_PAY_RETURN_URL = CALLBACK_HOST + '/api/pay/deposit/complete/'
KUAI_PAY_BACK_RETURN_URL = CALLBACK_HOST + '/api/pay/deposit/callback/'

#语音验证码参数
YTX_SID = "aaf98f89495b3f3801497488ebbe0f3f"
YTX_TOKEN = "dbf6b3bf0d514c6fa21cd12d29930c18"
YTX_BACK_RETURN_URL = CALLBACK_HOST + "/api/ytx/voice_back/"

ID_VERIFY_BACKEND = 'wanglibao_account.backends.ProductionIDVerifyBackEnd'
if ENV == ENV_DEV:
    ID_VERIFY_BACKEND = 'wanglibao_account.backends.TestIDVerifyBackEnd'

PROMO_TOKEN_USER_SESSION_KEY = 'promo_token_user_id'
PROMO_TOKEN_QUERY_STRING = 'promo_token'

CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)
# CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
CAPTCHA_CHALLENGE_FUNCT = 'wanglibao.helpers.random_char_challenge'

DEBUG_TOOLBAR_PATCH_SETTINGS = False
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL': '/static/js/lib/jquery.min.js'
}

USE_L10N = False
DATETIME_FORMAT = 'Y-m-d H:i:s'
ADMIN_ADDRESS = 'AK7WtEQ4Q9KPs8Io_zOncw'
# DATE_FORMAT='Y-m-d'

# AUTH_PROFILE_MODULE = 'wanglibao_profile.WanglibaoUserProfile'
CKEDITOR_CONFIGS = {
    "default": {
        'toolbar_custom': [
            ['Source'], ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord'],
            ['Styles', 'Format', 'Font', 'FontSize'],
            ['-', 'Find', 'Replace', '-', 'SelectAll', 'RemoveFormat'],
            '/',
            ['Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['TextColor', 'BGColor'], ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Flash', 'Table', 'HorizontalRule'],
            ['Smiley', 'SpecialChar'],
        ],
        'toolbar': 'custom',
    }
}

ISCJDAO = False
CJDAOKEY = '1234'
RETURN_REGISTER = "http://test.cjdao.com/productbuy/reginfo"
RETURN_PURCHARSE_URL = "http://test.cjdao.com/productbuy/saveproduct"
POST_PRODUCT_URL = "http://test.cjdao.com/p2p/saveproduct"

RETURN_TINMANG_UTL = "http://www.bangwoya.com/callback/callback.php"
RETURN_TINMANG_UTL_DEBUG = "http://demo.bangwoya.com/callback/callback.php"
TINMANGKEY= '456'

SUIT_CONFIG = {
    'LIST_PER_PAGE': 100
}
