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
from misc.models import Misc
from marketing.models import Reward

class TestMarketingAPI(TestCase):
    def setUp(self):
        InviteCode.objects.create(
            code='wanglibao',
            is_used=False
        )


        reward = Reward.objects.filter(type='金融摇滚夜').first()
        Reward.objects.create(
            type="金融摇滚夜",
            content="abcdefg"
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
            access_token=u'rock'
        )

        P2PRecord.objects.create(
            user_id=1,
            order_id=123456,
            amount=2000,
            catalog=u'申购'
        )

        WanglibaoUserProfile.objects.create(
            user_id=3,
            id_number=371322198606053816,
            name='yihen',
            id_is_valid=True
        )
        Misc.objects.create(
            key="activities",
            value='{"valid_activity":"thanks_given","rock_finance":{"amount":800, "start_time":"2015-12-09 12:00:00", "is_open":"true", "end_time":"2015-12-25 12:00:00"}}',
        )

    def test_rock_finance(self):
        client = Client()
        client.login(username="Tester", password="123456")
        responses = client.post("/api/rock/finance/vote/",
                                    {
                                        "catalog":"chenkun",
                                        "item": "alone"
                                    })

        response = client.get("/api/rock/finance/vote/")
        print response.content

