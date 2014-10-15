#!/usr/bin/env python
# encoding:utf-8

from django.views.generic import TemplateView
from django.http import HttpResponse
from wanglibao_help.models import Topic, Question


class HelpView(TemplateView):
    template_name = 'help.jade'

    def get(self, request):
        #topic 帮助中心左侧的栏目
        topics = Topic.objects.order_by("-id").all()
        #question field: title, answer,
        questions = Question.objects.order_by("-id").all()
        hot = '热门问题'
        result = {hot:[]}
        nav = [hot]
        for x in topics:
            nav.append(x.name)
            result[x.name] = []
        for k in questions:
            if k.topic.name in result:
                result[k.topic.name].append(k)
            if k.hotspot:
                result[hot].append(k)
        return {"nav":nav, "questions":result}
