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
        self.phone = raw_input('phone: ').strip()
        self.card_no = raw_input('card_no: ').strip()

        self.short_card_no = self.card_no[:6] + self.card_no[-4:]
        self.user = WanglibaoUserProfile.objects.get(phone=self.phone).user     
        self.gate_id = Card.objects.get(no=self.card_no).bank.gate_id

    def test_no_vcode(self):
        print self.kuai_short_pay.pre_pay(self.user, 0.01, self.short_card_no,
                                          self.phone, self.gate_id, '', '', '',)

    def test_with_vcode(self):
        print self.kuai_short_pay.pre_pay(self.user, 0.01, self.card_no,
                                          self.phone, self.gate_id, '', '', '')
        token = raw_input('token: ').strip() 
        vcode = raw_input('vcode: ').strip()
        print self.kuai_short_pay.pre_pay(self.user, 0.01, self.short_card_no,
                                          self.phone, self.gate_id, '', '', '',
                                          vcode=vcode, token=token)

    def handle(self, *args, **options):
        self.setUp()
        self.test_no_vcode()
        self.test_with_vcode()
