from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from wanglibao_hotlist.views import HotTrustViewSet
from wanglibao_portfolio.views import PortfolioViewSet, UserPortfolioViewSet
from wanglibao_preorder.views import PreOrderViewSet
from wanglibao_rest.views import UserViewSet, TrustViewSet, IssuerViewSet, PhoneValidateView, RegisterByPhone

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'trusts', TrustViewSet)
router.register(r'issuers', IssuerViewSet)

router.register(r'pre_order', PreOrderViewSet)

router.register(r'portfolio', PortfolioViewSet)
router.register(r'user_portfolio', UserPortfolioViewSet)

router.register(r'hot_trusts', HotTrustViewSet)

urlpatterns = patterns(
    '',
    url(r'^phonecode$', PhoneValidateView.as_view()),
    url(r'^register_by_phone$', RegisterByPhone.as_view()),
    url(r'^', include(router.urls)),
)
