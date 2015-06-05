#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import decimal
import logging
from django.forms import model_to_dict
from django.utils.decorators import method_decorator
from django.utils import timezone
import traceback
#from marketing.helper import RewardStrategy
import requests
from order.utils import OrderHelper
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_pay.models import PayInfo, Bank, Card
from wanglibao_pay.pay import Pay
import socket
from django.conf import settings
from django.db import transaction
from wanglibao_pay.util import get_client_ip, fmt_two_amount, handle_kuai_bank_limit
from wanglibao_pay.views import PayResult
from marketing import tools
import xml.etree.ElementTree as ET
#from wanglibao_sms import messages
#from django.utils import timezone
#from wanglibao_account import message as inside_message
from wanglibao_rest.utils import split_ua
from order.models import Order

logger = logging.getLogger(__name__)


class SignException(Exception):
    pass


class HuifuPay(Pay):
    PAY_BACK_RETURN_URL = settings.PAY_BACK_RETURN_URL
    PAY_RET_URL = settings.PAY_RET_URL
    WITHDRAW_BACK_RETURN_URL = settings.WITHDRAW_BACK_RETURN_URL
    MER_ID = settings.MER_ID
    CUSTOM_ID = settings.CUSTOM_ID
    HOST = settings.SIGN_HOST
    PORT = settings.SIGN_PORT
    PAY_URL = settings.PAY_URL
    WITHDRAW_URL = settings.WITHDRAW_URL

    FEE = decimal.Decimal(0)

    VERSION = '10'

    PAY_FIELDS = ['Version', 'CmdId', 'MerId', 'OrdId', 'OrdAmt', 'CurCode', 'Pid', 'RetUrl', 'MerPriv',
                  'GateId', 'UsrMp', 'DivDetails', 'OrderType', 'PayUsrId', 'PnrNum', 'BgRetUrl', 'IsBalance', 'ChkValue']
    WITHDRAW_FIELDS = ['Version', 'CmdId', 'CustId', 'SubAcctId', 'OrdId', 'OrdAmt', 'MerPriv', 'AcctName', 'BankId',
                       'AcctId', 'IsSubAcctId', 'UserMp', 'CertType', 'CertId', 'PrType', 'ProvName', 'AreaName', 'BranchName',
                       'PrPurpose', 'RetUrl', 'Charset', 'ChkType', 'ChkValue']
    BATCH_QUERY_FIELDS = ['Version', 'CmdId', 'CustId', 'BeginDate', 'EndDate', 'PageNum', 'Charset', 'ChkType', 'ChkValue']
    SIGN_REQUEST = 'S'
    VALIDATE_REQUEST = 'V'
    CHARSET = 'UTF8'
    CHECK_TYPE = 'R'

    @classmethod
    def __format_len(cls, length):
        return "{:0>4d}".format(length)

    def __get_package(self, raw_data, fields, type):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HuifuPay.HOST, HuifuPay.PORT))
        raw_str = u''
        for field in fields:
            if field != 'ChkValue' and field in raw_data:
                if raw_data[field]:
                    raw_str += unicode(raw_data[field])

        if type == HuifuPay.VALIDATE_REQUEST:
            raw_str += raw_data['ChkValue']

        raw_len = self.__format_len(len(raw_str.encode(HuifuPay.CHARSET)))
        package = type + HuifuPay.MER_ID + raw_len + raw_str
        package_len = self.__format_len(len(package.encode(HuifuPay.CHARSET)))
        package = (package_len + package).encode(HuifuPay.CHARSET)

        self.sock.sendall(package)

        sign = ''
        while 1:
            data = self.sock.recv(4096)
            if not data:
                break
            else:
                sign += data

        self.sock.close()
        return sign

    def sign_data(self, raw_data, fields):
        package = self.__get_package(raw_data, fields, HuifuPay.SIGN_REQUEST)
        package_len = len(package)
        if package_len < 15:
            raise SignException("Unformatted response: " + package)

        code = package[11:15]
        if code != '0000':
            raise SignException("Error Code: " + code)
        return package[15:271]

    def verify_sign(self, post, fields):
        package = self.__get_package(post, fields, HuifuPay.VALIDATE_REQUEST)
        package_len = len(package)
        if package_len != 15:
            raise SignException("Unformatted response: " + package)

        code = package[11:15]
        return code != '0000'

    def pay(self, post):
        post['Version'] = HuifuPay.VERSION
        post['BgRetUrl'] = HuifuPay.PAY_BACK_RETURN_URL
        post['RetUrl'] = HuifuPay.PAY_RET_URL
        post['CmdId'] = 'Buy'
        post['MerId'] = HuifuPay.MER_ID
        post['IsBalance'] = 'Y'

        post['ChkValue'] = self.sign_data(post, HuifuPay.PAY_FIELDS)
        return {
            'url': HuifuPay.PAY_URL + '/gar/RecvMerchant.do',
            'post': post
        }

    def withdraw(self, post):
        post['Version'] = HuifuPay.VERSION
        post['CmdId'] = 'prTrans'
        post['CustId'] = HuifuPay.CUSTOM_ID
        post['PrType'] = 'P'
        post['RetUrl'] = HuifuPay.WITHDRAW_BACK_RETURN_URL
        post['Charset'] = HuifuPay.CHARSET
        post['ChkType'] = HuifuPay.CHECK_TYPE


        post['ChkValue'] = self.sign_data(post, HuifuPay.WITHDRAW_FIELDS)
        return {
            'url': HuifuPay.WITHDRAW_URL + '/extUrl/prTransHttp',
            'post': post
        }

    def batch_query(self, post):
        post['Version'] = HuifuPay.VERSION
        post['CmdId'] = 'prBatchQuery'
        post['CustId'] = HuifuPay.CUSTOM_ID
        post['Charset'] = HuifuPay.CHARSET
        post['ChkType'] = HuifuPay.CHECK_TYPE

        post['ChkValue'] = self.sign_data(post, HuifuPay.BATCH_QUERY_FIELDS)

        r = requests.post(HuifuPay.WITHDRAW_URL + '/extUrl/prBatchInfo', post)
        root = ET.fromstring(r.text.encode('utf-8'))
        for result in root.findAll('result'):
            data = dict()
            for child in result:
                data[child.tag] = child.text

    @classmethod
    @method_decorator(transaction.atomic)
    def handle_withdraw_result(cls, data):
        order_id = data.get('OrdId', '')
        try:
            pay_info = PayInfo.objects.select_for_update().get(pk=order_id)
        except PayInfo.DoesNotExist:
            logger.warning('Order not found, order id: ' + order_id + ', response: ' + str(data))
            return PayResult.EXCEPTION

        if pay_info.status == PayInfo.FAIL:
            return PayResult.WITHDRAW_FAIL

        pay_info = PayInfo.objects.select_for_update().get(pk=order_id)
        pay_info.response = str(data)
        pay_info.error_code = data.get('RespCode', '')
        pay_info.error_message = data.get('RespDesc', '')
        transaction_status = data.get('TransStat', '')

        keeper = MarginKeeper(pay_info.user, pay_info.order.pk)

        try:
            pay = HuifuPay()
            if pay.verify_sign(data, HuifuPay.WITHDRAW_FIELDS):
                if data['RespCode'] == '000':
                    if transaction_status == 'S':
                        if pay_info.status != PayInfo.SUCCESS:
                            keeper.withdraw_ack(pay_info.total_amount)
                        pay_info.status = PayInfo.SUCCESS
                        result = PayResult.WITHDRAW_SUCCESS
                    elif transaction_status == 'I':
                        pay_info.status = PayInfo.ACCEPTED
                        result = PayResult.WITHDRAW_SUCCESS
                    elif transaction_status == 'F':
                        is_already_successful = False
                        if pay_info.status == 'S':
                            is_already_successful = True
                        pay_info.status = PayInfo.FAIL
                        result = PayResult.WITHDRAW_FAIL
                        keeper.withdraw_rollback(pay_info.total_amount, u'', is_already_successful)
                else:
                    pay_info.status = PayInfo.FAIL
                    result = PayResult.WITHDRAW_FAIL
                    keeper.withdraw_rollback(pay_info.total_amount)
            else:
                pay_info.status = PayInfo.EXCEPTION
                result = PayResult.EXCEPTION
                pay_info.error_message = 'Invalid signature'
                logger.fatal('invalid signature. order id: %s', str(pay_info.pk))
        except(socket.error, SignException) as e:
            result = PayResult.EXCEPTION
            pay_info.status = PayInfo.EXCEPTION
            pay_info.error_message = str(e)
            logger.fatal('unexpected error. order id: %s. exception: %s', str(pay_info.pk), str(e))

        pay_info.save()
        OrderHelper.update_order(pay_info.order, pay_info.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
        return result

    @classmethod
    @method_decorator(transaction.atomic)
    def handle_pay_result(cls, request):
        # TODO Add a log

        flag = False

        order_id = request.POST.get('OrdId', '')
        try:
            pay_info = PayInfo.objects.select_for_update().get(pk=order_id)
        except PayInfo.DoesNotExist:
            logger.warning('Order not found, order id: ' + order_id + ', response: ' + request.body)
            return PayResult.EXCEPTION

        if pay_info.status == PayInfo.SUCCESS:
            return PayResult.DEPOSIT_SUCCESS

        amount = request.POST.get('OrdAmt', '')
        code = request.POST.get('RespCode', '')
        message = request.POST.get('ErrMsg', '')
        pay_info.error_code = code
        pay_info.error_message = message
        pay_info.response = request.body
        pay_info.response_ip = get_client_ip(request)

        result = u''
        try:
            pay = HuifuPay()
            if pay.verify_sign(request.POST.dict(), HuifuPay.PAY_FIELDS):
                if pay_info.amount != decimal.Decimal(amount):
                    pay_info.status = PayInfo.FAIL
                    pay_info.error_message += u' 金额不匹配'
                    logger.error('Amount mismatch, order id: %s request amount: %f response amount: %s',
                                 order_id, float(pay_info.amount), amount)
                    result = PayResult.EXCEPTION
                else:
                    if code == '000000':
                        keeper = MarginKeeper(pay_info.user, pay_info.order.pk)
                        margin_record = keeper.deposit(amount)
                        pay_info.margin_record = margin_record
                        pay_info.status = PayInfo.SUCCESS
                        result = PayResult.DEPOSIT_SUCCESS
                        phone = pay_info.user.wanglibaouserprofile.phone

                        flag = True
                    else:
                        pay_info.status = PayInfo.FAIL
                        result = PayResult.DEPOSIT_FAIL
            else:
                pay_info.error_message = 'Invalid signature. Order id: ' + order_id
                logger.error(pay_info.error_message)
                pay_info.status = PayInfo.EXCEPTION
                result = PayResult.EXCEPTION
        except (socket.error, SignException) as e:
            pay_info.error_message = str(e)
            pay_info.status = PayInfo.EXCEPTION
            logger.fatal('sign error! order id: ' + order_id + ' ' + str(e))
            result = PayResult.EXCEPTION

        pay_info.save()

        if flag:
            device = split_ua(request)
            tools.despoit_ok(pay_info, device['device_type'])
            """
            # 迅雷活动, 12.8 首次充值
            start_time = timezone.datetime(2014, 12, 7)
            if PayInfo.objects.filter(user=pay_info.user, type='D', update_time__gt=start_time,
                                      status=PayInfo.SUCCESS).count() == 1:
                rs = RewardStrategy(pay_info.user)
                rs.reward_user(u'三天迅雷会员')


            title, content = messages.msg_pay_ok(amount)
            inside_message.send_one.apply_async(kwargs={
                "user_id": pay_info.user.id,
                "title": title,
                "content": content,
                "mtype": "activityintro"
            })
            """

        OrderHelper.update_order(pay_info.order, pay_info.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
        return result


class HuifuShortPay:
    FEE = 0

    def __init__(self):
        import hashlib
        self.MER_ID = settings.HUI_SHORT_MER_ID
        self.OPER_ID = settings.HUI_SHORT_OPER_ID

        m = hashlib.md5()
        m.update(settings.HUI_SHORT_LOGIN_PWD)
        self.OPER_PWD = m.hexdigest()

        self.PAY_URL = settings.HUI_SHORT_PAY_URL
        self.BIND_URL = settings.HUI_SHORT_BIND_URL
        self.DEBIND_URL = settings.HUI_SHORT_DEBIND_URL
        self.SIGN_HOST = settings.HUI_SHORT_SIGN_HOST
        self.SIGN_PORT = settings.HUI_SHORT_SIGN_PORT

        self.BIND_FIELDS = ['Version', 'CmdId', 'MerId', 
                            'OperId', 'LoginPwd', 'CardNo', 
                            'OpenAcctName', 'BankCode', 'CertType', 
                            'CertId', 'UsrMp', 'CardType', 'ChkValue']

        self.PAY_FIELDS = ["Version", "CmdId", "MerId", 
                            "OperId", "CardNo", "OpenAcctName", 
                            "CertType", "CertId", "UsrMp", "TransAmt",
                            "CardType", "Remark", "ChkValue"]

        self.DEBIND_FIELDS = ['Version', 'CmdId', 'MerId',
                              'OperId', 'CardNo', 'ChkValue']

        self.REGISTER_FIELDS = ['Version', 'CmdId', 'MerId',
                                'MerUsrId', 'UsrMp', 'IdType',
                                'IdNo', 'UsrName', 'UsrPwd',
                                'UsrRole', 'UsrShortName', 'IsCertChk',
                                'IsActivate', 'IsOperRecv', 'IsSignAutoPay',
                                'IsPrivateCash', 'UsrId', 'OperEmail',
                                'ProvId', 'AreaId', 'ChkValue']

    @classmethod
    def __format_len(cls, length):
        return "{:0>4d}".format(length)

    def __get_package(self, raw_data, fields, type):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.SIGN_HOST, self.SIGN_PORT))
        raw_str = u''
        for field in fields:
            if field != 'ChkValue' and field in raw_data:
                if raw_data[field]:
                    raw_str += unicode(raw_data[field])

        if type == HuifuPay.VALIDATE_REQUEST:
            raw_str += raw_data['ChkValue']

        raw_len = self.__format_len(len(raw_str.encode(HuifuPay.CHARSET)))
        package = type + self.MER_ID + raw_len + raw_str
        package_len = self.__format_len(len(package.encode(HuifuPay.CHARSET)))
        package = (package_len + package).encode(HuifuPay.CHARSET)

        self.sock.sendall(package)

        sign = ''
        while 1:
            data = self.sock.recv(4096)
            if not data:
                break
            else:
                sign += data

        self.sock.close()
        return sign

    def sign_data(self, raw_data, fields):
        package = self.__get_package(raw_data, fields, HuifuPay.SIGN_REQUEST)
        package_len = len(package)
        if package_len < 15:
            raise SignException("Unformatted response: " + package)

        code = package[11:15]
        if code != '0000':
            raise SignException("Error Code: " + code)
        return package[15:271]

    def _request_huifu(self, url, data):
        r = requests.post(url, data)
        print 'url>>>', url
        print 'data>>>', data
        print 'response>>>', r.text
        res_arr = map((lambda x: x.split('=')), r.text.rstrip('\r\n').split('\r\n'))
        return dict([(arr[0], arr[1]) for arr in res_arr])

    def _common_post_fields(self):
        post = dict()
        post['Version'] = '10'
        post['MerId'] = self.MER_ID

        return post

    def _bind_card_huifu(self, user, bank, card_no):
        post = dict()
        post.update(self._common_post_fields())

        post['OperId'] = '{mer_id}{phone}'.format(mer_id=self.MER_ID, phone=user.wanglibaouserprofile.phone)
        post['CardNo'] = card_no
        post['OpenAcctName'] = user.wanglibaouserprofile.name
        post['BankCode'] = bank.huifu_bind_code
        post['CertType'] = '00'
        post['CertId'] = user.wanglibaouserprofile.id_number
        post['UsrMp'] = user.wanglibaouserprofile.phone
        post['CardType'] = 'D'
        post['CmdId'] = 'WHBindCard'
        post['LoginPwd'] = self.OPER_PWD
        post['ChkValue'] = self.sign_data(post, self.BIND_FIELDS)

        return self._request_huifu(self.BIND_URL, post)

    def _card_pay_huifu(self, user, amount, card_no):
        """ 代扣充值 """
        post = dict()
        post.update(self._common_post_fields())
        post['OperId'] = '{mer_id}{phone}'.format(mer_id=self.MER_ID, phone=user.wanglibaouserprofile.phone)
        post['CardNo'] = card_no
        post['OpenAcctName'] = user.wanglibaouserprofile.name
        post['CertType'] = '00'
        post['CertId'] = user.wanglibaouserprofile.id_number
        post['UsrMp'] = user.wanglibaouserprofile.phone
        post['CardType'] = 'D'
        post['TransAmt'] = amount
        post['Remark'] = u"汇付天下快捷支付"
        post['CmdId'] = 'WHDebitDeductSave'
        post['LoginPwd'] = self.OPER_PWD
        post['ChkValue'] = self.sign_data(post, self.PAY_FIELDS)

        return self._request_huifu(self.PAY_URL, post)

    def _open_account_huifu(self, user):
        """ 开户 """
        post = dict()
        post.update(self._common_post_fields())
        post['CmdId'] = 'Regist'
        post['MerUsrId'] = user.wanglibaouserprofile.phone
        post['UsrMp'] = user.wanglibaouserprofile.phone
        post['IdType'] = '01'
        post['IdNo'] = user.wanglibaouserprofile.id_number
        post['UsrName'] = user.wanglibaouserprofile.name
        post['UsrPwd'] = self.OPER_PWD
        post['UsrRole'] = '12' #用户所属角色的角色号
        post['UsrShortName'] = user.wanglibaouserprofile.name
        post['IsCertChk'] = 'Y' #是否实名
        post['IsActivate'] = 'Y' #是否激活
        post['IsOperRecv'] = 'Y' #是否开通收款户
        post['IsSignAutoPay'] = 'Y' #是否签约自动扣款
        post['IsPrivateCash'] = 'Y' #是否允许对私结算
        post['ChkValue'] = self.sign_data(post, self.REGISTER_FIELDS)

        return self._request_huifu(self.PAY_URL, post)

    def _unbind_card_huifu(self, user, card_no):
        """ 解绑 """
        post = dict()
        post.update(self._common_post_fields())
        post['CardNo'] = card_no
        post['OperId'] = '{mer_id}{phone}'.format(mer_id=self.MER_ID, phone=user.wanglibaouserprofile.phone)
        post['CmdId'] = 'WHCancelBindCard'
        post['ChkValue'] = self.sign_data(post, self.DEBIND_FIELDS)

        return self._request_huifu(self.DEBIND_URL, post)

    def del_card_huifu(self, request):
        """ 解除绑定接口 """
        card_id = request.DATA.get('card_id', '')
        if not card_id or not card_id.isdigit():
            return {"ret_code": 20041, "message": "请输入正确的ID"}

        card = Card.objects.filter(id=card_id, user=request.user).first()

        if not card:
            return {"ret_code": 20042, "message": "该银行卡不存在"}

        if card.is_bind_huifu:
            res = self._unbind_card_huifu(user=request.user, card_no=card.no)
            if res['RespCode'] != u'000000':
                return {"ret_code": -2, "message": res['ErrMsg']}

            card.is_bind_huifu = False
            card.save()

        return {"ret_code": 0, "message": "删除成功"}

    def bind_card_wlbk(self, user, card_no, bank):
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
        card.is_bind_huifu = True
        card.save()
        return True

    def pre_pay(self, request, bank=None):
        if not request.user.wanglibaouserprofile.id_is_valid:
            return {"ret_code": 20111, "message": "请先进行实名认证"}

        amount = request.DATA.get("amount", "").strip()
        card_no = request.DATA.get("card_no", "").strip()
        input_phone = request.DATA.get("phone", "").strip()
        gate_id = request.DATA.get("gate_id", "").strip()

        if not amount or not card_no:
            return {"ret_code": 20112, 'message': '信息输入不完整'}
        if len(card_no) < 10 and not input_phone:
            return {"ret_code": 20112, 'message': '信息输入不完整'}

        try:
            float(amount)
        except:
            return {"ret_code": 20114, 'message': '金额格式错误'}

        amount = fmt_two_amount(amount)

        user = request.user
        profile = user.wanglibaouserprofile
        card, bank = None, None
        if gate_id:
            bank = Bank.objects.filter(gate_id=gate_id).first()
            if not bank or not bank.huifu_bind_code.strip():
                return {"ret_code": 201151, "message": "不支持该银行"}

        if len(card_no) == 10:
            card = Card.objects.filter(user=user, no__startswith=card_no[:6], no__endswith=card_no[-4:]).first()
        else:
            card = Card.objects.filter(no=card_no, user=user).first()
            if bank and card and bank != card.bank:
                return {"ret_code": 201153, "message": "银行卡与银行不匹配"}

        if not card or (card and not card.is_bind_huifu):
            # 开户
            res = self._open_account_huifu(user)
            if res['RespCode'] not in (u'000000', '220001'):
                return {"ret_code": -3, "message": res['ErrMsg']}

            # 邦卡
            res = self._bind_card_huifu(user=user, bank=bank, card_no=card_no)
            if res['RespCode'] not in (u'000000', u'223153'):
                return {"ret_code": -2, "message": res['ErrMsg']}

            # 保存卡信息到个人名下
            self.bind_card_wlbk(user, card_no, bank)

        try:
            pay_info = PayInfo()
            pay_info.amount = amount
            pay_info.total_amount = amount
            pay_info.type = PayInfo.DEPOSIT
            pay_info.status = PayInfo.INITIAL
            pay_info.user = user
            pay_info.channel = "huifu_bind"

            pay_info.request_ip = get_client_ip(request)
            order = OrderHelper.place_order(user, Order.PAY_ORDER, pay_info.status, pay_info=model_to_dict(pay_info))
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

            # 充值
            res = self._card_pay_huifu(user=user, amount=pay_info.amount, card_no=card_no)
            if res['RespCode'] != u'000000':
                pay_info.error_message = res['ErrMsg']
                pay_info.response = res
                pay_info.save()
                return {"ret_code": -3, "message": res['ErrMsg']}
            else:
                pay_info.fee = self.FEE
                keeper = MarginKeeper(pay_info.user, pay_info.order.pk)
                margin_record = keeper.deposit(amount)
                pay_info.margin_record = margin_record
                pay_info.status = PayInfo.SUCCESS
                pay_info.save()
                rs = {"ret_code": 0, "message": "success", "amount": amount, "margin": margin_record.margin_current}

            if rs['ret_code'] == 0 and not card:
                tools.despoit_ok(pay_info, device_type)

                # 充值成功后，更新本次银行使用的时间
                if len(pay_info.card_no) == 10:
                    Card.objects.filter(user=pay_info.user, no__startswith=pay_info.card_no[:6], no__endswith=pay_info.card_no[-4:]).update(last_update=timezone.now())
                else:
                    Card.objects.filter(user=pay_info.user, no=pay_info.card_no).update(last_update=timezone.now())

            OrderHelper.update_order(pay_info.order, pay_info.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
            return rs
        except Exception, e:
            message = PayResult.RETRY
            pay_info.status = PayInfo.FAIL
            pay_info.error_message = str(e)
            pay_info.save()
            OrderHelper.update_order(order, request.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
            return {"ret_code": "20119", "message": message}
