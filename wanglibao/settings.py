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
CERT_DIR = os.path.join(BASE_DIR, "certificate")

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
    'wanglibao_app',
    'wanglibao_anti', #add by yihen@20150813, anti module added
    'wanglibao_reward', #add by yihen@20150910
    'wanglibao_qiye', #add by wangxiaoqing
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
    'file_storage',
    'wanglibao_lottery',
    'daterange_filter',
    'experience_gold',
    'wanglibao_qiye',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'concurrency.middleware.ConcurrencyMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'wanglibao_app.middlewares.DisableAppCsrfCheck',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'marketing.middlewares.PromotionTokenMiddleWare',
    'marketing.middlewares.StatsKeyWordMiddleWare',
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
        'NAME': 'wanglibao',
        'USER': 'wanglibao',
        'PASSWORD': 'wanglibank',
        # 'HOST': '192.168.1.242',
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

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'local')
)

# Authentication backend
AUTHENTICATION_BACKENDS = (
    'wanglibao_account.auth_backends.EmailPhoneUsernameAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
    'wanglibao_account.auth_backends.TokenSecretSignAuthBackend',
    'weixin.auth_backend.OpenidAuthBackend',
)
import django.contrib.auth.backends

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
    "wanglibao.helpers.global_set",
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
# DEFAULT_FILE_STORAGE = 'file_storage.storages.DatabaseStorage'
DEFAULT_FILE_STORAGE = 'file_storage.storages.AliOSSStorage'


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
# 旧的漫道请求设置
# SMS_MANDAO_URL = 'http://sdk.entinfo.cn:8061/mdgxsend.ashx'
# SMS_MANDAO_MULTICAST_URL = 'http://sdk2.entinfo.cn:8061/mdsmssend.ashx'
# SMS_MANDAO_SN = 'SDK-BBX-010-20599'
# SMS_MANDAO_MD5_PWD = '4A4080BB5FCCC3422E14EA8247D1062C'

# 新的漫道请求设置
SMS_MANDAO_URL = 'http://sdk.entinfo.cn:8061/webservice.asmx/mdsmssend'
SMS_MANDAO_MULTICAST_URL = 'http://sdk2.entinfo.cn:8061/webservice.asmx/mdgxsend'

SMS_MANDAO_SN_MARKETING = 'SDK-SKY-010-02839'  # 营销类短信SDK
SMS_MANDAO_MD5_PWD_MARKETING = '1FE15236BBEB705A8F5D221F47164693'  # 营销类短信pwd

SMS_MANDAO_SN = 'SDK-SKY-010-02932'  # 应用类短信SDK
SMS_MANDAO_MD5_PWD = 'E9E12F71CE9A9E98B459CBF4BDD13315'  # 应用类短信pwd

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
        },
        'wanglibao_anti': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wanglibao/anti.log',
            'formatter': 'verbose'
        },
        'marketing': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wanglibao/marketing.log',
            'formatter': 'verbose'
        },
        'wanglibao_reward': {  #add by yihen@20150915
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wanglibao/wanglibao_reward.log',
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
        'weixin': {  #add by huomeimei
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wanglibao/weixin.log',
            'formatter': 'verbose'
        },
        'experience_gold': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wanglibao/experience_gold.log',
            'formatter': 'verbose'
        },
        'wanglibao_sms': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wanglibao/wanglibao_sms.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'wanglibao_sms': {
            'handlers': ['wanglibao_sms', 'console'],
            'level': 'DEBUG',
        },
        'shumi': {
            'handlers': ['file'],
            'level': 'DEBUG'
        },
        'wanglibao': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
        'wanglibao_pay': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
        'wanglibao_activity': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'wanglibao_p2p': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
        'wanglibao_redpack': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'rest': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'wanglibao_account': {
            'handlers': ['wanglibao_account', 'console'],
            'level': 'DEBUG',
        },
        'wanglibao_app': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'wanglibao_margin': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'wanglibao_lottery': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG'
        },
        'wanglibao_anti': {
            'handlers': ['wanglibao_anti', 'console'],
            'level': 'DEBUG'
        },
        'marketing': {
            'handlers': ['marketing', 'console'],
            'level': 'DEBUG'
        },
        'wanglibao_reward': {  # add by yihen@20150915
            'handlers': ['wanglibao_reward', 'console'],
            'level': 'DEBUG'
        },
        'wanglibao_rest': {  # add by yihen@20151028
              'handlers': ['wanglibao_rest', 'console'],
              'level': 'DEBUG'
          },
        'wanglibao_cooperation': {  # add by yihen@20150915
            'handlers': ['wanglibao_cooperation', 'console'],
            'level': 'DEBUG'
        },
        'weixin': {  # add by huomeimei
              'handlers': ['weixin', 'console'],
              'level': 'DEBUG'
        },
        'experience_gold': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG'
        },
        'wanglibao_profile': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG'
        },
    }
}


if ENV != ENV_DEV:
    LOGGING['loggers']['django']['level'] = 'INFO'
    LOGGING['loggers']['wanglibao_sms']['level'] = 'INFO'
    LOGGING['loggers']['wanglibao_lottery']['level'] = 'INFO'
    LOGGING['loggers']['wanglibao_pay']['level'] = 'INFO'

    # secure proxy SSL header and secure cookies
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # session expire at browser close
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True

    # wsgi scheme
    os.environ['wsgi.url_scheme'] = 'https'
    os.environ['HTTPS'] = 'on'

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

CELERY_QUEUES = {
                "celery":  {"exchange": "celery",
                              "routing_key": "celery"},
                "celery01": {"exchange": "celery01",
                              "routing_key": "celery01"},
                "celery02": {"exchange": "celery02",
                              "routing_key": "celery02"},
                }

from datetime import timedelta, datetime

CELERYBEAT_SCHEDULE = {
    'p2p-watchdog-1-minutes': {
        'task': 'wanglibao_p2p.tasks.p2p_watchdog',
        'schedule': timedelta(minutes=5),
    },
    # 'report-generate': {
    #     'task': 'report.tasks.generate_report',
    #     'schedule': crontab(minute=0, hour=16),
    # },
    'generate_site_data': {
        'task': 'marketing.tasks.generate_site_data',
        'schedule': crontab(minute=15, hour=4)
    },
    # 'post_product_cjdao': {
    #     'task': 'wanglibao_account.tasks.post_product_half_hour',
    #     'schedule': timedelta(minutes=30)
    # }

    'p2p_auto_ready_for_settle': {
        'task': 'wanglibao_p2p.tasks.p2p_auto_ready_for_settle',
        'schedule': crontab(minute=0, hour=16),
    },

    #add by guoya: 希财网渠道数据定时推送
    'xicai_send_data': {
        'task': 'wanglibao_account.tasks.xicai_send_data_task',
        'schedule': timedelta(hours=1),
    },

    #add by zhanghe: PC端WEB首页统计数据
    'pc_index_data': {
        'task': 'marketing.tasks.generate_pc_index_data',
        'schedule': crontab(minute=10, hour=0),
    },

    #add by lili: 全民佣金收入短信/站内信每日定时发送
    'all_invite_earning_data': {
        'task': 'marketing.tools.send_income_message_sms',
        'schedule': crontab(minute=0, hour=20)
    },
    #add by Guoya: 彩票PC版每天五点重置之前未中奖的用户
    'lottery_set_status': {
        'task': 'wanglibao_lottery.tasks.lottery_set_status',
        'schedule': crontab(minute=0, hour=5)
    },

    #add by Yihen@20150913，定时任务，3分钟给特定渠道返积分或发红包
    'handle_delay_time_data': {
        'task': 'wanglibao_anti.tasks.handle_delay_time_data',
        'schedule': timedelta(minutes=3)
    },

    # by Zhoudong 菜苗上报平台信息.
    'caimiao_platform_post': {
        'task': 'wanglibao_account.tasks.caimiao_platform_post_task',
        'schedule': crontab(minute=0, hour=0, day_of_month=1)
    },
    # by Zhoudong 菜苗上报标的信息.
    'caimiao_p2p_post': {
        'task': 'wanglibao_account.tasks.caimiao_p2p_info_post_task',
        'schedule': crontab(minute=0, hour=0)
    },
    # by Zhoudong 菜苗上报成交量.
    'caimiao_volumes_post': {
        'task': 'wanglibao_account.tasks.caimiao_volumes_info_post_task',
        'schedule': crontab(minute=0, hour=0)
    },
    # by Zhoudong 菜苗上报网贷评级.
    'caimiao_rating_post': {
        'task': 'wanglibao_account.tasks.caimiao_rating_info_post_task',
        'schedule': crontab(minute=0, hour=0)
    },
    #add by Huomeimei  每日更新虚拟全民淘金账号数据
    'update_virtual_earning': {
        'task': 'wanglibao_redpack.tasks.update_virtual_earning',
        'schedule': crontab(minute=0, hour=0)
    },
    # by Zhoudong 中金标的推送(包含新标, 更新, 下架)
    'zhongjin_send_data': {
        'task': 'wanglibao_account.tasks.zhongjin_post_task',
        'schedule': timedelta(hours=1),
    },
    # by Zhoudong 融途网标的推送(包含新标, 更新, 下架)
    'rongtu_send_data': {
        'task': 'wanglibao_account.tasks.rongtu_post_task',
        'schedule': timedelta(hours=1),
    },
    # 每天定时检测和生成原始邀请码
    'check_and_generate_codes': {
        'task': 'marketing.tools.check_and_generate_codes',
        'schedule': crontab(minute=0, hour=3)
    },

    # by Zhoudong 定期检查没有投资的新用户, 提醒投资
    'invested_status_task_check': {
        'task': 'marketing.tools.check_invested_status',
        'schedule': crontab(minute=0, hour=10),
    },
    # 每天下午17点半开始处理体验金的还款
    'experience_repayment_plan': {
        'task': 'experience_gold.tasks.experience_repayment_plan',
        'schedule': crontab(minute=0, hour=17),
    },
    # 定期检查还有3天到期的用户优惠券,发送提醒
    'redpack_status_task_check': {
        'task': 'marketing.tools.check_unavailable_3_days',
        'schedule': crontab(minute=0, hour=11),
    },
}

# CELERYBEAT_SCHEDULE_FILENAME = "/var/log/wanglibao/celerybeat-schedule"
CELERYBEAT_SCHEDULE_FILENAME = "/tmp/celerybeat-schedule"


ID_VERIFY_USERNAME = 'wljr_admin'
ID_VERIFY_PASSWORD = 'wljr888'
ID_LICENSE = '6a?zT-`f>_&lt;iDCC5V3[73#V?7$$t(a/p8w+u?o?[1(cf+T9&amp;7)3#I64)8n&amp;bJf`1Aa?o?z?x9V)qYq^eMgPqXw[.Tk.j?vLtNoa3KtGgYeb3Mc?x?v`0a8A.Fc-;&lt;a:c?/:a?/?v?j^qSuSyJg?x6abLLbFhM/3f:c?.2x?h?h?v.xOwMnGgSe?x.laLQtSyc6$y[:0#TH6QV\H3dh@9-u4b?.&lt;f?/+e?jS/JcRuAn)e?vY/Cc@;[.aMImHyFc$yKn+y?g?g&lt;f?g>c%a[sCcbX_ddVMcZ.a4?x?vRuKu0[=v=x?jEjJtZ[QvDfXw]uYw2d?v`V`4YscNJvTeUjBsBdKfCd?x-kXpcBHx]t?x?g4b)j>d&lt;z?jN.YgSyUk?x3h6t]gRe^dXgFhTeWlYjXwHgCd?x*w?jd7^eMgV;Ty]gc5?x'

if ENV == ENV_PRODUCTION:
    CALLBACK_HOST = 'https://www.wanglibao.com'
    STATIC_FILE_HOST = 'https://img.wanglibao.com'
    MER_ID = '872724'
    CUSTOM_ID = '000007522683'
    SIGN_HOST = '10.171.17.243'
    #SIGN_HOST = '10.160.18.243'
    SIGN_PORT = 8733

    HUI_SHORT_MER_ID = "510793"
    HUI_SHORT_SIGN_HOST = SIGN_HOST
    HUI_SHORT_SIGN_PORT = 8734
    HUI_SHORT_OPER_ID = "bjwl"
    HUI_SHORT_LOGIN_PWD = "cathy123"
    PAY_URL = 'https://mas.chinapnr.com'
    HUI_SHORT_BIND_URL = "%s/gao/entry.do" % PAY_URL
    HUI_SHORT_DEBIND_URL = "%s/gao/entry.do" % PAY_URL
    HUI_SHORT_PAY_URL = "%s/gar/entry.do" % PAY_URL
    WITHDRAW_URL = 'https://lab.chinapnr.com/buser'

    YEE_PROXY_PAY_MER_ID = '10012413099'
    YEE_PROXY_PAY_KEY = '418oFDp0384T5p236690c27Qp0893s8RZSG09VLy06A218ZCIi674V0h77M8'

    YEE_PAY_URL = "https://ok.yeepay.com/paymobile/api/pay/request"
    YEE_MER_ID = "10012413099"
    YEE_MER_PRIV_KEY = RSA.importKey(open(os.path.join(CERT_DIR, 'yeepay_mer_pri_key.pem'), 'r').read())
    YEE_MER_PUB_KEY = RSA.importKey(open(os.path.join(CERT_DIR, 'yeepay_mer_pub_key.pem'), 'r').read())
    YEE_PUB_KEY = RSA.importKey(open(os.path.join(CERT_DIR, "yeepay_pub_key.pem"), "r").read())

    YEE_URL = 'https://ok.yeepay.com/payapi'
    YEE_SHORT_BIND = '%s/api/tzt/invokebindbankcard' % YEE_URL
    YEE_SHORT_BIND_CHECK_SMS = '%s/api/tzt/confirmbindbankcard' % YEE_URL
    YEE_SHORT_BIND_CARD_QUERY = '%s/api/bankcard/bind/list' % YEE_URL
    YEE_SHORT_BIND_PAY_REQUEST = '%s/api/tzt/directbindpay' % YEE_URL
    YEE_SHORT_CALLBACK = '%s/api/pay/cnp/yee/callback/' % CALLBACK_HOST

    KUAI_PAY_URL = "https://mas.99bill.com:443/"

    #KUAI_PAY_URL = "https://mas.99bill.com:443/cnp/purchase"
    #KUAI_QUERY_URL = "https://mas.99bill.com:443/cnp/pci_query"
    #KUAI_DEL_URL = "https://mas.99bill.com:443/cnp/pci_del"
    #KUAI_DYNNUM_URL = "https://mas.99bill.com:443/cnp/getDynNum"

    KUAI_PEM_PATH = os.path.join(CERT_DIR, "81231006011001390.pem")
    KUAI_SIGNATURE_PEM_PATH = os.path.join(CERT_DIR, "kuai_pay_signature.pem")
    KUAI_MER_ID = "812310060110013"
    KUAI_MER_PASS = "vpos123"
    KUAI_TERM_ID = "00004559"

    YTX_API_URL = "https://app.cloopen.com:8883/2013-12-26"
    YTX_APPID = "8a48b55149896cfd0149adab1d9a1a93"
elif ENV == ENV_PREPRODUCTION:
    CALLBACK_HOST = 'https://pre.wanglibao.com'
    STATIC_FILE_HOST = 'https://img.wanglibao.com'
    MER_ID = '872724'
    CUSTOM_ID = '000007522683'
    #SIGN_HOST = 'www.wanglibao.com'
    SIGN_HOST = '10.171.17.243'
    SIGN_PORT = 8733

    HUI_SHORT_MER_ID = "510793"
    HUI_SHORT_SIGN_HOST = SIGN_HOST
    HUI_SHORT_SIGN_PORT = 8734
    HUI_SHORT_OPER_ID = "bjwl"
    HUI_SHORT_LOGIN_PWD = "cathy123"
    PAY_URL = 'https://mas.chinapnr.com'
    HUI_SHORT_BIND_URL = "%s/gao/entry.do" % PAY_URL
    HUI_SHORT_DEBIND_URL = "%s/gao/entry.do" % PAY_URL
    HUI_SHORT_PAY_URL = "%s/gar/entry.do" % PAY_URL
    WITHDRAW_URL = 'https://lab.chinapnr.com/buser'

    YEE_PROXY_PAY_MER_ID = '10012413099'
    YEE_PROXY_PAY_KEY = '418oFDp0384T5p236690c27Qp0893s8RZSG09VLy06A218ZCIi674V0h77M8'

    YEE_PAY_URL = "https://ok.yeepay.com/paymobile/api/pay/request"
    YEE_MER_ID = "10012413099"
    YEE_MER_PRIV_KEY = RSA.importKey(open(os.path.join(CERT_DIR, 'yeepay_mer_pri_key.pem'), 'r').read())
    YEE_MER_PUB_KEY = RSA.importKey(open(os.path.join(CERT_DIR, 'yeepay_mer_pub_key.pem'), 'r').read())
    YEE_PUB_KEY = RSA.importKey(open(os.path.join(CERT_DIR, "yeepay_pub_key.pem"), "r").read())

    YEE_URL = 'https://ok.yeepay.com/payapi'
    YEE_SHORT_BIND = '%s/api/tzt/invokebindbankcard' % YEE_URL
    YEE_SHORT_BIND_CHECK_SMS = '%s/api/tzt/confirmbindbankcard' % YEE_URL
    YEE_SHORT_BIND_CARD_QUERY = '%s/api/bankcard/bind/list' % YEE_URL
    YEE_SHORT_BIND_PAY_REQUEST = '%s/api/tzt/directbindpay' % YEE_URL
    YEE_SHORT_CALLBACK = '%s/api/pay/cnp/yee/callback/' % CALLBACK_HOST

    KUAI_PAY_URL = "https://mas.99bill.com:443/"

    #KUAI_PAY_URL = "https://mas.99bill.com:443/cnp/purchase"
    #KUAI_QUERY_URL = "https://mas.99bill.com:443/cnp/pci_query"
    #KUAI_DEL_URL = "https://mas.99bill.com:443/cnp/pci_del"
    #KUAI_DYNNUM_URL = "https://mas.99bill.com:443/cnp/getDynNum"

    KUAI_PEM_PATH = os.path.join(CERT_DIR, "81231006011001390.pem")
    KUAI_SIGNATURE_PEM_PATH = os.path.join(CERT_DIR, "kuai_pay_signature.pem")
    KUAI_MER_ID = "812310060110013"
    KUAI_MER_PASS = "vpos123"
    KUAI_TERM_ID = "00004559"

    YTX_API_URL = "https://app.cloopen.com:8883/2013-12-26"
    YTX_APPID = "8a48b55149896cfd0149adab1d9a1a93"
else:
    CALLBACK_HOST = 'https://staging.wanglibao.com'
    STATIC_FILE_HOST = 'https://staging.wanglibao.com'
    # MER_ID = '510743'
    # CUSTOM_ID = '000010124821'
    # huifu id 改为和生产相同
    MER_ID = '872724'
    CUSTOM_ID = '000007522683'
    SIGN_HOST = '127.0.0.1'
    SIGN_PORT = 8733
    HUI_SHORT_MER_ID = "510793"
    HUI_SHORT_SIGN_HOST = SIGN_HOST
    HUI_SHORT_SIGN_PORT = 8734
    HUI_SHORT_OPER_ID = "bjwl"
    HUI_SHORT_LOGIN_PWD = "cathy123"
    # PAY_URL = 'http://test.chinapnr.com'
    # huifu pay url改为和生产相同
    PAY_URL = 'https://mas.chinapnr.com'
    HUI_SHORT_BIND_URL = "%s/gar/entry.do" % PAY_URL
    HUI_SHORT_DEBIND_URL = "%s/gar/entry.do" % PAY_URL
    HUI_SHORT_PAY_URL = "%s/gar/entry.do" % PAY_URL
    WITHDRAW_URL = 'http://test.chinapnr.com/buser'

    YEE_PROXY_PAY_MER_ID = '10001126856'
    YEE_PROXY_PAY_KEY = '69cl522AV6q613Ii4W6u8K6XuW8vM1N6bFgyv769220IuYe9u37N4y7rI4Pl'
    YEE_PAY_URL = "http://mobiletest.yeepay.com/paymobile/api/pay/request"
    YEE_MER_ID = "10000419568"
    YEE_MER_PRIV_KEY = RSA.importKey(open(os.path.join(CERT_DIR, 'staging_yee_mer_priv_key.pem'), 'r').read())
    YEE_PUB_KEY = RSA.importKey(open(os.path.join(CERT_DIR, "staging_yee_public_key.pem"), "r").read())

    YEE_URL = 'https://ok.yeepay.com/payapi'
    YEE_SHORT_BIND = '%s/api/tzt/invokebindbankcard' % YEE_URL
    YEE_SHORT_BIND_CHECK_SMS = '%s/api/tzt/confirmbindbankcard' % YEE_URL
    YEE_SHORT_BIND_CARD_QUERY = '%s/api/bankcard/bind/list' % YEE_URL
    YEE_SHORT_BIND_PAY_REQUEST = '%s/api/tzt/directbindpay' % YEE_URL
    YEE_SHORT_CALLBACK = '%s/api/pay/cnp/yee/callback/' % CALLBACK_HOST

    KUAI_PAY_URL = "https://sandbox.99bill.com:9445"

    #KUAI_PAY_URL = "https://sandbox.99bill.com:9445/cnp/purchase"
    #KUAI_QUERY_URL = "https://sandbox.99bill.com:9445/cnp/pci_query"
    #KUAI_DEL_URL = "https://sandbox.99bill.com:9445/cnp/pci_del"
    #KUAI_DYNNUM_URL = "https://sandbox.99bill.com:9445/cnp/getDynNum"

    KUAI_PEM_PATH = os.path.join(CERT_DIR, "10411004511201290.pem")
    KUAI_SIGNATURE_PEM_PATH = os.path.join(CERT_DIR, "kuai_pay_signature.pem")
    KUAI_MER_ID = "104110045112012"
    KUAI_MER_PASS = "vpos123"
    KUAI_TERM_ID = "00002012"

    YTX_API_URL = "https://sandboxapp.cloopen.com:8883/2013-12-26"
    YTX_APPID = "8a48b55149896cfd0149ac6a77e41962"

PAY_BACK_RETURN_URL = CALLBACK_HOST + '/pay/deposit/callback/'
PAY_RET_URL = CALLBACK_HOST + '/pay/deposit/complete/'
WITHDRAW_BACK_RETURN_URL = CALLBACK_HOST + '/pay/withdraw/callback/'

#易宝网银支付
YEE_PROXY_PAY_URL = 'https://www.yeepay.com/app-merchant-proxy/node'
YEE_PROXY_PAY_WEB_CALLBACK_URL = CALLBACK_HOST + '/pay/deposit/yee_proxy_pay_complete/'


#易宝支付回调地址
YEE_PAY_RETURN_URL = CALLBACK_HOST + '/api/pay/yee/app/deposit/complete/'
YEE_PAY_BACK_RETURN_URL = CALLBACK_HOST + '/api/pay/yee/app/deposit/callback/'
#YEE_MER_SECRET_KEY = "418oFDp0384T5p236690c27Qp0893s8RZSG09VLy06A218ZCIi674V0h77M8"

#快钱回调地址
KUAI_PAY_RETURN_URL = CALLBACK_HOST + '/api/pay/deposit/complete/'
KUAI_PAY_BACK_RETURN_URL = CALLBACK_HOST + '/api/pay/deposit/callback/'
KUAI_PAY_TR3_SIGNATURE = ''

#语音验证码参数
YTX_SID = "aaf98f89495b3f3801497488ebbe0f3f"
YTX_TOKEN = "dbf6b3bf0d514c6fa21cd12d29930c18"
YTX_BACK_RETURN_URL = CALLBACK_HOST + "/api/ytx/voice_back/"

# 汇讯群呼语音验证码(快易通)
VOICE_HX_URL = 'http://i.huixun35.com/sdk/SMS'
VOICE_HX_UID = '52361'
VOICE_HX_PWD = 'e10adc3949ba59abbe56e057f20f883e'

# Modify by hb on 2015-11-25 for new id-verify-channel
#ID_VERIFY_BACKEND = 'wanglibao_account.backends.ProductionIDVerifyBackEnd'
ID_VERIFY_BACKEND = 'wanglibao_account.backends.ProductionIDVerifyV2BackEnd'
if ENV == ENV_DEV:
    ID_VERIFY_BACKEND = 'wanglibao_account.backends.TestIDVerifyBackEnd'
    # Modify by hb on 2015-12-02
    #STATIC_FILE_HOST = 'http://localhost:8000'
    STATIC_FILE_HOST = ''

PROMO_TOKEN_USER_SESSION_KEY = 'promo_token_user_id'
PROMO_TOKEN_QUERY_STRING = 'promo_token'
PROMO_TOKEN_USER_KEY = 'tid'

CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
# CAPTCHA_CHALLENGE_FUNCT = 'wanglibao.helpers.random_char_challenge'
CAPTCHA_LETTER_ROTATION = (-20, 20)

DEBUG_TOOLBAR_PATCH_SETTINGS = False
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL': '/static/js/lib/jquery.min.js'
}

USE_L10N = False
DATETIME_FORMAT = 'Y-m-d H:i:s'
# Modify by hb on 2015-11-25
#ADMIN_ADDRESS = 'AK7WtEQ4Q9KPs8Io_zOncw'
ADMIN_ADDRESS = 'PK7wlbQ4Q9KPs9Io_zOpac'
DATE_FORMAT = 'Y-m-d'

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
    },
    "mini":{
        'entities':False,
        'toolbar': [
                {'items': ['Source']},
            ]
    }
}

#aliyun oss
#ACCESS_KEY_ID = 'ONOxmm1lwPLUyJ6U'
#ACCESS_KEY = 'ainfVHfl2VnnaxlaG7SL9pYPwA6oJU'
ACCESS_KEY_ID = '9o58bkzjBVRXjUFg'
ACCESS_KEY = 'nwogz9MF5VjadUSsuDzDM0lKlTN4BN'
if ENV == ENV_PRODUCTION:
    OSS_ENDPOINT = 'oss-cn-beijing-internal.aliyuncs.com'
    OSS_BUCKET = 'wanglifile'

else:
    OSS_ENDPOINT = 'oss-cn-beijing.aliyuncs.com'
    OSS_BUCKET = 'wanglistaging'

#ISCJDAO = False
#CJDAOKEY = '1234'
#RETURN_REGISTER = "http://test.cjdao.com/productbuy/reginfo"
#RETURN_PURCHARSE_URL = "http://test.cjdao.com/productbuy/saveproduct"
#POST_PRODUCT_URL = "http://test.cjdao.com/p2p/saveproduct"

# 天芒
if ENV == ENV_PRODUCTION:
    TIANMANG_CALL_BACK_URL = "http://www.bangwoya.com/callback/callback.php"
else:
    TIANMANG_CALL_BACK_URL = "http://demo.bangwoya.com/callback/callback.php"
TINMANG_KEY= '30000065'
WLB_FOR_TIANMANG_KEY = '1988'

# 易瑞特
if ENV == ENV_PRODUCTION:
    #我们提供给第三方的加密秘钥
    WLB_FOR_YIRUITE_KEY = '1989'
    #第三方提供给我们的加密秘钥
    YIRUITE_KEY = "esn4s2enki"
    YIRUITE_CALL_BACK_URL = "http://app.offer99.com/callback/callback_adv/callback_adv_w345fe267d9149fcd3dabc7e9e39b783.php"
else:
    WLB_FOR_YIRUITE_KEY = '1989'
    YIRUITE_KEY = "al9e4ys5"
    YIRUITE_CALL_BACK_URL = "http://app.offer99.com/callback/callback_test.php"

# 蹦蹦网
if ENV == ENV_PRODUCTION:
    #蹦蹦网提供的本次合作ID
    BENGBENG_COOP_ID = '7539'
    WLB_FOR_BENGBENG_KEY = '1990'
    BENGBENG_KEY = "af0ee5f72c55cdd6"
    BENGBENG_CALL_BACK_URL = "http://www.bengbeng.com/reannal.php"
else:
    BENGBENG_COOP_ID = '10'
    WLB_FOR_BENGBENG_KEY = '1990'
    BENGBENG_KEY = "080cd5f1b5c179c2"
    BENGBENG_CALL_BACK_URL = "http://www.bengbeng.com/retaste.php"

# 聚享游
WLB_FOR_JUXIANGYOU_KEY = '1991'
if ENV == ENV_PRODUCTION:
    JUXIANGYOU_COOP_ID = '112'
    JUXIANGYOU_KEY = '1c12f445d038dd0f'
    JUXIANGYOU_CALL_BACK_URL = 'http://api.juxiangyou.com/web/p2pApi.php'
else:
    JUXIANGYOU_COOP_ID = '10'
    JUXIANGYOU_KEY = 'b0cj391b90p421n8'
    JUXIANGYOU_CALL_BACK_URL = 'http://api.juxiangyou.com/web/p2pApi_test.php'

#都玩
WLB_FOR_DOUWANWANG_KEY = '1992'
DOUWANWANG_CALL_BACK_URL = 'http://mall.366dw.com/interface/reflection'

#西财
XICAI_TOKEN_URL = 'http://api.csai.cn/oauth2/access_token2'
XICAI_CREATE_P2P_URL = 'http://api.csai.cn/api/create_p2p'
XICAI_UPDATE_P2P_URL = 'http://api.csai.cn/api/update_p2p'
XICAI_CLIENT_ID = '48e37e2cf4124c2c9f5bde3cc88d011c'
XICAI_CLIENT_SECRET = '2e3dd17e800d48bca50e61b19f8fc11d'
XICAI_LOAD_PAGE = 'https://www.wanglibao.com/p2p/detail/{p2p_id}/?promo_token=xicai'
WLB_FOR_CSAI_KEY = '1993'
XICAI_UPDATE_TIMEDELTA = timedelta(hours=1)
if ENV == ENV_PRODUCTION:
    XICAI_LOAD_PAGE = 'https://www.wanglibao.com/p2p/detail/{p2p_id}/?promo_token=xicai'
else:
    XICAI_LOAD_PAGE = 'https://staging.wanglibao.com/p2p/detail/{p2p_id}/?promo_token=xicai'

# 菜苗
CAIMIAO_SECRET = 'a400f466c02ddfde984f631c66b36c6489e07d55615d07da0d9dd4a6f7bdb888'
CAIMIAO_PlatformBasic_URL = 'http://121.40.31.143:86/api/JsonsFinancial/PlatformBasic/'
CAIMIAO_ProdMain_URL = 'http://121.40.31.143:86/api/JsonsFinancial/ProdMain/'
CAIMIAO_Volumes_URL = 'http://121.40.31.143:86/api/JsonsFinancial/Volumes/'
CAIMIAO_RATING_URL = 'http://121.40.31.143:86/api/JsonsFinancial/Rating/'

# 众牛
ZHONGNIU_SECRET = 'N9ecZSqh'

# 中金
ZHONGJIN_ID = 15
ZHONGJIN_TEST_ID = 34
ZHONGJIN_P2P_URL = 'http://open.rong.cnfol.com/product.html'
ZHONGJIN_P2P_TEST_URL = 'http://test.open.finance.cnfol.com/product.html'    # 未确定
ZHONGJIN_SECRET = '2CF7AC2A27CC9B48C4EFCD7E356CD95F'
ZHONGJIN_TEST_SECRET = '348BB1C9A2032B2DA855D082151E8B8E'
ZHONGJIN_UPDATE_TIMEDELTA = timedelta(hours=1)

# 01财经
ZO_SECRET = '3r2o3j3m3g3q3l2o7o'

# 米贷网
MIDAI_USERNAME = 'medai360'
MIDAI_PASSWORD = '12345678'

# 融途网
RONGTU_URL = 'http://shuju.erongtu.com/api/borrow'
RONGTU_URL_TEST = 'http://shuju.erongtu.com/api/test'
RONGTU_ID = 1638

# 金山
WLB_FOR_JINSHAN_KEY = '1994'
JINSHAN_CALL_BACK_URL = 'https://vip.wps.cn/task/api/reward'

# 上海外呼
WLB_FOR_SHLS_KEY = '1995'

# 南京外呼
WLB_FOR_NJWH_KEY = '2002'

# 石头村
WLB_FOR_SHITOUCUN_KEY = '1996'
SHITOUCUN_CALL_BACK_URL = 'http://www.stcun.com/task/interface/int'

# 富爸爸
FUBA_COOP_ID = 133
FUBA_KEY = 'wanglibao@123'
WLB_FOR_FUBA_KEY = '1997'
FUBA_CALL_BACK_URL = 'http://www.fbaba.net/track/cps.php'
FUBA_DEFAULT_TID = '1316'
FUBA_ACTIVITY_PAGE = 'index'
FUBA_PERIOD = 30
FUBA_CHANNEL_CODE = 'fuba'

#彩票
LINGCAIBAO_BASE_ISSUE = 2015090
LINGCAIBAO_BASE_DATETIME = datetime(2015, 8, 4)
LINGCAIBAO_CHANNEL_ID = 'wanglibao'
LINGCAIBAO_KEY = 'wanglibao'
if ENV == ENV_PRODUCTION:
    LINGCAIBAO_URL_ORDER = 'http://open.lingcaibao.com/lingcaiapi/order'
else:
    LINGCAIBAO_URL_ORDER = 'http://test.lingcaibao.com/lingcaiapi/order'

# 云端
WLB_FOR_YUNDUAN_KEY = '1998'
YUNDUAN_CALL_BACK_URL = 'http://www.yunduanlm.com/effect.php'
YUNDUAN_ACTIVITY_PAGE = 'marketing_baidu'
YUNDUAN_COOP_ID = 298

# 易车
WLB_FOR_YICHE_KEY = '1999'
if ENV == ENV_PRODUCTION:
    YICHE_COOP_ID = 200116
    YICHE_KEY = '2305fb3ee0c47140f0ea6b7e'
    YICHE_CALL_BACK_URL = 'http://openapi.chedai.bitauto.com/PlatForm/API'
else:
    YICHE_COOP_ID = 200104
    YICHE_KEY = '0dae7d5bbcd493785f057bc1'
    YICHE_CALL_BACK_URL = 'http://debug.openapi.chedai.com:8002/PlatForm/API'

# 智推
WLB_FOR_ZHITUI1_KEY = '2000'
ZHITUI_COOP_ID = '370'
ZHITUI_CALL_BACK_URL = 'http://api.zhitui.com/wanglibao/recive.php'

# 中国电信
WLB_FOR_ZGDX_KEY = '2001'
ZGDX_QUERY_URL = 'http://182.140.241.47:8080/fps/ESBFlowService.do'
# ZGDX_QUERY_KEY = 'hwDmXQLqdzJ4wozz'
# ZGDX_QUERY_IV = '7988680669963722'
if ENV == ENV_PRODUCTION:
    ZGDX_CALL_BACK_URL = 'http://182.140.241.47:8080/fps/flowService.do'
    ZGDX_PARTNER_NO = '102139887'
    ZGDX_SERVICE_CODE = 'FS0001'
    ZGDX_CONTRACT_ID = '101062'
    ZGDX_ACTIVITY_ID = '102292'
    ZGDX_KEY = 'hwDmXQLqdzJ4wozz'
    ZGDX_IV = '7988680669963722'
else:
    ZGDX_CALL_BACK_URL = 'http://118.123.170.72:8888/fps/flowService.do'
    ZGDX_PARTNER_NO = '100054374'
    ZGDX_SERVICE_CODE = 'FS0001'
    ZGDX_CONTRACT_ID = 'test20150901165440'
    ZGDX_ACTIVITY_ID = '100785'
    ZGDX_KEY = 'H5gOs1ZshKZ6WikN'
    ZGDX_IV = '8888159601152533'

# 返利投
WLB_FOR_FANLITOU_KEY = '2002'

# 迅雷VIP
WLB_FOR_XUNLEI9_KEY = '2003'
XUNLEIVIP_QUERY_URL = 'http://dynamic.vip.xunlei.com/xljinku/checkOrder'
XUNLEIVIP_CALL_BACK_URL = 'http://dynamic.vip.xunlei.com/xljinku/sendvip/'
XUNLEIVIP_REGISTER_CALL_BACK_URL = 'http://dynamic.vip.xunlei.com/script/act/coop_report.php'
XUNLEIVIP_LOGIN_URL = 'http://act.vip.xunlei.com/vip/cooplogin/?coop=wanglibao'
XUNLEIVIP_REGISTER_KEY = 'wpg8fijoah3qkb'
XUNLEIVIP_KEY = 'wgvjfe9ogh8b6b'
XUNLEI9_ACTIVITY_PAGE = 'marketing_xunlei_setp'
XUNLEI9_PV_URL = 'http://dypay.vip.xunlei.com/user/vipstat/'

# 脉脉
WLB_FOR_MAIMAI1_KEY = '2004'
MAIMAI1_CHANNEL_CODE = 'maimai1'
MAIMAI1_ACTIVITY_PAGE = 'maimai_index'
MAIMAI_CALL_BACK_URL = 'https://maimai.cn/hb_pingback'

# 亚洲财经
WLB_FOR_YZCJ_KEY = '2005'
YZCJ_COOP_KEY = 'yzcj_2005'
if ENV == ENV_PRODUCTION:
    YZCJ_CALL_BACK_URL = 'http://www.asiafinance.cn/wanglibaoBg.jspx'
else:
    YZCJ_CALL_BACK_URL = 'http://42.62.0.122:8080/jeecms/wanglibaoBg.jspx'


# 对第三方回调做IP鉴权所信任的IP列表
if ENV == ENV_PRODUCTION:
    local_ip = None
else:
    local_ip = '127.0.0.1'
TRUST_IP = [
    local_ip,
    # 中国电信出口ip
    '182.140.241.10',
    # 迅雷VIP
    '123.150.216.177',
    '111.161.125.177',
]

SUIT_CONFIG = {
    'LIST_PER_PAGE': 100
}

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = 'wanglibank_redis'

# CACHES = {
#     'default': {
#         'BACKEND': 'redis_cache.RedisCache',
#         'LOCATION': [
#             '127.0.0.1:6379',
#         ],
#         'OPTIONS': {
#             'DB': 0,
#             'PASSWORD': '',
#             'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
#             'PARSER_CLASS': 'redis.connection.HiredisParser',
#             'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
#             'CONNECTION_POOL_CLASS_KWARGS': {
#                 'max_connections': 50,
#                 'timeout': 20,
#             },
#             'MAX_CONNECTIONS': 1000,
#             'PICKLE_VERSION': -1,
#         }
#     }
# }
# REDIS_TIMEOUT = 7*24*60*60
# CUBES_REDIS_TIMEOUT = 60*60
# NEVER_REDIS_TIMEOUT = 365*24*60*60
AMORIZATION_AES_IV = '8'*16
AMORIZATION_AES_KEY = 'tpuyk8#3*09a@!ds8$j6wg$$.r!$pb7h'
THREE_DEFAULT_CHANNEL_CODE = 'wanglibao-three'
if ENV == ENV_PRODUCTION:
    WEIXIN_CALLBACK_URL = 'https://www.wanglibao.com'
else:
    WEIXIN_CALLBACK_URL = 'https://staging.wanglibao.com'
    CALLBACK_HOST = 'https://staging.wanglibao.com'
# 短信到达率统计时间间隔
MESSAGE_TIME_DELTA = timedelta(minutes=10)
WANGLIBAO_ACCESS_TOKEN_KEY = '31D21828CC9DA7CE527F08481E361A7E'

# 第三方来我们这的用户名密码去获取 token
TOKEN_CLIENTS = {
    'rong360': 'wanglibao_1116',
}

APP_DECRYPT_KEY = "31D21828CC9DA7CE527F08481E361A7E"


# 数据魔方接口
DATACUBE_URL = 'http://stat.wanglibao.com:10000/datacube/index'
if ENV == ENV_PRODUCTION:
    DATACUBE_URL = 'http://10.171.37.235:10000/datacube/index'
