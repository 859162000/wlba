# encoding:utf-8
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from django.conf import settings
import admin_views as views

urlpatterns = patterns(
    '',
    # view
    url(r'^weixin/material/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}, name='admin_weixin_material_file'),
    url(r'^weixin/account/manage/(?P<id>\d+)/$', views.WeixinView.as_view(), name='admin_weixin_manage'),
    url(r'^weixin/account/mass/$', views.WeixinMassView.as_view(), name='admin_weixin_mass'),
    url(r'^weixin/account/reply/$', views.WeixinReplyView.as_view(), name='admin_weixin_reply'),
    url(r'^weixin/account/menu/$', views.WeixinMenuView.as_view(), name='admin_weixin_menu'),
    url(r'^weixin/account/material/$', views.WeixinMaterialView.as_view(), name='admin_weixin_material'),
    url(r'^weixin/account/material/image/(?P<media_id>[\w-]+)/$', views.WeixinMaterialImageView.as_view(), name='admin_weixin_material_image'),
    url(r'^weixin/account/customer_service/$', views.WeixinCustomerServiceView.as_view(), name='admin_weixin_customer_service'),
    url(r'^weixin/account/customer_service/create/$', views.WeixinCustomerServiceCreateView.as_view(), name='admin_weixin_customer_service_create'),

    # ajax json api
    url(r'^weixin/account/material_list.json$', views.WeixinMaterialListJsonApi.as_view(), name='admin_weixin_material_list_json'),
    url(r'^weixin/account/customer_service.api$', views.WeixinCustomerServiceApi.as_view(), name='admin_weixin_customer_service_api'),
    url(r'^weixin/account/menu.api$', views.WeixinMenuApi.as_view(), name='admin_weixin_menu_api'),
)
