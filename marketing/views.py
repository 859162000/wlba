# encoding:utf-8
import json
import decimal
import pytz
from datetime import date, timedelta, datetime
from collections import defaultdict
from decimal import Decimal
import time
from wanglibao_p2p.models import P2PEquity
from django.db.models import Count, Sum
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator, PageNotAnInteger
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from wanglibao_p2p.models import P2PRecord
from django.views.generic import TemplateView
from django.http.response import HttpResponse, Http404
from mock_generator import MockGenerator
from django.conf import settings
from django.db.models.base import ModelState
from wanglibao_sms.utils import send_validation_code
from marketing.models import WanglibaoActivityReward, Channels, PromotionToken, IntroducedBy, IntroducedByReward, Reward, ActivityJoinLog
from marketing.tops import Top
from utils import local_to_utc

# used for reward
from django.forms import model_to_dict
from django.db.models import Q
from marketing.models import RewardRecord, NewsAndReport
from wanglibao_p2p.models import Earning
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao.templatetags.formatters import safe_phone_str
from wanglibao_account import message as inside_message
from order.models import Order
from order.utils import OrderHelper
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from wanglibao_redpack.models import RedPackEvent
from wanglibao_redpack import backends as redpack_backends
from wanglibao_activity.models import ActivityRecord, Activity
from wanglibao_account import message as inside_message
import logging
logger = logging.getLogger('marketing')

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
        # print result
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
            from tasks import add_introduced_award_all
            add_introduced_award_all.apply_async(kwargs={
                "start": start.date().__str__(),
                "end": end.date().__str__(),
                "amount_min": amount_min,
                "percent": percent,
            })

            message = u'正在统计，请稍后查询！'
        else:
            message = u'存在未审核记录，请先进行审核操作！'

        introduced_result = IntroducedByReward.objects.filter(checked_status=0).order_by("first_bought_at")
        if not introduced_by_reward.exists():
            introduced_result = IntroducedByReward.objects.filter(
                activity_start_at=start_utc,
                activity_end_at=end_utc
            ).order_by("first_bought_at")

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
            "amount_all": introduced_by_reward.aggregate(sum_introduced_reward=Sum('introduced_reward')) if introduced_by_reward else 0.00,
            "amount_user_all": introduced_by_reward.aggregate(sum_user_send_amount=Sum('user_send_amount')) if introduced_by_reward else 0.00,
            "amount_introduced_all": introduced_by_reward.aggregate(sum_introduced_send_amount=Sum('introduced_send_amount')) if introduced_by_reward else 0.00,
        }

    @method_decorator(permission_required('marketing.change_sitedata', login_url='/' + settings.ADMIN_ADDRESS))
    def dispatch(self, request, *args, **kwargs):
        return super(IntroducedAwardTemplate, self).dispatch(request, *args, **kwargs)

    def my_paginator(self, obj, limit=100):
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

        start = self.request.POST.get('start', '')
        end = self.request.POST.get('end', '')
        percent = self.request.POST.get('percent', '')
        amount_min = self.request.POST.get('amount_min', '')

        if check == '1':
            if start and end and percent and amount_min:
                from tasks import send_reward_all

                send_reward_all.apply_async(kwargs={
                    "start": start,
                    "end": end,
                    "amount_min": amount_min,
                    "percent": percent,
                })

            message = u'审核通过结束，稍后查询发放记录！'

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

        # text_content = u"【网利宝】您在邀请好友送收益的活动中，获得%s元收益，收益已经发放至您的网利宝账户。请注意查收。" % got_amount
        # if only_show is not True:
        #     send_messages.apply_async(kwargs={
        #         "phones": [introduced_by.wanglibaouserprofile.phone],
        #         "messages": [text_content]
        #     })

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
            earning.margin_record = keeper.deposit(got_amount, description=desc, catalog=u"邀请首次赠送")
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
            # print text_content


class NewsListView(TemplateView):
    """ News and Report list page """

    template_name = 'news_new.jade'

    def get_context_data(self, **kwargs):
        news = NewsAndReport.objects.filter().order_by('-score', '-created_at')

        news_list = []
        news_list.extend(news)

        limit = 10
        paginator = Paginator(news_list, limit)
        page = self.request.GET.get('page')

        try:
            news_list = paginator.page(page)
        except PageNotAnInteger:
            news_list = paginator.page(1)
        except Exception:
            news_list = paginator.page(paginator.num_pages)

        return {
            'news_list': news_list
        }


class NewsDetailView(TemplateView):
    """ News detail page """

    template_name = 'news_detail.jade'

    def get_context_data(self, id, **kwargs):
        context = super(NewsDetailView, self).get_context_data(**kwargs)

        try:
            news = NewsAndReport.objects.get(pk=id)

        except NewsAndReport.DoesNotExist:
            raise Http404(u'您查找的媒体报道不存在')

        context.update({
            'news': news,

        })

        return context


class ActivityJoinLogAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user
        amount = int(request.POST.get('amount', 0))
        if not user:
            return Response({'ret_code': 3001, 'message': u'用户没有登陆，请先登陆'})

        start_time = timezone.datetime(2015, 6, 29)
        dt = timezone.datetime.now()
        if dt > timezone.datetime(2015, 8, 4, 23, 59, 59):
            return Response({'ret_code': 3002, 'message': u'活动已过期'})

        user_ib = IntroducedBy.objects.filter(user=user, channel__name='xunlei', created_at__gt=start_time).first()
        if user_ib:
            has_log = ActivityJoinLog.objects.filter(user=user, action_name='xunlei_july').first()
            if has_log:
                return Response({'ret_code': 3002, 'message': u'已经参加过该活动，不能重复参加'})
            else:
                if amount:
                    ActivityJoinLog.objects.create(
                        user=user,
                        action_name=u'xunlei_july',
                        action_type=u'register',
                        action_message=u'用户参加数钱游戏得红包，3秒内每点击一次得10元，得多少钱送多少红包',
                        channel=u'xunlei',
                        gift_name=u'迅雷7月数钱红包',
                        join_times=1,
                        amount=amount,
                        create_time=timezone.now(),
                    )
                    divisor = amount / 50    # 50元红包的个数
                    remainder = amount % 50  # 金额除以50的余数，剩余红包金额
                    numbers = []
                    if divisor > 0:
                        numbers = [50] * divisor

                    numbers = numbers + [remainder]
                    for number in numbers:
                        describe = 'xunlei_july_' + str(number)
                        redpack_event = RedPackEvent.objects.filter(invalid=False, describe=describe,
                                                                    target_channel='xunlei',
                                                                    give_start_at__lt=dt, give_end_at__gt=dt).first()
                        if redpack_event:
                            redpack_backends.give_activity_redpack(user, redpack_event, 'pc')

                    return Response({'ret_code': 0, 'message': u'红包发放成功，请到用户中心查看'})
                else:
                    return Response({'ret_code': 3000, 'message': u'倒计时开始'})
        else:
            return Response({'ret_code': 3002, 'message': u'不符合参加条件'})


class ActivityJoinLogCountAPIView(APIView):
    permission_classes = ()

    def get(self, request):
        join_log = ActivityJoinLog.objects.filter(channel='xunlei',
                                                  action_name='xunlei_july').aggregate(amount_sum=Sum('amount'))

        return Response({'ret_code': 0,
                         'redpack_total': int(join_log['amount_sum']/10) if join_log['amount_sum'] else 0,
                         'amount_total': join_log['amount_sum'] if join_log['amount_sum'] else 0
        })


def ajax_get_activity_record(action='get_award', *gifts):
    """
        author: add by Yihen@20150825
        description:迅雷9月抽奖活动，获得用户的抽奖记录
    """
    records = ActivityJoinLog.objects.filter(action_name=action, action_type='login', join_times=0, amount__gt=0)
    data = [{'phone': record.user.wanglibaouserprofile.phone, 'awards': float(record.amount)} for record in records]
    if gifts:
        records = ActivityJoinLog.objects.filter(Q(gift_name=u'爱奇艺')|Q(gift_name=u'抠电影'), action_name=action, action_type='login', join_times=0)
        gift = [{'phone': record.user.wanglibaouserprofile.phone, 'awards': record.gift_name} for record in records]
    to_json_response = {
        'ret_code': 3005,
        'data': data,
        'gift': gift if gifts else "None",
        'message': u'获得抽奖成功用户',
    }
    return HttpResponse(json.dumps(to_json_response), content_type='application/json')


def ajax_post(request):
    """
        author: add by Yihen@20150825
        description:迅雷9月抽奖活动，响应web的ajax请求
    """
    user = request.user
    if not user.is_authenticated():
        to_json_response = {
            'ret_code': 3000,
            'message': u'用户没有登陆，请先登陆',
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    record = IntroducedBy.objects.filter(user_id=user.id).first()
    if record:
        record = Channels.objects.filter(id=record.channel_id).first()
    if not record or (record and record.name != 'xunlei9'):
        to_json_response = {
            'ret_code': 4000,
            'message': u'非迅雷渠道过来的用户',
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    if request.method == "POST":
        obj = ThunderAwardAPIView()
        action = request.POST.get("action", "")

        if action == 'GET_AWARD':
            res = obj.get_award(request)

        if action == 'IGNORE_AWARD':
            res = obj.ignore_award(request)

        if action == 'ENTER_WEB_PAGE':
            res = obj.enter_webpage(request)

        return res


class ThunderAwardAPIView(APIView):
    """
        Type: Add
        Modified By: Yihen@20150821
        description: 迅雷抽奖活动1.用户有三次摇奖机会，三次摇奖必中奖一次，中奖金额分别为100元（30%）、
                    150元（60%）、 200元（10%），中奖后提示中奖金额及中奖提示语，非中奖用户提示非中奖提示语。
    """

    def get_award(self, request):
        """
            TO-WRITE
        """
        join_log = ActivityJoinLog.objects.filter(user=request.user).first()
        join_log.join_times -= 1
        join_log.save(update_fields=['join_times'])
        money = self.get_award_mount(join_log.id)
        describe = 'xunlei_sept_' + str(money)
        try:
            dt = timezone.datetime.now()
            redpack_event = RedPackEvent.objects.filter(invalid=False, describe=describe,give_start_at__lte=dt, give_end_at__gte=dt).first()
        except Exception, reason:
            print reason

        if redpack_event:
            redpack_backends.give_activity_redpack(request.user, redpack_event, 'pc')

        to_json_response = {
            'ret_code': 3001,
            'get_time': (join_log.id % 3)+1,  # 第几次抽中
            'left': join_log.join_times,  # 还剩几次
            'amount': str(join_log.amount),  # 奖励的金额
            'message': u'终于等到你，还好我没放弃',
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    def ignore_award(self, request):
        """
            将剩余的刮奖次数减1，并返回最终结果
        """
        join_log = ActivityJoinLog.objects.filter(user=request.user).first()
        if join_log.join_times > 0:
            join_log.join_times -= 1
        join_log.save(update_fields=['join_times'])
        to_json_response = {
            'ret_code': 3002,
            'get_time': (join_log.id % 3)+1,  # 第几次抽中
            'left': join_log.join_times,  # 还剩几次
            'amount': str(join_log.amount),  # 奖励的金额
            'message': u'你和大奖只是一根头发的距离',
        }

        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    def get_award_mount(self, index):
        index %= 10
        if index in (0,):
            return 200
        if index in(3, 6, 9):
            return 150
        if index in(1, 2, 4, 5, 7, 8):
            return 100

    def enter_webpage(self, request):
        """
            进入页面的时候，判断是否生成记录，如果没有则生成并返回剩余刮奖次数3；如果有，则直接返回剩余刮奖次数；
        """
        join_log = ActivityJoinLog.objects.filter(user=request.user).first()
        if not join_log:
            activity = ActivityJoinLog.objects.create(
                user=request.user,
                action_name=u'get_award',
                action_type=u'login',
                action_message=u'迅雷抽奖活动',
                channel=u'all',
                gift_name=u'抽得千元大奖',
                amount=0,
                join_times=3,
                create_time=timezone.now(),
            )

            join_log = ActivityJoinLog.objects.filter(user=request.user, action_name='get_award').first()
            join_log.amount = self.get_award_mount(activity.id)
            join_log.save(update_fields=['amount'])

        to_json_response = {
            'ret_code': 3003,
            'get_time': (join_log.id % 3)+1,  # 第几次抽中
            'left': join_log.join_times,  # 还剩几次
            'amount': str(join_log.amount),  # 奖励的金额
            'message': u'欢迎刮奖',
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

class ThousandRedPackAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user
        if not user:
            return Response({'ret_code': 3001, 'message': u'用户没有登陆，请先登陆'})

        dt = timezone.datetime.now()
        start_time = timezone.datetime(dt.year, dt.month, dt.day)
        end_time = timezone.datetime(dt.year, dt.month, dt.day, 23, 59, 59)

        if dt > timezone.datetime(2015, 8, 7, 23, 59, 59):
            return Response({'ret_code': 3003, 'message': u'活动已过期'})

        join_log = ActivityJoinLog.objects.filter(channel='all', action_name='thousand_redpack',
                                                  create_time__gt=start_time, create_time__lt=end_time)\
                                          .aggregate(user_count=Count('id'))
        if join_log and join_log['user_count'] > 3000:
            return Response({'ret_code': 3002, 'message': u'抱歉，今天参加人数已经达到3000人，请明天再来'})

        has_log = ActivityJoinLog.objects.filter(user=user, action_name='thousand_redpack',
                                                 create_time__gt=start_time, create_time__lt=end_time).first()
        if has_log:
            return Response({'ret_code': 3003, 'message': u'您今天已经参加过该活动，不能重复参加'})
        else:
            ActivityJoinLog.objects.create(
                user=user,
                action_name=u'thousand_redpack',
                action_type=u'login',
                action_message=u'登陆后领取千元红包大礼',
                channel=u'all',
                gift_name=u'伸手领钱活动',
                join_times=1,
                amount=1000,
                create_time=timezone.now(),
            )
            numbers = ['100', '200', '300', '400']
            for number in numbers:
                describe = 'thousand_redpack_' + str(number)
                redpack_event = RedPackEvent.objects.filter(invalid=False, describe=describe,
                                                            give_start_at__lt=dt, give_end_at__gt=dt).first()
                if redpack_event:
                    redpack_backends.give_activity_redpack(user, redpack_event, 'pc')

            return Response({'ret_code': 0, 'message': u'红包发放成功，请到用户中心查看'})

class ThousandRedPackCountAPIView(APIView):
    permission_classes = ()

    def get(self, request):
        join_log = ActivityJoinLog.objects.filter(channel='all', action_name='thousand_redpack') \
                                          .aggregate(user_count=Count('id'))

        return Response({'ret_code': 0,
                         'redpack_total': int(join_log['user_count'] * 4) if join_log['user_count'] else 0,
        })

class ThunderActivityRewardCounter(APIView):
    """ 迅雷八月份活动统计迅雷会员发放个数，首次投资和首次充值发放迅雷会员"""
    permission_classes = ()

    def get(self, request):
        record = ActivityRecord.objects.filter(
            trigger_node__in=['first_pay', 'first_buy'],
            activity__code='xunlei8'
        ).filter(
            Q(activity__is_stopped=True) & Q(activity__stopped_at__gte=timezone.now()) | Q(activity__is_stopped=False) & Q(activity__start_at__lte=timezone.now()) & Q(activity__end_at__gte=timezone.now())
        ).aggregate(num=Count('id'))
        return Response({
            'ret_code': 0,
            'num': int(record['num']) if record['num'] else 0,
        })

def celebrate_ajax(request):
    """
        Author: add by Yihen@20150827
        Description: 网利宝公司活动 ,大转盘
    """
    user = request.user
    action = request.POST.get('action',)
    if action == 'GET_AWARD':
        return ajax_get_activity_record('celebrate_award')
    if not user.is_authenticated():
        to_json_response = {
            'ret_code': 4000,
            'message': u'用户没有登陆，请先登陆',
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    # delete by Yihen@20150906, 需求有变更，放开所有的渠道
    #record = IntroducedBy.objects.filter(user_id=user.id).first()

    #if record is not None and record.channel_id != 18:
    #    try:
    #        channel = Channels.objects.filter(id=record.channel_id).first()
    #    except Exception, reason:
    #        to_json_response = {
    #            'ret_code': 4000,
    #            'message': u'渠道用户不允许参加这个活动',
    #        }
    #        logger.debug("Exception:渠道用户不允许参加, Reason:%s" % ( reason, ) )
    #        logger.debug("Exception:渠道用户不允许参加, record.__dict__:%s" % (record.__dict__ , ) )
    #        return HttpResponse(json.dumps(to_json_response), content_type='application/json')
    #else:
    #    channel = None

    #if channel is not None and channel.name and channel.id != 18:
    #    to_json_response = {
    #        'ret_code': 4000,
    #        'message': u'渠道用户不允许参加这个活动',
    #    }
    #    return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    if request.is_ajax() and request.method == 'POST':
        activity = WanglibaoAwardActivity(request)
        if action == 'IS_VALID':
            return activity.is_valid_user()

        if action == 'ENTER_WEB_PAGE':
            left = activity.update_record_data()
            to_json_response = {
                'ret_code': 3005,
                'left': left,
                'message': u'更新记录数据成功',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json' )

        if action == 'AWARD_DONE':
            return activity.response_activity()

    else:
        to_json_response = {
            'ret_code': 3007,
            'message': u'请以ajax方式交互，并用post请求',
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json' )

class WanglibaoAwardActivity(APIView):
    """
        Author: add by Yihen@20150827
        Description: 网利宝公司活动
    """
    def __init__(self, request):
        self.request = request
        self.user = self.request.user
        activity_start = datetime(2015, 9, 6, 0, 0)
        self.record = P2PEquity.objects.filter(equity__gte=5000, created_at__gt=activity_start, user_id=request.user.id).aggregate(counts=Count('id'))

    def is_valid_user(self):
        """
            Description:判断用户是不是在活动期间内注册的新用户
        """
        create_at = int(time.mktime(self.user.date_joined.date().timetuple()))  # 用户注册的时间戳
        activity_start = time.mktime(datetime(2014, 8, 1).timetuple())  # 活动开始时间

        if activity_start > create_at:
            to_json_response = {
                'ret_code': 3000,
                'message': u'非活动期注册用户',
            }
        else:
            to_json_response = {
                'ret_code': 3001,
                'message': u'活动期注册用户',
            }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json' )

    def update_record_data(self):
        total, used = self.update_total_chances_and_awards()
        self.update_user_activity_logs()
        if total is not None and used is not None:
            return total - used
        else:
            return None

    def update_total_chances_and_awards(self):
        """
            每次进入转盘页面，会更新一下用户的抽奖机会和获奖机会, 如果用户是第一次玩，
            需要在获奖表里，给用户增加一条记录
        """
        if self.record:
            user_activity = WanglibaoActivityReward.objects.filter(user=self.request.user.id).first()
            if user_activity:
                user_activity.total_chances = self.record['counts']
                user_activity.total_awards = self.record['counts']
                user_activity.save(update_fields=['total_chances', 'total_awards'])
            else:
                user_activity = WanglibaoActivityReward.objects.create(
                    user=self.request.user,
                    activity_id='one_year_celebrate',
                    total_chances=self.record['counts'],
                    used_chances=0,
                    total_awards=self.record['counts'],
                    used_awards=0)
            return user_activity.total_awards, user_activity.used_awards
        else:
            return None, None

    def get_award_mount(self, activity_id):
        award_amount = {
            1000: 10,  # 1000元红包，10个
            500: 20,  # 500元红包，20个
            200: 50  # 200元红包，50个
        }

        def get_counts(money):
            count = ActivityJoinLog.objects.filter(action_name='celebrate_award', amount=money).aggregate(counts=Count('id'))
            return count["counts"]

        result = {key: get_counts(key) for key in award_amount.keys()}
        if activity_id % 100 == 0:
            for award in (1000, 500, 200):
                if result[award] < award_amount[award]:
                    return award

        if activity_id % 49 == 0:
            for award in (500, 200):
                if result[award] < award_amount[award]:
                    return award

        if activity_id % 48 == 0:
            for award in (200,):
                if result[award] < award_amount[award]:
                    return award

        return 50

    def update_user_activity_logs(self):
        """
            更新用户的红包记录
        """
        activity = ActivityJoinLog.objects.filter(action_name='celebrate_award', user_id=self.request.user.id, join_times__gt=0).aggregate(user_count=Count('id'))
        count = 0
        user_count = activity["user_count"] if activity else 0
        while user_count + count < self.record["counts"]:
            activity = ActivityJoinLog.objects.create(
                user=self.request.user,
                action_name=u'celebrate_award',
                action_type=u'login',
                action_message=u'一周年大转盘',
                channel=u'all',
                gift_name=u'周年抽奖大转盘',
                amount=0,
                join_times=1,
                create_time=timezone.now(),
            )

            join_log = ActivityJoinLog.objects.filter(action_name='celebrate_award', user=self.request.user, amount=0).order_by('-create_time').first()
            join_log.amount = self.get_award_mount(activity.id)
            join_log.save(update_fields=['amount'])
            count += 1

    def response_activity(self):
        user_activity = WanglibaoActivityReward.objects.filter(user=self.request.user.id).first()
        if user_activity.total_chances <= user_activity.used_chances:
            to_json_response = {
                'ret_code': 3016,
                'amount': 0,
                'left': user_activity.total_chances - user_activity.used_chances,
                'message': u'您的抽奖机会已经用完',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        join_log = ActivityJoinLog.objects.filter(user=self.request.user, action_name='celebrate_award', join_times__gt=0).first()
        join_log.join_times -= 1
        join_log.save(update_fields=['join_times'])
        money = join_log.amount
        describe = 'celebrate_year_' + str(int(money))
        try:
            dt = timezone.datetime.now()
            redpack_event = RedPackEvent.objects.filter(invalid=False, describe=describe, give_start_at__lte=dt, give_end_at__gte=dt).first()
        except Exception, reason:
            logger.debug("exception reason: %s " % (reason))

        if redpack_event:
            redpack_backends.give_activity_redpack(self.request.user, redpack_event, 'pc')

        #  更新奖品表相应字段值
        user_activity.used_chances += 1
        user_activity.used_awards += 1
        user_activity.save(update_fields=['used_chances', 'used_awards'])

        to_json_response = {
            'ret_code': 3006,
            'amount': str(money),
            'left': user_activity.total_chances - user_activity.used_chances,
            'message': u'终于等到你，还好我没放弃',
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')


def september_award_ajax(request):
    user = request.user
    action = request.POST.get('action',)
    logger.debug("in activity common_award_september, User Action: %s" % (action,))
    if action == 'GET_AWARD':
        return ajax_get_activity_record('common_award_sepetember')
    if not user.is_authenticated():
        to_json_response = {
            'ret_code': 4000,
            'message': u'用户没有登陆，请先登陆',
        }
        logger.debug("in activity common_award_september, User NO LOG IN")
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    activity = CommonAward(request)
    if action == 'IS_VALID_USER':
        return activity.is_register_in_activity_period()

    if action == 'IS_VALID_CHANNEL':
        return activity.is_valid_channel_register_user()

    if request.is_ajax() and request.method == 'POST':
        if action == "ENTER_WEB_PAGE":
            return activity.update_total_chances_and_awards()
        if action == 'GET_GIFT':
            return activity.get_gift_action()
        if action == 'GET_MONEY':
            return activity.get_money_action()
        if action == 'IGNORE':
            return activity.ignore_user_action()

class CommonAward(object):
    """
        Description: 9月PC常规
        Author: Yihen@20150907
    """

    def __init__(self, request):
        self.request = request
        self.user = self.request.user

    def is_valid_channel_register_user(self):
        channels = Activity.objects.filter(code="9yuechangguiPC").first()
        if not channels:
            to_json_response = {
                'ret_code': 3030,
                'message': u'There is no channel seted',
            }
            logger.debug("user_id:%d, check valid channel flow, no channel set" %(self.request.user.id))
            return HttpResponse(json.dumps(to_json_response), content_type='application/json' )

        channels = channels.channel.split(",")
        logger.debug("in activity common_award_september, set Channels: %s")
        record = IntroducedBy.objects.filter(user_id=self.request.user.id).first()

        if not record or (record and record.channel.name not in channels):
            to_json_response = {
                'ret_code': 3010,
                'message': u'渠道用户不是从对应的渠道过来',
            }
        else:
            to_json_response = {
                'ret_code': 3011,
                'message': u'渠道用户从对应的渠道过来',
            }
        logger.debug("user_id:%d, check invite_code flow,ret_code:%d, message:%s " %(self.request.user.id, to_json_response["ret_code"], to_json_response["message"]))
        return HttpResponse(json.dumps(to_json_response), content_type='application/json' )

    def is_register_in_activity_period(self):
        """
            Description:判断用户是不是在活动期间内注册的新用户
        """
        create_at = int(time.mktime(self.user.date_joined.date().timetuple()))  # 用户注册的时间戳
        activity_start = time.mktime(datetime(2014, 9, 10).timetuple())  # 活动开始时间

        if activity_start > create_at:
            to_json_response = {
                'ret_code': 3000,
                'message': u'非活动期注册用户',
            }
        else:
            to_json_response = {
                'ret_code': 3001,
                'message': u'活动期注册用户',
            }
        logger.debug("user_id:%d, check invite_code flow,ret_code:%d, message:%s " %(self.request.user.id, to_json_response["ret_code"], to_json_response["message"]))
        return HttpResponse(json.dumps(to_json_response), content_type='application/json' )

    def get_award_mount(self, activity_id):
        award = (100, 150, 200,)
        index = activity_id % 3
        return award[index]

    def get_counts(self, gift):
        join_log = ActivityJoinLog.objects.filter(action_name='common_award_sepetember', gift_name=gift).aggregate(counts=Count('id'))
        return join_log["counts"]

    def get_award_index(self, activity_id):
        while activity_id%10 == 0:
            activity_id = activity_id/10

        return activity_id%2

    def get_award_gift(self, activity_id):
        award = [u"抠电影", u"爱奇艺"]
        gifts = {
            u"抠电影":483,
           u"爱奇艺":680,
        }
        index = self.get_award_index(activity_id)
        if activity_id % 10 == 0:  # 控制概率, %10 不是 %20,因为一次产生两条获奖记录
            counts = self.get_counts(award[index])
            if counts < gifts[award[index]]:
                return award[index]
            else:
                index = index^1
                counts = self.get_counts(award[index])
                if counts < gifts[award[index]]:
                    return award[index]
                else:
                    return u"None"
        else:
            return u"None"

    def ignore_user_action(self):
        user_activity = WanglibaoActivityReward.objects.filter(user=self.request.user.id).first()
        if user_activity.total_chances <= user_activity.used_chances:
            to_json_response = {
                'ret_code': 3024,
                'total_chances': user_activity.total_chances,
                'used_chances': user_activity.used_chances,
                'gift': u'None',
                'message': u'您的抽奖机会已经用完了',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        user_activity.used_chances += 1
        user_activity.save(update_fields=["used_chances"])
        to_json_response = {
            'ret_code': 3013,
            'total_chances': user_activity.total_chances,
            'used_chances': user_activity.used_chances,
            'message': u'此次行为忽略',
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    def get_gift_action(self):
        user_activity = WanglibaoActivityReward.objects.filter(user=self.request.user.id).first()
        if user_activity.total_chances <= user_activity.used_chances:
            to_json_response = {
                'ret_code': 3024,
                'total_chances': user_activity.total_chances,
                'used_chances': user_activity.used_chances,
                'gift': u'None',
                'message': u'您的抽奖机会已经用完了',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')
        else:
            gift = ActivityJoinLog.objects.filter(action_name='common_award_sepetember', user=self.request.user).exclude(Q(gift_name=u'现金红包')|Q(gift_name=u"None")).first()
            if gift and gift.join_times == 0:
                to_json_response = {
                    'ret_code': 3025,
                    'type': "gift",
                    'message': u'您的奖品已经被领走了',
                }
                return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        gift = ActivityJoinLog.objects.filter(action_name='common_award_sepetember', user=self.request.user, join_times=1).exclude(gift_name=u'现金红包').first()
        if gift:
            gift.join_times = 0
            gift.save(update_fields=["join_times"])

        user_activity.used_chances += 1
        user_activity.used_awards += 1
        user_activity.save(update_fields=["used_chances", "used_awards"])
        now = timezone.now()

        #发放奖品

        if gift:
            gift_name = "9月pc常规"+gift.gift_name
        else:
            gift_name = "None"

        reward = Reward.objects.filter(type=gift_name,
                                       is_used=False,
                                       end_time__gte=now).first()

        inside_message.send_one.apply_async(kwargs={
            "user_id": self.request.user.id,
            "title": reward.description,
            "content": reward.content,
            "mtype": "activity"
        })

        to_json_response = {
            'ret_code': 3014,
            'total_chances': user_activity.total_chances,
            'used_chances': user_activity.used_chances,
            'gift': gift.gift_name,
            'message': u'获得非现金奖项',
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    def get_money_action(self):
        user_activity = WanglibaoActivityReward.objects.filter(user=self.request.user.id).first()
        if user_activity.total_chances <= user_activity.used_chances:
            to_json_response = {
                'ret_code': 3024,
                'total_chances': user_activity.total_chances,
                'used_chances': user_activity.used_chances,
                'gift': u'None',
                'message': u'您的抽奖机会已经用完了',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')
        else:
            join_log = ActivityJoinLog.objects.filter(action_name='common_award_sepetember', user=self.request.user, amount__gt=0).first()
            if join_log and join_log.join_times == 0:
                to_json_response = {
                    'ret_code': 3025,
                    'type': "money",
                    'message': u'您的奖品已经被领走了',
                }
                return HttpResponse(json.dumps(to_json_response), content_type='application/json')


        join_log = ActivityJoinLog.objects.filter(action_name='common_award_sepetember', user=self.request.user, amount__gt=0).first()
        if join_log:
            join_log.join_times = 0
            join_log.save(update_fields=["join_times"])

        user_activity = WanglibaoActivityReward.objects.filter(user=self.request.user.id).first()
        user_activity.used_chances += 1
        user_activity.used_awards += 1
        user_activity.save(update_fields=["used_chances", "used_awards"])

        describe = 'common_september_' + str(int(join_log.amount))
        try:
            dt = timezone.datetime.now()
            redpack_event = RedPackEvent.objects.filter(invalid=False, describe=describe, give_start_at__lte=dt, give_end_at__gte=dt).first()
        except Exception, reason:
            logger.debug("send redpack Exception, msg:%s" % (reason,))

        if redpack_event:
            redpack_backends.give_activity_redpack(self.request.user, redpack_event, 'pc')

        to_json_response = {
            'ret_code': 3015,
            'total_chances': user_activity.total_chances,
            'used_chances': user_activity.used_chances,
            'money': str(join_log.amount),
            'message': u'获得现金奖项',
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    def update_total_chances_and_awards(self):
        """
            每次进入转盘页面，如果用户是第一次玩，会创建WanglibaoActivityReward记录
        """
        user_activity = WanglibaoActivityReward.objects.filter(user=self.request.user).first()
        if not user_activity:
            user_activity = WanglibaoActivityReward.objects.create(
                user=self.request.user,
                activity_id='common_award_sepetember',
                total_chances=3,  # 共有三次抽奖机会
                used_chances=0,
                total_awards=1,  # 有一次必中现金
                used_awards=0)

            activity = ActivityJoinLog.objects.create(
                user=self.request.user,
                action_name=u'common_award_sepetember',
                action_type=u'login',
                action_message=u'九月PC常规活动',
                channel=u'all',
                gift_name=u'现金红包',
                amount=0,
                join_times=1,
                create_time=timezone.now(),
            )

            join_log = ActivityJoinLog.objects.filter(action_name='common_award_sepetember', user=self.request.user, amount=0).order_by('-create_time').first()
            join_log.amount = self.get_award_mount(activity.id)
            join_log.save(update_fields=['amount'])

            activity = ActivityJoinLog.objects.create(
                user=self.request.user,
                action_name=u'common_award_sepetember',
                action_type=u'login',
                action_message=u'九月PC常规活动',
                channel=u'all',
                gift_name=u"None",
                amount=0,
                join_times=0,
                create_time=timezone.now(),
            )

            gift = ActivityJoinLog.objects.filter(action_name='common_award_sepetember', user=self.request.user, gift_name=u"None").order_by('-create_time').first()
            gift.gift_name = self.get_award_gift(activity.id)
            if gift.gift_name != u"None":
                gift.join_times = 1
                gift.save(update_fields=['join_times', 'gift_name'])

                user_activity = WanglibaoActivityReward.objects.filter(user=self.request.user).first()
                user_activity.total_awards += 1
                user_activity.save(update_fields=['total_awards'])

        else:
            gift = ActivityJoinLog.objects.filter(action_name='common_award_sepetember', user=self.request.user).exclude(gift_name=u'现金红包').first()
            join_log = ActivityJoinLog.objects.filter(action_name='common_award_sepetember', user=self.request.user, amount__gt=0).first()

        to_json_response = {
            'ret_code': 3012,
            'total_chances': user_activity.total_chances,
            'used_chances': user_activity.used_chances,
            'amount': str(join_log.amount),
            'amount_left': join_log.join_times,
            'gift': gift.gift_name,
            'gift_left':gift.join_times,
            'message': u'获得用户抽奖信息',
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')
