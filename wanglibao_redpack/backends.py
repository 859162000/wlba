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
from marketing import  helper
from wanglibao_sms import messages
from wanglibao_sms.tasks import send_messages
from wanglibao_account import message as inside_message
from wanglibao_pay.util import fmt_two_amount
from misc.models import Misc
from wanglibao_margin.marginkeeper import MarginKeeper
from marketing.models import IntroducedBy

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
                    "unavailable_at":stamp(event.unavailable_at), "event_id":event.id,
                    "highest_amount":event.highest_amount}
            if event.available_at < timezone.now() < event.unavailable_at:
                if event.apply_platform == "all" or event.apply_platform == device_type:
                    if obj['method'] == REDPACK_RULE['percent']:
                        #obj['amount'] = "%.2f" % (obj['amount']/100.0)
                        obj['amount'] = obj['amount']/100.0
                    packages['available'].append(obj)
        packages['available'].sort(key=lambda x:x['unavailable_at'])
    else:
        packages = {"used":[], "unused":[], "expires":[], "invalid":[]}
        records = RedPackRecord.objects.filter(user=user)
        for x in records:
            event = x.redpack.event
            obj = {"name":event.name, "receive_at":stamp(x.created_at),
                    "available_at":stamp(event.available_at), "unavailable_at":stamp(event.unavailable_at),
                    "id":x.id, "invest_amount":event.invest_amount, "amount":event.amount, "event_id":event.id,
                    "highest_amount":event.highest_amount,
                    "method":REDPACK_RULE[event.rtype]}
            if obj['method'] == REDPACK_RULE['percent']:
                obj['amount'] = obj['amount']/100.0

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

def utc_transform(dt):
    tp = dt.timetuple()
    stamp = time.mktime(tp)
    dt = datetime.datetime.fromtimestamp(stamp,pytz.utc)
    return dt.replace(tzinfo=None)

def local_transform_str(dt):
    dt = dt.replace(tzinfo=pytz.utc)
    newdt = dt.astimezone(pytz.timezone("Asia/Shanghai"))
    return newdt.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")

def exchange_redpack(token, device_type, user):
    if token == "":
        return {"ret_code":30161, "message":"请输入兑换码"}
    token = token.replace("'","").replace('"',"").replace("`","")
    #redpack = RedPack.objects.filter(token=token).first()
    redpack = RedPack.objects.extra(where=["binary token='%s'" % token]).first()
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

    if event.amount == 0:
        #金额为0,为特殊红包
        xle = Misc.objects.filter(key=event.describe).first()
        if xle:
            try:
                obj = json.loads(xle.value)
                if "event_id" not in obj or "event_new_id" not in obj or "event_old_id" not in obj:
                    return {"ret_code":301691, "message":"服务器内部错误"}
                if int(obj['event_id']) != event.id:
                    return {"ret_code":301694, "message":"活动错误"}

                register_time = timezone.datetime(2015, 3, 13)
                register_time = utc_transform(register_time).replace(tzinfo=pytz.utc)
                if user.date_joined > register_time:
                    record = RedPackRecord.objects.filter(user=user, redpack__event=obj['event_new_id']).first()
                    if record:
                        return {"ret_code":301695, "message":"您已参与过此活动"}

                    event_on = RedPackEvent.objects.filter(id=obj['event_new_id'], invalid=False, value=0).first()
                else:
                    record = RedPackRecord.objects.filter(user=user, redpack__event=obj['event_old_id']).first()
                    if record:
                        return {"ret_code":301695, "message":"您已参与过此活动"}
                    event_on = RedPackEvent.objects.filter(id=obj['event_old_id'], invalid=False, value=0).first()
                
                if not event_on:
                    return {"ret_code":301692, "message":"没有此活动"}
                redpack_on = RedPack.objects.filter(event=event_on, token="").first()
                if not redpack_on:
                    return {"ret_code":301693, "message":"兑换码无效"}
                redpack.status = "used"
                redpack.save()

                record = RedPackRecord()
                record.user = user
                record.redpack = redpack_on
                record.change_platform = device_type
                record.save()
                #修改event
                event = event_on
            except Exception,e:
                logger.info(u"%s" % e)
                return {"ret_code":30169, "message":"服务器内部错误"}
        else:
            return {"ret_code":301641, "message":"请输入有效的兑换码"}

    else:
        record = RedPackRecord()
        record.user = user
        record.redpack = redpack
        record.change_platform = device_type
        redpack.status = "used"
        redpack.save()
        record.save()

    _send_message(user, event)
    return {"ret_code":0, "message":"兑换成功"}

def _send_message(user, event):
    fmt_str = "%Y年%m月%d日"
    give_time = timezone.localtime(event.unavailable_at).strftime(fmt_str)
    if event.rtype == 'percent':
        send_messages.apply_async(kwargs={
            'phones': [user.wanglibaouserprofile.phone],
            'messages': [messages.redpack_give_percent(event.amount, event.highest_amount, event.name, give_time)]
        })
    else:
        send_messages.apply_async(kwargs={
            'phones': [user.wanglibaouserprofile.phone],
            'messages': [messages.redpack_give(event.amount, event.name, give_time)]
        })
    if event.rtype == 'percent':
        title, content = messages.msg_redpack_give_percent(event.amount, event.highest_amount, event.name, give_time)
    else:
        title, content = messages.msg_redpack_give(event.amount, event.name, give_time)
    inside_message.send_one.apply_async(kwargs={
        "user_id": user.id,
        "title": title,
        "content": content,
        "mtype": "activity"
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


def give_activity_redpack_new(user, rtype, redpack_id, device_type, rule_id):
    _give_activity_redpack_new(user, rtype, redpack_id, device_type, rule_id)


def give_buy_redpack(user, device_type, rtype='buy', describe=''):
    now = timezone.now()
    rps = RedPackEvent.objects.filter(give_mode=rtype, invalid=False, give_start_at__lt=now, give_end_at__gt=now)
    if describe:
        rps = rps.filter(describe=describe)
    for x in rps:
        give_activity_redpack(user=user, event=x, device_type=device_type)


def _give_activity_redpack_new(user, rtype, redpack_id, device_type, rule):
    """ rule_id: get message template """
    now = timezone.now()
    user_channel = helper.which_channel(user)
    device_type = _decide_device(device_type)
    rps = RedPackEvent.objects.filter(give_mode=rtype, invalid=False, id=redpack_id, \
                                      give_start_at__lt=now, give_end_at__gt=now).first()
    if rps:
        if rps.target_channel != "" and rule.activity.is_all_channel is False:
            chs = rps.target_channel.split(",")
            chs = [m for m in chs if m.strip() != ""]
            if user_channel not in chs:
                return
        redpack = RedPack.objects.filter(event=rps, status="unused").first()
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


def _give_redpack(user, rtype, device_type):
    now = timezone.now()
    user_ch = helper.which_channel(user)
    device_type = _decide_device(device_type)
    rps = RedPackEvent.objects.filter(give_mode=rtype, invalid=False, give_start_at__lt=now, give_end_at__gt=now)
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
        return False,u"没有此红包"
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


def consume(redpack, amount, user, order_id, device_type):
    amount = fmt_two_amount(amount)
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

    rtype = event.rtype
    rule_value = event.amount
    deduct = _calc_deduct(amount, rtype, rule_value, event)

    record.order_id = order_id
    record.apply_platform = device_type
    record.apply_amount = deduct
    record.apply_at = timezone.now()
    record.save()

   # if REDPACK_RULE[rtype] == "*":
   #     #return {"ret_code":30176, "message":"目前不支付百分比红包"}
   #     rule_value = rule_value/100.0
   #     deduct = fmt_two_amount(amount * rule_value)
   #     actual_amount = amount + deduct
   # elif REDPACK_RULE[rtype] == "-":
   #     if event.id == 7:
   #         t5 = amount * 0.005
   #         if t5 >= rule_value:
   #             deduct = rule_value
   #         else:
   #             deduct = t5
   #         deduct = fmt_two_amount(deduct)
   #     else:
   #         if amount <= rule_value:
   #             actual_amount = amount
   #             deduct = amount
   #         else:
   #             actual_amount = amount - rule_value
   # elif REDPACK_RULE[rtype] == "+":
   #     actual_amount = amount + rule_value

    return {"ret_code":0, "message":"ok", "deduct":deduct}

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
    real_deduct = deduct.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_DOWN)
    return real_deduct

def restore(order_id, amount, user):
    if type(amount) != decimal.Decimal:
        amount = fmt_two_amount(amount)
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
    deduct = _calc_deduct(amount, rtype, rule_value, event)
   # if REDPACK_RULE[rtype] == "*":
   #     #return {"ret_code":30176, "message":"目前不支持百分比红包"}

   #     #rule_value = float("%.2f" % (rule_value/100.0))
   #     #actual_amount = amount + amount * rule_value
   #     #deduct = round(amount * rule_value)
   #     rule_value = rule_value/100.0
   #     deduct = fmt_two_amount(amount * rule_value)
   #     actual_amount = amount + deduct
   # elif REDPACK_RULE[rtype] == "-":
   #     if event.id == 7:
   #         t5 = amount * 0.005
   #         if t5 >= rule_value:
   #             deduct = rule_value
   #         else:
   #             deduct = t5
   #         deduct = fmt_two_amount(deduct)
   #     else:
   #         if amount <= rule_value:
   #             actual_amount = amount
   #             deduct = amount
   #         else:
   #             actual_amount = amount - rule_value
   # elif REDPACK_RULE[rtype] == "+":
   #     actual_amount = amount + rule_value
    logger.info(u"%s--%s 退回账户 %s" % (event.name, record.id, timezone.now()))
    return {"ret_code":0, "deduct":deduct}

def deduct_calc(amount, redpack_amount):
    if not amount or not redpack_amount:
        return {"ret_code":30181, "message":"金额错误"}
    try:
        float(amount)
        float(redpack_amount)
    except:
        return {"ret_code":30182, "message":"金额格式不正确"}

    t5 = fmt_two_amount(amount) * decimal.Decimal('0.005')
    redpack_amount = fmt_two_amount(redpack_amount)
    real_deduct = fmt_two_amount(0)
    if t5 >= redpack_amount:
        real_deduct = redpack_amount
    else:
        real_deduct = t5
    real_deduct = real_deduct.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_DOWN)
    return {"ret_code":0, "deduct":real_deduct}


def increase_hike(user, product_id):
    if not user or not product_id:
        return
    product = P2PProduct.objects.filter(id=product_id).first()
    if not product:
        return
    pr = P2PRecord.objects.filter(user=user, product=product).first()
    if not pr:
        return
    if (timezone.now() - pr.create_time).days > 10:
        return
    #InterestHike.objects.select_for_update().filter(user=user, product=product, invalid=False).first()
    record = InterestHike.objects.filter(user=user, product=product, invalid=False).first()
    if not record:
        record = InterestHike()
        record.user = user
        record.product = product
        record.rate = decimal.Decimal("0.001")
    record.intro_total += 1
    record.save()
    return {"ret_code":0, "message":"ok"}

def settle_hike(product):
    if not product:
        return None
    if product.pay_method.startswith(u"日计息"):
        term = decimal.Decimal(product.period) / decimal.Decimal(360)
    else:
        term = decimal.Decimal(product.period) / decimal.Decimal(12)

    hike_list = []
    #records = InterestHike.objects.filter(product=product, invalid=False, paid=False).first()
    records = InterestHike.objects.filter(product=product, invalid=False, paid=False)
    for x in records:
        equity = P2PEquity.objects.filter(user=x.user, product=product).first()
        if equity:
            intro_total = x.intro_total
            if x.intro_total > 20:
                intro_total = 20
            amount = equity.equity * term * x.rate * intro_total
            amount = amount.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_DOWN)
            x.amount = amount
            x.paid = True
            x.updated_at = timezone.now()
            x.save()
            hike_list.append({"user":x.user, "amount":amount})
    return hike_list

def get_hike(user, product_id):
    _hike = InterestHike.objects.filter(user=user, product=product_id, invalid=False).first()
    if _hike:
        if _hike.paid:
            hike = _hike.amount
        else:
            if _hike.intro_total > 20:
                hike = "%.2f%%" % (_hike.rate * 20 * 100) 
            else:
                hike = "%.2f%%" % (_hike.rate * _hike.intro_total * 100) 
    else:
        hike = ""
    return hike

#获取加息次数
def get_hike_nums(user):
    _nums = InterestHike.objects.filter(user=user, invalid=False).aggregate(Sum('intro_total'))
    if _nums['intro_total__sum']:
        nums = _nums['intro_total__sum']
    else:
        nums = 0
    return nums

#获取加息总额
def get_hike_amount(user):
    _amount = InterestHike.objects.filter(user=user, invalid=False, paid=True).aggregate(Sum('amount'))
    if not _amount['amount__sum']:
        amount = 0
    else:
        amount = _amount['amount__sum']
    return amount

def commission(user, product, equity, start):
    _amount = P2PRecord.objects.filter(user=user, product=product, create_time__gt=start).aggregate(Sum('amount'))
    if _amount['amount__sum'] and _amount['amount__sum'] <= equity:
        commission = decimal.Decimal(_amount['amount__sum']) * decimal.Decimal("0.003")
        commission = commission.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_DOWN)
        first_intro = IntroducedBy.objects.filter(user=user).first()
        if first_intro:
            first = MarginKeeper(first_intro.introduced_by)
            first.deposit(commission, catalog=u"全民淘金")

            income = Income(user=first_intro.introduced_by, invite=user, level=1,
                            product=product, amount=_amount['amount__sum'],
                            earning=commission, order_id=first.order_id, paid=True, created_at=timezone.now())
            income.save()
        sec_intro = IntroducedBy.objects.filter(user=first_intro.user).first()
        if sec_intro:
            second = MarginKeeper(first_intro.introduced_by)
            second.deposit(commission, catalog=u"全民淘金")

            income = Income(user=sec_intro.introduced_by, invite=user, level=2,
                            product=product, amount=_amount['amount__sum'],
                            earning=commission, order_id=second.order_id, paid=True, created_at=timezone.now())
            income.save()
