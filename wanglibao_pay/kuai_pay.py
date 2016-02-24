#!/usr/bin/env python
# encoding:utf-8
from base64 import b64decode

import logging
import traceback
from M2Crypto import X509
from django.contrib.auth.models import User
from lxml import etree
import requests
from django.conf import settings
from django.forms import model_to_dict
from django.db import transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from wanglibao_pay import util
from wanglibao_pay.exceptions import ThirdPayError, VerifyError
from wanglibao_pay.models import PayInfo, PayResult, Bank, Card
from order.utils import OrderHelper
from order.models import Order
from wanglibao_margin.marginkeeper import MarginKeeper
from marketing import tools
from wanglibao_rest.utils import split_ua
from wanglibao_account.cooperation import CoopRegister
import re

logger = logging.getLogger(__name__)


class KuaiPay:
    FEE = 0

    def __init__(self):
        self.MER_ID = settings.KUAI_MER_ID
        self.MER_PASS = settings.KUAI_MER_PASS
        #self.PAY_URL = settings.KUAI_PAY_URL
        #self.QUERY_URL = settings.KUAI_QUERY_URL
        #self.DEL_URL = settings.KUAI_DEL_URL
        #self.DYNNUM_URL = settings.KUAI_DYNNUM_URL

        self.PAY_URL = settings.KUAI_PAY_URL + "/cnp/purchase"
        self.QUERY_URL = settings.KUAI_PAY_URL + "/cnp/pci_query"
        self.DEL_URL = settings.KUAI_PAY_URL + "/cnp/pci_del"
        self.DYNNUM_URL = settings.KUAI_PAY_URL + "/cnp/getDynNum"

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

        logger.critical(res.content)

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
                            card['gate_id'] = bank.gate_id
                            if bank.kuai_limit:
                                card.update(util.handle_kuai_bank_limit(bank.kuai_limit))
                        if "storablePan" in z:
                            card['storable_no'] = z["storablePan"]['value']
                    cards.append(card)
        if res_code != "00":
            return {"ret_code":20091, "message":message}
        if merchantId != self.MER_ID or customerId != str(request.user.id):
            return {"ret_code":20092, "message":"卡信息不匹配"}

        try:
            card_list = Card.objects.filter(user=request.user).select_related('bank').order_by('-last_update')
            bank_list = [c.bank.gate_id for c in card_list]
            cards_tmp = sorted(cards, key=lambda x: bank_list.index(x['gate_id']))
            cards = cards_tmp
        except:
            pass

        return {"ret_code":0, "message":"test", "cards":cards}

    def _handle_dynnum_result(self, res):
        if res.status_code != 200 or "errorCode" in res.content:
            return False

        logger.critical(res.content)

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
        logger.critical(data)
        logger.critical(res.content)

        if res.status_code != 200 or "errorCode" in res.content:
            return {"ret_code":20101, "message":"解除绑定失败"}
        result = self._handle_del_result(res)
        if not result:
            return {"ret_code":20102, "message":"解除信息不匹配"}
        elif result['ret_code']:
            return {"ret_code":20103, "message":result['message']}

        if len(card_no) == 10:
            Card.objects.filter(user=user, no__startswith=card_no[:6], no__endswith=card_no[-4:]).update(is_bind_kuai=False)
        else:
            Card.objects.filter(no=card_no, user=user).update(is_bind_kuai=False)

        return {"ret_code":0, "message":"ok"}

    def unbind_card(self, card_short_no, bank_kuai_code, user_id):
        dic = {"user_id": user_id, "bank_id": bank_kuai_code, "storable_no":
                card_short_no}
        data = self._sp_delbind_xml(dic)
        res = self._request(data, self.DEL_URL)
        logger.critical(data)
        logger.critical(res.content)

        if res.status_code != 200 or "errorCode" in res.content:
            return {"ret_code": 20101, "message": "解除绑定失败"}
        result = self._handle_del_result(res)
        if not result:
            return {"ret_code": 20102, "message": "解除信息不匹配"}
        elif result['ret_code']:
            return {"ret_code": 20103, "message": result['message']}

        card.is_bind_kuai = False
        if not card.is_bind_yee:
            card.is_the_one_card = False
        card.save()

        return {"ret_code": 0, "message": "ok"}

    def delete_bind_new(self, request, card, bank):
        storable_no = card.no if len(card.no) == 10 else card.no[:6] + card.no[-4:]

        return self.unbind_card(storable_no, card.bank.kuai_code,
                request.user.id)

    
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
                logger.critical("second pay info")
                logger.critical(u"%s"%data)
                url = self.PAY_URL
            else:
                data = self._sp_dynnum_xml(dic)
                logger.critical("first pay info")
                logger.critical(u"%s" % data)

                url = self.DYNNUM_URL

            res = self._request(data, url)

            if len(card_no) == 10:
                result = self._handle_pay_result(res)
                if not result:
                    return {"ret_code":201171, "message":"信息不匹配"}
                elif result['ret_code'] > 0:
                    pay_info.error_message = result['message']
                    pay_info.response = res.content
                    pay_info.save()
                    return {"ret_code":201181, "message":result['message']}
                device = split_ua(request)
                ms = self.handle_margin(result['amount'], result['order_id'], result['user_id'],
                                        util.get_client_ip(request), res.content, device, request)

                return ms
            else:
                token = self._handle_dynnum_result(res)
                if not token:
                    return {"ret_code":201172, "message":"信息不匹配"}
                elif token['ret_code'] != 0:
                    pay_info.error_message = token['message']
                    pay_info.save()
                    return {"ret_code":201182, "message":token['message']}

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
        logger.critical("#" * 50)
        logger.critical(data)
        res = self._request(data, self.PAY_URL)
        logger.critical(res.content)
        if res.status_code != 200 or "errorCode" in res.content:
            if "B.MGW.0120" in res.content:
                return {"ret_code":201221, "message":"银行与银行卡不匹配"}
            return {"ret_code":20122, "message":"服务器异常"}
        result = self._handle_pay_result(res)
        logger.critical(result)
        if not result:
            return {"ret_code":20123, "message":"信息不匹配"}
        elif result['ret_code'] == 51:
            #余额不足也进行绑定卡信息
            self.bind_card(pay_info, request)
            return {"ret_code":201241, "message":result['message']}
        elif result['ret_code'] > 0:
            return {"ret_code":20124, "message":result['message']}
        device = split_ua(request)
        ms = self.handle_margin(result['amount'], result['order_id'], result['user_id'],
                                util.get_client_ip(request), res.content, device, request)
        return ms

    @method_decorator(transaction.atomic)
    def handle_margin(self, amount, order_id, user_id, ip, response_content, device, request):
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
            logger.critical("orderId:%s amount:%s, response amount:%s" % (order_id, pay_info.amount, amount))
            rs = {"ret_code":20132, "message":PayResult.EXCEPTION}
        elif pay_info.user_id != user_id:
            pay_info.status = PayInfo.FAIL
            pay_info.error_message += u"用户不匹配"
            logger.critical("orderId:%s 充值用户ID不匹配" % order_id)
            rs = {"ret_code":20133, "message":PayResult.EXCEPTION}
        else:
            pay_info.fee = self.FEE
            keeper = MarginKeeper(pay_info.user, pay_info.order.pk)
            margin_record = keeper.deposit(amount)
            pay_info.margin_record = margin_record
            pay_info.status = PayInfo.SUCCESS
            logger.critical("orderId:%s success" % order_id)
            rs = {"ret_code": 0, "message":"success", "amount":amount, "margin":margin_record.margin_current,
                  'order_id': order_id}


        pay_info.save()
        if rs['ret_code'] == 0:
            #保存卡信息到个人名下
            self.bind_card(pay_info, request)
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
            try:
                # fix@chenweibi, add order_id
                tools.deposit_ok.apply_async(kwargs={"user_id": pay_info.user.id, "amount": pay_info.amount,
                                                     "device": device, "order_id": order_id})
            except:
                pass

            # 充值成功后，更新本次银行使用的时间
            if len(pay_info.card_no) == 10:
                Card.objects.filter(user=pay_info.user, no__startswith=pay_info.card_no[:6], no__endswith=pay_info.card_no[-4:]).update(last_update=timezone.now(), is_bind_kuai=True)
            else:
                Card.objects.filter(user=pay_info.user, no=pay_info.card_no).update(last_update=timezone.now(), is_bind_kuai=True)

        OrderHelper.update_order(pay_info.order, pay_info.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
        return rs

    def bind_card(self, pay_info, request):
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

            # try:
            #     # 处理第三方用户绑卡回调
            #     CoopRegister(request).process_for_binding_card(request.user)
            # except Exception, e:
            #     logger.error(e)

            return True

    def pay_callback(self, request):
        logger.critical(request.DATA)
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
        value = {"value":node.text.strip() if node.text else '', "attr":node.attrib}
        res.append({tag:value})
    return


class KuaiShortPay:
    FEE = 0

    def __init__(self):
        self.MER_ID = settings.KUAI_MER_ID
        self.MER_PASS = settings.KUAI_MER_PASS
        #self.PAY_URL = settings.KUAI_PAY_URL
        #self.QUERY_URL = settings.KUAI_QUERY_URL
        #self.DEL_URL = settings.KUAI_DEL_URL
        #self.DYNNUM_URL = settings.KUAI_DYNNUM_URL

        self.PAY_URL = settings.KUAI_PAY_URL + "/cnp/purchase"
        self.QUERY_URL = settings.KUAI_PAY_URL + "/cnp/pci_query"
        self.DEL_URL = settings.KUAI_PAY_URL + "/cnp/pci_del"
        self.DYNNUM_URL = settings.KUAI_PAY_URL + "/cnp/getDynNum"

        self.PAY_BACK_RETURN_URL = settings.KUAI_PAY_BACK_RETURN_URL
        self.PAY_TR3_SIGNATURE = settings.KUAI_PAY_TR3_SIGNATURE
        self.TERM_ID = settings.KUAI_TERM_ID

        self.headers = {"User-Agent":"wanglibao for 99bill client by lzj",
                        "Content-Type":"application/x-www-form-urlencoded"}
        self.xmlheader = '<?xml version="1.0" encoding="UTF-8"?>\n'
        self.pem = settings.KUAI_PEM_PATH
        self.signature_pem = settings.KUAI_SIGNATURE_PEM_PATH
        self.auth = (self.MER_ID, self.MER_PASS)
        self.ERR_CODE_WAITING = '222222'

    def _check_signature(self, str_content, signature):
        """
        使用self.pem指定的证书校验str_content的合法性
        :param str_content:
        :return:
        """
        cert = X509.load_cert(self.signature_pem)
        pubkey = cert.get_pubkey()
        pubkey.reset_context(md='sha1')
        pubkey.verify_init()
        pubkey.verify_update(str_content)
        result = pubkey.verify_final(b64decode(signature))
        if result != 1:
            raise VerifyError(self.signature_pem ,str_content, signature)
        else:
            return True

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
                    <tr3Url>%s</tr3Url>
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
        """ % (self.MER_ID, self.TERM_ID, self.PAY_BACK_RETURN_URL, dic['time'], dic['card_no'], dic['bank_id'],
               dic['amount'], dic['order_id'], dic['user_id'], dic['name'], dic['id_number'],
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

    def _sp_pay_tr4_xml(self, ref_number):
        """
        快捷支付TR4应答消息
        :param ref_number:
        :return:
        """
        xml = etree.XML("""
            <MasMessage xmlns="http://www.99bill.com/mas_cnp_merchant_interface">
                <version>1.0</version>
                <TxnMsgContent>
                    <txnType>PUR</txnType>
                    <interactiveStatus>TR4</interactiveStatus>
                    <merchantId>%s</merchantId>
                    <terminalId>%s</terminalId>
                    <refNumber>%s</refNumber>
                </TxnMsgContent>
            </MasMessage>
        """ % (self.MER_ID, self.TERM_ID, ref_number))
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

        logger.critical(res.content)

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
                            card['gate_id'] = bank.gate_id
                            if bank.kuai_limit:
                                card.update(util.handle_kuai_bank_limit(bank.kuai_limit))
                        if "storablePan" in z:
                            card['storable_no'] = z["storablePan"]['value']
                    cards.append(card)
        if res_code != "00":
            return {"ret_code":20091, "message":message}
        if merchantId != self.MER_ID or customerId != str(request.user.id):
            return {"ret_code":20092, "message":"卡信息不匹配"}

        try:
            card_list = Card.objects.filter(user=request.user).select_related('bank').order_by('-last_update')
            bank_list = [c.bank.gate_id for c in card_list]
            cards_tmp = sorted(cards, key=lambda x: bank_list.index(x['gate_id']))
            cards = cards_tmp
        except:
            pass

        return {"ret_code":0, "message":"test", "cards":cards}

    def query_bind_new(self, user_id):
        data = self._sp_bind_xml(user_id)
        res = self._request(data, self.QUERY_URL)
        if res.status_code != 200:
            return {"ret_code": -1, "message": "fetch error"}
        if "errorCode" in res.content:
            return {"ret_code": -1, "message": "fetch error"}
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
                    for z in y['pciInfo']['value']:
                        if "storablePan" in z:
                            cards.append(z["storablePan"]['value'])

        return {"ret_code": 0, "message": "success", "cards": cards}

    def _handle_dynnum_result(self, res):
        if res.status_code != 200 or "errorCode" in res.content:
            return False

        logger.critical(res.content)

        dic = self._result2dict(res.content)
        res_code = ''
        token = ''
        message = ''
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

    def handle_pay_result(self, res_content):
        dic = self._result2dict(res_content)
        mer_id = None
        message = ''
        ref_number = ''
        signature = ''
        user_id = 0
        bank_name = ''
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
                    if "refNumber" in x: ref_number = x['refNumber']['value'];continue
                    if 'signature' in x: signature = x['signature']['value'];continue
        if mer_id != self.MER_ID:
            return False

        # 必定返回order_id
        pay_info = PayInfo.objects.get(order_id=order_id)
        if not user_id:
            user_id = pay_info.user.id

        if not bank_name:
            bank_name = pay_info.bank.name

        result = {"ret_code": 0, "order_id":int(order_id), "user_id":int(user_id),
                    "bank_name":bank_name, "amount":amount, 'message': '成功',
                    'res_content': res_content, "ref_number": ref_number, 'signature': signature}
        res_code = res_code.lower()
        if res_code == "00":
            pass
        elif res_code == "t6":
            result.update({"ret_code": 1, "message":"验证码不正确"})
        elif res_code == "c0" or res_code == "68":
            result.update({"ret_code": 2, "message":"请耐心等候充值完成"})
        elif res_code == "og":
            result.update({"ret_code": 3, "message":"充值金额太大"})
        elif res_code == "tc":
            result.update({"ret_code": 4, "message":"不能使用信用卡"})
        elif res_code == "51":
            result.update({"ret_code": 51, "message":"余额不足"})
        elif res_code == 't3':
            result.update({'ret_code': 7, 'message': message})
        else:
            result.update({"ret_code": 5, "message":message})
        return result

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
        logger.critical(data)
        logger.critical(res.content)

        if res.status_code != 200 or "errorCode" in res.content:
            return {"ret_code":20101, "message":"解除绑定失败"}
        result = self._handle_del_result(res)
        if not result:
            return {"ret_code":20102, "message":"解除信息不匹配"}
        elif result['ret_code']:
            return {"ret_code":20103, "message":result['message']}
        return {"ret_code":0, "message":"ok"}

    def unbind_card(self, card_short_no, bank_kuai_code, user_id):
        dic = {"user_id": user_id, "bank_id": bank_kuai_code, "storable_no":
                card_short_no}
        data = self._sp_delbind_xml(dic)
        res = self._request(data, self.DEL_URL)
        logger.critical(data)
        logger.critical(res.content)

        if res.status_code != 200 or "errorCode" in res.content:
            return {"ret_code": 20101, "message": "解除绑定失败"}
        result = self._handle_del_result(res)
        if not result:
            return {"ret_code": 20102, "message": "解除信息不匹配"}
        elif result['ret_code']:
            return {"ret_code": 20103, "message": result['message']}

        cards = [c for c in Card.objects.filter(user_id=user_id).all() if
                 (c.no[:6] + c.no[-4:]) == card_short_no]
        for card in cards:
            card.is_bind_kuai = False
            if not card.is_bind_yee:
                card.is_the_one_card = False
            card.save()

        return {"ret_code": 0, "message": "ok"}

    def delete_bind_new(self, request, card, bank):
        storable_no = card.no if len(card.no) == 10 else card.no[:6] + card.no[-4:]

        return self.unbind_card(storable_no, card.bank.kuai_code,
                request.user.id)

    @method_decorator(transaction.atomic)
    def _handle_third_pay_error(self, error, user_id, payinfo_id, order_id):
        logger.exception(error)
        user = User.objects.get(id=user_id)
        # t3错误，一个银行不能绑定多张卡或者未绑定
        if error.code == 201183:
            self.sync_bind_card(user)
        pay_info = PayInfo.objects.select_for_update().get(id=payinfo_id)

        if pay_info.status == PayInfo.PROCESSING:
            order = Order.objects.get(id=order_id)

            if isinstance(error, ThirdPayError):
                error_code = error.code
                is_inner_error = False
            else:
                error_code = 20119
                is_inner_error = True
            error_message = error.message
            pay_info.save_error(error_code=error_code, error_message=error_message, is_inner_error=is_inner_error)
            OrderHelper.update_order(order, user, pay_info=model_to_dict(pay_info), status=pay_info.status)
            return {"ret_code": error_code, "message": error_message, 'order_id':order_id, 'pay_info_id':payinfo_id}
        else:
            # 若TR3已经完成该交易，直接返回结果
            return {"ret_code": pay_info.error_code, "message": pay_info.error_message,
                    'order_id':order_id, 'pay_info_id':payinfo_id}

    def pre_pay(self, user, amount, card_no, input_phone, gate_id, device_type, ip, request, exit_for_test=False):
        # if not user.wanglibaouserprofile.id_is_valid:
        #     return {"ret_code":20111, "message":"请先进行实名认证"}

        # amount = request.DATA.get("amount", "").strip()
        # card_no = request.DATA.get("card_no", "").strip()
        # input_phone = request.DATA.get("phone", "").strip()
        # gate_id = request.DATA.get("gate_id","").strip()

        # if not amount or not card_no:
        #     return {"ret_code":20112, 'message':'信息输入不完整'}
        # if len(card_no) > 10 and (not input_phone or not gate_id):
        #     return {"ret_code":20112, 'message':'信息输入不完整'}

        #if card_no[0] in ("3", "4", "5"):
        #    return {"ret_code":20113, "message":"不能使用信用卡"}

        # try:
        #     float(amount)
        # except:
        #     return {"ret_code":20114, 'message':'金额格式错误'}

        # amount = util.fmt_two_amount(amount)
        #if amount < 100 or amount % 100 != 0 or len(str(amount)) > 20:
        #if amount < 10 or amount % 1 != 0 or len(str(amount)) > 20:
        # if amount < 10 or len(str(amount)) > 20:
        #     return {"ret_code":20115, 'message':'充值须大于等于10元'}

        # user = request.user
        profile = user.wanglibaouserprofile
        card = None
        bank = None
        if gate_id:
            bank = Bank.objects.filter(gate_id=gate_id).first()
            if not bank or not bank.kuai_code.strip():
                return {"ret_code":201151, "message":"不支持该银行"}
        #fix bink new bank card warning message
        #if len(card_no) == 10:
            #card = Card.objects.filter(user=user, no__startswith=card_no[:6], no__endswith=card_no[-4:]).first()
        #else:
            #card = Card.objects.filter(no=card_no, user=user).first()
            #if bank and card and bank != card.bank:
                #return {"ret_code":201153, "message":"银行卡与银行不匹配"}

        if not card:
            card = self.add_card_unbind(user, card_no, bank, request)

        if not card and not bank:
            return {"ret_code":201152, "message":"卡号不存在或银行不存在"}

        pay_info = PayInfo()
        pay_info.amount = amount
        pay_info.total_amount = amount
        pay_info.type = PayInfo.DEPOSIT
        pay_info.status = PayInfo.INITIAL
        pay_info.user = user
        pay_info.channel = "kuaipay"

        # pay_info.request_ip = util.get_client_ip(request)
        pay_info.request_ip = ip
        pay_info.device = device_type
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

        if exit_for_test:
            return {"order_id":order.id}

        try:
            dic = {"user_id":user.id, "order_id":order.id, "id_number":profile.id_number.upper(),
                    "phone":input_phone, "name":profile.name, "amount":amount,
                    "card_no":pay_info.card_no}

            if len(card_no) == 10:
                dic['storable_no'] = card_no
                dic['bank_id'] = card.bank.kuai_code
                dic['time'] = timezone.now().strftime("%Y%m%d%H%M%S")

                self._request_dict = dic
                data = self._sp_qpay_xml(dic)
                logger.critical("second pay info")
                logger.critical(u"%s"%data)
                url = self.PAY_URL
            else:
                self._request_dict = dic
                data = self._sp_dynnum_xml(dic)
                logger.critical("first pay info")
                logger.critical(u"%s" % data)

                url = self.DYNNUM_URL

            res = self._request(data, url)
            logger.critical("kuai pay request result")
            logger.critical(res.content)
            if len(card_no) == 10:
                result = self.handle_pay_result(res.content)
                if not result:
                    raise ThirdPayError(201171, '信息不匹配')
                elif result['ret_code'] >0:
                    if result['ret_code'] == 2:
                        raise ThirdPayError(self.ERR_CODE_WAITING, result['message'])
                    elif result['ret_code'] == 7:
                        raise ThirdPayError(201183, result['message'])
                    else:
                        raise ThirdPayError(201181, result['message'])
                # device = split_ua(request)
                ms = self.handle_margin(result['amount'], result['order_id'], result['user_id'], ip, res.content,
                                        device_type, request)

                return ms
            else:
                token = self._handle_dynnum_result(res)
                if not token:
                    raise ThirdPayError(201172, '信息不匹配')
                elif token['ret_code'] != 0:
                    # if token['ret_code'] == 2:
                    #     raise ThirdPayError(self.ERR_CODE_WAITING, token['message'])
                    # else:
                    raise ThirdPayError(201182, token['message'])

                return {"ret_code":0, "message":"ok", "order_id":order.id, "token":token['token']}
        except Exception, e:
            return self._handle_third_pay_error(e, user.id, pay_info.id, order.id)

    def dynnum_bind_pay(self, user, vcode, order_id, token, input_phone, device_type, ip, request):
        # vcode = request.DATA.get("vcode", "").strip()
        # order_id = request.DATA.get("order_id", "").strip()
        # token = request.DATA.get("token", "").strip()
        # input_phone = request.DATA.get("phone", "").strip()

        # if not order_id.isdigit():
        #     return {"ret_code":20125, "message":"订单号错误"}

        pay_info = PayInfo.objects.filter(order_id=order_id).first()
        if not pay_info or pay_info.status == PayInfo.SUCCESS:
            return {"ret_code":20121, "message":"订单不存在或已支付成功"}
        # user = request.user
        profile = user.wanglibaouserprofile

        try:
            dic = {"user_id":user.id, "order_id":order_id, "id_number":profile.id_number.upper(),
                    "phone":input_phone, "name":profile.name, "amount":pay_info.amount,
                    "time":pay_info.create_time.strftime("%Y%m%d%H%M%S"), "vcode":vcode,
                    "card_no":pay_info.card_no, "token":token, "bank_id":pay_info.bank.kuai_code}
            self._request_dict = dic
            data = self._sp_bindpay_xml(dic)
            logger.critical("#" * 50)
            logger.critical(data)
            res = self._request(data, self.PAY_URL)
            logger.critical(res.content)
            if res.status_code != 200 or "errorCode" in res.content:
                if "B.MGW.0120" in res.content:
                    raise ThirdPayError(201221, "银行与银行卡不匹配")
                raise ThirdPayError(20122, "服务器异常")
            result = self.handle_pay_result(res.content)
            if not result:
                raise ThirdPayError(20123, "信息不匹配")
            # elif result['ret_code'] == 51:
            #     # #余额不足也进行绑定卡信息
            #     # self.bind_card(pay_info)
            #     raise ThirdPayError(201241, result['message'])
            elif result['ret_code'] > 0:
                if result['ret_code'] == 2:
                    # todo add test
                    raise ThirdPayError(self.ERR_CODE_WAITING, result['message'])
                else:
                    raise ThirdPayError(result['ret_code'], result['message'])
                return {"ret_code":20124, "message":result['message']}
            # device = split_ua(request)
            ms = self.handle_margin(result['amount'],
                                    result['order_id'],
                                    result['user_id'],
                                    ip,
                                    res.content,
                                    device_type,
                                    request)
            return ms
        except Exception, e:
            return self._handle_third_pay_error(e, user.id, pay_info.id, order_id)

    @method_decorator(transaction.atomic)
    def handle_margin(self, amount, order_id, user_id, ip, response_content, device_type, request):
        # todo add test
        pay_info = PayInfo.objects.select_for_update().filter(order_id=order_id).first()
        if not pay_info:
            return {"ret_code":20131, "message":"order not exist", "amount": amount}
        if pay_info.status == PayInfo.SUCCESS:
            return {"ret_code":0, "message":PayResult.DEPOSIT_SUCCESS, "amount": amount}

        pay_info.error_message = ""
        pay_info.response = response_content
        pay_info.response_ip = ip
        if pay_info.amount != amount:
            pay_info.status = PayInfo.FAIL
            pay_info.error_message += u' 金额不匹配'
            logger.critical("orderId:%s amount:%s, response amount:%s" % (order_id, pay_info.amount, amount))
            rs = {"ret_code":20132, "message":PayResult.EXCEPTION}
        elif pay_info.user_id != user_id:
            pay_info.status = PayInfo.FAIL
            pay_info.error_message += u"用户不匹配"
            logger.critical("orderId:%s 充值用户ID不匹配" % order_id)
            rs = {"ret_code":20133, "message":PayResult.EXCEPTION}
        else:
            pay_info.fee = self.FEE
            keeper = MarginKeeper(pay_info.user, pay_info.order.pk)
            margin_record = keeper.deposit(amount)
            pay_info.margin_record = margin_record
            pay_info.status = PayInfo.SUCCESS
            logger.critical("orderId:%s success" % order_id)
            rs = {"ret_code": 0, "message": "success", "amount": amount, "margin": margin_record.margin_current,
                  "order_id": order_id}

        pay_info.save()
        if rs['ret_code'] == 0:
            # #保存卡信息到个人名下
            # self.bind_card(pay_info)

            try:
                # fix@chenweibi, add order_id
                tools.deposit_ok.apply_async(kwargs={"user_id": pay_info.user.id, "amount": pay_info.amount,
                                                     "device": device_type, "order_id": order_id})
                CoopRegister(request).process_for_recharge(pay_info.user, pay_info.order_id)
            except:
                logger.exception('kuai_pay_deposit_call_back_failed')

            # 充值成功后，更新本次银行使用的时间
            if len(pay_info.card_no) == 10:
                Card.objects.filter(user=pay_info.user, no__startswith=pay_info.card_no[:6], no__endswith=pay_info.card_no[-4:]).update(last_update=timezone.now(), is_bind_kuai=True)
            else:
                Card.objects.filter(user=pay_info.user, no=pay_info.card_no).update(last_update=timezone.now(), is_bind_kuai=True)

        OrderHelper.update_order(pay_info.order, pay_info.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
        return rs

    def bind_card(self, pay_info):
        """
        该方法已经废弃，使用add_card_unbind
        :param pay_info:
        :return:
        """
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

    def _pay_callback_check_requirement(self, pay_info, user_id, amount, ref_number, res_content, signature):
        """
        3重验证：
        1.signature正确
        2.回调的信息和pay_info中保存的一致
        3.若为失败状态，失败代码为2;或是状态为处理中，
        :param pay_info:
        :param signature,支付渠道的签名验证码
        :return:
        """
        # if signature != self.PAY_TR3_SIGNATURE:
        #     return False
        str_to_sign = re.sub(r'<signature>.*</signature>', '', res_content)
        self._check_signature(str_to_sign, signature)

        if not ref_number:
            return False

        if pay_info.user.id != user_id or pay_info.amount != amount:
            return False

        if pay_info.status == PayInfo.FAIL and pay_info.error_code == self.ERR_CODE_WAITING:
            # 返回码c0,68会被_handle_pay_result处理为2
            return True

        if pay_info.status == PayInfo.PROCESSING:
            # 当TR2未收到时
            return True

        return False


    def pay_callback(self, user_id, amount, res_code, res_message, order_id, ref_number, res_content,
                     signature, request):
        """
        快钱快捷支付TR3应答API。
        TR1中会将该api的地址传给快钱，快钱在TR3阶段回调该API。
        TR1中需要将“Always TR3”标志位设置为“是”，以便打开TR3回调。否则在TR2应答为交易成功、失败时（应答码非C0或是68），不会发送TR3.
        实现功能：
            1.如果TR2阶段的应答码是C0或是68（等待最终交易结果），可以通过TR3的应答确认最终的交易状态
            2.如果由于服务停止等原因，导致TR2应答遗漏，可以通过TR3的应答来确认最终的交易状态
        :param ref_number: 第三方支付的订单号，不是我方订单号
        :return:
        """
        # 检查条件
        with transaction.atomic():
            pay_info = PayInfo.objects.select_for_update().get(order_id=order_id)
            try:
                if self._pay_callback_check_requirement(pay_info, user_id, amount, ref_number, res_content, signature):
            # 处理TR3: 若失败，保存出错信息；若成功，handle_margin, 保存成功的返回
                    if res_code == 0:
                        # 第三方不管我方处理的结果，只在乎是否发送TR4，所以不用处理返回
                        self.handle_margin(amount, pay_info.order.id, user_id,
                                           pay_info.request_ip, res_content, pay_info.device, request)
                    else:
                        raise ThirdPayError(res_code, res_message)
            except Exception, e:
                self._handle_third_pay_error(e, user_id, pay_info.id, pay_info.order.id)

        # TR4应答
        self._request_dict = dict(user_id=user_id, order_id=order_id, amount=amount)
        return self._sp_pay_tr4_xml(ref_number)
        # return '<?xml version="1.0" encoding="UTF-8"?><MasMessage xmlns="http://www.99bill.com/mas_cnp_merchant_interface"><version>1.0</version><TxnMsgContent><txnType>PUR</txnType><interactiveStatus>TR4</interactiveStatus><merchantId>%s</merchantId><terminalId>%s</terminalId><refNumber>%s</refNumber></TxnMsgContent></MasMessage>'%(self.MER_ID, self.TERM_ID, ref_number)

    def add_card_unbind(self, user, card_no, bank, request):
        """ 保存卡信息到个人名下，不绑定任何渠道 """
        if len(card_no) == 10:
            card = Card.objects.filter(user=user, no__startswith=card_no[:6], no__endswith=card_no[-4:]).first()
        else:
            card = Card.objects.filter(no=card_no, user=user).first()

        add_card = False
        if not card:
            card = Card()
            card.user = user
            card.no = card_no
            card.is_default = False

            add_card = True

        card.bank = bank
        card.save()

        # if add_card:
        #     try:
        #         # 处理第三方用户绑卡回调
        #         CoopRegister(request).process_for_binding_card(request.user)
        #     except Exception, e:
        #         logger.error(e)

        return card

    def sync_bind_card(self, user):
        # 查询块钱已经绑定卡
        res = self.query_bind_new(user.id)
        if res['ret_code'] != 0: return res
        if 'cards' in res:
            kuai_card_no_list = []
            for car in res['cards']:
                card = Card.objects.filter(user=user, no__startswith=car[:6], no__endswith=car[-4:]).first()
                if card:
                    kuai_card_no_list.append(card.no)
            # suppoort kuai_card_no_list = []
            Card.objects.filter(user=user, no__in=kuai_card_no_list).update(is_bind_kuai=True)
            Card.objects.filter(user=user).exclude(no__in=kuai_card_no_list).update(is_bind_kuai=False)
            Card.objects.filter(is_bind_kuai=False, is_bind_yee=False,
                                is_the_one_card=True).update(is_the_one_card=False)
