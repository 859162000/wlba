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
    url(r'^regist/$', views.WeixinRegister.as_view(), name="weixin_register"),
    url(r'^regist/succees/$', TemplateView.as_view(template_name="weixin_regist_succees_new.jade")),
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
    url(r'bind/$', login_required(views.WeixinBind.as_view(), login_url='/weixin/login/'), name='weixin_bind'),
    # url(r'bind/login/$', views.WeixinBindLogin.as_view(), name='sub_login'),
    # url(r'bind/register/$', views.WeixinBindRegister.as_view(), name='sub_register'),
    url(r'weixin_unbind/$', views.UnBindWeiUser.as_view(), name='weixin_unbind'),
    url(r'^reward/(?P<status>\w+)/$', login_required(views.WeixinCouponList.as_view(), login_url='/weixin/login/')),

    # js api
    url(r'^api/jsapi_config/$', views.WeixinJsapiConfig.as_view(), name='weixin_jsapi_config_api'),
    url(r'^api/login/$', views.WeixinLoginAPI.as_view(), name='weixin_login_api'),

    url(r'^api/unbind/$', views.UnBindWeiUserAPI.as_view(), name='weixin_unbind_api'),
    url(r'^api/send_template_msg/$', views.SendTemplateMessage.as_view(), name='send_template_message'),
    url(r'^api/pay/order/$', views.WeixinPayOrder.as_view(), name='weixin_pay_order_api'),
    url(r'api/wx_code/$', views.AuthorizeCode.as_view(), name='weixin_authorize_code'),
    url(r'api/wx_userinfo/$', views.AuthorizeUser.as_view(), name='weixin_authorize_user_info'),
    url(r'api/wx_getinfo/$', views.GetAuthUserInfo.as_view(), name='weixin_get_user_info'),
    url(r'api/account/wx_getinfo/$', views.GetUserInfo.as_view(), name='weixin_get_account_user_info'),
    url(r'api/generate/qr_limit_scene_ticket/$', views.GenerateQRLimitSceneTicket.as_view(), name='generate_qr_limit_scene_ticket'),
    url(r'api/generate/qr_scene_ticket/$', views.GenerateQRSceneTicket.as_view(), name='generate_qr_scene_ticket'),

    #test
    url(r'^jump_page/$', views.JumpPageTemplate.as_view(template_name="sub_times.jade"), name='jump_page'),
    url(r'^is_bind/$', TemplateView.as_view(template_name="sub_is_bind.jade")),
    url(r'^login_success/$', TemplateView.as_view(template_name="sub_login_success.jade")),
    url(r'^unbind_success/$', TemplateView.as_view(template_name="sub_unbind_success.jade")),
    url(r'^award_index/$', TemplateView.as_view(template_name="sub_award.jade")),
    url(r'^award_rule/$', TemplateView.as_view(template_name="sub_award_rule.jade")),
    url(r'^sub_code/$', TemplateView.as_view(template_name="sub_code.jade")),

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
