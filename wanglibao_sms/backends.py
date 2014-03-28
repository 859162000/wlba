from django.conf import settings
import requests


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
