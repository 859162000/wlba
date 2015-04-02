#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import decimal
import logging
from django.forms import model_to_dict
from django.utils.decorators import method_decorator
#from marketing.helper import RewardStrategy
import requests
from order.utils import OrderHelper
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_pay.models import PayInfo
from wanglibao_pay.pay import Pay
import socket
from django.conf import settings
from django.db import transaction
from wanglibao_pay.util import get_client_ip
from wanglibao_pay.views import PayResult
from marketing import tools
import xml.etree.ElementTree as ET
#from wanglibao_sms import messages
#from django.utils import timezone
#from wanglibao_account import message as inside_message
from wanglibao_rest.utils import split_ua

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
