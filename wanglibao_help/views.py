#!/usr/bin/env python
# encoding:utf-8

from django.views.generic import TemplateView
from django.http import HttpResponse
from wanglibao_help.models import Topic, Question


class HelpView(TemplateView):
    template_name = 'help.jade'

    def get_context_data(self, **kwargs):
        #topic 帮助中心左侧的栏目
        topics = Topic.objects.order_by("-id").all()
        #question field: title, answer, id
        questions = Question.objects.order_by("-id").all()
        nav = [{"id":"0", "name":u'热门问题'}]
        result = {"0":[]}
        for x in topics:
            nav.append({"id":str(x.id), "name":x.name})
            result[str(x.id)] = []
        for k in questions:
            for m in nav[1:]:
                if k.topic.name == m['name']:
                    result[m["id"]].append(k)
            if k.hotspot:
                result[nav[0]['id']].append(k)
        #nav struct [{"id":"", "name":""}, ]
        #questions struct {"nav中的id":[{"id":"","title":"","answer":""}]}
        return {"nav":nav, "questions":result}
