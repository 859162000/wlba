# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from django.http.response import HttpResponse
from mock_generator import MockGenerator

class GennaeratorCode(TemplateView):
    template_name = 'gennerator_code.jade'

    def post(self, request):

        try:
            counts = int(request.POST.get('counts'))
        except:
            message = u'请输入合法的数字'
        else:

            MockGenerator.generate_codes(counts)
            message = u'生成 %s 条邀请码' % counts
        return HttpResponse({
            message
        })
