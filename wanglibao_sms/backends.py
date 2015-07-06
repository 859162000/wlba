#!/usr/bin/env python
# encoding:utf-8

from django.conf import settings
import time
import json
import hashlib
import requests
import httplib2
import base64
import logging
from suds.client import Client


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
            'content': text,
            'ext': '',
            'stime': '',
            'rrid': '',
            'msgfmt': ''
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

#SMS_EMAY_SN = "6SDK-EMY-6688-KEZSM"
#SMS_EMAY_KEY = "wanglibao"
#SMS_EMAY_PWD = "660687"
#SMS_EMAY_URL = "http://sdk4report.eucp.b2m.cn:8080/sdk/SDKService?wsdl"

class EmaySMS:
    @classmethod
    def register(cls):
        ws = Client(settings.SMS_EMAY_URL).service
        rs = ws.registEx(settings.SMS_EMAY_SN, settings.SMS_EMAY_KEY, settings.SMS_EMAY_PWD)
        print(rs)

    @classmethod
    def send_messages(cls, destmobile, smsContent, smsPriority=5, smsID=0):
        if not destmobile or not smsContent:
            return 500, {"status_code":500, "message":"params invalid"}

        if not isinstance(destmobile, list):
            destmobile = [destmobile]
        if len(smsContent) == 0 or len(destmobile) > 200:
            return 500, {"status_code":500, "message":"sms content cannot be empty or mobiles large than 200"}

        if isinstance(smsContent, list):
            smsContent = smsContent[0]
        try:
            ws = Client(settings.SMS_EMAY_URL).service
            rs = ws.sendSMS(settings.SMS_EMAY_SN, settings.SMS_EMAY_KEY, "", destmobile, smsContent, "", "GBK", smsPriority, smsID)
            message = rs
            if str(rs) == "0":
                status = 200
            else:
                status = 400
        except Exception,e:
            status = 500
            message = str(e)
        return status, {"status_code":status, "message":message}

    @classmethod
    def balance(cls):
        ws = Client(settings.SMS_EMAY_URL).service
        rs = ws.getBalance(settings.SMS_EMAY_SN, settings.SMS_EMAY_KEY)
        print(rs)

    @classmethod
    def get_report(cls):
        ws = Client(settings.SMS_EMAY_URL).service
        rs = ws.getReport(settings.SMS_EMAY_SN, settings.SMS_EMAY_KEY)
        print(rs)


class YTXVoice:
    @classmethod
    def verify(cls, phone, vcode):
        uri = "%s/Accounts/%s/Calls/VoiceVerify" % (settings.YTX_API_URL, settings.YTX_SID)
        ct = time.strftime("%Y%m%d%H%M%S", time.localtime())
        sig = hashlib.md5("%s%s%s" % (settings.YTX_SID, settings.YTX_TOKEN, ct)).hexdigest().upper()
        uri += "?sig=%s" % sig
        http = httplib2.Http()
        params = {"appId":settings.YTX_APPID, "verifyCode":vcode, "to":phone, 
                    "playTimes":"3", "respUrl":settings.YTX_BACK_RETURN_URL}
        data = json.dumps(params)
        headers = {"Accept":"application/json", "Content-Type":"application/json;charset=utf-8",
                    "Content-Length":str(len(data))}
        headers['Authorization'] = base64.encodestring("%s:%s" % (settings.YTX_SID, ct))
        response, content = http.request(uri, 'POST', headers=headers, body=data)
        if str(response['status']) == "200":
            # resp = {"statusCode":"000000","VoiceVerify":{"dateCreated":"2013-02-01 15:53:06","callSid":" ff8080813c373cab013c94be9fe300c5"}}
            resp = json.loads(content)
            if resp["statusCode"] == "000000":
                return 200, content
        return 500, content

if __name__ == "__main__":
    #EmaySMS.register()
    #EmaySMS.send_messages("18664387989", [u"abcdefg中国李振璟"])
    EmaySMS.balance()
    EmaySMS.get_report()
    #backends.YTXVoice.verify("18637172100", "123456")
