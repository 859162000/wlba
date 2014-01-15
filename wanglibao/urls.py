from django.conf.urls import patterns, include, url
from django.contrib.auth.models import User, Group, Permission, ContentType
from rest_framework import viewsets, routers
from rest_framework.renderers import UnicodeJSONRenderer
from rest_framework.serializers import HyperlinkedModelSerializer
from trust.models import Trust, Issuer

from django.contrib import admin
admin.autodiscover()


class UserSerializer (HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'first_name', 'last_name', 'email', 'date_joined')


class UserViewSet(viewsets.ModelViewSet):
    model = User
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    model = Group


class PermissionViewSet(viewsets.ModelViewSet):
    model = Permission


class ContentTypeViewSet(viewsets.ModelViewSet):
    model = ContentType


class TrustViewSet(viewsets.ModelViewSet):
    model = Trust
    filter_fields = ('name', 'short_name', 'expected_earning_rate')

class IssuerViewSet(viewsets.ModelViewSet):
    model = Issuer


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'contentTypes', ContentTypeViewSet)
router.register(r'trusts', TrustViewSet)
router.register(r'issuers', IssuerViewSet)


urlpatterns = patterns(
    '',
    url(r'^register', 'trust.views.register'),
    url(r'^', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^accounts/', include('registration.backends.default.urls')),
)
