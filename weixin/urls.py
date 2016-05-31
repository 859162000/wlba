# encoding:utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.decorators import login_required
from wanglibao_activity.views import WeixinGGLTemplate
import views, activity_views, manage_views, sub_views, base, main_views
from experience_gold.views import ExperienceGoldView
from common.decorators import fwh_login_required
from marketing.views import HMDP2PListView

urlpatterns = patterns(
    '',
    url(r'^join/(?P<account_key>\w+)/$', views.WeixinJoinView.as_view(), name='weixin_join'),
    url(r'^list/$', views.P2PListView.as_view(template_name='weixin_list.jade'), name='weixin_p2p_list'),
    url(r'^account/$', login_required(views.WeixinAccountHome.as_view(), login_url='/weixin/login/'), name='weixin_account'),
    url(r'^view/(?P<template>\w+)/(?P<id>\w+)/$', views.P2PDetailView.as_view(), name='weixin_p2p_detail'),
    url(r'^account/bankcard/$', login_required(views.WeixinAccountBankCard.as_view(), login_url='/weixin/login/'), name='weixin_bankcard'),
    url(r'^account/bankcard/add/$', login_required(views.WeixinAccountBankCardAdd.as_view(), login_url='/weixin/login/'), name='weixin_bankcard_add'),

    url(r'^login/$', views.WeixinLogin.as_view(), name='weixin_login'),
    url(r'^coop_login/$', views.WeixinCoopLogin.as_view(), name='weixin_coop_login'),
    url(r'^oauth/login/$', views.WeixinOauthLoginRedirect.as_view(), name='weixin_oauth_login_redirect'),
    url(r'^regist/$', views.WeixinRegister.as_view(), name="weixin_register"),
    url(r'^coop_regist/$', views.WeixinCoopRegister.as_view(), name="weixin_coop_register"),
    url(r'^regist/succees/$', TemplateView.as_view(template_name="weixin_regist_succees_new.jade")),
    url(r'^regist/first/$', TemplateView.as_view(template_name="weixin_registProcess_first.jade")),
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
    #url(r'^trade-pwd/back/$', TemplateView.as_view(template_name="weixin_tradepwd_back.jade")),
    url(r'^trade-pwd/back/$', login_required(TemplateView.as_view(template_name="weixin_tradepwd_back.jade"), login_url='/weixin/login/')),

    url(r'^received/all/$', login_required(views.WeiXinReceivedAll.as_view(), login_url='/weixin/login/'), name='weixin_received_all'),
    url(r'^received/month/$', login_required(views.WeiXinReceivedMonth.as_view(), login_url='/weixin/login/'), name='weixin_received_month'),
    url(r'^received/detail/$', login_required(views.WeiXinReceivedDetail.as_view(), login_url='/weixin/login/'), name='weixin_received_detail'),

    url(r'^unbind/$', views.UnBindWeiUser.as_view(), name='weixin_unbind'),
    url(r'^reward/(?P<status>\w+)/$', login_required(views.WeixinCouponList.as_view(), login_url='/weixin/login/')),

    url(r'^p2p_list/coop/$', views.P2PListView.as_view(), name='weixin_p2p_list_coop'),

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

    url(r'^sub_invite/$', fwh_login_required(activity_views.InviteWeixinFriendTemplate.as_view(template_name="sub_invite_server.jade"),login_url='/weixin/sub_login_redirect/'),
                                                                                            name='sub_invite'),
    url(r'^award_index/$', fwh_login_required(TemplateView.as_view(template_name="sub_award.jade"),login_url='/weixin/sub_login_redirect/'
                                          ),name='award_index'),
    # url(r'^award_reatcoin/$', fwh_login_required(RedirectView.as_view(url='/weixin/award_eatcoin/'),login_url='/weixin/sub_login_redirect/')),
    url(r'^award_eatcoin/$', TemplateView.as_view(template_name="sub_eatcoin.jade")),
    url(r'^award_rule/$', TemplateView.as_view(template_name="sub_award_rule.jade")),

    url(r'^sub_regist_first/$', fwh_login_required(TemplateView.as_view(template_name="service_registProcess_first.jade"), login_url="/weixin/sub_login_redirect/")),
    url(r'^sub_regist_second/$', fwh_login_required(views.WeixinRegisterBindCard.as_view(template_name="service_registProcess_second.jade"), login_url="/weixin/sub_login_redirect/")),
    url(r'^sub_regist_three/$', fwh_login_required(TemplateView.as_view(template_name="service_registProcess_three.jade"), login_url="/weixin/sub_login_redirect/")),
    url(r'^sub_account/$', fwh_login_required(main_views.AccountTemplate.as_view(template_name="service_account.jade"), login_url="/weixin/sub_login_redirect/"), name='sub_account'),
    # url(r'^sub_account_old/$', fwh_login_required(main_views.AccountTemplate.as_view(template_name="service_account_old.jade"), login_url="/weixin/sub_login_redirect/")),

    url(r'^sub_recharge/$', fwh_login_required(main_views.RechargeTemplate.as_view(template_name="service_recharge.jade"), login_url="/weixin/sub_login_redirect/"), name="sub_recharge"),
    url(r'^sub_list/$', fwh_login_required(main_views.FwhP2PlistTemplate.as_view(template_name="service_list.jade"), login_url="/weixin/sub_login_redirect/"), name='fwh_p2p_list'),
    url(r'^sub_detail/(?P<template>\w+)/(?P<id>\w+)/$', fwh_login_required(views.P2PDetailView.as_view(source='fwh'), login_url="/weixin/sub_login_redirect/")),
    url(r'^sub_experience/(?P<template>(account))/$', fwh_login_required(ExperienceGoldView.as_view(), login_url='/weixin/sub_login_redirect/')),
    url(r'^sub_transaction/(?P<status>\w+)/$', fwh_login_required(views.WeixinTransaction.as_view(template_name="service_transaction_repay.jade", source='fwh'), login_url="/weixin/sub_login_redirect/")),

    url(r'^sub_reward/(?P<status>\w+)/$', fwh_login_required(views.WeixinCouponList.as_view(template_name="service_reward.jade"), login_url="/weixin/sub_login_redirect/")),
    #银行卡管理
    url(r'^sub_bankcards/$', fwh_login_required(views.WeixinAccountBankCard.as_view(template_name="service_bankcard.jade"), login_url="/weixin/sub_login_redirect/")),
    url(r'^sub_pwd_back/$', TemplateView.as_view(template_name="service_tradepwd_back.jade")),
    #微站 api
    url(r'api/fwh_login/$', main_views.WXLoginAPI.as_view(), name='weixin_fwh_login'),
    url(r'api/fwh/p2p_ajax_list/$', main_views.P2PListFWH.as_view(), name='fwh_p2p_ajax_list'),

    #刮刮乐
    url(r'^activity_ggl/$', fwh_login_required(WeixinGGLTemplate.as_view(template_name="service_scratch.jade"),login_url='/weixin/sub_login_redirect/'
                                          ),name='activity_ggl'),
    url(r'^sub_checkIn/$', fwh_login_required(TemplateView.as_view(template_name="service_checkIn.jade"),login_url='/weixin/sub_login_redirect/'
                                          ),name='sub_checkIn'),
    url(r'^sub_checkIn_share/$', TemplateView.as_view(template_name="service_checkIn_share.jade")),

    url(r'^new_user_gift/$', fwh_login_required(TemplateView.as_view(template_name="server_new_user_gift.jade"),login_url='/weixin/sub_login_redirect/'
                                          ),name='new_user_gift'),
    url(r'^app_airport_operation/$', fwh_login_required(TemplateView.as_view(template_name="app_airport_operation.jade"),login_url='/weixin/sub_login_redirect/')),
    url(r'^app_august_phone/$', fwh_login_required(TemplateView.as_view(template_name="app_august_phone.jade"), login_url='/weixin/sub_login_redirect/')),
)


#渠道注册落地页
urlpatterns += patterns(
    '',
    url(r'^channel_register/$', views.ChannelRegister.as_view(), name="weixin_register"),
    #url(r'^channel_register/$', TemplateView.as_view(template_name="channel_register.jade")),
    url(r'^channel_register_success/$', TemplateView.as_view(template_name="channel_register_success.jade"))
)
#活动api
urlpatterns += patterns(
    '',
    url(r'^sign_info/$', activity_views.GetSignShareInfo.as_view()),
    url(r'^daily_action/$', activity_views.DailyActionAPIView.as_view()),
    url(r'^continue_action_reward/$', activity_views.GetContinueActionReward.as_view()),
    #Comment by hb on 2016-05-31
    #url(r'^fetch_xunlei_vipcard/$', activity_views.FetchXunleiCardAward.as_view()),

)
#活动页面
urlpatterns += patterns(
    '',
    #Comment by hb on 2016-05-31
    #url(r'^app_xunlei_welfare/$', fwh_login_required(TemplateView.as_view(template_name="app_xunlei_welfare.jade"), login_url='/weixin/sub_login_redirect/')),
)
#h5活动页面
urlpatterns += patterns(
    '',
    url(r'^fwh_open_day_review/$', HMDP2PListView.as_view(template_name="app_open_day_review.jade", p2p_list_url_name="fwh_p2p_list")),
)
# 微信管理后台
urlpatterns += patterns(
    '',
    url(r'^sub_join/(?P<account_key>\w+)/$', sub_views.SubWeixinJoinView.as_view(), name='sub_weixin_join'),
)


