from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from trust.views import TrustViewSet, IssuerViewSet
from wanglibao_bank_financing.views import BankFinancingViewSet, BankViewSet
from wanglibao_fund.views import FundViewSet, FundIssuerViewSet
from wanglibao_hotlist.views import HotTrustViewSet
from wanglibao_portfolio.views import PortfolioViewSet, UserPortfolioViewSet, ProductTypeViewSet
from wanglibao_preorder.views import PreOrderViewSet
from wanglibao_rest.views import UserViewSet,  PhoneValidateView, RegisterByPhone, UserExisting

router = DefaultRouter()
router.register(r'users', UserViewSet)

router.register(r'trusts', TrustViewSet)
router.register(r'issuers', IssuerViewSet)

router.register(r'bank_financings', BankFinancingViewSet)
router.register(r'banks', BankViewSet)

router.register(r'funds', FundViewSet)
router.register(r'fund_issuers', FundIssuerViewSet)

router.register(r'pre_orders', PreOrderViewSet)

router.register(r'portfolios', PortfolioViewSet)
router.register(r'products', ProductTypeViewSet)
router.register(r'user_portfolios', UserPortfolioViewSet)

router.register(r'hot_trusts', HotTrustViewSet)


urlpatterns = patterns(
    '',
    # TODO add format check on phone
    url(r'^phone_validation_code/(?P<phone>\d{11})/$', PhoneValidateView.as_view()),
    url(r'^user_existing/$', UserExisting.as_view()),
    url(r'^', include(router.urls)),
)
