#!/usr/bin/env python
# encoding:utf-8

import urllib
import logging
import time
import json
import requests
import traceback
from django.conf import settings
from django.forms import model_to_dict
from django.db import transaction
from django.utils import timezone
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
            tools.despoit_ok(pay_info, device)
        OrderHelper.update_order(pay_info.order, pay_info.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
        return rs

    def pre_pay(self, request):
        self.app_pay(request)


class YeeShortPay:
    """ 易宝快捷支付 """

    FEE = 0

    def __init__(self):
        self.PRIV_KEY = settings.YEE_MER_PRIV_KEY
        self.YEE_PUB_KEY = settings.YEE_PUB_KEY
        self.MER_ID = settings.YEE_MER_ID
        self.BIND_URL = settings.YEE_SHORT_BIND
        self.UNBIND_URL = settings.YEE_SHORT_UNBIND
        self.BIND_SEND_SMS = settings.YEE_SHORT_BIND_SEND_SMS
        self.BIND_CHECK_SMS = settings.YEE_SHORT_BIND_CHECK_SMS
        self.BIND_CARD_QUERY = settings.YEE_SHORT_BIND_CARD_QUERY
        self.BIND_PAY_REQUEST = settings.YEE_SHORT_BIND_PAY_REQUEST
        self.BIND_PAY_VALIDATE = settings.YEE_SHORT_BIND_PAY_VALIDATE

    def _sign(self, dic):
        values = self._sort(dic)
        h = SHA.new(values)
        signer = pk.new(self.PRIV_KEY)
        sign_result = signer.sign(h)
        sign_result = base64.b64encode(sign_result)
        dic["sign"] = sign_result

        rand_aes_key = util.randstr()
        data = self.aes_base64_encrypt(json.dumps(dic), rand_aes_key)

        encryptkey = self.rsa_base64_encrypt(rand_aes_key, self.YEE_PUB_KEY)
        return data, encryptkey

    def _sort(self, dic):
        keys = dic.keys()
        keys.sort()
        return "".join([str(dic[k]) for k in keys])

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
        """
        1. rsa encrypt
        2. base64 encrypt
        """
        cipher = PKCS1_v1_5.new(key)
        return base64.b64encode(cipher.encrypt(data))

    def rsa_base64_decrypt(self,data,key):
        """
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
        """
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

    def save_card(self, user, card_no, bank):
        """ 保存卡信息到个人名下 """
        if len(card_no) == 10:
            card = Card.objects.filter(user=user, no__startswith=card_no[:6], no__endswith=card_no[-4:]).first()
        else:
            card = Card.objects.filter(no=card_no, user=user).first()

        if not card:
            card = Card()
            card.user = user
            card.no = card_no
            card.is_default = False

        card.bank = bank
        card.is_bind_yee = True
        card.save()
        return True

    def _format_post(self, post):
        """ 签名格式化请求数据 """
        data, encryptkey = self._sign(post)
        return {"data": data, "encryptkey": encryptkey, "merchantaccount": self.MER_ID}

    def _request_yee(self, url, data):
        post = self._format_post(data)
        res = requests.post(url, post)
        return self._response_data_change(res=json.loads(res.text))

    def _response_data_change(self, res):
        """ 将易宝返回的数据格式化成程序通用数据 """
        if 'data' not in res:
            return {'ret_code': 20012, 'message': '易宝数据有误'}

        flag, data = self._response_decode(res=res)
        if not flag:
            return {'ret_code': 20011, 'message': '签名验证失败'}

        if 'error_code' in data:
            return {'ret_code': data['error_code'], 'message': data['error_msg'], 'data': data}

        return {'ret_code': 0, 'message': 'ok', 'data': data}

    def _response_decode(self, res):
        """ 返回数据合法性校验 """
        if 'encryptkey' in res and 'data' in res:
            ybaeskey = self.rsa_base64_decrypt(res['encryptkey'], self.PRIV_KEY)
            data = json.loads(self.aes_base64_decrypt(res['data'], ybaeskey))
            if 'sign' in data:
                sign = data.pop('sign')
                if self._verify(data, sign):
                    return True, data
        return False, res

    def _bind_card_request(self, request, phone, card_no, request_id, terminaltype, terminalid):
        """ 邦卡请求 """
        user = request.user

        post = dict()
        post['merchantaccount'] = self.MER_ID
        post['cardno'] = card_no
        post['idcardtype'] = '01'
        post['idcardno'] = user.wanglibaouserprofile.id_number
        post['username'] = user.wanglibaouserprofile.name
        post['phone'] = phone
        post['requestid'] = request_id
        post['userip'] = util.get_client_ip(request)
        post['productcatalog'] = '18'
        post['identityid'] = user.wanglibaouserprofile.id_number
        post['identitytype'] = 5
        post['terminaltype'] = terminaltype  # 终端标识类型
        post['terminalid'] = terminalid  # 终端设备id

        return self._request_yee(url=self.BIND_URL, data=post)

    def _bind_send_sms(self, request_id):
        """ 绑卡发送验证码 """
        post = dict()
        post['merchantaccount'] = self.MER_ID
        post['requestid'] = request_id
        return self._request_yee(url=self.BIND_SEND_SMS, data=post)

    def _bind_check_sms(self, request_id, validatecode):
        """ 绑卡校验验证码 """
        post = dict()
        post['merchantaccount'] = self.MER_ID
        post['requestid'] = request_id
        post['validatecode'] = validatecode
        return self._request_yee(url=self.BIND_CHECK_SMS, data=post)

    def bind_card_query(self, user):
        """ 查询已经绑定的银行卡 """
        if not user.wanglibaouserprofile.id_is_valid:
            return {"ret_code": 20071, "message": "请先进行实名认证"}

        post = dict()
        post['merchantaccount'] = self.MER_ID
        post['identityid'] = user.wanglibaouserprofile.id_number
        post['identitytype'] = 5
        return self._request_yee(url=self.BIND_CARD_QUERY, data=post)

    def delete_bind(self, user, card, bank):
        """ 解绑银行卡 """
        if card.is_bind_yee and card.yee_bind_id:
            res = self._unbind_card(user, card.yee_bind_id)
            if res['ret_code'] !=0:
                return {'ret_code': res['ret_code'], 'message': res['message']}

            card.is_bind_yee = False
            card.yee_bind_id = ''
            card.save()
            return res

    def _unbind_card(self, user, bind_id):
        """ 解绑银行卡 """
        post = dict()
        post['merchantaccount'] = self.MER_ID
        post['bindid'] = bind_id  # 绑卡ID
        post['identityid'] = user.wanglibaouserprofile.id_number
        post['identitytype'] = 5
        return self._request_yee(url=self.UNBIND_URL, data=post)

    def _pay_request(self, request, order_id, card, pay_info, terminaltype, terminalid):
        """ 支付请求 """
        post = dict()
        post['merchantaccount'] = self.MER_ID
        post['bindid'] = str(card.yee_bind_id)
        post['orderid'] = order_id
        post['transtime'] = int(time.time())
        post['amount'] = int(pay_info.amount * 100)
        post['productcatalog'] = '18'
        post['productname'] = '网利宝-APP充值'
        post['identityid'] = request.user.wanglibaouserprofile.id_number
        post['identitytype'] = 5
        post['terminaltype'] = terminaltype  # 终端标识类型
        post['terminalid'] = terminalid  # 终端设备id
        post['userip'] = util.get_client_ip(request)
        return self._request_yee(url=self.BIND_PAY_REQUEST, data=post)

    def _pay_validity(self, order_id):
        """ 确认支付 """
        post = dict()
        post['merchantaccount'] = self.MER_ID
        post['orderid'] = order_id
        return self._request_yee(url=self.BIND_PAY_VALIDATE, data=post)

    def add_card_unbind(self, user, card_no, bank):
        """ 保存卡信息到个人名下，不绑定任何渠道 """
        if len(card_no) == 10:
            card = Card.objects.filter(user=user, no__startswith=card_no[:6], no__endswith=card_no[-4:]).first()
        else:
            card = Card.objects.filter(no=card_no, user=user).first()

        if not card:
            card = Card()
            card.user = user
            card.no = card_no
            card.is_default = False

        card.bank = bank
        card.save()
        return card

    def pre_pay(self, request):
        """ 获取验证码支付还是直接支付
            长卡号获取验证码
            短卡号直接支付
        """
        if not request.user.wanglibaouserprofile.id_is_valid:
            return {"ret_code": 20111, "message": "请先进行实名认证"}

        amount = request.DATA.get("amount", "").strip()
        card_no = request.DATA.get("card_no", "").strip()
        input_phone = request.DATA.get("phone", "").strip()
        gate_id = request.DATA.get("gate_id", "").strip()

        # 易宝支付需要设备信息
        deviceid = request.DATA.get("device_id", "").strip()

        if not amount or not card_no or not deviceid or not gate_id:
            return {"ret_code": 20112, 'message': '信息输入不完整'}
        if len(card_no) > 10 and (not input_phone or not gate_id):
            return {"ret_code": 20113, 'message': '卡号格式不正确'}

        try:
            float(amount)
        except:
            return {"ret_code": 20114, 'message': '金额格式错误'}

        amount = util.fmt_two_amount(amount)
        if amount < 10 or len(str(amount)) > 20:
            return {"ret_code": 20115, 'message': '充值须大于等于10元'}

        user = request.user
        profile = user.wanglibaouserprofile

        bank = Bank.objects.filter(gate_id=gate_id).first()
        if not bank or not bank.yee_bind_code.strip():
            return {"ret_code": 201116, "message": "不支持该银行"}

        if len(card_no) == 10:
            card = Card.objects.filter(user=user, no__startswith=card_no[:6], no__endswith=card_no[-4:]).first()
        else:
            card = Card.objects.filter(no=card_no, user=user).first()

        if not card:
            card = self.add_card_unbind(user, card_no, bank)

        if not card or not bank:
            return {'ret_code': 200117, 'message': '卡号不存在或银行不存在'}

        if bank and card and bank != card.bank:
            return {"ret_code": 200118, "message": "银行卡与银行不匹配"}

        # 获取设备标识
        terminal = deviceid.split(":")
        deviceid = terminal[-1]
        tmpdic = {"imei": 0, "mac": 1, "uuid": 2, "other": 3}
        if terminal[0] in tmpdic:
            terminaltype = tmpdic[terminal[0]]
        else:
            terminaltype = tmpdic['other']

        try:
            pay_info = PayInfo()
            pay_info.amount = amount
            pay_info.total_amount = amount
            pay_info.type = PayInfo.DEPOSIT
            pay_info.status = PayInfo.INITIAL
            pay_info.user = user
            pay_info.channel = "yeepay_bind"

            pay_info.request_ip = util.get_client_ip(request)
            order = OrderHelper.place_order(user, Order.PAY_ORDER, pay_info.status, pay_info=model_to_dict(pay_info))
            pay_info.order = order

            pay_info.bank = card.bank
            pay_info.card_no = card.no

            pay_info.request = ""
            pay_info.status = PayInfo.PROCESSING
            pay_info.account_name = profile.name
            pay_info.save()
            OrderHelper.update_order(order, user, pay_info=model_to_dict(pay_info), status=pay_info.status)

            if len(card_no) == 10:
                # 直接支付交易，已经绑定了银行卡，直接进行支付操作
                res = self._pay_request(request, order.id, card, pay_info, terminaltype, deviceid)
                if res['ret_code'] != 0:
                    pay_info.error_code = res['ret_code']
                    pay_info.error_message = res['message']
                    if 'data' in res:
                        pay_info.response = res['data']
                    pay_info.save()
                    return res

                res = self._pay_validity(order.id)
                if res['ret_code'] != 0:
                    pay_info.error_code = res['ret_code']
                    pay_info.error_message = res['message']
                    if 'data' in res:
                        pay_info.response = res['data']
                    pay_info.save()
                    return res

                device = split_ua(request)
                device_type = device['device_type']
                ms = self.handle_margin(pay_info.amount, order.id, user.id, util.get_client_ip(request), res['data'], device_type)
                return ms
            else:
                # 未绑定银行卡，需要先绑定银行卡获取验证码，然后在确认支付

                # 商户生成的唯一绑卡请求号，最长50位
                request_id = '{phone}{time}'.format(phone=profile.phone, time=timezone.now().strftime("%Y%m%d%H%M%S"))

                # 请求绑定银行卡
                res = self._bind_card_request(request, input_phone, card_no, request_id, terminaltype, deviceid)
                if res['ret_code'] != 0:
                    pay_info.error_code = res['ret_code']
                    pay_info.error_message = res['message']
                    if 'data' in res:
                        pay_info.response = res['data']
                    pay_info.save()
                    return res

                # 请求绑定银行卡发送验证码
                res = self._bind_send_sms(request_id)
                if res['ret_code'] != 0:
                    pay_info.error_code = res['ret_code']
                    pay_info.error_message = res['message']
                    if 'data' in res:
                        pay_info.response = res['data']
                    pay_info.save()
                    return res

                return {"ret_code": 0, "message": "ok", "order_id": order.id, "token": request_id}

        except Exception, e:
            logger.error(traceback.format_exc())
            message = PayResult.RETRY
            pay_info.status = PayInfo.FAIL
            pay_info.error_message = str(e)
            pay_info.save()
            OrderHelper.update_order(order, request.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
            return {"ret_code": "20119", "message": message}

    def dynnum_bind_pay(self, request):
        """ 验证码通过邦卡支付
            先校邦卡验证码，邦卡验证码通过之后，在进行支付操作
        """
        vcode = request.DATA.get("vcode", "").strip()
        order_id = request.DATA.get("order_id", "").strip()
        request_id = request.DATA.get("token", "").strip()
        input_phone = request.DATA.get("phone", "").strip()

        # 易宝支付需要设备信息
        deviceid = request.DATA.get("device_id", "").strip()

        if not order_id.isdigit():
            return {"ret_code": 20125, "message": "订单号错误"}

        pay_info = PayInfo.objects.filter(order_id=order_id).first()
        if not pay_info or pay_info.status == PayInfo.SUCCESS:
            return {"ret_code": 20121, "message": "订单不存在或已支付成功"}

        user = request.user
        card_no = pay_info.card_no
        if len(card_no) == 10:
            card = Card.objects.filter(user=user, no__startswith=card_no[:6], no__endswith=card_no[-4:]).first()
        else:
            card = Card.objects.filter(no=card_no, user=user).first()

        res = self._bind_check_sms(request_id, vcode)
        if res['ret_code'] != 0:
            pay_info.error_code = res['ret_code']
            pay_info.error_message = res['message']
            if 'data' in res:
                pay_info.response = res['data']
            pay_info.save()
            return res
        # 绑定银行卡成功
        card.is_bind_yee = True
        card.yee_bind_id = res['data']['bindid']
        card.save()

        # 获取设备标识
        terminal = deviceid.split(":")
        deviceid = terminal[-1]
        tmpdic = {"imei": 0, "mac": 1, "uuid": 2, "other": 3}
        if terminal[0] in tmpdic:
            terminaltype = tmpdic[terminal[0]]
        else:
            terminaltype = tmpdic['other']

        res = self._pay_request(request, order_id, card, pay_info, terminaltype, deviceid)
        if res['ret_code'] != 0:
            pay_info.error_code = res['ret_code']
            pay_info.error_message = res['message']
            if 'data' in res:
                pay_info.response = res['data']
            pay_info.save()
            return res

        res = self._pay_validity(order_id)
        if res['ret_code'] != 0:
            pay_info.error_code = res['ret_code']
            pay_info.error_message = res['message']
            if 'data' in res:
                pay_info.response = res['data']
            pay_info.save()
            return res

        device = split_ua(request)
        ms = self.handle_margin(pay_info.amount, order_id, user.id, util.get_client_ip(request), res['data'], device)
        return ms

    @method_decorator(transaction.atomic)
    def handle_margin(self, amount, order_id, user_id, ip, response_content, device):
        pay_info = PayInfo.objects.filter(order_id=order_id).first()
        if not pay_info:
            return {"ret_code": 20131, "message": "order not exist"}
        if pay_info.status == PayInfo.SUCCESS:
            return {"ret_code": 0, "message": PayResult.DEPOSIT_SUCCESS, "amount": amount}

        pay_info.error_message = ""
        pay_info.response = response_content
        pay_info.response_ip = ip

        if pay_info.amount != amount:
            pay_info.status = PayInfo.FAIL
            pay_info.error_message += u' 金额不匹配'
            logger.error("orderId:%s amount:%s, response amount:%s" % (order_id, pay_info.amount, amount))
            rs = {"ret_code": 20132, "message": PayResult.EXCEPTION}
        elif pay_info.user_id != user_id:
            pay_info.status = PayInfo.FAIL
            pay_info.error_message += u"用户不匹配"
            logger.error("orderId:%s 充值用户ID不匹配" % order_id)
            rs = {"ret_code": 20133, "message": PayResult.EXCEPTION}
        else:
            pay_info.fee = self.FEE
            keeper = MarginKeeper(pay_info.user, pay_info.order.pk)
            margin_record = keeper.deposit(amount)
            pay_info.margin_record = margin_record
            pay_info.status = PayInfo.SUCCESS
            logger.error("orderId:%s success" % order_id)
            rs = {"ret_code": 0, "message": "success", "amount": amount, "margin": margin_record.margin_current}

        pay_info.save()
        if rs['ret_code'] == 0:
            tools.despoit_ok(pay_info, device)

            # 充值成功后，更新本次银行使用的时间
            if len(pay_info.card_no) == 10:
                Card.objects.filter(user=pay_info.user, no__startswith=pay_info.card_no[:6], no__endswith=pay_info.card_no[-4:]).update(last_update=timezone.now())
            else:
                Card.objects.filter(user=pay_info.user, no=pay_info.card_no).update(last_update=timezone.now())

        OrderHelper.update_order(pay_info.order, pay_info.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
        return rs
