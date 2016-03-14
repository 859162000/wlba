# coding=utf-8

import string
import uuid
import re
from django.db import transaction
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template import add_to_builtins
from django.template.loader import render_to_string
from registration.models import RegistrationProfile
from wanglibao import settings
import logging
from M2Crypto.EVP import Cipher
import requests
import json


logger = logging.getLogger(__name__)

ALPHABET = string.ascii_uppercase + string.ascii_lowercase + \
           string.digits + '-_'
ALPHABET_REVERSE = dict((c, i) for (i, c) in enumerate(ALPHABET))
BASE = len(ALPHABET)
SIGN_CHARACTER = '$'

# Try to load pyjade tags
add_to_builtins('pyjade.ext.django.templatetags')


def num_encode(n):
    if n < 0:
        return SIGN_CHARACTER + num_encode(-n)
    s = []
    while True:
        n, r = divmod(n, BASE)
        s.append(ALPHABET[r])
        if n == 0: break
    return ''.join(reversed(s))


def generate_username(identifier):
    """
    Generate a valid username from identifier, it can be an mail address
    or phone number
    """
    guid = uuid.uuid1()
    return num_encode(guid.int)


def detect_identifier_type(identifier):
    mobile_regex = re.compile('^1\d{10}$')
    if mobile_regex.match(identifier) is not None:
        return 'phone'

    email_regex = re.compile(
        '^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$')
    if email_regex.match(identifier) is not None:
        return 'email'

    return 'unknown'


@method_decorator(transaction.atomic)
def create_user(user_id, identifier, user_type='0'):
    username = generate_username(identifier)
    identifier_type = detect_identifier_type(identifier)
    if identifier_type == "unknown":
        return None

    user = User(pk=user_id, username=username)
    user.save()

    user.wanglibaouserprofile.utype = user_type
    user.wanglibaouserprofile.save()
    if identifier_type == 'email':
        user.email = identifier
        user.is_active = False
        registration_profile = RegistrationProfile.objects.create_profile(user)
        user.save()

        from_email, to = settings.DEFAULT_FROM_EMAIL, user.email
        context = {"activation_code": registration_profile.activation_key}

        subject = render_to_string('html/activation-title.html', context).strip('\n').encode('utf-8')
        text_content = render_to_string('html/activation-text.html', context).encode('utf-8')
        html_content = render_to_string('html/activation-html.html', context).encode('utf-8')

        email = EmailMultiAlternatives(subject, text_content, from_email, [to])
        email.attach_alternative(html_content, "text/html")
        email.send()

    elif identifier_type == 'phone':
        profile = user.wanglibaouserprofile
        profile.phone = identifier
        profile.phone_verified = True
        profile.save()

        user.is_active = True
        user.save()
    return user


class Crypto(object):
    def __init__(self, alg='aes_128_cbc'):
        self.alg = alg

    def encrypt_mode_cbc(self, data, key, iv):
        """
        使用aes_128_cbc算法对数据加密得到字节流
        :param data:
        :param key:
        :param iv:
        :return:
        """

        cipher = Cipher(alg=self.alg, key=key, iv=iv, op=1)
        buf = cipher.update(data)
        buf += cipher.final()
        del cipher

        return buf

    def encode_bytes(self, buf):
        """
        将字节流16进制加密
        :param buf:
        :return:
        """

        # 将字节流转为十进制
        des_list = [ord(i) for i in buf]

        # 原码转补码
        in_list = [~h ^ 255 if h > 128 else h for h in des_list]

        # 十六进制加密
        ret = []
        for byte in in_list:
            ret.append(chr(((byte >> 4) & 0xF) + 97))
            ret.append(chr((byte & 0xF) + 97))
        return ''.join(ret)

    def decode_bytes(self, enc_str):
        """
        将数据16进制解密为字节流
        :param enc_str:
        :return:
        """

        # 16进制解密
        in_list = []
        for i in range(0, len(enc_str), 2):
            in_list.append(((ord(enc_str[i]) - 97) << 4) + (ord(enc_str[i + 1]) - 97))

        # 十进制转字节流
        data_buf = ''.join([chr(i) for i in in_list])
        return data_buf

    def decrypt_mode_cbc(self, data_buf, key, iv):
        """
        使用aes_128_cbc算法对数据加密得到字节流
        :param data_buf:
        :param key:
        :param iv:
        :return:
        """

        cipher = Cipher(alg=self.alg, key=key, iv=iv, op=0)
        buf = cipher.update(data_buf)
        data = buf + cipher.final()
        del cipher
        return data


def get_bajinshe_access_token(coop_id, coop_key, order_id):
    access_token = None
    message = None

    coop_access_token_url = settings.BAJINSHE_ACCESS_TOKEN_URL

    data = {
        'platform': coop_id,
        'key': coop_key,
        'order_id': order_id,
    }

    headers = {
       'Content-Type': 'application/json',
    }

    res = requests.post(url=coop_access_token_url, data=json.dumps(data), headers=headers)
    logger.info("bajinshe access token url [%s]" % res.url)
    logger.info("bajinshe access token request data [%s]" % data)
    res_status_code = res.status_code
    if res_status_code == 200:
        res_data = res.json()
        if res_data['code'] == '10000':
            access_token = res_data.get('access_token', None)
            message = res_data.get('msg', '')
        else:
            logger.info("bajinshe access token faild return %s" % res_data)
    else:
        message = 'bad request %s' % res_status_code
        logger.info("bajinshe access token connect faild with status code[%s]" % res_status_code)
        logger.info(res.text)

    logger.info("get_bajinshe_access_token process result: %s" % message)
    return access_token


def get_bajinshe_base_data(order_id):
    data = dict()
    coop_id = settings.BAJINSHE_COOP_ID
    coop_key = settings.BAJINSHE_COOP_KEY
    access_token = get_bajinshe_access_token(coop_id, coop_key, order_id)
    if access_token:
        data = {
            'access_token': access_token,
            'platform': coop_id,
            'order_id': order_id
        }

    return data
