from wanglibao_pay.pay import Pay
import socket


class SignException(Exception):
    pass


class HuifuPay(Pay):
    RMB = 'RMB'
    VERSION = '10'
    BACK_RETURN_URL = 'http://111.206.165.46:8000/pay/callback/'
    RET_URL = 'http://111.206.165.46:8000/pay/callback/'
    MER_ID = '510672'
    PAY_FEILDS = ['Version', 'CmdId', 'MerId', 'OrdId', 'OrdAmt', 'CurCode', 'Pid', 'RetUrl', 'MerPriv',
                  'GateId', 'UsrMp', 'DivDetails', 'OrderType', 'PayUsrId', 'PnrNum', 'BgRetUrl', 'IsBalance', 'ChkValue']
    HOST = '192.168.0.12'
    PORT = 8733
    SIGN_REQUEST = 'S'
    VALIDATE_REQUEST = 'V'
    URL = 'http://test.chinapnr.com'

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HuifuPay.HOST, HuifuPay.PORT))

    @classmethod
    def __format_len(cls, length):
        return "{:0>4d}".format(length)

    def __get_package(self, raw_data, fields, type):
        raw_str = ''
        for field in fields:
            if field != 'ChkValue' and field in raw_data:
                raw_str += str(raw_data[field])

        if type == HuifuPay.VALIDATE_REQUEST:
            raw_str += raw_data['ChkValue']

        raw_len = self.__format_len(len(raw_str))
        package = type + HuifuPay.MER_ID + raw_len + raw_str
        package_len = self.__format_len(len(package))
        package = package_len + package

        self.sock.sendall(package)

        sign = ''
        while 1:
            data = self.sock.recv(4096)
            if not data:
                break
            else:
                sign += data

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

    def verify_sign(self, post):
        package = self.__get_package(post, HuifuPay.PAY_FEILDS, HuifuPay.VALIDATE_REQUEST)
        package_len = len(package)
        if package_len != 15:
            raise SignException("Unformatted response: " + package)

        code = package[11:15]
        return code != '0000'

    def pay(self, post):
        post['Version'] = HuifuPay.VERSION
        post['BgRetUrl'] = HuifuPay.BACK_RETURN_URL
        post['RetUrl'] = HuifuPay.RET_URL
        post['CmdId'] = 'Buy'
        post['MerId'] = HuifuPay.MER_ID

        post['ChkValue'] = self.sign_data(post, HuifuPay.PAY_FEILDS)
        return {
            'url': HuifuPay.URL + '/gar/RecvMerchant.do',
            'post': post
        }