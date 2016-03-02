from decimal import Decimal
from string import Template
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from mock import MagicMock
from order.models import Order
from wanglibao import test_util
import new
from wanglibao_margin.models import Margin, MarginRecord
from wanglibao_pay.exceptions import VerifyError, ThirdPayError
from wanglibao_pay.kuai_pay import KuaiShortPay
from wanglibao_pay.mock_generator import PayMockGenerator
from wanglibao_pay.models import PayInfo, Card
from wanglibao_pay.pay import PayOrder, YeeProxyPayCallbackMessage

PAY_RES = Template("""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
<MasMessage xmlns="http://www.99bill.com/mas_cnp_merchant_interface"><version>1.0</version>\
<TxnMsgContent><txnType>PUR</txnType><interactiveStatus>TR2</interactiveStatus><amount>$amount</amount>\
<merchantId>104110045112012</merchantId><terminalId>00004559</terminalId>\
<entryTime>20151015091014</entryTime><externalRefNumber>$order_id</externalRefNumber>\
<customerId>$user_id</customerId><transTime>20151015171054</transTime>\
<refNumber>001262175679</refNumber><responseCode>$res_code</responseCode>\
<responseTextMessage>交易成功</responseTextMessage><cardOrg>CU</cardOrg>\
<issuer>平安银行</issuer><storableCardNo>6230582412</storableCardNo></TxnMsgContent></MasMessage>\
""")


def mock_request_switch(pay_inst, status='succeed'):
    """
    模拟快钱的返回，可以返回：成功，失败，等待三种返回
    """
    def _request_side_effect(pay_inst, data, url, status=status):
        dic = pay_inst._request_dict
        if status == 'succeed':
            res_code = '00'
        elif status == 'fail':
            res_code = '01'
        elif status == 'wait':
            res_code = 'c0'
        res = MagicMock()
        res.status_code = 200
        if url == pay_inst.DYNNUM_URL:
            res_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
    <MasMessage xmlns="http://www.99bill.com/mas_cnp_merchant_interface">\
    <GetDynNumContent><merchantId>812310060110013</merchantId><customerId>%s</customerId>\
    <storablePan>6214857068</storablePan><token>323881987</token><responseCode>%s</responseCode>\
    </GetDynNumContent></MasMessage>\
    """ % (dic['user_id'], res_code)

        elif url == pay_inst.PAY_URL:
            #需确保amount， externalRefNumber， customerId
            res_content = PAY_RES.substitute(amount=dic['amount'], order_id=dic['order_id'],
                                             user_id=dic['user_id'], res_code=res_code)
        res.content = res_content
        return res
    pay_inst._request = new.instancemethod(_request_side_effect, pay_inst, None)

class KuaiPaySignatureTests(TestCase):
    def setUp(self):
        self.kuai_pay = KuaiShortPay()
        # self.signature = 'Zcm+Px/tP9F/YqS40S64r2/eXMKtqzmgJdoFY0NPyCgzNKKw5OT0WXVTyP6Tw0twc42iO3zee33t6qGhim/Saq0LOB2Y9P/fCkGDEci6gsi9Sp7BRUFukNnOsZ8zS4fK2VtiVt8dQ5qK/qWLNdTdXo90zSZhy1jMefoZiVYgZYM='
        # self.content = '<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><MasMessage xmlns=\"http://www.99bill.com/mas_cnp_merchant_interface\"><version>1.0</version><TxnMsgContent><txnType>PUR</txnType><interactiveStatus>TR3</interactiveStatus><amount>10</amount><merchantId>104110045112012</merchantId><terminalId>00002012</terminalId><entryTime>20151022062806</entryTime><externalRefNumber>1905449</externalRefNumber><transTime>20151022142927</transTime><refNumber>000012576108</refNumber><responseCode>00</responseCode><cardOrg>CU</cardOrg><storableCardNo>6225880549</storableCardNo><authorizationCode>369646</authorizationCode></TxnMsgContent></MasMessage>'
        self.signature = 'M6BbwS15vMEXIGLV4ezSdV6PlMrkAmCRBoeCfQL8kWFsSzvXLIxfIVMDVm5Cg/uyfmazhHPjnUG4UG6XzlnxqGq6V5fWlAYL9r9Dv13IZh+bKRi+al6g7PKt3jv37r1SGVkpiz9CZUJjZg/2CooSZMf50awUk4rqJQeGChnUgrM='
        self.content = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><MasMessage xmlns="http://www.99bill.com/mas_cnp_merchant_interface"><version>1.0</version><TxnMsgContent><txnType>PUR</txnType><interactiveStatus>TR3</interactiveStatus><amount>1000</amount><merchantId>104110045112012</merchantId><terminalId>00002012</terminalId><entryTime>20151023083037</entryTime><externalRefNumber>1905623</externalRefNumber><transTime>20151023163200</transTime><refNumber>000012580909</refNumber><responseCode>00</responseCode><cardOrg>CU</cardOrg><storableCardNo>6228481972</storableCardNo><authorizationCode>123397</authorizationCode></TxnMsgContent></MasMessage>'

    def test_signature(self):
        print self.kuai_pay.pem, self.signature, self.content
        # succeed
        self.assertEqual(True, self.kuai_pay._check_signature(self.content, self.signature))
        # fail
        self.assertRaises(VerifyError, self.kuai_pay._check_signature, self.content, '')

class PayTests(TestCase):
    def setUp(self):
        # generate user
        test_util.prepare_user_with_profile()
        #generate bank
        PayMockGenerator.generate_bank()

        self.user = test_util.get_user()
        self.amount_0 = 0
        self.amount_1 = 100
        self.amount_2 = 200
        self.card_no = '123456789123456'
        #短码，用于后续快捷支付
        self.short_card_no = '1234563456'
        self.input_phone = '15011488088'
        self.gate_id = '28'
        self.device = 'android'
        self.ip = '192.168.1.1'
        #手机验证码
        self.VCODE = 'abc'
        self.TOKEN = '323881987'
        self.request = MagicMock()
        self.request.user = ''

# todo better 等去掉requests 之后开启测试
# class KuaiPayTests(PayTests):
#     def setUp(self):
#         super(KuaiPayTests, self).setUp()
#
#         self.kuai_pay = KuaiShortPay()
#         # todo better 暂时无法构造签名，只能到服务器上测试该方法
#         self.kuai_pay._check_signature = MagicMock(ret_value=True)
#         self.kuai_pay._request = MagicMock()
#         mock_request_switch(self.kuai_pay)
#
#     def _clear_margin(self):
#         margin = Margin.objects.get(user_id=self.user.id)
#         margin.amount = 0
#         margin.save()
#
#     def test_result2dict(self):
#         # transtime 的值为空
#         c = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><MasMessage xmlns="http://www.99bill.com/\
# mas_cnp_merchant_interface"><version>1.0</version><TxnMsgContent><txnType>PUR</txnType><interactiveStatus>TR2\
# </interactiveStatus><amount>200.00</amount><merchantId>812310060110013</merchantId><terminalId>00004559</terminalId>\
# <entryTime>20151101022840</entryTime><externalRefNumber>36825386</externalRefNumber><customerId>759891</customerId>\
# <transTime></transTime><responseCode>68</responseCode><responseTextMessage>deal time out</responseTextMessage>\
# </TxnMsgContent></MasMessage>"""
#         r = self.kuai_pay._result2dict(c)
#         print r
#
#     def test_dynnum_pay(self):
#         """
#         验证码支付
#         :return:
#         """
#         mock_request_switch(self.kuai_pay)
#         res = self.kuai_pay.pre_pay(self.user, self.amount_1, self.card_no, self.input_phone, self.gate_id, self.device,
#                                     self.ip)
#         order_id = res['order_id']
#         self.assertEqual(self.TOKEN, res['token'])
#         order = Order.objects.get(id=order_id)
#         pay_info = PayInfo.objects.get(order_id=order_id)
#         margin = Margin.objects.get(user_id=self.user.id)
#         self.assertEqual('处理中', order.status)
#         self.assertEqual('处理中', pay_info.status)
#         self.assertEqual(0, margin.margin)
#
#
#         res = self.kuai_pay.dynnum_bind_pay(self.user, self.VCODE, order_id, self.TOKEN, self.input_phone,
#                                             self.device, self.ip)
#         order = Order.objects.get(id=order_id)
#         pay_info = PayInfo.objects.get(order_id=order_id)
#         margin = Margin.objects.get(user_id=self.user.id)
#         margin_record = MarginRecord.objects.filter(order_id=order_id)
#         self.assertEqual('成功', order.status)
#         self.assertEqual('成功', pay_info.status)
#         self.assertEqual(self.amount_1, margin.margin)
#         self.assertEqual(1, margin_record.count())
#
#         self._clear_margin()
#
#     def test_dynnum_failed(self):
#         """
#         获取验证码失败
#         :return:
#         """
#         mock_request_switch(self.kuai_pay, status='fail')
#         res = self.kuai_pay.pre_pay(self.user, self.amount_1, self.card_no, self.input_phone, self.gate_id, self.device,
#                                     self.ip)
#         print res
#         order_id = res['order_id']
#         self.assertNotEqual(0, res['ret_code'])
#         order = Order.objects.get(id=order_id)
#         pay_info = PayInfo.objects.get(order_id=order_id)
#         margin = Margin.objects.get(user_id=self.user.id)
#         self.assertEqual('失败', order.status)
#         self.assertEqual('失败', pay_info.status)
#         self.assertEqual(0, margin.margin)
#
#     def test_dynnum_pay_failed(self):
#         """
#         验证码支付失败
#         :return:
#         """
#         res = self.kuai_pay.pre_pay(self.user, self.amount_1, self.card_no, self.input_phone, self.gate_id, self.device,
#                                     self.ip)
#         print res
#         order_id = res['order_id']
#         self.assertEqual(self.TOKEN, res['token'])
#         order = Order.objects.get(id=order_id)
#         pay_info = PayInfo.objects.get(order_id=order_id)
#         margin = Margin.objects.get(user_id=self.user.id)
#         self.assertEqual('处理中', order.status)
#         self.assertEqual('处理中', pay_info.status)
#         self.assertEqual(0, margin.margin)
#
#         mock_request_switch(self.kuai_pay, status='fail')
#         res = self.kuai_pay.dynnum_bind_pay(self.user, self.VCODE, order_id, self.TOKEN, self.input_phone,
#                                             self.device, self.ip)
#         order = Order.objects.get(id=order_id)
#         pay_info = PayInfo.objects.get(order_id=order_id)
#         margin = Margin.objects.get(user_id=self.user.id)
#         margin_record = MarginRecord.objects.filter(order_id=order_id)
#         self.assertEqual('失败', order.status)
#         self.assertEqual('失败', pay_info.status)
#         self.assertEqual(0, margin.margin)
#         self.assertEqual(0, margin_record.count())
#
#     def test_qpay(self):
#         """
#         一键支付
#         :return:
#         """
#         mock_request_switch(self.kuai_pay)
#         res = self.kuai_pay.pre_pay(self.user, self.amount_2, self.short_card_no, self.input_phone, self.gate_id,
#                                     self.device, self.ip)
#         order_id = res['order_id']
#         order = Order.objects.get(id=order_id)
#         pay_info = PayInfo.objects.get(order_id=order_id)
#         margin = Margin.objects.get(user_id=self.user.id)
#         margin_record = MarginRecord.objects.filter(order_id=order_id)
#         self.assertEqual('成功', order.status)
#         self.assertEqual('成功', pay_info.status)
#         self.assertEqual(self.amount_2, margin.margin)
#         self.assertEqual(1, margin_record.count())
#
#         self._clear_margin()
#
#     def test_qpay_failed(self):
#         """
#         一键支付失败
#         :return:
#         """
#         mock_request_switch(self.kuai_pay, status='fail')
#         res = self.kuai_pay.pre_pay(self.user, self.amount_2, self.short_card_no, self.input_phone, self.gate_id,
#                                     self.device, self.ip)
#         order_id = res['order_id']
#         order = Order.objects.get(id=order_id)
#         pay_info = PayInfo.objects.get(order_id=order_id)
#         margin = Margin.objects.get(user_id=self.user.id)
#         margin_record = MarginRecord.objects.filter(order_id=order_id)
#         self.assertEqual('失败', order.status)
#         self.assertEqual('失败', pay_info.status)
#         self.assertEqual(0, margin.margin)
#         self.assertEqual(0, margin_record.count())
#
#         self._clear_margin()
#
#
#     def test_2_qpay(self):
#         """
#         两次一键支付
#         :return:
#         """
#         mock_request_switch(self.kuai_pay)
#         self.kuai_pay.pre_pay(self.user, self.amount_1, self.short_card_no, self.input_phone, self.gate_id,
#                                     self.device, self.ip)
#         self.kuai_pay.pre_pay(self.user, self.amount_2, self.short_card_no, self.input_phone, self.gate_id,
#                                     self.device, self.ip)
#         margin = Margin.objects.get(user_id=self.user.id)
#         self.assertEqual(self.amount_1 + self.amount_2, margin.margin)
#
#         self._clear_margin()
#
#     def test_qpay_tr3(self):
#         """
#         一键支付通过tr3成功
#         :return:
#         """
#         mock_request_switch(self.kuai_pay,status='wait')
#         res = self.kuai_pay.pre_pay(self.user, self.amount_2, self.short_card_no, self.input_phone, self.gate_id,
#                                     self.device, self.ip)
#         order_id = res['order_id']
#         order = Order.objects.get(id=order_id)
#         pay_info = PayInfo.objects.get(order_id=order_id)
#         margin = Margin.objects.get(user_id=self.user.id)
#         margin_record = MarginRecord.objects.filter(order_id=order_id)
#         self.assertEqual('失败', order.status)
#         self.assertEqual('失败', pay_info.status)
#         self.assertEqual(self.kuai_pay.ERR_CODE_WAITING, pay_info.error_code)
#         self.assertEqual(0, margin.margin)
#         self.assertEqual(0, margin_record.count())
#
#         mock_request_switch(self.kuai_pay)
#         request_body = PAY_RES.substitute(amount=self.amount_2, order_id=order.id,
#                                              user_id=self.user.id, res_code='00')
#
#         pm = self.kuai_pay.handle_pay_result(request_body)
#         print pm
#         result = self.kuai_pay.pay_callback(pm['user_id'],
#                                   pm['amount'],
#                                   pm['ret_code'],
#                                   pm['message'],
#                                   pm['order_id'],
#                                   pm['ref_number'],
#                                   pm['res_content'],
#                                   pm['signature'])
#         order = Order.objects.get(id=order_id)
#         pay_info = PayInfo.objects.get(order_id=order_id)
#         margin = Margin.objects.get(user_id=self.user.id)
#         margin_record = MarginRecord.objects.filter(order_id=order_id)
#         self.assertEqual('成功', order.status)
#         self.assertEqual('成功', pay_info.status)
#         self.assertEqual(self.amount_2, margin.margin)
#         self.assertEqual(1, margin_record.count())
#
#         self._clear_margin()
#
#     def test_qpay_tr3_fail(self):
#         """
#         一键支付tr3也失败
#         :return:
#         """
#         mock_request_switch(self.kuai_pay,status='wait')
#         res = self.kuai_pay.pre_pay(self.user, self.amount_2, self.short_card_no, self.input_phone, self.gate_id,
#                                     self.device, self.ip)
#         order_id = res['order_id']
#         order = Order.objects.get(id=order_id)
#         pay_info = PayInfo.objects.get(order_id=order_id)
#         margin = Margin.objects.get(user_id=self.user.id)
#         margin_record = MarginRecord.objects.filter(order_id=order_id)
#         self.assertEqual('失败', order.status)
#         self.assertEqual('失败', pay_info.status)
#         self.assertEqual(self.kuai_pay.ERR_CODE_WAITING, pay_info.error_code)
#         self.assertEqual(0, margin.margin)
#         self.assertEqual(0, margin_record.count())
#
#         request_body = PAY_RES.substitute(amount=self.amount_2, order_id=order.id,
#                                              user_id=self.user.id, res_code='01')
#         pm = self.kuai_pay.handle_pay_result(request_body)
#         print pm
#         result = self.kuai_pay.pay_callback(
#                                   pm['user_id'],
#                                   pm['amount'],
#                                   pm['ret_code'],
#                                   pm['message'],
#                                   pm['order_id'],
#                                   pm['ref_number'],
#                                   pm['res_content'],
#                                   pm['signature'])
#         order = Order.objects.get(id=order_id)
#         pay_info = PayInfo.objects.get(order_id=order_id)
#         margin = Margin.objects.get(user_id=self.user.id)
#         margin_record = MarginRecord.objects.filter(order_id=order_id)
#         self.assertEqual('失败', order.status)
#         self.assertEqual('失败', pay_info.status)
#         self.assertEqual(0, margin.margin)
#         self.assertEqual(0, margin_record.count())
#
#         self._clear_margin()
#
#     def test_qpay_tr3_losing_tr2(self):
#         """
#         一键支付，tr2信息没有接受到
#         :return:
#         """
#         mock_request_switch(self.kuai_pay,status='wait')
#         res = self.kuai_pay.pre_pay(self.user, self.amount_2, self.short_card_no, self.input_phone, self.gate_id,
#                                     self.device, self.ip, exit_for_test=True)
#         order_id = res['order_id']
#         order = Order.objects.get(id=order_id)
#         pay_info = PayInfo.objects.get(order_id=order_id)
#         margin = Margin.objects.get(user_id=self.user.id)
#         margin_record = MarginRecord.objects.filter(order_id=order_id)
#         self.assertEqual('处理中', order.status)
#         self.assertEqual('处理中', pay_info.status)
#         self.assertEqual(0, margin.margin)
#         self.assertEqual(0, margin_record.count())
#
#         request_body = PAY_RES.substitute(amount=self.amount_2, order_id=order.id,
#                                              user_id=self.user.id, res_code='00')
#         pm = self.kuai_pay.handle_pay_result(request_body)
#         print pm
#         result = self.kuai_pay.pay_callback(
#                                   pm['user_id'],
#                                   pm['amount'],
#                                   pm['ret_code'],
#                                   pm['message'],
#                                   pm['order_id'],
#                                   pm['ref_number'],
#                                   pm['res_content'],
#                                   pm['signature'])
#         order = Order.objects.get(id=order_id)
#         pay_info = PayInfo.objects.get(order_id=order_id)
#         margin = Margin.objects.get(user_id=self.user.id)
#         margin_record = MarginRecord.objects.filter(order_id=order_id)
#         self.assertEqual('成功', order.status)
#         self.assertEqual('成功', pay_info.status)
#         self.assertEqual(self.amount_2, margin.margin)
#         self.assertEqual(1, margin_record.count())


class PayOrderTest(PayTests):
    def setUp(self):
        super(PayOrderTest, self).setUp()
        self.pay_order = PayOrder()

    def test_order_before_pay_success_without_card(self):
        order_id = self.pay_order.order_before_pay(self.user, self.amount_1, self.gate_id,
                                                self.ip, self.device)
        pay_info = PayInfo.objects.get(order_id=order_id)
        self.assertEqual(self.amount_1, pay_info.amount)
        self.assertEqual(self.user, pay_info.user)


    def test_order_before_pay(self):
        # def order_before_pay(self, user, amount, card_no, gate_id, phone_for_card, request_ip, device):
        #     return order.id
        order_id = self.pay_order.order_before_pay(self.user, self.amount_1, self.gate_id,
                                                self.ip, self.device, self.card_no, self.input_phone)
        pay_info = PayInfo.objects.get(order_id=order_id)
        self.assertEqual(self.amount_1, pay_info.amount)
        self.assertEqual(self.user, pay_info.user)

    def test_order_after_pay_success(self):
        # def order_after_pay_succcess(self, amount, order_id, res_ip, res_content):
        #    rs = {"ret_code": 0, "message": "success", "amount": amount, "margin": margin_record.margin_current,
        #       "order_id": order_id}
        # 正常
        margin_before = Margin.objects.get(user_id=self.user.id).margin
        order_id = self.pay_order.order_before_pay(self.user, self.amount_1, self.gate_id,
                                                self.ip, self.device, self.card_no, self.input_phone)
        rs = self.pay_order.order_after_pay_succcess(self.amount_1, order_id, 'res_ip', 'res_content', self.request)
        self.assertEqual(PayInfo.objects.get(order_id=order_id).status, PayInfo.SUCCESS)
        margin_after = Margin.objects.get(user_id=self.user.id).margin
        self.assertEqual(margin_after-margin_before, self.amount_1)
        margin_record_amount = MarginRecord.objects.get(order_id=order_id).amount
        self.assertEqual(margin_record_amount, self.amount_1)


    def test_order_after_pay_success_add_card(self):
        # def order_after_pay_succcess(self, amount, order_id, res_ip, res_content):
        #    rs = {"ret_code": 0, "message": "success", "amount": amount, "margin": margin_record.margin_current,
        #       "order_id": order_id}
        # 正常
        margin_before = Margin.objects.get(user_id=self.user.id).margin
        order_id = self.pay_order.order_before_pay(self.user, self.amount_1, self.gate_id,
                                                self.ip, self.device, self.card_no, self.input_phone)
        rs = self.pay_order.order_after_pay_succcess(self.amount_1, order_id, 'res_ip', 'res_content', self.request,
                                                     need_bind_card=True)
        self.assertEqual(PayInfo.objects.get(order_id=order_id).status, PayInfo.SUCCESS)
        margin_after = Margin.objects.get(user_id=self.user.id).margin
        self.assertEqual(margin_after-margin_before, self.amount_1)
        margin_record_amount = MarginRecord.objects.get(order_id=order_id).amount
        self.assertEqual(margin_record_amount, self.amount_1)
        Card.objects.filter(no=self.card_no).exists()


    def test_order_after_pay_error(self):
        # def order_after_pay_error(self, error, order_id):
        # return {"ret_code": error_code, "message": error_message, 'order_id':order_id, 'pay_info_id':pay_info.id}
        # 正常
        margin_before = Margin.objects.get(user_id=self.user.id).margin
        order_id = self.pay_order.order_before_pay(self.user, self.amount_1, self.gate_id,
                                                self.ip, self.device, self.card_no, self.input_phone)
        rs = self.pay_order.order_after_pay_error(ThirdPayError(77777, 'illegal condition within pay'), order_id)

        self.assertEqual(PayInfo.objects.get(order_id=order_id).status, PayInfo.FAIL)
        margin_after = Margin.objects.get(user_id=self.user.id).margin
        self.assertEqual(margin_after-margin_before, self.amount_0)
        self.assertRaises(ObjectDoesNotExist, MarginRecord.objects.get, order_id=order_id)
        # todo urgent 异常 transaction

    # def test_order_restart_fail(self):
    #     order_id = self.pay_order.order_before_pay(self.user, self.amount_1, self.gate_id,
    #                                             self.ip, self.device, self.card_no, self.input_phone)
    #     rs = self.pay_order.order_after_pay_error(ThirdPayError(77777, 'illegal condition within pay'), order_id)
    #     self.pay_order.order_after_pay_succcess
    #     self.pay_order.order_restart_fail(order_id)

#     todo better 覆盖：短卡号




class YeeProxyPayCallbackMessageTest(TestCase):
    def test_parse_message_test(self):
        request_get_para = dict(p1_MerId='10001126856',
                           r0_Cmd='Buy',
                           r1_Code='1',
                           r2_TrxId='418329545762402G',
                           r3_Amt='0.01',
                           r4_Cur='RMB',
                           r5_Pid='Wanglibao',
                           r6_Order='1925745',
                           r7_Uid='',
                           r8_MP='',
                           r9_BType='1',
                           ru_Trxtime='20151119130908',
                           ro_BankOrderId='1490128225',
                           rb_BankId='YJZF-NET',
                           rp_PayDate='20151119130907',
                           rq_CardNo='',
                           rq_SourceFee='0.0',
                           rq_TargetFee='0.0',
                           hmac='4d433af4e4eea2a6d054e8f1864810a4')
        pay_message = YeeProxyPayCallbackMessage().parse_message(request_get_para, 'response')
        self.assertEqual(0.01, float(pay_message.amount))
        self.assertEqual(1925745, pay_message.order_id)


















