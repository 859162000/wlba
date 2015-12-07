# encoding:utf-8
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from django.conf import settings
import admin_views as views
import manage_views

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
    url(r'^weixin/account/api/material_list/$', views.WeixinMaterialListJsonApi.as_view(), name='admin_weixin_material_list_json'),
    url(r'^weixin/account/api/customer_service/$', views.WeixinCustomerServiceApi.as_view(), name='admin_weixin_customer_service_api'),
    url(r'^weixin/account/api/menu/$', views.WeixinMenuApi.as_view(), name='admin_weixin_menu_api'),
)

# 微信管理后台
urlpatterns += patterns(
    '',
    # view
    url(r'^weixin/manage/$', manage_views.IndexView.as_view(), name='wx_manage_index'),
    url(r'^weixin/manage/account/(?P<account_key>\w+)/$', manage_views.AccountView.as_view(), name='wx_manage_account'),
    url(r'^weixin/manage/menu/$', manage_views.MenuView.as_view(), name='wx_manage_menu'),
    url(r'^weixin/manage/material/$', manage_views.MaterialView.as_view(), name='wx_manage_material'),
    url(r'^weixin/manage/material/img/(?P<media_id>[\w_-]+)/$', manage_views.MaterialImageView.as_view(), name='wx_manage_material_image'),

    # api
    url(r'^weixin/manage/api/menu/$', manage_views.MenuAPI.as_view(), name='wx_manage_menu_api'),
    url(r'^weixin/manage/api/materials/$', manage_views.MaterialListAPI.as_view(), name='wx_manage_material_list_api'),
    url(r'^weixin/manage/api/materials/count/$', manage_views.MaterialCountAPI.as_view(), name='wx_manage_material_count_api'),
    url(r'^weixin/manage/api/materials/(?P<media_id>\w+)/$', manage_views.MaterialDetailAPI.as_view(), name='wx_manage_material_detail_api'),
)
