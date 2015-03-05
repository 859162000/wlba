# encoding:utf-8
import json
import decimal
import pytz
from datetime import date, timedelta, datetime
from collections import defaultdict
from decimal import Decimal, ROUND_DOWN

from django.db.models import Count, Sum
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator, PageNotAnInteger
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from wanglibao_p2p.models import P2PRecord
from django.views.generic import TemplateView
from django.http.response import HttpResponse
from mock_generator import MockGenerator
from django.conf import settings
from django.db.models.base import ModelState
from wanglibao_sms.utils import validate_validation_code, send_validation_code
from marketing.models import PromotionToken, IntroducedBy, IntroducedByReward, Reward
from marketing.tops import Top
from utils import local_to_utc

# used for reward
from django.forms import model_to_dict
from marketing.models import RewardRecord
from wanglibao_sms.tasks import send_messages
from wanglibao_p2p.models import Earning
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao.templatetags.formatters import safe_phone_str
from wanglibao_account import message as inside_message
from order.models import Order
from order.utils import OrderHelper

# Create your views here.

class YaoView(TemplateView):
    template_name = 'yaoqing.jade'

class MarketingView(TemplateView):
    template_name = 'diary.jade'

    def get_context_data(self, **kwargs):

        start = self.request.GET.get('start', '')
        end = self.request.GET.get('end', '')
        if start and end:
            d0 = datetime.strptime(start, '%Y-%m-%d').date()
            d1 = datetime.strptime(end, '%Y-%m-%d').date()
        else:
            d0 = (datetime.now() - timedelta(days=7)).date()
            d1 = date.today()

        users = User.objects.filter(date_joined__range=(d0, d1)).order_by('each_day') \
            .extra({'each_day': 'date(date_joined)'}).values('each_day') \
            .annotate(joined_num=Count('id'))

        trades = P2PRecord.objects.filter(create_time__range=(d0, d1), catalog='申购').order_by('each_day') \
            .extra({'each_day': 'date(create_time)'}).values('each_day') \
            .annotate(trade_num=Count('id'), amount=Sum('amount'))

        d = defaultdict(dict)

        for l in (users, trades):
            for elem in l:
                d[elem['each_day']].update(elem)

        dd = d.values()

        result = sorted(dd, key=lambda x: x['each_day'])


        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                elif isinstance(obj, decimal.Decimal):
                    return float(obj)
                elif isinstance(obj, ModelState):
                    return None
                else:
                    return json.JSONEncoder.default(self, obj)

        json_re = json.dumps(result, cls=DateTimeEncoder)

        return {
            'result': result,
            'users': users,
            'json_re': json_re,
            'start': d0.strftime('%Y-%m-%d'),
            'end': d1.strftime('%Y-%m-%d')
        }

    @method_decorator(permission_required('marketing.change_sitedata', login_url='/' + settings.ADMIN_ADDRESS))
    def dispatch(self, request, *args, **kwargs):
        return super(MarketingView, self).dispatch(request, *args, **kwargs)

class TopsView(TemplateView):

    template_name = 'tops.jade'

    def get_context_data(self, **kwargs):
        day = self.request.GET.get('today', '')
        week = self.request.GET.get('week', 1)
        if day == '':
            today = datetime.now()
        else:
            today = datetime.strptime(day, '%Y-%m-%d')
        top = Top()
        result = top.day_tops(today)
        all = top.all_tops()
        week_tops = top.certain_week(int(week))
        print result
        return {
            'result': result,
            'week_tops': week_tops,
            'all_tops': all,
            'today': today.strftime('%Y-%m-%d'),
            'week': week
        }


class GennaeratorCode(TemplateView):
    template_name = 'gennerator_code.jade'

    def post(self, request):

        try:
            counts = int(request.POST.get('counts'))
        except:
            message = u'请输入合法的数字'
        else:
            MockGenerator.generate_codes(counts)
            message = u'生成 %s 条邀请码, 请点击<a href="/AK7WtEQ4Q9KPs8Io_zOncw/marketing/invitecode/" />查看</a>' % counts
        return HttpResponse({
            message
        })


class TvView(TemplateView):
    template_name = 'tv.jade'
    def get_context_data(self, **kwargs):
        return {}


class AppShareView(TemplateView):
    template_name = 'app_share.jade'

    def get_context_data(self, **kwargs):
        identifier = self.request.GET.get('phone')
        reg = self.request.GET.get('reg')

        return {
            'identifier': identifier,
            'reg': reg
        }


class AppShareRegView(TemplateView):
    template_name = 'app_share_reg.jade'

    def get_context_data(self, **kwargs):
        identifier = self.request.GET.get('identifier')
        friend_identifier = self.request.GET.get('friend_identifier')

        if friend_identifier:
            try:
                user = User.objects.get(wanglibaouserprofile__phone=friend_identifier)
                promo_token = PromotionToken.objects.get(user=user)
                invitecode = promo_token.token
            except:
                invitecode = ''
        else:
            invitecode = ''

        send_validation_code(identifier)
        return {
            'identifier': identifier,
            'invitecode': invitecode
        }


class NewYearView(TemplateView):
    template_name = 'newyear.jade'

    def get_context_data(self, **kwargs):
        top = Top()
        day_tops = top.day_tops(datetime.now())
        lastday_tops = top.lastday_tops()
        week_tops = top.week_tops(datetime.now())
        all_tops = top.all_tops()
        prizes = top.certain_prize()
        return {
            'day_tops': day_tops,
            'lastday_tops': lastday_tops,
            'week_tops': week_tops,
            'month_tops': all_tops,
            'prizes': prizes,
            'is_valid': top.is_valid()
        }


class AggregateView(TemplateView):
    """according the time and amount, filter the amount of user money
    """
    template_name = 'aggregate.jade'

    DEFAULT_START = '2015-01-14'
    DEFAULT_END = '2015-01-31'
    DEFAULT_AMOUNT_MIN = '1300000'

    @property
    def timezone_util(self):
        return pytz.timezone('Asia/Shanghai')

    def get_context_data(self, **kwargs):
        start = self.request.GET.get('start', '')
        end = self.request.GET.get('end', '')
        amount_min = self.request.GET.get('amount_min', '')
        amount_max = self.request.GET.get('amount_max', '')

        if start and end and amount_min:
            try:
                start = datetime.strptime(start, '%Y-%m-%d')
                end = datetime.strptime(end, '%Y-%m-%d')
                amount_min = Decimal(amount_min)
                if amount_max:
                    amount_max = Decimal(amount_max)
            except Exception:
                return {
                    "message": u'查询条件数据不合法！',
                    'start': start.date().__str__() if isinstance(start, datetime) else start,
                    'end': end.date().__str__() if isinstance(end, datetime) else end,
                    'amount_min': amount_min,
                    'amount_max': amount_max
                }
        else:
            return {
                "message": u'请输入查询条件！',
                'start': start,
                'end': end,
                'amount_min': amount_min,
                'amount_max': amount_max
            }

        trades = P2PRecord.objects.filter(
            create_time__range=(local_to_utc(start, source_time='min'), local_to_utc(end, source_time='max'))
        ).filter(product__status__in=[
            u'满标待打款',
            u'满标已打款',
            u'满标待审核',
            u'满标已审核',
            u'还款中',
            u'已完成', ]
        ).values('user').annotate(amount=Sum('amount'))

        if amount_min:
            trades = trades.filter(amount__gte=amount_min)
        if amount_max:
            trades = trades.filter(amount__lt=amount_max)

        # 总计所有符合条件的金额
        # amount_all = trades.aggregate(Sum('amount'))
        amount_all = 0
        for tr in trades:
            amount_all += decimal.Decimal(tr['amount'])

        # 关联用户认证信息
        trades = trades.select_related('user__wanglibaouserprofile').values(
            'user',
            'amount',
            'user__wanglibaouserprofile__phone',
            'user__wanglibaouserprofile__name'
        ).order_by('-amount')

        # 增加分页查询机制
        limit = 100
        paginator = Paginator(trades, limit)
        page = self.request.GET.get('page')
        try:
            result = paginator.page(page)
        except PageNotAnInteger:
            result = paginator.page(1)
        except Exception:
            result = paginator.page(paginator.num_pages)

        return {
            'result': result,
            'start': start.strftime('%Y-%m-%d'),
            'end': end.strftime('%Y-%m-%d'),
            'amount_min': amount_min,
            'amount_max': amount_max,
            'amount_all': amount_all
        }

    @method_decorator(permission_required('marketing.change_sitedata', login_url='/' + settings.ADMIN_ADDRESS))
    def dispatch(self, request, *args, **kwargs):
        return super(AggregateView, self).dispatch(request, *args, **kwargs)


class IntroducedAwardTemplate(TemplateView):
    """this class can used to query the introduced_by users and their first trade, according
    the percent calculated the first trade earnings, add it into db and after checked, reward it
    to their father
    """
    template_name = 'introduced_by.jade'

    def get_context_data(self, **kwargs):
        """ 根据条件查询邀请人收益统计表，管理员审核通过后系统会自动发放奖金到用户账户
            1：表中不存在未审核记录，直接根据用户条件统计信息
            2：表中存在未审核记录，提示用户需要先审核才允许再次统计
        """
        start = self.request.GET.get('start', '')
        end = self.request.GET.get('end', '')
        percent = self.request.GET.get('percent', '')
        amount_min = self.request.GET.get('amount_min', '')

        if start and end and percent and amount_min:
            try:
                start = datetime.strptime(start, '%Y-%m-%d')
                end = datetime.strptime(end, '%Y-%m-%d')
                # local time convert to utc time
                start_utc = local_to_utc(start, source_time='min')
                end_utc = local_to_utc(end, source_time='max')

                amount_min = Decimal(amount_min)
                percent = Decimal(percent)
            except Exception, e:
                return {
                    "message": u"查询条件数据不合法！",
                    "start": start.date().__str__() if isinstance(start, datetime) else start,
                    "end": end.date().__str__() if isinstance(end, datetime) else end,
                    "amount_min": amount_min,
                    "percent": percent,
                }
        else:
            return {
                "message": u"请输入统计条件！",
                "start": start.date().__str__() if isinstance(start, datetime) else start,
                "end": end.date().__str__() if isinstance(end, datetime) else end,
                "amount_min": amount_min,
                "percent": percent,
            }

        introduced_by_reward = IntroducedByReward.objects.filter(checked_status=0)

        # 如果存在未审核记录，将未审核记录和未审核记录的统计条件反馈给页面
        if introduced_by_reward.count() == 0:
            # 不存在未审核记录，直接进行统计
            # 查询复合条件的首次交易的被邀请人和邀请人信息
            if self.add_introduced_award(start_utc, end_utc, amount_min, percent):
                message = u'统计成功！'
            else:
                message = u'统计失败！'
        else:
            message = u'存在未审核记录，请先进行审核操作！'

        introduced_result = IntroducedByReward.objects.filter(checked_status=0)
        if introduced_by_reward and introduced_by_reward.count() > 0:
            time_zone = pytz.timezone('Asia/Shanghai')
            result_first = introduced_result.first()
            start = result_first.activity_start_at.astimezone(time_zone)
            end = result_first.activity_end_at.astimezone(time_zone)
            amount_min = result_first.activity_amount_min
            percent = result_first.percent_reward

        return {
            "message": message,
            "result": self.my_paginator(introduced_result),
            "start": start.date().__str__(),
            "end": end.date().__str__(),
            "amount_min": amount_min,
            "percent": percent,
            "amount_all": introduced_by_reward.aggregate(sum_introduced_reward=Sum('introduced_reward')) if introduced_by_reward else 0.00
        }

    @staticmethod
    def add_introduced_award(start_utc, end_utc, amount_min, percent):
        # 不存在未审核记录，直接进行统计
        # 查询复合条件的首次交易的被邀请人和邀请人信息
        new_user = IntroducedBy.objects.filter(
            bought_at__range=(start_utc, end_utc)
        ).exclude(
            introduced_by__username__startswith="channel"
        ).exclude(
            introduced_by__wanglibaouserprofile__utype__gt=0
        )
        query_set_list = []
        for first_user in new_user:
            # everyone
            first_record = P2PRecord.objects.filter(
                user=first_user.user,
                create_time__range=(start_utc, end_utc),
                catalog='申购',
                product__status__in=[
                    u'满标待打款',
                    u'满标已打款',
                    u'满标待审核',
                    u'满标已审核',
                    u'还款中',
                    u'已完成', ]
            ).order_by('create_time').first()

            # first trade min amount limit
            if first_record is not None and first_record.amount >= Decimal(amount_min):
                reward = IntroducedByReward()
                reward.user = first_user.user
                reward.introduced_by_person = first_user.introduced_by
                reward.product = first_record.product
                reward.first_bought_at = first_user.bought_at
                reward.first_amount = first_record.amount

                # 计算被邀请人首笔投资总收益
                amount_earning = Decimal(
                    Decimal(first_record.amount) * (Decimal(first_record.product.period) / Decimal(12))
                ).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
                reward.first_reward = amount_earning
                # 邀请人活取被邀请人首笔投资收益
                reward.introduced_reward = Decimal(
                    amount_earning * Decimal(percent) * Decimal('0.01')
                ).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

                reward.activity_start_at = start_utc
                reward.activity_end_at = end_utc
                reward.activity_amount_min = Decimal(amount_min)
                reward.percent_reward = Decimal(percent)
                reward.checked_status = 0
                # reward.save()
                query_set_list.append(reward)

        if query_set_list:
            IntroducedByReward.objects.bulk_create(query_set_list)

        return True

    @method_decorator(permission_required('marketing.change_sitedata', login_url='/' + settings.ADMIN_ADDRESS))
    def dispatch(self, request, *args, **kwargs):
        return super(IntroducedAwardTemplate, self).dispatch(request, *args, **kwargs)

    def my_paginator(self, obj, limit=10):
        # 增加分页查询机制
        paginator = Paginator(obj, limit)
        page = self.request.GET.get('page')
        try:
            obj = paginator.page(page)
        except PageNotAnInteger:
            obj = paginator.page(1)
        except Exception:
            obj = paginator.page(paginator.num_pages)
        return obj

    def post(self, request, **kwargs):
        """ 发放红包 """
        check = request.POST.get('check_ok', '') or request.POST.get('check_no', '')
        if check == '1':
            # 审核通过，给用户发放奖励
            reward_type = u'邀请送收益'
            # True 标识只将信息标准输出到终端上，不进行实际操作
            # False 标识实际发送红包
            only_show = False
            records = IntroducedByReward.objects.filter(checked_status=0)
            for record in records:
                self.reward_user(
                    user=record.user,
                    introduced_by=record.introduced_by_person,
                    reward_type=reward_type,
                    got_amount=record.introduced_reward,
                    product=record.product,
                    only_show=only_show
                )

            # self.reward_user_all()
            IntroducedByReward.objects.filter(checked_status=0).update(checked_status=1)
            message = u'审核通过成功，为用户发送收益成功！'


        elif check == '2':
            # 审核未通过，删除统计记录
            records = IntroducedByReward.objects.filter(checked_status=0)
            records.delete()
            message = u'审核未通过成功，已经清除统计记录！'

        else:
            # 非法操作
            message = u'非法操作！'

        context = {
            "message": message
        }
        return self.render_to_response(context)

    @staticmethod
    def reward_user(user, introduced_by, reward_type, got_amount, product, only_show):
        reward = Reward.objects.filter(is_used=False, type=reward_type).first()

        text_content = u"【网利宝】您在邀请好友送收益的活动中，获得%s元收益，收益已经发放至您的网利宝账户。请注意查收。回复TD退订4008-588-066【网利宝】" % got_amount
        if only_show is not True:
            send_messages.apply_async(kwargs={
                "phones": [introduced_by.wanglibaouserprofile.phone],
                "messages": [text_content]
            })

        if only_show is not True:
            earning = Earning()
            earning.amount = got_amount
            earning.type = 'I'
            earning.product = product
            order = OrderHelper.place_order(
                introduced_by,
                Order.ACTIVITY,
                u"邀请送收益活动赠送",
                earning=model_to_dict(earning))
            earning.order = order
            keeper = MarginKeeper(introduced_by, order.pk)

            # 赠送活动描述
            desc = u'%s,邀请好友首次理财活动中，活赠%s元' % (introduced_by.wanglibaouserprofile.name, got_amount)
            earning.margin_record = keeper.deposit(got_amount, description=desc)
            earning.user = introduced_by
            earning.save()

        message_content = u"您在邀请好友送收益的活动中，您的好友%s在活动期间完成首次投资，根据活动规则，您获得%s元收益。<br/>\
                          <a href = 'https://www.wanglibao.com/accounts/home/'>查看账户余额</a><br/>\
                          感谢您对我们的支持与关注。<br/>\
                          网利宝" % (safe_phone_str(user.wanglibaouserprofile.phone), got_amount)

        if only_show is not True:
            RewardRecord.objects.create(user=introduced_by, reward=reward, description=message_content)
            inside_message.send_one.apply_async(kwargs={
                "user_id": introduced_by.id,
                "title": u"邀请送收益活动",
                "content": message_content,
                "mtype": "activity"
            })
        else:
            print message_content
            print introduced_by.wanglibaouserprofile.name
            print safe_phone_str(user.wanglibaouserprofile.phone)
            print text_content

    # def reward_user_all(self):
    #     """ 方法在批量保存 earning 的时候有问题
    #     """
    #     reward_type = u'邀请送收益活动'
    #     # True 标识只将信息标准输出到终端上，不进行实际操作
    #     # False 标识实际发送红包
    #     only_show = False
    #     records = IntroducedByReward.objects.filter(checked_status=0)
    #
    #     phones_list = []
    #     messages_list = []
    #     text_content = u"【网利宝】您在邀请好友送收益的活动中，获得{0}元收益，收益已经发放至您的网利宝账户。请注意查收。回复TD退订4008-588-066【网利宝】"
    #
    #     user_id_list = []
    #     title_list = []
    #     content_list = []
    #     mtype_list = []
    #     message_content = u"您在邀请好友送收益的活动中，您的好友{0}在活动期间完成首次投资，根据活动规则，您获得{1}元收益。<br/>\
    #                       <a href = 'https://www.wanglibao.com/accounts/home/'>查看账户余额</a><br/>\
    #                       感谢您对我们的支持与关注。<br/>\
    #                       网利宝"
    #
    #     # 发放收益入库记录
    #     earing_set_list = []
    #     reward_record_set_list = []
    #
    #     for record in records:
    #         ###
    #         # 批量生成短信
    #         ###
    #         phones_list.append(record.user.wanglibaouserprofile.phone)
    #         messages_list.append(text_content.format(record.introduced_reward,))
    #
    #         ###
    #         # 批量生成站内信
    #         ###
    #         user_id_list.append(record.introduced_by_person.id)
    #         title_list.append(u"邀请送收益活动")
    #         message_content_tmp = message_content.format(
    #             safe_phone_str(record.user.wanglibaouserprofile.phone),
    #             record.introduced_reward
    #         )
    #         content_list.append(message_content_tmp)
    #         mtype_list.append("activity")
    #
    #         # ###
    #         # # 创建站内信内容
    #         # ###
    #         # reward_record = RewardRecord()
    #         # reward_record.user = record.introduced_by_person
    #         # reward = Reward.objects.filter(is_used=False, type=reward_type).first()
    #         # reward_record.reward = reward
    #         # reward_record.description = message_content_tmp
    #         # reward_record_set_list.append(reward_record)
    #
    #         # 生成用户收益金额几描述
    #         earning = Earning()
    #         earning.amount = record.introduced_reward
    #         earning.type = 'I'
    #         earning.product = record.product
    #         order = OrderHelper.place_order(
    #             record.introduced_by_person,
    #             Order.ACTIVITY,
    #             u"邀请送收益活动赠送",
    #             earning=model_to_dict(earning))
    #         earning.order = order
    #         keeper = MarginKeeper(record.introduced_by_person, order.pk)
    #
    #         # 赠送活动描述
    #         desc = u'{0},邀请好友首次理财活动中，活赠{1}元'.format(
    #             record.introduced_by_person.wanglibaouserprofile.name,
    #             record.introduced_reward
    #         )
    #         earning.margin_record = keeper.deposit(record.introduced_reward, description=desc)
    #         earning.user = record.introduced_by_person
    #         earning.save()
    #         earing_set_list.append(earning)
    #
    #     if only_show is not True:
    #         # 批量发送消息
    #         send_messages.apply_async(kwargs={
    #             "phones": phones_list,
    #             "messages": messages_list
    #         })
    #
    #         # 收益入库
    #         Earning.objects.bulk_create(earing_set_list)
    #
    #         # 发站内信
    #         for user_id, content in dict(zip(user_id_list, content_list)).items():
    #             self._send_one_site(user_id, reward_type, content)
    #     else:
    #         for n in xrange(len(user_id_list)):
    #             print messages_list[n]
    #             print phones_list[n]
    #             print content_list[n]
    #
    # def _send_one_site(self, introduced_by, reward_type, message_content):
    #     reward = Reward.objects.filter(is_used=False, type=reward_type).first()
    #     RewardRecord.objects.create(user=introduced_by, reward=reward, description=message_content)
    #     inside_message.send_one.apply_async(kwargs={
    #         "user_id": introduced_by.id,
    #         "title": u"邀请送收益活动",
    #         "content": message_content,
    #         "mtype": "activity"
    #     })
