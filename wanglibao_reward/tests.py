# encoding:utf-8
from django.contrib.auth.models import User
from wanglibao_account.models import Binding
from wanglibao_p2p.models import P2PRecord
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

# Create your tests here.
from marketing.models import InviteCode, GiftOwnerGlobalInfo
from wanglibao_sms.utils import send_validation_code
from wanglibao_reward.models import WanglibaoActivityReward

class TestThanksGivenAPI(TestCase):
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

        WanglibaoActivityReward.objects.create(
            user=user,
            activity="ThanksGiven",
            left_times=3,
            join_times=3,
            redpack_event_id=1,
            reward_id=21
        )
        Binding.objects.create(
            user_id=1,
            access_token=u'xunlei'
        )

        P2PRecord.objects.create(
            user_id=1,
            amount=2000,
            catalog=u'申购'
        )

    def test_distribute(self):
        self.client = Client()
        self.client.login(username="Tester", password='123456')
        response = self.client.post("/api/activity/reward/",
                                    {
                                        'activity':"thanks_givens",
                                        'action': "POINT_AT"
                                    }
                                    )
        print response.content

