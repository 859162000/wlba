from django.contrib.auth import get_user_model
from django.test import TestCase
from wanglibao_sms.models import PhoneValidateCode

User = get_user_model()

# test 1234

class APITestCase(TestCase):
    def test_register_with_api(self):
        """
        Testing logic:
        1. Create the validate code
        2. Send the request with invalid code
            check the error code, no user created

        3. Send the request with correct code
            check that the user created and can be logged in with password

        """
        phone = '13811111111'
        password = 'wanglibank'

        response = self.client.post('/api/phone_validation_code/%s/' % phone, {})

        self.assertEqual(response.status_code, 200)

        validate_code = PhoneValidateCode.objects.all()[0].validate_code

        # Wrong validate code
        response = self.client.post('/api/register/', {
            'identifier': phone,
            'password': password,
            'validate_code': validate_code + '9',
            'nickname': 'nickname'
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(wanglibaouserprofile__phone=phone).exists())

        # Correct validate code
        response = self.client.post('/api/register/', {
            'identifier': phone,
            'password': password,
            'validate_code': validate_code,
            'nickname': 'nickname'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(wanglibaouserprofile__phone=phone).exists())

    def test_reset_with_api(self):
        phone = '13811111111'
        password = 'wanglibank'

        response = self.client.post('/api/phone_validation_code/%s/' % phone, {})

        self.assertEqual(response.status_code, 200)

        validate_code = PhoneValidateCode.objects.all()[0].validate_code

        # Correct validate code
        response = self.client.post('/api/register/', {
            'identifier': phone,
            'password': password,
            'validate_code': validate_code,
            'nickname': 'nickname'
        })

        self.assertEqual(response.status_code, 200)

        validate_code = PhoneValidateCode.objects.all()[0].validate_code

        new_pass = 'wanglibank_new'
        # Wrong validate code
        response = self.client.post('/api/reset_password/', {
            'identifier': phone,
            'new_password': new_pass,
            'validate_code': validate_code,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(wanglibaouserprofile__phone=phone).exists())

        u = User.objects.filter(wanglibaouserprofile__phone=phone).first()
        self.assertTrue(u.check_password(new_pass))