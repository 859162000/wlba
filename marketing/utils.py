# -*- coding: utf-8 -*-

import pytz
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger
from django.db import connection
from django.db.models import Sum
from marketing.models import IntroducedBy, PromotionToken, ClientData, Channels
from wanglibao_p2p.models import AmortizationRecord, P2PRecord
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
        else:
            recordpromo = PromotionToken.objects.filter(token=invitecode).first()
            if recordpromo:
                introduced_by_user = User.objects.get(pk=recordpromo.pk)
                save_introducedBy(user, introduced_by_user)

        request.session[settings.PROMO_TOKEN_QUERY_STRING] = None

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


def pc_data_generator():
    # 累计交易金额
    p2p_amount = P2PRecord.objects.filter(catalog='申购').aggregate(Sum('amount'))['amount__sum']
    # 累计交易人数
    user_number = P2PRecord.objects.filter(catalog='申购').values('id').count()

    # 提前还款的收益
    income_pre = AmortizationRecord.objects.filter(catalog='提前还款').aggregate(Sum('interest'))['interest__sum']
    income_pre = income_pre if income_pre else 0
    # 非提前还款的收益（已发收益＋未发收益）
    sql = "select sum(a.interest) from wanglibao_p2p_useramortization as a left join wanglibao_p2p_productamortization as b on a.product_amortization_id=b.id LEFT JOIN (select distinct product_id from wanglibao_p2p_p2pequity where confirm=True and not exists (select distinct a.product_id from wanglibao_p2p_productamortization a, wanglibao_p2p_amortizationrecord b where a.id=b.amortization_id and b.catalog='提前还款') ) as c on b.product_id=c.product_id;"
    cursor = connection.cursor()
    cursor.execute(sql)
    income = cursor.fetchone()
    cursor.close()
    user_income = income[0] + income_pre
    key = 'pc_index_data'
    return {
        'p2p_amount': float(p2p_amount),
        'user_number': user_number,
        'user_income': float(user_income)
    }