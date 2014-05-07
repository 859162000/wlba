from urlparse import urlparse

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from forms import EmailOrPhoneRegisterForm
from utils import detect_identifier_type
from wanglibao_sms.models import PhoneValidateCode
from wanglibao_sms.utils import send_validation_code


class EmailOrPhoneRegisterFormTestCase(TestCase):
    def test_register_by_email(self):
        form_data = {
            'nickname': 'nickname',
            'identifier': 'test@test.com',
            'password': 'testpassword',
        }

        form = EmailOrPhoneRegisterForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_register_by_phone(self):
        phone = "13811111111"
        validate_code = "133223"
        send_validation_code(phone, validate_code)
        form_data = {
            'nickname': 'nickname',
            'identifier': '13811111111',
            'validate_code': '133223',
            'password': 'testpassword',
        }

        form = EmailOrPhoneRegisterForm(data=form_data)
        self.assertEqual(form.is_valid(), True)


class RegisterViewTestCase(TestCase):

    def test_phone_duplicate(self):
        phone = '12345678901'

        # fake user is validated by mail, but he has an unverified phone number
        fake_user = User.objects.create(username='fake')
        fake_user.wanglibaouserprofile.phone = phone
        fake_user.wanglibaouserprofile.phone_verified = False
        fake_user.wanglibaouserprofile.save()

        # The real user not registered, but holds the true phone
        validate_code = '123456'
        send_validation_code(phone, validate_code)

        self.client.post("/accounts/register/", {
            'nickname': 'nickname',
            'identifier': phone,
            'validate_code': validate_code,
            'password': 'testpassword'
        })

        user = User.objects.get(wanglibaouserprofile__phone=phone, wanglibaouserprofile__phone_verified=True)
        self.assertTrue(user.wanglibaouserprofile.phone_verified)


class PasswordChangeTestCase(TestCase):

    def test_password_change(self):
        oldpassword = 'testpassword'
        new_password = 'newtestpassword'
        user = User.objects.create(username="testuser", email="testuser@test.com")
        user.set_password(oldpassword)
        user.save()

        response = self.client.post("/accounts/password/change/", {
            'old_password': oldpassword,
            'new_password1': new_password,
            'new_password2': new_password
        })

        self.assertEqual(response.status_code, 302)

        self.assertTrue(self.client.login(identifier='testuser@test.com', password=oldpassword))

        response = self.client.post("/accounts/password/change/", {
            'old_password': oldpassword,
            'new_password1': new_password,
            'new_password2': new_password
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.find('done') >= 0)

        # Now test one error case
        response = self.client.post("/accounts/password/change/", {
            'old_password': 'wrongpass',
            'new_password1': new_password,
            'new_password2': new_password
        })

        self.assertEqual(response.status_code, 400)


class LoginTestCase(TestCase):
    default_username = 'default_user'
    default_pass = 'password'
    default_phone = '13333333333'

    def test_login_email(self):
        user = User.objects.create(username='test', email='test@test.com')
        user.set_password('pass')
        user.save()

        response = self.client.post("/accounts/login/", {
            'identifier': 'test@test.com',
            'password': 'pass'
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.url).path, settings.LOGIN_REDIRECT_URL)

        response = self.client.post("/accounts/login/", {
            'identifier': 'test@test.com',
            'password': 'pass_wrong'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, 'login.jade')


    def test_login_phone(self):
        user = User.objects.create(username='test')
        user.set_password(self.default_pass)
        user.save()
        user.wanglibaouserprofile.phone = self.default_phone
        user.wanglibaouserprofile.phone_verified = True
        user.wanglibaouserprofile.save()

        response = self.client.post("/accounts/login/", {
            'identifier': self.default_phone,
            'password': self.default_pass
        })

        self.assertEqual(response.status_code, 302)


class UtilityTestCase(TestCase):
    def test_detect_identifier_type(self):
        type = detect_identifier_type('13000000000')
        self.assertEqual('phone', type)

        type = detect_identifier_type('x@c.com')
        self.assertEqual('email', type)

        type = detect_identifier_type('')
        self.assertEqual('unknown', type)


class EndToEndTestCase(TestCase):
    def test_register_with_email(self):
        self.client.post("/accounts/register/", {
            'nickname': 'nickname',
            'identifier': 'test@test.com',
            'password': 'testpassword',
        })

        user = User.objects.get(email='test@test.com')
        self.assertEqual('test@test.com', user.email)

    def test_register_with_phone(self):
        phone = '12345123232'

        self.client.post("/api/phone_validation_code/register/%s/" % (phone,), {})

        validate_code = PhoneValidateCode.objects.get(phone=phone).validate_code

        self.client.post("/accounts/register/", {
            'nickname': 'nickname',
            'identifier': phone,
            'validate_code': validate_code,
            'password': 'testpassword',
        })

        user = User.objects.get(wanglibaouserprofile__phone=phone)
        self.assertEqual(phone, user.wanglibaouserprofile.phone)
        self.assertTrue(user.is_active)
        self.assertTrue(user.wanglibaouserprofile.phone_verified)

    def test_reset_password_by_email(self):
        self.client.post("/accounts/register/", {
            'nickname': 'nickname',
            'identifier': 'test@test.com',
            'password': 'testpass'
        })

        user = User.objects.get(email='test@test.com')
        user.is_active = True
        user.save()

        response = self.client.post("/accounts/password/reset/identifier/", {
            'identifier_wrong': 'test@test.com'
        })

        self.assertEqual(response.status_code, 400)

        response = self.client.post("/accounts/password/reset/identifier/", {
            'identifier': 'test@test.com'
        })

        self.assertEqual(response.status_code, 200)
