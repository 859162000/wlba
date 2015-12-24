# -*- coding: utf-8 -*-

import pytz
import time
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger
from django.db import connection
from django.db.models import Sum
from marketing.models import (IntroducedBy, PromotionToken, ClientData, Channels,
                              ChannelsNew, RevenueExchangeRepertory, RevenueExchangeRecord,
                              RevenueExchangePlan, RevenueExchangeOrder)
from wanglibao_p2p.models import AmortizationRecord, P2PRecord
from wanglibao.settings import THREE_DEFAULT_CHANNEL_CODE
from wanglibao.settings import ENV, ENV_PRODUCTION
import logging


logger = logging.getLogger('p2p')


def get_channel_record(channel_code):
    record = Channels.objects.filter(code=channel_code).first()
    # if record:
    #     if record.is_abandoned or record.coop_status > 0:
    #         record = Channels.objects.get(code=THREE_DEFAULT_CHANNEL_CODE)
    #     else:
    #         record = None
    return record


def get_user_channel_record(user_id):
    channel = Channels.objects.filter(introducedby__user_id=user_id).first()
    return channel


def set_promo_user(request, user, invitecode=''):
    if not user:
        return

    if not invitecode:
        invitecode = request.session.get(settings.PROMO_TOKEN_QUERY_STRING, None)

    if invitecode:
        record = get_channel_record(invitecode)
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

# Modify by hb on 2015-12-18 : add return value
def log_clientinfo(device, atype, user_id=0, order_id=0, amount=0):
    # fix@chenweibi, add order_id
    if type(device) != dict:
        return False

    if "device_type" not in device:
        return False

    app_version = device.get('app_version', '')
    if device['device_type'] == "pc" and app_version != 'wlb_h5':
        return False

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
    ci.order_id = order_id
    ci.save()

    return True


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
    else:
        source_time = source_date.time()

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
    down_line_amount = 1355000000.00
    yesterday = datetime.now()-timedelta(1)
    yesterday_start = local_to_utc(yesterday, 'min')
    yesterday_end = local_to_utc(yesterday, 'max')
    # 累计交易金额
    p2p_amount = P2PRecord.objects.filter(catalog='申购', create_time__lte=yesterday_end).aggregate(Sum('amount'))['amount__sum']
    # 昨日交易总额
    p2p_amount_yesterday = P2PRecord.objects.filter(catalog='申购', create_time__gte=yesterday_start, create_time__lte=yesterday_end).aggregate(Sum('amount'))['amount__sum']
    # 累计交易人数
    user_number = P2PRecord.objects.filter(catalog='申购', create_time__lte=yesterday_end).values('id').count()
    #累计注册人数
    p2p_register_number = User.objects.filter(date_joined__lte=yesterday_end).all().values('id').count()
    # 提前还款的收益
    income_pre = AmortizationRecord.objects.filter(catalog='提前还款', created_time__lte=yesterday_end).aggregate(Sum('interest'))['interest__sum']
    income_pre = income_pre if income_pre else 0
    # 非提前还款的收益（已发收益＋未发收益）
    sql = "select sum(a.interest) from wanglibao_p2p_useramortization as a left join wanglibao_p2p_productamortization as b on a.product_amortization_id=b.id LEFT JOIN (select distinct product_id from wanglibao_p2p_p2pequity where confirm=True and not exists (select distinct a.product_id from wanglibao_p2p_productamortization a, wanglibao_p2p_amortizationrecord b where a.id=b.amortization_id and b.catalog='提前还款') ) as c on b.product_id=c.product_id;"
    cursor = connection.cursor()
    cursor.execute(sql)
    income = cursor.fetchone()
    cursor.close()
    user_income = income[0] + income_pre
    key = 'pc_index_data'
    p2p_amount = 0 if p2p_amount is None else p2p_amount
    p2p_amount_yesterday = 0 if p2p_amount_yesterday is None else p2p_amount_yesterday
    return {
        'p2p_amount': float(p2p_amount) + down_line_amount,
        'user_number': user_number,
        'user_income': float(user_income),
        'p2p_register_number':p2p_register_number,
        "p2p_amount_yesterday":float(p2p_amount_yesterday)
    }


def generate_revenue_exchange_record(user, product, order_id=None, description=None):
    """生成p2p奖品流水"""

    try:
        # 查询收益兑换计划
        exchange_plan = RevenueExchangePlan.objects.get(product=product)
        reward_type = exchange_plan.reward_name
        price = product.equality_prize_amount

        # 查询收益兑换订单
        p2p_record = P2PRecord.objects.filter()
        exchange_order = RevenueExchangeOrder.objects.get(user, order_id=)

        p2p_reward = RevenueExchangeRepertory.objects.filter(type=reward_type, is_used=False,
                                                             price=price).first()
        if p2p_reward:
            p2p_reward_record = RevenueExchangeRecord()
            p2p_reward_record.user = user
            p2p_reward_record.reward = p2p_reward
            p2p_reward_record.order_id = order_id
            p2p_reward_record.description = description
            p2p_reward_record.save()

            p2p_reward.is_used = True
            p2p_reward.save()
            return True
        else:
            # FixMe, 如果是线上环境就给管理员发短信
            # if ENV == ENV_PRODUCTION:

            logger.warning("unfounded p2p_reward for user[%s], type[%s], price[%s]" %
                           (user_id, _type, _price))
    except Exception, e:
        logger.info("generate p2p_reward_record failed")
        logger.error(e)
