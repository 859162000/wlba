# encoding:utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.decorators import login_required
import views
import manage_views

urlpatterns = patterns(
    '',
    url(r'^join/(?P<account_key>\w+)/$', views.WeixinJoinView.as_view(), name='weixin_join'),
    url(r'^list/$', views.P2PListView.as_view(), name='weixin_p2p_list'),
    url(r'^account/$', login_required(views.WeixinAccountHome.as_view(), login_url='/weixin/login/'), name='weixin_account'),
    url(r'^view/(?P<template>\w+)/(?P<id>\w+)/$', views.P2PDetailView.as_view(), name='weixin_p2p_detail'),
    url(r'^account/bankcard/$', login_required(views.WeixinAccountBankCard.as_view(), login_url='/weixin/login/'), name='weixin_bankcard'),
    url(r'^account/bankcard/add/$', login_required(views.WeixinAccountBankCardAdd.as_view(), login_url='/weixin/login/'), name='weixin_bankcard_add'),
    url(r'^login/$', views.WeixinLogin.as_view(), name='weixin_login'),
    url(r'^oauth/login/$', views.WeixinOauthLoginRedirect.as_view(), name='weixin_oauth_login_redirect'),
    url(r'^regist/$', TemplateView.as_view(template_name="weixin_regist.jade")),
    url(r'^security/$', login_required(views.WeixinAccountSecurity.as_view(), login_url='/weixin/login/'), name='weixin_security'),
    url(r'^authentication/', TemplateView.as_view(template_name="weixin_authentication.jade")),
    url(r'^recharge/$', login_required(views.WeixinRecharge.as_view(), login_url='/weixin/login/'), name='weixin_recharge_first'),
    url(r'^recharge/second/$', login_required(views.WeixinRechargeSecond.as_view(), login_url='/weixin/login/'), name='weixin_recharge_second'),
    url(r'^pay/test/$', views.WeixinPayTest.as_view(), name="weixin_pay_test"),
    url(r'^pay/notify/$', views.WeixinPayNotify.as_view(), name='weixin_pay_notify'),
    url(r'^transaction/(?P<status>\w+)/$', login_required(views.WeixinTransaction.as_view(), login_url='/weixin/login/'), name="weixin_transaction"),
    url(r'^more/$', TemplateView.as_view(template_name="weixin_more.jade")),
    url(r'^more/contactus/$', TemplateView.as_view(template_name="weixin_contactus.jade")),
    url(r'^more/aboutus/$', TemplateView.as_view(template_name="weixin_aboutus.jade")),

    # js api
    url(r'^api/jsapi_config/$', views.WeixinJsapiConfig.as_view(), name='weixin_jsapi_config_api'),
    url(r'^api/login/$', views.WeixinLoginAPI.as_view(), name='weixin_login_api'),
    url(r'^api/pay/order/$', views.WeixinPayOrder.as_view(), name='weixin_pay_order_api'),
)

# 微信管理后台
urlpatterns += patterns(
    '',
    # view
    url(r'^manage/$', manage_views.IndexView.as_view(), name='wx_manage_index'),
    url(r'^manage/account/(?P<account_key>\w+)/$', manage_views.AccountView.as_view(), name='wx_manage_account'),
    url(r'^manage/menu/$', manage_views.MenuView.as_view(), name='wx_manage_menu'),
    url(r'^manage/material/$', manage_views.MaterialView.as_view(), name='wx_manage_material'),
    url(r'^manage/material/img/(?P<media_id>[\w_-]+)/$', manage_views.MaterialImageView.as_view(), name='wx_manage_material_image'),

    # api
    url(r'^manage/api/menu/$', manage_views.MenuAPI.as_view(), name='wx_manage_menu_api'),
    url(r'^manage/api/materials/$', manage_views.MaterialListAPI.as_view(), name='wx_manage_material_list_api'),
    url(r'^manage/api/materials/count/$', manage_views.MaterialCountAPI.as_view(), name='wx_manage_material_count_api'),
    url(r'^manage/api/materials/(?P<media_id>\w+)/$', manage_views.MaterialDetailAPI.as_view(), name='wx_manage_material_detail_api'),
)
