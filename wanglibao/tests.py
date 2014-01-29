from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.datetime_safe import datetime
from wanglibao.forms import EmailOrPhoneRegisterForm
from wanglibao_profile.models import PhoneValidateCode


class EmailOrPhoneRegisterFormTestCase(TestCase):
    def setUp(self):
        pass

    def test_register_by_email(self):
        form_data = {
            'identifier': 'test@test.com',
            'type': 'email',
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
            'type': 'phone',
            'password': 'testpassword',
        }

        form = EmailOrPhoneRegisterForm(data=form_data)
        self.assertEqual(form.is_valid(), True)


class RegisterViewTestCase(TestCase):

    def test_email_register(self):
        self.client.post("/accounts/register/", {
            'identifier': 'test@test.com',
            'type': 'email',
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
            'type': 'phone',
            'password': 'testpassword',
        })

        user = User.objects.get(wanglibaouserprofile__phone=phone)
        self.assertEqual(phone, user.wanglibaouserprofile.phone)


class LoginTestCase(TestCase):
    def test_login_email(self):
        user = User.objects.create(username='test', email='test@test.com')
        user.set_password('pass')
        user.save()

        response = self.client.post("/accounts/login", {
            'email': 'test@test.com',
            'password': 'pass'
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        response = self.client.post("/accounts/login", {
            'email': 'test@test.com',
            'password': 'pass_wrong'
        }, follow=True)

        self.assertEqual(response.status_code, 200)