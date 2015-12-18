# encoding:utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.decorators import login_required
import views, activity_views, manage_views, sub_views, base


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
    url(r'^regist/first/$', TemplateView.as_view(template_name="weixin_registProcess_first.jade")),
    url(r'^regist/second/$', TemplateView.as_view(template_name="weixin_registProcess_second.jade")),
    url(r'^regist/three/$', TemplateView.as_view(template_name="weixin_registProcess_three.jade")),


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
    url(r'^bind/$', login_required(views.WeixinBind.as_view(), login_url='/weixin/login/'), name='weixin_bind'),


    url(r'^unbind/$', views.UnBindWeiUser.as_view(), name='weixin_unbind'),
    url(r'^reward/(?P<status>\w+)/$', login_required(views.WeixinCouponList.as_view(), login_url='/weixin/login/')),



    # js api
    url(r'^api/jsapi_config/$', views.WeixinJsapiConfig.as_view(), name='weixin_jsapi_config_api'),
    url(r'^api/login/$', views.WeixinLoginAPI.as_view(), name='weixin_login_api'),

    url(r'^api/unbind/$', views.UnBindWeiUserAPI.as_view(), name='weixin_unbind_api'),
    url(r'^api/pay/order/$', views.WeixinPayOrder.as_view(), name='weixin_pay_order_api'),
    url(r'api/wx_code/$', views.AuthorizeCode.as_view(), name='weixin_authorize_code'),
    url(r'api/wx_userinfo/$', views.AuthorizeUser.as_view(), name='weixin_authorize_user_info'),
    url(r'api/wx_getinfo/$', views.GetAuthUserInfo.as_view(), name='weixin_get_user_info'),
    url(r'api/account/wx_getinfo/$', views.GetUserInfo.as_view(), name='weixin_get_account_user_info'),
    url(r'api/generate/qr_limit_scene_ticket/$', views.GenerateQRLimitSceneTicket.as_view(), name='generate_qr_limit_scene_ticket'),#生成永久二维码
    url(r'api/generate/qr_scene_ticket/$', views.GenerateQRSceneTicket.as_view(), name='generate_qr_scene_ticket'),#生成临时二维码

    #test
    url(r'^jump_page/$', views.JumpPageTemplate.as_view(template_name="sub_times.jade"), name='jump_page'),
    url(r'^is_bind/$', TemplateView.as_view(template_name="sub_is_bind.jade")),
    url(r'^award_index/$', activity_views.AwardIndexTemplate.as_view(template_name="sub_award.jade"), name='award_index'),
    url(r'^award_rule/$', TemplateView.as_view(template_name="sub_award_rule.jade")),
    url(r'^sub_code/$', base.ChannelBaseTemplate.as_view(template_name="sub_code.jade", wx_classify='fwh', wx_code='test1')),#wx_classify='dyh' or 'fwh'
    url(r'^sub_invite/$', activity_views.InviteWeixinFriendTemplate.as_view(template_name="sub_invite_server.jade"), name='sub_invite'),
    #微站
    # url(r'^sub_login/$', TemplateView.as_view(template_name="service_login.jade")),
    # url(r'^sub_regist/$', TemplateView.as_view(template_name="service_regist.jade")),
    # url(r'^sub_regist_first/$', TemplateView.as_view(template_name="service_registProcess_first.jade")),
    # url(r'^sub_regist_second/$', TemplateView.as_view(template_name="service_registProcess_second.jade")),
    # url(r'^sub_regist_three/$', TemplateView.as_view(template_name="service_registProcess_three.jade")),
    # url(r'^sub_account/$', TemplateView.as_view(template_name="service_account.jade")),

)

# 微信管理后台
urlpatterns += patterns(
    '',
    url(r'^sub_join/(?P<account_key>\w+)/$', sub_views.SubWeixinJoinView.as_view(), name='sub_weixin_join'),
)


