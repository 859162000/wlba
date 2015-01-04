# encoding: utf-8
from datetime import datetime, timedelta
from wanglibao_p2p.models import P2PRecord
from marketing.models import Activity
from django.db.models import Sum
from django.contrib.auth.models import User
from django.utils import timezone
from itertools import groupby

import pytz

# 把datetime 转为 date, group by date
def extract_date(p2p_record):
    return timezone.localtime(p2p_record.create_time).date()


def extract_user(p2p_record):
    return p2p_record.user


class Top(object):
    def __init__(self, limit=5):
        self.num_limit = limit

    @property
    def timezone_util(self):
        return pytz.timezone('Asia/Shanghai')

    @property
    def activity_start(self):
        activity = Activity.objects.filter(description__endswith="_tops_")
        if activity.count() == 0:
            return None

        return activity[0].start_time

    @property
    def activity_start_local(self):
        return timezone.localtime(self.activity_start)

    def extract_user_list(self, p2p_records):
        user_list = list()

        for record in p2p_records:
            user = User.objects.filter(pk=record['user']).select_related('wanglibaouserprofile')[0]

            user_list.append({
                'id': record['user'],
                'amount_sum': record['amount_sum'],
                'phone': user.wanglibaouserprofile.phone
            })

        return user_list


    def day_tops(self, day=datetime.now()):

        if self.activity_start_local is None:
            return []

        amsterdam = self.timezone_util

        begin = amsterdam.localize(datetime.combine(day.date(), day.min.time()))
        end = amsterdam.localize(datetime.combine(day.date(), day.max.time()))

        records = P2PRecord.objects.filter(create_time__range=(begin.astimezone(pytz.utc), end.astimezone(pytz.utc)),
                                           catalog='申购').values('user') \
            .annotate(amount_sum=Sum('amount')) \
            .order_by('-amount_sum')[:self.num_limit]

        return self.extract_user_list(records)

    def lastday_tops(self):
        return self.day_tops(datetime.now()-timedelta(days=1))

    def allday_tops(self, start=datetime.now()):

        if self.activity_start_local is None:
            return []

        amsterdam = self.timezone_util
        begin = amsterdam.localize(datetime.combine(start.date(), start.min.time()))

        p2p_records = P2PRecord.objects.filter(create_time__gte=begin.astimezone(pytz.utc), catalog='申购') \
            .select_related('user__wanglibaouserprofile')

        user_list = []

        # group by every day
        for each_day, group in groupby(p2p_records, key=extract_date):
            # group by user every day
            for user, group_inner in groupby(list(group), key=extract_user):
                amount_sum = 0
                for record in group_inner:
                    amount_sum += record.amount

                if hasattr(user, 'wanglibaouserprofile'):
                    user_list.append(
                        {'each_day': each_day, 'user': user.wanglibaouserprofile.phone, 'amount_sum': amount_sum})

        return user_list


    def week_tops(self, start=datetime.now()):
        """
        :param start: 某天, 默认为当天
        :return: 某周的投资排行榜
        """
        if self.activity_start_local is None:
            return []
        amsterdam = self.timezone_util

        # 用utc时间算出当前的日期是属于活动的第几周
        if start.tzinfo == None:
            week = (amsterdam.localize(start).astimezone(pytz.utc) - self.activity_start).days / 7
        else:
            week = (start.astimezone(pytz.utc) - self.activity_start).days / 7

        begin_local = self.activity_start + timedelta(days=week * 7 + 1)
        end_local = self.activity_start + timedelta(days=(week + 1) * 7 + 1)

        begin = datetime.combine(begin_local.date(), begin_local.min.time())
        end = datetime.combine(end_local.date(), end_local.min.time())

        p2p_records = P2PRecord.objects.filter(create_time__gte=begin, create_time__lt=end, catalog='申购')\
            .values('user')\
            .annotate(amount_sum=Sum('amount'))\
            .order_by('-amount_sum')[:self.num_limit]

        return self.extract_user_list(p2p_records)

    def allweek_tops(self):
        if self.activity_start_local is None:
            return []
        start = timezone.localtime(self.activity_start)
        weeks = []
        for i in range(0, 4):
            weeks.append(self.week_tops(start + timedelta(days=i * 7 + 1)))

        return weeks

    def all_tops(self):
        if self.activity_start_local is None:
            return []

        amsterdam = self.timezone_util

        begin = amsterdam.localize(
            datetime.combine(self.activity_start_local.date(), self.activity_start_local.min.time()))
        end = amsterdam.localize(datetime.combine((self.activity_start_local + timedelta(days=28)).date(),
                                                  self.activity_start_local.min.time()))

        records = P2PRecord.objects.filter(create_time__range=(begin.astimezone(pytz.utc), end.astimezone(pytz.utc))
                                           , catalog='申购') \
            .values('user') \
            .annotate(amount_sum=Sum('amount')) \
            .order_by('-amount_sum')[:self.num_limit]

        return self.extract_user_list(records)

