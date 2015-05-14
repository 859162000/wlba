# encoding:utf-8
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from django.conf import settings
import admin_views as views

urlpatterns = patterns(
    '',
    # view
    url(r'^weixin/material/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}, name='admin_weixin_material_file'),
    url(r'^weixin/account/manage/(?P<id>\w+)/$', views.WeixinView.as_view(), name='admin_weixin_manage'),
    url(r'^weixin/account/manage/(?P<id>\w+)/mass/$', views.WeixinMassView.as_view(), name='admin_weixin_mass'),
    url(r'^weixin/account/manage/(?P<id>\w+)/reply/$', views.WeixinReplyView.as_view(), name='admin_weixin_reply'),
    url(r'^weixin/account/manage/(?P<id>\w+)/menu/$', views.WeixinMenuView.as_view(), name='admin_weixin_menu'),
    url(r'^weixin/account/manage/(?P<id>\w+)/material/$', views.WeixinMaterialView.as_view(), name='admin_weixin_material'),
    url(r'^weixin/account/manage/(?P<id>\w+)/material/image/(?P<media_id>[\w-]+)/$', views.WeixinMaterialImageView.as_view(), name='admin_weixin_material_image'),
    url(r'^weixin/account/manage/(?P<id>\w+)/customer_service/$', views.WeixinCustomerServiceView.as_view(), name='admin_weixin_customer_service'),
    url(r'^weixin/account/manage/(?P<id>\w+)/customer_service/create/$', views.WeixinCustomerServiceCreateView.as_view(), name='admin_weixin_customer_service_create'),

    # ajax json api
    url(r'^weixin/account/manage/(?P<id>\w+)/material_list.json$', views.WeixinMaterialListJsonApi.as_view(), name='admin_weixin_material_list_json'),
    url(r'^weixin/account/manage/(?P<id>\w+)/customer_service/create.api$', views.WeixinCustomerServiceCreateApi.as_view(), name='admin_weixin_customer_service_create_api'),
    url(r'^weixin/menu/create.api$', views.WeixinMenuCreateApi.as_view(), name='admin_weixin_menu_create_api'),
    url(r'^weixin/menu/delete.api$', views.WeixinMenuDeleteApi.as_view(), name='admin_weixin_menu_delete_api'),
)
