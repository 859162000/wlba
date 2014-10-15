#!/usr/bin/env python
# encoding:utf-8

from django.contrib import admin
from wanglibao_help.models import Topic, Question

class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic', 'title', 'answer', 'hotspot')


admin.site.register(Topic, TopicAdmin)
admin.site.register(Question, QuestionAdmin)
