# encoding=utf-8
import json
from common.tools import chunks
import datetime
from Crypto.Cipher import PKCS1_v1_5, AES
from Crypto.PublicKey import RSA
import M2Crypto
import base64
import requests


#  数据库需要记录宝付银行代码，绑定关系唯一标示(bind_id)
BAO_PAY_URL = 'https://tgw.baofoo.com/cutpayment/api/backTransRequest'
# BAO_PAY_URL = 'https://public.baofoo.com/cutpayment/api/backTransRequest'
BAO_PAY_RSA_PUB_KEY_PATH = './certificate/baopay_test_pub_key.pem'
BAO_PAY_RSA_PRIV_KEY_PATH = './certificate/baopay_test_pri_key.pem'
BAO_PAY_MEMBER_ID = '100000178'
BAO_PAY_TERMINAL_ID = '100000859'
BAO_PAY_ENCRYPT_BLOCK_SIZE = 117
BAO_PAY_DECRYPT_BLOCK_SIZE = 128

class BaoPayException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return 'error_code:%s, error_message:%s' % (self.code, self.message)

class BaoPayParaException(BaoPayException):
    def __init__(self,  message):
        self.code = 300001
        self.message = message

class BaoPay(object):
    def __init__(self):
        self.url = BAO_PAY_URL 
        self.rsa_priv_key = RSA.importKey(open(BAO_PAY_RSA_PRIV_KEY_PATH).read())
        self.rsa_pub_key = M2Crypto.RSA.load_pub_key(BAO_PAY_RSA_PUB_KEY_PATH)
        self.envelope_para = CommonEnvelopePara()

    def _get_para(self, para_object):
        para = {}
        for k, v in vars(para_object).items():
            if k.startswith('para_') and k != 'para_txn_sub_type':
                if not v:
                    raise BaoPayParaException('BaoPayPara %s is None' % k)
                para.update({k[5:]: v})
        return para

    def _get_rsa_content(self, content):
        """
        rsa先做b64转换，再分段加密
        """
        cipher = PKCS1_v1_5.new(self.rsa_priv_key)
        b64_content = base64.b64encode(json.dumps(content))
        return ''.join([cipher.encrypt(block) 
            for block in chunks(b64_content, BAO_PAY_ENCRYPT_BLOCK_SIZE)])

    def _get_post(self):
        post_para = self._get_para(self.envelope_para)
        print 'post_data_content:' + str(self._get_para(self))
        data_content=self._get_rsa_content(self._get_para(self))
        post_para.update(data_content=data_content)
        post_para.update(txn_sub_type=self.para_txn_sub_type)
        return post_para

    def post(self):
        return requests.post(self.url, self._get_post())

    def decode_base64(self, data):
        """Decode base64, padding being optional.

        :param data: Base64 data as an ASCII byte string
        :returns: The decoded byte string.

        """
        print data, '|', len(data)
        missing_padding = 4 - len(data) % 4
        if missing_padding:
            data += b'='* missing_padding
        return base64.decodestring(data)

    def _decrypt_response(self, resp_text):
        # resp_text = ''.join([self.rsa_pub_key.public_decrypt(block, M2Crypto.RSA.pkcs1_padding)
            # for block in chunks(resp_text, BAO_PAY_DECRYPT_BLOCK_SIZE)])
        r = ''
        for block in chunks(resp_text, BAO_PAY_DECRYPT_BLOCK_SIZE):
            print block, '|', len(block)
            import binascii
            r += self.rsa_pub_key.public_decrypt(binascii.unhexlify(block), M2Crypto.RSA.pkcs1_padding)
        return r

class CommonEnvelopePara(object):

    def __init__(self):
        self.para_version = '4.0.0.0' #版本号
        self.para_member_id = BAO_PAY_MEMBER_ID # 商户编号
        self.para_terminal_id = BAO_PAY_TERMINAL_ID #终端号
        self.para_txn_type = '0431' # 交易类型
        self.para_txn_sub_type = None # 交易子类型
        self.para_data_type = 'json' # 加密数据类型

class CommmonContentPara(object):
    def __init__(self):
        self.para_txn_sub_type = None  # 交易子类型
        self.para_biz_type = '0000'  # 接入类型
        self.para_member_id = BAO_PAY_MEMBER_ID
        self.para_terminal_id = BAO_PAY_TERMINAL_ID 
        self.para_trans_serial_no = None # 商户流水编号，8-20
        self.para_trans_id = None # 商户订单号，8-20
        self.para_trade_date = datetime.datetime.now().strftime('%Y%m%d%H%M%S') # 订单日期，年年年年月月日日时时分分秒秒


class PreBindCardPara(CommmonContentPara, BaoPay):
    def __init__(self):
        CommmonContentPara.__init__(self)
        BaoPay.__init__(self)
        self.para_txn_sub_type = '11'
        self.para_acc_no = None # 绑定卡号
        self.para_id_card_type = '01' # 证件类型，默认为01，身份证
        self.para_id_card = None # 身份证号
        self.para_id_holder = None # 持卡人姓名
        self.para_mobile = None # 绑定手机号
        self.para_pay_code = None # 银行编码

class ConfirmBindCardPara(CommmonContentPara, BaoPay):
    def __init__(self):
        super(ConfirmBindCardPara, self).__init__()
        self.para_txn_sub_type = '12'
        self.para_sms_code = None # 确认绑定的短信验证码

class PrePayPara(CommmonContentPara, BaoPay):
    def __init__(self):
        super(PrePayPara, self).__init__()
        # 14 预支付交易(不发送短信)
        # 15 预支付交易(不发送短信)
        self.para_txn_sub_type = '15'
        self.para_bind_id = None  # 用于绑定关系的唯一标示
        self.para_txn_amt = None # 交易金额,分
        self.para_risk_content = None # 风险控制参数

class ConfirmPayPara(CommmonContentPara, BaoPay):
    def __init__(self):
        super(ConfirmPayPara, self).__init__()
        # 确认支付不需要trans_id, 需要business_no
        # 为了保持一致性我们也可以把trans_id post 过去
        self.para_txn_sub_type = '16'
        self.para_business_no =  None # 宝付业务流水号
        self.para_sms_code = None # 支付时的短信验证码


if __name__ == '__main__':
    BAO_PAY_BIND_ID = '201603261412121000009649074'
    pre_bind_card_para = PreBindCardPara()
    pre_bind_card_para.para_trans_id = '4011' 
    pre_bind_card_para.para_trans_serial_no = '4012'
    pre_bind_card_para.para_acc_no = '4211' # 绑定卡号
    pre_bind_card_para.para_id_card = '4212' # 身份证号
    pre_bind_card_para.para_id_holder = '小东' # 持卡人姓名
    pre_bind_card_para.para_mobile = '1501138888' # 绑定手机号
    pre_bind_card_para.para_pay_code = 'CMBC' # 银行编码
    resp_text = pre_bind_card_para.post().text
    print 'resp:', resp_text, len(resp_text)
    print pre_bind_card_para._decrypt_response(resp_text)







