# -*- coding: utf-8 -*-


from django.views.generic import TemplateView
from wanglibao_activity.models import ActivityTemplates, ActivityImages


class TemplatesFormatTemplate(TemplateView):

    template_name = 'lx.jade'

    def get_context_data(self, **kwargs):
        template_id = kwargs['id']
        print 'template_id>>>', template_id
        record = ActivityTemplates.objects.filter(id=template_id).first()
        if record:
            pass

        return {
            'result': None,
            'banner': record.banner,
            'is_login': record.is_login,
        }