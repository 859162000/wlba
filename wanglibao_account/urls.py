#!/usr/bin/env python
# encoding:utf-8

from django.conf import settings
from django.conf.urls import patterns, url, include
# from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, RedirectView
from registration.backends.default.views import ActivationView
from forms import EmailOrPhoneAuthenticationForm, TokenSecretSignAuthenticationForm
from views import (RegisterView, PasswordResetGetIdentifierView, ResetPassword, EmailSentView, AccountHome,
                   AccountTransaction, AccountBankCard, AccountTransactionP2P, IdVerificationView,
                   AccountTransactionDeposit, AccountRedPacket, AccountCoupon,
                   AccountTransactionWithdraw, P2PAmortizationView, user_product_contract, test_contract,
                   Third_login, Third_login_back, MessageView, MessageDetailAPIView, MessageCountAPIView,
                   MessageListAPIView, AccountRepayment, AddressView, AccountInviteView, user_product_contract_kf,
                   JrjiaAutoRegisterView, ManualModifyPhoneTemplate, IdentityInformationTemplate, ValidateAccountInfoTemplate,
                SMSModifyPhoneValidateTemplate, SMSModifyPhoneTemplate)
from django.contrib.auth import views as auth_views
from views import AutomaticView
from wanglibao_account.cooperation import JrjiaCPSView, JrjiaP2PStatusView, JrjiaP2PInvestView, JrjiaReportView, \
    JrjiaUsStatusView
from wanglibao_account.views import FirstPayResultView
from wanglibao_lottery.views import LotteryListTemplateView
from wanglibao_account.decorators import login_required

urlpatterns = patterns(
    '',
    url(r'^home/$', login_required(AccountHome.as_view(),
                                   login_url='/accounts/login/')),
    url(r'^home/experience/$', login_required(AccountHome.as_view(),
                                              login_url='/accounts/login/')),
    url(r'^home/jiuxian/$', login_required(AccountHome.as_view(),
                                           login_url='/accounts/login/'), name='accounts_jiuxian'),
    url(r'^p2p/amortization/(?P<product_id>\d+)', login_required(P2PAmortizationView.as_view(),
                                                                 login_url='/accounts/login/')),
    url(r'^p2p/contract/(?P<product_id>\d+)', user_product_contract),
    url(r'^contract_for_kf',                 user_product_contract_kf),
    url(r'^transaction/fund/$', login_required(AccountTransaction.as_view(),
                                               login_url='/accounts/login/')),
    url(r'^transaction/p2p/$', login_required(AccountTransactionP2P.as_view(), login_url='/accounts/login/')),
    url(r'^redpacket/(?P<status>\w+)/$', login_required(AccountRedPacket.as_view(), login_url='/accounts/login/')),
    url(r'^coupon/(?P<status>\w+)/$', login_required(AccountCoupon.as_view(), login_url='/accounts/login/')),

    url(r'^repayment/$', login_required(AccountRepayment.as_view(), login_url='/accounts/login/')),
    url(r'^transaction/deposit/$', login_required(AccountTransactionDeposit.as_view(),
                                                  login_url='/accounts/login/')),
    # 彩票详情页
    # url(r'^caipiao/detail/$', login_required(AccountTransactionDeposit.as_view(),
    #                                               login_url='/accounts/login/')),
    url(r'^transaction/withdraw/$', login_required(AccountTransactionWithdraw.as_view(),
                                                   login_url='/accounts/login/')),
    url(r'^bankcard/$', login_required(AccountBankCard.as_view(),
                                       login_url='/accounts/login/')),
    url(r'^favorite/$', login_required(TemplateView.as_view(template_name='account_favorite.jade'),
                                       login_url='/accounts/login/')),
    url(r'^setting/$', login_required(TemplateView.as_view(template_name='account_setting.jade'),
                                      login_url='/accounts/login/')),
    url(r'^id_verify/$', login_required(IdVerificationView.as_view(), login_url='/accounts/login/')),
    #url(r'^add_introduce/$', login_required(IntroduceRelation.as_view(), login_url='/accounts/login/')),

    url(r'^invite/$', login_required(AccountInviteView.as_view(), login_url='/accounts/login/')),
    url(r'^frozen/$', TemplateView.as_view(template_name="frozen.jade"), name='accounts_frozen'),

    url(r'^login/ajax/$', 'wanglibao_account.views.ajax_login'),

    url(r'^login/$', 'django.contrib.auth.views.login',
        {
            "template_name": "login_test.jade",
            "authentication_form": EmailOrPhoneAuthenticationForm,
        }, name="auth_login"),
    url(r'^token/login/ajax/$', 'wanglibao_account.views.ajax_token_login'),
    url(r'^token_login/$', 'django.contrib.auth.views.login',
        {
            "template_name": "fetchtoken.jade",
            "authentication_form": TokenSecretSignAuthenticationForm,
        }, name="token_login"),

    url(r'^login/callback/$', login_required(Third_login_back.as_view())),
    url(r'^login/(?P<login_type>\w+)/$', login_required(Third_login.as_view())),

    url(r'^register/$', RegisterView.as_view(), name='auth_register'),
    url(r'^register/first/$', TemplateView.as_view(template_name="register_first.jade")),
    # url(r'^register/three/$', TemplateView.as_view(template_name="register_three.jade")),
    url(r'^register/three/$', login_required(FirstPayResultView.as_view())),
    url(r'^api/register/jrjia/$', JrjiaAutoRegisterView.as_view(), name='auth_register_auto'),
    url(r'^api/cps/$', JrjiaCPSView.as_view(), name='auth_register_auto'),
    url(r'^api/pstatus/$', JrjiaP2PStatusView.as_view(), name='auth_register_auto'),
    url(r'^api/pinvest/$', JrjiaP2PInvestView.as_view(), name='auth_register_auto'),
    url(r'^api/report/$', JrjiaReportView.as_view(), name='auth_register_auto'),
    url(r'^api/usstatus/$', JrjiaUsStatusView.as_view(), name='auth_register_auto'),
    url(r'^register/wap/$', RedirectView.as_view(url='/weixin/regist/', permanent=True), name='wap_register'),
    url(r'^register/ajax/$', 'wanglibao_account.views.ajax_register'),

    url(r'^message/$', login_required(MessageView.as_view(), login_url='/accounts/login/')),
    url(r'^message/list/$', MessageListAPIView.as_view(), name='message_list_view'),
    url(r'^message/count/$', MessageCountAPIView.as_view(), name='message_count_view'),
    url(r'^message/(?P<message_id>\d+)/$', MessageDetailAPIView.as_view(), name='message_detail_view'),
    url(r'^email/sent/$', EmailSentView.as_view(), name='email_sent'),

    url(r'^password/change/$', "wanglibao_account.views.password_change", name='password_change'),
    url(r'^password/change/done/', TemplateView.as_view(template_name='html/password_change_done.html'),
        name='password_change_done'),
    url(r'^activate/complete/$',
        TemplateView.as_view(template_name='activation_complete.jade'),
        name='registration_activation_complete'),
    url(r'^activate/(?P<activation_key>\w+)/$',
        ActivationView.as_view(template_name="activate.jade"),
        name='registration_activate'),

    url(r'^password/reset/identifier/', PasswordResetGetIdentifierView.as_view(), name="password_reset"),
    url(r'^password/reset/validate/', PasswordResetGetIdentifierView.as_view(), name="password_reset_validate"),
    url(r'^password/reset/send_mail/', "wanglibao_account.views.send_validation_mail", name="send_validation_mail"),
    url(r'^password/reset/send_validate_code/', "wanglibao_account.views.send_validation_phone_code",
        name="send_validation_phone_code"),
    url(r'^password/reset/validate_phone_code/', "wanglibao_account.views.validate_phone_code"),
    url(r'^password/reset/set_password/', ResetPassword.as_view(), name="password_reset_set_password"),
    url(r'^password/reset/done/', TemplateView.as_view(template_name="password_reset_done.jade"),
        name="password_reset_done"),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        {
            'post_reset_redirect': 'password_reset_done',
            'template_name': 'password_reset_confirm.jade',
        },
        name='auth_password_reset_confirm'),
    url(r'', include('registration.backends.default.urls')),
    url(r'^address/$', login_required(AddressView.as_view(), login_url='/accounts/login/'), name='accounts_address'),

    url(r'^auto_tender/$', login_required(AutomaticView.as_view(), login_url='/accounts/login/')),
    url(r'^caipiao/$', login_required(LotteryListTemplateView.as_view(), login_url='/accounts/login/')),

    url(r'^security/$', login_required(IdentityInformationTemplate.as_view(template_name='account_safe.jade'), login_url='/accounts/login/')),
    url(r'^manual_modify/vali_acc_info/$', login_required(ValidateAccountInfoTemplate.as_view(template_name="manual_audit.jade"), login_url='/accounts/login/')),
    url(r'^manual_modify/phone/$', ManualModifyPhoneTemplate.as_view()),
    url(r'^sms_modify/vali_acc_info/$', login_required(SMSModifyPhoneValidateTemplate.as_view(template_name="sms_vali_phone.jade"), login_url='/accounts/login/')),
    url(r'^sms_modify/phone/$', login_required(SMSModifyPhoneTemplate.as_view(template_name="sms_modify_phone.jade"), login_url='/accounts/login/'))
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^contract/test/(?P<equity_id>\w+)/', test_contract)
    )