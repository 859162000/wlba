#!/usr/bin/env python
# encoding:utf-8

from django.conf.urls import patterns, url

from wanglibao_rest.views import (BidHasBindingForChannel, AccessUserExistsApi, CoopDataDispatchApi,
                                  RenRenLiQueryApi)


urlpatterns = patterns(
    '',
    # 判断bid是否已经绑定渠道
    url(r'^has_binding/(?P<channel_code>[a-z0-9A-Z_]*)/(?P<bid>[a-z0-9A-Z_]*)/$', BidHasBindingForChannel.as_view()),

    # 判断手机号是否已经绑定渠道或被注册
    url(r'^access_user/exists/$', AccessUserExistsApi.as_view()),

    # 渠道中心数据调度接口
    url(r'^dispatch/$', CoopDataDispatchApi.as_view()),

    # 人人利查询接口
    url(r'^renrenli/query/$', RenRenLiQueryApi.as_view()),
)
