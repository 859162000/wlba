try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('wanglibao_anti.views',
                       url(r'captcha/refresh/$', 'captcha_refresh', name='captcha-refresh'),
                       )
