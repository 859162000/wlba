#!/usr/bin/env python
# encoding:utf-8

import sys

from wanglibao_margin.models import MonthProduct

reload(sys)
sys.setdefaultencoding('utf8')

import pytz
import time
import datetime
import json
import re
import logging
import decimal
from django.utils import timezone
from django.db.models import Sum
from django.db import transaction
from wanglibao_redpack.models import RedPack, RedPackRecord, RedPackEvent, InterestHike, Income
from wanglibao_p2p.models import P2PRecord, P2PProduct, P2PEquity
from marketing import helper
from wanglibao_sms import messages
# from wanglibao_sms.tasks import send_messages
# from wanglibao_sms.send_php import PHPSendSMS
from wanglibao_account import message as inside_message
from wanglibao_pay.util import fmt_two_amount
from misc.models import Misc
from wanglibao_margin.marginkeeper import MarginKeeper
from marketing.models import IntroducedBy
from wanglibao_sms.tasks import send_sms_one


logger = logging.getLogger(__name__)

REDPACK_RULE = {"direct": "-", "fullcut": "-", "percent": "*", "interest_coupon": "~"}


def local_datetime(dt):
    return timezone.get_current_timezone().normalize(dt)


def stamp(dt):
    return long(time.mktime(local_datetime(dt).timetuple()))


def list_redpack(user, status, device_type, product_id=0, rtype='redpack', app_version=''):
    if status not in ("all", "available"):
        return {"ret_code": 30151, "message": u"参数错误"}

    if not user.is_authenticated():
        packages = {"available": []}
        return {"ret_code": 0, "packages": packages}

    device_type = _decide_device(device_type)
    period_name = dict(RedPackEvent.PERIOD_TYPE)
    if status == "available":
        packages = {"available": []}

        # 检测是否有配置不使用理财券的产品id, 如果有且符合条件,则返回空理财券列表
        p2p_ids = Misc.objects.filter(key='no_coupons_p2p_ids').first()
        if p2p_ids:
            try:
                p2p_ids_value = p2p_ids.value
                no_coupons_p2p_ids = [int(p2pid) for p2pid in p2p_ids_value.split(',') if p2pid != '']
                if int(product_id) in no_coupons_p2p_ids:
                    return {"ret_code": 0, "packages": packages}
            except Exception:
                logger.exception('misc error, product ids')
                pass

        try:
            product = P2PProduct.objects.filter(pk=product_id).values('id', 'period', 'types_id', 'pay_method').first()
        except Exception:
            product = None

        try:
            records_count = RedPackRecord.objects.filter(user=user, product_id=product_id) \
                .filter(redpack__event__rtype='interest_coupon').count()
        except Exception:
            records_count = 0

        if records_count == 0:
            # 红包
            records = RedPackRecord.objects.filter(user=user, order_id=None, product_id=None)\
                .exclude(redpack__event__rtype='interest_coupon').select_related('redpack', 'redpack__event')\
                .order_by('-redpack__event__amount')
            for x in records:
                if x.order_id:
                    continue
                redpack = x.redpack
                if redpack.status == "invalid":
                    continue
                event = x.redpack.event
                p2p_id = int(event.p2p_id) or 0
                p2p_types_id = 0
                p2p_types_name = ''
                if product:
                    p2p_res_id = int(product['id'])
                    if p2p_id:
                        if p2p_id != p2p_res_id:
                            continue
                    if event.p2p_types:
                        p2p_types_id = int(event.p2p_types.id)
                        p2p_types_name = event.p2p_types.name
                        if product['types_id']:
                            if product['types_id'] != p2p_types_id:
                                continue
                        # if p2p_id:
                        #     if p2p_id != p2p_res_id:
                        #         continue
                    if event.period:
                        event_period = int(event.period)
                        period_type = event.period_type if event.period_type else 'month'
                        product_period = int(product['period'])
                        pay_method = product['pay_method']
                        if period_type == 'month' or period_type == 'day':
                            if product_period != event_period:
                                continue
                        else:
                            matches = re.search(u'日计息', pay_method)
                            if matches and matches.group():
                                if period_type == 'month_gte':
                                    if event_period * 30 > product_period:
                                        continue
                                elif period_type == 'month_lte':
                                    if event_period * 30 < product_period:
                                        continue
                                elif period_type == 'day_lte':
                                    if event_period < product_period:
                                        continue
                                elif period_type == 'day_gte':
                                    if event_period > product_period:
                                        continue
                            else:
                                if period_type == 'month_gte':
                                    if event_period > product_period:
                                        continue
                                elif period_type == 'month_lte':
                                    if event_period < product_period:
                                        continue
                                elif period_type == 'day_lte':
                                    if event_period < product_period * 30:
                                        continue
                                elif period_type == 'day_gte':
                                    if event_period > product_period * 30:
                                        continue
                        # if p2p_id:
                        #     if p2p_id != p2p_res_id:
                        #         continue

                start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
                                                          x.created_at, event.available_at, event.unavailable_at)
                end_time_day = end_time.strftime('%Y-%m-%d')
                period_tmp = event.period
                if device_type == 'ios' or device_type == 'android':
                    if app_version <= "2.9.0":
                        period_type_event = event.period_type if event.period_type not in ('month_lte', 'day_lte') else ''
                        if device_type == 'ios' and event.period_type in ('month_lte', 'day_lte'):
                            period_tmp = 0
                    else:
                        period_type_event = event.period_type
                else:
                    period_type_event = event.period_type

                obj = {
                    "name": event.name, "method": REDPACK_RULE[event.rtype], "amount": event.amount,
                    "id": x.id, "invest_amount": event.invest_amount, 'end_time_day': end_time_day,
                    "unavailable_at": stamp(end_time), "event_id": event.id,
                    "period": period_tmp,
                    "period_type": period_type_event,
                    "period_name": u'限' + str(event.period) + period_name.get(event.period_type, ''),
                    "p2p_types_id": p2p_types_id, "p2p_types_name": p2p_types_name,
                    "highest_amount": event.highest_amount, "order_by": 2
                }
                if start_time < timezone.now() < end_time:
                    if event.apply_platform == "all" or event.apply_platform == device_type or \
                            (device_type in ('ios', 'android') and event.apply_platform == 'app'):
                        if obj['method'] == REDPACK_RULE['percent']:
                            obj['amount'] /= 100.0
                        packages['available'].append(obj)
            # 排序
            packages['available'].sort(key=lambda x: x['highest_amount'], reverse=True)
            packages['available'].sort(key=lambda x: x['end_time_day'])
            packages['available'].sort(key=lambda x: x['amount'], reverse=True)

        # 加息券
        # 检测app版本号，小于2.5.2版本不返回加息券列表
        is_show = True
        if device_type == 'ios' or device_type == 'android':
            if app_version < "2.5.3":
                is_show = False
        if is_show:
            records_count_p2p = RedPackRecord.objects.filter(user=user, product_id=product_id).count()
            if records_count_p2p == 0:
                coupons = RedPackRecord.objects.filter(user=user, order_id=None, product_id=None)\
                    .filter(redpack__event__rtype='interest_coupon').select_related('redpack', 'redpack__event')\
                    .order_by('-redpack__event__amount')
                for coupon in coupons:
                    if coupon.order_id:
                        continue
                    redpack = coupon.redpack
                    if redpack.status == 'invalid':
                        continue
                    event = coupon.redpack.event
                    p2p_id = int(event.p2p_id) or 0
                    p2p_types_id = 0
                    p2p_types_name = ''
                    if product:
                        p2p_res_id = int(product['id'])
                        if p2p_id:
                            if p2p_id != p2p_res_id:
                                continue
                        if event.p2p_types:
                            p2p_types_id = int(event.p2p_types.id)
                            p2p_types_name = event.p2p_types.name
                            if product['types_id']:
                                if product['types_id'] != p2p_types_id:
                                    continue
                        if event.period:
                            event_period = int(event.period)
                            period_type = event.period_type if event.period_type else 'month'
                            product_period = int(product['period'])
                            pay_method = product['pay_method']
                            if period_type == 'month' or period_type == 'day':
                                if product_period != event_period:
                                    continue
                            else:
                                matches = re.search(u'日计息', pay_method)
                                if matches and matches.group():
                                    if period_type == 'month_gte':
                                        if event_period * 30 > product_period:
                                            continue
                                    elif period_type == 'month_lte':
                                        if event_period * 30 < product_period:
                                            continue
                                    elif period_type == 'day_lte':
                                        if event_period < product_period:
                                            continue
                                    elif period_type == 'day_gte':
                                        if event_period > product_period:
                                            continue
                                else:
                                    if period_type == 'month_gte':
                                        if event_period > product_period:
                                            continue
                                    elif period_type == 'month_lte':
                                        if event_period < product_period:
                                            continue
                                    elif period_type == 'day_lte':
                                        if event_period < product_period * 30:
                                            continue
                                    elif period_type == 'day_gte':
                                        if event_period > product_period * 30:
                                            continue

                    start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
                                                              coupon.created_at, event.available_at, event.unavailable_at)
                    end_time_day = end_time.strftime('%Y-%m-%d')
                    period_tmp = event.period
                    if device_type == 'ios' or device_type == 'android':
                        if app_version <= "2.9.0":
                            period_type_event = event.period_type if event.period_type not in ('month_lte', 'day_lte') else ''
                            if device_type == 'ios' and event.period_type in ('month_lte', 'day_lte'):
                                period_tmp = 0
                        else:
                            period_type_event = event.period_type
                    else:
                        period_type_event = event.period_type

                    obj = {
                        "name": event.name, "method": REDPACK_RULE[event.rtype], "amount": event.amount,
                        "id": coupon.id, "invest_amount": event.invest_amount, 'end_time_day': end_time_day,
                        "unavailable_at": stamp(end_time), "event_id": event.id,
                        "period": period_tmp,
                        "period_type": period_type_event,
                        "period_name": u'限' + str(event.period) + period_name.get(event.period_type, ''),
                        "p2p_types": p2p_types_id, "p2p_types_name": p2p_types_name,
                        "highest_amount": event.highest_amount, "order_by": 1
                    }

                    if start_time < timezone.now() < end_time:
                        if event.apply_platform == "all" or event.apply_platform == device_type or \
                                (device_type in ('ios', 'android') and event.apply_platform == 'app'):
                            if obj['method'] == REDPACK_RULE['interest_coupon']:
                                obj['amount'] /= 100.0
                            packages['available'].append(obj)
                # 排序
                packages['available'].sort(key=lambda x: x['end_time_day'])
                packages['available'].sort(key=lambda x: x['amount'], reverse=True)

        # packages['available'].sort(key=lambda x: x['unavailable_at'])
        packages['available'].sort(key=lambda x: x['order_by'], reverse=True)
    else:
        packages = {"used": [], "unused": [], "expires": [], "invalid": []}
        if rtype == 'redpack':
            records = RedPackRecord.objects.filter(user=user).exclude(redpack__event__rtype='interest_coupon')\
                .select_related('redpack__event')
        elif rtype == 'coupon':
            records = RedPackRecord.objects.filter(user=user).filter(redpack__event__rtype='interest_coupon')\
                .select_related('redpack__event')
        else:
            records = RedPackRecord.objects.filter(user=user).select_related('redpack__event')

        for x in records:
            event = x.redpack.event
            if event.rtype == 'interest_coupon':
                order_by = 1
                if device_type == 'ios' or device_type == 'android':
                    if app_version < "2.5.3":
                        continue
            else:
                order_by = 2
            start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
                                                      x.created_at, event.available_at, event.unavailable_at)

            if event.p2p_types:
                p2p_types_id = int(event.p2p_types.id)
                p2p_types_name = event.p2p_types.name
            else:
                p2p_types_id = 0
                p2p_types_name = ''
            period_tmp = event.period
            if device_type == 'ios' or device_type == 'android':
                if app_version <= "2.9.0":
                    period_type_event = event.period_type if event.period_type not in ('month_lte', 'day_lte') else ''
                    if device_type == 'ios' and event.period_type in ('month_lte', 'day_lte'):
                        period_tmp = 0
                else:
                    period_type_event = event.period_type
            else:
                period_type_event = event.period_type

            obj = {
                "name": event.name, "receive_at": stamp(x.created_at),
                "available_at": stamp(start_time), "unavailable_at": stamp(end_time),
                "id": x.id, "invest_amount": event.invest_amount, "amount": event.amount, "event_id": event.id,
                "highest_amount": event.highest_amount,
                "period": period_tmp,
                "period_type": period_type_event,
                "period_name": str(event.period) + period_name.get(event.period_type, ''),
                "p2p_types_id": p2p_types_id, "p2p_types_name": p2p_types_name,
                "method": REDPACK_RULE[event.rtype], "order_by": order_by
            }

            if obj['method'] == REDPACK_RULE['percent'] or obj['method'] == REDPACK_RULE['interest_coupon']:
                obj['amount'] /= 100.0

            if x.order_id:
                # 增加对月利宝使用过的红包处理
                pr = P2PRecord.objects.filter(order_id=x.order_id).first()
                if pr:
                    obj.update({"product": pr.product.name, "apply_at": stamp(x.apply_at),
                                "apply_platform": x.apply_platform})
                    packages['used'].append(obj)
                    packages['used'].sort(key=lambda x: x['unavailable_at'])
                    packages['used'].sort(key=lambda x: x['order_by'])
                else:
                    obj.update({"product": u'月利宝产品', "apply_at": stamp(x.apply_at),
                                "apply_platform": x.apply_platform})
                    packages['used'].append(obj)
                    packages['used'].sort(key=lambda x: x['unavailable_at'])
                    packages['used'].sort(key=lambda x: x['order_by'])
                    logger.debug(u'月利宝产品使用的红包, order_id = {}, redpackrecord_id = {}'
                                 .format(x.order_id, x.id))
                    continue
            else:
                if x.redpack.status == "invalid":
                    packages['invalid'].append(obj)
                    packages['invalid'].sort(key=lambda x: x['unavailable_at'])
                    packages['invalid'].sort(key=lambda x: x['order_by'])
                else:
                    if end_time < timezone.now():
                        packages['expires'].append(obj)
                        packages['expires'].sort(key=lambda x: x['unavailable_at'])
                        packages['expires'].sort(key=lambda x: x['order_by'])
                    else:
                        packages['unused'].append(obj)
                        packages['unused'].sort(key=lambda x: x['unavailable_at'])
                        packages['unused'].sort(key=lambda x: x['order_by'])

    return {"ret_code": 0, "packages": packages}


def utc_transform(dt):
    tp = dt.timetuple()
    stamp = time.mktime(tp)
    dt = datetime.datetime.fromtimestamp(stamp,pytz.utc)
    return dt.replace(tzinfo=None)


def local_transform_str(dt):
    dt = dt.replace(tzinfo=pytz.utc)
    newdt = dt.astimezone(pytz.timezone("Asia/Shanghai"))
    return newdt.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")


def exchange_redpack(token, device_type, user, app_version=''):
    if token == "":
        return {"ret_code": 30161, "message": u"请输入兑换码"}
    token = token.replace("'", "").replace('"', "").replace("`", "")
    #redpack = RedPack.objects.filter(token=token).first()
    redpack = RedPack.objects.extra(where=["binary token='%s'" % token]).first()
    if not redpack:
        return {"ret_code": 30162, "message": u"请输入正确的兑换码"}
    if redpack.status == "used":
        return {"ret_code": 30163, "message": u"兑换码已被兑换"}
    elif redpack.status == "invalid":
        return {"ret_code": 30164, "message": u"请输入有效的兑换码"}
    event = redpack.event
    device_type = _decide_device(device_type)
    if event.rtype == 'interest_coupon':
        if device_type == 'ios' or device_type == 'android':
            if app_version < "2.5.3":
                return {"ret_code": 30160, "message": u"版本过低，不支持使用加息券，赶快升级"}
    now = timezone.now()
    if event.give_start_at > now:
        return {"ret_code": 30165, "message": u"请在%s之后兑换" % local_datetime(event.give_start_at).strftime("%Y-%m-%d %H:%M:%S")}
    elif event.give_end_at < now:
        return {"ret_code": 30166, "message": u"兑换码已过期"}
    if event.target_channel != "":
        ch = helper.which_channel(user)
        if ch != event.target_channel:
            return {"ret_code": 30167, "message": u"不符合领取条件"}
    if event.give_platform != "all" and (event.give_platform != device_type or (event.give_platform == 'app' and device_type not in ('ios', 'android'))):
        return {"ret_code": 30168, "message": u"不符合领取条件"}

    if event.amount == 0:
        return {"ret_code": 301641, "message": u"请输入有效的兑换码"}
    else:
        record = RedPackRecord()
        record.user = user
        record.redpack = redpack
        record.change_platform = device_type
        redpack.status = "used"
        redpack.save()
        record.save()

    start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
                                              record.created_at, event.available_at, event.unavailable_at)

    _send_message(user, event, end_time)
    return {"ret_code": 0, "message": u"兑换成功"}


def _send_message(user, event, end_time):
    fmt_str = "%Y年%m月%d日"
    if end_time:
        unavailable_at = end_time
    else:
        unavailable_at = event.unavailable_at
    give_time = timezone.localtime(unavailable_at).strftime(fmt_str)
    mtype = 'activity'
    rtype = u'元红包'
    coupon_amount = event.amount
    if event.rtype == 'interest_coupon':
        rtype = u'%加息券'
    if event.rtype == 'percent':
        coupon_amount = event.highest_amount

    # 发送短信,功能推送id: 4
    # 模板中的参数变量必须以 name=value 的形式传入
    phone = user.wanglibaouserprofile.phone
    # PHPSendSMS().send_sms_one(4, phone, 'phone', amount=coupon_amount, rtype=rtype)
    send_sms_one.apply_async(kwargs={
                                "rule_id": 4,
                                "phone": phone,
                                "user_type":'phone',
                                "amount":coupon_amount,
                                "rtype":rtype
                                    })
    # send_messages.apply_async(kwargs={
    #     'phones': [user.wanglibaouserprofile.phone],
    #     'messages': [messages.red_packet_get_alert(coupon_amount, rtype)],
    #     'ext': 666,  # 营销类短信发送必须增加ext参数,值为666
    # })
    if event.rtype == 'percent':
        title, content = messages.msg_redpack_give_percent(event.amount, event.highest_amount, event.name, give_time)
    elif event.rtype == 'interest_coupon':
        title, content = messages.msg_give_coupon(event.name, event.amount, give_time)
        mtype = 'coupon'
    else:
        title, content = messages.msg_redpack_give(event.amount, event.name, give_time)
    inside_message.send_one.apply_async(kwargs={
        "user_id": user.id,
        "title": title,
        "content": content,
        "mtype": mtype
    })


def _decide_device(device_type):
    device_type = device_type.lower()
    if device_type == "ios":
        return "ios"
    elif device_type == "android":
        return "android"
    elif device_type == "all":
        return "all"
    else:
        return "pc"


def give_register_redpack(user, device_type):
    _give_redpack(user, "register", device_type)


def give_validation_redpack(user, device_type):
    _give_redpack(user, "validation", device_type)


def give_first_pay_redpack(user, device_type):
    _give_redpack(user, "first_pay", device_type)


def give_first_buy_redpack(user, device_type):
    _give_redpack(user, "first_buy", device_type)

# def give_first_bind_wx_redpack(user, device_type):
#     return _give_one_redpack(user, 'first_bind_weixin', u'首次绑定微信红包', device_type)


def give_buy_redpack(user, device_type, give_mode='buy', describe=''):
    now = timezone.now()
    rps = RedPackEvent.objects.filter(give_mode=give_mode, invalid=False, give_start_at__lt=now, give_end_at__gt=now)
    if describe:
        rps = rps.filter(describe=describe)
    for x in rps:
        give_activity_redpack(user=user, event=x, device_type=device_type)


def _give_redpack(user, give_mode, device_type):
    now = timezone.now()
    user_ch = helper.which_channel(user)
    device_type = _decide_device(device_type)
    rps = RedPackEvent.objects.filter(give_mode=give_mode, invalid=False, give_start_at__lt=now, give_end_at__gt=now)
    for x in rps:
        #if x.target_channel != "" and user_ch != x.target_channel:
        if x.target_channel != "":
            chs = x.target_channel.split(",")
            chs = [m for m in chs if m.strip()!=""]
            if user_ch not in chs:
                continue
        redpack = RedPack.objects.filter(event=x, status="unused").first()
        if redpack:
            event = redpack.event
            give_pf = event.give_platform
            if give_pf == "all" or give_pf == device_type:
                if redpack.token != "":
                    redpack.status = "used"
                    redpack.save()
                record = RedPackRecord()
                record.user = user
                record.redpack = redpack
                record.change_platform = device_type
                record.save()

                start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
                                                          record.created_at, event.available_at, event.unavailable_at)
                _send_message(user, event, end_time)


# def _give_one_redpack(user, give_mode, describe, device_type):
#     now = timezone.now()
#     user_ch = helper.which_channel(user)
#     device_type = _decide_device(device_type)
#     rps = RedPackEvent.objects.filter(give_mode=give_mode, describe=describe, invalid=False, give_start_at__lt=now, give_end_at__gt=now).first()
#     if rps:
#         #if x.target_channel != "" and user_ch != x.target_channel:
#         if rps.target_channel != "":
#             chs = rps.target_channel.split(",")
#             chs = [m for m in chs if m.strip()!=""]
#             if user_ch not in chs:
#                 return None
#         redpack = RedPack.objects.filter(event=rps, status="unused").first()
#         if redpack:
#             event = redpack.event
#             give_pf = event.give_platform
#             if give_pf == "all" or give_pf == device_type:
#                 if redpack.token != "":
#                     redpack.status = "used"
#                     redpack.save()
#                 record = RedPackRecord()
#                 record.user = user
#                 record.redpack = redpack
#                 record.change_platform = device_type
#                 record.save()
#
#                 start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
#                                                           record.created_at, event.available_at, event.unavailable_at)
#                 _send_message(user, event, end_time)
#                 return record.id
#     return None


#发放奖励类型的红包
def give_activity_redpack(user, event, device_type, just_one_packet=False, check_issue_time=False):
    """

    :param user:
    :param event: 支持RedPackEevent对象或是一个event的名字
    :param device_type:
    :param just_one_packet: 置为True，对于某个红包活动用户只能获得一个红包，不能获得多个
    :param check_issue_time：检查发放时间，超期不发放
    :return:
    """
    device_type = _decide_device(device_type)
    # 后台设置必须保证红包的event不重名
    if not isinstance(event, RedPackEvent):
        try:
            event = RedPackEvent.objects.get(name=event)
        except:
            return False, u"活动名称错误"
    #检查红包发放时间
    now = timezone.now()
    if now < event.give_start_at or now > event.give_end_at:
        return False, u'活动已过期'
    redpack = RedPack.objects.filter(event=event, status="unused").first()
    if not redpack:
        return False, u"没有此优惠券"
    if redpack.token != "":
        redpack.status = "used"
        redpack.save()
    if just_one_packet and RedPackRecord.objects.filter(redpack=redpack, user=user).exists():
        return False, u"限领一个红包"
    record = RedPackRecord()
    record.user = user
    record.redpack = redpack
    record.change_platform = device_type
    record.save()

    start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
                                              record.created_at, event.available_at, event.unavailable_at)
    _send_message(user, event, end_time)
    return True,""

# Add by hb on 2015-12-14
def give_activity_redpack_new(user, event, device_type, just_one_packet=False, check_issue_time=False):
    """

    :param user:
    :param event: 支持RedPackEevent对象或是一个event的名字
    :param device_type:
    :param just_one_packet: 置为True，对于某个红包活动用户只能获得一个红包，不能获得多个
    :param check_issue_time：检查发放时间，超期不发放
    :return:
    """
    device_type = _decide_device(device_type)
    # 后台设置必须保证红包的event不重名
    if not isinstance(event, RedPackEvent):
        try:
            event = RedPackEvent.objects.get(name=event)
        except:
            return False, u"活动名称错误", 0
    #检查红包发放时间
    now = timezone.now()
    if now < event.give_start_at or now > event.give_end_at:
        return False, u'活动已过期', 0
    redpack = RedPack.objects.filter(event=event, status="unused").first()
    if not redpack:
        return False, u"没有此优惠券", 0
    if redpack.token != "":
        redpack.status = "used"
        redpack.save()
    if just_one_packet and RedPackRecord.objects.filter(redpack=redpack, user=user).exists():
        return False, u"限领一个红包", 0
    record = RedPackRecord()
    record.user = user
    record.redpack = redpack
    record.change_platform = device_type
    record.save()

    start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
                                              record.created_at, event.available_at, event.unavailable_at)
    _send_message(user, event, end_time)

    redpack_record_id = 0
    if record and record.id:
        redpack_record_id = record.id

    return True, "", redpack_record_id

def consume(redpack, amount, user, order_id, device_type, product_id):
    amount = fmt_two_amount(amount)
    record = RedPackRecord.objects.filter(user=user, id=redpack).first()
    redpack = record.redpack
    event = redpack.event
    device_type = _decide_device(device_type)

    start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
                                              record.created_at, event.available_at, event.unavailable_at)
    if not record:
        return {"ret_code": 30171, "message": u"优惠券不存在"}
    if record.order_id or record.product_id:
        return {"ret_code": 30172, "message": u"优惠券已使用"}
    if redpack.status == "invalid":
        return {"ret_code": 30173, "message": u"优惠券已作废"}
    if not start_time < timezone.now() < end_time:
        return {"ret_code": 30174, "message": u"优惠券不可使用"}
    if amount < event.invest_amount:
        return {"ret_code": 30175, "message": u"投资金额不满足优惠券规则%s" % event.invest_amount}
    if event.apply_platform != "all" and (event.apply_platform != device_type or (event.give_platform == 'app' and device_type not in ('ios', 'android'))):
        return {"ret_code": 30176, "message": u"此优惠券只能在%s平台使用" % event.apply_platform}

    rtype = event.rtype
    rule_value = event.amount
    if event.rtype != 'interest_coupon':
        deduct = _calc_deduct(amount, rtype, rule_value, event)
    else:
        deduct = 0

    record.order_id = order_id
    record.product_id = product_id
    record.apply_platform = device_type
    record.apply_amount = deduct
    record.apply_at = timezone.now()
    record.save()

    return {"ret_code": 0, "message": u"ok", "deduct": deduct, "rtype": event.rtype}


def _calc_deduct(amount, rtype, rule_value, event):
    if REDPACK_RULE[rtype] == "*":
        percent = decimal.Decimal(str(rule_value/100.0))
        deduct = amount * percent
        if event.highest_amount > 0:
            if deduct >= event.highest_amount:
                deduct = decimal.Decimal(event.highest_amount)
    elif REDPACK_RULE[rtype] == "-":
        if event.id == 7:
            t5 = amount * decimal.Decimal('0.005')
            if t5 >= rule_value:
                deduct = decimal.Decimal(str(rule_value))
            else:
                deduct = t5
        else:
            if amount <= rule_value:
                deduct = amount
            else:
                deduct = decimal.Decimal(str(rule_value))
    elif REDPACK_RULE[rtype] == "~":
        deduct = decimal.Decimal(0)
    real_deduct = deduct.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_DOWN)
    return real_deduct


def restore(order_id, amount, user):
    if type(amount) != decimal.Decimal:
        amount = fmt_two_amount(amount)
    record = RedPackRecord.objects.filter(user=user, order_id=order_id).first()
    if not record:
        return {"ret_code": -1, "message": "redpack not exists"}
    record.apply_platform = ""
    record.apply_at = None
    record.order_id = None
    record.product_id = None
    record.save()

    event = record.redpack.event
    rtype = event.rtype
    rule_value = event.amount
    # deduct = event.amount
    deduct = _calc_deduct(amount, rtype, rule_value, event)
    if rtype == "interest_coupon":
        logger.info(u"%s--%s 退回加息券 %s" % (event.name, record.id, timezone.now()))
        return {"ret_code": 1, "deduct": deduct}
    else:
        logger.info(u"%s--%s 退回账户 %s" % (event.name, record.id, timezone.now()))
        return {"ret_code": 0, "deduct": deduct}


def deduct_calc(amount, redpack_amount):
    if not amount or not redpack_amount:
        return {"ret_code": 30181, "message": u"金额错误"}
    try:
        float(amount)
        float(redpack_amount)
    except:
        return {"ret_code": 30182, "message": u"金额格式不正确"}

    t5 = fmt_two_amount(amount) * decimal.Decimal('0.005')
    redpack_amount = fmt_two_amount(redpack_amount)
    real_deduct = fmt_two_amount(0)
    if t5 >= redpack_amount:
        real_deduct = redpack_amount
    else:
        real_deduct = t5
    real_deduct = real_deduct.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_DOWN)
    return {"ret_code": 0, "deduct": real_deduct}


def get_interest_coupon(user, product_id):
    try:
        records = RedPackRecord.objects.filter(user=user, product_id=product_id) \
            .filter(redpack__event__rtype='interest_coupon').first()
    except Exception:
        records = None

    try:
        redpack_records = RedPackRecord.objects.filter(user=user, product_id=product_id) \
            .exclude(redpack__event__rtype='interest_coupon').first()
    except Exception:
        redpack_records = None

    if records:
        amount = records.redpack.event.amount
        return {"ret_code": 0, "used_type": u"coupon", "amount": amount}
    elif redpack_records:
        return {"ret_code": 0, "used_type": u"redpack", "message": u'已经用过红包，不能再使用加息券'}
    else:
        return {"ret_code": 3002, "message": u"还未使用理财券"}


def get_hike_nums(user):
    _nums = InterestHike.objects.filter(user=user, invalid=False).aggregate(Sum('intro_total'))
    if _nums['intro_total__sum']:
        nums = _nums['intro_total__sum']
    else:
        nums = 0
    return nums


def get_hike_amount(user):
    _amount = InterestHike.objects.filter(user=user, invalid=False, paid=True).aggregate(Sum('amount'))
    if not _amount['amount__sum']:
        amount = 0
    else:
        amount = _amount['amount__sum']
    return amount


def commission_exist(product):
    return Income.objects.filter(product=product).exists()
    # return record


def commission(user, product, equity, start):
    """
    计算全民佣金,千三,取消第二级
    :param user:
    :param product:
    :param equity:
    :param start:
    """
    _amount = P2PRecord.objects.filter(user=user, product=product, create_time__gt=start).aggregate(Sum('amount'))
    if _amount['amount__sum'] and _amount['amount__sum'] <= equity:
        commission = decimal.Decimal(_amount['amount__sum']) * decimal.Decimal("0.003")
        commission = commission.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_DOWN)
        first_intro = IntroducedBy.objects.filter(user=user).first()
        if first_intro and first_intro.introduced_by:
            first = MarginKeeper(first_intro.introduced_by)
            first.deposit(commission, catalog=u"全民淘金")

            income = Income(user=first_intro.introduced_by, invite=user, level=1,
                            product=product, amount=_amount['amount__sum'],
                            earning=commission, order_id=first.order_id, paid=True, created_at=timezone.now())
            income.save()

            # sec_intro = IntroducedBy.objects.filter(user=first_intro.introduced_by).first()
            # if sec_intro and sec_intro.introduced_by:
            #     second = MarginKeeper(sec_intro.introduced_by)
            #     second.deposit(commission, catalog=u"全民淘金")
            #
            #     income = Income(user=sec_intro.introduced_by, invite=user, level=2,
            #                     product=product, amount=_amount['amount__sum'],
            #                     earning=commission, order_id=second.order_id, paid=True, created_at=timezone.now())
            #     income.save()

# Add by hb on 2016-06-12
def commission_one(user, product, equity, start, end):
    """
    计算全民佣金,千三,取消第二级
    :param user:
    :param product:
    :param equity:
    :param start:
    """
    first_msg = u''
    sec_msg = u''

    _amount = P2PRecord.objects.filter(user=user, product=product, create_time__gt=start, create_time__lt=end).aggregate(Sum('amount'))
    if _amount['amount__sum'] and _amount['amount__sum'] <= equity:
        commission = decimal.Decimal(_amount['amount__sum']) * decimal.Decimal("0.003")
        commission = commission.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_DOWN)
        first_intro = IntroducedBy.objects.filter(user=user).first()
        if first_intro and first_intro.introduced_by:
            first_msg = commission_one_pay_one(first_intro.introduced_by, user, product, 1, _amount['amount__sum'], commission)

            # 二级关系佣金计算中止时间：
            sec_intro_end_time = timezone.datetime(2016, 6, 7, 16, 00, 00, tzinfo=timezone.utc)
            if first_intro.created_at >= sec_intro_end_time :
                sec_msg = u'sec_intro: [%s] introduced [%s] 邀请关系已过有效期(%s)，本次投资不结算二级佣金' % (first_intro.introduced_by.id, user.id, first_intro.created_at)
            else:
                sec_intro = IntroducedBy.objects.filter(user=first_intro.introduced_by).first()
                if sec_intro and sec_intro.introduced_by:
                    sec_msg = commission_one_pay_one(sec_intro.introduced_by, user, product, 2, _amount['amount__sum'], commission)

    return first_msg, sec_msg

# Add by hb on 2016-06-12
def commission_one_pay_one(user, invite, product, level, amount, earning):
    try:
        with transaction.atomic():
            income, create_flag = Income.objects.get_or_create(user=user, invite=invite, product=product,
                defaults={'level':level, 'amount':amount, 'earning':earning, 'paid':False})
            income = Income.objects.select_for_update().get(id=income.id)
            if income and not income.paid :
                margin = MarginKeeper(user)
                margin.deposit(earning, catalog=u"全民淘金")

                income.order_id = margin.order_id
                income.paid = True
                income.save()
                return u'Success: [%s] introduced [%s] in [%s], level:%s, amount:%s, earning:%s' % (user.id, invite.id, product, level, amount, earning)
            # Only for debug by hb on 2016-06-13
            if income and income.paid:
                return u'Ignore: [%s] introduced [%s] in [%s], level:%s, amount:%s, earning:%s' % (user.id, invite.id, product, level, amount, earning)
            if not income:
                return u'NotFound: [%s] introduced [%s] in [%s], level:%s, amount:%s, earning:%s' % (user.id, invite.id, product, level, amount, earning)
    except Exception, ex:
        return u'[%s] introduced [%s] in [%s], Except:(%s)' % (user.id, invite.id, product, ex)

def get_start_end_time(auto, auto_days, created_at, available_at, unavailable_at):
    if auto and auto_days > 0:
        start_tmp = created_at
        end_tmp = created_at + timezone.timedelta(days=int(auto_days))

        from marketing.utils import local_to_utc
        start_time = local_to_utc(datetime.datetime(start_tmp.year, start_tmp.month, start_tmp.day), 'min')
        end_time = local_to_utc(datetime.datetime(end_tmp.year, end_tmp.month, end_tmp.day), 'max')
    else:
        start_time = available_at
        end_time = unavailable_at
    return start_time, end_time


def get_app_version():
    misc = Misc.objects.filter(key='android_update').first()


# Add by hmm on 2016-2-4
#为二月红包宴年前专用接口，节后会调整
def give_activity_redpack_for_hby(user, event, device_type, just_one_packet=False, check_issue_time=False):
    """

    :param user:
    :param event: 支持RedPackEevent对象或是一个event的名字
    :param device_type:
    :param just_one_packet: 置为True，对于某个红包活动用户只能获得一个红包，不能获得多个
    :param check_issue_time：检查发放时间，超期不发放
    :return:
    """
    device_type = _decide_device(device_type)
    # 后台设置必须保证红包的event不重名
    if not isinstance(event, RedPackEvent):
        try:
            event = RedPackEvent.objects.get(name=event)
        except:
            return False, u"活动名称错误", 0
    #检查红包发放时间
    now = timezone.now()
    if now < event.give_start_at or now > event.give_end_at:
        return False, u'活动已过期', 0
    redpack = RedPack.objects.filter(event=event, status="unused").first()
    if not redpack:
        return False, u"没有此优惠券", 0
    if redpack.token != "":
        redpack.status = "used"
        redpack.save()
    if just_one_packet and RedPackRecord.objects.filter(redpack=redpack, user=user).exists():
        return False, u"限领一个红包", 0
    record = RedPackRecord()
    record.user = user
    record.redpack = redpack
    record.change_platform = device_type
    record.save()

    # start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
    #                                           record.created_at, event.available_at, event.unavailable_at)
    # _send_message_for_hby(user, event, end_time)

    return True, "", record


#为二月红包宴年前专用接口，节后会调整
def _send_message_for_hby(user, event, end_time):
    fmt_str = "%Y年%m月%d日"
    if end_time:
        unavailable_at = end_time
    else:
        unavailable_at = event.unavailable_at
    give_time = timezone.localtime(unavailable_at).strftime(fmt_str)
    mtype = 'activity'
    rtype = u'元红包'
    coupon_amount = event.amount
    if event.rtype == 'interest_coupon':
        rtype = u'%加息券'
    if event.rtype == 'percent':
        coupon_amount = event.highest_amount

    # 发送短信,功能推送id: 4
    # 模板中的参数变量必须以 name=value 的形式传入
    # phone = user.wanglibaouserprofile.phone
    # PHPSendSMS().send_sms_one(4, phone, 'phone', amount=coupon_amount, rtype=rtype)

    # send_messages.apply_async(kwargs={
    #     'phones': [user.wanglibaouserprofile.phone],
    #     'messages': [messages.red_packet_get_alert(coupon_amount, rtype)],
    #     'ext': 666,  # 营销类短信发送必须增加ext参数,值为666
    # })
    if event.rtype == 'percent':
        title, content = messages.msg_redpack_give_percent(event.amount, event.highest_amount, event.name, give_time)
    elif event.rtype == 'interest_coupon':
        title, content = messages.msg_give_coupon(event.name, event.amount, give_time)
        mtype = 'coupon'
    else:
        title, content = messages.msg_redpack_give(event.amount, event.name, give_time)
    inside_message.send_one.apply_async(kwargs={
        "user_id": user.id,
        "title": title,
        "content": content,
        "mtype": mtype
    })
