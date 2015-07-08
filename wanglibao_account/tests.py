# coding=utf-8
from urlparse import urlparse

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from forms import EmailOrPhoneRegisterForm
from utils import detect_identifier_type, verify_id, create_user
from wanglibao_account.backends import parse_id_verify_response
from wanglibao_account.cooperation import CoopRegister
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

    def test_register(self):
        phone = '12345678901'

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


class IdVerificationTestCase(TestCase):
    def test_verify_id(self):
        verification, error = verify_id(u'李硕', '130702198408260655')

        self.assertIsNone(error)

    def test_parse_response(self):
        response = u"""
            <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
               <s:Body>
                  <SimpleCheckResponse xmlns="http://www.nciic.com.cn">
                     <SimpleCheckResult xmlns:a="http://schemas.datacontract.org/2004/07/Finance.EPM" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
                        <a:ResponseCode>100</a:ResponseCode>
                        <a:ResponseText>成功</a:ResponseText>
                        <a:Identifier>
                           <a:Address i:nil="true"/>
                           <a:BirthPlace i:nil="true"/>
                           <a:Birthday>1984-08-26</a:Birthday>
                           <a:Company i:nil="true"/>
                           <a:Education i:nil="true"/>
                           <a:FormerName i:nil="true"/>
                           <a:IDNumber>130702198408260655</a:IDNumber>
                           <a:IsQueryCitizen>false</a:IsQueryCitizen>
                           <a:MaritalStatus i:nil="true"/>
                           <a:Name>李硕</a:Name>
                           <a:Nation i:nil="true"/>
                           <a:NativePlace i:nil="true"/>
                           <a:Photo/>
                           <a:QueryTime i:nil="true"/>
                           <a:Result>一致</a:Result>
                           <a:Sex>男性</a:Sex>
                        </a:Identifier>
                        <a:RawXml i:nil="true"/>
                     </SimpleCheckResult>
                  </SimpleCheckResponse>
               </s:Body>
            </s:Envelope>"""

        r = parse_id_verify_response(response)
        self.assertEqual(r['response_code'], 100)

    def test_one_user_only_verify_2_times(self):
        identifier = '13800000000'
        password = 'testpass'

        create_user(identifier=identifier, password=password, nickname=identifier)

        self.client.login(identifier=identifier, password=password)

        response = self.client.post("/accounts/id_verify/", {
            'name': 'testName',
            'id_number': '12386718523671243574'
        })

        self.assertEqual(response.status_code, 302)

        response = self.client.post("/accounts/id_verify/", {
            'name': 'testName',
            'id_number': '12386718523671243574'
        })

        self.assertEqual(response.status_code, 302)

        response = self.client.post("/accounts/id_verify/", {
            'name': 'testName',
            'id_number': '12386718523671243574'
        })

        self.assertEqual(response.status_code, 200)

class CooperationTestCase(TestCase):
    def setUp(self):
        coop_register = CoopRegister()
    def test_all_processors_for_session(self):
