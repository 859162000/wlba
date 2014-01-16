from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from wanglibao_rest.views import UserViewSet, TrustViewSet, IssuerViewSet, PhoneValidateView, RegisterByPhone

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'trusts', TrustViewSet)
router.register(r'issuers', IssuerViewSet)

urlpatterns = patterns(
    '',
    url(r'^phonecode$', PhoneValidateView.as_view()),
    url(r'^register_by_phone$', RegisterByPhone.as_view()),
    url(r'^', include(router.urls)),
)
