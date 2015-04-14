# -*- coding: utf-8 -*-


from django.views.generic import TemplateView
from wanglibao_activity.models import ActivityTemplates, ActivityImages


class TemplatesFormatTemplate(TemplateView):
    def get_context_data(self, **kwargs):

        template_id = kwargs['id']
        record = ActivityTemplates.objects.filter(id=template_id).first()

        include = {
            "1": "include/activity_time.jade",
            "2": "include/activity_prize.jade",
            "3": "include/activity_friends.jade",
            "4": "include/activity_process.jade",
            "5": "include/activity_use_rule.jade",
            "6": "include/activity_prize_rule.jade",
            "7": "include/activity_act_rule.jade",
            "8": "include/activity_earning_one.jade",
            "9": "include/activity_earning_two.jade",
            "10": "include/activity_earning_three.jade",
            "11": "include/activity_earning_four.jade"
        }

        sequence, sequence_one, sequence_two, module_background = None, None, None, None
        if record:
            # 活动模块
            if record.is_activity_desc == 2:
                if record.desc_img:
                    id_list = map(lambda x: x.strip(), record.desc_img.split(','))
                    record.desc_img = ActivityImages.objects.filter(id__in=id_list)
                    """
                    # the first method, don't use it
                    ordering = "FIELD(`id`, %s)" % ','.join(str(k) for k in id_list)
                    record.desc_img = record.desc_img.extra(select={'ordering': ordering}, order_by=('ordering',))
                    """
                    # the second method
                    record.desc_img = list(record.desc_img)
                    record.desc_img.sort(key=lambda x: id_list.index(str(x.id)))
            # 奖品发放模块
            if record.is_reward and record.is_reward in (3, 4):
                id_list = map(lambda x: x.strip(), record.reward_img.split(','))
                record.reward_img = ActivityImages.objects.filter(id__in=id_list)
                """
                # the first method, don't use it
                ordering = "FIELD(`id`, %s)" % ','.join(str(k) for k in id_list)
                record.reward_img.extra(select={'ordering': ordering}, order_by=('ordering',))
                """
                # the second method
                record.reward_img = list(record.reward_img)
                record.reward_img.sort(key=lambda x: id_list.index(str(x.id)))

                if record.is_reward == 3:
                    record.reward_desc = map(lambda x: x.strip(), record.reward_img.first().desc_one.split('|*|'))
            # 规则模块
            if record.is_rule_use == 2:
                record.rule_use = map(lambda x: x.strip(), record.rule_use.split('|*|'))

            if record.is_rule_activity == 2:
                record.rule_activity = map(lambda x: x.strip(), record.rule_activity.split('|*|'))

            if record.is_rule_reward == 2:
                record.rule_reward = map(lambda x: x.strip(), record.rule_reward.split('|*|'))
            # logo模块位置调整
            if record.location:
                record.logo, record.logo_other = record.logo_other, record.logo

            # 自定义模块
            if record.is_diy:
                record.diy_img = ActivityImages.objects.filter(id=record.diy_img.strip())
                if record.diy_img:
                    record.diy_desc = map(lambda x: x.strip(), record.diy_img.first().desc_one.split('|*|'))
            # 新手投资模块描述
            record.teacher_desc = map(lambda x: x.strip(), record.teacher_desc.split('|*|'))
            record.teacher_desc.extend(['' for n in range(5-len(record.teacher_desc))])

            # 根据序号活取各个加载模块
            if record.models_sequence:
                record.models_sequence = map(lambda x: x.strip(), record.models_sequence.split(','))

            # 同蓝图控制
            if record.is_background:
                module_background = include.get(record.background_location)
                location = record.models_sequence.index(record.background_location)
                sequence_one = [include.get(key) for key in record.models_sequence[:location]]
                sequence_two = [include.get(key) for key in record.models_sequence[location+1:]]

            if record.models_sequence:
                sequence = [include.get(key) for key in record.models_sequence]

        return {
            'result': record,
            'sequence': sequence,
            'module_background': module_background,
            'sequence_one': sequence_one,
            'sequence_two': sequence_two,
        }