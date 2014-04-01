# encoding: utf-8
import datetime

from django.test import TestCase
from django.utils import timezone
from wanglibao_sms.backends import TestBackEnd, UrlBasedSMSBackEnd
from wanglibao_sms.models import PhoneValidateCode
from wanglibao_sms.utils import send_validation_code, validate_validation_code


class BackEndTestCase(TestCase):

    def test_test_backend(self):
        status, message = TestBackEnd.send('13800000000', 'Dummy text')
        self.assertEqual(status, 200)

    # def test_url_backend(self):
    #    status, message = UrlBasedSMSBackEnd.send('13146871968', u'网利宝验证码：123456，30分钟有效，请不要泄露给他人。如非本人操作，可不必理会。')
    #    self.assertEqual(status, 200)

    def test_validation_flow(self):
        phone = '12345222223'
        validate_code = '111111'

        status, message = send_validation_code(phone, validate_code)
        self.assertEqual(status, 200)

        status, message = validate_validation_code(phone, validate_code)
        self.assertEqual(status, 200)

        record = PhoneValidateCode.objects.get(phone=phone)
        record.last_send_time = timezone.now() - datetime.timedelta(hours=1)
        record.save()
        status, message = validate_validation_code(phone, validate_code)

        self.assertEqual(status, 410)

