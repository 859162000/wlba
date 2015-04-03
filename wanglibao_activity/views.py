# -*- coding: utf-8 -*-


from django.views.generic import TemplateView
from wanglibao_activity.models import ActivityTemplates, ActivityImages


class TemplatesFormatTemplate(TemplateView):

    template_name = 'template_one.jade'

    def get_context_data(self, **kwargs):
        template_id = kwargs['id']
        record = ActivityTemplates.objects.filter(id=template_id).first()

        if record:
            if record.is_activity_desc == 2:
                record.desc_img = ActivityImages.objects.filter(id__in=record.desc_img.split(',')).order_by('-priority')

            if record.is_reward == 2:
                record.reward_desc = record.reward_desc.split('|*|')

            if record.is_rule_use == 2:
                record.rule_use = record.rule_use.split('|*|')

            if record.is_rule_activity == 2:
                record.rule_activity = record.rule_activity.split('|*|')

            if record.is_rule_reward == 2:
                record.rule_reward = record.rule_reward.split('|*|')

            if record.location:
                record.logo, record.logo_other = record.logo_other, record.logo

        return {
            'result': record
        }