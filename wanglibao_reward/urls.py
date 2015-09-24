#!/usr/bin/env python
# encoding:utf-8

from django.conf.urls import url, patterns
import views
urlpatterns = patterns(
    '',
    url(r'^share/(?P<phone_num>\w+)/(?P<openid>[\w,"\-","_"]+)/(?P<order_id>[\w,"_","\-"]+)/(?P<activity>[\w,"_","\-"]+)/$', views.WeixinShareDetailView.as_view(), name='weixin_share_order_detail'),
    url(r'^share/start/$', views.WeixinShareStartView.as_view(), name='weixin_share_order_gift'),
    url(r'^share/end/$', views.WeixinShareEndView.as_view(), name='weixin_share_end'),
)
