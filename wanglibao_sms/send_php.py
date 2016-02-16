#!/usr/bin/env python
# encoding:utf-8

import json
import time
import random
import requests
import logging
from hashlib import md5
from datetime import datetime

logger = logging.getLogger('wanglibao_sms')

PHP_SMS_HOST = 'http://101.200.149.172/index.php?s=/node_push/send.html'
# PHP_SMS_HOST = 'http://haopeiwen.dev.wanglibao.com/wanglibao_push/index.php?s=/node_push/send.html'
PHP_AUTH_ID = 'admin'
PHP_AUTH_KEY = '192006250b4c09247ec02edce69f6a2d'


class SMSBackEnd(object):
    """
    The sms sending backend
    """

    @classmethod
    def send_sms(cls, *args, **kwargs):
        raise NotImplemented("The method not implemented yet")


class PHPSendSMS(SMSBackEnd):
    """
    PHP发短信服务
    """
    @classmethod
    def send_sms(cls, rule_id, data_messages):
        """
        :param rule_id: send node id
        :param data_messages: must be dict
        :return status_code, json data
            {"result":"success","msg":"success","code":0,"total":2,"end":2}
        """
        if not rule_id or not data_messages:
            return 400, {
                "result": "fail",
                "msg": "params error",
                "code": 400,
            }
        if not isinstance(data_messages, dict):
            return 400, {
                "result": "fail",
                "msg": "data_messages is not dictionary",
                "code": 400,
            }

        nonstr = generate_random_str(8)
        timestamp = int(time.time())
        post_data = {
            "auth_id": PHP_AUTH_ID,
            "rule_id": rule_id,
            "nonstr": nonstr,
            "timestamp": timestamp,
        }
        # 排序
        # post_data = [(k, post_data[k]) for k in sorted(post_data.keys())]

        # 拼接字符串
        post_data_str = "auth_id={0}&nonstr={1}&rule_id={2}&timestamp={3}&key={4}".format(
                PHP_AUTH_ID, nonstr, rule_id, timestamp, PHP_AUTH_KEY
        )
        # MD5
        sign = md5(post_data_str.encode('utf-8')).hexdigest()

        post_data['data'] = data_messages
        post_data['sign'] = sign
        post_data_json = json.dumps(post_data)

        headers = {'content-type': 'application/json'}
        response = requests.post(PHP_SMS_HOST, post_data_json, headers=headers)

        status_code = response.status_code
        try:
            res_text = json.loads(response.text)
        except:
            res_text = response.text

        # 写入日志
        logger.info(">>>> json data: {}".format(post_data_json))
        logger.info("<<<< {}; rule_id: {}; status_code: {}; response_text: {}".format(
            datetime.now(), rule_id, status_code, res_text
        ))
        return status_code, res_text

    @classmethod
    def send_sms_one(cls, rule_id, user_id, user_type, **kwargs):
        if not rule_id or not user_id or not user_type:
            logger.info(">>>> 参数不全,发送失败 ")
            return

        if not user_type:
            user_type = 'phone'

        data_messages = {
            0: {
                'user_id': user_id,
                'user_type': user_type,
                'params': {
                    key: str(kwargs[key]) for key in kwargs.keys()
                }
            }
        }
        # 功能推送id: rule_id
        cls.send_sms(rule_id=rule_id, data_messages=data_messages)

    @classmethod
    def send_sms_msg_one(cls, rule_id, user_id, user_type, msg):
        if not rule_id or not user_id or not user_type or not msg:
            logger.info(">>>> 参数不全,发送失败 ")
            return

        if not user_type:
            user_type = 'phone'

        data_messages = {
            0: {
                'user_id': user_id,
                'user_type': user_type,
                'msg': msg
            }
        }
        # 功能推送id: rule_id
        cls.send_sms(rule_id=rule_id, data_messages=data_messages)


def generate_random_str(count):
    """
    :param count: int
    :return: random string
    """
    letters = 'abcdefghijkm34npqrGHIJKMNstuvwxyzABCDEF567PQRSTUVWXY1289'

    return ''.join(random.sample(letters, count))


def test():
    data = {
        0: {
            'user_id': '18612803787',
            'user_type': 'phone',
            'params': {
                'a': 'hello',
            }
        },
        1: {
            'user_id': '15038038823',
            'user_type': 'phone',
            'params': {
                'a': 'hello',
            }
        },
    }

    PHPSendSMS.send_sms(5, data)


if __name__ == "__main__":
    test()

