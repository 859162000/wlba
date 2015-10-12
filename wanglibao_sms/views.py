# -*- coding: utf-8 -*-
import logging
import urllib2
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http.response import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.generic import TemplateView
import pytz
from rest_framework import renderers
from rest_framework.views import APIView

from wanglibao import settings
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao.settings import SMS_MANDAO_USER_URL, SMS_MANDAO_SN, SMS_MANDAO_MD5_PWD, SMS_MANDAO_REPORT_URL
from wanglibao_sms.models import ArrivedRate, MessageInRedis


def get_user_messages():
    """
    author: zhoudong
    write user's messages into the log file in '/var/log/wanglibao/user_message/*.log'
    """
    logger = logging.getLogger('get_user_messages')

    url = SMS_MANDAO_USER_URL + '?sn=%s&pwd=%s' % (SMS_MANDAO_SN, SMS_MANDAO_MD5_PWD)
    ret = urllib2.urlopen(url).read()
    ret = ret.rsplit('</string>')[0].split('<string xmlns="http://tempuri.org/">')[1]

    if len(ret) < 10:
        try:
            logger.debug(u'本阶段没数据\n')
        except Exception, e:
            print logger.debug(e)
    else:
        try:
            ret = '\n' + ret + '\n'
            logger.debug(ret)
        except Exception, e:
            print logger.debug(e)
    return ret


def get_report_messages():
    """
    author: zhoudong
    write user's messages into the log file in '/var/log/wanglibao/report_message/*.log'
    and save to the DB every 10 minutes
    """
    logger = logging.getLogger('get_report_messages')

    url = SMS_MANDAO_REPORT_URL + '?sn=%s&pwd=%s&maxid=1' % (SMS_MANDAO_SN, SMS_MANDAO_MD5_PWD)
    ret = urllib2.urlopen(url).read()
    ret = ret.rsplit('</string>')[0].split('<string xmlns="http://tempuri.org/">')[1]

    if len(ret) < 10:
        try:
            logger.info(u'本阶段没数据\n')
        except Exception, e:
            print logger.info(e)
    else:
        ret = '\n' + ret + '\r\n'
        try:
            logger.info(ret)
        except Exception, e:
            print logger.info(e)

        achieved = ret.count('DELIVRD') + ret.count(',0,')
        total = ret.count('\r\n')

        now = timezone.now()
        local_now = timezone.localtime(now).replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
        delta = settings.MESSAGE_TIME_DELTA
        start = local_now - delta

        ArrivedRate.objects.create(channel=u'慢道', achieved=achieved, total_amount=total,
                                   rate=float(achieved)/total*100, start=start, end=local_now)

    return ret


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
