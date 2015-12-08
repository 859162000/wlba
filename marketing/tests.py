# encoding:utf-8
from django.contrib.auth.models import User
from wanglibao_account.models import Binding
from wanglibao_p2p.models import P2PRecord
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from wanglibao_profile.models import WanglibaoUserProfile
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

        WanglibaoUserProfile.objects.create(
            user_id=3,
            id_number=371322198606053816,
            name='yihen',
            id_is_valid=True
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


    def test_send_sms(self):
        response = self.client.post("/api/inner/send_sms/",
                                    {
                                        'phone': 13521522035,
                                        'message': "hello world"
                                    })

        print response.content


    def test_validate_id(self):
        response = self.client.post("/api/inner/validate_id/",
                                    {
                                        "id":371322198606063816,
                                        'name':"yihen"
                                    }
                                    )

        print response.content

    def test_save_channel(self):
        response = self.client.post("/api/inner/save_channel/",
                                    {
                                    })

        print response.content