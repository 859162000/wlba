# encoding:utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.decorators import login_required
from .views import EnterpriseUserProfileApi, EnterpriseUserProfileExtraApi


urlpatterns = patterns(
    '',
    # url(r'^login/', QiYeIndex.as_view(), name='qiye index'),
    # url(r'^info/', QiYeIndex.as_view(), name='qiye index'),

    # 企业理财
    url(r'enterprise/extra$', EnterpriseUserProfileExtraApi.as_view()),
    url(r'enterprise/$', EnterpriseUserProfileApi.as_view()),
)

