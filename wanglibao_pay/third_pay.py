#!/usr/bin/env python
# encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import urllib
import logging
import time
import json
import traceback
from lxml import etree
import requests
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
from wanglibao_sms.utils import validate_validation_code
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

class KuaiPay:
    FEE = 0

    def __init__(self):
        self.MER_ID = settings.KUAI_MER_ID
        self.MER_PASS = settings.KUAI_MER_PASS
        self.PAY_URL = settings.KUAI_PAY_URL
        self.QUERY_URL = settings.KUAI_QUERY_URL
        self.DEL_URL = settings.KUAI_DEL_URL
        self.DYNNUM_URL = settings.KUAI_DYNNUM_URL
        self.PAY_BACK_RETURN_URL = settings.KUAI_PAY_BACK_RETURN_URL
        self.TERM_ID = settings.KUAI_TERM_ID

        self.headers = {"User-Agent":"wanglibao for 99bill client by lzj",
                        "Content-Type":"application/x-www-form-urlencoded"}
        self.xmlheader = '<?xml version="1.0" encoding="UTF-8"?>\n'
        self.pem = settings.KUAI_PEM_PATH
        self.auth = (self.MER_ID, self.MER_PASS)

    def _sp_bind_xml(self, user_id):
        xml = etree.XML("""
            <MasMessage xmlns="http://www.99bill.com/mas_cnp_merchant_interface">
                <version>1.0</version>
                <PciQueryContent>
                    <merchantId>%s</merchantId>
                    <customerId>%s</customerId>
                    <cardType>0002</cardType>
                </PciQueryContent>
            </MasMessage>
        """ % (self.MER_ID, user_id))
        return self.xmlheader + etree.tostring(xml)

    def _sp_delbind_xml(self, dic):
        xml = etree.XML("""
            <MasMessage xmlns="http://www.99bill.com/mas_cnp_merchant_interface">
                <version>1.0</version>
                <PciDeleteContent>
                    <merchantId>%s</merchantId>
                    <customerId>%s</customerId>
                    <storablePan>%s</storablePan>
                    <bankId>%s</bankId>
                </PciDeleteContent>
            </MasMessage>
        """ % (self.MER_ID, dic['user_id'],
                dic['storable_no'], dic['bank_id']))
        return self.xmlheader + etree.tostring(xml)

    def _sp_dynnum_xml(self, dic):
        xml = etree.XML("""
            <MasMessage xmlns="http://www.99bill.com/mas_cnp_merchant_interface">
                <version>1.0</version>
                <GetDynNumContent>
                    <merchantId>%s</merchantId>
                    <customerId>%s</customerId>
                    <externalRefNumber>%s</externalRefNumber>
                    <amount>%s</amount>
                    <pan>%s</pan>
                    <phoneNO>%s</phoneNO>
                    <cardHolderName>%s</cardHolderName>
                    <idType>0</idType>
                    <cardHolderId>%s</cardHolderId>
                </GetDynNumContent>
            </MasMessage>
        """ % (self.MER_ID, dic['user_id'], dic['order_id'],
                dic['amount'], dic['card_no'], dic['phone'],
                dic['name'], dic['id_number']))
        return self.xmlheader + etree.tostring(xml, encoding="utf-8")

    def _sp_bindpay_xml(self, dic):
        xml = etree.XML("""
            <MasMessage xmlns="http://www.99bill.com/mas_cnp_merchant_interface">
                <version>1.0</version>
                <TxnMsgContent>
                    <interactiveStatus>TR1</interactiveStatus>
                    <txnType>PUR</txnType>
                    <merchantId>%s</merchantId>
                    <terminalId>%s</terminalId>
                    <entryTime>%s</entryTime>
                    <cardNo>%s</cardNo>
                    <bankId>%s</bankId>
                    <amount>%s</amount>
                    <externalRefNumber>%s</externalRefNumber>
                    <customerId>%s</customerId>
                    <cardHolderName>%s</cardHolderName>
                    <idType>0</idType>
                    <cardHolderId>%s</cardHolderId>
                    <spFlag>QuickPay</spFlag>
                    <extMap>
                        <extDate><key>phone</key><value>%s</value></extDate>
                        <extDate><key>validCode</key><value>%s</value></extDate>
                        <extDate><key>savePciFlag</key><value>1</value></extDate>
                        <extDate><key>token</key><value>%s</value></extDate>
                        <extDate><key>payBatch</key><value>1</value></extDate>
                    </extMap>
                </TxnMsgContent>
            </MasMessage>
        """ % (self.MER_ID, self.TERM_ID, dic['time'], dic['card_no'], dic['bank_id'], dic['amount'], 
                dic['order_id'], dic['user_id'], dic['name'], dic['id_number'],
                dic['phone'], dic['vcode'], dic['token']))
        return self.xmlheader + etree.tostring(xml, encoding="utf-8")

    def _sp_qpay_xml(self, dic):
        xml = etree.XML("""
            <MasMessage xmlns="http://www.99bill.com/mas_cnp_merchant_interface">
                <version>1.0</version>
                <TxnMsgContent>
                    <interactiveStatus>TR1</interactiveStatus>
                    <txnType>PUR</txnType>
                    <merchantId>%s</merchantId>
                    <terminalId>%s</terminalId>
                    <tr3Url>%s</tr3Url>
                    <entryTime>%s</entryTime>
                    <storableCardNo>%s</storableCardNo>
                    <bankId>%s</bankId>
                    <amount>%s</amount>
                    <externalRefNumber>%s</externalRefNumber>
                    <customerId>%s</customerId>
                    <spFlag>QPay02</spFlag>
                    <extMap>
                        <extDate><key>phone</key><value></value></extDate>
                        <extDate><key>validCode</key><value></value></extDate>
                        <extDate><key>savePciFlag</key><value>0</value></extDate>
                        <extDate><key>token</key><value></value></extDate>
                        <extDate><key>payBatch</key><value>2</value></extDate>
                    </extMap>
                </TxnMsgContent>
            </MasMessage>
        """ % (self.MER_ID, self.TERM_ID, self.PAY_BACK_RETURN_URL, dic['time'],
                dic['storable_no'], dic['bank_id'], dic['amount'], dic['order_id'],
                dic['user_id']))
        return self.xmlheader + etree.tostring(xml, encoding="utf-8")

    def _request(self, data, url):
        headers = self.headers
        headers['Content-Length'] = str(len(data))
        res = requests.post(url, headers=headers, data=data, cert=self.pem, auth=self.auth)
        return res

    def _result2dict(self, content):
        xml = etree.XML(content)
        nsmap = xml.nsmap.values()
        nsmap = ["{"+x+"}" for x in nsmap]

        xml.tag = del_xmlns(nsmap, xml.tag)
        dic = {xml.tag: []}
        xml2dict(xml, dic[xml.tag], nsmap)
        return dic

    def query_bind(self, request):
        data = self._sp_bind_xml(request.user.id)
        res = self._request(data, self.QUERY_URL)

        logger.error(res.content)

        if res.status_code != 200:
            return {"ret_code":-1, "message":"fetch error"}
        if "errorCode" in res.content:
            return {"ret_code":-1, "message":"fetch error"}
        #c = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><MasMessage xmlns="http://www.99bill.com/mas_cnp_merchant_interface"><PciQueryContent><merchantId>104110045112012</merchantId><customerId>1</customerId><cardType>0001</cardType><pciInfos><pciInfo><bankId>CMB</bankId><storablePan>6225750715</storablePan><shortPhoneNo>1803291</shortPhoneNo><phoneNO>18038153291</phoneNO></pciInfo><pciInfo><bankId>CMB</bankId><storablePan>6225750716</storablePan><shortPhoneNo>1803292</shortPhoneNo><phoneNO>18038153292</phoneNO></pciInfo></pciInfos><responseCode>00</responseCode></PciQueryContent></MasMessage> """
        dic = self._result2dict(res.content)
        pqc = dic['MasMessage'][0]['PciQueryContent']['value']
        cards = []
        for x in pqc:
            if "responseCode" in x: res_code = x['responseCode']['value'];continue
            if "merchantId" in x: merchantId = x['merchantId']['value'];continue
            if "customerId" in x: customerId = x['customerId']['value'];continue
            if "responseTextMessage" in x: message = x['responseTextMessage']['value'];continue
            if "pciInfos" in x:
                pis = x['pciInfos']['value']
                for y in pis:
                    card = {}
                    for z in y['pciInfo']['value']:
                        if "bankId" in z:
                            card['bank_id'] = z['bankId']['value']
                            bank = Bank.objects.filter(kuai_code=card['bank_id']).first()
                            card['bank_name'] = bank.name
                            if bank.kuai_limit:
                                card.update(_handle_kuai_bank_limit(bank.kuai_limit))
                        if "storablePan" in z:
                            card['storable_no'] = z["storablePan"]['value']
                    cards.append(card)
        if res_code != "00":
            return {"ret_code":20091, "message":message}
        if merchantId != self.MER_ID or customerId != str(request.user.id):
            return {"ret_code":20092, "message":"卡信息不匹配"}

        card_list = Card.objects.filter(user=request.user).select_related('bank')
        bank_list = [card_list.bank.kuai_code]
        cards = sorted(cards, lambda x: bank_list.index(x['bank_id']))
        return {"ret_code":0, "message":"test", "cards":cards}

    def _handle_dynnum_result(self, res):
        if res.status_code != 200 or "errorCode" in res.content:
            return False

        logger.error(res.content)

        dic = self._result2dict(res.content)
        res_code = None
        gdc = dic['MasMessage'][0]["GetDynNumContent"]
        for x in gdc['value']:
            if "responseCode" in x: res_code = x['responseCode']['value'];continue
            if "token" in x: token = x['token']['value'];continue
            if "responseTextMessage" in x: message = x['responseTextMessage']['value'];continue
        res_code = res_code.lower()
        if res_code == "00":
            return {"ret_code":0, "token":token}
        elif res_code == "96":
            return {"ret_code":1, "message":"支付网关服务异常"}
        else:
            return {"ret_code":2, "message":message}

    def _handle_pay_result(self, res):
        dic = self._result2dict(res.content)
        mer_id = None
        for k in dic['MasMessage']:
            if "TxnMsgContent" in k:
                tmc = k['TxnMsgContent']['value']
                for x in tmc:
                    #if "amount" in x:amount = float(x['amount']['value']); continue
                    if "amount" in x:amount = util.fmt_two_amount(x['amount']['value']); continue
                    if "responseCode" in x: res_code = x['responseCode']['value']; continue
                    if "externalRefNumber" in x: order_id = x['externalRefNumber']['value']; continue
                    if "merchantId" in x: mer_id = x['merchantId']['value']; continue
                    if "customerId" in x: user_id = x['customerId']['value']; continue
                    if "issuer" in x: bank_name = x['issuer']['value']; continue
                    if "responseTextMessage" in x: message = x['responseTextMessage']['value'];continue
        if mer_id != self.MER_ID:
            return False

        res_code = res_code.lower()
        if res_code == "00":
            return {"ret_code": 0, "order_id":int(order_id), "user_id":int(user_id),
                    "bank_name":bank_name, "amount":amount}
        elif res_code == "t6":
            return {"ret_code": 1, "message":"验证码不正确"}
        elif res_code == "c0":
            return {"ret_code": 2, "message":"请耐心等候充值完成"}
        elif res_code == "og":
            return {"ret_code": 3, "message":"充值金额太大"}
        elif res_code == "tc":
            return {"ret_code": 4, "message":"不能使用信用卡"}
        elif res_code == "51":
            return {"ret_code": 51, "message":"余额不足"}
        else:
            return {"ret_code": 5, "message":message}

    def _handle_del_result(self, res):
        dic = self._result2dict(res.content)
        mer_id = None
        pdc = dic['MasMessage'][0]['PciDeleteContent']['value']
        for x in pdc:
            if "responseCode" in x: res_code = x['responseCode']['value'];continue
            if "merchantId" in x: mer_id = x['merchantId']['value'];continue
            if "customerId" in x: user_id = x['customerId']['value'];continue
            if "responseTextMessage" in x: message = x['responseTextMessage']['value'];continue
        if mer_id != self.MER_ID:
            return False 
        res_code = res_code.lower()
        if res_code == "00":
            return {"ret_code":0}
        else:
            return {"ret_code":1, "message":message}

    def delete_bind(self, request):
        user = request.user

        #card_no = request.DATA.get("card_no", "").strip()
        card_no = request.DATA.get("storable_no", "").strip()
        bank_id = request.DATA.get("bank_id", "").strip()

        dic = {"user_id":user.id, "bank_id":bank_id,
                "storable_no":card_no}

        data = self._sp_delbind_xml(dic)
        res = self._request(data, self.DEL_URL)
        logger.error(data)
        logger.error(res.content)

        if res.status_code != 200 or "errorCode" in res.content:
            return {"ret_code":20101, "message":"解除绑定失败"}
        result = self._handle_del_result(res)
        if not result:
            return {"ret_code":20102, "message":"解除信息不匹配"}
        elif result['ret_code']:
            return {"ret_code":20103, "message":result['message']}
        return {"ret_code":0, "message":"ok"}
    
    def pre_pay(self, request):
        if not request.user.wanglibaouserprofile.id_is_valid:
            return {"ret_code":20111, "message":"请先进行实名认证"}

        amount = request.DATA.get("amount", "").strip()
        card_no = request.DATA.get("card_no", "").strip()
        input_phone = request.DATA.get("phone", "").strip()
        gate_id = request.DATA.get("gate_id","").strip()

        if not amount or not card_no:
            return {"ret_code":20112, 'message':'信息输入不完整'}
        if len(card_no) > 10 and (not input_phone or not gate_id):
            return {"ret_code":20112, 'message':'信息输入不完整'}

        #if card_no[0] in ("3", "4", "5"):
        #    return {"ret_code":20113, "message":"不能使用信用卡"}

        try:
            float(amount)
        except:
            return {"ret_code":20114, 'message':'金额格式错误'}

        amount = util.fmt_two_amount(amount)
        #if amount < 100 or amount % 100 != 0 or len(str(amount)) > 20:
        #if amount < 10 or amount % 1 != 0 or len(str(amount)) > 20:
        if amount < 10 or len(str(amount)) > 20:
            return {"ret_code":20115, 'message':'充值须大于等于10元'}

        user = request.user
        profile = user.wanglibaouserprofile
        card = None
        bank = None
        if gate_id:
            bank = Bank.objects.filter(gate_id=gate_id).first()
            if not bank or not bank.kuai_code.strip():
                return {"ret_code":201151, "message":"不支持该银行"}
        if len(card_no) == 10:
            card = Card.objects.filter(user=user, no__startswith=card_no[:6], no__endswith=card_no[-4:]).first()
        else:
            card = Card.objects.filter(no=card_no, user=user).first()
            if bank and card and bank != card.bank:
                return {"ret_code":201153, "message":"银行卡与银行不匹配"}

        if not card and not bank:
            return {"ret_code":201152, "message":"卡号不存在或银行不存在"}

        try:
            pay_info = PayInfo()
            pay_info.amount = amount
            pay_info.total_amount = amount
            pay_info.type = PayInfo.DEPOSIT
            pay_info.status = PayInfo.INITIAL
            pay_info.user = user
            pay_info.channel = "kuaipay"

            pay_info.request_ip = util.get_client_ip(request)
            order = OrderHelper.place_order(user, Order.PAY_ORDER, pay_info.status,
                                            pay_info = model_to_dict(pay_info))
            pay_info.order = order

            if card:
                pay_info.bank = card.bank
                pay_info.card_no = card.no
            else:
                pay_info.bank = bank
                pay_info.card_no = card_no

            pay_info.request = ""
            pay_info.status = PayInfo.PROCESSING
            pay_info.account_name = profile.name
            pay_info.save()
            OrderHelper.update_order(order, user, pay_info=model_to_dict(pay_info), status=pay_info.status)

            dic = {"user_id":user.id, "order_id":order.id, "id_number":profile.id_number.upper(),
                    "phone":input_phone, "name":profile.name, "amount":amount,
                    "card_no":pay_info.card_no}

            if len(card_no) == 10:
                dic['storable_no'] = card_no
                dic['bank_id'] = card.bank.kuai_code
                dic['time'] = timezone.now().strftime("%Y%m%d%H%M%S")

                data = self._sp_qpay_xml(dic)
                logger.error("second pay info")
                logger.error(u"%s"%data)
                url = self.PAY_URL
            else:
                data = self._sp_dynnum_xml(dic)
                logger.error("first pay info")
                logger.error(u"%s" % data)

                url = self.DYNNUM_URL

            res = self._request(data, url)

            if len(card_no) == 10:
                result = self._handle_pay_result(res)
                if not result:
                    return {"ret_code":201171, "message":"信息不匹配"}
                elif result['ret_code'] >0:
                    pay_info.error_message = result['message']
                    pay_info.response = res.content
                    pay_info.save()
                    return {"ret_code":201181, "message":result['message']}
                device = split_ua(request)
                device_type = device['device_type']
                ms = self.handle_margin(result['amount'], result['order_id'], result['user_id'], util.get_client_ip(request), res.content, device_type)
                return ms
            else:
                token = self._handle_dynnum_result(res)
                if not token:
                    return {"ret_code":201172, "message":"信息不匹配"}
                elif token['ret_code'] != 0:
                    pay_info.error_message = token['message']
                    pay_info.save()
                    return {"ret_code":201182, "message":token['message']}

                # 充值成功后，更新本次银行使用的时间
                card.update(last_update=timezone.now())

                return {"ret_code":0, "message":"ok", "order_id":order.id, "token":token['token']}
        except Exception, e:
            logger.error(traceback.format_exc())
            message = PayResult.RETRY
            pay_info.status = PayInfo.FAIL
            pay_info.error_message = str(e)
            pay_info.save()
            OrderHelper.update_order(order, request.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
            return {"ret_code":"20119", "message":message}
            
    def dynnum_bind_pay(self, request):
        vcode = request.DATA.get("vcode", "").strip()
        order_id = request.DATA.get("order_id", "").strip()
        token = request.DATA.get("token", "").strip()
        input_phone = request.DATA.get("phone", "").strip()

        if not order_id.isdigit():
            return {"ret_code":20125, "message":"订单号错误"}

        pay_info = PayInfo.objects.filter(order_id=order_id).first()
        if not pay_info or pay_info.status == PayInfo.SUCCESS:
            return {"ret_code":20121, "message":"订单不存在或已支付成功"}
        user = request.user
        profile = user.wanglibaouserprofile
        dic = {"user_id":user.id, "order_id":order_id, "id_number":profile.id_number.upper(),
                "phone":input_phone, "name":profile.name, "amount":pay_info.amount,
                "time":pay_info.create_time.strftime("%Y%m%d%H%M%S"), "vcode":vcode,
                "card_no":pay_info.card_no, "token":token, "bank_id":pay_info.bank.kuai_code}
        data = self._sp_bindpay_xml(dic)
        logger.error("#" * 50)
        logger.error(data)
        res = self._request(data, self.PAY_URL)
        logger.error(res.content)
        if res.status_code != 200 or "errorCode" in res.content:
            if "B.MGW.0120" in res.content:
                return {"ret_code":201221, "message":"银行与银行卡不匹配"}
            return {"ret_code":20122, "message":"服务器异常"}
        result = self._handle_pay_result(res)
        logger.error(result)
        if not result:
            return {"ret_code":20123, "message":"信息不匹配"}
        elif result['ret_code'] == 51:
            #余额不足也进行绑定卡信息
            self.bind_card(pay_info)
            return {"ret_code":201241, "message":result['message']}
        elif result['ret_code'] > 0:
            return {"ret_code":20124, "message":result['message']}
        device = split_ua(request)
        device_type = device['device_type']
        ms = self.handle_margin(result['amount'], result['order_id'], result['user_id'], util.get_client_ip(request), res.content, device_type)
        return ms

    @method_decorator(transaction.atomic)
    def handle_margin(self, amount, order_id, user_id, ip, response_content, device_type):
        pay_info = PayInfo.objects.filter(order_id=order_id).first()
        if not pay_info:
            return {"ret_code":20131, "message":"order not exist"}
        if pay_info.status == PayInfo.SUCCESS:
            return {"ret_code":0, "message":PayResult.DEPOSIT_SUCCESS, "amount":amount}

        pay_info.error_message = ""
        pay_info.response = response_content
        pay_info.response_ip = ip

        if pay_info.amount != amount:
            pay_info.status = PayInfo.FAIL
            pay_info.error_message += u' 金额不匹配'
            logger.error("orderId:%s amount:%s, response amount:%s" % (order_id, pay_info.amount, amount))
            rs = {"ret_code":20132, "message":PayResult.EXCEPTION}
        elif pay_info.user_id != user_id:
            pay_info.status = PayInfo.FAIL
            pay_info.error_message += u"用户不匹配"
            logger.error("orderId:%s 充值用户ID不匹配" % order_id)
            rs = {"ret_code":20133, "message":PayResult.EXCEPTION}
        else:
            pay_info.fee = self.FEE
            keeper = MarginKeeper(pay_info.user, pay_info.order.pk)
            margin_record = keeper.deposit(amount)
            pay_info.margin_record = margin_record
            pay_info.status = PayInfo.SUCCESS
            logger.error("orderId:%s success" % order_id)
            rs = {"ret_code":0, "message":"success", "amount":amount, "margin":margin_record.margin_current}

        pay_info.save()
        if rs['ret_code'] == 0:
            #保存卡信息到个人名下
            self.bind_card(pay_info)
           # card_no = pay_info.card_no
           # if len(card_no) > 10:
           #     exist_cards = Card.objects.filter(no=card_no, user=pay_info.user).first()
           #     if not exist_cards:
           #         card = Card()
           #         card.bank = pay_info.bank
           #         card.no = card_no
           #         card.user = pay_info.user
           #         card.is_default = False
           #         card.save()
            tools.despoit_ok(pay_info, device_type)
        OrderHelper.update_order(pay_info.order, pay_info.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
        return rs

    def bind_card(self, pay_info):
        #保存卡信息到个人名下
        card_no = pay_info.card_no
        if len(card_no) > 10:
            exist_cards = Card.objects.filter(no=card_no, user=pay_info.user).first()
            if exist_cards:
                return False
            card = Card()
            card.bank = pay_info.bank
            card.no = card_no
            card.user = pay_info.user
            card.is_default = False
            card.save()
            return True

    def pay_callback(self, request):
        logger.error(request.DATA)
        pass

def del_xmlns(xmlns, tag):
    for x in xmlns:
        if x in tag:
            return tag.replace(x, "")
    return tag

def xml2dict(node, res, xmlns):
    rep = {}

    tag = del_xmlns(xmlns, node.tag)
    if len(node):
        for x in list(node):
            tag_x = del_xmlns(xmlns, x.tag)
            rep[tag] = []
            value = xml2dict(x, rep[tag], xmlns)

            if len(x):
                value = {"value":rep[tag], "attr":x.attrib}
                res.append({tag_x:value})
            else:
                res.append(rep[tag][0])
    else:
        value = {}
        value = {"value":node.text.strip(), "attr":node.attrib}
        res.append({tag:value})
    return

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

    card =  Card.objects.filter(id=card_id, user=request.user).first()
    if not card:
        return {"ret_code":20042, "message":"该银行卡不存在"}
    #删除快捷支付信息
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

def list_bank(request):
    #banks = Bank.get_deposit_banks()
    banks = Bank.get_kuai_deposit_banks()
    rs = []
    for x in banks:
        obj = {"name":x.name, "gate_id":x.gate_id, "bank_id":x.kuai_code}
        if x.kuai_limit:
            obj.update(_handle_kuai_bank_limit(x.kuai_limit))
        rs.append(obj)
    if not rs:
        return {"ret_code":20051, "message":"没有可选择的银行"}
    return {"ret_code":0, "message":"ok", "banks":rs}

def _handle_kuai_bank_limit(limitstr):
    obj = {}
    try:
        first, second = limitstr.split("|")
        arr = first.split(",")
        obj['first_one'] = arr[0].split("=")[1]
        obj['first_day'] = arr[1].split("=")[1]
        arr1 = second.split(",")
        obj['second_one'] = arr1[0].split("=")[1]
        obj['second_day'] = arr1[1].split("=")[1]
    except:
        pass
    return obj

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
