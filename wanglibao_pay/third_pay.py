#!/usr/bin/env python
# encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import logging
from django.forms import model_to_dict
from django.db import transaction
from django.db.models import Q
from django.utils.decorators import method_decorator
from wanglibao_pay import util
from wanglibao_pay.models import PayInfo, Bank, Card
from order.utils import OrderHelper
from order.models import Order
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_sms.utils import validate_validation_code
from marketing import tools

from wanglibao_rest.utils import split_ua

from wanglibao_pay.kuai_pay import KuaiPay, KuaiShortPay
from wanglibao_pay.huifu_pay import HuifuShortPay
from wanglibao_pay.yee_pay import YeePay, YeeShortPay

logger = logging.getLogger(__name__)




def add_bank_card(request):
    card_no = request.DATA.get("card_number", "")
    gate_id = request.DATA.get("gate_id", "")

    if not card_no or not gate_id:
        return {"ret_code":20021, "message":"信息输入不完整"}

    if len(card_no) > 25 or not card_no.isdigit():
        return {"ret_code":20022, "message":"请输入正确的银行卡号"}
    #if card_no[0] in ("3", "4", "5"):
    #    return {"ret_code":20023, "message":"不支持信用卡"}

    user = request.user
    bank = Bank.objects.filter(gate_id=gate_id).first()
    if not bank:
        return {"ret_code":20025, "message":"不支持该银行"}

    exist_cards = Card.objects.filter(no=card_no, user=user).first()
    if exist_cards:
        return {"ret_code":20024, "message":"该银行卡已经存在"}
    exist_cards = Card.objects.filter(user=user, no__startswith=card_no[:6], no__endswith=card_no[-4:]).first()
    if exist_cards:
        return {"ret_code":20026, "message":"该银行卡已经存在"}

    is_default = request.DATA.get("is_default", "false")
    if is_default.lower() in ("true", "1"):
        is_default = True
    else:
        is_default = False
    card = Card()
    card.bank = bank
    card.no = card_no
    card.user = user
    card.is_default = is_default
    card.save()

    return {"ret_code":0, "message":"ok", "card_id":card.id}

def list_bank_card(request):
    try:
       cards =  Card.objects.filter(user=request.user)
    except Exception,e:
        return {"ret_code":20031, "message":"请添加银行卡"}
    rs = []
    for x in cards:
        rs.append({"bank_name":x.bank.name, "card_no":x.no, "card_id":x.id, "default":x.is_default})
    if not rs:
        return {"ret_code":20031, "message":"请添加银行卡"}
    return {"ret_code":0, "message":"ok", "cards":rs}

def del_bank_card(request):
    card_id = request.DATA.get("card_id", "")
    if not card_id or not card_id.isdigit():
        return {"ret_code":20041, "message":"请输入正确的ID"}

    card = Card.objects.filter(id=card_id, user=request.user).first()
    if not card:
        return {"ret_code":20042, "message":"该银行卡不存在"}
    # 删除快捷支付信息
    storable_no = card.no[:6] + card.no[-4:]
    pay = KuaiPay()
    dic = {"user_id":request.user.id, "bank_id":card.bank.kuai_code,
            "storable_no":storable_no}

    data = pay._sp_delbind_xml(dic)
    res = pay._request(data, pay.DEL_URL)
    logger.error("#api delete card")
    logger.error(res.content)

    card.delete()
    return {"ret_code":0, "message":"删除成功"}

def del_bank_card_new(request):
    """ 删除银行卡，需要解绑所有已绑定渠道"""
    card_id = request.DATA.get("card_id", "")
    if not card_id or not card_id.isdigit():
        return {"ret_code": 20041, "message": "请输入正确的ID"}

    card = Card.objects.filter(id=card_id, user=request.user).first()
    if not card:
        return {"ret_code": 20042, "message": "该银行卡不存在"}

    # 删除快捷支付信息
    res = _unbind_common(request, card, card.bank)
    if res['ret_code'] != 0: return res

    card.delete()
    return {"ret_code": 0, "message": "删除成功"}

def list_bank(request):
    #banks = Bank.get_deposit_banks()
    banks = Bank.get_kuai_deposit_banks()
    rs = []
    for x in banks:
        obj = {"name":x.name, "gate_id":x.gate_id, "bank_id":x.kuai_code}
        if x.kuai_limit:
            obj.update(util.handle_kuai_bank_limit(x.kuai_limit))
        rs.append(obj)
    if not rs:
        return {"ret_code":20051, "message":"没有可选择的银行"}
    return {"ret_code":0, "message":"ok", "banks":rs}

#def handle_kuai_bank_limit(limitstr):
#    obj = {}
#    try:
#        first, second = limitstr.split("|")
#        arr = first.split(",")
#        obj['first_one'] = arr[0].split("=")[1]
#        obj['first_day'] = arr[1].split("=")[1]
#        arr1 = second.split(",")
#        obj['second_one'] = arr1[0].split("=")[1]
#        obj['second_day'] = arr1[1].split("=")[1]
#    except:
#        pass
#    return obj

@method_decorator(transaction.atomic)
def withdraw(request):
    amount = request.DATA.get("amount", "").strip()
    card_id = request.DATA.get("card_id", "").strip()
    vcode = request.DATA.get("validate_code", "").strip()
    if not amount or not card_id :
        return {"ret_code":20061, "message":u"信息输入不完整"}

    user = request.user
    if not user.wanglibaouserprofile.id_is_valid:
        return {"ret_code":20062, "message":u"请先进行实名认证"}

    try:
        float(amount)
    except:
        return {"ret_code":20063, 'message':u'金额格式错误'}
    amount = util.fmt_two_amount(amount)
    if len(str(amount)) > 20:
        return {"ret_code":20068, 'message':'金额格式错误，大于100元且为100倍数'}
    if not 0 <= amount <= 50000:
        return {"ret_code":20064, 'message':u'提款金额在0～50000之间'}

    margin = user.margin.margin
    if amount > margin:
        return {"ret_code":20065, 'message':u'余额不足'}

    phone = user.wanglibaouserprofile.phone
    status, message = validate_validation_code(phone, vcode)
    if status != 200:
        return {"ret_code":20066, "message":u"验证码输入错误"}
    fee = amount * YeePay.FEE
    #实际提现金额
    actual_amount = amount - fee
    card = Card.objects.filter(pk=card_id).first()
    if not card or card.user != user:
        return {"ret_code":20067, "message":u"请选择有效的银行卡"}

    pay_info = PayInfo()
    pay_info.amount = actual_amount
    pay_info.fee = fee
    pay_info.total_amount = amount
    pay_info.type = PayInfo.WITHDRAW
    pay_info.user = user
    pay_info.card_no = card.no
    pay_info.account_name = user.wanglibaouserprofile.name
    pay_info.bank = card.bank
    pay_info.request_ip = util.get_client_ip(request)
    pay_info.status = PayInfo.ACCEPTED
    pay_info.channel = "app"

    try:
        order = OrderHelper.place_order(user, Order.WITHDRAW_ORDER, pay_info.status,
                                        pay_info=model_to_dict(pay_info))
        pay_info.order = order
        keeper = MarginKeeper(user, pay_info.order.pk)
        margin_record = keeper.withdraw_pre_freeze(amount)
        pay_info.margin_record = margin_record

        pay_info.save()
        return {"ret_code":0, 'message':u'提现成功', "amount":amount, "phone":phone}
    except Exception, e:
        pay_info.error_message = str(e)
        pay_info.status = PayInfo.FAIL
        pay_info.save()
        return {"ret_code":20065, 'message':u'余额不足'}


def card_bind_list(request):
    # 查询已经绑定支付渠道的银行卡列表
    try:
        card_list = []
        cards = Card.objects.filter(Q(user=request.user), Q(is_bind_huifu=True) | Q(is_bind_kuai=True) | Q(is_bind_yee=True)).select_related('bank').order_by('-last_update')
        if cards.exists():
            # 排序
            bank_list = [card.bank.gate_id for card in cards]
            cards = sorted(cards, key=lambda x: bank_list.index(x.bank.gate_id))

            for card in cards:
                tmp = {
                    'bank_id': card.bank.id,
                    'bank_name': card.bank.name,
                    'gate_id': card.bank.gate_id,
                    'storable_no': card.no[:6] + card.no[-4:]
                }

                # 将银行卡对应银行的绑定的支付通道限额信息返回
                channel = card.bank.channel
                if channel == 'huifu':
                    if card.bank.huifu_bind_limit:
                        tmp.update(util.handle_kuai_bank_limit(card.bank.huifu_bind_limit))

                elif channel == 'yeepay':
                    if card.bank.yee_bind_limit:
                        tmp.update(util.handle_kuai_bank_limit(card.bank.yee_bind_limit))

                elif channel == 'kuaipay':
                    if card.bank.kuai_limit:
                        tmp.update(util.handle_kuai_bank_limit(card.bank.kuai_limit))

                card_list.append(tmp)

        return {"ret_code": 0, "message": "ok", "cards": card_list}

    except Exception, e:
        logger.error(e.message)
        return {"ret_code": 20031, "message": "请添加银行卡"}


def _unbind_huifu(request, card, bank=None):
    return HuifuShortPay().delete_bind(request.user, card, bank)


def _unbind_kuaipay(request, card, bank=None):
    return KuaiShortPay().delete_bind_new(request.user, card, bank)


def _unbind_yeepay(request, card, bank=None):
    return YeeShortPay().delete_bind(request.user, card, bank)


def _unbind_common(request, card, bank):
    if card.is_bind_huifu:
        res = _unbind_huifu(request, card, bank)
        if res['ret_code'] != 0: return res

    if card.is_bind_yee:
        res = _unbind_yeepay(request, card, bank)
        if res['ret_code'] != 0: return res

    if card.is_bind_kuai:
        res = _unbind_kuaipay(request, card, bank)
        if res['ret_code'] != 0: return res

    return {"ret_code": 0, "message": "银行卡解绑成功"}


def card_unbind(request):
    """ 请求解绑银行卡 """
    user = request.user
    card_no = request.DATA.get("storable_no", "").strip()
    bank_id = request.DATA.get("bank_id", "").strip()

    bank = Bank.objects.filter(id=bank_id).first()
    if not bank:
        return {"ret_code": 20101, "message": "解除信息不匹配"}

    if len(card_no) < 10:
        return {"ret_code": 20102, "message": "银行卡号不正确"}

    if len(card_no) == 10:
        card = Card.objects.filter(user=user, no__startswith=card_no[:6], no__endswith=card_no[-4:]).first()
    else:
        card = Card.objects.filter(no=card_no, user=user).first()

    if not card:
        return {"ret_code": 20103, "message": "银行卡未绑定"}

    return _unbind_common(request, card, bank)


def bind_pay_deposit(request):
    """ 根据银行设置的支付渠道进行支付渠道的支付
        1、获取验证码
        2、快捷支付功能
    """
    gate_id = request.DATA.get("gate_id", "").strip()

    if not gate_id:
        return {"ret_code": 20001, 'message': '信息输入不完整'}

    bank = Bank.objects.filter(gate_id=gate_id).first()

    if not bank:
        return {"ret_code": 20002, "message": "银行ID不正确"}

    if bank.channel == 'huifu':
        return HuifuShortPay().pre_pay(request)

    elif bank.channel == 'yeepay':
        return YeeShortPay().pre_pay(request)

    elif bank.channel == 'kuaipay':
        return KuaiShortPay().pre_pay(request)

    else:
        return {"ret_code": 20004, "message": "请选择支付渠道"}


def bind_pay_dynnum(request):
    """ 根据银行设置的支付渠道进行支付渠道的支付
        1、确认支付功能
    """
    user = request.user
    card_no = request.DATA.get("card_no", "").strip()

    if not card_no:
        return {"ret_code": 20001, 'message': '信息输入不完整'}

    if len(card_no) == 10:
        card = Card.objects.filter(user=user, no__startswith=card_no[:6], no__endswith=card_no[-4:]).first()
    else:
        card = Card.objects.filter(no=card_no, user=user).first()

    if not card:
        return {"ret_code": 20002, "message": "银行卡未绑定"}

    if card.bank.channel == 'huifu':
        return {'ret_code': 20003, 'message': '汇付天下请选择快捷支付渠道'}

    elif card.bank.channel == 'yeepay':
        return YeeShortPay().dynnum_bind_pay(request)

    elif card.bank.channel == 'kuaipay':
        return KuaiShortPay().dynnum_bind_pay(request)
    else:
        return {"ret_code": 20004, "message": "请选择支付渠道"}
