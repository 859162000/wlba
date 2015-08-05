# -*- coding: utf-8 -*-

import pytz
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger
from marketing.models import IntroducedBy, PromotionToken, ClientData, Channels
from wanglibao_p2p.models import P2PProduct
from wanglibao_account.models import Binding
import logging


logger = logging.getLogger('p2p')


def set_promo_user(request, user, invitecode=''):
    if not user:
        return

    if not invitecode:
        invitecode = request.session.get(settings.PROMO_TOKEN_QUERY_STRING, None)


    if invitecode:
        record = Channels.objects.filter(code=invitecode).first()
        if record:
            save_introducedBy_channel(user, record)
#            tid = request.DATA.get('tid', '').strip()
#            save_to_binding(user, record.name, tid)
        else:
            recordpromo = PromotionToken.objects.filter(token=invitecode).first()
            if recordpromo:
                introduced_by_user = User.objects.get(pk=recordpromo.pk)
                save_introducedBy(user, introduced_by_user)

        request.session[settings.PROMO_TOKEN_QUERY_STRING] = None

def save_to_binding(user, btype, bid):
        if btype and bid:
            binding = Binding()
            binding.user = user
            binding.btype = btype
            binding.bid = bid
            binding.save()

def save_introducedBy(user, introduced_by_user, product_id=0):
    record = IntroducedBy()
    record.introduced_by = introduced_by_user
    record.user = user
    #if product_id:
    #    pt = P2PProduct.objects.filter(id=product_id).first()
    #    if pt:
    #        record.product_id=product_id
    record.product_id=product_id
    record.save()

def save_introducedBy_channel(user, channel):
    record = IntroducedBy()
    record.channel = channel
    record.user = user
    record.save()

def log_clientinfo(device, atype, user_id=0, amount=0):
    if type(device) != dict:
        return
    if "device_type" not in device or device['device_type'] == "pc":
        return
    ci = ClientData()
    if atype=="register": action='R'
    elif atype=="login": action='L'
    elif atype=="validation": action='V'
    elif atype=="deposit": action='D'
    elif atype=="buy": action='B'
    elif atype=="withdraw": action='W'

    if device['device_type'] == "android":
        device['model'] = device['model'][:-8]
    ci.version = device['app_version']
    ci.userdevice = device['model']
    ci.os = device['device_type']
    ci.os_version = device['os_version']
    ci.network = device['network']
    ci.channel = device['channel_id']
    ci.user_id = user_id
    ci.amount = amount
    ci.action = action
    ci.save()


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
