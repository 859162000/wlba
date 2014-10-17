#!/usr/bin/env python
# encoding:utf-8

from django.views.generic import TemplateView
from django.template.defaulttags import register
from wanglibao_help.models import Topic, Question


class HelpView(TemplateView):
    template_name = 'help.jade'

    @register.filter(name="lookup")
    def get_item(dictionary, key):
        return dictionary.get(key)

    def get_context_data(self, **kwargs):
        #topic 帮助中心左侧的栏目
        topics = Topic.objects.order_by("-id").all()
        #question field: title, answer, id
        questions = Question.objects.order_by("-id").all()
        nav = [{"id":"0", "name":u'热门问题'}]
        result = {"0":[]}
        for x in topics:
            nav.append({"id":str(x.id), "name":x.name, "questions": x.question_set.get_queryset()})
            result[str(x.id)] = []
        for k in questions:
            for m in nav[1:]:
                if k.topic.name == m['name']:
                    result[m["id"]].append(k)
            if k.hotspot:
                result[nav[0]['id']].append(k)

        map = dict((obj.get('id'), obj.get('name')) for obj in nav)

        #nav struct [{"id":"", "name":""}, ]
        #questions struct {"nav中的id":[{"id":"","title":"","answer":""}]}
        return {"nav":nav, "questions":result, 'map': map}
