#!/usr/bin/env python
# encoding:utf-8

import hashlib
import urllib
import httplib2
import time
import json
import itertools

class BaeChannel:
    def __init__(self):
        self.host = "http://channel.api.duapp.com/rest/2.0/channel/"
        self.ak = "08l55kZYVhykO4H6nOO4oUZL"
        self.sk = "lZzlmTHdfgj12o97oSRCFGGRIy8ASL5F"
        self.http = httplib2.Http()
        self.userAgent = "wanglibao push service by zhenjing"

    def pushAndroidMessage(self, userId, channelId, messages, msgKeys):
        return self._pushMsg(userId, channelId, messages, msgKeys, deviceType=3)

    def pushIosMessage(self, userId, channelId, messages, msgKeys):
        if "type" not in messages:
            messages['type'] = "normal"
        if "user_id" not in messages:
            messages['user_id'] = 0
        messages = json.dumps({"type":messages['type'],"user_id":messages['user_id'], 
                            "aps": {"alert":messages['message'], "sound":"default", "badge":1}})
        return self._pushMsg(userId, channelId, messages, msgKeys, deviceType=4, message_type=1, ds=2)

    def _pushMsg(self, userId, channelId, messages, msgKeys, deviceType=3, message_type=0, ds=2):
        msg = safestr(messages)
        params = {"method":"push_msg", "push_type":"1", "apikey":self.ak,
                    "user_id":userId, "channel_id":channelId, "messages":msg, "deploy_status":ds,
                    "device_type":str(deviceType), "message_type":str(message_type),
                    "msg_keys":msgKeys, "timestamp":int(time.time())}
        url = self.host + "channel"
        params['sign'] = self.sign("POST", url, params)
        data = urllib.urlencode(params)
        headers = {"User-Agent":self.userAgent,
                    "Content-Length":str(len(data)),
                    "Content-Type":"application/x-www-form-urlencoded"}
        response, content = self.http.request(url, 'POST', headers=headers, body=data)
        if str(response['status']) == "200":
            response['status'] = 0
        return response['status'], content

    def sign(self, method, url, arrContent):
        seq = method + url
        keys = arrContent.keys()
        keys.sort()
        for key in keys:
            seq += key + '=' + str(arrContent[key])
        seq += self.sk
        sign = hashlib.md5(urllib.quote_plus(seq))  
        return sign.hexdigest().upper()

def safestr(obj, encoding="utf-8"):
    if isinstance(obj, unicode):
        return obj.encode(encoding)
    elif isinstance(obj, str):
        return obj
    elif hasattr(obj, 'next'): # iterator
        return itertools.imap(safestr, obj)
    else:
        return str(obj)
