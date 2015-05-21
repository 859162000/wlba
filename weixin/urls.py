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
    url(r'^view/(?P<template>\w+)/(?P<id>\w+)/', views.P2PDetailView.as_view(), name='weixin_p2p_detail'),
    url(r'^login/$', views.WeixinLogin.as_view(), name='weixin_login'),
    url(r'^oauth/login/$', views.WeixinOauthLoginRedirect.as_view(), name='weixin_oauth_login_redirect'),
    url(r'^regist/', TemplateView.as_view(template_name="weixin_regist.jade")),
    url(r'^security/', TemplateView.as_view(template_name="weixin_security.jade")),
    url(r'^value/', TemplateView.as_view(template_name="weixin_value.jade")),
    url(r'^authentication/', TemplateView.as_view(template_name="weixin_authentication.jade")),
    url(r'^recharge/', TemplateView.as_view(template_name="weixin_recharge.jade")),
    url(r'^pay/test/$', views.WeixinPayTest.as_view(), name="weixin_pay_test"),
    url(r'^pay/notify/$', views.WeixinPayNotify.as_view(), name='weixin_pay_notify'),

    # js api
    url(r'^api/jsapi_config/$', views.WeixinJsapiConfig.as_view(), name='weixin_jsapi_config_api'),
    url(r'^api/login/$', views.WeixinLoginApi.as_view(), name='weixin_login_api'),
    url(r'^api/pay/order/$', views.WeixinPayOrder.as_view(), name='weixin_pay_order_api'),

)
