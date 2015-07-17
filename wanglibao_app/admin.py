#!/usr/bin/env python
# encoding: utf-8

__author__ = 'zhanghe'

from django.contrib import admin
from wanglibao_app.views import RecommendProductManagerView


admin.site.register_view('app/recommend_manager', view=RecommendProductManagerView.as_view(), name=u'设置推荐标的')
