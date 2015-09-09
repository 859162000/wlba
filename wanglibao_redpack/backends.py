#!/usr/bin/env python
# encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import pytz
import time
import datetime
import json
import logging
import decimal
from django.utils import timezone
from django.db.models import Sum
from wanglibao_redpack.models import RedPack, RedPackRecord, RedPackEvent, InterestHike, Income
from wanglibao_p2p.models import P2PRecord, P2PProduct, P2PEquity
from marketing import helper
from wanglibao_sms import messages
from wanglibao_sms.tasks import send_messages
from wanglibao_account import message as inside_message
from wanglibao_pay.util import fmt_two_amount
from misc.models import Misc
from wanglibao_margin.marginkeeper import MarginKeeper
from marketing.models import IntroducedBy
import json

logger = logging.getLogger(__name__)

REDPACK_RULE = {"direct": "-", "fullcut": "-", "percent": "*", "interest_coupon": "~"}


def local_datetime(dt):
    return timezone.get_current_timezone().normalize(dt)


def stamp(dt):
    return long(time.mktime(local_datetime(dt).timetuple()))
    #return long(time.mktime(dt.timetuple()))


def list_redpack(user, status, device_type, product_id=0, rtype='redpack', app_version=''):
    if status not in ("all", "available"):
        return {"ret_code": 30151, "message": u"参数错误"}

    if not user.is_authenticated():
        packages = {"available": []}
        return {"ret_code": 0, "packages": packages}

    device_type = _decide_device(device_type)
    if status == "available":
        packages = {"available": []}

        records_count = RedPackRecord.objects.filter(user=user, product_id=product_id) \
            .filter(redpack__event__rtype='interest_coupon').count()

        if records_count == 0:
            # 红包
            records = RedPackRecord.objects.filter(user=user, order_id=None, product_id=None)\
                .exclude(redpack__event__rtype='interest_coupon')
            for x in records:
                if x.order_id:
                    continue
                redpack = x.redpack
                if redpack.status == "invalid":
                    continue
                event = x.redpack.event

                start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
                                                          x.created_at, event.available_at, event.unavailable_at)

                obj = {"name": event.name, "method": REDPACK_RULE[event.rtype], "amount": event.amount,
                        "id": x.id, "invest_amount": event.invest_amount,
                        "unavailable_at": stamp(end_time), "event_id": event.id,
                        "highest_amount": event.highest_amount, "order_by": 2}
                if start_time < timezone.now() < end_time:
                    if event.apply_platform == "all" or event.apply_platform == device_type:
                        if obj['method'] == REDPACK_RULE['percent']:
                            obj['amount'] = obj['amount']/100.0
                        packages['available'].append(obj)

        # 加息券
        # 检测app版本号，小于2.5.2版本不返回加息券列表
        is_show = True
        if device_type == 'ios' or device_type == 'android':
            if app_version < "2.5.3":
                is_show = False
        if is_show:
            if product_id > 0:
                records_count = RedPackRecord.objects.filter(user=user, product_id=product_id).count()
                if records_count == 0:
                    coupons = RedPackRecord.objects.filter(user=user, order_id=None, product_id=None)\
                        .filter(redpack__event__rtype='interest_coupon')
                    for coupon in coupons:
                        if coupon.order_id:
                            continue
                        redpack = coupon.redpack
                        if redpack.status == 'invalid':
                            continue
                        event = coupon.redpack.event
                        start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
                                                                  coupon.created_at, event.available_at, event.unavailable_at)

                        obj = {"name": event.name, "method": REDPACK_RULE[event.rtype], "amount": event.amount,
                               "id": coupon.id, "invest_amount": event.invest_amount,
                               "unavailable_at": stamp(end_time), "event_id": event.id,
                               "highest_amount": event.highest_amount, "order_by": 1}
                        if start_time < timezone.now() < end_time:
                            if event.apply_platform == "all" or event.apply_platform == device_type:
                                if obj['method'] == REDPACK_RULE['interest_coupon']:
                                    obj['amount'] = obj['amount']/100.0
                                packages['available'].append(obj)

        packages['available'].sort(key=lambda x: x['unavailable_at'])
        packages['available'].sort(key=lambda x: x['order_by'])
    else:
        packages = {"used": [], "unused": [], "expires": [], "invalid": []}
        if rtype == 'redpack':
            records = RedPackRecord.objects.filter(user=user).exclude(redpack__event__rtype='interest_coupon')
        elif rtype == 'coupon':
            records = RedPackRecord.objects.filter(user=user).filter(redpack__event__rtype='interest_coupon')
        else:
            records = RedPackRecord.objects.filter(user=user)

        for x in records:
            event = x.redpack.event
            if event.rtype == 'interest_coupon':
                order_by = 1
            else:
                order_by = 2
            start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
                                                      x.created_at, event.available_at, event.unavailable_at)

            obj = {"name": event.name, "receive_at": stamp(x.created_at),
                    "available_at": stamp(start_time), "unavailable_at": stamp(end_time),
                    "id": x.id, "invest_amount": event.invest_amount, "amount": event.amount, "event_id": event.id,
                    "highest_amount": event.highest_amount,
                    "method": REDPACK_RULE[event.rtype], "order_by": order_by}
            if obj['method'] == REDPACK_RULE['percent'] or obj['method'] == REDPACK_RULE['interest_coupon']:
                obj['amount'] = obj['amount']/100.0

            if x.order_id:
                pr = P2PRecord.objects.filter(order_id=x.order_id).first()
                obj.update({"product":pr.product.name, "apply_at":stamp(x.apply_at),
                            "apply_platform":x.apply_platform})
                packages['used'].append(obj)
                packages['used'].sort(key=lambda x: x['unavailable_at'])
                packages['used'].sort(key=lambda x: x['order_by'])
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
    if event.give_platform != "all" and event.give_platform != device_type:
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

    _send_message(user, event)
    return {"ret_code": 0, "message": u"兑换成功"}


def _send_message(user, event):
    fmt_str = "%Y年%m月%d日"
    give_time = timezone.localtime(event.unavailable_at).strftime(fmt_str)
    mtype = 'activity'
    if event.rtype == 'percent':
        pass
        #send_messages.apply_async(kwargs={
        #    'phones': [user.wanglibaouserprofile.phone],
        #    'messages': [messages.redpack_give_percent(event.amount, event.highest_amount, event.name, give_time)]
        #})
    else:
        pass
        #send_messages.apply_async(kwargs={
        #    'phones': [user.wanglibaouserprofile.phone],
        #    'messages': [messages.redpack_give(event.amount, event.name, give_time)]
        #})
    if event.rtype == 'percent':
        title, content = messages.msg_redpack_give_percent(event.amount, event.highest_amount, event.name, give_time)
    elif event.rtype == 'interest_coupon':
        # TODO 此处需要根据获得加息券的时间来处理到期时间，可能需要新增加参数来获得加息券的发送时间
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
                _send_message(user, event)


#发放奖励类型的红包
def give_activity_redpack(user, event, device_type):
    device_type = _decide_device(device_type)
    redpack = RedPack.objects.filter(event=event, status="unused").first()
    if not redpack:
        return False, u"没有此优惠券"
    if redpack.token != "":
        redpack.status = "used"
        redpack.save()
    record = RedPackRecord()
    record.user = user
    record.redpack = redpack
    record.change_platform = device_type
    record.save()
    _send_message(user, event)
    return True,""


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
    if event.apply_platform != "all" and event.apply_platform != device_type:
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


# def increase_hike(user, product_id):
#     if not user or not product_id:
#         return
#     product = P2PProduct.objects.filter(id=product_id).first()
#     if not product:
#         return
#     pr = P2PRecord.objects.filter(user=user, product=product).first()
#     if not pr:
#         return
#     if (timezone.now() - pr.create_time).days > 10:
#         return
#     #InterestHike.objects.select_for_update().filter(user=user, product=product, invalid=False).first()
#     record = InterestHike.objects.filter(user=user, product=product, invalid=False).first()
#     if not record:
#         record = InterestHike()
#         record.user = user
#         record.product = product
#         record.rate = decimal.Decimal("0.001")
#     record.intro_total += 1
#     record.save()
#     return {"ret_code":0, "message":"ok"}
#
# def settle_hike(product):
#     if not product:
#         return None
#     if product.pay_method.startswith(u"日计息"):
#         term = decimal.Decimal(product.period) / decimal.Decimal(360)
#     else:
#         term = decimal.Decimal(product.period) / decimal.Decimal(12)
#
#     hike_list = []
#     #records = InterestHike.objects.filter(product=product, invalid=False, paid=False).first()
#     records = InterestHike.objects.filter(product=product, invalid=False, paid=False)
#     for x in records:
#         equity = P2PEquity.objects.filter(user=x.user, product=product).first()
#         if equity:
#             intro_total = x.intro_total
#             if x.intro_total > 20:
#                 intro_total = 20
#             amount = equity.equity * term * x.rate * intro_total
#             amount = amount.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_DOWN)
#             x.amount = amount
#             x.paid = True
#             x.updated_at = timezone.now()
#             x.save()
#             hike_list.append({"user":x.user, "amount":amount})
#     return hike_list


def get_interest_coupon(user, product_id):
    records = RedPackRecord.objects.filter(user=user, product_id=product_id) \
        .filter(redpack__event__rtype='interest_coupon').first()
    if records:
        amount = records.redpack.event.amount
        return {"ret_code": 0, "amount": amount}
    else:
        return {"ret_code": 3002, "message": u"还未使用加息券"}


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
    record = Income.objects.filter(product=product).first()
    return record


def commission(user, product, equity, start, end):
    _amount = P2PRecord.objects.filter(user=user, product=product, create_time__gt=start,
                                       create_time__lt=end).aggregate(Sum('amount'))
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

            sec_intro = IntroducedBy.objects.filter(user=first_intro.introduced_by).first()
            if sec_intro and sec_intro.introduced_by:
                second = MarginKeeper(sec_intro.introduced_by)
                second.deposit(commission, catalog=u"全民淘金")

                income = Income(user=sec_intro.introduced_by, invite=user, level=2,
                                product=product, amount=_amount['amount__sum'],
                                earning=commission, order_id=second.order_id, paid=True, created_at=timezone.now())
                income.save()


def get_start_end_time(auto, auto_days, created_at, available_at, unavailable_at):
    if auto and auto_days > 0:
        start_time = created_at
        end_time = created_at + timezone.timedelta(days=int(auto_days))
    else:
        start_time = available_at
        end_time = unavailable_at
    return start_time, end_time


def get_app_version():
    misc = Misc.objects.filter(key='android_update').first()