from django.conf.urls import patterns, include, url
from django.contrib.auth.models import User, Group, Permission, ContentType
from rest_framework import viewsets, routers

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

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'contentTypes', ContentTypeViewSet)


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wanglibao.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^', include(router.urls)),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
