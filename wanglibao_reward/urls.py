#!/usr/bin/env python
# encoding:utf-8

from django.conf.urls import url, patterns
import views
from django.contrib.auth.decorators import login_required

urlpatterns = patterns(
    '',
    url(r'^share/(?P<phone_num>\w+)/(?P<openid>[\w,"\-","_"]+)/(?P<order_id>[\w,"_","\-"]+)/(?P<activity>[\w,"_","\-"]+)/$', views.WeixinShareDetailView.as_view(), name='weixin_share_order_detail'),
    url(r'^share/start/$', views.WeixinShareStartView.as_view(), name='weixin_share_order_gift'),
    url(r'^share/end/$', views.WeixinShareEndView.as_view(), name='weixin_share_end'),

    url(r'^weixin/bonus/$', views.WeixinAnnualBonusView.as_view(), name='weixin_annual_bonus'),
    url(r'^weixin/bonus/from_regist/$', views.WeixinAnnualBonusView.as_view(), name='weixin_annual_bonus_from_regist'),

    url(r'^qm_banquet/$', views.QMBanquetTemplate.as_view(), name='qm_banquet'),
    url(r'^new_ameal/$', views.QMBanquetTemplate.as_view(template_name="new_ameal.jade")),
    url(r'^lantern_banquet/$', views.LanternBanquetTemplate.as_view(template_name="festival_two.html")),
    url(r'^spring_reward/$', views.MarchAwardTemplate.as_view(template_name="app_spring_mobilization.jade")),
    url(r"^march_reward/$", views.MarchAwardTemplate.as_view(template_name="spring_mobilization.jade")),
)