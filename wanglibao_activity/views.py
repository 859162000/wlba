# -*- coding: utf-8 -*-

from django.views.generic import TemplateView
from django.http import Http404, HttpResponse, HttpResponseRedirect
from wanglibao_activity.models import ActivityTemplates, ActivityImages, ActivityShow
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from weixin.views import _generate_ajax_template
from .utils import get_queryset_paginator
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger

class TemplatesFormatTemplate(TemplateView):
    def get_context_data(self, **kwargs):

        template_id = kwargs['id']
        record = ActivityTemplates.objects.filter(id=template_id).first()

        include = {
            "1": "include/activity_time.jade",
            "2": "include/activity_prize.jade",
#            "3": "include/activity_friends.jade",
#            "4": "include/activity_process.jade",
            "5": "include/activity_use_rule.jade",
            "6": "include/activity_act_rule.jade",
            "7": "include/activity_prize_rule.jade",
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


class PcActivityShowHomeView(TemplateView):
    template_name = 'area.jade'

    def get_context_data(self, **kwargs):
        activity_list = ActivityShow.objects.filter(link_is_hide=False,
                                                    is_pc=True,
                                                    start_at__lte=timezone.now(),
                                                    end_at__gt=timezone.now()
                                                    ).select_related('activity').\
                                                    order_by('-activity__priority')

        banner = {}
        try:
            banner['main'] = activity_list.filter(banner_pos='main')[0].pc_banner
        except Exception:
            banner['main'] = ''

        try:
            banner['left'] = activity_list.filter(banner_pos='second_left')[0].pc_banner
        except Exception:
            banner['left'] = ''

        try:
            banner['right'] = activity_list.filter(banner_pos='second_right')[0].pc_banner
        except Exception:
            banner['right'] = ''

        limit = 6
        activity_list = get_queryset_paginator(activity_list, 1, limit)

        return {
            'banner': banner,
            'results': activity_list[:limit]
        }


class ActivityListPC(APIView):
    permission_classes = ()

    @property
    def allowed_methods(self):
        return ['GET', 'POST']

    def get(self, request):
        template_name = 'include/ajax/area_ajax.jade'

        activity_list = ActivityShow.objects.filter(link_is_hide=False,
                                                    is_pc=True,
                                                    start_at__lte=timezone.now(),
                                                    end_at__gt=timezone.now(),
                                                    ).select_related('activity').\
                                                    order_by('-activity__priority')

        category = request.GET.get('category', 'all')
        if category:
            activity_list = activity_list.filter(category=category)

        page = request.GET.get('page', 1)
        pagesize = request.GET.get('pagesize', 6)
        page = int(page)
        pagesize = int(pagesize)

        paginator = Paginator(activity_list, pagesize)

        try:
            activity_list = paginator.page(page)
        except PageNotAnInteger:
            activity_list = paginator.page(1)
        except Exception:
            activity_list = paginator.page(paginator.num_pages)

        all_page = paginator.num_pages
        data_count = paginator.count
        html_data = _generate_ajax_template(activity_list, template_name)

        return Response({
            'html_data': html_data,
            'page': page,
            'all_page': all_page,
            'data_count': data_count
        })


# class ActivityDetailView(TemplateView):
#     def get_context_data(self, platform, id, **kwargs):
#         context = super(ActivityDetailView, self).get_context_data(**kwargs)
#         activity_show = None
#
#         try:
#             if platform == 'pc':
#                 activity_show = ActivityShow.objects.get(pk=id, is_pc=True, link_is_hide=False,
#                                                          start_at_lte=timezone.now(),
#                                                          end_at_gt=timezone.now())
#                 self.template_name = activity_show.pc_template
#             elif platform == 'app':
#                 activity_show = ActivityShow.objects.get(pk=id, is_app=True, link_is_hide=False,
#                                                          start_at_lte=timezone.now(),
#                                                          end_at_gt=timezone.now())
#                 self.template_name = activity_show.app_template
#         except Exception:
#             raise Http404(u'您查找的活动页面不存在')
#
#         context.update({
#             'activity': activity_show.activity,
#         })
#
#         return context
