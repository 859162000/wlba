#!/usr/bin/env python
# encoding:utf-8

from django.conf import settings
import requests
import logging
#from suds.client import Client


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
        return 200, "Send to phone succeeded", None


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

        if len(phones) > 1 and len(messages) == 1:
            url = settings.SMS_MANDAO_MULTICAST_URL
        params = {
            'sn': settings.SMS_MANDAO_SN,
            'pwd': settings.SMS_MANDAO_MD5_PWD,
            'mobile': phone,
            'content': text
        }

        response = requests.post(url, params)

        status_code = 200
        message = None

        if response.status_code != 200:
            status_code = response.status_code
            message = 'Failed to send sms'

        elif response.text.startswith('-'):
            status_code = int(response.text)
            message = 'Failed to call the service'

        return status_code, {
            "status_code": status_code,
            "message": message,
            "response_status": response.status_code,
            "response_text": response.text
        }

"""
softwareSerialNo = "6SDK-EMY-6688-KEZSM"
key = "wanglibao"
password = "660687"
url = "http://sdk4report.eucp.b2m.cn:8080/sdk/SDKService?wsdl"

class EmaySMS:
    @classmethod
    def register(cls):
        ws = Client(url).service
        rs = ws.registEx(softwareSerialNo, key, password)
        print(rs)

    @classmethod
    def send(cls, destmobile, smsContent, smsPriority=5, smsID=0):
        if not destmobile or not smsContent:
            return 400, "params invalid"

        if not isinstance(destmobile, list):
            destmobile = [destmobile]
        try:
            ws = Client(url).service
            rs = ws.sendSMS(softwareSerialNo, key, "", destmobile, smsContent, "", "GBK", smsPriority, smsID)
        except:
            return 400,"Internal server error"
        print(rs)

    @classmethod
    def balance(cls,):
        ws = Client(url).service
        rs = ws.getBalance(softwareSerialNo, key)
        print(rs)


if __name__ == "__main__":
    #EmaySMS.register()
    #EmaySMS.send("18637172100", "abcdefg")
    EmaySMS.balance()
"""
