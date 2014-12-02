#!/usr/bin/env python
# encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import hashlib
import urllib
import logging
import time
import json
import traceback
from django.conf import settings
from django.forms import model_to_dict
from django.db import transaction
from django.utils.decorators import method_decorator
from wanglibao_pay import util
from wanglibao_pay.models import PayInfo, PayResult, Bank, Card
from order.utils import OrderHelper
from order.models import Order
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_sms.utils import validate_validation_code

from Crypto import Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as pk
from Crypto.Cipher import PKCS1_v1_5, AES
import base64

logger = logging.getLogger(__name__)


class YeePay:
    FEE = 0

    def __init__(self):
        self.MER_ID = settings.YEE_MER_ID
        self.PAY_URL = settings.YEE_PAY_URL
        self.PRIV_KEY = settings.YEE_MER_PRIV_KEY
        #self.PUB_KEY = settings.YEE_MER_PUB_KEY
        self.YEE_PUB_KEY = settings.YEE_PUB_KEY
        self.PAY_RETURN_URL = settings.YEE_PAY_RETURN_URL
        self.PAY_BACK_RETURN_URL = settings.YEE_PAY_BACK_RETURN_URL

    def _sign(self, dic):
        values = self._sort(dic)
        h = SHA.new(values)
        signer = pk.new(self.PRIV_KEY)
        signn = signer.sign(h)
        signn = base64.b64encode(signn)
        dic["sign"] = signn

        rand_aes_key = util.randstr()
        data = self.aes_base64_encrypt(json.dumps(dic), rand_aes_key)

        encryptkey = self.rsa_base64_encrypt(rand_aes_key, self.YEE_PUB_KEY)
        return data, encryptkey

    def _sort(self, dic):
        keys = dic.keys()
        keys.sort()
        _arr = []
        for k in keys:
            _arr.append(str(dic[k]))
        values = "".join(_arr)
        return values

    def aes_base64_encrypt(self,data,key):
        cipher = AES.new(key)
        return base64.b64encode(cipher.encrypt(self._pkcs7padding(data)))

    def aes_base64_decrypt(self,data,key):
        """
        1. base64 decode
        2. aes decode
        3. dpkcs7padding
        """
        cipher = AES.new(key)
        return self._depkcs7padding(cipher.decrypt(base64.b64decode(data)))

    def _pkcs7padding(self, data):
        """
        对齐块
        size 16
        999999999=>9999999997777777
        """
        size = AES.block_size
        count = size - len(data)%size
        if count:
            data+=(chr(count)*count)
        return data

    def _depkcs7padding(self, data):
        """
        反对齐
        """
        newdata = '' 
        for c in data:
            if ord(c) > AES.block_size:
                newdata+=c
        return newdata

    def rsa_base64_encrypt(self,data,key):
        '''
        1. rsa encrypt
        2. base64 encrypt
        '''
        cipher = PKCS1_v1_5.new(key) 
        return base64.b64encode(cipher.encrypt(data))

    def rsa_base64_decrypt(self,data,key):
        '''
        1. base64 decrypt
        2. rsa decrypt
        示例代码
        
       key = RSA.importKey(open('privkey.der').read())
        >>>
        >>> dsize = SHA.digest_size
        >>> sentinel = Random.new().read(15+dsize)      # Let's assume that average data length is 15
        >>>
        >>> cipher = PKCS1_v1_5.new(key)
        >>> message = cipher.decrypt(ciphertext, sentinel)
        >>>
        >>> digest = SHA.new(message[:-dsize]).digest()
        >>> if digest==message[-dsize:]:                # Note how we DO NOT look for the sentinel
        >>>     print "Encryption was correct."
        >>> else:
        >>>     print "Encryption was not correct."
        '''
        cipher = PKCS1_v1_5.new(key)
        return cipher.decrypt(base64.b64decode(data), Random.new().read(15+SHA.digest_size))

    def _verify(self, dic, sign):
        sign = base64.b64decode(sign)
        values = self._sort(dic)
        verifier = pk.new(self.YEE_PUB_KEY)
        if verifier.verify(SHA.new(values), sign):
            return True
        else:
            return False

    def app_pay(self, request):
        if not request.user.wanglibaouserprofile.id_is_valid:
            return {"ret_code":20071, "message":"请先进行实名认证"}

        amount = request.DATA.get("amount", "").strip()
        deviceid = request.DATA.get("device_id", "").strip()

        if not amount or not deviceid:
            return {"ret_code":20072, 'message':'信息输入不完整'}

        try:
            float(amount)
        except:
            return {"ret_code":20073, 'message':'金额格式错误'}

        amount = util.fmt_two_amount(amount)
        if amount < 100 or amount % 100 != 0 or len(str(amount)) > 20:
            return {"ret_code":20074, 'message':'金额格式错误，大于100元且为100倍数'}
        #if str(amount) != "0.02":
        #    return {"ret_code":20074, 'message':'金额只能为2分钱'}

        terminal = deviceid.split(":")
        deviceid = terminal[-1]
        tmpdic = {"imei":0, "mac":1, "uuid":2, "other":3}
        if terminal[0] in tmpdic:
            terminaltype = tmpdic[terminal[0]]
        else:
            terminaltype = tmpdic['other']


        card_id = request.DATA.get("card_id", "")
        user = request.user
        amount_sec = int(amount*100)
        useragent = request.META.get("HTTP_USER_AGENT", "noagent").strip()

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
                    return {"ret_code":20075, 'message':'选择的银行卡不存在'}
                pay_info.bank = card.bank
                pay_info.card_no = card.no

            pay_info.request_ip = util.get_client_ip(request)
            order = OrderHelper.place_order(user, Order.PAY_ORDER, pay_info.status,
                                            pay_info = model_to_dict(pay_info))
            pay_info.order = order
            pay_info.save()

            profile = user.wanglibaouserprofile
            dic = {"merchantaccount":self.MER_ID, "orderid":str(order.id), "transtime":long(time.mktime(pay_info.create_time.timetuple())),
                    "amount":amount_sec, "productcatalog":"18", "productname":"网利宝-APP充值",
                    "identityid":str(user.id), "identitytype":2, "terminaltype":terminaltype,
                    "terminalid":deviceid, "userip":pay_info.request_ip, "userua":useragent,
                    "callbackurl":self.PAY_BACK_RETURN_URL, "fcallbackurl":self.PAY_RETURN_URL,
                    "version":0, "paytypes":"1", "cardno":card_id, "orderexpdate":60}
            data, encryptkey = self._sign(dic)
            logger.error("%s" % dic)

            pay_info.request = str(dic)
            pay_info.status = PayInfo.PROCESSING
            pay_info.account_name = profile.name
            pay_info.save()
            OrderHelper.update_order(order, user, pay_info=model_to_dict(pay_info), status=pay_info.status)

            params = {"data":data, "encryptkey":encryptkey, "merchantaccount":self.MER_ID}
            url = "%s?%s" % (self.PAY_URL, urllib.urlencode(params))
            logger.error(url)
            return {"ret_code":0, "url":url}
        except Exception, e:
            logger.error(traceback.format_exc())
            message = PayResult.RETRY
            pay_info.status = PayInfo.FAIL
            pay_info.error_message = str(e)
            pay_info.save()
            OrderHelper.update_order(order, request.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
            logger.fatal('sign error! order id: ' + str(pay_info.pk) + ' ' + str(e))
            return {"ret_code":"20076", "message":message}

    @method_decorator(transaction.atomic)
    def pay_callback(self, request):
        encryptkey = request.GET.get("encryptkey", "")
        data = request.GET.get("data", "")

        if not encryptkey or not data:
            return {"ret_code":20081, "message":"params invalid"}

        try:
            ybaeskey = self.rsa_base64_decrypt(encryptkey, self.PRIV_KEY)
            params = json.loads(self.aes_base64_decrypt(data, ybaeskey))
        except Exception,e:
            logger.error(traceback.format_exc())
            return {"ret_code":20088, "message":"data decrypt error"}

        logger.error("%s" % params)

        amount = util.fmt_two_amount(params['amount']) / 100

        if "sign" not in params:
            return {"ret_code":20082, "message":"params sign not exist"}
        sign = params.pop("sign")
        if not self._verify(params, sign):
            return {"ret_code":20083, "message":"params sign invalid"}

        if params['merchantaccount'] != self.MER_ID:
            return {"ret_code":20084, "message":"params merhantaccount invalid"}

        orderId = params['orderid']
        pay_info = PayInfo.objects.filter(order_id=orderId).first()
        if not pay_info:
            return {"ret_code":20085, "message":"order not exist"}
        if pay_info.status == PayInfo.SUCCESS:
            return {"ret_code":0, "message":PayResult.DEPOSIT_SUCCESS, "amount":amount}
        
        pay_info.error_message = str(params['status'])
        pay_info.response = "%s" % params
        pay_info.response_ip = util.get_client_ip(request)

        if not pay_info.bank and "bank" in params:
            bank = Bank.objects.filter(name=params['bank']).first()
            if bank:
                pay_info.bank = bank

        if pay_info.amount != amount:
            pay_info.status = PayInfo.FAIL
            pay_info.error_message += u' 金额不匹配'
            logger.error("orderId:%s amount:%s, response amount:%s" % (orderId, pay_info.amount, amount))
            rs = {"ret_code":20086, "message":PayResult.EXCEPTION}
        else:
            if params['status'] == 1:
                pay_info.fee = self.FEE
                keeper = MarginKeeper(pay_info.user, pay_info.order.pk)
                margin_record = keeper.deposit(amount)
                pay_info.margin_record = margin_record
                pay_info.status = PayInfo.SUCCESS
                logger.error("orderId:%s yeepay response status:%s" % (orderId, params['status']))
                rs = {"ret_code":0, "message":"success", "amount":amount, "uid":pay_info.user.id}
            else:
                pay_info.status = PayInfo.FAIL
                logger.error("orderId:%s yeepay response status: %s" % (orderId, params['status']))
                rs = {"ret_code":20087, "message":PayResult.DEPOSIT_FAIL}

        pay_info.save()
        OrderHelper.update_order(pay_info.order, pay_info.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
        return rs


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
                "notify_url":self.PAY_BACK_RETURN_URL, "oid_partner":self.MER_ID,
                "risk_item":params['risk_item']}
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
            data = self.ios_sign({"id":str(order.id), "amount":str(amount), "create_time":pay_info.create_time,
                                "risk_item":str({"frms_ware_category":"2009",
                                            "user_info_mercht_userno":str(user.id),
                                            "user_info_bind_phone":profile.phone,
                                            "user_info_dt_register":util.fmt_dt_14(user.date_joined),
                                            "user_info_full_name":profile.name,
                                            "user_info_id_type":"0",
                                            "user_info_id_no":profile.id_number,
                                            "user_info_identify_state":"1",
                                            "user_info_identify_type":"3"})})
            data.update({"id_no":profile.id_number, "id_type":"0", "acct_name":profile.name})

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

    @method_decorator(transaction.atomic)
    def ios_withdraw(self, request):
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
        if not 0 <= amount <= 50000:
            return {"ret_code":20064, 'message':u'提款金额在0～50000之间'}
        margin = user.margin.margin
        if amount > margin:
            return {"ret_code":20065, 'message':u'余额不足'}

        phone = user.wanglibaouserprofile.phone
        status, message = validate_validation_code(phone, vcode)
        if status != 200:
            return {"ret_code":20066, "message":u"验证码输入错误"}
        fee = amount * LianlianPay.FEE
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


def add_bank_card(request):
    card_no = request.DATA.get("card_number", "")
    gate_id = request.DATA.get("gate_id", "")

    if not card_no or not gate_id:
        return {"ret_code":20021, "message":"信息输入不完整"}

    if len(card_no) > 25 or not card_no.isdigit():
        return {"ret_code":20022, "message":"请输入正确的银行卡号"}
    #bank_card_name = bankcard_checker.check(int(card_no[:6]))
    #if not bank_card_name:
    #    return {"ret_code":20022, "message":"请输入合法的银行卡号"}
    #bank_card_name = bank_card_name.upper()
    if card_no[0] in ("3", "4", "5"):
        return {"ret_code":20023, "message":"不支付信用卡"}

    user = request.user
    bank = Bank.objects.filter(gate_id=gate_id).first()
    if not bank:
        return {"ret_code":20025, "message":"不支持该银行"}

    exist_cards = Card.objects.filter(no=card_no, user=user).first()
    if exist_cards:
        return {"ret_code":20024, "message":"该银行卡已经存在"}

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

    card =  Card.objects.filter(id=card_id, user=request.user).first()
    if not card:
        return {"ret_code":20042, "message":"该银行卡不存在"}
    card.delete()
    return {"ret_code":0, "message":"删除成功"}

def list_bank(request):
    banks = Bank.get_deposit_banks()
    rs = []
    for x in banks:
        rs.append({"name":x.name, "gate_id":x.gate_id})
    if not rs:
        return {"ret_code":20051, "message":"没有可选择的银行"}
    return {"ret_code":0, "message":"ok", "banks":rs}
