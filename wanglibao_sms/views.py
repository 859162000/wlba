# -*- coding: utf-8 -*-
import os
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http.response import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.generic import TemplateView
import pytz
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework.views import APIView

# from models import AchievedMessage, ReportMessage
import time
from wanglibao import settings
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_sms.models import ArrivedRate, MessageInRedis


class AchievedMessages(APIView):
    """
    author: Zhoudong
    获取客户发送的短信参数, 保存到DB.
    # https 方式用get方法给我们传参
    method: GET.
    """
    permission_classes = ()

    def get(self, request):

        # 开发测试用数据
        # data = self.request.GET.get('args', '123456,62891,138****065,ceshi01,2015-09-24 15:51:05;\
        #                                       4464023,62891,139****404,test02,2015-09-23 15:51:17')
        data = self.request.GET.get('args', None)
        if data:
            file_name = time.strftime('%Y-%m-%d' + '.log', time.localtime())
            try:
                os.mkdir('/var/log/wanglibao/user_message/')
            except Exception, e:
                print e
            try:
                os.system('touch %s%s' % ('/var/log/wanglibao/user_message/', file_name))
            except Exception, e:
                print e

            try:
                f = open('/var/log/wanglibao/user_message/' + file_name, 'a+')
                args_list = data.split(';')
                for args in args_list:
                    # 保留所有参数
                    params = args.replace(',', '\t') + '\n'
                    # 保留需要的参数
                    # params = '\t'.join(args.split(',')[1:5]) + '\n'
                    f.write(params)
                f.close()
            except Exception, e:
                Response(str(e))

        return Response(data)


class ReportMessages(APIView):
    """
    author: Zhoudong
    获取短信回执参数, 保存到DB.
    method: GET.
    """
    permission_classes = ()

    def get(self, request):

        # 开发测试用数据
        # data = self.request.GET.get('args', '123456,62891,159*404,564687,DELIVRD,2015-09-24 13:01:36; \
        #                                       123456,62891,189*404,420937,DELIVRD,2015-09-23 13:01:42')
        data = self.request.GET.get('args', None)
        if data:
            file_name = time.strftime('%Y-%m-%d' + '.log', time.localtime())
            try:
                os.mkdir('/var/log/wanglibao/report_message/')
            except Exception, e:
                print e
            try:
                os.system('touch %s%s' % ('/var/log/wanglibao/report_message/', file_name))
            except Exception, e:
                print e

            try:
                f = open('/var/log/wanglibao/report_message/' + file_name, 'a+')
                args_list = data.split(';')
                for args in args_list:
                    # 保留所有参数
                    params = args.replace(',', '\t') + '\n'
                    # 保留需要的参数
                    # params = '\t'.join(args.split(',')[1:5]) + '\n'
                    f.write(params)
                f.close()
            except Exception, e:
                Response(str(e))

        return Response(data)


def count_message_arrived_rate():
    """
    author: Zhoudong
    定时统计到达率
    :return:
    """
    now = timezone.now()
    local_now = timezone.localtime(now).replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
    delta = settings.MESSAGE_TIME_DELTA
    start = local_now - delta

    total = 0
    achieved = 0

    file_name = time.strftime('%Y-%m-%d' + '.log', time.localtime())
    f = open('/var/log/wanglibao/report_message/' + file_name, 'r')
    lines = f.readlines()

    for line in lines:
        time_str = line.split('\t')[-1].split('\n')[0]
        check_time = \
            timezone.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone(settings.TIME_ZONE))

        if start < check_time < local_now:
            total += 1
            if line.split('\t')[4] == 0 or line.split('\t')[4] == 'DELIVRD':
                achieved += 1

    if total > 0:
        ArrivedRate.objects.create(channel=u'慢道', achieved=achieved, total_amount=total,
                                   rate=float(achieved)/total*100, start=start, end=local_now)


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


class MessageList(TemplateView):
    """
    author: Zhoudong
    显示所有短信用于编辑
    """
    template_name = 'messages.jade'
    permission_classes = (IsAdminUserOrReadOnly,)

    def get_context_data(self, **kwargs):

        messages = MessageInRedis.objects.all()

        return {
            "messages": messages
        }


class MessageEdit(APIView):
    """
    author: Zhoudong
    根据时间段, 获取到达率
    method: GET.
    改成定期执行加入数据库, 统计一定时间段的到达率
    """
    permission_classes = (IsAdminUserOrReadOnly,)

    def get(self, request):

        redirect_url = reverse('wanglibao:message_for_admin')

        mid = int(self.request.GET.get('mid', None))
        message_for = self.request.GET.get('message_for', None)
        title = self.request.GET.get('title', None)
        content = self.request.GET.get('content', None)

        try:
            message = MessageInRedis.objects.get_by_id(id=mid)
            message.message_for = message_for
            message.title = title
            message.content = content
            message.save()
        except Exception, e:
            print e

        return HttpResponseRedirect(redirect_url)
