# encoding:utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.decorators import login_required
from views import QiYeIndex, QiYeInfo


urlpatterns = patterns(
    '',
    url(r'^login/', QiYeIndex.as_view(), name='qiye index'),
    url(r'^info/', QiYeInfo.as_view(), name='qiye info'),
)

