# encoding=utf-8
from django.test import TestCase
from django.core.management.base import BaseCommand

# class KuaiPayBindPayTest(TestCase):
class Command(BaseCommand):
    """
    测试快钱绑卡后使用验证码和不使用验证码两种模式
    """
    def setUp(self):
        from wanglibao_pay.kuai_pay import KuaiShortPay
        from wanglibao_profile.models import WanglibaoUserProfile
        from wanglibao_pay.models import Card

        self.kuai_short_pay = KuaiShortPay()
        # self.phone = raw_input('phone: ').strip()
        # self.card_no = raw_input('card_no: ').strip()
        self.phone = '15011488086'
        self.card_no = '6225880145470549'

        self.short_card_no = self.card_no[:6] + self.card_no[-4:]
        self.user = WanglibaoUserProfile.objects.get(phone=self.phone).user     
        self.gate_id = Card.objects.get(no=self.card_no).bank.gate_id

    def test_bind_pay(self):
        print self.kuai_short_pay.pre_pay(self.user, 0.01, self.card_no,
                                          self.phone, self.gate_id, '', '', '')
        order_id = raw_input('order_id: ').strip()
        token = raw_input('token: ').strip() 
        vcode = raw_input('vcode: ').strip()
        print self.kuai_short_pay.dynnum_bind_pay(self.user, vcode, order_id, token, 
                                                  '', '', '', '')
    def test_qpay_no_vcode(self):
        print self.kuai_short_pay.pre_pay(self.user, 0.01, self.short_card_no,
                                          self.phone, self.gate_id, '', '', '',)

    def test_qpay_with_vcode(self):
        print self.kuai_short_pay.pre_pay(self.user, 0.01, self.short_card_no,
                                          self.phone, self.gate_id, '', '', '',
                                          mode='vcode_for_qpay')
        order_id = raw_input('order_id: ').strip()
        token = raw_input('token: ').strip() 
        vcode = raw_input('vcode: ').strip()
        print self.kuai_short_pay.dynnum_bind_pay(self.user, vcode, order_id, token, 
                                                  '', '', '', '', mode='qpay_with_sms')

    def handle(self, *args, **options):
        self.setUp()
        self.test_bind_pay()
        raw_input('continue/kill')
        self.test_qpay_no_vcode()
        raw_input('continue/kill')
        self.test_qpay_with_vcode()
