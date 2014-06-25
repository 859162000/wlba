# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import decimal
from wanglibao_pay.pay import Pay
import socket


class SignException(Exception):
    pass


class HuifuPay(Pay):
    PAY_BACK_RETURN_URL = 'http://111.206.165.46:8000/pay/deposit/callback/'
    PAY_RET_URL = 'http://111.206.165.46:8000/pay/deposit/complete/'
    WITHDRAW_BACK_RETURN_URL = 'http://111.206.165.46:8000/pay/withdraw/callback/'
    MER_ID = '510672'
    CUSTOM_ID = '000010124821'
    HOST = '192.168.0.12'
    PORT = 8733
    PAY_URL = 'http://test.chinapnr.com'
    WITHDRAW_URL = 'http://test.chinapnr.com/buser'

    FEE = decimal.Decimal('0.0025')

    VERSION = '10'
    PAY_FIELDS = ['Version', 'CmdId', 'MerId', 'OrdId', 'OrdAmt', 'CurCode', 'Pid', 'RetUrl', 'MerPriv',
                  'GateId', 'UsrMp', 'DivDetails', 'OrderType', 'PayUsrId', 'PnrNum', 'BgRetUrl', 'IsBalance', 'ChkValue']
    WITHDRAW_FIELDS = ['Version', 'CmdId', 'CustId', 'SubAcctId', 'OrdId', 'OrdAmt', 'MerPriv', 'AcctName', 'BankId',
                       'AcctId', 'IsSubAcctId', 'UserMp', 'CertType', 'CertId', 'PrType', 'ProvName', 'AreaName', 'BranchName',
                       'PrPurpose', 'RetUrl', 'Charset', 'ChkType', 'ChkValue']
    SIGN_REQUEST = 'S'
    VALIDATE_REQUEST = 'V'
    CHARSET = 'UTF8'

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
        post['ChkType'] = 'R'


        post['ChkValue'] = self.sign_data(post, HuifuPay.WITHDRAW_FIELDS)
        return {
            'url': HuifuPay.WITHDRAW_URL + '/extUrl/prTransHttp',
            'post': post
        }


