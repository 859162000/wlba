# encoding=utf-8
import json
from common.tools import chunks, update_by_keys
import datetime
from Crypto.Cipher import PKCS1_v1_5, AES
from Crypto.PublicKey import RSA
import M2Crypto
import base64
import requests
import logging
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_pay.models import Bank, Card, PayInfo
from wanglibao_pay.pay import PayOrder


#  数据库需要记录宝付银行代码，绑定关系唯一标示(bind_id), business_no
# TODO 1.暂时不使用短信验证码，business_no 暂时不用放入数据库
# TODO 参数校验
# TODO 等待状态异常处理
BAO_PAY_URL = 'https://tgw.baofoo.com/cutpayment/api/backTransRequest'
# BAO_PAY_URL = 'https://public.baofoo.com/cutpayment/api/backTransRequest'
BAO_PAY_RSA_PUB_KEY_PATH = './certificate/baopay_test_pub_key.pem'
BAO_PAY_RSA_PRIV_KEY_PATH = './certificate/baopay_test_pri_key.pem'
BAO_PAY_MEMBER_ID = '100000178'
BAO_PAY_TERMINAL_ID = '100000916'
# BAO_PAY_MEMBER_ID = '100000178'
# BAO_PAY_TERMINAL_ID = '100000859'
BAO_PAY_ENCRYPT_BLOCK_SIZE = 117
BAO_PAY_DECRYPT_BLOCK_SIZE = 128

logger = logging.getLogger(__name__)

class PayException(Exception):
    # 会触发该异常的第三方返回码, list
    thirdpay_ret_code = None
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return 'error_code:%s, error_message:%s' % (self.code, self.message)

class PayParaException(PayException):
    def __init__(self,  message):
        super(PayParaException, self).__init__(300001, message)

class PayWaitingException(PayException):
    def __init__(self,  message):
        super(PayWaitingException, self).__init__(222222, message)

class BaoPayWaitingException(PayWaitingException):
    thirdpay_ret_code = ['BF00115', 'BF00113', 'BF00144', 'BF00202', 'BF00238']

class BaoPayInterface(object):
    """
    组装宝付的底层支付接口，供前端调用
    """
    def __init__(self, user, request_ip, device_type):
        self.baopay = BaoPay(user, request_ip, device_type)

    def pre_pay(self, card_no, amount, mobile=None, gate_id=None, request=None):
        if len(card_no) == 10:
            self._binded_pay_without_sms(card_no, amount, request)
        else:
            self._first_pay_get_sms(card_no, mobile, gate_id, request)

    def dynnum_bind_pay(self, order_id, sms_code, request):
        self._first_pay_confirm(order_id, sms_code, request)

    def _first_pay_get_sms(self, card_no, mobile, gate_id, amount):
        """
        return -- {"ret_code":0, "message":"ok", "order_id":, "token":}
        """
        resp = self.baopay.pre_bind(card_no, mobile, gate_id, amount)
        return {'ret_code':0, 'message': 'ok', 
                    'order_id': resp['order_id'], 'token': ''}

    def _first_pay_confirm(self, order_id, sms_code, request):
        """
        return -- {"ret_code": 0, "message": "success", 
                "amount": amount, "margin":, "order_id": }
        """
        self.baopay.confirm_bind(order_id, sms_code)
        pre_pay_resp = self.baopay.pre_pay_by_order_id(order_id)
        resp = self.baopay.confirm_pay(order_id, 
                pre_pay_resp['business_no'], request)
        r = {'ret_code': 0, 'message': 'success'}
        update_by_keys(r, resp, 'amount', 'margin', 'order_id')
        return r

    def _binded_pay_without_sms(self, card_no, amount, request):
        """
        绑卡后直接支付不使用短信验证码
        card_no --  短卡号
        return -- 和first_pay_confirm相同
        """
        card = Card.objects.filter(user=self.baopay.user, 
                no__startswith=card_no[:6], no__endswith=card_no[-4:]).get()
        pre_pay_resp = self.baopay.pre_pay_by_card_id(card.id, amount)
        resp = self.baopay.confirm_pay(pre_pay_resp['order_id'], 
                pre_pay_resp['business_no'], request)
        r = {'ret_code': 0, 'message': 'success'}
        update_by_keys(r, resp, 'amount', 'margin', 'order_id')
        return r



class BaoPay(object):
    """
    宝付认证支付 
    """

    def __init__(self, user, request_ip, device_type):
        self.pay_order = PayOrder()
        self.user = user
        self.profile = WanglibaoUserProfile.objects.get(user=user)
        self.id_no = self.profile.id_number
        self.id_name = self.profile.name
        self.request_ip = request_ip
        self.device_type = device_type
    

    def pre_bind(self, no, mobile, gate_id, amount):
        try:
            bank_code = Bank.objects.get(gate_id=gate_id).bao_bind_code
            order_id = self.pay_order.order_before_pay(self.user, amount, gate_id, 
                    self.request_ip, self.device_type, no, mobile)
            pre_bind_para = PreBindCardPara(order_id, no, self.id_no, 
                    self.id_name, mobile, bank_code)
            pre_bind_para.post()
            return {'order_id': order_id}
        except PayException, err:
            self.pay_order.order_after_pay_error(err, order_id)
            raise

    def confirm_bind(self, order_id, sms_code):
        try:
            confirm_bind_para = ConfirmBindCardPara(order_id, sms_code)
            confirm_bind_para.post()
            pay_info = PayInfo.objects.get(order__id=order_id)
            self.pay_order.add_card(pay_info.card_no, pay_info.bank, 
                    pay_info.user, pay_info.channel)
        except PayException, err:
            self.pay_order.order_after_pay_error(err, order_id)
            raise


    def pre_pay_by_order_id(self, order_id):
        """
        首次支付使用绑卡时的order
        """
        try:
            pay_info = PayInfo.objects.get(order__id=order_id)
            card = Card.objects.get(no=pay_info.card_no)
            bind_id = card.bao_bind_id
            amount = pay_info.amount
            return self._pre_pay(order_id, bind_id, amount)
        except PayException, err:
            self.pay_order.order_after_pay_error(err, order_id)
            raise

    def pre_pay_by_card_id(self, card_id, amount):
        """
        后续支付创建新的order
        """
        try:
            card = Card.objects.get(pk=card_id)
            gate_id = card.bank.gate_id
            no = card.no
            bind_id = card.bao_bind_id
            order_id = self.pay_order.order_before_pay(self.user, amount, gate_id, 
                    self.request_ip, self.device_type, no )
            return self._pre_pay(order_id, bind_id, amount)
        except PayException, err:
            self.pay_order.order_after_pay_error(err, order_id)
            raise

    def _pre_pay(self, order_id, bind_id, amount):
        pre_pay_para = PrePayPara(order_id, bind_id, amount)
        resp = pre_pay_para.post()
        resp.update(order_id=order_id)

    def confirm_pay(self, order_id, business_no, request):
        """
        暂时不使用短信验证码，business_no暂时不放到数据库中
        """
        try:
            confirm_pay_para = ConfirmPayPara(order_id, business_no)
            resp_json = confirm_pay_para.post()
            order_id = resp_json['trans_id']
            amount = resp_json['txn_amt']
            resp_content = resp_json['resp_content']
            return self.pay_order.order_after_pay_succcess(amount, order_id,  
                    res_content=resp_content, request=request)
        except PayException, err:
            self.pay_order.order_after_pay_error(err, order_id)
            raise
    
class BaoPayConn(object):
    """
    负责和宝付通讯，发送请求，加解密
    """
    def __init__(self):
        self.url = BAO_PAY_URL 
        self.rsa_priv_key = M2Crypto.RSA.load_key(BAO_PAY_RSA_PRIV_KEY_PATH)
        self.rsa_pub_key = M2Crypto.RSA.load_pub_key(BAO_PAY_RSA_PUB_KEY_PATH)
        self.envelope_para = CommonEnvelopePara()

    def _get_para(self, para_object):
        para = {}
        for k, v in vars(para_object).items():
            if k.startswith('para_'):
                # 选填用空字符标示，不报错
                if v == None:
                    raise PayParaException('BaoPayPara %s is None' % k)
                para.update({k[5:]: v})
        return para

    def _get_encrypt_content(self, content):
        """
        rsa先做b64转换，再分段加密,再做hex编码
        """
        b64_content = base64.b64encode(json.dumps(content))
        content = ''.join([self.rsa_priv_key.private_encrypt(block, M2Crypto.RSA.pkcs1_padding) 
            for block in chunks(b64_content, BAO_PAY_ENCRYPT_BLOCK_SIZE)])
        return content.encode('hex')

    def _get_post(self):
        post_para = self._get_para(self.envelope_para)
        post_para.update(txn_sub_type=self.para_txn_sub_type)
        data_content = self._get_para(self)
        data_content.update(txn_sub_type=self.para_txn_sub_type)
        logging.critical('Baopay_post: %s | %s' % (post_para, data_content))
        data_content=self._get_encrypt_content(data_content)
        post_para.update(data_content=data_content)
        # logging.critical('Baopay_post_encypted: %s' %  post_para)
        return post_para

    def post(self):
        resp = requests.post(self.url, self._get_post())
        resp_json = json.loads(self._decrypt_response(resp.text))
        resp_code = resp_json['resp_code']
        resp_message = resp_json['resp_message']
        if resp_code != 0:
            if resp_code in BaoPayWaitingException.thirdpay_ret_code:
                raise BaoPayWaitingException(resp_message)
            raise PayException(resp_message)
        resp_json.update(resp_content=resp.text)
        return resp_json



    def _decrypt_response(self, resp_text):
        """
        参考_get_encrypt_content,反正处理 
        """
        resp_text = resp_text.decode('hex')
        r = ''
        for block in chunks(resp_text, BAO_PAY_DECRYPT_BLOCK_SIZE):
            print block, '|', len(block)
            r += self.rsa_pub_key.public_decrypt(block, M2Crypto.RSA.pkcs1_padding)
        return r.decode('base64')

class CommonEnvelopePara(object):
    """
    宝付通用的envelope参数,直接post，不用加密
    """

    def __init__(self):
        self.para_version = '4.0.0.0' #版本号
        self.para_member_id = BAO_PAY_MEMBER_ID # 商户编号
        self.para_terminal_id = BAO_PAY_TERMINAL_ID #终端号
        self.para_txn_type = '0431' # 交易类型
        self.para_txn_sub_type = '' # 交易子类型
        self.para_data_type = 'json' # 加密数据类型

class CommmonContentPara(object):
    """
    宝付通用参数，会被json化之后加密放到data_content中
    """
    def __init__(self):
        self.para_txn_sub_type = ''  # 交易子类型
        self.para_biz_type = '0000'  # 接入类型
        self.para_member_id = BAO_PAY_MEMBER_ID
        self.para_terminal_id = BAO_PAY_TERMINAL_ID 
        self.para_trans_serial_no = None # 商户流水编号，8-20
        self.para_trans_id = None # 商户订单号，8-20
        self.para_trade_date = datetime.datetime.now().strftime('%Y%m%d%H%M%S') # 订单日期，年年年年月月日日时时分分秒秒
        self.para_additional_info = '' # 附加字段
        self.para_req_reserved = '' # 请求方保留域


class PreBindCardPara(CommmonContentPara, BaoPayConn):
    """
    预绑卡参数
    """
    def __init__(self, order_id, no, id_no, id_name, mobile, bank_code):
        CommmonContentPara.__init__(self)
        BaoPayConn.__init__(self)
        self.para_txn_sub_type = '11'
        self.para_acc_no = no # 绑定卡号
        self.para_id_card_type = '01' # 证件类型，默认为01，身份证
        self.para_id_card = id_no # 身份证号
        self.para_id_holder = id_name # 持卡人姓名
        self.para_mobile = mobile # 绑定手机号
        self.para_pay_code = bank_code # 银行编码
        self.para_valid_date = '' # 卡有效期
        self.para_valid_no = '' # 卡安全码

class ConfirmBindCardPara(CommmonContentPara, BaoPayConn):
    """
    确认绑卡参数 
    """
    def __init__(self, order_id, sms_code):
        super(ConfirmBindCardPara, self).__init__()
        self.para_txn_sub_type = '12'
        self.para_sms_code = sms_code # 确认绑定的短信验证码

class PrePayPara(CommmonContentPara, BaoPayConn):
    """
    预支付参数，暂时不使用短信验证
    """
    def __init__(self, order_id, bind_id, amount):
        super(PrePayPara, self).__init__()
        # 14 预支付交易(不发送短信)
        # 15 预支付交易(不发送短信)
        self.para_txn_sub_type = '15'
        self.para_bind_id = None  # 用于绑定关系的唯一标示
        self.para_txn_amt = None # 交易金额,分
        # todo ? client_ip 
        self.para_risk_content = '' # 风险控制参数

class ConfirmPayPara(CommmonContentPara, BaoPayConn):
    """
    确认支付参数 
    """
    def __init__(self, order_id, business_no, sms_code=''):
        super(ConfirmPayPara, self).__init__()
        # 确认支付不需要trans_id, 需要business_no
        # 为了保持一致性我们也可以把trans_id post 过去
        self.para_txn_sub_type = '16'
        self.para_business_no =  None # 宝付业务流水号
        self.para_sms_code = sms_code # 支付时的短信验证码


if __name__ == '__main__':
    BAO_PAY_BIND_ID = '201603261412121000009649074'
    pre_bind_card_para = PreBindCardPara()
    pre_bind_card_para.para_trans_id = '40111232' 
    pre_bind_card_para.para_trans_serial_no = '40121234'
    pre_bind_card_para.para_acc_no = '6228480444455553333' # 绑定卡号
    pre_bind_card_para.para_id_card = '320301198502169142' # 身份证号
    pre_bind_card_para.para_id_holder = 'wb' # 持卡人姓名
    pre_bind_card_para.para_mobile = '15011388888' # 绑定手机号
    pre_bind_card_para.para_pay_code = 'ABC' # 银行编码
    resp_text = pre_bind_card_para.post().text
    print pre_bind_card_para._decrypt_response(resp_text)







