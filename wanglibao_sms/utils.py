import random
from django.conf import settings
from django.template.loader import render_to_string
import datetime
from django.utils import timezone
from wanglibao_sms.backends import UrlBasedSMSBackEnd, TestBackEnd
from wanglibao_sms.models import PhoneValidateCode
import logging
logger = logging.getLogger(__name__)


def generate_validate_code():
    return "%d" % (random.randrange(100000, 1000000))


def send_sms(phone, message):
    logger.debug('Send short messages')
    backend = settings.SMS_BACKEND
    class_name = backend.split('.')[-1]

    if class_name == 'TestBackEnd':
        return TestBackEnd.send(phone, message)
    elif class_name == 'UrlBasedSMSBackEnd':
        return UrlBasedSMSBackEnd.send(phone, message)
    else:
        raise NameError("The specific backend not implemented")


def send_validation_code(phone, validate_code=None):
    if validate_code is None:
        validate_code = generate_validate_code()

    now = timezone.now()
    try:
        phone_validate_code_item = PhoneValidateCode.objects.get(phone=phone)

        if (now - phone_validate_code_item.last_send_time) <= datetime.timedelta(minutes=1):
            return 429, "Called too frequently"
        else:
            phone_validate_code_item.validate_code = validate_code
            phone_validate_code_item.last_send_time = now
            phone_validate_code_item.code_send_count += 1
            phone_validate_code_item.save()
    except PhoneValidateCode.DoesNotExist:
        PhoneValidateCode.objects.create(
            phone=phone,
            validate_code=validate_code,
            last_send_time=now,
            code_send_count=1)

    content = render_to_string('html/activation-sms.html', {'validation_code': validate_code})
    status, message = send_sms(phone, content)

    if status != 200:
        return status, message

    return 200, ''


def validate_validation_code(phone, code):
    status_code, message = 404, ''
    try:
        phone_validate_item = PhoneValidateCode.objects.get(phone=phone)
        now = timezone.now()

        if phone_validate_item.validate_code == code:
            if (now - phone_validate_item.last_send_time) >= datetime.timedelta(minutes=30):
                status_code, message = 410, 'The code is expired'

            else:
                phone_validate_item.is_validated = True
                phone_validate_item.save()

                status_code, message = 200, ''

        else:
            pass

    except PhoneValidateCode.DoesNotExist:
        pass

    return status_code, message
