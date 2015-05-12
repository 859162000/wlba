# encoding:utf-8
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from django.conf import settings
import admin_views as views

urlpatterns = patterns(
    '',
    # view
    url(r'^weixin/account/manage/(?P<id>\w+)/$', views.WeixinView.as_view(), name='weixin_manage'),
    url(r'^weixin/account/manage/(?P<id>\w+)/mass/$', views.WeixinMassView.as_view(), name='weixin_mass'),
    url(r'^weixin/account/manage/(?P<id>\w+)/reply/$', views.WeixinReplyView.as_view(), name='weixin_reply'),
    url(r'^weixin/account/manage/(?P<id>\w+)/menu/$', views.WeixinMenuView.as_view(), name='weixin_menu'),
    url(r'^weixin/account/manage/(?P<id>\w+)/material/$', views.WeixinMaterialView.as_view(), name='weixin_material'),
    url(r'^weixin/material/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}, name='weixin_material_file'),
    url(r'^weixin/account/manage/(?P<id>\w+)/material/image/(?P<media_id>[\w-]+)/$', views.WeixinMaterialImageView.as_view(), name='weixin_material_image'),

    # ajax json api
    url(r'^weixin/account/manage/(?P<id>\w+)/material_list.json$', views.WeixinMaterialListJsonApi.as_view(), name='weixin_material_list_json'),
)
