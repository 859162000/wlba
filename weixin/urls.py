# encoding:utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.decorators import login_required
from wanglibao_activity.views import WeixinGGLTemplate
import views, activity_views, manage_views, sub_views, base, main_views
from experience_gold.views import ExperienceGoldView
urlpatterns = patterns(
    '',
    url(r'^join/(?P<account_key>\w+)/$', views.WeixinJoinView.as_view(), name='weixin_join'),
    url(r'^list/$', views.P2PListView.as_view(template_name='weixin_list.jade'), name='weixin_p2p_list'),
    url(r'^account/$', login_required(views.WeixinAccountHome.as_view(), login_url='/weixin/login/'), name='weixin_account'),
    url(r'^view/(?P<template>\w+)/(?P<id>\w+)/$', views.P2PDetailView.as_view(), name='weixin_p2p_detail'),
    url(r'^account/bankcard/$', login_required(views.WeixinAccountBankCard.as_view(), login_url='/weixin/login/'), name='weixin_bankcard'),
    url(r'^account/bankcard/add/$', login_required(views.WeixinAccountBankCardAdd.as_view(), login_url='/weixin/login/'), name='weixin_bankcard_add'),

    url(r'^login/$', views.WeixinLogin.as_view(), name='weixin_login'),
    url(r'^oauth/login/$', views.WeixinOauthLoginRedirect.as_view(), name='weixin_oauth_login_redirect'),
    url(r'^regist/$', views.WeixinRegister.as_view(), name="weixin_register"),
    url(r'^regist/succees/$', TemplateView.as_view(template_name="weixin_regist_succees_new.jade")),
    url(r'^regist/first/$', TemplateView.as_view(template_name="weixin_registProcess_first.jade")),
    #url(r'^regist/second/$', TemplateView.as_view(template_name="weixin_registProcess_second.jade")),
    url(r'^regist/second/$', login_required(views.WeixinRegisterBindCard.as_view(), login_url='/weixin/login/'), name='weixin_regist_bind_card'),
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

    url(r'^trade-pwd/edit/$', TemplateView.as_view(template_name="weixin_tradepwd_edit.jade")),
    url(r'^trade-pwd/back/$', TemplateView.as_view(template_name="weixin_tradepwd_back.jade")),
    url(r'^received/all/$', login_required(views.WeiXinReceivedAll.as_view(), login_url='/weixin/login/'), name='weixin_received_all'),
    url(r'^received/month/$', login_required(views.WeiXinReceivedMonth.as_view(), login_url='/weixin/login/'), name='weixin_received_month'),
    url(r'^received/detail/$', login_required(views.WeiXinReceivedDetail.as_view(), login_url='/weixin/login/'), name='weixin_received_detail'),

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

    #
    url(r'^jump_page/$', views.JumpPageTemplate.as_view(template_name="sub_times.jade"), name='jump_page'),
    url(r'^is_bind/$', TemplateView.as_view(template_name="sub_is_bind.jade")),


    # url(r'^sub_code/$', base.ChannelBaseTemplate.as_view(template_name="sub_code.jade", wx_classify='fwh', wx_code='test1')),#wx_classify='dyh' or 'fwh'


    #微站
    url(r'^sub_login_redirect/$', main_views.WXLoginRedirect.as_view(), name="sub_login_redirect"),
    url(r'^sub_login/$', main_views.WXLogin.as_view(template_name="service_login.jade"), name="fwh_login"),
    url(r'^sub_regist/$', main_views.WXRegister.as_view(template_name="service_regist.jade")),

    url(r'^sub_invite/$', login_required(activity_views.InviteWeixinFriendTemplate.as_view(template_name="sub_invite_server.jade"),login_url='/weixin/sub_login_redirect/'),
                                                                                            name='sub_invite'),
    url(r'^award_index/$', login_required(TemplateView.as_view(template_name="sub_award.jade"),login_url='/weixin/sub_login_redirect/'
                                          ),name='award_index'),
    url(r'^award_rule/$', TemplateView.as_view(template_name="sub_award_rule.jade")),

    url(r'^sub_regist_first/$', login_required(TemplateView.as_view(template_name="service_registProcess_first.jade"), login_url="/weixin/sub_login_redirect/")),
    url(r'^sub_regist_second/$', login_required(views.WeixinRegisterBindCard.as_view(template_name="service_registProcess_second.jade"), login_url="/weixin/sub_login_redirect/")),
    url(r'^sub_regist_three/$', login_required(TemplateView.as_view(template_name="service_registProcess_three.jade"), login_url="/weixin/sub_login_redirect/")),
    url(r'^sub_account/$', login_required(main_views.AccountTemplate.as_view(template_name="service_account.jade"), login_url="/weixin/sub_login_redirect/"), name='sub_account'),

    url(r'^sub_recharge/$', login_required(main_views.RechargeTemplate.as_view(template_name="service_recharge.jade"), login_url="/weixin/sub_login_redirect/"), name="sub_recharge"),
    url(r'^sub_list/$', login_required(main_views.FwhP2PlistTemplate.as_view(template_name="service_list.jade"), login_url="/weixin/sub_login_redirect/")),
    url(r'^sub_detail/(?P<template>\w+)/(?P<id>\w+)/$', login_required(views.P2PDetailView.as_view(source='fwh'), login_url="/weixin/sub_login_redirect/")),
    url(r'^sub_experience/(?P<template>(account))/$', login_required(ExperienceGoldView.as_view(), login_url='/weixin/sub_login_redirect/')),
    url(r'^sub_transaction/(?P<status>\w+)/$', login_required(views.WeixinTransaction.as_view(template_name="service_transaction_repay.jade", source='fwh'), login_url="/weixin/sub_login_redirect/")),

    url(r'^sub_reward/(?P<status>\w+)/$', login_required(views.WeixinCouponList.as_view(template_name="service_reward.jade"), login_url="/weixin/sub_login_redirect/")),
    #银行卡管理
    url(r'^sub_bankcards/$', login_required(views.WeixinAccountBankCard.as_view(template_name="service_bankcard.jade"), login_url="/weixin/sub_login_redirect/")),
    url(r'^sub_pwd_back/$', TemplateView.as_view(template_name="service_tradepwd_back.jade")),
    #微站 api
    url(r'api/fwh_login/$', main_views.WXLoginAPI.as_view(), name='weixin_fwh_login'),
    url(r'api/fwh/p2p_ajax_list/$', main_views.P2PListFWH.as_view(), name='fwh_p2p_ajax_list'),

    #刮刮乐
    url(r'^activity_ggl/$', login_required(WeixinGGLTemplate.as_view(template_name="service_scratch.jade"),login_url='/weixin/sub_login_redirect/'
                                          ),name='activity_ggl'),
    url(r'^sub_checkIn/$', TemplateView.as_view(template_name="service_checkIn.jade")),

)
#活动api
urlpatterns += patterns(
    '',
    url(r'^sign_info/$', activity_views.GetSignShareInfo.as_view()),
    url(r'^daily_action/$', activity_views.DailyActionAPIView.as_view()),
)
# 微信管理后台
urlpatterns += patterns(
    '',
    url(r'^sub_join/(?P<account_key>\w+)/$', sub_views.SubWeixinJoinView.as_view(), name='sub_weixin_join'),
)


