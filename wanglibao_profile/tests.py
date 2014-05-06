from django.contrib.auth.models import User
from django.test import TestCase
import simplejson


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

