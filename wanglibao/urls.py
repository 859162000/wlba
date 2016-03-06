# -*- coding: utf-8 -*-

from adminplus.sites import AdminSitePlus
from django.conf.urls import patterns, include, url

from django.contrib import admin
from wanglibao import settings

admin.site = AdminSitePlus()
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^' + settings.ADMIN_ADDRESS + '/', include(admin.site.urls)),
    url(r'^api/', include('wanglibao_rest.urls')),
    url(r'^oauth2/', include('wanglibao_oauth2.urls', namespace='oauth2')),
)

handler500 = 'wanglibao.views.server_error'
