# encoding: utf-8
from datetime import datetime, timedelta
from wanglibao_p2p.models import P2PRecord
from marketing.models import Activity
from django.db.models import Sum
from django.utils import timezone
from itertools import groupby
from rest_framework.response import Response

import pytz

class Top(object):

    @property
    def timezone_util(self):
        return pytz.timezone('Asia/Shanghai')

    def day_tops(self, day=datetime.now()):

        amsterdam = self.timezone_util

        begin = amsterdam.localize(datetime.combine(day.date(), day.min.time()))
        end = amsterdam.localize(datetime.combine(day.date(), day.max.time()))

        records = P2PRecord.objects.filter(create_time__range=(begin.astimezone(pytz.utc), end.astimezone(pytz.utc))) \
            .values('user') \
            .annotate(amount_sum=Sum('amount')) \
            .order_by('-amount_sum')



        return records


    def allday_tops(self, start=datetime.now()):

        amsterdam = self.timezone_util
        begin = amsterdam.localize(datetime.combine(start.date(), start.min.time()))

        p2p_records = P2PRecord.objects.filter(create_time__gte=begin.astimezone(pytz.utc))

        user_list = []


        #把datetime 转为 date, group by date
        def extract_date(p2p_record):
            return timezone.localtime(p2p_record.create_time).date()

        def extract_user(p2p_record):
            return p2p_record.user

        # group by every day
        for each_day, group in groupby(p2p_records, key=extract_date):
            # group by user every day
            for user, group_inner in groupby(list(group), key=extract_user):
                amount_sum = 0
                for record in group_inner:
                    amount_sum += record.amount

                if hasattr(user, 'wanglibaouserprofile'):
                    user_list.append({'each_day': each_day, 'user': user.wanglibaouserprofile.phone, 'amount_sum': amount_sum})

        return user_list


    def week_tops(self, start=datetime.now()):
        pass


    def allweek_tops(self):
        pass



    def all_tops(self, start=datetime.now()):

        activity = Activity.objects.filter(description__endswith="_tops_")
        if activity.count() == 0:
            return Response({"ret_code": 0, "records": "nna"})

        start = activity[0].start_time

        local_time = timezone.localtime(start)
        amsterdam = self.timezone_util

        begin = amsterdam.localize(datetime.combine(local_time.date(), local_time.min.time()))
        end = amsterdam.localize(datetime.combine((local_time+timedelta(days=28)).date(), local_time.min.time()))

        records = P2PRecord.objects.filter(create_time__range=(begin.astimezone(pytz.utc), end.astimezone(pytz.utc))) \
            .values('user') \
            .annotate(amount_sum=Sum('amount')) \
            .order_by('-amount_sum')

        return records

