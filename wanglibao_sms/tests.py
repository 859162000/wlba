# encoding: utf-8
import datetime

from django.test import TestCase
from django.utils import timezone
from wanglibao_sms.backends import TestBackEnd, ManDaoSMSBackEnd
from wanglibao_sms.models import PhoneValidateCode
from wanglibao_sms.utils import send_validation_code, validate_validation_code


class BackEndTestCase(TestCase):

    def test_test_backend(self):
        status, message = TestBackEnd.send('13800000000', 'Dummy text')
        self.assertEqual(status, 200)

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

    def test_mandao_backend(self):
        status, message = ManDaoSMSBackEnd.send('15011488086', u'手机尾号[2323]的验证码是[1234]，欢迎使用网利宝，您的贴心理财专家！回复TD退订 400-855-9600【网利宝】')
        self.assertEqual(status, 200)
