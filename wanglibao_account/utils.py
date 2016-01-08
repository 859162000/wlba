# coding=utf-8
import string
import uuid
import re
import datetime
import time
from django.conf import settings
#from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template, add_to_builtins
from django.template.loader import render_to_string, get_template
from django.utils import timezone
from registration.models import RegistrationProfile
from wanglibao_account.backends import TestIDVerifyBackEnd, ProductionIDVerifyBackEnd, ProductionIDVerifyV2BackEnd
from marketing.utils import get_user_channel_record
from wanglibao_pay.models import PayInfo
from wanglibao_p2p.models import P2PRecord
from wanglibao import settings
from wanglibao.settings import ENV, ENV_PRODUCTION
import logging
import hashlib
import pytz
from M2Crypto.EVP import Cipher
import urllib
from .models import UserThreeOrder
import requests
import json

from decimal import Decimal
from wanglibao_p2p.amortization_plan import get_amortization_plan


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


#User = get_user_model()


@method_decorator(transaction.atomic)
def create_user(identifier, password, nickname):
    username = generate_username(identifier)
    identifier_type = detect_identifier_type(identifier)
    if identifier_type =="unknown":
        return None

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
    elif class_name == 'ProductionIDVerifyV2BackEnd':
        return ProductionIDVerifyV2BackEnd.verify(name, id_number)
    else:
        raise NameError("The specific backend not implemented")


def generate_contract(equity, template_name=None, equities=None):
    """
    Generate the contract file for the equity.
    :param equity: Equity param, which links the product and user
    :return: The string representation of the contract
    """
    context = Context({
        'equity': equity,
        'equities': equities,
        'now': timezone.now()
    })

    if template_name is not None:
        template = get_template(template_name)
    elif equity.product.contract_template is None:
        template = get_template('contract_template.jade')
    else:
        # Load the template from database
        template = Template(equity.product.contract_template.content)
        # print equity.product.contract_template.content[:100]

    return template.render(context)


def generate_contract_preview(productAmortizations, product, template_name=None):
    """
    Generate the contract file for the equity.
    :param equity: Equity param, which links the product and user
    :return: The string representation of the contract
    """
    context = Context({
        'productAmortizations': productAmortizations,
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
    u'按月付息': 2,
    u'到期还本付息': 4
}


# class CjdaoUtils():
#
#     @classmethod
#     def get_wluser_by_phone(cls, phone):
#         """
#
#         :param phone:
#         :return:
#         """
#         if phone:
#             return User.objects.filter(wanglibaouserprofile__phone=phone).first()
#
#     @classmethod
#     def quick_md5_value(cls, uaccount, phone, companyid, key):
#         data_string = '{}{}{}{}'.format(uaccount, phone, companyid, key)
#         return cls.md5str(data_string)
#
#     @classmethod
#     def md5_value(cls, *args):
#         data_string = ''.join(args)
#         m = hashlib.md5()
#         m.update(data_string)
#         return m.hexdigest()
#
#     @classmethod
#     def valid_md5(cls, str, *args):
#         data_string = ''.join(args)
#         m = hashlib.md5()
#         m.update(data_string)
#         return str == m.hexdigest()
#
#     @classmethod
#     def return_register(cls, cjdaoinfo, user, key):
#
#         k = ('phone', 'usertype', 'uaccount', 'companyid', 'accountbalance')
#
#         v = (user.wanglibaouserprofile.phone, str(cjdaoinfo.get('usertype')), str(cjdaoinfo.get('uaccount')),
#              str(cjdaoinfo.get('companyid')), str(float(user.margin.margin)), key)
#
#         p = dict(zip(k, v))
#         p.update(md5_value=cls.md5_value(*v))
#         return p
#
#
#     @classmethod
#     def return_purchase(cls, cjdaoinfo, user, margin_record, p2p, key):
#
#         reward = Decimal.from_float(0).quantize(Decimal('0.0000'), 'ROUND_DOWN')
#         if p2p.activity:
#             reward = p2p.activity.rule.rule_amount.quantize(Decimal('0.0000'), 'ROUND_DOWN')
#         expectedrate = Decimal.from_float(p2p.expected_earning_rate) / 100 + reward
#         expectedrate = float(expectedrate.quantize(Decimal('0.000'), 'ROUND_DOWN'))
#
#         terms = get_amortization_plan(p2p.pay_method).generate(p2p.total_amount,
#                                                                p2p.expected_earning_rate / 100,
#                                                                p2p.amortization_count,
#                                                                p2p.period)
#         total_earning = terms.get("total") - p2p.total_amount
#
#         realincome = (margin_record.amount / p2p.total_amount ) * total_earning
#         realincome = realincome.quantize(Decimal('0.00'), 'ROUND_DOWN')
#
#         print realincome
#
#         k = ('uaccount', 'phone', 'usertype', 'companyid', 'thirdproductid',
#              'productname', 'buytime', 'money', 'expectedrate', 'realincome', 'transactionstatus',
#              'ordercode', 'accountbalance')
#
#
#         p2pname = p2p.name
#         productname = p2pname.encode('utf-8')
#
#         v = (cjdaoinfo.get('uaccount'), str(user.wanglibaouserprofile.phone), str(cjdaoinfo.get('usertype')),
#              cjdaoinfo.get('companyid'), str(p2p.id), productname,
#              timezone.localtime(margin_record.create_time).strftime("%Y-%m-%d"),
#              str(float(margin_record.amount)), str(expectedrate), str(realincome), '2', str(margin_record.order_id),
#              str(float(margin_record.margin_current)), key)
#
#         p = dict(zip(k, v))
#         p.update(md5_value=cls.md5_value(*v))
#
#         return p
#
#     @classmethod
#     def post_product(cls, p2p, key):
#
#         k = [
#             'thirdproductid', 'productname', 'companyname', 'startinvestmentmoney', 'acceptinvestmentmoney',
#             'loandeadline',
#             'expectedrate', 'risktype', 'incomeway', 'creditrating', 'iscurrent', 'isredeem', 'isassignment']
#
#
#         reward = 0
#         if p2p.activity:
#             reward = p2p.activity.rule.rule_amount.quantize(Decimal('0.0000'), 'ROUND_DOWN')
#         expectedrate = float(p2p.expected_earning_rate / 100) + float(reward)
#
#         p2pname = p2p.name
#         productname = p2pname.encode('utf-8')
#
#         incomeway = PAY_METHOD.get(p2p.pay_method, 0)
#         if incomeway:
#             v = (
#                 str(p2p.id), productname, '网利宝', '100', str(p2p.available_amout), str(p2p.period),
#                 str(expectedrate), '1', str(incomeway), 'a', '1', '1', '1', key)
#         else:
#             k.remove('incomeway')
#             v = (
#                 str(p2p.id), productname, '网利宝', '100', str(p2p.available_amout), str(p2p.period),
#                 str(expectedrate), '1', 'a', '1', '1', '1', key)
#
#         p = dict(zip(k, v))
#         p.update(md5_value=cls.md5_value(*v))
#         return p
#
#

def str_add_md5(value):
    if value and isinstance(value, str):
        m = hashlib.md5()
        m.update(value)
        return m.hexdigest()
    else:
        return ''


def str_to_utc(time_str):
    """
    :param str:  '2015-08-08'
    :return:     datetime.datetime(2015, 8, 8, 7, 0, tzinfo=<UTC>)
    """
    time_zone = settings.TIME_ZONE
    local = pytz.timezone(time_zone)
    naive = datetime.datetime.strptime(time_str, "%Y-%m-%d")
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)

    return utc_dt


def str_to_float(time_str):
    """
    :param time_str:
    :return:
    """
    return time.mktime(time.strptime(time_str, "%Y-%m-%d"))


def encrypt_mode_cbc(data, key, iv):
    """
    aes加密得到十进制串
    :param data:
    :param key:
    :param iv:
    :return:
    """

    cipher = Cipher(alg='aes_128_cbc', key=key, iv=iv, op=1)
    buf = cipher.update(data)
    buf += cipher.final()
    del cipher

    # 将明文从字节流转为十进制
    des_list = [int('%02X' % (ord(i)), 16) for i in buf]

    # 原码转补码
    in_list = [~h ^ 255 if h > 128 else h for h in des_list]

    return in_list


def encodeBytes(in_list):
    """
    十进制按电信规则16进制加密
    :param bytelist:
    :return:
    """

    ret = []
    for byte in in_list:
        ret.append(chr(((byte >> 4) & 0xF) + 97))
        ret.append(chr((byte & 0xF) + 97))
    return ''.join(ret)


def get_client_ip(request):
    """
    获取客户端ip
    :param request:
    :return:
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class FileObject(object):
    """构造文件对象（file, size云存储所需）"""

    def __init__(self, content, size):
        self.file = content
        self.size = size


def base64_to_image(base64_str):
    """base64编码转图片流"""

    import base64
    import cStringIO

    img_str = base64.b64decode(base64_str)
    img_handle = cStringIO.StringIO()
    img_handle.write(img_str)
    img_handle.seek(0)
    img_file = FileObject(img_handle, len(img_str))

    return img_file


def xunleivip_generate_sign(data, key):
    sorted_data = sorted(data.iteritems(), key=lambda asd:asd[0], reverse=False)
    encode_data = urllib.urlencode(sorted_data)
    sign = hashlib.md5(encode_data+str(key)).hexdigest()
    return sign


def zgdx_order_query(params):
    """
    中国电信业务查询
    """

    coop_key = getattr(settings, 'ZGDX_KEY', None)
    iv = getattr(settings, 'ZGDX_IV', None)
    url = getattr(settings, 'ZGDX_QUERY_URL', None)
    if coop_key and iv and url:
        data = {
            'phone_id': params.get('phone_id', ''),
            'service_code': params.get('service_code', ''),
            'request_no': params.get('request_no', ''),
            'start_time': params.get('start_time', ''),
            'end_time': params.get('end_time', ''),
        }

        encrypt_data = encrypt_mode_cbc(json.dumps(data), coop_key, iv)
        params = {
            'code': encodeBytes(encrypt_data),
            'partner_no': params.get('partner_no', None),
        }

        try:
            res = requests.post(url, data=json.dumps(params))
            if res.status_code == 200:
                logger.info("zgdx return:%s" % res.text)
                res = res.json()
                res_code = res.get('result_code', '')
                result = res.get('result', '')
                if res_code == '00000':
                    json_response = {
                        'ret_code': 0,
                        'message': 'success',
                        'data': result
                    }
                else:
                    json_response = {
                        'ret_code': res_code,
                        'message': result
                    }
            else:
                json_response = {
                    'ret_code': 50001,
                    'message': 'api error'
                }
                logger.info('zgdx connect to query api faild with status %s' % res.status_code)
        except Exception, e:
            json_response = {
                'ret_code': 50001,
                'message': 'api error'
            }
            logger.info('zgdx connect to query api faild')
            logger.info(e)
    else:
        json_response = {
            'ret_code': 50001,
            'message': 'api error'
        }
        logger.info("zgdx_order_query coop_key, iv or url None")

    return json_response


def xunlei9_order_query(params):
    """
    迅雷VIP业务查询
    """

    url = getattr(settings, 'XUNLEIVIP_QUERY_URL', None)
    coop_key = getattr(settings, 'XUNLEIVIP_KEY', None)
    if coop_key and url:
        data = {
            'uid': params.get('uid', ''),
            'act': params.get('act', ''),
            'orderid': params.get('orderid', ''),
        }

        data['sign'] = xunleivip_generate_sign(data, coop_key)

        try:
            res = requests.get(url, params=data).json()
            json_response = {
                'ret_code': 0,
                'message': 'success',
                'data': res
            }
        except Exception, e:
            json_response = {
                'ret_code': 50001,
                'message': 'api error'
            }
    else:
        json_response = {
            'ret_code': 50001,
            'message': 'api error'
        }

    return json_response


def update_coop_order(request_no, channel_code, result_code, msg):
    order = UserThreeOrder.objects.filter(request_no=request_no, order_on__code=channel_code).first()

    if order:
        logger.info("Enter %s order update===>>>" % channel_code)
        logger.info("%s update params:{request_no=%s, result_code=%s, "
                    "msg=%s}===>>>" % (channel_code, request_no, result_code, msg))
        try:
            order.result_code = result_code
            order.msg = msg
            order.answer_at = datetime.datetime.now()
            order.save()
            response = {
                'ret_code': 1,
                'message': 'success'
            }
        except Exception, e:
            logger.info('%s request_no %s save to UserThreeOrder faild.' % (channel_code, request_no))
            logger.info(e)
            response = {
                'ret_code': 50000,
                'message': 'api error.'
            }
    else:
        response = {
            'ret_code': 20002,
            'message': u'订单流水号不存在'
        }

    return response


def str_to_dict(s):
    """
    将字符串转换成字典
    ret=0&error=test' ==> {u'ret': u'0', u'error': u'test'}
    :param s:
    :return: result
    """

    result = {}
    for item in s.split('&'):
        key, value = item.split('=')
        result[urllib.unquote_plus(key)] = urllib.unquote_plus(value)

    return result


class Xunlei9AdminCallback(object):
    """迅雷9管理后台回调"""

    def xunlei_call_back(self, user, tid, data, url, order_id):
        order_id = '%s_%s' % (order_id, data['act'])
        data['uid'] = tid
        data['orderid'] = order_id
        data['type'] = 'baijin'
        sign = xunleivip_generate_sign(data, settings.XUNLEIVIP_KEY)
        params = dict({'sign': sign}, **data)

        # 创建渠道订单记录
        channel_recode = get_user_channel_record(user.id)
        order = UserThreeOrder.objects.get_or_create(user=user, order_on=channel_recode, request_no=order_id)[0]
        order.save()

        # 异步回调
        from .tasks import xunleivip_callback
        xunleivip_callback.apply_async(
            kwargs={'url': url, 'params': params,
                    'channel': channel_recode.code, 'order_id': order_id})

    def recharge_call_back(self, obj, order_prefix=''):
        penny = Decimal(0.01).quantize(Decimal('.01'))
        pay_info = PayInfo.objects.filter(user=obj.user, type='D', amount__gt=penny,
                                          status=PayInfo.SUCCESS).order_by('create_time').first()

        # 判断用户是否绑定和首次充值
        if pay_info and int(pay_info.amount) >= 100:
            data = {
                'sendtype': '1',
                'num1': 7,
                'act': 5171
            }

            order_prefix = order_prefix or pay_info.order_id
            self.xunlei_call_back(obj.user, obj.bid, data,
                                  settings.XUNLEIVIP_CALL_BACK_URL,
                                  order_prefix)

    def purchase_call_back(self, obj, order_prefix=''):
        p2p_record = P2PRecord.objects.filter(user=obj.user, catalog=u'申购').order_by('create_time').first()

        # 判断是否首次投资
        if p2p_record and int(p2p_record.amount) >= 1000:
            data = {
                'sendtype': '0',
                'num1': 12,
                'act': 5170
            }

            order_prefix = order_prefix or p2p_record.order_id
            self.xunlei_call_back(obj.user, obj.bid, data,
                                  settings.XUNLEIVIP_CALL_BACK_URL,
                                  order_prefix)

    def process_callback(self, obj, order_list):
        if order_list.exists():
            if order_list.count() == 1:
                order_prefix, order_suffix = order_list.first().request_no.split('_')
                if order_list.first().result_code:
                    if int(order_suffix) == 5170:
                        self.recharge_call_back(obj)
                    elif int(order_suffix) == 5171:
                        self.purchase_call_back(obj)
                else:
                    if int(order_suffix) == 5170:
                        self.recharge_call_back(obj)
                        self.purchase_call_back(obj, order_prefix)
                    elif int(order_suffix) == 5171:
                        self.recharge_call_back(obj, order_prefix)
                        self.purchase_call_back(obj)
            else:
                for order in order_list:
                    if order.result_code == '':
                        order_prefix, order_suffix = order.request_no.split('_')
                        if int(order_suffix) == 5170:
                            self.purchase_call_back(obj, order_prefix)
                        elif int(order_suffix) == 5171:
                            self.recharge_call_back(obj, order_prefix)
        else:
            self.recharge_call_back(obj)
            self.purchase_call_back(obj)


class ZGDXAdminCallback(object):
    """迅雷9管理后台回调"""

    def __init__(self):
        self.c_code = 'zgdx'
        self.call_back_url = settings.ZGDX_CALL_BACK_URL
        self.partner_no = settings.ZGDX_PARTNER_NO
        self.service_code = settings.ZGDX_SERVICE_CODE
        self.contract_id = settings.ZGDX_CONTRACT_ID
        self.activity_id = settings.ZGDX_ACTIVITY_ID
        self.coop_key = settings.ZGDX_KEY
        self.iv = settings.ZGDX_IV

    def zgdx_call_back(self, user, plat_offer_id, order_id=None):
        logger.info("ZGDX-Enter zgdx_call_back for zgdx: user[%s], order_id[%s], plat_offer_id[%s]" % (user.id,
                                                                                                       order_id,
                                                                                                       plat_offer_id))
        if datetime.datetime.now().day >= 28:
            effect_type = '1'
        else:
            effect_type = '0'

        request_no_prefix = order_id or str(user.id) + timezone.now().strftime("%Y%m%d%H%M%S")
        request_no = request_no_prefix + '_' + plat_offer_id
        phone = user.wanglibaouserprofile.phone
        code = {
            'request_no': request_no,
            'phone_id': phone,
            'service_code': self.service_code,
            'contract_id': self.contract_id,
            'activity_id': self.activity_id,
            'order_type': '1',
            'plat_offer_id': plat_offer_id,
            'effect_type': effect_type,
        }
        encrypt_str = encrypt_mode_cbc(json.dumps(code), self.coop_key, self.iv)
        params = {
            'code': encodeBytes(encrypt_str),
            'partner_no': self.partner_no,
        }

        # 创建渠道订单记录
        channel_recode = get_user_channel_record(user.id)
        order = UserThreeOrder.objects.get_or_create(user=user, order_on=channel_recode, request_no=request_no)[0]
        order.save()

        # 异步回调
        from .tasks import zgdx_callback
        zgdx_callback.apply_async(
            kwargs={'url': self.call_back_url, 'params': params, 'channel': self.c_code})

    def binding_card_call_back(self, obj, order_prefix=''):
        logger.info("ZGDX-Enter recharge_call_back for zgdx: user[%s], order_prefix[%s]" % (obj.user.id, order_prefix))
        self.zgdx_call_back(obj.user, '104369', order_prefix)
        if obj.extra != '1':
            obj.extra = '1'
            obj.save()

    def purchase_call_back(self, obj, order_prefix=''):
        logger.info("ZGDX-Enter purchase_call_back for zgdx: user[%s], order_prefix[%s]" % obj.user.id, order_prefix)

        p2p_record = P2PRecord.objects.filter(user_id=obj.user.id, catalog=u'申购').order_by('create_time').first()
        if p2p_record:
            order_prefix = order_prefix or p2p_record.order_id
            p2p_amount = int(p2p_record.amount)
            if p2p_amount >= 1000:
                if 1000 <= p2p_amount < 2000:
                    plat_offer_id = '104371'
                else:
                    plat_offer_id = '104372'
                self.zgdx_call_back(obj.user, plat_offer_id, order_prefix)

    def process_callback(self, obj, order_list):
        if ENV != ENV_PRODUCTION:
            pass
            # return
        if order_list.exists():
            if order_list.count() == 1:
                order_prefix, order_suffix = order_list.first().request_no.split('_')
                if order_list.first().result_code:
                    if order_suffix == '104369':
                        self.purchase_call_back(obj)
                    elif order_suffix in ['104371', '104372']:
                        self.binding_card_call_back(obj)
                else:
                    if order_suffix == '104369':
                        self.purchase_call_back(obj)
                        self.binding_card_call_back(obj, order_prefix)
                    elif order_suffix in ['104371', '104372']:
                        self.binding_card_call_back(obj)
                        self.purchase_call_back(obj, order_prefix)
            else:
                for order in order_list:
                    if order.result_code == '':
                        order_prefix, order_suffix = order.request_no.split('_')
                        if order_suffix == '104369':
                            self.binding_card_call_back(obj, order_prefix)
                        elif order_suffix in ['104371', '104372']:
                            self.purchase_call_back(obj, order_prefix)
        else:
            self.binding_card_call_back(obj)
            self.purchase_call_back(obj)