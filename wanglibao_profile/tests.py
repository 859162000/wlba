# encoding=utf8

from django.contrib.auth.models import User
from django.test import TestCase
import simplejson
from wanglibao_account.test_util import prepare_user_with_profile
from wanglibao_profile.backends import trade_pwd_set, trade_pwd_is_set, trade_pwd_check
from wanglibao_profile.models import WanglibaoUserProfile


class ProfileAPITest(TestCase):
    def test_update_profile(self):
        # Set up a user
        test_user = 'testuser'
        test_phone = '13999999999'
        test_password = 'password1'
        test_nickname = 'test'
        test_id_number = '12312312412412412413123'
        test_access_token = '12312321312'

        new_user = User.objects.create(username='testuser')
        new_user.set_password(test_password)
        new_user.is_active = True
        new_user.save()

        new_user.wanglibaouserprofile.phone = test_phone
        new_user.wanglibaouserprofile.phone_verified = True
        new_user.wanglibaouserprofile.nick_name = test_nickname
        new_user.wanglibaouserprofile.save()

        self.client.login(identifier=test_phone, password=test_password)
        response = self.client.put('/api/profile/', simplejson.dumps({
            'id_number': test_id_number
        }), content_type="application/json")

        self.assertEqual(response.status_code, 200)

        user = User.objects.get(pk=new_user.pk)
        self.assertEqual(user.wanglibaouserprofile.id_number, test_id_number)

        self.client.put('/api/profile/', simplejson.dumps({
            'shumi_access_token': test_access_token
        }), content_type="application/json")

        user = User.objects.get(pk=new_user.pk)
        self.assertEqual(user.wanglibaouserprofile.shumi_access_token, test_access_token)

class TradePasswdTest(TestCase):
    def setUp(self):
        self.profile = prepare_user_with_profile()

    def test_set_and_check(self):
        trade_pwd_set(self.profile.user_id, 1, new_trade_pwd='123456')
        assert trade_pwd_is_set(self.profile.user_id) == True
        self.assertEqual(trade_pwd_check(self.profile.user_id, '123456'),
                         {'ret_code': 0, 'message': '交易密码正确', 'retry_count': 3})
        #测试锁定次数
        self.assertEqual(trade_pwd_check(self.profile.user_id, '0123456'), {'ret_code': 30047, 'message': '交易密码错误', 'retry_count': 2})
        self.assertEqual(trade_pwd_check(self.profile.user_id, '0123456'), {'ret_code': 30047, 'message': '交易密码错误', 'retry_count': 1})
        self.assertEqual(trade_pwd_check(self.profile.user_id, '0123456'), {'ret_code': 30047, 'message': '交易密码错误', 'retry_count': 0})
        self.assertEqual(trade_pwd_check(self.profile.user_id, '123456'), {'ret_code':30048, 'message': '重试次数过多，交易密码被锁定', 'retry_count': 0})
        #测试锁定时间
        self.profile = WanglibaoUserProfile.objects.get(user__id=self.profile.user_id)
        self.profile.trade_pwd_last_failed_time = self.profile.trade_pwd_last_failed_time - 3600*3
        self.profile.save()
        self.assertEqual(trade_pwd_check(self.profile.user_id, '123456'), {'ret_code': 0, 'message': '交易密码正确', 'retry_count': 3})



