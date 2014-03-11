from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.datetime_safe import datetime
from wanglibao.forms import EmailOrPhoneRegisterForm
from wanglibao.utils import detect_identifier_type
from wanglibao_profile.models import PhoneValidateCode


class EmailOrPhoneRegisterFormTestCase(TestCase):
    def setUp(self):
        pass

    def test_register_by_email(self):
        form_data = {
            'identifier': 'test@test.com',
            'password': 'testpassword',
        }

        form = EmailOrPhoneRegisterForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_register_by_phone(self):
        validate_code_record = PhoneValidateCode.objects.create(
            phone="13810652323",
            validate_code="133223",
            last_send_time=datetime.now(),
        )
        validate_code_record.save()

        form_data = {
            'identifier': '13810652323',
            'validate_code': '133223',
            'password': 'testpassword',
        }

        form = EmailOrPhoneRegisterForm(data=form_data)
        self.assertEqual(form.is_valid(), True)


class RegisterViewTestCase(TestCase):

    def test_email_register(self):
        self.client.post("/accounts/register/", {
            'identifier': 'test@test.com',
            'password': 'testpassword',
        })

        user = User.objects.get(email='test@test.com')
        self.assertEqual('test@test.com', user.email)

    def test_phone_register(self):
        phone = '12345123232'
        validate_code = "132232"

        validate_code_record = PhoneValidateCode.objects.create(
            phone=phone,
            validate_code=validate_code,
            last_send_time=datetime.now(),
        )
        validate_code_record.save()

        self.client.post("/accounts/register/", {
            'identifier': phone,
            'validate_code': validate_code,
            'password': 'testpassword',
        })

        user = User.objects.get(wanglibaouserprofile__phone=phone)
        self.assertEqual(phone, user.wanglibaouserprofile.phone)
        self.assertTrue(user.is_active)
        self.assertTrue(user.wanglibaouserprofile.phone_verified)

    def test_phone_duplicate(self):
        phone = '12345678901'

        # fake user is validated by mail, but he has an unverified phone number
        fake_user = User.objects.create(username='fake')
        fake_user.wanglibaouserprofile.phone = phone
        fake_user.wanglibaouserprofile.phone_verified = False
        fake_user.wanglibaouserprofile.save()

        # The real user not registered, but holds the true phone
        validate_code = '123456'
        validate_code_record = PhoneValidateCode()
        validate_code_record.validate_code = validate_code
        validate_code_record.phone = phone
        validate_code_record.last_send_time = datetime.now()

        validate_code_record.save()

        self.client.post("/accounts/register/", {
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
    def test_login_email(self):
        user = User.objects.create(username='test', email='test@test.com')
        user.set_password('pass')
        user.save()

        response = self.client.post("/accounts/login", {
            'identifier': 'test@test.com',
            'password': 'pass'
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        response = self.client.post("/accounts/login", {
            'identifier': 'test@test.com',
            'password': 'pass_wrong'
        }, follow=True)

        self.assertEqual(response.status_code, 200)


class UtilTestCase(TestCase):
    def test_detect_identifier_type(self):
        type = detect_identifier_type('13000000000')
        self.assertEqual('phone', type)

        type = detect_identifier_type('x@c.com')
        self.assertEqual('email', type)

        type = detect_identifier_type('')
        self.assertEqual('unknown', type)