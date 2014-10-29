from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from trust.views import TrustViewSet, IssuerViewSet
from wanglibao_account.views import (UserViewSet, ResetPasswordAPI, FundInfoAPIView,
                            AccountHomeAPIView, AccountP2PRecordAPI, AccountFundRecordAPI, AccountP2PAssetAPI, AccountFundAssetAPI,
                            P2PAmortizationAPI, UserProductContract, ChangePasswordAPIView)
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
    P2PProductDetailView, P2PProductListView
from wanglibao_pay.views import CardViewSet, LianlianAppPayView, LianlianAppPayCallbackView
from wanglibao_portfolio.views import PortfolioViewSet, ProductTypeViewSet
from wanglibao_preorder.views import PreOrderViewSet
from wanglibao_profile.views import ProfileView
from wanglibao_rest.views import (SendValidationCodeView, SendRegisterValidationCodeView, 
            UserExisting, RegisterAPIView, IdValidate, AdminIdValidate,
            WeixinRegisterAPIView)

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
    url(r'^id_validate/', IdValidate.as_view()),
    url(r'^admin_id_validate/', AdminIdValidate.as_view()),

    url(r'^home/$', AccountHomeAPIView.as_view()),
    url(r'^home/p2precord', AccountP2PRecordAPI.as_view()),
    url(r'^home/fundrecord', AccountFundRecordAPI.as_view()),
    url(r'^home/p2passet', AccountP2PAssetAPI.as_view()),
    url(r'^home/fundasset', AccountFundAssetAPI.as_view()),
    url(r'^home/p2p/amortization/(?P<product_id>\d+)', P2PAmortizationAPI.as_view()),

    url(r'^p2p/contract/(?P<product_id>\d+)', UserProductContract.as_view()),
    url(r'^pay/lianlian/app/deposit/$', LianlianAppPayView.as_view(), name="lianlian-deposit-view"),
    url(r'^pay/lianlian/app/deposit/callback/$', LianlianAppPayCallbackView.as_view(), name="lianlian-deposit-view"),
)

urlpatterns += patterns('',
    url(r'^api-token-auth/', 'wanglibao_rest.views.obtain_auth_token'),
    url(r'wrapper/', 'drf_wrapper.views.wrapper_view'),
)

urlpatterns += patterns('',
    url(r'^fund_info/', FundInfoAPIView.as_view()),
)
