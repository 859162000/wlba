# encoding: utf-8

from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from marketing.tasks import send_redpack
from marketing.utils import local_to_utc, paginator_factory
from models import PlayList
from tops import Top
from rest_framework import renderers
from rest_framework.views import APIView
from wanglibao.templatetags.formatters import safe_phone_str


class Investment(TemplateView):
    """ 实时活动打榜页面"""
    template_name = 'day.jade'

    def get_context_data(self, **kwargs):
        now = datetime.now()
        if now.date().__str__() <= '2015-03-23':
            return {
                "top_ten": None,
                "top_len": 0
            }

        day_tops = _get_top_records()
        return {
            "top_ten": day_tops,
            "top_len": len(day_tops)
        }


class InvestmentHistory(APIView):
    """ 查询历史榜单 """
    permission_classes = ()

    def post(self, request):
        day = request.DATA.get('day')
        if day <= '2015-03-23':
            result = [{
                "tops": None,
                "tops_len": 0
            }]
        else:
            day_tops = _get_top_records(datetime.strptime(day, '%Y-%m-%d'), amount_min=30000)
            for tmp in day_tops:
                if 'phone' in tmp:
                    tmp['phone'] = safe_phone_str(tmp['phone'])
            result = [{
                "tops": day_tops,
                "tops_len": len(day_tops)
            }]
        return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))


def _get_top_records(day=None, amount_min=None):
    if day is None:
        day = datetime.now()
    top = Top(limit=10)
    if amount_min:
        return top.day_tops_activate(day, amount_min=amount_min)
    else:
        return top.day_tops_activate(day)


class InvestmentRewardView(TemplateView):
    """ 日累计投资打榜活取奖励
    """
    template_name = 'investment_reward.jade'

    def _activity_rule(self, cat='investment'):
        """ 活动规则列表
        (最小金额， 最大金额，发放红包开始名次，发放红包截止名次，发放红包金额，递减递增要求，活动id)

        根据最大金额和最小金额查询投资人排序
        根据发放红包的开始名次和截止名次发放红包奖金,遵守前包括后不包括原则
        红包发放规则当为（-100）时表示红包奖金依次递减
        """
        rules = None
        if cat == 'investment':
            rules = (
                (60000, None, None, 10, 1000, -100, u'每日打榜红包_1000-100', ),
                (60000, None, 10, None, 60, None, u'每日打榜红包_60'),
                (50000, 59999, None, None, 50, None, u'每日打榜红包_50',),
                (40000, 49999, None, None, 40, None, u'每日打榜红包_40',),
                (30000, 39999, None, None, 30, None, u'每日打榜红包_30',),
                (20000, 29999, None, None, 20, None, u'每日打榜红包_20',),
                (10000, 19999, None, None, 10, None, u'每日打榜红包_10',),
            )
        elif cat == 'investment_three':
            rules = (
                (30000, None, None, 10, 1000, -100, u'每日打榜红包_1000-100', ),
                (30000, None, 10, None, 60, None, u'每日打榜红包_60'),
            )

        return rules

    def get_context_data(self, **kwargs):
        """ 根据条件查询累计投资
        """
        status, message, data = self._filter_rule(**kwargs)
        if not status:
            return {"message": message}

        day, rule = data['day'], data['rule']
        amount_min, amount_max, start, end, reward, exchange, redpack = rule

        play_list = PlayList.objects.filter(
            play_at=local_to_utc(day, 'min'),
            redpackevent=redpack
        )

        if play_list.count() > 0:
            message = u'统计日期已经存在统计记录！'
        else:
            if not self._generate_records(day=day, rule=rule):
                message = u'统计记录生成失败！'

        if not message: message = u'统计结束！'
        return self._return_format(message, day, redpack)

    def _query_play_list(self, day, redpack):
        play_list = PlayList.objects.filter(
            play_at=local_to_utc(day, 'min'),
            redpackevent=redpack
        ).select_related(
            'user__wanglibaouserprofile'
        ).order_by('-amount', 'ranking', 'created_at')
        return play_list

    def _filter_rule(self, cat=None, request=None):
        """将输入规则和默认规则比对"""
        data = dict.fromkeys(['day', 'rule'])

        if cat == 'post':
            day = request.POST.get('day', '')
            redpack = request.POST.get('redpack', '')
        else:
            day = self.request.GET.get('day', '')
            redpack = self.request.GET.get('redpack', '')

        if not redpack: return False, u'请选择红包类型', data

        if day:
            try:
                data['day'] = datetime.strptime(day, '%Y-%m-%d')
            except:
                return False, u'日期格式有误，请重新输入！', data
        else:
            data['day'] = datetime.now()

        # 不使用默认规则，则使用动态统计规则
        # rules = self._activity_rule(cat='investment')
        rules = self._activity_rule(cat='investment_three')
        if not rules: return False, u'目前不支持输入的活动类型', data
        rule = filter(lambda x: x[6] == redpack, rules)
        if rule:
            data['rule'] = rule[0]
            return True, None, data

        return False, u'统计条件不合法', data

    def _return_format(self, message, day, redpack):
        play_list = self._query_play_list(day, redpack)
        play_list_checked = play_list.filter(checked_status=2)
        return {
            "message": message,
            "result": paginator_factory(obj=play_list, page=self.request.GET.get('page'), limit=100),
            "day": day.date().__str__(),
            "redpack": redpack,
            "amount_all": play_list.aggregate(reward=Sum('reward')) if play_list else 0.00,
            "amount_redpack": play_list_checked.aggregate(reward=Sum('reward')) if play_list_checked else 0.00
        }

    @staticmethod
    def _generate_records(day, rule):
        """ 统计生产新数据
        """
        amount_min, amount_max, start, end, reward, exchange, redpack = rule
        tops = Top(limit=0)
        records = tops.day_tops_first_come_first_served(
            day=day,
            amount_min=amount_min,
            amount_max=amount_max
        )[start: end]

        play_set_list = []
        n = 0
        for record in records:
            play = PlayList()
            play.play_at = local_to_utc(day, source_time='min')
            play.user = User.objects.get(id=record['user'])
            play.amount = record['amount_sum']
            reward_user = reward + (n * exchange) if exchange else reward
            play.reward = reward_user
            play.redpackevent = redpack
            play.ranking = n + 1
            if amount_min: play.amount_min = amount_min
            if amount_max: play.amount_max = amount_max
            if start: play.start = start
            if end: play.end = end
            play_set_list.append(play)
            n += 1

        if play_set_list:
            PlayList.objects.bulk_create(play_set_list)
        return True

    def post(self, request, **kwargs):
        """ 审核发放红包 """
        status, message, data = self._filter_rule(cat='post', request=request)

        if not status: return self.render_to_response({"message": message})

        day, rule = data['day'], data['rule']
        amount_min, amount_max, start, end, reward, exchange, redpack = rule

        records = self._query_play_list(day=day, redpack=redpack)
        if records.count() == 0:
            message = u'不存在需要审核数据，请检查操作流程是否正确！'
            return self.render_to_response(self._return_format(message, day, redpack))
        if records.filter(checked_status__in=[1, 2]).count() > 0:
            message = u'此规则已经审核，不允许再次审核！'
            return self.render_to_response(self._return_format(message, day, redpack))

        check_button = request.POST.get('check_button')
        if check_button == '1':
            # 上线前打开控制
            # if datetime.now().date() <= day.date():
            #     message = u'未到日终，不允许审核发放红包！'
            #     return self.render_to_response(self._return_format(message, day, redpack))

            records.filter(checked_status=0).update(checked_status=1)
            send_redpack.apply_async(kwargs={
                "day": day.date().__str__(),
                "desc": redpack,
                "rtype": "activity"
            })
            message = u'审核通过完成，稍等查询红包发放结果！'
        elif check_button == '2':
            records.filter(checked_status=0).delete()
            message = u'审核未通过完成，将统计记录清除！'

        return self.render_to_response({
            "message": message,
            "day": day if isinstance(day, str) else day.date().__str__()
        })

    @method_decorator(permission_required('marketing.change_sitedata', login_url='/' + settings.ADMIN_ADDRESS))
    def dispatch(self, request, *args, **kwargs):
        return super(InvestmentRewardView, self).dispatch(request, *args, **kwargs)
