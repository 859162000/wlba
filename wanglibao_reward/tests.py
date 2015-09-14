# encoding:utf-8
from django.test import TestCase
from django.contrib.auth.models import User

from wanglibao_reward.models import WanglibaoActivityGift, WanglibaoActivityGiftGlobalCfg,WanglibaoUserGift


class TestActivityGift(TestCase):
    def setUp(self):
        User.objects.create(email='liuyihen@wanglibank.com',password=u"123456")

    def test_log_in(self):
        user = User.objects.filter(email='liuyihen@wanglibank.com')
        self.assertEquals(user.password, "123456", u"登录失败")
