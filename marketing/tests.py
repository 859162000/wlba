from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

# Create your tests here.
from marketing.models import IntroducedBy
from wanglibao_sms.utils import send_validation_code


class TestPromoCodeCreation(TestCase):
    def test_promo_code_creation(self):
        u = User(username='test', password='hehehehe')
        u.save()

        self.assertIsNotNone(u.promotiontoken)


    def test_promo_code_connection(self):
        u = User(username='test', password='hehehe')
        u.save()

        phone = '12345678901'
        # The real user not registered, but holds the true phone
        validate_code = '123456'
        send_validation_code(phone, validate_code)

        self.client.post("/accounts/register/?promo_token=%s" % u.promotiontoken.token, {
            'nickname': 'nickname',
            'identifier': phone,
            'validate_code': validate_code,
            'password': 'testpassword'
        })

        connection = IntroducedBy.objects.all()[0]
        self.assertEqual(connection.user.wanglibaouserprofile.phone, phone)
        self.assertEqual(connection.introduced_by.username, 'test')
