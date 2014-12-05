#!/usr/bin/env python
# encoding:utf-8

from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from trust.views import TrustViewSet, IssuerViewSet
from wanglibao_account.views import (UserViewSet, ResetPasswordAPI, FundInfoAPIView,
                            AccountHomeAPIView, AccountP2PRecordAPI, AccountFundRecordAPI, AccountP2PAssetAPI, AccountFundAssetAPI,
                            P2PAmortizationAPI, UserProductContract, ChangePasswordAPIView,
                            AdminSendMessageAPIView)
from wanglibao_bank_financing.views import BankFinancingViewSet, BankViewSet
from wanglibao_banner.views import BannerViewSet
from wanglibao_buy.views import TradeInfoViewSet, DailyIncomeViewSet, TotalIncome
from wanglibao_cash.views import CashViewSet, CashIssuerViewSet
from wanglibao_favorite.views import FavoriteTrustViewSet, FavoriteFundViewSet, FavoriteFinancingViewSet, \
    FavoriteCashViewSet
from wanglibao_feedback.views import FeedbackViewSet
from wanglibao_fund.views import FundViewSet, FundIssuerViewSet
from wanglibao_hotlist.views import HotTrustViewSet, HotFundViewSet, MobileHotTrustViewSet, \
    MobileHotFundViewSet, MobileMainPageViewSet, MobileMainPageP2PViewSet
from wanglibao_p2p.views import PurchaseP2P, PurchaseP2PMobile, P2PProductViewSet, RecordView, \
    P2PProductDetailView
from wanglibao_pay.views import (CardViewSet, BankCardAddView, BankCardListView, BankCardDelView, 
                            BankListAPIView, YeePayAppPayView, YeePayAppPayCallbackView,
                            YeePayAppPayCompleteView, WithdrawAPIView, FEEAPIView)

from wanglibao_portfolio.views import PortfolioViewSet, ProductTypeViewSet
from wanglibao_preorder.views import PreOrderViewSet
from wanglibao_profile.views import ProfileView
from wanglibao_rest.views import (SendValidationCodeView, SendRegisterValidationCodeView, 
                            UserExisting, RegisterAPIView, IdValidate, AdminIdValidate,
                            WeixinRegisterAPIView, IdValidateAPIView, ClientUpdateAPIView,
                            YTXVoiceCallbackAPIView, SendVoiceCodeAPIView,
                            SendVoiceCodeTwoAPIView, MobileDownloadAPIView, Statistics)


router = DefaultRouter()

router.register(r'trusts', TrustViewSet)
router.register(r'issuers', IssuerViewSet)

router.register(r'bank_financings', BankFinancingViewSet)
router.register(r'banks', BankViewSet)

router.register(r'funds', FundViewSet)
router.register(r'fund_issuers', FundIssuerViewSet)

router.register(r'cashes', CashViewSet)
router.register(r'cash_issuers', CashIssuerViewSet)

router.register(r'portfolios', PortfolioViewSet)
router.register(r'products', ProductTypeViewSet)

router.register(r'hot_trusts', HotTrustViewSet)
router.register(r'hot_funds', HotFundViewSet)
router.register(r'mobile_hot_trusts', MobileHotTrustViewSet)
router.register(r'mobile_hot_funds', MobileHotFundViewSet)
router.register(r'mobile_main', MobileMainPageViewSet)
router.register(r'mobile_main_p2p', MobileMainPageP2PViewSet)

router.register(r'favorite/trusts', FavoriteTrustViewSet)
router.register(r'favorite/funds', FavoriteFundViewSet)
router.register(r'favorite/financings', FavoriteFinancingViewSet)
router.register(r'favorite/cashes', FavoriteCashViewSet)

router.register(r'p2ps', P2PProductViewSet)

router.register(r'pre_orders', PreOrderViewSet)
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'trade_info', TradeInfoViewSet)
router.register(r'banners', BannerViewSet)
router.register(r'users', UserViewSet)

router.register(r'daily_income', DailyIncomeViewSet)

router.register(r'card', CardViewSet)


urlpatterns = patterns(
    '',
    url(r'^register/$', RegisterAPIView.as_view()),
    url(r'^register/wx/$', WeixinRegisterAPIView.as_view()),
    url(r'^change_password/$', ChangePasswordAPIView.as_view()),
    url(r'^reset_password/$', ResetPasswordAPI.as_view()),
    url(r'^phone_validation_code/(?P<phone>\d{11})/$', SendValidationCodeView.as_view()),
    url(r'^phone_validation_code/register/(?P<phone>\d{11})/$', SendRegisterValidationCodeView.as_view()),
    url(r'^phone_validation_code/reset_password/(?P<phone>\d{11})/$', SendValidationCodeView.as_view()),
    url(r'^user_exists/(?P<identifier>[\w\.@]+)/$', UserExisting.as_view()),
    url(r'^profile/', ProfileView.as_view()),
    url(r'^total_income', TotalIncome.as_view()),
    url(r'^p2p/purchase/$', PurchaseP2P.as_view()),
    url(r'^p2p/purchase/mobile/$', PurchaseP2PMobile.as_view()),
    url(r'^p2ps/(?P<product_id>\d+)/records/', RecordView.as_view()),

    # url(r'^p2ps/$', P2PProductListView.as_view()),
    url(r'^p2ps/(?P<pk>[0-9]+)/$', P2PProductDetailView.as_view()),

    url(r'', include(router.urls)),
    #客户端使用,重写
    url(r'^id_validation/$', IdValidateAPIView.as_view()),
    url(r'^bank_card/add/$', BankCardAddView.as_view()),
    url(r'^bank_card/list/$', BankCardListView.as_view()),
    url(r'^bank_card/del/$', BankCardDelView.as_view()),
    url(r'^bank/list/$', BankListAPIView.as_view()),

    url(r'^id_validate/', IdValidate.as_view()),
    url(r'^admin_id_validate/$', AdminIdValidate.as_view()),
    url(r'^admin_send_message/$', AdminSendMessageAPIView.as_view()),

    url(r'^home/$', AccountHomeAPIView.as_view()),
    url(r'^home/p2precord', AccountP2PRecordAPI.as_view()),
    url(r'^home/fundrecord', AccountFundRecordAPI.as_view()),
    url(r'^home/p2passet', AccountP2PAssetAPI.as_view()),
    url(r'^home/fundasset', AccountFundAssetAPI.as_view()),
    url(r'^home/p2p/amortization/(?P<product_id>\d+)', P2PAmortizationAPI.as_view()),

    url(r'^p2p/contract/(?P<product_id>\d+)', UserProductContract.as_view()),
    #url(r'^pay/lianlian/app/deposit/$', LianlianAppPayView.as_view(), name="lianlian-deposit-view"),
    #url(r'^pay/lianlian/app/deposit/callback/$', LianlianAppPayCallbackView.as_view(), name="lianlian-deposit-view"),
    url(r'^withdraw/$', WithdrawAPIView.as_view(), name="withdraw-api-view"),
    url(r'^fee/$', FEEAPIView.as_view(), name="withdraw-api-view"),

    url(r'^pay/yee/app/deposit/$', YeePayAppPayView.as_view(), name="yee-deposit-view"),
    url(r'^pay/yee/app/deposit/callback/$', YeePayAppPayCallbackView.as_view(), name="yee-deposit-callback"),
    url(r'^pay/yee/app/deposit/complete/$', YeePayAppPayCompleteView.as_view(), name="yee-deposit-fcallback"),

    url(r'^client_update/$', ClientUpdateAPIView.as_view()),
    url(r'^ytx/voice_back', YTXVoiceCallbackAPIView.as_view()),
    url(r'^ytx/send_voice_code/$', SendVoiceCodeAPIView.as_view()),
    url(r'^ytx/send_voice_code/2/$', SendVoiceCodeTwoAPIView.as_view()),
    #url(r'^pushtest/$', PushTestView.as_view()),
    url(r'^marketing/tv', Statistics.as_view()),
    url(r'^mobiledownload/$', MobileDownloadAPIView.as_view())
)

urlpatterns += patterns('',
    url(r'^api-token-auth/', 'wanglibao_rest.views.obtain_auth_token'),
    url(r'wrapper/', 'drf_wrapper.views.wrapper_view'),
)

urlpatterns += patterns('',
    url(r'^fund_info/', FundInfoAPIView.as_view()),
)
