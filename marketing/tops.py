# encoding: utf-8
from datetime import datetime, timedelta
from wanglibao_p2p.models import P2PRecord
from marketing.models import Activity
from django.db.models import Sum, Max
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

        #
        # if activity.count() != 0:
        #     return activity[0].start_time


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


    def day_tops(self, day):

        if self.activity_start is None:
            return []
        if not day:
            day = datetime.now()

        amsterdam = self.timezone_util

        begin = amsterdam.localize(datetime.combine(day.date(), day.min.time()))
        end = amsterdam.localize(datetime.combine(day.date(), day.max.time()))

        records = P2PRecord.objects.filter(create_time__range=(begin.astimezone(pytz.utc), end.astimezone(pytz.utc)),
                                           catalog='申购').values('user') \
            .annotate(amount_sum=Sum('amount')) \
            .order_by('-amount_sum')[:self.num_limit]

        return self.extract_user_list(records)

    def certain_day(self, days):
        if days < 1 or days > 28:
            return []

        return self.day_tops(self.activity_start_local+timedelta(days-1))

    def lastday_tops(self):
        amsterdam = self.timezone_util
        if ((amsterdam.localize(datetime.now())-self.activity_start_local).days == 0):
            return []
        return self.day_tops(datetime.now()-timedelta(days=1))

    def allday_tops(self):

        if self.activity_start is None:
            return []

        amsterdam = self.timezone_util

        begin = amsterdam.localize(
            datetime.combine(self.activity_start_local.date(), self.activity_start_local.min.time()))
        end_local = self.activity_start_local + timedelta(days=27)
        end = amsterdam.localize(datetime.combine(end_local.date(),
                                                  end_local.max.time()))

        p2p_records = P2PRecord.objects.filter(
            create_time__range=(begin.astimezone(pytz.utc), end.astimezone(pytz.utc)), catalog='申购') \
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

    def certain_week(self, week):

        if week < 1 or week > 4:
            return []

        return self.week_tops(self.activity_start_local+timedelta(weeks=week-1))


    def week_tops(self, start):
        """
        :param start: 某天, 默认为当天
        :return: 某周的投资排行榜
        """
        if self.activity_start is None:
            return []
        amsterdam = self.timezone_util
        if not start:
            start = datetime.now()

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
        if self.activity_start is None:
            return []
        start = timezone.localtime(self.activity_start)
        weeks = []
        for i in range(0, 4):
            weeks.append(self.week_tops(start + timedelta(days=i * 7 + 1)))

        return weeks

    def all_tops(self):
        if self.activity_start is None:
            return []

        amsterdam = self.timezone_util

        begin = amsterdam.localize(
            datetime.combine(self.activity_start_local.date(), self.activity_start_local.min.time()))
        end_local = self.activity_start_local + timedelta(days=27)
        end = amsterdam.localize(datetime.combine(end_local.date(),
                                                  end_local.max.time()))

        records = P2PRecord.objects.filter(create_time__range=(begin.astimezone(pytz.utc), end.astimezone(pytz.utc))
                                           , catalog='申购') \
            .values('user') \
            .annotate(amount_sum=Sum('amount')) \
            .order_by('-amount_sum')[:self.num_limit]

        return self.extract_user_list(records)

    def certain_prize(self):
        week = (datetime.now().date()-self.activity_start_local.date()).days / 7
        if week > 3:
            week = 3

        return self.top_prize(week)

    def is_valid(self):
        return datetime.now() < datetime(year=2015, month=2, day=2, minute=0, second=0, microsecond=0)

    def top_prize(self, index):
        weeks = [
            {
                "day": [
                    {"name": "松下-F-PDF35C-G-空气净化器", "price": 699, "src": "/static/images/newyear/prize/day_1_1.jpg"},
                    {"name": "法国拉玛特雄狮堡干红葡萄酒", "price": 498, "src": "/static/images/newyear/prize/day_1_2.jpg"},
                    {"name": "小米移动电源", "price": 79, "src": "/static/images/newyear/prize/day_1_3.jpg"},
                ],
                "week": [
                    {"name": "乐视电视-40寸", "price": 2400, "src": "/static/images/newyear/prize/week_1_1.jpg"},
                    {"name": "Kindle-Paperwhite", "price": 899, "src": "/static/images/newyear/prize/week_1_2.jpg"},
                    {"name": "500元京东卡", "price": 500, "src": "/static/images/newyear/prize/week_1_3.jpg"},
                ]
            },
            {
                "day": [
                    {"name": "53°贵州茅台", "price": 868, "src": "/static/images/newyear/prize/day_2_1.jpg"},
                    {"name": "300元京东卡", "price": 300, "src": "/static/images/newyear/prize/day_2_2.jpg"},
                    {"name": "法国梅多克中级庄 干红葡萄酒", "price": 89, "src": "/static/images/newyear/prize/day_2_3.jpg"},
                ],
                "week": [
                    {"name": "ipad-air-1", "price": 2400, "src": "/static/images/newyear/prize/week_2_1.jpg"},
                    {"name": "Kindle-Paperwhite", "price": 899, "src": "/static/images/newyear/prize/week_2_2.jpg"},
                    {"name": "500元京东卡", "price": 500, "src": "/static/images/newyear/prize/week_2_3.jpg"},
                ]
            },
            {
                "day": [
                    {"name": "松下-F-PDF35C-G-空气净化器", "price": 699, "src": "/static/images/newyear/prize/day_3_1.jpg"},
                    {"name": "法国拉玛特雄狮堡干红葡萄酒", "price": 498, "src": "/static/images/newyear/prize/day_3_2.jpg"},
                    {"name": "小米移动电源", "price": 79, "src": "/static/images/newyear/prize/day_3_3.jpg"},
                ],
                "week": [
                    {"name": "乐视电视-40寸", "price": 2400, "src": "/static/images/newyear/prize/week_3_1.jpg"},
                    {"name": "Kindle-Paperwhite", "price": 899, "src": "/static/images/newyear/prize/week_3_2.jpg"},
                    {"name": "500元京东卡", "price": 500, "src": "/static/images/newyear/prize/week_3_3.jpg"},
                ]
            },
            {
                "day": [
                    {"name": "53°贵州茅台", "price": 868, "src": "/static/images/newyear/prize/day_4_1.jpg"},
                    {"name": "300元京东卡", "price": 300, "src": "/static/images/newyear/prize/day_4_2.jpg"},
                    {"name": "法国梅多克中级庄 干红葡萄酒", "price": 89, "src": "/static/images/newyear/prize/day_4_3.jpg"},
                ],
                "week": [
                    {"name": "乐视电视-40寸", "price": 2400, "src": "/static/images/newyear/prize/week_4_1.jpg"},
                    {"name": "Kindle-Paperwhite", "price": 899, "src": "/static/images/newyear/prize/week_4_2.jpg"},
                    {"name": "500元京东卡", "price": 500, "src": "/static/images/newyear/prize/week_4_3.jpg"},
                ]
            },
        ]


        return weeks[index]

    def day_tops_first_come_first_served(self, day, amount_min=None, amount_max=None):
        """ 查询日榜单，先到先得
        """
        amsterdam = self.timezone_util

        begin = amsterdam.localize(datetime.combine(day.date(), day.min.time()))
        end = amsterdam.localize(datetime.combine(day.date(), day.max.time()))

        records = P2PRecord.objects.filter(
            create_time__range=(begin.astimezone(pytz.utc), end.astimezone(pytz.utc)),
            catalog='申购'
        ).values(
            'user'
        ).annotate(
            amount_sum=Sum('amount'),
            create_time=Max('create_time')
        )

        if amount_min:
            records = records.filter(amount_sum__gte=amount_min)
        if amount_max:
            records = records.filter(amount_sum__lte=amount_max)

        records = records.order_by('-amount_sum', 'create_time')

        if self.num_limit != 0:
            records = records[:self.num_limit]

        return records

    def day_tops_activate(self, day=datetime.now(), amount_min=60000):
        """ 根据查询出的榜单，查询对应的用户信息
        """
        return self.extract_user_list(
            self.day_tops_first_come_first_served(day=day, amount_min=amount_min)
        )