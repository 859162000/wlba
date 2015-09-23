#!/usr/bin/env python
# encoding:utf-8

from django.conf.urls import url, patterns
import views
urlpatterns = patterns(
    '',
    url(r'^share/(?P<phone_num>\d+)/(?P<openid>\d+)/(?P<order_id>\d+)/(?P<activity>[\w,"_"]+)/$', views.WeixinShareDetailView.as_view(), name='weixin_share_order_detail'),
    url(r'^share/start/$', views.WeixinShareStartView.as_view(), name='weixin_share_order_gift'),
    url(r'^share/end/$', views.WeixinShareEndView.as_view(), name='weixin_share_end'),
)
