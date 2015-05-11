# encoding:utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView
import views

urlpatterns = patterns(
    '',
    url(r'^connect/(?P<id>\w+)/$', views.ConnectView.as_view(), name='weixin_connect'),
    url(r'^login/$', views.WeixinLogin.as_view(), name='weixin_login'),
    url(r'^oauth/login/(?P<id>\w+)/', views.WeixinOauthLoginRedirect.as_view(), name='weixin_oauth_login_redirect'),
    # js api
    url(r'^(?P<id>\w+)/jsapi_config.json$', views.WeixinJsapiConfig.as_view(), name='weixin_jsapi_config')
)
