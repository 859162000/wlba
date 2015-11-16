import hmac
from django.conf import settings
from django.db import transaction
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.decorators import method_decorator
import requests
from order.models import Order
from order.utils import OrderHelper
from wanglibao_account.auth_backends import User
from wanglibao_bank_financing.models import Bank
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_pay import util
from wanglibao_pay.exceptions import ThirdPayError
from wanglibao_pay.models import PayInfo, Card, PayResult
import logging

logger = logging.getLogger(__name__)

class PayOrder(object):
    """
    用于绑卡，支付请求和订单系统的交互
    未绑卡时根据card_no 和gate_id可以知道银行卡，银行，支付渠道信息
    绑卡后根据card_no 就可以知道银行卡，银行，支付渠道信息
    """
    @method_decorator(transaction.atomic)
    def order_before_pay(self, user, amount, card_no, gate_id, phone_for_card, request_ip, device):
        """

        :param user:
        :param amount:
        :param card_no:
        :param gate_id:
        :param request_ip:
        :param channel: kuaipay, yeepay, huifupay
        :return:
        """

        # todo 参数校验
        if len(card_no) == 10:
            card = Card.objects.filter(user=user, no__startswith=card_no[:6], no__endswith=card_no[-4:]).first()
        else:
            card = Card.objects.filter(no=card_no, user=user).first()
        bank = Bank.objects.filter(gate_id=gate_id).first()
        channel = ''
        # if not bank or not bank.kuai_code.strip():
        #         # return {"ret_code":201151, "message":"不支持该银行"}
        # if bank and card and bank != card.bank:
        #     # return {"ret_code":201153, "message":"银行卡与银行不匹配"}
        #
        # if not card and not bank:
        #     # return {"ret_code":201152, "message":"卡号不存在或银行不存在"}


        pay_info = PayInfo()
        pay_info.amount = amount
        pay_info.total_amount = amount
        pay_info.type = PayInfo.DEPOSIT
        pay_info.status = PayInfo.INITIAL
        pay_info.user = user
        pay_info.channel = channel
        pay_info.phone_for_card = phone_for_card
        pay_info.device = device
        # todo 是否记录更全面的客户端信息
        pay_info.request_ip = request_ip
        order = OrderHelper.place_order(user, Order.PAY_ORDER, pay_info.status,
                                        pay_info = model_to_dict(pay_info))

        # todo 不同状态（已绑卡，未绑卡）事bank和card_no的处理
        pay_info.order = order
        if card:
            pay_info.bank = card.bank
            pay_info.card_no = card.no
        else:
            pay_info.bank = bank
            pay_info.card_no = card_no

        # todo 时间处理
        pay_info.request = ""
        pay_info.status = PayInfo.PROCESSING
        pay_info.account_name = user.wanglibaouserprofile.name
        pay_info.save()
        OrderHelper.update_order(order, user, pay_info=model_to_dict(pay_info), status=pay_info.status)
        return order.id

    def order_restart_fail(self, order_id):
        """
        将pay_info 设置为processing状态，重新开始处理失败或是异常的订单
        :param pay_info_id:
        :return:
        """
        pay_info = PayInfo.objects.select_for_update().filter(order_id=order_id).get()
        if pay_info.status == PayInfo.EXCEPTION or pay_info.status == PayInfo.FAIL:
            pay_info.status = PayInfo.PROCESSING
            return 0
        elif pay_info.status == PayInfo.SUCCESS:
            return 1
        else:
            raise ThirdPayError(77777, 'illegal condition within pay')


    @method_decorator(transaction.atomic)
    def order_after_pay_succcess(self, amount, order_id, res_ip, res_content):
        """
        处理订单和用户的账户
        :param amount:
        :param order_id:
        :param user_id:
        :param ip:
        :param res_content:
        :param device:
        :return:
        """
        # 参数校验
        pay_info = PayInfo.objects.select_for_update().filter(order_id=order_id).first()
        if not pay_info:
            # return {"ret_code":20131, "message":"order not exist", "amount": amount}
            raise ThirdPayError(20131, 'order not exist')
        # todo 只允许processing状态的
        if pay_info.status == PayInfo.SUCCESS:
            return {"ret_code":0, "message":PayResult.DEPOSIT_SUCCESS, "amount": amount}
        if pay_info.amount != amount:
            raise ThirdPayError(20132, PayResult.EXCEPTION)
        if pay_info.user_id != pay_info.user_id:
            raise ThirdPayError(20133, PayResult.EXCEPTION)

        # 更新pay_info和margin信息
        pay_info.error_message = ""
        pay_info.response = res_content
        #
        pay_info.response_ip = res_ip
        pay_info.fee = self.FEE
        keeper = MarginKeeper(pay_info.user, pay_info.order.pk)
        margin_record = keeper.deposit(amount)
        pay_info.margin_record = margin_record
        pay_info.status = PayInfo.SUCCESS
        pay_info.save()

        # 更新card和order信息
        if len(pay_info.card_no) == 10:
            Card.objects.filter(user=pay_info.user, no__startswith=pay_info.card_no[:6], no__endswith=pay_info.card_no[-4:]).update(last_update=timezone.now(), is_bind_kuai=True)
        else:
            Card.objects.filter(user=pay_info.user, no=pay_info.card_no).update(last_update=timezone.now(), is_bind_kuai=True)
        OrderHelper.update_order(pay_info.order, pay_info.user, pay_info=model_to_dict(pay_info), status=pay_info.status)

        # todo 加入存款成功的回调
        logger.critical("orderId:%s success" % order_id)
        rs = {"ret_code": 0, "message": "success", "amount": amount, "margin": margin_record.margin_current,
              "order_id": order_id}
        return rs

    @method_decorator(transaction.atomic)
    def order_after_pay_error(self, error, order_id):
        logger.exception(error)
        pay_info = PayInfo.objects.select_for_update().get(order_id=order_id)

        if pay_info.status == PayInfo.PROCESSING:
            order = Order.objects.get(id=order_id)
            user = User.objects.get(id=pay_info.user_id)

            if isinstance(error, ThirdPayError):
                error_code = error.code
                is_inner_error = False
            else:
                error_code = 20119
                is_inner_error = True
            error_message = error.message
            pay_info.save_error(error_code=error_code, error_message=error_message, is_inner_error=is_inner_error)
            OrderHelper.update_order(order, user, pay_info=model_to_dict(pay_info), status=pay_info.status)
            return {"ret_code": error_code, "message": error_message, 'order_id':order_id, 'pay_info_id':pay_info.id}
        else:
            # 若TR3或者前期已经完成该交易，直接返回结果
            return {"ret_code": pay_info.error_code, "message": pay_info.error_message,
                    'order_id':order_id, 'pay_info_id':pay_info.id}

class PayMessage(object):
    """
    处理第三方支付通道返回的支付结果信息
    """

            # result = {"ret_code": 0, "order_id":int(order_id), "user_id":int(user_id),
            #         "bank_name":bank_name, "amount":amount, 'message': '成功',
            #         'res_content': res_content, "ref_number": ref_number, 'signature': signature}

    def __init__(self):
        self.order_id = 0
        # self.user_id = 0
        # self.bank_name = ''
        self.amount = 0
        # 用0标示支付成功，其他情况保存原始id
        self.ret_code = 0
        self.res_message = ''
        self.res_content = ''
        self.res_ip = ''
        # self.ref_number = 0
        # self.signature = ''

    def __repr__(self):
        return '%s: order %s amount %s raw_message %s' % (self.__class__.__name__, self.order_id, self.amount,
                                                          self.res_content)

    def _convert_message(self, res_content, res_ip):
        """
        将第三方信息转换为dict以便后续处理
        :param res_content:
        :return:
        """
        self.res_ip = res_ip

    def _check_signature(self, message_dict):
        """
        校验第三方信息转换之后的dict，如签名等第三方参数
        :return: 合法后将信息注入self， 出错报ThirdPayError
        """
        raise NotImplementedError()

    def _check_result(self):
        """
        校验第三方信息转换之后的PayMessage是否符合业务逻辑
        :return: self
        """
        if self.ret_code != 0:
            # todo error如何返回给前段？
            raise ThirdPayError(40017, '第三方支付失败' + str(self))
        amount = PayInfo.objects.get(order_id=self.order_id).amount
        if self.amount != amount:
            raise ThirdPayError(40019, '第三方返回参数与数据库不一致' + str(self))

    def parse_message(self, res_content):
        self._check_signature(self._convert_message(res_content))
        self._check_result()
        return self

class YeeProxyPayCallbackMessage(PayMessage):

    @staticmethod
    def get_hmac(para_dict, para_type):
        """
        @:param para_dict:
        @:param type: request or response
        """
        # 参与hmac计算的参数以及其顺序
        request_para_order = ['p0_Cmd', 'p1_MerId', 'p2_Order', 'p3_Amt', 'p4_Cur', 'p5_Pid', 'p8_Url']
        response_para_order = ['p1_MerId', 'r0_Cmd', 'r1_Code', 'r2_TrxId', 'r3_Amt', 'r4_Cur', 'r5_Pid', 'r6_Order',
                               'r7_Uid', 'r8_MP', 'r9_BType']
        secret_key = settings.YEE_MER_PRIV_KEY

        if para_type == 'request':
            para_order = request_para_order
        else:
            para_order = response_para_order

        str_to_sign = ''.join([para_dict.get(k, '') for k in para_order])
        hmac_str = hmac.new(secret_key, str_to_sign).hexdigest()
        return hmac_str

    def _convert_message(self, res_in_post, res_ip):
        """
        第三方返回的参数直接放到了 request.POST中，不用转换
        :param res_in_post:
        :return:
        """
        super(YeeProxyPayCallbackMessage, self)._convert_message(res_in_post, res_ip)
        return res_in_post

    def _check_signature(self, message_dict):
        # check
        hmac = self.get_hmac(message_dict, 'response')
        if message_dict.get('r8_MP') != '2' or hmac != message_dict.get('hmac'):
            raise ThirdPayError(40015, '不合法的第三方支付信息' + str(message_dict))

        try:
            # convert data
            self.order_id = int(message_dict.get('r6_Order'))
            self.amount = int(message_dict.get('r3_Amt'))
            # 1代表成功，因为只有成功才会回调，所以只会是1
            ret_code = int(message_dict.get('r1_Code'))
            if ret_code == 1:
                self.ret_code = 0
            else:
                self.ret_code = ret_code
            self.res_message = '支付成功'
            self.res_content = str(message_dict)
        except:
            raise ThirdPayError(40015, '不合法的第三方支付信息' + str(message_dict))

class YeeProxyPay(object):
    """
    易宝网银支付，跳转到易宝的支付页面
    1.后台回调地址要通过管理页面设置，页面重定向通过p8_Url设置
    2.生成hmac的参数是有顺序的
    """
    def __int__(self):
        self.pay_order = PayOrder()
        # TODO ADD TO SETTINGS
        self.proxy_pay_url = settings.YEE_PROXY_PAY_URL

    def _post(self, order_id, amount):
        post_para = {
            'p0_Cmd': 'Buy',
            'p1_MerId': settings.YEE_MER_ID,
            'p2_Order': order_id,
            'p3_Amt': amount,
            'p4_Cur': 'CNY',
            # 商品名称， Max（20）,p6, p7为商品分类，描述，我们暂时就不传了
            'p5_Pid': '网利宝最专业的选择',
            # 回调地址， Max（200）
            'p8_Url': settings.YEE_PROXY_PAY_WEB_CALLBACK_URL,
            'hmac': ''
        }
        post_para.update(hmac=self.get_hmac(post_para))
        return post_para

    def _request(self, url, post_data):
        return requests.post(url, post_data)

    def proxy_pay(self, user, amount, card_no, gate_id, phone_for_card, request_ip, device, exit_for_test=False):
        order_id = self.pay_order.order_before_pay(user, amount, card_no, gate_id, phone_for_card, request_ip, device)
        post_data = self._post(order_id, amount)
        self._request(self.proxy_pay_url, post_data)

    def proxy_pay_callback(self, pay_message):
        """

        :type pay_message: PayMessage
        :return:
        """
        try:
            # use PayMessage to CHECK PARA, RAISE ERROR before proxy_pay_callback
            self.pay_order.order_after_pay_succcess(pay_message.amount, pay_message.order_id, pay_message.res_ip,
                                                    pay_message.res_content)
        except ThirdPayError, error:
            self.pay_order.order_after_pay_error(error, pay_message.order_id)




