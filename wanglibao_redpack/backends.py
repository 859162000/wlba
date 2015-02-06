#!/usr/bin/env python
# encoding:utf-8


import time
import logging
from django.utils import timezone
from wanglibao_redpack.models import RedPack, RedPackRecord, RedPackEvent
from wanglibao_p2p.models import P2PRecord
from marketing import  helper

logger = logging.getLogger(__name__)

REDPACK_RULE = {"direct":"-", "fullcut":"-", "percent":"*"}

def local_datetime(dt):
    return timezone.get_current_timezone().normalize(dt)

def stamp(dt):
    return long(time.mktime(local_datetime(dt).timetuple()))
    #return long(time.mktime(dt.timetuple()))

def list_redpack(user, status, device_type):
    if status not in ("all", "available"):
        return {"ret_code":30151, "message":"参数错误"}

    if not user.is_authenticated():
        packages = {"available":[]}
        return {"ret_code":0, "packages":packages}

    device_type = _decide_device(device_type)
    if status == "available":
        packages = {"available":[]}
        records = RedPackRecord.objects.filter(user=user, order_id=None)
        for x in records:
            if x.order_id:
                continue
            redpack = x.redpack
            if redpack.status == "invalid":
                continue
            event = x.redpack.event
            obj = {"name":event.name, "method":REDPACK_RULE[event.rtype], "amount":event.amount,
                    "id":x.id, "invest_amount":event.invest_amount,
                    "unavailable_at":stamp(event.unavailable_at)}
            if event.available_at < timezone.now() < event.unavailable_at:
                if event.apply_platform == "all" or event.apply_platform == device_type:
                    if obj['method'] == REDPACK_RULE['percent']:
                        obj['amount'] = "%.2f" % (obj['amount']/100.0)
                    packages['available'].append(obj)
        packages['available'].sort(key=lambda x:x['unavailable_at'])
    else:
        packages = {"used":[], "unused":[], "expires":[], "invalid":[]}
        records = RedPackRecord.objects.filter(user=user)
        for x in records:
            event = x.redpack.event
            obj = {"name":event.name, "receive_at":stamp(x.created_at),
                    "available_at":stamp(event.available_at), "unavailable_at":stamp(event.unavailable_at),
                    "id":x.id, "invest_amount":event.invest_amount, "amount":event.amount}
            if x.order_id:
                pr = P2PRecord.objects.filter(order_id=x.order_id).first()
                obj.update({"product":pr.product.name, "apply_at":stamp(x.apply_at),
                            "apply_platform":x.apply_platform})
                packages['used'].append(obj)
            else:
                if x.redpack.status == "invalid":
                    packages['invalid'].append(obj)
                else:
                    if event.unavailable_at < timezone.now():
                        packages['expires'].append(obj)
                    else:
                        packages['unused'].append(obj)
    return {"ret_code":0, "packages":packages}

def exchange_redpack(token, device_type, user):
    if token == "":
        return {"ret_code":30161, "message":"请输入兑换码"}
    redpack = RedPack.objects.filter(token=token).first()
    device_type = _decide_device(device_type)
    if not redpack:
        return {"ret_code":30162, "message":"请输入正确的兑换码"}
    if redpack.status == "used":
        return {"ret_code":30163, "message":"兑换码已被兑换"}
    elif redpack.status == "invalid":
        return {"ret_code":30164, "message":"请输入有效的兑换码"}
    event = redpack.event
    now = timezone.now()
    if event.give_start_at > now:
        return {"ret_code":30165, "message":"请在%s之后兑换" % local_datetime(event.give_start_at).strftime("%Y-%m-%d %H:%M:%S")}
    elif event.give_end_at < now:
        return {"ret_code":30166, "message":"兑换码已过期"}
    if event.target_channel != "":
        ch = helper.which_channel(user)
        if ch != event.target_channel:
            return {"ret_code":30167, "message":"不符合领取条件"}
    if event.give_platform != "all" and event.give_platform != device_type:
        return {"ret_code":30168, "message":"不符合领取条件"}

    record = RedPackRecord()
    record.user = user
    record.redpack = redpack
    record.change_platform = device_type
    redpack.status = "used"
    redpack.save()
    record.save()
    return {"ret_code":0, "message":"兑换成功"}

def _decide_device(device_type):
    device_type = device_type.lower()
    if device_type == "ios":
        return "ios"
    elif device_type == "android":
        return "android"
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

def _give_redpack(user, rtype, device_type):
    now = timezone.now()
    user_ch = helper.which_channel(user)
    device_type = _decide_device(device_type)
    rps = RedPackEvent.objects.filter(give_mode=rtype, invalid=False, give_start_at__lt=now, give_end_at__gt=now)
    for x in rps:
        if x.target_channel != "" and user_ch != x.target_channel:
            continue
        redpack = RedPack.objects.filter(event=x, status="unused").first()
        if redpack:
            give_pf = redpack.event.give_platform
            if give_pf == "all" or give_pf == device_type:
                if redpack.token != "":
                    redpack.status = "used"
                    redpack.save()
                record = RedPackRecord()
                record.user = user
                record.redpack = redpack
                record.change_platform = device_type
                record.save()


def consume(redpack, amount, user, order_id, device_type):
    record = RedPackRecord.objects.filter(user=user, id=redpack).first()
    redpack = record.redpack
    event = redpack.event
    device_type = _decide_device(device_type)
    if not record:
        return {"ret_code":30171, "message":"红包不存在"}
    if record.order_id:
        return {"ret_code":30172, "message":"红包已使用"}
    if redpack.status == "invalid":
        return {"ret_code":30173, "message":"红包已作废"}
    if not event.available_at < timezone.now() < event.unavailable_at:
        return {"ret_code":30174, "message":"红包不可使用"}
    if amount < event.invest_amount:
        return {"ret_code":30175, "message":"投资金额不满足红包规则%s" % event.invest_amount}
    if event.apply_platform != "all" and event.apply_platform != device_type:
        return {"ret_code":30176, "message":"此红包只能在%s平台使用" % event.apply_platform}

    record.order_id = order_id
    record.apply_platform = device_type
    record.apply_at = timezone.now()
    record.save()

    rtype = event.rtype
    rule_value = event.amount
    deduct = event.amount
    if REDPACK_RULE[rtype] == "*":
        return {"ret_code":30176, "message":"目前不支付百分比红包"}

        rule_value = float("%.2f" % (rule_value/100.0))
        actual_amount = amount + amount * rule_value
        deduct = round(amount * rule_value)
    elif REDPACK_RULE[rtype] == "-":
        if amount <= rule_value:
            actual_amount = amount
            deduct = amount
        else:
            actual_amount = amount - rule_value
    elif REDPACK_RULE[rtype] == "+":
        actual_amount = amount + rule_value

    return {"ret_code":0, "message":"ok", "actual_amount":actual_amount, "deduct":deduct}

def _calc_deduct():
    pass

def restore(order_id, amount, user):
    record = RedPackRecord.objects.filter(user=user, order_id=order_id).first()
    if not record:
        return {"ret_code":-1, "message":"redpack not exists"}
    record.apply_platform = ""
    record.apply_at = None
    record.order_id = None
    record.save()

    event = record.redpack.event
    rtype = event.rtype
    rule_value = event.amount
    deduct = event.amount
    if REDPACK_RULE[rtype] == "*":
        return {"ret_code":30176, "message":"目前不支付百分比红包"}

        rule_value = float("%.2f" % (rule_value/100.0))
        actual_amount = amount + amount * rule_value
        deduct = round(amount * rule_value)
    elif REDPACK_RULE[rtype] == "-":
        if amount <= rule_value:
            actual_amount = amount
            deduct = amount
        else:
            actual_amount = amount - rule_value
    elif REDPACK_RULE[rtype] == "+":
        actual_amount = amount + rule_value
    logger.info(u"%s--%s 退回账户 %s" % (event.name, record.id, timezone.now()))
    return {"ret_code":0, "deduct":deduct}
