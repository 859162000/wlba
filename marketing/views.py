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
from marketing.models import PromotionToken, IntroducedBy
from marketing.tops import Top


# Create your views here.

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
        start = self.request.GET.get('start', '') or AggregateView.DEFAULT_START
        end = self.request.GET.get('end', '') or AggregateView.DEFAULT_END
        amount_min = self.request.GET.get('amount_min', '') or AggregateView.DEFAULT_AMOUNT_MIN
        amount_max = self.request.GET.get('amount_max', '')

        start = datetime.strptime(start, '%Y-%m-%d')
        end = datetime.strptime(end, '%Y-%m-%d')

        # 时间国际化
        amsterdam = self.timezone_util
        begin = amsterdam.localize(datetime.combine(start, start.min.time()))
        end = amsterdam.localize(datetime.combine(end, end.max.time()))

        trades = P2PRecord.objects.filter(
            create_time__range=(begin.astimezone(pytz.utc), end.astimezone(pytz.utc))
        ).annotate(amount_sum=Sum('amount'))

        if amount_min:
            trades = trades.filter(amount_sum__gte=amount_min)
        if amount_max:
            trades = trades.filter(amount_sum__lt=amount_max)

        # 总计所有符合条件的金额
        amount_all = trades.aggregate(Sum('amount_sum'))
        # 关联用户认证信息
        trades = trades.select_related('user__wanglibaouserprofile').order_by('-amount_sum')

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


class IntroducedReward(TemplateView):
    template_name = 'introduced_by.jade'


class IntroduceAward(TemplateView):
    """this class can used to query the introduced_by users and their first trade, according
    the percent calculated the first trade earnings, add it into db and after checked, reward it
    to their father
    """
    template_name = 'reward.jade'

    @method_decorator(permission_required('marketing.change_sitedata', login_url='/' + settings.ADMIN_ADDRESS))
    def dispatch(self, request, *args, **kwargs):
        return super(IntroduceAward, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        start = self.request.GET.get('start', None)
        end = self.request.GET.get('end', None)
        percent = self.request.GET.get('percent', None)
        amount_min = self.request.GET.get('amount_min', None)

        if start and end and percent is not None and amount_min is not None:
            try:
                start = datetime.strptime(start, '%Y-%m-%d')
                end = datetime.strptime(end, '%Y-%m-%d')
                # local time convert to utc time
                start_utc = local_to_utc(start, source_time='min')
                end_utc = local_to_utc(end, source_time='max')
            except Exception:
                return {
                    "message": u"输入日期格式有误！"
                }
        else:
            return {
                "message": u"统计条件数据不合法！"
            }

        # query all the user who bought the first trade between the date
        new_user = IntroducedBy.objects.filter(
            bought_at__range=(start_utc, end_utc)
        ).exclude(
            introduced_by__username__startswith="channel"
        ).exclude(
            introduced_by__wanglibaouserprofile__utype__gt=0
        )

        for first_user in new_user:
            # everyone
            first_record = P2PRecord.objects.filter(
                user=first_user.user,
                create_time__range=(start_utc, end_utc),
                catalog='申购'
            ).earliest("create_time")

            # first trade min amount limit
            if first_record.amount >= Decimal(amount_min):
                amount_earning = Decimal(Decimal(first_record.amount) * Decimal(percent) * (Decimal(first_record.product.period) / Decimal(12))).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
                print u"%s邀请了%s，首笔交易%s元，%s获得%s元奖金" % (first_user.introduced_by.wanglibaouserprofile.name, first_user.user.wanglibaouserprofile.name, first_record.amount, first_user.introduced_by.wanglibaouserprofile.name, amount_earning)

            pass
        pass
    pass


def local_to_utc(source_date, source_time='min'):
    """To convert Local Date to UTC Date

    Args:
        source_date: the origin date
        source_time: the origin time
            if the source_time value is min, it means 00:00:00
            if the source_time value is max, it means 23:59:59
            others just convert the value time

    return the utc time
    """

    # get the time zone
    time_zone = pytz.timezone('Asia/Shanghai')

    if source_time == 'min':
        source_time = source_date.min.time()
    elif source_time == 'max':
        source_time = source_date.max.time()

    # convert to utc time
    new = time_zone.localize(datetime.combine(source_date, source_time))
    return new.astimezone(pytz.utc)