#!/usr/bin/env python
# encoding:utf-8

from django.conf.urls import patterns, url

from wanglibao_rest.views import (BidHasBindingForChannel, CoopDataDispatchApi, RenRenLiQueryApi, TanLiuLiuInvestmentQuery)


urlpatterns = patterns(
    '',
    # 判断bid是否已经绑定渠道
    url(r'^has_binding/(?P<channel_code>[a-z0-9A-Z_]*)/(?P<bid>[a-z0-9A-Z_]*)/$', BidHasBindingForChannel.as_view()),

    # 渠道中心数据调度接口
    url(r'^dispatch/$', CoopDataDispatchApi.as_view()),

    # 人人利查询接口
    url(r'^renrenli/query/$', RenRenLiQueryApi.as_view()),

    # 弹66用户投资记录查询接口
    url(r'^tanliuliu/query/$', TanLiuLiuInvestmentQuery.as_view()),
)
