from django.conf import settings
import requests
import logging


logger = logging.getLogger(__name__)


class SMSBackEnd(object):
    """
    The sms sending backend
    """

    @classmethod
    def send(cls, phone, text):
        """
        send the text to the phone number
        """
        raise NotImplemented("The method not implemented yet")

    @classmethod
    def send_messages(cls, phones, messages):
        raise NotImplemented("The method not implemented yet")


class TestBackEnd(SMSBackEnd):
    """
    The test backend which always success when called
    """
    @classmethod
    def send(cls, phone, text):
        return 200, "Send to phone succeeded"


class UrlBasedSMSBackEnd(SMSBackEnd):
    """
    The backend which send message to a url
    """
    @classmethod
    def send(cls, phone, text):
        url = settings.SMS_URL

        params = {
            'account': settings.SMS_ACCOUNT,
            'password': settings.SMS_PASSWORD,
            'mobile': phone,
            'content': text
        }

        request = requests.post(url, params)

        if request.status_code != 200:
            return request.status_code, 'Failed to send sms'

        import xml.etree.ElementTree as ET
        doc = ET.fromstring(request.content)

        namespace = doc.tag.lstrip('{').split('}')[0].join(['{', '}'])
        return_code = int(next(doc.iter(namespace + 'code')).text)

        if return_code != 2:
            return 400, "Failed to send sms"

        return 200, "Send to phone succeeded"


class ManDaoSMSBackEnd(SMSBackEnd):
    """
    The backend for ManDao sms service
    """
    @classmethod
    def send(cls, phone, text):
        return cls.send_messages([phone], [text])

    @classmethod
    def send_messages(cls, phones, messages):
        phone = ",".join(phones)
        text = ",".join(messages)

        url = settings.SMS_MANDAO_URL

        params = {
            'sn': settings.SMS_MANDAO_SN,
            'pwd': settings.SMS_MANDAO_MD5_PWD,
            'mobile': phone,
            'content': text
        }

        response = requests.post(url, params)

        logger.info("ManDao services called with response: %d %s" % (response.status_code, response.text))
        print "ManDao services called with response: %d %s" % (response.status_code, response.text)

        if response.status_code != 200:
            return response.status_code, 'Failed to send sms'

        response_text = response.text

        if response_text.startswith('-'):
            return int(response_text), 'Failed to call the service'

        return 200, "Succeeded sending sms"
