#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
import json
import string
import hashlib
import logging
from django.db import transaction
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template import add_to_builtins
from django.template.loader import render_to_string
from registration.models import RegistrationProfile
from common.tasks import common_callback
from common.tools import detect_identifier_type, Aes
from common.utils import get_bajinshe_access_token, save_to_callback_record
from wanglibao import settings
from wanglibao_rest.utils import generate_bisouyi_sign, generate_bisouyi_content
from wanglibao_oauth2.utils import get_client_with_channel_code
from .models import Binding


logger = logging.getLogger(__name__)

ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits + '-_'
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


def has_binding_for_bid(channel_code, bid):
    return Binding.objects.filter(channel__code=channel_code, bid=bid).exists()


def get_coop_binding_for_phone(channel_code, phone):
    return Binding.objects.filter(channel__code=channel_code, user__wanglibaouserprofile__phone=phone).first()


def get_bajinshe_base_data(order_id):
    data = dict()
    coop_id = settings.BAJINSHE_COOP_ID
    access_token = get_bajinshe_access_token(order_id)
    if access_token:
        data = {
            'access_token': access_token,
            'platform': coop_id,
            'order_id': order_id
        }

    return data


def get_renrenli_base_data(channel_code):
    data = dict()
    coop_account_name = settings.RENRENLI_ACCOUNT_NAME
    coop_account_pwd = settings.RENRENLI_ACCOUNT_PWD
    client = get_client_with_channel_code(channel_code)
    if client:
        sign = hashlib.md5(coop_account_name + coop_account_pwd +
                           client.client_id + client.client_secret).hexdigest()
        data = {
            'Cust_id': client.client_id,
            'Sign_type': 'MD5',
            'Sign': sign,
        }

    return data


def parse_bisouyi_content(encrypt_str):
    try:
        ase = Aes()
        decrypt_text = ase.decrypt(settings.BISOUYI_AES_KEY, encrypt_str, mode_tag='ECB')
        content_data = json.loads(decrypt_text)
    except:
        logger.exception('parse_bisouyi_content with data[%s] raise error: ' % encrypt_str)
        content_data = {}

    return content_data


def bisouyi_callback(url, content_data, channel_code, callback_data=None, async_callback=True, order_id=None, ret_parser=''):
    content = generate_bisouyi_content(content_data)

    headers = {
        'Content-Type': 'application/json',
        'cid': settings.BISOUYI_CLIENT_ID,
        'sign': generate_bisouyi_sign(content),
    }

    data = json.dumps({'content': content})

    if callback_data:
        callback_data['order_id'] = order_id
        callback_data['request_url'] = url
        callback_data['request_data'] = data
        callback_data['request_headers'] = headers
        callback_data['request_action'] = 1
        callback_data['ret_parser'] = ret_parser

        save_to_callback_record(callback_data, channel_code)

    if async_callback:
        common_callback.apply_async(
            kwargs={'channel': channel_code, 'url': url,
                    'params': data, 'headers': headers,
                    'order_id': order_id, 'ret_parser': ret_parser})
    else:
        common_callback(channel=channel_code, url=url,
                        params=data, headers=headers,
                        order_id=order_id, ret_parser=ret_parser)
