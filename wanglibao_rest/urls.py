from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from trust.views import TrustViewSet, IssuerViewSet
from wanglibao_bank_financing.views import BankFinancingViewSet, BankViewSet
from wanglibao_cash.views import CashViewSet, CashIssuerViewSet
from wanglibao_favorite.views import FavoriteTrustViewSet, FavoriteFundViewSet, FavoriteFinancingViewSet, \
    FavoriteCashViewSet
from wanglibao_fund.views import FundViewSet, FundIssuerViewSet
from wanglibao_hotlist.views import HotTrustViewSet, HotFinancingViewSet, HotFundViewSet
from wanglibao_portfolio.views import PortfolioViewSet, UserPortfolioViewSet, ProductTypeViewSet
from wanglibao_preorder.views import PreOrderViewSet
from wanglibao_rest.views import UserViewSet,  SendValidationCodeView, UserExisting

router = DefaultRouter()
router.register(r'users', UserViewSet)

router.register(r'trusts', TrustViewSet)
router.register(r'issuers', IssuerViewSet)

router.register(r'bank_financings', BankFinancingViewSet)
router.register(r'banks', BankViewSet)

router.register(r'funds', FundViewSet)
router.register(r'fund_issuers', FundIssuerViewSet)

router.register(r'cashes', CashViewSet)
router.register(r'cash_issuers', CashIssuerViewSet)

router.register(r'pre_orders', PreOrderViewSet)

router.register(r'portfolios', PortfolioViewSet)
router.register(r'products', ProductTypeViewSet)
router.register(r'user_portfolios', UserPortfolioViewSet)

router.register(r'hot_trusts', HotTrustViewSet)
router.register(r'hot_financings', HotFinancingViewSet)
router.register(r'hot_funds', HotFundViewSet)

router.register(r'favorite/trusts', FavoriteTrustViewSet)
router.register(r'favorite/funds', FavoriteFundViewSet)
router.register(r'favorite/financings', FavoriteFinancingViewSet)
router.register(r'favorite/cashes', FavoriteCashViewSet)

urlpatterns = patterns(
    '',
    url(r'^phone_validation_code/register/(?P<phone>\d{11})/$', SendValidationCodeView.as_view()),
    url(r'^phone_validation_code/reset_password/(?P<phone>\d{11})/$', SendValidationCodeView.as_view()),
    url(r'^user_exists/(?P<identifier>[\w\.@]+)/$', UserExisting.as_view()),
    url(r'^', include(router.urls)),
)
