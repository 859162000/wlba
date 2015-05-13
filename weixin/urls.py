# encoding:utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.decorators import login_required
import views

urlpatterns = patterns(
    '',
    url(r'^connect/(?P<id>\w+)/$', views.ConnectView.as_view(), name='weixin_connect'),
    url(r'^list/', views.P2PListView.as_view(), name='weixin_p2p_list'),
    url(r'^account/', login_required(views.WeixinAccountHome.as_view(), login_url='/weixin/login/'), name='weixin_account'),
    url(r'^detail/(?P<id>\w+)', views.P2PDetailView.as_view(), name='weixin_p2p_detail'),
    url(r'^login/$', views.WeixinLogin.as_view(), name='weixin_login'),
    url(r'^oauth/login/$', views.WeixinOauthLoginRedirect.as_view(), name='weixin_oauth_login_redirect'),

    # js api
    url(r'^jsapi_config.json$', views.WeixinJsapiConfig.as_view(), name='weixin_jsapi_config_api'),
    url(r'^login.api$', views.WeixinLoginApi.as_view(), name='weixin_login_api')

)
