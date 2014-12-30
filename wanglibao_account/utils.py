# coding=utf-8
import string
import uuid
import re
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template, add_to_builtins
from django.template.loader import render_to_string, get_template
from django.utils import timezone
from registration.models import RegistrationProfile
from wanglibao_account.backends import TestIDVerifyBackEnd, ProductionIDVerifyBackEnd
import logging
import hashlib
import requests
from decimal import Decimal


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
    backend = settings.ID_VERIFY_BACKEND
    class_name = backend.split('.')[-1]

    if class_name == 'TestIDVerifyBackEnd':
        return TestIDVerifyBackEnd.verify(name, id_number)
    elif class_name == 'ProductionIDVerifyBackEnd':
        return ProductionIDVerifyBackEnd.verify(name, id_number)
    else:
        raise NameError("The specific backend not implemented")


def generate_contract(equity, template_name=None):
    """
    Generate the contract file for the equity.

    :param equity: Equity param, which links the product and user
    :return: The string representation of the contract
    """
    context = Context({
        'equity': equity,
        'now': timezone.now()
    })

    if template_name is not None:
        template = get_template(template_name)
    elif equity.product.contract_template is None:
        template = get_template('contract_template.jade')
    else:
        # Load the template from database
        template = Template(equity.product.contract_template.content)

    return template.render(context)


def generate_contract_preview(equity, product, template_name=None):
    """
    Generate the contract file for the equity.

    :param equity: Equity param, which links the product and user
    :return: The string representation of the contract
    """
    context = Context({
        'equity': equity,
        'product': product,
        'now': timezone.now()
    })

    if template_name is not None:
        template = get_template(template_name)
    elif product.contract_template is None:
        template = get_template('contract_template.jade')
    else:
        # Load the template from database
        template = Template(product.contract_template.content_preview)

    return template.render(context)


def mlgb_md5(phone, flag):
    new_str = '{}{}'.format(phone, flag)
    m = hashlib.md5()
    m.update(new_str)
    return m.hexdigest()


PAY_METHOD = {
    u'等额本息': 1,
    u'按月付息': 3,
    u'到期还本付息': 4,
    u'先息后本': 2
}


class CjdaoUtils():
    @classmethod
    def get_wluser_by_phone(cls, phone):
        """

        :param phone:
        :return:
        """
        if phone:
            return User.objects.filter(wanglibaouserprofile__phone=phone).first()

    @classmethod
    def quick_md5_value(cls, uaccount, phone, companyid, key):
        data_string = '{}{}{}{}'.format(uaccount, phone, companyid, key)
        return cls.md5str(data_string)

    @classmethod
    def md5_value(cls, *args):
        data_string = ''.join(args)
        m = hashlib.md5()
        m.update(data_string)
        return m.hexdigest()

    @classmethod
    def valid_md5(cls, str, *args):
        data_string = ''.join(args)
        m = hashlib.md5()
        m.update(data_string)
        return str == m.hexdigest()

    @classmethod
    def return_register(cls, cjdaoinfo, user, key):

        k = ('phone', 'usertype', 'uaccount', 'companyid', 'accountbalance')

        v = (user.wanglibaouserprofile.phone, str(cjdaoinfo.get('usertype')), str(cjdaoinfo.get('uaccount')),
             str(cjdaoinfo.get('companyid')), str(user.margin.margin), key)

        p = dict(zip(k, v))
        p.update(md5_value=cls.md5_value(*v))
        return p


    @classmethod
    def return_purchase(cls, cjdaoinfo, user, margin_record, p2p, key):

        reward = Decimal.from_float(0).quantize(Decimal('0.0'), 'ROUND_DOWN')
        if p2p.activity:
            reward = p2p.activity.rule.rule_amount.quantize(Decimal('0.0'), 'ROUND_DOWN')
        expectedrate = float(p2p.expected_earning_rate / 100) + float(reward)

        realincome = expectedrate * float(margin_record.amount) * p2p.period / 12

        k = ('uaccount', 'phone', 'usertype', 'companyid', 'thirdproductid',
             'productname', 'buytime', 'money', 'expectedrate', 'realincome', 'transactionstatus',
             'ordercode', 'accountbalance')


        p2pname = p2p.name
        productname = p2pname.encode('utf-8')

        v = (cjdaoinfo.get('uaccount'), str(user.wanglibaouserprofile.phone), str(cjdaoinfo.get('usertype')),
             cjdaoinfo.get('companyid'), str(p2p.id), productname,
             timezone.localtime(margin_record.create_time).strftime("%Y-%m-%d"),
             str(float(margin_record.amount)), str(expectedrate), str(realincome), '2', str(margin_record.order_id),
             str(float(margin_record.margin_current)), key)

        p = dict(zip(k, v))
        p.update(md5_value=cls.md5_value(*v))

        return p

    @classmethod
    def post_product(cls, p2p, key):

        k = (
            'thirdproductid', 'productname', 'companyname', 'startinvestmentmoney', 'acceptinvestmentmoney',
            'loandeadline',
            'expectedrate', 'risktype', 'incomeway', 'creditrating', 'iscurrent', 'isredeem', 'isassignment')

        incomeway = PAY_METHOD.get(p2p.pay_method, 0)
        reward = 0
        if p2p.activity:
            reward = p2p.activity.rule.rule_amount.quantize(Decimal('0.0000'), 'ROUND_DOWN')
        expectedrate = p2p.expected_earning_rate + float(reward * 100)

        v = (
            str(p2p.id), p2p.name, '网利宝', '100', str(p2p.available_amout), str(p2p.amortization_count),
            str(expectedrate), '1', str(incomeway), 'a', '1', '1', '1', key)

        p = dict(zip(k, v))
        p.update(md5_value=cls.md5_value(*v))
        return p



