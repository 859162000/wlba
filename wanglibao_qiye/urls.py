# encoding:utf-8
from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.decorators import login_required
from .views import (EnterpriseProfileCreateApi, QiYeIndex, QiYeInfo, EnterpriseProfileUploadApi,
                    EnterpriseProfileUpdateApi, GetEnterpriseUserProfileApi, EnterpriseProfileEditView,
                    EnterpriseProfileIsExistsApi)



urlpatterns = patterns(
    '',
    url(r'^login/', QiYeIndex.as_view(), name='qiye index'),
    url(r'^info/', login_required(QiYeInfo.as_view(),
                                  login_url='/qiye/login/'), name='qiye info'),

    # 企业理财
    url(r'profile/extra/$', login_required(EnterpriseProfileUploadApi.as_view(), login_url='/qiye/login/')),
    url(r'profile/create/$', login_required(EnterpriseProfileCreateApi.as_view(), login_url='/qiye/login/')),
    url(r'profile/update/$', login_required(EnterpriseProfileUpdateApi.as_view(), login_url='/qiye/login/')),
    url(r'profile/get/$', login_required(GetEnterpriseUserProfileApi.as_view(), login_url='/qiye/login/')),
    url(r'profile/edit/$', login_required(EnterpriseProfileEditView.as_view(),
                                          login_url='/qiye/login/'), name='qiye update'),
    url(r'profile/exists/$', login_required(EnterpriseProfileIsExistsApi.as_view(), login_url='/qiye/login/')),
)

