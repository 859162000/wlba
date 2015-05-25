#!/usr/bin/env python
# encoding:utf-8

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
from marketing import tools

from Crypto import Random
from Crypto.Hash import SHA
#from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as pk
from Crypto.Cipher import PKCS1_v1_5, AES
import base64
from wanglibao_rest.utils import split_ua

logger = logging.getLogger(__name__)


class YeePay:
    FEE = 0

    def __init__(self):
        self.MER_ID = settings.YEE_MER_ID
        self.PAY_URL = settings.YEE_PAY_URL
        self.PRIV_KEY = settings.YEE_MER_PRIV_KEY
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
        #if amount < 100 or amount % 100 != 0 or len(str(amount)) > 20:
        if amount < 10 or len(str(amount)) > 20:
            #return {"ret_code":20074, 'message':'金额格式错误，大于100元且为100倍数'}
            return {"ret_code":20074, 'message':'充值金额需大于10元'}
        if amount > 20000:
            return {"ret_code":20073, 'message':'单笔充值不超过2万，单月不超过5万。如需充值更多金额可以去网站完成。'}

        terminal = deviceid.split(":")
        deviceid = terminal[-1]
        tmpdic = {"imei":0, "mac":1, "uuid":2, "other":3}
        if terminal[0] in tmpdic:
            terminaltype = tmpdic[terminal[0]]
        else:
            terminaltype = tmpdic['other']


        card_id = request.DATA.get("card_id", "")
        user = request.user
        #amount_sec = int(amount*100)
        amount_sec = long(amount*100)
        useragent = request.META.get("HTTP_USER_AGENT", "noagent").strip()

        try:
            pay_info = PayInfo()
            pay_info.amount = amount
            pay_info.total_amount = amount
            pay_info.type = PayInfo.DEPOSIT
            pay_info.status = PayInfo.INITIAL
            pay_info.user = user
            pay_info.channel = "yeepay"

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
        if rs['ret_code'] == 0:
            device = split_ua(request)
            tools.despoit_ok(pay_info, device['device_type'])
        OrderHelper.update_order(pay_info.order, pay_info.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
        return rs
