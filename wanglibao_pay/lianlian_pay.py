#!/usr/bin/env python
# encoding:utf-8

import hashlib
import logging
from django.conf import settings
from django.forms import model_to_dict
from django.db import transaction
from django.utils.decorators import method_decorator
from wanglibao_pay import util, bankcard_checker
from wanglibao_pay.models import PayInfo, PayResult, Bank, Card
from order.utils import OrderHelper
from order.models import Order
from wanglibao_margin.marginkeeper import MarginKeeper

logger = logging.getLogger(__name__)



class LianlianPay:
    FEE = 0

    def __init__(self):
        self.MER_ID = settings.LIAN_MER_ID
        self.PAY_SECRET_KEY = settings.LIAN_PAY_SECRET_KEY
        self.PAY_URL = settings.LIAN_PAY_URL
        self.PAY_RETURN_URL = settings.LIAN_PAY_RETURN_URL
        self.PAY_BACK_RETURN_URL = settings.LIAN_PAY_BACK_RETURN_URL

    def _sign(self, dic):
        keys = dic.keys()
        keys.sort()
        s = []
        for x in keys:
            if dic[x] != "":
                s.append("%s=%s" % (x, dic[x]))
        s.append("key=%s" % self.PAY_SECRET_KEY)
        return hashlib.md5("&".join(s)).hexdigest()

    def ios_sign(self, params):
        dic = {"no_order":params['id'], "busi_partner":"108001",
                "sign_type":"MD5", "money_order":params['amount'],
                "notify_url":self.PAY_BACK_RETURN_URL, "oid_partner":self.MER_ID}
        dic['dt_order'] = util.fmt_dt_14(params['create_time'])
        dic['sign'] = self._sign(dic)
        return dic

    def ios_pay(self, request):
        if not request.user.wanglibaouserprofile.id_is_valid:
            return {"ret_code":20001, "message":"请先进行实名认证"}

        amount = request.DATA.get("amount", "")
        try:
            float(amount)
        except:
            return {"ret_code":20006, 'message':'金额格式错误'}

        amount = util.fmt_two_amount(amount)
        if amount < 100 or amount % 100 != 0 or len(str(amount)) > 20:
            return {"ret_code":20002, 'message':'金额格式错误，大于100元且为100倍数'}

        card_id = request.DATA.get("card_id", "")
        user = request.user

        try:
            pay_info = PayInfo()
            pay_info.amount = amount
            pay_info.total_amount = amount
            pay_info.type = PayInfo.DEPOSIT
            pay_info.status = PayInfo.INITIAL
            pay_info.user = user

            if card_id:
                card =  Card.objects.filter(id=card_id, user=user).first()
                if not card:
                    return {"ret_code":20006, 'message':'选择的银行卡不存在'}
                pay_info.bank = card.bank
                pay_info.card_no = card.no

            pay_info.request_ip = util.get_client_ip(request)
            order = OrderHelper.place_order(user, Order.PAY_ORDER, pay_info.status,
                                            pay_info = model_to_dict(pay_info))
            pay_info.order = order
            pay_info.save()

            profile = user.wanglibaouserprofile
            data = self.ios_sign({"id":order.id, "amount":amount, "create_time":pay_info.create_time})
            data.update({"user_name":profile.name, "id_number":profile.id_number})

            pay_info.request = str(data)
            pay_info.status = PayInfo.PROCESSING
            pay_info.account_name = profile.name
            pay_info.save()
            OrderHelper.update_order(order, user, pay_info=model_to_dict(pay_info), status=pay_info.status)

            return {"ret_code":0, "data":data}
        except Bank.DoesNotExist:
            message = u'请选择有效的银行'
            return {"ret_code":"20004", "message":message}
        except Exception, e:
            message = PayResult.RETRY
            pay_info.status = PayInfo.FAIL
            pay_info.error_message = str(e)
            pay_info.save()
            OrderHelper.update_order(order, request.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
            logger.fatal('sign error! order id: ' + str(pay_info.pk) + ' ' + str(e))
            return {"ret_code":"20005", "message":message}

    @method_decorator(transaction.atomic)
    def ios_pay_callback(self, request):
        #做来源IP限制
        dic = {}
        dic['oid_partner'] = request.DATA.get('oid_partner', "")
        dic['sign_type'] = request.DATA.get('sign_type', "")
        dic['dt_order'] = request.DATA.get('dt_order', "")
        dic['no_order'] = request.DATA.get('no_order', "")
        dic['oid_paybill'] = request.DATA.get('oid_paybill', "")
        dic['money_order'] = request.DATA.get('money_order', "")
        dic['result_pay'] = request.DATA.get('result_pay', "")
        dic['settle_date'] = request.DATA.get('settle_date', "")
        dic['info_order'] = request.DATA.get('info_order', "")
        dic['pay_type'] = request.DATA.get('pay_type', "")
        dic['bank_code'] = request.DATA.get('bank_code', "")
        dic['no_agree'] = request.DATA.get('no_agree', "")
        dic['id_type'] = request.DATA.get('id_type', "")
        dic['id_no'] = request.DATA.get('id_no', "")
        dic['acct_name'] = request.DATA.get('acct_name', "")


        #dic = {"no_order":117183, "sign_type":"MD5", "money_order":"100.00",
        #        "oid_partner":self.MER_ID}
        #import datetime
        #dic['create_time'] = datetime.datetime.fromtimestamp(1413488234.0)
        #dic['oid_paybill'] = 2011030900001098
        #dic['result_pay'] = "FAIL"
        if dic['sign_type'] == "MD5":
            sign = self._sign(dic)
        elif dic['sign_type'] == "RSA":
            sign = ""
            logger.error('RSA sign error')
        else:
            logger.error('sign error')
            return {"ret_code":20105, "message":u"不支持的签名算法"}

        ret_sign = request.DATA.get('sign', "")
        if sign != ret_sign:
            return {"ret_code":20101, "message":u"签名错误"}

        orderId = dic['no_order']
        try:
            pay_info = PayInfo.objects.select_for_update().get(order_id=orderId)
        except PayInfo.DoesNotExist:
            logger.warning('Order not found, order id: %s' % orderId)
            return {"ret_code":20102, "message":PayResult.EXCEPTION}

        if pay_info.status == PayInfo.SUCCESS:
            return {"ret_code":0, "message":PayResult.DEPOSIT_SUCCESS}

        amount = util.fmt_two_amount(dic['money_order'])
        pay_info.error_message = dic['result_pay']
        pay_info.response = "%s" % dic
        pay_info.response_ip = util.get_client_ip(request)

        if pay_info.amount != amount:
            pay_info.status = PayInfo.FAIL
            pay_info.error_message += u' 金额不匹配'
            logger.error('Amount mismatch, order id: %s request amount: %f response amount: %s',
                            orderId, float(pay_info.amount), amount)
            rs = {"ret_code":20103, "message":PayResult.EXCEPTION}
        else:
            if dic['result_pay'] == "SUCCESS":
                pay_info.fee = self.FEE
                keeper = MarginKeeper(pay_info.user, pay_info.order.pk)
                margin_record = keeper.deposit(amount)
                pay_info.margin_record = margin_record
                pay_info.status = PayInfo.SUCCESS
                rs = {"ret_code":0, "message":PayResult.DEPOSIT_SUCCESS}
            else:
                pay_info.status = PayInfo.FAIL
                rs = {"ret_code":20104, "message":PayResult.DEPOSIT_FAIL}

        pay_info.save()
        OrderHelper.update_order(pay_info.order, pay_info.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
        return rs


def add_bank_card(request):
    card_no = request.DATA.get("card_number", "")
    if not card_no or len(card_no) > 25 or not card_no.isdigit():
        return {"ret_code":20021, "message":"请输入正确的银行卡号"}
    bank_card_name = bankcard_checker.check(int(card_no[:6]))
    if not bank_card_name:
        return {"ret_code":20022, "message":"请输入合法的银行卡号"}
    bank_card_name = bank_card_name.upper()
    if "信用" in bank_card_name or "VISA" in bank_card_name or "MASTER" in bank_card_name or "万事达" in bank_card_name or "贷记" in bank_card_name:
        return {"ret_code":20023, "message":"不支付信用卡"}

    user = request.user
    exist_cards = Card.objects.filter(no=card_no, user=user)
    if exist_cards:
        return {"ret_code":20024, "message":"该银行卡已经存在"}
    bank_name = ".".join(bank_card_name.split(".")[:-1])
    try:
        bank = Bank.objects.filter(name=bank_name).first()
    except:
        return {"ret_code":20025, "message":"%s,不支持该银行" % bank_name}

    is_default = request.DATA.get("is_default", "false")
    if is_default.lower() == "true":
        is_default = True
    else:
        is_default = False
    card = Card()
    card.bank = bank
    card.no = card_no
    card.user = user
    card.is_default = is_default
    card.save()

    return {"ret_code":0, "message":"ok", "bank_name":bank_name, "card_id":card.id}

def list_bank_card(request):
    try:
       cards =  Card.objects.filter(user=request.user)
    except Exception,e:
        return {"ret_code":20031, "message":"请添加银行卡"}
    rs = []
    for x in cards:
        rs.append({"bank_name":x.bank.name, "card_no":x.no, "card_id":x.id, "default":x.is_default})
    return {"ret_code":0, "message":"ok", "cards":rs}

def del_bank_card(request):
    card_id = request.DATA.get("card_id", "")
    if not card_id or not card_id.isdigit():
        return {"ret_code":20041, "message":"请输入正确的ID"}

    card =  Card.objects.filter(id=card_id, user=request.user).first()
    if not card:
        return {"ret_code":20042, "message":"该银行卡不存在"}
    card.delete()
    return {"ret_code":0, "message":"删除成功"}
