# encoding:utf-8
from django.contrib.auth.models import User
from wanglibao_account.models import Binding
from wanglibao_p2p.models import P2PRecord
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

# Create your tests here.
from marketing.models import InviteCode, GiftOwnerGlobalInfo
from wanglibao_sms.utils import send_validation_code


class TestMarketingAPI(TestCase):
    def setUp(self):
        InviteCode.objects.create(
            code='wanglibao',
            is_used=False
        )

        GiftOwnerGlobalInfo.objects.create(
            description='jcw_ticket_80',
            amount=30,
            valid=True,
        )
        GiftOwnerGlobalInfo.objects.create(
            description='jcw_ticket_188',
            amount=100,
            valid=True,
        )

        user = User.objects.create_user(username="Tester", email='tester@wanglibao.com', password='123456')
        user.is_active = True
        user.save()

        Binding.objects.create(
            user_id=1,
            access_token=u'xunlei'
        )

        P2PRecord.objects.create(
            user_id=1,
            amount=2000,
            catalog=u'申购'
        )

    def test_quick_applyer(self):
        response = self.client.post("/api/quick/applyer/",
                         {
                            'phone':13521522034,
                             'name':'hello',
                             'address': u'北京',
                             'apply_way': 0,
                             'amount': '10-30'
                         }
                         )
        print response.content

    def test_gift_owner(self):
        client = Client()
        client.login(username="Tester", password='123456')
        response = client.post("/api/gift/owner/?promo_token=jcw",
                        {
                            'phone': 13423444354,
                            'name': 'Yihen',
                            'address': u"北京市朝阳区"
                        })
        print response.content
