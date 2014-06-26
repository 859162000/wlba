# coding=utf-8
import string
import uuid
import re
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from registration.models import RegistrationProfile
import requests
from wanglibao_account.models import IdVerification
import logging

logger = logging.getLogger(__name__)

ALPHABET = string.ascii_uppercase + string.ascii_lowercase + \
           string.digits + '-_'
ALPHABET_REVERSE = dict((c, i) for (i, c) in enumerate(ALPHABET))
BASE = len(ALPHABET)
SIGN_CHARACTER = '$'


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

User = get_user_model()


def create_user(identifier, password, nickname):
    username = generate_username(identifier)
    identifier_type = detect_identifier_type(identifier)

    user = User(username=username)
    user.set_password(password)
    user.save()

    user.wanglibaouserprofile.nick_name = nickname
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


def verify_id(name, id_number):
    records = IdVerification.objects.filter(id_number=id_number)
    if records.exists():
        record = records.first()
        return record, None

    request = u"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:nci="http://www.nciic.com.cn" xmlns:fin="http://schemas.datacontract.org/2004/07/Finance.EPM">
           <soapenv:Header/>
           <soapenv:Body>
              <nci:SimpleCheck>
                 <!--Optional:-->
                 <nci:request>
                    <!--Optional:-->
                    <fin:IDNumber>%s</fin:IDNumber>
                    <!--Optional:-->
                    <fin:Name>%s</fin:Name>
                 </nci:request>
                 <!--Optional:-->
                 <nci:cred>
                    <!--Optional:-->
                    <fin:BindInfo></fin:BindInfo>
                    <!--Optional:-->
                    <fin:Password>%s</fin:Password>
                    <!--Optional:-->
                    <fin:UserName>%s</fin:UserName>
                 </nci:cred>
              </nci:SimpleCheck>
           </soapenv:Body>
        </soapenv:Envelope>"""

    encoded_request = (request % (id_number, name, settings.ID_VERIFY_PASSWORD, settings.ID_VERIFY_USERNAME)).encode("utf-8")

    headers = {
        "Host": "service.sfxxrz.com",
        "SOAPAction": "http://www.nciic.com.cn/IIdentifierService/SimpleCheck",
        "Content-Type": "text/xml; charset=UTF-8",
        "Content-Length": len(encoded_request),
    }

    response = requests.post(url='http://service.sfxxrz.com/IdentifierService.svc',
                             headers=headers,
                             data=encoded_request,
                             verify=False)

    if response.status_code != 200:
        logger.error("Failed to send request: status: %d, ", response.status_code)
        return None, "Failed to send request"

    parsed_response = parse_id_verify_response(response.text)
    result = bool(parsed_response['response_code'] == 100)

    if not result:
        logger.error("Failed to validate: %s" % response.text)

    record = IdVerification(id_number=id_number, name=name, is_valid=result)
    record.save()

    return record, None


def parse_id_verify_response(text):
    import xml.etree.ElementTree as ETree

    root = ETree.fromstring(text.encode('utf-8'))
    response_code = int(next(root.iter('{http://schemas.datacontract.org/2004/07/Finance.EPM}ResponseCode')).text)

    return {
        'response_code': response_code,
    }
