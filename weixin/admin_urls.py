# encoding:utf-8
from __future__ import unicode_literals
from django.conf.urls import patterns, url
import admin_views as views

urlpatterns = patterns(
    '',
    url(r'^weixin/account/manage/(?P<id>\w+)/$', views.WeixinView.as_view(), name='weixin_manage'),
    url(r'^weixin/account/manage/(?P<id>\w+)/mass/$', views.WeixinMassView.as_view(), name='weixin_mass'),
    url(r'^weixin/account/manage/(?P<id>\w+)/reply/$', views.WeixinReplyView.as_view(), name='weixin_reply'),
    url(r'^weixin/account/manage/(?P<id>\w+)/menu/$', views.WeixinMenuView.as_view(), name='weixin_menu'),
    url(r'^weixin/account/manage/(?P<id>\w+)/material/$', views.WeixinMaterialView.as_view(), name='weixin_material'),
)
