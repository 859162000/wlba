from django.conf.urls import patterns, include, url
from django.contrib.auth.models import User, Group, Permission, ContentType
from rest_framework import viewsets, routers
from trust.models import Trust, Issuer

from django.contrib import admin
admin.autodiscover()


class UserViewSet(viewsets.ModelViewSet):
    model = User


class GroupViewSet(viewsets.ModelViewSet):
    model = Group


class PermissionViewSet(viewsets.ModelViewSet):
    model = Permission


class ContentTypeViewSet(viewsets.ModelViewSet):
    model = ContentType


class TrustViewSet(viewsets.ModelViewSet):
    model = Trust


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
    url(r'^', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
