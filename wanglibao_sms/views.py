# -*- coding: utf-8 -*-
import logging
import urllib2
import datetime
from django.db.models import Sum
from django.http.response import HttpResponse
from django.utils import timezone
import pytz
import time
from rest_framework import renderers
from rest_framework.views import APIView

from wanglibao import settings
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_sms.models import ArrivedRate, MessageTemplate
from wanglibao_sms import messages as sms_messages
from wanglibao_rest.common import DecryptParmsAPIView


def count_messages_arrived_rate():
    """
    author: Zhoudong
    定时统计到达率
    :return:
    """
    now = timezone.now()
    local_now = timezone.localtime(now)

    minute = local_now.minute
    if minute % 10 == 0:
        pass
    else:
        minute = minute / 10 * 10

    end = datetime.datetime(year=local_now.year,
                            month=local_now.month,
                            day=local_now.day,
                            hour=local_now.hour,
                            minute=minute,
                            second=0).replace(tzinfo=pytz.timezone(settings.TIME_ZONE))

    delta = settings.MESSAGE_TIME_DELTA
    start = end - delta

    total = 0
    achieved = 0

    file_name = time.strftime('%Y-%m-%d' + '.log', time.localtime())
    try:
        f = open('/var/log/wanglibao/report_messages/' + file_name, 'r')
        lines = f.readlines()
        f.close()

        for line in lines:
            s = line.split(',')[-1]
            time_str = s.split()[0] + ' ' + s.split()[1]
            check_time = \
                timezone.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone(settings.TIME_ZONE))

            if start < check_time < end:
                total += 1
                if line.split(',')[4] == 0 or line.split(',')[4] == 'DELIVRD':
                    achieved += 1

        if total > 0:
            ArrivedRate.objects.get_or_create(channel=u'慢道', achieved=achieved, total_amount=total,
                                              rate=float(achieved) / total * 100, start=start, end=end)
    except Exception, e:
        print e


def check_arrived_rate_tasks(period=2):
    """
    检查是不是有任务跳过了没有执行.
    TODO: 每天的改进为只打开一次文件
    :param period: 检查的天数
    :return:
    """
    now = timezone.now()
    local_now = timezone.localtime(now)

    minute = local_now.minute
    if minute % 10 == 0:
        pass
    else:
        minute = minute / 10 * 10

    end = datetime.datetime(year=local_now.year,
                            month=local_now.month,
                            day=local_now.day,
                            hour=local_now.hour,
                            minute=minute,
                            second=0).replace(tzinfo=pytz.timezone(settings.TIME_ZONE))

    start_0 = end - datetime.timedelta(days=period)
    delta = settings.MESSAGE_TIME_DELTA
    start_1 = end - delta

    start = start_0
    while start < start_1:
        try:
            ArrivedRate.objects.get(start=start)
        except Exception, e:
            print 'get_error: ', e
            total = 0
            achieved = 0
            end = start + delta

            file_name = str(start.year) + '-' + str(start.month) + '-' + str(start.day) + '.log'
            try:
                f = open('/var/log/wanglibao/report_messages/' + file_name, 'r')
                lines = f.readlines()
                f.close()

                for line in lines:
                    s = line.split(',')[-1]
                    time_str = s.split()[0] + ' ' + s.split()[1]
                    check_time = \
                        timezone.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone(settings.TIME_ZONE))

                    if start < check_time < end:
                        total += 1
                        if line.split(',')[4] == 0 or line.split(',')[4] == 'DELIVRD':
                            achieved += 1

                if total > 0:
                    ArrivedRate.objects.get_or_create(channel=u'慢道', achieved=achieved, total_amount=total,
                                                      rate=float(achieved) / total * 100, start=start, end=end)
            except Exception, e:
                print e

        start += datetime.timedelta(minutes=10)


class ArriveRate(APIView):
    """
    author: Zhoudong
    根据时间段, 获取到达率
    method: GET.
    改成定期执行加入数据库, 统计一定时间段的到达率
    """
    permission_classes = (IsAdminUserOrReadOnly,)

    def get(self, request):

        start = self.request.GET.get('start', None)
        end = self.request.GET.get('end', timezone.now())
        msgs = ArrivedRate.objects.filter(created_at__lte=end)
        if start:
            msgs = msgs.filter(created_at__gte=start)
        result = dict()
        try:
            achieved = msgs.aggregate(Sum('achieved'))['achieved__sum'] or 0
            total = msgs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            rate = "%.2f" % (float(achieved) / total * 100)
            result['achieved'] = achieved
            result['total'] = total
            result['rate'] = rate
            result['status'] = 0
            result['msg'] = u'成功'

        except Exception, e:
            print e
            result = {
                'status': -1,
                'msg': u'除数为0,没有数据',
            }

        return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))


class SendSMSNoticeAPIView(DecryptParmsAPIView):
    """
    发送短信接口, template_id: 1=>success; 2=>fail
    """
    permission_classes = ()

    def post(self, request):
        phone = self.params.get('phone')
        sms_func_name = self.params.get('sms_func_name')
        if not sms_func_name:
            return

        sms_template = MessageTemplate.objects.filter(message_for=sms_func_name).first()
        if sms_template:
            sms_content = sms_template.content
        else:
            if sms_func_name == 'changed_mobile_success':
                sms_content = sms_messages.changed_mobile_success()
            else:
                sms_content = sms_messages.changed_mobile_fail()

        # 发送短信
        from .tasks import send_messages
        send_messages.apply_async(kwargs={
            "phones": [phone, ],
            "messages": [sms_content, ],
        })
        return HttpResponse(renderers.JSONRenderer().render({"message":'ok'}, 'application/json'))
