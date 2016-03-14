# encoding:utf-8
from wanglibao_reward.models import WanglibaoActivityReward as ActivityReward
import base64
import hashlib
import os
import json
import decimal
import pytz
from datetime import date, timedelta, datetime
from collections import defaultdict
from decimal import Decimal
import time
from weixin.models import WeixinUser
from wanglibao_p2p.models import P2PEquity
from django.db import transaction
from django.db.models import Count, Sum, connection
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator, PageNotAnInteger
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from wanglibao_p2p.models import P2PRecord
from django.views.generic import TemplateView
from django.http.response import HttpResponse, Http404, HttpResponseRedirect
from mock_generator import MockGenerator
from django.conf import settings
from django.db.models.base import ModelState
from wanglibao_sms.utils import send_validation_code, validate_validation_code
from misc.models import Misc
from weixin.base import OpenIdBaseAPIView, BaseWeixinTemplate
from wanglibao_sms.models import *
from marketing.models import WanglibaoActivityReward, Channels, PromotionToken, IntroducedBy, IntroducedByReward, \
    Reward, ActivityJoinLog, QuickApplyInfo, GiftOwnerGlobalInfo, GiftOwnerInfo, WanglibaoVoteCounter
from marketing.tops import Top
from utils import local_to_utc
from wanglibao_reward.models import WanglibaoWeixinRelative
# used for reward
from wanglibao_profile.models import Account2015
from weixin.models import WeixinAccounts
import cStringIO
from wanglibao_account.utils import FileObject
from django.forms import model_to_dict
from django.db.models import Q
from marketing.models import RewardRecord, NewsAndReport
from wanglibao_p2p.models import Earning
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao.templatetags.formatters import safe_phone_str
from order.models import Order
from order.utils import OrderHelper
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from wanglibao_redpack.models import RedPackEvent
from wanglibao_redpack import backends as redpack_backends
from wanglibao_activity.models import ActivityRecord, Activity, ActivityRule
from wanglibao_account import message as inside_message
from wanglibao_account.models import Binding
from wanglibao_pay.models import PayInfo
from wanglibao_activity.models import TRIGGER_NODE
from marketing.utils import get_user_channel_record
from wanglibao_p2p.models import EquityRecord
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao.templatetags.formatters import safe_phone_str
from wanglibao.settings import XUNLEIVIP_REGISTER_KEY
import urllib
import hashlib
import logging
import qrcode
from wanglibao_reward.models import WanglibaoActivityReward
logger = logging.getLogger('marketing')
TRIGGER_NODE = [i for i, j in TRIGGER_NODE]

import re
import sys
import time
from smtplib import SMTP
from email.header import Header
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from rest_framework import renderers
from django.core.urlresolvers import reverse
from misc.views import MiscRecommendProduction
from marketing.utils import pc_data_generator
from wanglibao_account.cooperation import CoopRegister
from wanglibao_account.utils import xunleivip_generate_sign
from weixin.base import ChannelBaseTemplate
from wanglibao_rest.utils import get_client_ip
reload(sys)

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


class TvViewInside(TemplateView):
    template_name = 'tv_inside.jade'

    def get_context_data(self, **kwargs):
        return {}


class AppShareView(TemplateView):
    template_name = 'app_invite_friends.jade'

    def get_context_data(self, **kwargs):
        try:
            identifier = self.request.GET.get('p')
            friend_phone = base64.b64decode(identifier + '=')
        except:
            identifier = self.request.GET.get('phone')
            friend_phone = identifier

        # 网站数据
        m = MiscRecommendProduction(key=MiscRecommendProduction.KEY_PC_DATA, desc=MiscRecommendProduction.DESC_PC_DATA)
        site_data = m.get_recommend_products()
        if site_data:
            site_data = site_data[MiscRecommendProduction.KEY_PC_DATA]
        else:
            site_data = pc_data_generator()
            m.update_value(value={MiscRecommendProduction.KEY_PC_DATA: site_data})

        identifier_result = identifier and identifier.strip() or identifier
        return {
            'site_data': site_data,
            'identifier': identifier_result,
            'friend_phone': friend_phone,
        }


class AppShareViewShort(TemplateView):
    template_name = 'app_invite_friends.jade'

    def get_context_data(self, **kwargs):
        try:
            identifier = self.request.GET.get('p')
            friend_phone = base64.b64decode(identifier + '=')
        except:
            identifier = self.request.GET.get('phone')
            friend_phone = identifier

        if friend_phone:
            try:
                user = User.objects.get(wanglibaouserprofile__phone=friend_phone)
                promo_token = PromotionToken.objects.get(user=user)
                invite_code = promo_token.token
            except:
                invite_code = ''
        else:
            invite_code = ''

        # 网站数据
        m = MiscRecommendProduction(key=MiscRecommendProduction.KEY_PC_DATA, desc=MiscRecommendProduction.DESC_PC_DATA)
        site_data = m.get_recommend_products()
        if site_data:
            site_data = site_data[MiscRecommendProduction.KEY_PC_DATA]
        else:
            site_data = pc_data_generator()
            m.update_value(value={MiscRecommendProduction.KEY_PC_DATA: site_data})

        url = self.request.get_host() + self.request.get_full_path()
        return {
            'site_data': site_data,
            'invite_code': invite_code,
            'friend_phone': friend_phone,
            'url': url
        }

class AppShareViewError(TemplateView):
    template_name = 'app_invite_error.jade'

    def get_context_data(self, **kwargs):
        try:
            identifier = kwargs['phone']
            phone = base64.b64decode(identifier + '=')
        except:
            phone = ''
        url = self.request.get_host() + '/aws/?p=' + identifier

        return {
            'phone': phone,
            'url': url
        }

class AppShareViewSuccess(TemplateView):
    template_name = 'app_invite_success.jade'

    def get_context_data(self, **kwargs):
        try:
            identifier = kwargs['phone']
            phone = base64.b64decode(identifier + '=')
        except:
            phone = ''
        url = self.request.get_host() + '/aws/?p=' + identifier
        return {
            'phone': phone,
            'url': url
        }


class AppShareRegView(TemplateView):
    template_name = 'app_share_reg.jade'

    def get_context_data(self, **kwargs):
        identifier = self.request.GET.get('identifier').strip()
        friend_identifier = self.request.GET.get('friend_identifier').strip()

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


class ShortAppShareRegView(TemplateView):
    template_name = 'app_share_reg.jade'

    def get_context_data(self, **kwargs):
        try:
            identifier = self.request.GET.get('i')
            identifier = base64.b64decode(identifier + '=')
            friend_identifier = self.request.GET.get('fi')
            try:
                friend_identifier = str(int(friend_identifier))
            except:
                friend_identifier = base64.b64decode(friend_identifier + '=')
        except Exception, e:
            print e
            identifier = self.request.GET.get('identifier').strip()
            friend_identifier = self.request.GET.get('friend_identifier').strip()

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

    template_name = 'media_coverage.jade'

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

def get_left_awards(init=108000):
    return init-ActivityJoinLog.objects.filter(action_name='oct_get_award', join_times=0).count()

def ajax_xunlei(request):
    """
        description:迅雷抽奖活动，响应web的ajax请求
    """
    user = request.user
    if not user.is_authenticated():
        to_json_response = {
            'ret_code': 3000,
            'message': u'用户没有登陆，请先登陆',
            'award': get_left_awards()
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    record = get_user_channel_record(user.id)
    try:
        key = 'xunlei_event'
        event = Misc.objects.filter(key=key).first()
        if event:
            event = json.loads(event.value)
            logger.debug("event value:%s" %(event,))
            if type(event) == dict:
                channel = event['channel']
                reward = event['reward']
    except Exception, reason:
        logger.exception('get misc record exception, msg:%s' % (reason,))
        raise
    if not record or (record and record.name != channel):
        to_json_response = {
            'ret_code': 4000,
            'message': u'非迅雷渠道过来的用户',
            'award': get_left_awards()
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    if request.method == "POST":
        obj = ThunderInterestAwardAPIView()
        action = request.POST.get("action", "")
        logger.debug("迅雷10月  action type:%s" %(action,))
        if action == 'GET_RECORD':
            obj.get_reward_record(request, 'oct_get_award')

        if action == 'GET_AWARD':
            res = obj.get_award(request, reward)

        if action == 'IGNORE_AWARD':
            res = obj.ignore_award(request)

        if action == 'ENTER_WEB_PAGE':
            res = obj.enter_webpage(request)

        return res


class ThunderInterestAwardAPIView(APIView):
    """
        description: 迅雷抽奖活动1.用户有三次摇奖机会，三次摇奖必中奖一次，中奖内容为加息券，
                    中奖后提示中奖金额及中奖提示语，非中奖用户提示非中奖提示语。
    """

    def get_left_awards(self, init=108000):
       return init-ActivityJoinLog.objects.filter(action_name='oct_get_award', join_times=0).count()

    def get_award(self, request, reward):
        """
            TO-WRITE
        """
        join_log = ActivityJoinLog.objects.filter(user=request.user).first()
        if join_log.join_times == 0:
            to_json_response = {
                'ret_code': 3100,
                'get_time': (join_log.id % 3)+1,  # 第几次抽中
                'left': join_log.join_times,  # 还剩几次
                'amount': str(join_log.amount),  # 加息额度
                'message': u'抽奖机会已经用完了',
                'award': self.get_left_awards()
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')
        join_log.join_times -= 1
        join_log.save(update_fields=['join_times'])
        money = self.get_award_mount(join_log.id)
        describe = str(reward) + str(money)
        try:
            dt = timezone.datetime.now()
            logger.debug("select condition-- invalid:False, describe:%s, give_start&give_end:%s",(describe, dt,))
            redpack_event = RedPackEvent.objects.filter(invalid=False, describe=describe, give_start_at__lte=dt, give_end_at__gte=dt).first()
        except Exception, reason:
            print reason

        if redpack_event:
            logger.debug("发送出去的加息券, user:%s, redpack:%s" %(request.user, redpack_event,))
            redpack_backends.give_activity_redpack(request.user, redpack_event, 'pc')

        to_json_response = {
            'ret_code': 3001,
            'get_time': (join_log.id % 3)+1,  # 第几次抽中
            'left': join_log.join_times,  # 还剩几次
            'amount': str(join_log.amount),  # 加息额度
            'message': u'终于等到你，还好我没放弃',
            'award': self.get_left_awards()
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    def get_reward_record(self, request, action):
        records = ActivityJoinLog.objects.filter(action_name=action, action_type='login', join_times=0, amount__gt=0)
        data = [{'phone': record.user.wanglibaouserprofile.phone, 'awards': float(record.amount)} for record in records]
        to_json_response = {
            'ret_code': 3005,
            'data': data,
            'message': u'获得抽奖成功用户',
            'award': self.get_left_awards()
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    def ignore_award(self, request):
        """
            将剩余的刮奖次数减1，并返回最终结果
        """
        join_log = ActivityJoinLog.objects.filter(user=request.user).first()
        if join_log.join_times > 0:
            join_log.join_times -= 1
        else:
            to_json_response = {
                'ret_code': 3100,
                'get_time': (join_log.id % 3)+1,  # 第几次抽中
                'left': join_log.join_times,  # 还剩几次
                'amount': str(join_log.amount),  # 加息额度
                'message': u'抽奖机会已经用完了',
                'award': self.get_left_awards()
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        join_log.save(update_fields=['join_times'])
        to_json_response = {
            'ret_code': 3002,
            'get_time': (join_log.id % 3)+1,  # 第几次抽中
            'left': join_log.join_times,  # 还剩几次
            'amount': str(join_log.amount),  # 加息额度
            'message': u'你和大奖只是一根头发的距离',
            'award': self.get_left_awards()
        }

        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    def get_award_mount(self, index):
        index %= 10
        if index in (0,):
            return 0.5
        if index in(3, 6, 9):
            return 0.5
        if index in(1, 2, 4, 5, 7, 8):
            return 0.5

    def enter_webpage(self, request):
        """
            进入页面的时候，判断是否生成记录，如果没有则生成并返回剩余刮奖次数3；如果有，则直接返回剩余刮奖次数；
        """
        join_log = ActivityJoinLog.objects.filter(user=request.user).first()
        if not join_log:
            join_log = ActivityJoinLog.objects.create(
                user=request.user,
                action_name=u'oct_get_award',
                action_type=u'login',
                action_message=u'迅雷抽奖活动',
                channel=u'all',
                gift_name=u'抽得加息券',
                amount=0,
                join_times=3,
                create_time=timezone.now(),
            )

            join_log.amount = self.get_award_mount(join_log.id)
            join_log.save(update_fields=['amount'])

        to_json_response = {
            'ret_code': 3003,
            'get_time': (join_log.id % 3)+1,  # 第几次抽中
            'left': join_log.join_times,  # 还剩几次
            'amount': str(join_log.amount),  # 加息额度
            'message': u'欢迎刮奖',
            'award': self.get_left_awards()
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')


def ajax_post(request):
    """
        description:迅雷9月抽奖活动，响应web的ajax请求
    """
    user = request.user
    if not user.is_authenticated():
        to_json_response = {
            'ret_code': 3000,
            'message': u'用户没有登陆，请先登陆',
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    record = get_user_channel_record(user.id)
    try:
        key = 'xunlei_event'
        event = Misc.objects.filter(key=key).first()
        if event:
            event = json.loads(event.value)
            if type(event) == dict:
                channel = event['channel']
                reward = event['reward']
    except Exception, reason:
        logger.exception('get misc record exception, msg:%s' % (reason,))
        raise
    if not record or (record and record.name != channel):
        to_json_response = {
            'ret_code': 4000,
            'message': u'非迅雷渠道(%s)过来的用户' %(eval(request.GET.get('prom_token',"None")),)
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    if request.method == "POST":
        obj = ThunderAwardAPIView()
        action = request.POST.get("action", "")
        logger.debug("迅雷9月  action type:%s" %(action,))

        if action == 'GET_AWARD':
            res = obj.get_award(request, reward)

        if action == 'IGNORE_AWARD':
            res = obj.ignore_award(request)

        if action == 'ENTER_WEB_PAGE':
            res = obj.enter_webpage(request)

        return res


class ThunderAwardAPIView(APIView):
    """
        description: 迅雷抽奖活动1.用户有三次摇奖机会，三次摇奖必中奖一次，中奖金额分别为100元（30%）、
                    150元（60%）、 200元（10%），中奖后提示中奖金额及中奖提示语，非中奖用户提示非中奖提示语。
    """

    def get_award(self, request, reward):
        """
            TO-WRITE
        """
        join_log = ActivityJoinLog.objects.filter(user=request.user).first()
        if join_log.join_times == 0:
            to_json_response = {
                'ret_code': 3100,
                'get_time': (join_log.id % 3)+1,  # 第几次抽中
                'left': join_log.join_times,  # 还剩几次
                'amount': str(join_log.amount),  # 奖励的金额
                'message': u'抽奖机会已经用完了',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')
        join_log.join_times -= 1
        join_log.save(update_fields=['join_times'])
        money = self.get_award_mount(join_log.id)
        describe = str(reward) + str(money)
        try:
            dt = timezone.datetime.now()
            redpack_event = RedPackEvent.objects.filter(invalid=False, describe=describe, give_start_at__lte=dt, give_end_at__gte=dt).first()
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
        else:
            to_json_response = {
                'ret_code': 3100,
                'get_time': (join_log.id % 3)+1,  # 第几次抽中
                'left': join_log.join_times,  # 还剩几次
                'amount': str(join_log.amount),  # 奖励的金额
                'message': u'抽奖机会已经用完了',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

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


def get_first_pay_info(user_id, start_time, end_time):
    try:
        payinfo = PayInfo.objects.filter(user_id=user_id, create_time__gte=start_time,
                                         create_time__lte=end_time).order_by('create_time')
        first_pay_info = payinfo[0]
    except:
        first_pay_info = None
    return first_pay_info


class UserActivityStatusAPIView(APIView):
    """
    用户活动状态查询接口
    """
    permission_classes = (IsAuthenticated, )

    def get_activity_info(self, activity_id):
        try:
            activity_info = Activity.objects.get(id=activity_id)
        except:
            activity_info = None
        return activity_info

    def check_params(self, activity_id, trigger_node):
        json_response = {}
        if not activity_id:
            json_response = {
                'ret_code': '20002',
                'message': u'activity_id参数缺失'
            }

        if not trigger_node:
            json_response = {
                'ret_code': '20003',
                'message': u'trigger_node参数缺失'
            }

        elif trigger_node not in TRIGGER_NODE:
            json_response = {
                'ret_code': '30003',
                'message': u'不存在的trigger_node'
            }

        return json_response

    def get_activitys_rule_min_amount(self, activity_id, trigger_node):
        min_amount = None
        try:
            min_amount = ActivityRule.objects.filter(activity_id=activity_id, trigger_node=trigger_node,
                                                     is_used=True).order_by('min_amount')[0]
        except:
            pass
        return min_amount

    def get_user_cost_info(self, user_id, trigger_node):
        # 获取用户支付或投资的记录
        cost_info = None
        if trigger_node == 'first_pay':
            cost_info = PayInfo.objects.filter(user_id=user_id)
        elif trigger_node == 'first_buy':
            cost_info = P2PRecord.objects.filter(user_id=user_id)
        return cost_info

    def get_activity_user_validation_status(self, activity_record, user, activity_starttime):
        # 判断用户是否在活动期间实名，并生成返回信息
        userprofile = user.wanglibaouserprofile
        if activity_record:
            json_response = {
                'ret_code': '10001',
                'message': u'用户已参加过活动'
            }
        elif userprofile.id_is_valid:
            if userprofile.id_valid_time < activity_starttime:
                json_response = {
                    'ret_code': '00003',
                    'message': u'实名时间不符合活动条件'
                }
            else:
                json_response = {
                    'ret_code': '00001',
                    'message': u'用户未参加活动，已达到活动条件'
                }
        else:
            json_response = {
                'ret_code': '00000',
                'message': u'用户未实名'
            }
        return json_response

    def get_activity_user_register_status(self, activity_record):
        # 判断用户是否在活动期间注册，并生成返回信息
        if activity_record:
            json_response = {
                'ret_code': '10001',
                'message': u'用户已参加过活动'
            }
        else:
            json_response = {
                'ret_code': '00000',
                'message': u'用户未达到活动条件'
            }
        return json_response

    def get_activity_user_first_cost_status(self, activity_record, activity_info,
                                            cost_record, activity_id, trigger_node):
        # 获取用户活动期间内的首次支付以及首次投资的记录
        json_response = {}
        starttime = activity_info.start_at
        endtime = activity_info.end_at
        try:
            frist_cost_record = cost_record.filter(create_time__gte=starttime,
                                                   create_time__lte=endtime).order_by('create_time')[0]
        except:
            frist_cost_record = None

        # 判断用户是否在活动期间完成首次支付或者首投的动作，是否满足活动条件，并生成返回信息
        amount = frist_cost_record.amount if frist_cost_record else None
        if activity_record:
            if frist_cost_record:
                json_response = {
                    'ret_code': '10001',
                    'message': u'用户已参加活动',
                }
        else:
            min_pay_amount = self.get_activitys_rule_min_amount(activity_id, trigger_node)
            if frist_cost_record:
                if min_pay_amount and amount >= min_pay_amount:
                    json_response = {
                        'ret_code': '00001',
                        'message': u'用户未参加活动，已达到活动条件',
                    }
                else:
                    json_response = {
                        'ret_code': '00000',
                        'message': u'用户未达到活动条件',
                    }
            else:
                json_response = {
                    'ret_code': '00002',
                    'message': u'用户活动期内没有开销记录',
                }
        return json_response

    def get_user_channel(self, user_id):
        # 判断用户是否属于活动指定渠道用户
        Introducedby = IntroducedBy.objects.filter(user_id=user_id).first()
        if Introducedby:
            if Introducedby.channel:
                channel_name = Introducedby.channel.name
            if not Introducedby.channel_id:
                channel_name = 'wanglibao'
        else:
            channel_name = 'wanglibao-other'
        return channel_name

    def get(self, request):
        activity_id = request.GET.get('activity_id', None)
        trigger_node = request.GET.get('trigger_node', None)
        user = request.user
        activity_info = None
        # 校验参数是否有效
        json_response = self.check_params(activity_id, trigger_node)
        if not json_response:
            activity_info = self.get_activity_info(activity_id)
            if activity_info:
                channel_code = self.get_user_channel(user.id)
                activity_channel = activity_info.channel
                if not activity_info.is_all_channel:
                    if activity_channel and channel_code not in activity_channel.split(','):
                        json_response = {
                            'ret_code': '00005',
                            'message': u'非活动指定渠道用户'
                        }
            else:
                json_response = {
                    'ret_code': '30002',
                    'message': u'不存在的activity_id'
                }

        if not json_response:
            activity_record = ActivityRecord.objects.filter(user_id=user.id, activity__id=activity_id,
                                                            trigger_node=trigger_node).first()
            if trigger_node == 'register':
                json_response = self.get_activity_user_register_status(activity_record)
            elif trigger_node == 'validation':
                json_response = self.get_activity_user_validation_status(activity_record, user,
                                                                         activity_info.start_at)
            elif trigger_node in ('first_pay', 'first_buy'):
                cost_record = self.get_user_cost_info(user.id, trigger_node)
                if cost_record.exists():
                    if cost_record.filter(create_time__lt=activity_info.start_at).exists():
                        json_response = {
                            'ret_code': '00000',
                            'message': u'用户未达到活动条件'
                        }
                    else:
                        json_response = self.get_activity_user_first_cost_status(activity_record, activity_info,
                                                                                 cost_record, activity_id, trigger_node)
                else:
                    json_response = {
                        'ret_code': '00002',
                        'message': u'用户没有开销记录'
                    }

        if not json_response:
            json_response = {
                'ret_code': '50000',
                'message': u'异常查询'
            }
        return HttpResponse(json.dumps(json_response), content_type='application/json')


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
        activity_start = time.mktime(datetime(2014, 1, 1).timetuple())  # 活动开始时间

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
    print "Action from Application:%s" % (action,)
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
        if action == 'REPEAT':
            return activity.user_repeat_action()

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
        activity_start = time.mktime(datetime(2014, 1, 1).timetuple())  # 活动开始时间

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

    def user_repeat_action(self):
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

        to_json_response = {
            'ret_code': 3033,
            'total_chances': user_activity.total_chances,
            'used_chances': user_activity.used_chances,
            'message': u'app端，重复刮卡请求',
        }
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

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
                user_activity.used_chances += 1
                user_activity.save(update_fields=["used_chances"])
                to_json_response = {
                    'ret_code': 3025,
                    'type': "gift",
                    'used_chances': user_activity.used_chances,
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

        reward = Reward.objects.filter(type=gift_name.strip(),
                                       is_used=False,
                                       end_time__gte=now).first()

        inside_message.send_one.apply_async(kwargs={
            "user_id": self.request.user.id,
            "title": reward.description,
            "content": reward.content,
            "mtype": "activity"
        })
        reward.is_used = True
        reward.save()

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
                user_activity.used_chances += 1
                user_activity.save(update_fields=["used_chances"])
                to_json_response = {
                    'ret_code': 3025,
                    'type': "money",
                    'used_chances': user_activity.used_chances,
                    'message': u'您的奖品已经被领走了',
                }
                return HttpResponse(json.dumps(to_json_response), content_type='application/json')


        join_log = ActivityJoinLog.objects.filter(action_name='common_award_sepetember', user=self.request.user, amount__gt=0).first()
        if join_log:
            join_log.join_times = 0
            join_log.save(update_fields=["join_times"])

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


class ThunderTenAcvitityTemplate(ChannelBaseTemplate):
    template_name = 'xunlei_three.jade'
    wx_code = ''

    def check_params(self, channel_code, sign, _time, nickname, user_id):
        response_data = {}
        channel_codes = ('xunlei9', 'mxunlei')
        if not channel_code or channel_code not in channel_codes:
            response_data = {
                'ret_code': '20001',
                'message': u'非法请求',
            }
        elif not sign:
            response_data = {
                'ret_code': '10001',
                'message': u'签名不存在',
            }
        elif not nickname:
            response_data = {
                'ret_code': '10003',
                'message': u'用户昵称不存在',
            }
        elif not _time:
            response_data = {
                'ret_code': '10005',
                'message': u'时间戳不存在',
            }
        elif not user_id:
            response_data = {
                'ret_code': '10007',
                'message': u'用户ID不存在',
            }

        return response_data

    def get_context_data(self, **kwargs):
        params = self.request.GET
        sign = params.get('sign', '').strip()
        _time = params.get('time', '').strip()
        nickname = params.get('nickname', '').strip()
        user_id = params.get('xluserid', '').strip()
        channel_code = params.get('promo_token', '').strip()
        response_data = self.check_params(channel_code, sign, _time, nickname, user_id)

        self.wx_code = channel_code
        context = super(ThunderTenAcvitityTemplate, self).get_context_data(**kwargs)

        device_list = ['android', 'iphone']
        user_agent = self.request.META.get('HTTP_USER_AGENT', "").lower()
        for device in device_list:
            match = re.search(device, user_agent)
            if match and match.group():
                self.template_name = 'app_xunlei.jade'

        if not response_data:
            check_data = {
                'time': _time,
                'xluserid': user_id,
            }

            if len(nickname) > 3:
                nickname = nickname[:3]+'...'

            if xunleivip_generate_sign(check_data, XUNLEIVIP_REGISTER_KEY) == sign:
                response_data = {
                    'ret_code': '10000',
                    'message': 'success',
                    'nickname': nickname,
                }
            else:
                response_data = {
                    'ret_code': '10002',
                    'message': u'签名错误',
                }

        context.update(response_data)
        return context


class QuickApplyerAPIView(APIView):
    permission_classes = ()

    def send_mail(self, sender, reciver, title, body):
        SMTPSVR = 'smtp.exmail.qq.com'
        user = 'develop@wanglibank.com'
        pw = 'abc&321'
        msg = MIMEMultipart()
        msg['From'] = '%s <%s>' % (Header('网利技术服务', 'utf-8'), sender)
        if isinstance(reciver, list):
            msg['To'] = ';'.join(reciver)
        else:
            msg['To'] = reciver
        msg['Subject'] = Header(title, 'utf-8')
        msg['Accept-Language'] = 'zh-CN'
        msg['Accept-Charset'] = 'ISO-8859-1,utf-8'
        body = MIMEText(body, 'html', 'utf-8')
        body.set_charset('utf-8')
        msg.attach(body)
        sendSvr = SMTP(SMTPSVR, 25)
        sendSvr.login(user, pw)
        sendSvr.sendmail(sender, reciver, msg.as_string())
        sendSvr.quit()

    def post(self, request):
        email ={
        u"北京": 'beijingoffice@wanglibank.com',
        u"上海": 'shanghaioffice@wanglibank.com',
        u"中山": 'zhongshanoffice@wanglibank.com',
        u"深圳": 'shenzhenoffice@wanglibank.com',

        u"天津": 'tianjinoffice@wanglibank.com',
        u"长沙": 'changshaoffice@wanglibank.com',
        u"武汉": 'wuhanoffice@wanglibank.com',
        u"贵阳": 'guiyangoffice@wanglibank.com',

        u"西安": 'xianoffice@wanglibank.com',
        u"青岛": 'qingdaooffice@wanglibank.com',
        u"石家庄": 'shijiazhuangoffice@wanglibank.com',
        u"海口": 'haikouoffice@wanglibank.com',

        u"郑州": 'zhengzhouoffice@wanglibank.com',
        u"重庆": 'chongqingoffice@wanglibank.com',
        u"其它": 'qitachengshioffice@wanglibank.com',
        }

        apply = {
            0: u'我有房',
            1: u'我有车',
            2: u'其它',
        }

        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        apply_way = request.POST.get('apply_way', '')
        amount = request.POST.get('amount', '')

        if not(name and phone and address and apply_way and amount):
            to_json_response = {
                'ret_code': 1000,
                'message': u'您的输入信息有遗漏'
            }

            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        mytime = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')+timedelta(days=-7)
        last_register = datetime.strftime(mytime, '%Y-%m-%d %H:%M:%S')
        applyer = QuickApplyInfo.objects.filter(phone=phone, create_time__gte=last_register)
        if applyer.count() >= 2:
            to_json_response = {
                'ret_code': '1001',
                'message': u"您已提交过申请，请等待业务人员联系"
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        try:
            applyer = QuickApplyInfo.objects.create(
                name=name,
                phone=phone,
                address=address,
                apply_way=apply_way,
                apply_amount=amount
            )
        except Exception, reason:
            logger.debug("贷款专区，申请人数据入库报异常, reason:%s" % (reason,))
            to_json_response = {
                'ret_code': '1002',
                'message': u"申请人信息入库异常"
            }

            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        title = "[%s - %s]贷款申请" % (address, apply[int(apply_way)])
        body = "姓名:%s <br/> 手机号:%s<br/> 城市:%s<br/> 资产状况:%s<br/> 贷款金额:%s<br/>" % (name, phone, address,apply[int(apply_way)], amount)
        self.send_mail('develop@wanglibank.com', email[address], title, body)
        to_json_response = {
            'ret_code': '0',
            'message': u"提交成功,请您耐心等待"
        }

        return HttpResponse(json.dumps(to_json_response), content_type='application/json')


class GiftOwnerInfoAPIView(APIView):
    permission_classes = ()

    def get_left_awards(self):
        items = GiftOwnerGlobalInfo.objects.filter(description__in=('jcw_ticket_80', 'jcw_ticket_188')).values("amount", "description")
        for item in items:
            if item["description"] == "jcw_ticket_80":
                jcw_ticket_80 = item["amount"]
            elif item["description"] == "jcw_ticket_188":
                jcw_ticket_188 = item["amount"]
        return jcw_ticket_80, jcw_ticket_188

    def post(self, request):
        action = request.DATA.get('action', 'OTHERS')
        name = request.DATA.get('name', '')
        phone = request.DATA.get('phone', '')
        address = request.DATA.get('address', '')

        try:
            (award80, award188) = self.get_left_awards()
        except Exception, reason:
            logger.exception(u'获取门票global配置报异常, reason:%s' % (reason,))
            to_json_response = {
                'ret_code': 1002,
                'message': u'门票配置报异常',
                'award80': -1,
                'award100': -1
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        if action == 'VALIDATION':
            status, message = validate_validation_code(request.DATA.get("phone", ""), request.DATA.get("validation", ""))
            to_json_response = {
                'ret_code': 1,
                'message': message,
                'status': status
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        if action == "ENTER_WEB_PAGE":
            to_json_response = {
                'ret_code': 1,
                'message': u'首次进入页面',
                'award80': award80,
                'award100': award188
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        item = GiftOwnerInfo.objects.filter(config__description__in=('jcw_ticket_80', 'jcw_ticket_188'), sender=request.user)
        if action == "HAS_TICKET":
            to_json_response = {
                'ret_code': 2,
                'message': u'判断是否领过票',
                'award80': award80,
                'award100': award188,
                'has_ticket': "True" if item.exists() else "False"
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        if not self.request.user.is_authenticated():
            to_json_response = {
                'ret_code': 1030,
                'message': u'请先登录，再领取奖品',
                'award80': award80,
                'award100': award188
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        record = get_user_channel_record(request.user.id)
        if not record or (record and record.name != 'jcw'):
            to_json_response = {
                'ret_code': 1000,
                'message': u'用户不是聚橙网渠道',
                'award80': award80,
                'award100': award188
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        if item.exists():
            to_json_response = {
                'ret_code': 1010,
                'message': u'您已经领取过门票，不可重复领取',
                'award80': award80,
                'award100': award188
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        binding = Binding.objects.filter(user_id=request.user.id).first()
        p2p_record = P2PRecord.objects.filter(user_id=request.user.id, catalog=u'申购')
        if binding and p2p_record.count() == 1:
            p2p_amount = int(p2p_record.first().amount)
            if p2p_amount >= 500 and p2p_amount < 1000:
                try:
                    config = GiftOwnerGlobalInfo.objects.select_for_update(description=u'jcw_ticket_80', valid=True).first()
                except Exception, reason:
                    logger.debug(u"获取奖品信息全局配置表报异常,reason:%s" % (reason,))
                    raise
                if config and config.amount>0:
                    try:
                        GiftOwnerInfo.objects.create(
                            sender=self.request.user,
                            config=config,
                            name=name,
                            phone=phone,
                            address=address,
                            award=u'张昊辰门票',
                            type='80'
                        )
                    except Exception, reason:
                        logger.exception(u'获奖用户(%s)信息入库失败, reason:%s' % (self.request.user,reason))
                        config.save()
                    else:
                        config.amount -= 1
                        config.save()
                        logger.info(u"获奖用户 (%s) 信息入库成功" % (self.request.user,))
                        to_json_response = {
                            'ret_code': 0,
                            'message': u'获得80元没票一张',
                            'award80': award80-1,
                            'award100': award188
                        }
                        return HttpResponse(json.dumps(to_json_response), content_type='application/json')

            elif p2p_amount >= 1000:
                try:
                    config = GiftOwnerGlobalInfo.objects.select_for_update(description=u'jcw_ticket_188', valid=True).first()
                except Exception, reason:
                    logger.debug(u"获取奖品信息全局配置表报异常,reason:%s" % (reason,))
                    raise
                if config and config.amount > 0:
                    try:
                        GiftOwnerInfo.objects.create(
                            sender=self.request.user,
                            config=config,
                            name=name,
                            phone=phone,
                            address=address,
                            award=u'张昊辰门票',
                            type='188'
                        )
                    except Exception, reason:
                        logger.exception(u'获奖用户(%s)信息入库失败, reason:%s' % (self.request.user,reason))
                        config.save()
                    else:
                        config.amount -= 1
                        config.save()
                        logger.info(u"获奖用户 (%s) 信息入库成功" % (self.request.user,))
                        to_json_response={
                            'ret_code': 0,
                            'message': u'获得188元没票一张',
                            'award80': award80,
                            'award100': award188-1
                        }
                        return HttpResponse(json.dumps(to_json_response), content_type='application/json')
            else:
                to_json_response = {
                    'ret_code': 200,
                    'message': u'用户的投资额度不符合领奖规则',
                    'award80': award80,
                    'award100': award188
                }
                return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        else:
            to_json_response = {
                'ret_code': 100,
                'message': u'首投用户才有可以领取门票',
                'award80': award80,
                'award100': award188
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')


class OpenidPhoneForFencai(APIView):
    permission_classes = ()

    def post(self, request):
        openid = request.POST.get("openid")
        phone = request.POST.get("phone")
        if not openid or not phone or not phone.isdigit():
            return Response({'code': -1, "message": "error"})
        relative, created = WanglibaoWeixinRelative.objects.get_or_create(openid=openid)
        if not relative.phone_for_fencai or relative.phone_for_fencai != phone:
            relative.phone_for_fencai = phone
            relative.save()
        return Response({"code": 0, "message": "ok"})

class AppLotteryTemplate(TemplateView):
    template_name = 'app_lottery.jade'

    def get_context_data(self, *args, **kwargs):
        openid = self.request.GET.get('openid')
        phone = ""
        relative = WanglibaoWeixinRelative.objects.filter(openid=openid).first()
        if relative:
            phone = relative.phone_for_fencai
        return {
            'openid': openid,
            'phone': phone,
        }



    def dispatch(self, request, *args, **kwargs):
        openid = self.request.GET.get('openid')

        if not openid:
            redirect_uri = settings.CALLBACK_HOST + reverse("app_lottery")
            count = 0
            for key in self.request.GET.keys():
                if count == 0:
                    redirect_uri += '?%s=%s'%(key, self.request.GET.get(key))
                else:
                    redirect_uri += "&%s=%s"%(key, self.request.GET.get(key))
                count += 1
            redirect_uri = urllib.quote(redirect_uri)
            account_id = 3
            key = 'share_redpack'
            shareconfig = Misc.objects.filter(key=key).first()
            if shareconfig:
                shareconfig = json.loads(shareconfig.value)
                if type(shareconfig) == dict:
                    account_id = shareconfig['account_id']
            redirect_url = reverse('weixin_authorize_code')+'?state=%s&redirect_uri=%s' % (account_id, redirect_uri)
            # print redirect_url
            return HttpResponseRedirect(redirect_url)
        return super(AppLotteryTemplate, self).dispatch(request, *args, **kwargs)



class NoConfigException(Exception):
    def __init__(self, conf):
        self.conf = conf

    def __str__(self):
        return u'后台没有配置:  {0},'.format(self.conf)


class RewardDistributeAPIView(APIView):
    permission_classes = ()
    def __init__(self):
        super(RewardDistributeAPIView, self).__init__()
        self.activity_key = 'wechat_activity'  #Misc配置
        self.index = 0         #使用activity的index,对应MISC中的配置
        self.activitys = None
        self.activity = None
        self.redpacks = dict() #红包amount: 红包object
        self.redpack_amount = list()
        self.rates = (0.4, 1.9, 9, 13, 0.6, 2.1, 11, 12, 50)  #每一个奖品的获奖概率，按照奖品amount的大小排序对应
        self.action_name = u'weixin_distribute_redpack'

    def get_activitys_from_wechat_misc(self):
        """从misc中获得活动的值
        """
        try:
            wechat_conf = Misc.objects.filter(key=self.activity_key).first()
            if None == wechat_conf:
                raise NoConfigException("misc {0}".format(self.activity_key))

        except NoConfigException as no_conf:
            logger.exception(no_conf)
            raise
        except Exception, reason:
            logger.exception(u"获取MISC 中wechat_activity配置异常, reason:%s" % (reason, ))
            raise

        conf_value = json.loads(wechat_conf.value)
        if type(conf_value) == dict:
            try:
                self.activitys = conf_value['activity'].split(",")
            except KeyError, reason:
                logger.exception(u"misc-wechat_activity-activity key ERROR异常，reason:{0}".format(reason))
            else:
                logger.debug(u"MISC中activity的配置是%s" % (self.activitys,))


    def get_activity(self):
        try:
            self.activity = Activity.objects.filter(code=self.activitys[self.index]).first()
        except KeyError, reason:
            logger.debug(u"活动管理中没有配置activity, reason:%s" % (reason, ))
            raise

        if None == self.activity:
            raise NoConfigException(u"活动管理没有配置")

    def get_redpacks(self):
        try:
            rules = ActivityRule.objects.filter(activity=self.activity).first()
        except Exception, reason:
            logger.debug(u"rules获取抛异常, reason:%s" % (reason,))
            raise

        if None == rules:
            raise NoConfigException(u"Rule没有配置")
        try:
            redpacks = list(rules.redpack.split(","))
            logger.debug(u"后台配置的红包id是：{0}".format(redpacks))
            QSet = RedPackEvent.objects.filter(id__in=redpacks)
        except Exception, reason:
            logger.debug(u"获得配置红包报异常, reason:%s" % (reason,))
            raise
        for item in QSet:
            self.redpacks[item.amount] = item

        self.redpack_amount = sorted(self.redpacks.keys(), reverse=True)
        logger.debug(u"红包的大小依次为：%s" % (self.redpack_amount, ))
        logger.debug(u"对应红包的获奖概率是：%s" % (self.rates, ))

    def decide_which_to_distribute(self, user):
        """ 决定发送哪一个奖品
        """
        sent_count = ActivityJoinLog.objects.filter(action_name=self.action_name).count() + 1
        rate = 50

        for item in self.rates:
            if sent_count%(100/item)==0:
                rate = item
                break

        #根据rate找到对应的红包
        index = self.rates.index(rate)
        logger.debug(u"rate:{0},index:{1}, redpack_amount:{2}".format(rate,index, self.redpack_amount))
        try:
            join_log = ActivityJoinLog.objects.create(
                user=user,
                action_name=self.action_name,
                join_times=3,
                amount=self.redpack_amount[index],
            )
        except IndexError, reason:
            logger.exception(u"redpack_amount 索引超范围了,reason:{0}".format(reason))
            raise
        except Exception, reason:
            logger.exception(u"创建用户获奖记录异常了， reason:{0}".format(reason))
        else:
            logger.debug("生成用户的抽奖记录:{0}".format(join_log))
        return join_log

    @method_decorator(transaction.atomic)
    def distribute_redpack(self, user):
        """给用户发送出去一个奖品
        """
        try:
            today = time.strftime("%Y-%m-%d", time.localtime())
            join_log = ActivityJoinLog.objects.select_for_update().filter(action_name=self.action_name, user=user, create_time__gte=today).first()
            if join_log.join_times == 0:
                join_log.save()
                return "No Reward"
            else:
                redpack_event = self.redpacks.get(float(join_log.amount))
        except Exception, reason:
            logger.debug(u"获得用户的预配置红包抛异常, reason:{0}".format(reason))
        else:
            logger.debug("join_log.amount的值为:{0}, redpack_event的值为:{1}, redpacks的值为:{2}".format(join_log.amount, redpack_event, self.redpacks))

        try:
            redpack_backends.give_activity_redpack(user, redpack_event, 'pc')
        except Exception, reason:
            logger.debug(u'给用户 {0}发送红包报错, redpack_event:{1}, reason:{2}'.format(user, redpack_event,reason))
            join_log.save()
            raise
        else:
            logger.debug(u'给用户发送出去的红包大小是: {0}'.format(redpack_event.amount))
            join_log.join_times -= 1
            join_log.save()
            return join_log

    @method_decorator(transaction.atomic)
    def ignore_post_action(self, user):
        """处理用户的没有抽到奖品的动作流程
        """
        today = time.strftime("%Y-%m-%d", time.localtime())
        join_log = ActivityJoinLog.objects.select_for_update().filter(user=user, create_time__gte=today).first()
        if join_log.join_times == 0:
            join_log.save()
            return "No Chance"
        else:
            join_log.join_times -= 1
            join_log.save()
            return join_log

    def prepare_for_distribute(self):
        self.get_activitys_from_wechat_misc()
        self.get_activity()
        self.get_redpacks()

    def post(self, request):
        # openid = request.DATA.get("openid", "")
        # if None == openid:
        #     to_json_response = {
        #         'ret_code': 3010,
        #         'message': u'openid 没有传入',
        #     }
        #     return HttpResponse(json.dumps(to_json_response), content_type='application/json')
        #
        # w_user = WeixinUser.objects.filter(openid=openid)
        # if not w_user.exists() or not w_user.first().user:
        #     to_json_response = {
        #         'ret_code': 3011,
        #         'message': u'weixin info No saved',
        #     }
        #     return HttpResponse(json.dumps(to_json_response), content_type='application/json')
        # else:
        #     user = w_user.first().user
        user = request.user
        today = time.strftime("%Y-%m-%d", time.localtime())
        join_log = ActivityJoinLog.objects.filter(user=user, create_time__gte=today, action_name=self.action_name).first()

        self.prepare_for_distribute()
        if not join_log:
            logger.debug(u'用户{0}第一次进入页面，给用户生成抽奖记录'.format(user))
            join_log = self.decide_which_to_distribute(user)

        key = float("{0:.1f}".format(join_log.amount))
        redpack_event = self.redpacks.get(key)

        if join_log.join_times == 0:
            logger.debug(u'用户{0}的抽奖次数已经用完了'.format(user))
            to_json_response = {
                'ret_code': 3001,
                'message': u'用户的抽奖次数已经用完了',
                'left': 0,
                'redpack': redpack_event.id
            }

            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        action = request.DATA.get("action", "")
        logger.debug(u"用户{0}前端传入的行为是：{1}".format(user, action,))

        try:
            assert action in ("ENTER_WEB_PAGE", "GET_REWARD", "IGNORE")
        except AssertionError:
            logger.debug(u"参数不正确，action:{0}".format(action))
            to_json_response = {
                'ret_code': 3002,
                'message': u'传入的参数不正确',
            }

            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        join_log = ActivityJoinLog.objects.filter(user=user, create_time__gte=today).first()
        logger.debug(u"剩余的抽奖次数：{0}".format(join_log.join_times,))
        if action == "ENTER_WEB_PAGE":
            to_json_response = {
                'ret_code': 4000,
                'message': u'进入页面',
                'amount': str(join_log.amount),
                'left': join_log.join_times,
                'redpack': redpack_event.id
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        if action == "GET_REWARD":
            join_log = self.distribute_redpack(user)
            to_json_response = {
                'ret_code': 0,
                'message': u'发奖成功',
                'amount': str(join_log.amount),
                'left': join_log.join_times,
                'redpack': redpack_event.id
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        if action == "IGNORE":
            join_log = self.ignore_post_action(user)
            to_json_response = {
                'ret_code': 4002,
                'message': u'忽略本次操作',
                'amount': str(join_log.amount),
                'left': join_log.join_times,
                'redpack': redpack_event.id
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')


class RockFinanceQRCodeView(TemplateView):
    template_name = 'qrcode.jade'

    def get_context_data(self, **kwargs):

        logger.debug("rock finance qrcode view，开始准备渲染数据")
        user_id = self.request.GET.get("user_id", -1)
        logger.debug("二维码用户user_id:%s" % user_id)
        reward = WanglibaoActivityReward.objects.filter(user_id=user_id, activity='rock_finance').first()
        if not reward:
            logger.debug(u"您没有领取到对应的入场二维码, user:%s" % self.request.user)
            return {"code": 1003, "message": u"您没有领到对应的入场二维码"}

        if reward.has_sent:  # 二维码可能被重复使用
            logger.debug(u"您的二维码已经被使用过, img:%s, user:%s" % (reward.qrcode, self.request.user))
            return {"code": -1, "img": reward.qrcode, "message": u"您的二维码已经被使用"}
        else:
            logger.debug(u"reward.qrcode img url:%s, user:%s" % (reward.qrcode, self.request.user))
            return {"code": 0, "img": reward.qrcode, "message": u"得到合法二维码"}


class RockFinanceForOldUserAPIView(APIView):
    permission_classes = ()

    def post(self, request):
        key = 'activities'
        activity_config = Misc.objects.filter(key=key).first()
        if activity_config:
            activity = json.loads(activity_config.value)
            if type(activity) == dict:
                try:
                    rock_finance = activity['rock_finance']
                    is_open = rock_finance["is_open"]
                    amount = rock_finance["amount"]
                    start_time = rock_finance["start_time"]
                    end_time = rock_finance["end_time"]
                except KeyError, reason:
                    logger.debug(u"misc中activities配置错误，请检查,reason:%s" % reason)
                    raise Exception(u"misc中activities配置错误，请检查，reason:%s" % reason)
            else:
                raise Exception(u"misc中activities的配置参数，应是字典类型")
        else:
            raise Exception(u"misc中没有配置activities杂项")

        logger.debug(u"user:%s, 运行开关:%s, 开放时间:%s, 结束时间:%s, 总票数:%s" % (request.user, is_open, start_time, end_time, amount))

        # 是否是登录用户
        if not request.user.is_authenticated():
            to_json_response = {
                'ret_code': 1000,
                'message': u'用户没有登录',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        p2p_record = P2PRecord.objects.filter(amount__gte=1000, user_id=request.user.id, catalog=u'申购', create_time__gte=start_time, create_time__lte=end_time).first()

        if not p2p_record:
            to_json_response = {
                'ret_code': 1001,
                'message': u'没有投资满5000',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        # 1: 如果活动没有打开
        if is_open == "false":
            logger.debug(u'开关没打开')
            to_json_response = {
                'ret_code': 1002,
                'message': u'活动开关没打开',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        # 2: 如果票数到800了，直接跳出
        counts = ActivityReward.objects.filter(activity='rock_finance').count()
        if counts >= amount:
            logger.debug(u'票已经发完了, %s' % (counts))
            to_json_response = {
                'ret_code': 1003,
                'message': u'票已经发完了',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        # 3 :如果时间已经过了, 直接跳出; 如果活动时间还没有开始，也直接跳出
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if now < start_time or now > end_time:
            logger.debug("start_time:%s, end_time:%s, now:%s" % (start_time, end_time, now))
            to_json_response = {
                'ret_code': 1004,
                'message': u'没有在预定的时间内购标',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        reward = Reward.objects.filter(type='金融摇滚夜', is_used=False).first()
        if not reward:
            logger.debug(u"奖品没有了")
            to_json_response = {
                'ret_code': 1005,
                'message': u'小子你来晚了，奖品发光了',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        activity_record = ActivityReward.objects.filter(user=request.user, activity='rock_finance').first()
        if activity_record:
            logger.debug(u'已经领过奖品了')
            to_json_response = {
                'ret_code': 1006,
                'message': u'已经领过奖品了',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        with transaction.atomic():
            reward = Reward.objects.select_for_update().filter(content=reward.content).first()
            try:
                activity_reward = ActivityReward.objects.create(
                    activity='rock_finance',
                    order_id=p2p_record.order_id,
                    user=request.user,
                    p2p_amount=p2p_record.amount,
                    reward=reward,
                    has_sent=False, #当被扫码后， has_sent变成true
                    left_times=1,
                    join_times=1,
                )
            except Exception, reason:
                logger.debug(u"生成获奖记录报异常, reason:%s" % reason)
                raise Exception(u"生成获奖记录异常")
            else:
                #不知道为什么create的时候，会报错
                m = Misc.objects.filter(key='weixin_qrcode_info').first()
                original_id = None
                if m and m.value:
                    info = json.loads(m.value)
                    original_id = info.get('fwh')
                    account = WeixinAccounts.getByOriginalId(original_id)
                encoding_str = urllib.quote("%s/api/check/qrcode/?owner_id=%s&activity=rock_finance&content=%s" % (settings.WEIXIN_CALLBACK_URL, request.user.id, reward.content))
                qrcode_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_base&state=%s" % (account.app_id, encoding_str, original_id)
                logger.debug("encoding_st:%s, qrcode_url:%s" % (encoding_str, qrcode_url))
                img = qrcode.make(qrcode_url)
                _img = img.tobytes()
                img_handle = cStringIO.StringIO()
                img.save(img_handle)
                img_handle.seek(0)
                _img = FileObject(img_handle, len(_img))
                activity_reward.qrcode.save("rock_finance.png", _img, save=True)
                activity_reward.save()
                logger.debug("before save: activity_reward.qrcode:%s" % activity_reward.qrcode)
                #将奖品通过站内信发出
                inside_message.send_one.apply_async(kwargs={
                    "user_id": request.user.id,
                    "title": u"网利宝摇滚之夜门票",
                    "content": u"网利宝摇滚夜欢迎您的到来，点击<a href='%s/rock/finance/qrcode/?user_id=%s'>获得入场二维码</a>查看，<br/> 感谢您对我们的支持与关注。<br/>网利宝" % (settings.WEIXIN_CALLBACK_URL, request.user.id),
                    "mtype": "activity"
                })
                reward.is_used = True
                reward.save()
                logger.debug("after save:activity_reward.qrcode:%s" % activity_reward.qrcode)

                logger.debug(u"user:%s, 站内信已经发出, 奖品内容:%s" % (request.user, reward.content))
                to_json_response = {
                    'ret_code': 0,
                    'message': u'用户的站内信已经发出',
                }
                return HttpResponse(json.dumps(to_json_response), content_type='application/json')


class RockFinanceAPIView(APIView):
    permission_classes = ()

    def get_qrcode(self, request):
        if not request.user.is_authenticated():
            return Response({"code": 1002, "message": u"请您先登录"})

        reward = WanglibaoActivityReward.objects.filter(user=request.user, activity='rock_finance').first()
        if not reward:
            return Response({"code": 1003, "message": u"您没有领到对应的入场二维码"})

        if reward.is_used:  # 二维码可能被重复使用
            return Response({"code": -1, "img": reward.qrcode, "message": u"您的二维码已经被使用"})
        else:
            return Response({"code": 0, "img": reward.qrcode, "message": u"得到合法二维码"})

    def get_vote_static(self):
        """
            得到整体的全部数据
        """
        records = WanglibaoVoteCounter.objects.filter(activity="rock_finance")
        records = {"".join(['《', str(record.item), '》']): record.count for record in records}  #前端要求带书名号
        return Response({"records": records, "message": u'整体的汇总数据', "code":0})

    def get(self, request):
        _type = request.GET.get("type", None)
        if not _type or _type not in ('qrcode', 'static'):
            return Response({"code": 1001, "message": u"请传入合理参数"})

        if _type == 'qrcode':
            return self.get_qrcode(request)
        if _type == 'static':
            return self.get_vote_static()

    def post(self, request):
        """
        items 的数据格式为： "乐队-歌曲,乐队-歌曲,..."
        """
        items = request.DATA.get("items", None)

        try:
            assert None is not items
        except AssertionError:
            return Response({"code": 1000, "message": u'传入的参数不合法'})
        else:
            items = items.split(",")

        musics = list()
        teams = list()
        for item in items:
            item = item.split("-")
            teams.append(item[0])
            musics.append(item[1])

        vote_counter = WanglibaoVoteCounter.objects.filter(activity="rock_finance", item__in=musics)

        for music in musics:
            vote = vote_counter.filter(item=music).first()
            if not vote:
                vote = WanglibaoVoteCounter.objects.create(
                    activity="rock_finance",
                    catalog=teams[musics.index(music)],
                    item=music,
                    count=0
                )

            vote.count += 1
            vote.save()
        return Response({"code": 0, "message": u'投票成功'})


class RockFinanceCheckAPIView(BaseWeixinTemplate):
    template_name = 'rockfinance_checkresult.jade'

    def get_context_data(self, **kwargs):
        key = 'activities'
        activity_config = Misc.objects.filter(key=key).first()
        if activity_config:
            activity = json.loads(activity_config.value)
            if type(activity) == dict:
                try:
                    rock_finance = activity['rock_finance']
                    is_open = rock_finance["is_open"]
                    start_scan = rock_finance["start_scan"]
                    end_scan = rock_finance["end_scan"]
                    openids = rock_finance["openids"]
                except KeyError, reason:
                    logger.debug(u"misc中activities配置错误，请检查,reason:%s" % reason)
                    raise Exception(u'misc中activities配置错误，请检查。reason:%s'% reason)
        else:
            raise Exception(u"misc中没有配置activities杂项")

        logger.debug("user:%s, is_open:%s, start_scan:%s, end_scan:%s openids:%s, scaner_openid:%s" % (self.request.user, is_open, start_scan, end_scan, openids, self.openid))

        #判断是否在扫描列表里
        if self.openid and self.openid not in openids:
            return {"code": 1000, "message": u"您没有扫描权限"}

        #判断活动是否开启
        if is_open == "false":
            return {"code": 1001, "message": u"活动还没有开启"}

        #判断是否在扫描的时间段内
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if now < start_scan or now > end_scan:
            return {"code": 1002, "message": u'扫描时间段不合理'}


        owner_id = self.request.GET.get("owner_id", None)
        activity = self.request.GET.get("activity", None)
        content = self.request.GET.get("content", None)

        try:
            assert None not in (owner_id, activity, content)
        except AssertionError:
            return {"code": 1005, "message": u"二维码链接的参数不对"}

        with transaction.atomic():
            reward_record = WanglibaoActivityReward.objects.select_for_update().filter(has_sent=False, user_id=owner_id, activity=activity, reward__content=content).first()
            if not reward_record:
                return {"code": 1003, "message": u'您的二维码不合法, 可能已经被使用了'}

            if reward_record.has_sent:
                reward_record.save()
                return {"code": 1004, "message": u'每一个二维码只能被使用一次'}

            reward_record.has_sent = True
            reward_record.left_times = 0
            reward_record.save()
            return {"code": 0, "message": u'欢迎您参加网利宝金融摇滚夜'}


class ThunderBindingApi(APIView):
    """
    迅雷用户绑定接口
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        # Add by hb on 2015-12-30
        # Modify by cwb@20151230
        user = self.request.user
        user_channel = get_user_channel_record(user)
        channel_codes = ('xunlei9', 'mxunlei')
        if not user_channel or user_channel.code not in channel_codes:
            response_data = {
                'ret_code': '10004',
                'message': u'非迅雷渠道用户',
            }
            return HttpResponse(json.dumps(response_data), content_type='application/json')

        channel_code = request.POST.get('promo_token', '').strip()
        channel_user = request.POST.get('xluserid', '').strip()
        channel_time = request.POST.get('time', '').strip()
        channel_sign = request.POST.get('sign', '').strip()
        nick_name = request.POST.get('nickname', '').strip()
        if channel_code and (channel_code in channel_codes and channel_user
                             and channel_time and channel_sign and nick_name):
            user = self.request.user
            binding = Binding.objects.filter(user_id=user.id).first()
            if not binding:
                CoopRegister(request).process_after_binding(user)
                binding = Binding.objects.filter(user_id=user.id).first()
                if binding:
                    response_data = {
                        'ret_code': '10000',
                        'message': u'绑定成功',
                        'nickname': nick_name,
                    }
                else:
                    response_data = {
                        'ret_code': '10003',
                        'message': u'绑定失败',
                    }
            else:
                response_data = {
                    'ret_code': '10002',
                    'message': u'该用户已绑定过',
                    'nickname': nick_name,
                }
        else:
            response_data = {
                'ret_code': '10001',
                'message': u'非法请求',
            }

        logger.info("%s binding user_id[%s], promo_token[%s], xluserid[%s], time[%s], sign[%s], result[%s]"
                    % (user_channel.code, user.id, channel_code, channel_user, channel_time, channel_sign, response_data))

        return HttpResponse(json.dumps(response_data), content_type='application/json')


import math
class CustomerAccount2015ApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        error_code = 0
        error_message = u''
        account_dict = dict()

        user = self.request.user
        if user and user.id:
            user_id = user.id
            account = Account2015.objects.filter(user_id=user_id).first()
            if account:
                account_dict = account.toJSON_filter()
                if account.tz_times>0:
                    account_dict['tz_avg_time'] = round(365.0/float(account.tz_times), 2)
                if account.tz_amount>0:
                    a = round(account.tz_sterm_amount / account.tz_amount * 100, 2)
                    b = round(account.tz_mterm_amount / account.tz_amount * 100, 2)
                    c = round(account.tz_lterm_amount / account.tz_amount * 100, 2)

                    aa = math.ceil(a)
                    bb = math.ceil(b)
                    cc = math.ceil(c)

                    abc = aa + bb +cc
                    if abc>100 and abc<=101:
                        max_value = max(aa, bb, cc)
                        if aa==max_value:
                            aa = aa - 1
                        elif bb==max_value:
                            bb = bb - 1
                        elif cc==max_value:
                            cc = cc - 1
                    elif abc>101 and abc<=102:
                        min_value = min(aa, bb, cc)
                        if aa==min_value:
                            bb = bb - 1
                            cc = cc - 1
                        elif bb==min_value:
                            aa = aa - 1
                            cc = cc - 1
                        elif cc==min_value:
                            aa = aa - 1
                            bb = bb - 1
                    elif abc>102:
                            aa = aa - 1
                            bb = bb - 1
                            cc = cc - 1

                    account_dict['tz_sterm_percent'] = a
                    account_dict['tz_mterm_percent'] = b
                    account_dict['tz_lterm_percent'] = c

                    account_dict['tz_sterm_point'] = aa
                    account_dict['tz_mterm_point'] = bb
                    account_dict['tz_lterm_point'] = cc

                    try:
                        account.total_visit_count += 1
                        if not account.first_visit_time:
                            account.first_visit_time = timezone.now()
                            account.first_visit_ipaddr = get_client_ip(request)
                        else:
                            account.last_visit_time = timezone.now()
                            account.last_visit_ipaddr = get_client_ip(request)
                        account.save()
                    except Exception, ex:
                        logger.exception("=20150127= Failed to save account2015 visited record: [%s], [%s]", user_id, ex)

                error_code=0
                error_message=u'Success'
            else:
                error_code=0
                error_message=u'未统计的2016年新注册用户'
                zc_ranking = User.objects.filter(id__lte=user_id).count()
                account_dict['zc_ranking'] = zc_ranking
                account_dict['tz_amount'] = 0
                account_dict['income_reward'] = 0
                account_dict['invite_income'] = 0

            profile = user.wanglibaouserprofile
            user_name = u'网利宝用户'
            if profile:
                if profile.id_is_valid:
                    user_name= profile.name
                else:
                    user_name = safe_phone_str(profile.phone)
                account_dict['user_name'] = user_name
        else:
            error_code=404
            error_message=u'User not found'

        resp = {"error_code":error_code, "error_message":error_message, "account":account_dict}
        return HttpResponse(json.dumps(resp, sort_keys=True), content_type='application/json')
