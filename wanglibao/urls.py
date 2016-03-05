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
)

handler500 = 'wanglibao.views.server_error'
