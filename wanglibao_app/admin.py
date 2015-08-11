#!/usr/bin/env python
# encoding: utf-8

__author__ = 'zhanghe'

from django.contrib import admin
from wanglibao_app.views import RecommendProductManagerView, AppIncomeMiscTemplateView


admin.site.register_view('app/recommend_manager', view=RecommendProductManagerView.as_view(), name=u'设置推荐标的')
admin.site.register_view('app/income_misc', view=AppIncomeMiscTemplateView.as_view(), name=u'设置收益比例参数')

