# -*- coding: utf-8 -*-

import pytz
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger
from marketing.models import IntroducedBy, PromotionToken, ClientData, Channels
from wanglibao_redpack import backends as redpack_backends
import logging


logger = logging.getLogger('p2p')


def set_promo_user(request, user, invitecode=''):
    if not user:
        return

    if not invitecode:
        invitecode = request.session.get(settings.PROMO_TOKEN_QUERY_STRING, None)

    product_id = request.session.get(settings.PROMO_TOKEN_PRODUCT, None)

    if invitecode:
        record = Channels.objects.filter(code=invitecode).first()
        if record:
            save_introducedBy_channel(user, record)
        else:
            recordpromo = PromotionToken.objects.filter(token=invitecode).first()
            if recordpromo:
                introduced_by_user = User.objects.get(pk=recordpromo.pk)
                save_introducedBy(user, introduced_by_user)
                redpack_backends.increase_hike(introduced_by_user, product_id)

        request.session[settings.PROMO_TOKEN_QUERY_STRING] = None
        request.session[settings.PROMO_TOKEN_PRODUCT] = None

       # user_id = request.session.get(settings.PROMO_TOKEN_USER_SESSION_KEY, None)
       # if user_id:
       #     introduced_by_user = User.objects.get(pk=user_id)
       #     save_introducedBy(user, introduced_by_user)

       #     # Clean the session
       #     del request.session[settings.PROMO_TOKEN_USER_SESSION_KEY]

def save_introducedBy(user, introduced_by_user):
    record = IntroducedBy()
    record.introduced_by = introduced_by_user
    record.user = user
    record.save()

def save_introducedBy_channel(user, channel):
    record = IntroducedBy()
    record.channel = channel
    record.user = user
    record.save()


def save_client(request, phone, action):
    """
    保存客户端信息
    :param request: 客户端请求
    :param phone:   请求用户电话号码
    :param action:  动作，0表示注册，1表示购买
    :return:
    """

    version = request.DATA.get('version', '')
    userdevice = request.DATA.get('userDevice', '')
    network = request.DATA.get('network', '')
    channelid = request.DATA.get('channelId', '')
    try:
        c = ClientData(version=version, userdevice=userdevice, network=network, channelid=channelid,
                       phone=phone, action=action)
        c.save()
    except:
        logger.error(u"客户端信息失败，请检查参数")


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


def paginator_factory(obj, page=1, limit=100):
    """ the page paginator generator

    Args:
        obj: the QuerySet of the query result
        page: the page number to response
        limit: the records number of this page

    return the instance of paginator
    """
    paginator = Paginator(obj, limit)
    try:
        ins = paginator.page(page)
    except PageNotAnInteger:
        ins = paginator.page(1)
    except Exception:
        ins = paginator.page(paginator.num_pages)

    return ins
