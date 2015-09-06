#!/usr/bin/env python
# encoding:utf-8
import decimal
import json
import urllib2
from django.utils.http import urlencode
from wanglibao_account.utils import str_to_float

if __name__ == '__main__':
    import os
    import sys

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wanglibao.settings')

import hashlib
import datetime
import time
import logging
from django.contrib.auth.models import User
from django.db.models import Sum, Q, Count
from django.http import HttpResponse
from django.utils import timezone
import requests
from rest_framework import renderers
from rest_framework.views import APIView
from marketing.models import Channels, IntroducedBy, PromotionToken
from marketing.utils import set_promo_user
from wanglibao import settings
from wanglibao.settings import YIRUITE_CALL_BACK_URL, \
     TIANMANG_CALL_BACK_URL, WLB_FOR_YIRUITE_KEY, YIRUITE_KEY, BENGBENG_KEY, \
     WLB_FOR_BENGBENG_KEY, BENGBENG_CALL_BACK_URL, BENGBENG_COOP_ID, JUXIANGYOU_COOP_ID, JUXIANGYOU_KEY, \
     JUXIANGYOU_CALL_BACK_URL, TINMANG_KEY, DOUWANWANG_CALL_BACK_URL, JINSHAN_CALL_BACK_URL, WLB_FOR_JINSHAN_KEY, \
     WLB_FOR_SHLS_KEY, SHITOUCUN_CALL_BACK_URL, WLB_FOR_SHITOUCUN_KEY, FUBA_CALL_BACK_URL, WLB_FOR_FUBA_KEY, \
     FUBA_COOP_ID, FUBA_KEY, FUBA_CHANNEL_CODE, FUBA_DEFAULT_TID, FUBA_PERIOD, \
     WLB_FOR_YUNDUAN_KEY, YUNDUAN_CALL_BACK_URL, YUNDUAN_COOP_ID, WLB_FOR_YICHE_KEY, YICHE_COOP_ID, \
     YICHE_KEY, YICHE_CALL_BACK_URL, WLB_FOR_ZHITUI1_KEY, ZHITUI_COOP_ID, ZHITUI_CALL_BACK_URL, \
     WLB_FOR_ZGDX_KEY, ZGDX_CALL_BACK_URL, ZGDX_PARTNER_NO, ZGDX_SERVICE_CODE, ZGDX_CONTRACT_ID, \
     ZGDX_ACTIVITY_ID, ZGDX_PLAT_OFFER_ID, ZGDX_KEY, ZGDX_IV
from wanglibao_account.models import Binding, IdVerification
from wanglibao_account.tasks import common_callback, jinshan_callback, yiche_callback
from wanglibao_p2p.models import P2PEquity, P2PRecord, P2PProduct, ProductAmortization
from wanglibao_pay.models import Card
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_redis.backend import redis_backend
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import re
from M2Crypto.EVP import Cipher

logger = logging.getLogger(__name__)


def get_uid_for_coop(user_id):
    """
    返回给渠道的用户ID
    :param user_id:
    :return:
    """
    m = hashlib.md5()
    m.update('wlb' + str(user_id))
    uid = m.hexdigest()
    return uid


def get_username_for_coop(user_id):
    """
    返回给渠道的用户名
    :param user_id:
    :return:
    """
    try:
        user_name = WanglibaoUserProfile.objects.get(user_id=int(user_id)).name
        return u'*' + user_name[1:]
    except:
        return None


def get_phone_for_coop(user_id):
    try:
        phone_number = WanglibaoUserProfile.objects.get(user_id=user_id).phone
        return phone_number[:3] + '***' + phone_number[-2:]
    except:
        return None


def get_first_investment_for_coop(user_id):
    try:
        p2p_record = P2PRecord.objects.filter(user_id=user_id, catalog=u'申购').order_by('create_time')
        amount = p2p_record[0].amount
        first_invest_time = p2p_record[0].create_time
        total_amount = P2PEquity.objects.filter(user_id=user_id).aggregate(Sum('equity'))['equity__sum'] or 0
        return amount, total_amount, first_invest_time,
    except:
        return None, None, None

def get_last_investment_for_coop(user_id):
    try:
        p2p_record = P2PRecord.objects.filter(user_id=user_id, catalog=u'申购').order_by('create_time')
        return p2p_record.last()
    except:
        return None


def get_tid_for_coop(user_id):
    try:
        return Binding.objects.filter(user_id=user_id).get().bid
    except:
        return None


def get_validate_time_for_coop(user_id):
    try:
        id_number = WanglibaoUserProfile.objects.filter(user_id=user_id).get().id_number
        validate_time = IdVerification.objects.filter(id_number=id_number).get().created_at
        return validate_time
    except Exception, e:
        return None


def get_binding_time_for_coop(user_id):
    try:
        binding_time = Card.objects.filter(user_id=user_id).order_by('add_at').first().add_at
        return binding_time
    except Exception, e:
        return None


def save_to_binding(user, record, request):
    try:
        if record and record.name == 'shls' or record.name == 'zhitui1':
            coop = CoopRegister(request)
            for processor in coop.processors:
                if processor.c_code == processor.channel_code:
                    processor.save_to_binding(user)
    except:
        pass


def generate_Encrypt(key, iv, mode, data):
    mode = mode.lower()
    cipher = Cipher(alg=mode, key=key, iv=iv, op=1)
    buf = cipher.update(data)
    buf = buf + cipher.final()
    del cipher
    # 将明文从字节流转为16进制
    output = ''
    for i in buf:
        output += '%02X' % (ord(i))
    return output

#判断网站来自mobile还是pc
def check_mobile(request):
    """
    demo :
        def is_from_mobile():
            if check_mobile(request):
                return 'mobile'
            else:
                return 'pc'
    :param request:
    :return:
    """
    user_agent = request.META.get('HTTP_USER_AGENT', None)
    _long_matches = r'googlebot-mobile|android|avantgo|blackberry|blazer|elaine' \
                    r'|hiptop|ip(hone|od)|kindle|midp|mmp|mobile|o2|opera mini|' \
                    r'palm( os)?|pda|plucker|pocket|psp|smartphone|symbian|treo|' \
                    r'up\.(browser|link)|vodafone|wap|windows ce; (iemobile|ppc)|' \
                    r'xiino|maemo|fennec'
    _long_matches = re.compile(_long_matches, re.IGNORECASE)
    _short_matches = r'1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|' \
                     r'ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|' \
                     r'aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|' \
                     r'be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|' \
                     r'c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|' \
                     r'da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|' \
                     r'el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|' \
                     r'fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|' \
                     r'haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-|' \
                     r' |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|' \
                     r'ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|' \
                     r'kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|' \
                     r'\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|' \
                     r'ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|' \
                     r'mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|' \
                     r'n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|' \
                     r'on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|' \
                     r'pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|' \
                     r'po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|' \
                     r'i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|' \
                     r'ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|' \
                     r'shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|' \
                     r'sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|' \
                     r'tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|' \
                     r'tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|' \
                     r'\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|' \
                     r'webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-'
    _short_matches = re.compile(_short_matches, re.IGNORECASE)

    if _long_matches.search(user_agent) != None:
        return True
    user_agent = user_agent[0:4]
    if _short_matches.search(user_agent) != None:
        return True
    return False


#######################第三方用户注册#####################

class CoopRegister(object):
    """
    第三方用户注册api
    """
    def __init__(self, request):
        # 本渠道的名称
        self.c_code = None
        self.request = request
        # 传递渠道邀请码时使用的变量名
        self.external_channel_key = settings.PROMO_TOKEN_QUERY_STRING
        self.internal_channel_key = 'channel_code'
        # 传递渠道用户时使用的变量名
        self.external_channel_user_key = settings.PROMO_TOKEN_USER_KEY
        self.internal_channel_user_key = 'channel_user'
        # 渠道提供给我们的秘钥
        self.coop_key = None
        self.call_back_url = None

    @property
    def channel_code(self):
        """
        从GET请求中获取的渠道邀请码
        """
        return self.request.session.get(self.internal_channel_key, None)

    def get_channel_code_from_request(self):
        return self.request.GET.get(self.external_channel_key, None)

    @property
    def channel_name(self):
        """
        渠道名
        """
        try:
            channel_name = Channels.objects.filter(code=self.channel_code).get().name
        except:
            channel_name = None
        return channel_name

    @property
    def channel_user(self):
        return self.request.session.get(self.internal_channel_user_key, None)

    @property
    def channel_extra(self):
        """
        渠道扩展参数
        """
        return self.request.session.get(self.extra_key, 'wlb_extra')

    def channel_user_from_db(self, user):
        """
        从binding中获取用户在渠道中的id
        :param user:
        :return:
        """
        try:
            return Binding.objects.filter(user=user).get().bid
        except:
            return None

    def save_to_session(self):
        channel_code = self.get_channel_code_from_request()
        channel_user = self.request.GET.get(self.external_channel_user_key, None)
        if channel_code:
            self.request.session[self.internal_channel_key] = channel_code
            # logger.debug('save to session %s:%s'%(self.internal_channel_key, channel_code))
        if channel_user:
            self.request.session[self.internal_channel_user_key] = channel_user
            # logger.debug('save to session %s:%s'%(self.internal_channel_user_key, channel_user))

    def clear_session(self):
        self.request.session.pop(self.internal_channel_key, None)
        self.request.session.pop(self.internal_channel_user_key, None)

    def save_to_introduceby(self, user, invite_code):
        """
        处理使用邀请码注册的用户
        """
        set_promo_user(self.request, user, invite_code)
        # try:
        #    channel = Channels.objects.filter(code=invite_code).get()
        #    introduced_by_record = IntroducedBy()
        #    introduced_by_record.channel = channel
        #    introduced_by_record.user = user
        #    introduced_by_record.save()
        #    logger.debug('save user %s introduced by channel to introducedby ' %user)
        # except:
        #    pass
        #
        # try:
        #    user_promote_token = PromotionToken.objects.filter(token=invite_code).get()
        #    #使用user_id查询
        #    introduced_by_user = User.objects.get(pk=user_promote_token.pk)
        #    introduced_by_record = IntroducedBy()
        #    introduced_by_record.introduced_by = introduced_by_user
        #    introduced_by_record.user = user
        #    introduced_by_record.save()
        #    logger.debug('save user %s introduced by user to introducedby ' %user)
        # except:
        #    pass

    def save_to_binding(self, user):
        """
        处理从url获得的渠道参数
        :param user:
        :return:
        """
        channel_user = self.channel_user
        bid_len = Binding._meta.get_field_by_name('bid')[0].max_length
        if channel_user and len(channel_user) <= bid_len:
            binding = Binding()
            binding.user = user
            binding.btype = self.channel_name
            binding.bid = channel_user
            binding.save()
            # logger.debug('save user %s to binding'%user)

    def register_call_back(self, user):
        """
        用户注册成功后的回调
        :param user:
        :return:
        """
        pass

    def validate_call_back(self, user):
        """
        用户实名验证后的回调
        :param user:
        :return:
        """
        pass

    def binding_card_call_back(self, user):
        """
        用户绑定银行卡之后的回调
        :param user:
        :return:
        """
        pass

    def purchase_call_back(self, user):
        """
        用户购买后回调，一般用于用于用户首次投资之后回调第三方接口
        :param user:
        :return:
        """
        pass

    def process_for_register(self, user, invite_code):
        """
        用户可以在从渠道跳转后的注册页使用邀请码，优先考虑邀请码
        """
        self.save_to_introduceby(user, invite_code)
        self.save_to_binding(user)
        self.register_call_back(user)
        self.clear_session()

    @property
    def processors(self):
        return [processor_class(self.request) for processor_class in coop_processor_classes]

    def all_processors_for_session(self):
        for processor in self.processors:
            channel_code = processor.get_channel_code_from_request()
            if processor.c_code == channel_code:
                processor.save_to_session()
                return
        self.save_to_session()

    def all_processors_for_user_register(self, user, invite_code):
        try:
            if not invite_code:
                invite_code = self.channel_code
            # logger.debug('get invite code %s'%(invite_code))
            if invite_code:
                # 通过渠道注册
                for processor in self.processors:
                    if processor.c_code == processor.channel_code:
                        processor.process_for_register(user, invite_code)
                        return
                # 默认注册
                self.process_for_register(user, invite_code)
        except:
            logger.exception('channel register process error for channel %s and user %s'%(invite_code, user.id))

    def get_user_channel_processor(self, user):
        """
        返回该用户的渠道处理器
        """
        try:
            channel_code = Channels.objects.filter(introducedby__user_id = user.id).get().code
            for channel_processor in self.processors:
                if channel_processor.c_code == channel_code:
                    return channel_processor
        except:
            return None

    def process_for_validate(self, user):
        try:
            channel_processor = self.get_user_channel_processor(user)
            # logger.debug('channel processor %s'%channel_processor)
            if channel_processor:
                channel_processor.validate_call_back(user)
        except:
            logger.exception('channel validate process error for user %s'%(user.id))

    def process_for_binding_card(self, user):
        try:
            channel_processor = self.get_user_channel_processor(user)
            # logger.debug('channel processor %s'%channel_processor)
            if channel_processor:
                channel_processor.binding_card_call_back(user)
        except:
            logger.exception('channel bind card process error for user %s'%(user.id))

    def process_for_purchase(self, user):
        try:
            channel_processor = self.get_user_channel_processor(user)
            if channel_processor:
                channel_processor.purchase_call_back(user)
        except:
            logger.exception('channel bind purchase process error for user %s'%(user.id))


class TianMangRegister(CoopRegister):
    def __init__(self, request):
        super(TianMangRegister, self).__init__(request)
        self.c_code = 'tianmang'
        self.coop_key = TINMANG_KEY
        self.call_back_url = TIANMANG_CALL_BACK_URL

    def register_call_back(self, user):
        params={
            "oid": self.coop_key,
            "sn" : self.channel_user,
            "uid": get_uid_for_coop(user.id),
            "uname": get_username_for_coop(user.id),
            "method": "json"
        }
        common_callback.apply_async(
            kwargs={'url': self.call_back_url, 'params': params, 'channel': 'tianmang'})


class YiRuiTeRegister(CoopRegister):
    def __init__(self, request):
        super(YiRuiTeRegister, self).__init__(request)
        self.c_code = 'yiruite'
        self.coop_key = YIRUITE_KEY
        self.call_back_url = YIRUITE_CALL_BACK_URL

    def register_call_back(self, user):
        uid_for_coop = get_uid_for_coop(user.id)
        sign = hashlib.md5(self.channel_user + uid_for_coop + self.coop_key).hexdigest()
        params = {
            "tid": self.channel_user,
            "uid": uid_for_coop,
            'ip': 'https://www.wanglibao.com',
            "sign": sign
        }
        # yiruite_callback.apply_async(kwargs={'url': self.call_back_url, 'params': params})
        common_callback.apply_async(
            kwargs={'url': self.call_back_url, 'params': params, 'channel':self.c_code})


class BengbengRegister(CoopRegister):
    def __init__(self, request):
        super(BengbengRegister, self).__init__(request)
        self.c_code = 'bengbeng'
        self.coop_id = BENGBENG_COOP_ID
        self.coop_key = BENGBENG_KEY
        self.call_back_url = BENGBENG_CALL_BACK_URL

    def binding_card_call_back(self, user):
        uid_for_coop = get_uid_for_coop(user.id)
        channel_user = self.channel_user_from_db(user)
        sign = hashlib.md5(self.coop_id + channel_user + uid_for_coop + self.coop_key).hexdigest()
        params = {
            'adID': self.coop_id,
            'annalID': channel_user,
            'idCode': uid_for_coop,
            'doukey': sign,
            'idName': get_username_for_coop(user.id)
        }
        common_callback.apply_async(
            kwargs={'url': self.call_back_url, 'params': params, 'channel': self.c_code})


class JuxiangyouRegister(CoopRegister):
    def __init__(self, request):
        super(JuxiangyouRegister, self).__init__(request)
        self.c_code = 'juxiangyou'
        self.coop_id = JUXIANGYOU_COOP_ID
        self.coop_key = JUXIANGYOU_KEY
        self.call_back_url = JUXIANGYOU_CALL_BACK_URL

    def register_call_back(self, user):
        uid_for_coop = get_uid_for_coop(user.id)
        sign = hashlib.md5(self.coop_id + self.channel_user + uid_for_coop + self.coop_key).hexdigest()
        params = {
            'tokenID' : self.coop_id,
            'recordID' : self.channel_user,
            'accessCode' : uid_for_coop,
            'accessKey' : sign
        }
        common_callback.apply_async(
            kwargs={'url': self.call_back_url, 'params': params, 'channel': self.c_code})


class DouwanRegister(CoopRegister):
    def __init__(self, request):
        super(DouwanRegister, self).__init__(request)
        self.c_code = 'douwanwang'
        self.call_back_url = DOUWANWANG_CALL_BACK_URL

    def douwan_callback(self, user, step):
        params = {
            'tid': get_tid_for_coop(user.id),
            step: get_uid_for_coop(user.id)
        }
        common_callback.apply_async(
            kwargs={'url': self.call_back_url, 'params': params, 'channel':self.c_code})

    def register_call_back(self, user):
        self.douwan_callback(user, 'step1')

    def validate_call_back(self, user):
        self.douwan_callback(user, 'step2')

    def binding_card_call_back(self, user):
        self.douwan_callback(user, 'step3')


class JinShanRegister(CoopRegister):
    def __init__(self, request):
        super(JinShanRegister, self).__init__(request)
        self.c_code = 'jinshan'
        self.extra_key = 'extra'
        self.call_back_url = JINSHAN_CALL_BACK_URL

    @property
    def channel_extra(self):
        """
        渠道扩展参数
        """
        return self.request.session.get(self.extra_key, None)

    def save_to_session(self):
        super(JinShanRegister, self).save_to_session()
        channel_extra = self.request.GET.get(self.extra_key, 'wlb_extra')
        if channel_extra:
            self.request.session[self.extra_key] = channel_extra
            # logger.debug('save to session %s:%s'%(self.extra_key, channel_extra))

    def save_to_binding(self, user):
        """
        处理从url获得的渠道参数
        :param user:
        :return:
        """
        channel_user = self.channel_user
        channel_extra = self.channel_extra
        bid_len = Binding._meta.get_field_by_name('bid')[0].max_length
        extra_len = Binding._meta.get_field_by_name('extra')[0].max_length
        if channel_user and len(channel_user) <= bid_len and len(channel_extra) <= extra_len:
            binding = Binding()
            binding.user = user
            binding.btype = self.channel_name
            binding.bid = channel_user
            binding.extra = channel_extra
            binding.save()
            # logger.debug('save user %s to binding'%user)

    def jinshan_call_back(self, user, offer_type, key):
        # Binding.objects.get(user_id=user.id),使用get如果查询不到会抛异常
        binding = Binding.objects.filter(user_id=user.id).first()
        if binding:
            extra = binding.extra
            bid = binding.bid
            sign = hashlib.md5( str(bid) + offer_type + key ).hexdigest()
            params = {
                'userid': bid,
                'offer_type': offer_type,
                'pass': sign,
                'extra': extra,
            }
            jinshan_callback.apply_async(
                kwargs={'url': self.call_back_url, 'params': params})

    def register_call_back(self, user):
        self.jinshan_call_back(user, 'wangli_regist_none', 'ZSEt6lzsK1rigjcOXZhtA6KfbGoS')

    def validate_call_back(self, user):
        self.jinshan_call_back(user, 'wangli_regist_reward', 'Cp9AhO2o9BQTDhbUBnHxmY0X4Kbg')

    def purchase_call_back(self, user):
        if P2PRecord.objects.filter(user_id=user.id, catalog=u'申购').count() == 1:
            self.jinshan_call_back(user, 'wangli_invest_reward', 'pA71ZhBf4DDeet7SLiLlGsT1qTYu')


class WaihuRegister(CoopRegister):
    def __init__(self, request):
        super(WaihuRegister, self).__init__(request)
        self.c_code = 'shls'


class ShiTouCunRegister(CoopRegister):
    def __init__(self, request):
        super(ShiTouCunRegister, self).__init__(request)
        self.extra_key = 'extra'
        self.c_code = 'shitoucun'
        self.call_back_url = SHITOUCUN_CALL_BACK_URL

    def save_to_session(self):
        super(ShiTouCunRegister, self).save_to_session()
        channel_extra = self.request.GET.get(self.extra_key, 'wlb_extra')
        if channel_extra:
            self.request.session[self.extra_key] = channel_extra
            # logger.debug('save to session %s:%s'%(self.extra_key, channel_extra))

    def save_to_binding(self, user):
        """
        处理从url获得的渠道参数
        :param user:
        :return:
        """
        channel_user = self.channel_user
        channel_extra = self.channel_extra
        bid_len = Binding._meta.get_field_by_name('bid')[0].max_length
        extra_len = Binding._meta.get_field_by_name('extra')[0].max_length
        if channel_user and len(channel_user) <= bid_len and len(channel_extra) <= extra_len:
            binding = Binding()
            binding.user = user
            binding.btype = self.channel_name
            binding.bid = channel_user
            binding.extra = channel_extra
            binding.save()
            # logger.debug('save user %s to binding'%user)

    def shitoucun_call_back(self, user):
        # Binding.objects.get(user_id=user.id),使用get如果查询不到会抛异常
        binding = Binding.objects.filter(user_id=user.id).first()
        if binding:
            logo = binding.extra
            uid = binding.bid
            uid_for_coop = get_uid_for_coop(user.id)
            params = {
                'logo': logo,
                'uid': uid,
                'e_uid': uid_for_coop,
                'e_user': uid_for_coop,
            }
            common_callback.apply_async(
                kwargs={'url': self.call_back_url, 'params': params, 'channel':self.c_code})

    def purchase_call_back(self, user):
        # 判断是否是首次投资
        if P2PRecord.objects.filter(user_id=user.id, catalog=u'申购').count() == 1:
            self.shitoucun_call_back(user)


class FUBARegister(CoopRegister):
    def __init__(self, request):
        super(FUBARegister, self).__init__(request)
        self.c_code = FUBA_CHANNEL_CODE
        self.call_back_url = FUBA_CALL_BACK_URL
        self.coop_id = FUBA_COOP_ID
        self.coop_key = FUBA_KEY

    @property
    def channel_user(self):
        # 富爸爸需求，如果uid为空，uid设置为FUBA_DEFAULT_TID
        channel_user = self.request.session.get(self.internal_channel_user_key)
        if not channel_user:
            channel_user = FUBA_DEFAULT_TID
        return channel_user

    def save_to_binding(self, user):
        """
        处理从url获得的渠道参数
        :param user:
        :return:
        """
        channel_user = self.channel_user
        bid_len = Binding._meta.get_field_by_name('bid')[0].max_length
        if len(channel_user) <= bid_len:
            if channel_user == FUBA_DEFAULT_TID or Binding.objects.filter(bid=channel_user).count() == 0:
                binding = Binding()
                binding.user = user
                binding.btype = self.channel_name
                binding.bid = channel_user
                binding.save()
                # logger.debug('save user %s to binding'%user)

    def purchase_call_back(self, user):
        """
        投资回调
        """
        # Binding.objects.get(user_id=user.id),使用get如果查询不到会抛异常
        binding = Binding.objects.filter(user_id=user.id).first()
        p2p_record = get_last_investment_for_coop(user.id)
        if binding and p2p_record:
            # 如果结算时间过期了则不执行回调
            earliest_settlement_time = redis_backend()._get('%s_%s' % (self.c_code, binding.bid))
            if earliest_settlement_time:
                earliest_settlement_time = datetime.datetime.strptime(earliest_settlement_time, '%Y-%m-%d %H:%M:%S')
                current_time = datetime.datetime.now()
                # 如果上次访问的时间是在30天前则不更新访问时间
                if earliest_settlement_time + datetime.timedelta(days=int(FUBA_PERIOD)) <= current_time:
                    return

            order_id = p2p_record.id
            goodsprice = p2p_record.amount
            # goodsname 提供固定值，固定值自定义，但不能为空
            goodsname = u"名称:网利宝,类型:产品标,周期:1月"
            sig = hashlib.md5(str(order_id)+str(self.coop_key)).hexdigest()
            status = u"直投【%s 元：已付款】" % goodsprice
            params = {
                'action': 'create',
                'planid': self.coop_id,
                'order': order_id,
                'goodsmark': '1',
                'goodsprice': goodsprice,
                'goodsname': goodsname,
                'sig': sig,
                'status': status,
                'uid': binding.bid,
            }
            common_callback.apply_async(
                kwargs={'url': self.call_back_url, 'params': params, 'channel':self.c_code})
            # 记录开始结算时间
            if not binding.extra:
                # earliest_settlement_time 为最近一次访问着陆页（跳转页）的时间
                if earliest_settlement_time:
                    binding.extra=earliest_settlement_time
                    binding.save()


class YunDuanRegister(CoopRegister):
    def __init__(self, request):
        super(YunDuanRegister, self).__init__(request)
        self.c_code = 'yunduan'
        self.coop_id = YUNDUAN_COOP_ID
        self.call_back_url = YUNDUAN_CALL_BACK_URL

    def yunduan_call_back(self):
        params = {
            'type': 'ef',
            'pid': self.coop_id,
        }
        # 云端跟踪回调
        common_callback.apply_async(
            kwargs={'url': self.call_back_url, 'params': params, 'channel':self.c_code})

        # 云端效果回调
        params['type'] = 'ec'
        common_callback.apply_async(
            kwargs={'url': self.call_back_url, 'params': params, 'channel':self.c_code})

    def validate_call_back(self, user):
        binding = Binding.objects.filter(user_id=user.id).first()
        if binding:
            self.yunduan_call_back()

    def purchase_call_back(self, user):
        # 判断是否是首次投资
        binding = Binding.objects.filter(user_id=user.id).first()
        p2p_record = P2PRecord.objects.filter(user_id=user.id, catalog=u'申购')
        if binding and p2p_record.count() == 1:
            self.yunduan_call_back()


class YiCheRegister(CoopRegister):
    def __init__(self, request):
        super(YiCheRegister, self).__init__(request)
        self.c_code = 'yiche'
        self.call_back_url = YICHE_CALL_BACK_URL
        self.coop_id = YICHE_COOP_ID
        self.coop_key = YICHE_KEY

    def yiche_call_back(self, url, params):
        params['_pid'] = self.coop_id
        params['format'] = 'xml'
        params['_ts'] = int(time.time())
        params_iteritems = sorted(params.iteritems(), key=lambda asd:asd[0], reverse=False)
        params_iteritems = '&'.join([key.lower()+'='+str(value) for key, value in params_iteritems if value])
        params['_sign'] = hashlib.md5(params_iteritems+self.coop_key).hexdigest()
        yiche_callback.apply_async(
            kwargs={'url': url, 'params': params, 'channel': self.c_code})

    def register_call_back(self, user):
        binding = Binding.objects.filter(user_id=user.id).first()
        if binding:
            url = self.call_back_url + '?method=AddPlatFormFinanceUser'
            introduced_by = IntroducedBy.objects.filter(user_id=user.id).first()
            mobile = '******'.join(get_phone_for_coop(user.id).split('***'))
            params = {
                'userId': binding.bid,
                'userName': mobile,
                'mobile': mobile,
                'companyId': 9,
                'regTime': introduced_by.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'regSource': 3,
            }
            self.yiche_call_back(url, params)

    def validate_call_back(self, user):
        binding = Binding.objects.filter(user_id=user.id).first()
        if binding:
            url = self.call_back_url + '?method=UpdatePlatFormFinanceUser'
            username = get_username_for_coop(user.id)
            params = {
                'userId': binding.bid,
                'realName': username,
                'companyId': 9,
            }
            self.yiche_call_back(url, params)

    def purchase_call_back(self, user):
        binding = Binding.objects.filter(user_id=user.id).first()
        p2p_record = get_last_investment_for_coop(user.id)
        if binding and p2p_record:
            url = self.call_back_url + '?method=AddPlatFormFinanceOrder'
            invest_time = p2p_record.create_time
            params = {
                'userId': binding.bid,
                'orderNo': p2p_record.id,
                'invest': str(p2p_record.amount),
                'investTime': invest_time.strftime('%Y-%m-%d %H:%M:%S'),
                'companyId': 9,
            }
            self.yiche_call_back(url, params)

            url = self.call_back_url + '?method=UpdatePlatFormFinanceOrder'
            period = p2p_record.product.period
            pay_method = p2p_record.product.pay_method
            profit_time = None
            # 根据支付方式判定标周期的单位（天/月）
            if pay_method in [u'等额本息', u'按月付息', u'到期还本付息']:
                profit_time = invest_time + relativedelta(months=period)
            elif pay_method in [u'日计息一次性还本付息', u'日计息月付息到期还本']:
                profit_time = invest_time + relativedelta(days=period)
            params = {
                'orderNo': p2p_record.id,
                'profit': '0.01',
                'profitTime': profit_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            self.yiche_call_back(url, params)


class ZhiTuiRegister(CoopRegister):
    def __init__(self, request):
        super(ZhiTuiRegister, self).__init__(request)
        self.c_code = 'zhitui1'
        self.extra_key = 'extra'
        self.coop_id = ZHITUI_COOP_ID
        self.call_back_url = ZHITUI_CALL_BACK_URL

    @property
    def channel_extra(self):
        """
        渠道扩展参数
        """
        return self.request.session.get(self.extra_key, '')

    def save_to_session(self):
        super(ZhiTuiRegister, self).save_to_session()
        channel_extra = self.request.GET.get(self.extra_key, None)
        if channel_extra:
            self.request.session[self.extra_key] = channel_extra
            # logger.debug('save to session %s:%s'%(self.extra_key, channel_extra))

    def save_to_binding(self, user):
        """
        处理从url获得的渠道参数
        :param user:
        :return:
        """
        channel_user = self.channel_user
        channel_extra = self.channel_extra
        bid_len = Binding._meta.get_field_by_name('bid')[0].max_length
        extra_len = Binding._meta.get_field_by_name('extra')[0].max_length
        if channel_user and len(channel_user) <= bid_len and len(channel_extra) <= extra_len:
            binding = Binding()
            binding.user = user
            binding.btype = self.channel_name
            binding.bid = channel_user
            binding.extra = channel_extra
            binding.save()
            # logger.debug('save user %s to binding'%user)

    def purchase_call_back(self, user):
        binding = Binding.objects.filter(user_id=user.id).first()
        p2p_record = get_last_investment_for_coop(user.id)
        if binding and p2p_record:
            invest_time = p2p_record.create_time
            invest_amount = p2p_record.amount
            period = p2p_record.product.period
            pay_method = p2p_record.product.pay_method
            # 根据支付方式判定标周期的单位（天/月）,如果是单位为月则转换为天
            if pay_method in [u'等额本息', u'按月付息', u'到期还本付息']:
                period = (invest_time + relativedelta(months=period) - invest_time).days

            if check_mobile(self.request):
                note = 'wap'
            else:
                note = 'pc'
            params = {
                'a_id': binding.extra,
                'subid': binding.bid,
                'o_cd': p2p_record.id,
                'p_cd': '',
                'price': invest_amount,
                'it_cnt': 1,
                'o_date': invest_time.strftime('%Y%m%d%H%M%S'),
                'rate': round(invest_amount * int(period) * Decimal(0.01) / Decimal(365), 2),
                'rate_memo': '',
                'status': 1,
                'note': note,
            }
            common_callback.apply_async(
                kwargs={'url': self.call_back_url, 'params': params, 'channel': self.c_code})


class ZGDXRegister(CoopRegister):
    def __init__(self, request):
        super(ZGDXRegister, self).__init__(request)
        self.c_code = 'zgdx'
        self.call_back_url = ZGDX_CALL_BACK_URL
        self.partner_no = ZGDX_PARTNER_NO
        self.service_code = ZGDX_SERVICE_CODE
        self.contract_id = ZGDX_CONTRACT_ID
        self.activity_id = ZGDX_ACTIVITY_ID
        self.plat_offer_id = ZGDX_PLAT_OFFER_ID
        self.coop_key = ZGDX_KEY
        self.iv = ZGDX_IV

    def zgdx_call_back(self, params):
        params['partner_no'] = self.partner_no,
        params_code = params['code']
        params_code['service_code'] = self.service_code,
        params_code['contract_id'] = self.contract_id,
        params_code['activity_id'] = self.activity_id,
        params_code['order_type'] = 1,
        params_code['plat_offer_id'] = self.plat_offer_id,
        if datetime.datetime.now().day >= 28:
            params_code['effect_type'] = 1,
        else:
            params_code['effect_type'] = 0,
        params['code'] = generate_Encrypt(self.coop_key, self.iv, 'aes_128_ecb', params_code)
        common_callback.apply_async(
            kwargs={'url': self.call_back_url, 'params': params, 'channel': self.c_code})

    def binding_card_call_back(self, user):
        binding = Binding.objects.filter(user_id=user.id).first()
        if binding:
            phone_number = WanglibaoUserProfile.objects.get(user_id=user.id).phone
            params = {
                'code': {
                    'request_no': get_username_for_coop(str(user.id)+'1'),
                    'phone_id': phone_number,
                },
            }
            self.zgdx_call_back(params)

    def purchase_call_back(self, user):
        # 判断是否是首次投资
        binding = Binding.objects.filter(user_id=user.id).first()
        p2p_record = P2PRecord.objects.filter(user_id=user.id, catalog=u'申购')
        # if binding and p2p_record.count() == 1:
        phone_number = WanglibaoUserProfile.objects.get(user_id=user.id).phone
        params = {
            'code': {
                'request_no': get_username_for_coop(str(user.id)+'2'),
                'phone_id': phone_number,
            },
        }
        self.zgdx_call_back(params)


# 注册第三方通道
coop_processor_classes = [TianMangRegister, YiRuiTeRegister, BengbengRegister,
                          JuxiangyouRegister, DouwanRegister, JinShanRegister,
                          ShiTouCunRegister, FUBARegister, YunDuanRegister,
                          YiCheRegister, ZhiTuiRegister, WaihuRegister]


#######################第三方用户查询#####################

class CoopQuery(APIView):
    """
    第三方用户查询api
    """
    permission_classes = ()
    channel = None

    # 查询用户的类型
    REGISTERED_USER = 0
    VALIDATED_USER = 1
    BINDING_USER = 2
    INVESTED_USER = 3

    # 每一页用户数
    PAGE_LENGTH = 20

    def get_promo_user(self, channel_code, startday, endday):
        """

        :param channel_code: like "tianmang"
        :param startday: 日期格式20050606
        :param endday:
        :return:
        """
        startday = datetime.datetime.strptime(startday, "%Y%m%d")
        endday = datetime.datetime.strptime(endday, "%Y%m%d")
        if startday > endday:
            endday, startday = startday, endday

        # daydelta = datetime.timedelta(days=1)
        daydelta = datetime.timedelta(hours=23, minutes=59, seconds=59, milliseconds=59)
        endday += daydelta
        promo_list = IntroducedBy.objects.filter(channel__code=channel_code, created_at__gte=startday, created_at__lte=endday)
        # logger.debug("promo user:%s"%[promo_user.user for promo_user in promo_list])
        return promo_list

    def check_sign(self, channel_code, startday, endday, sign):
        m = hashlib.md5()
        key = getattr(settings, 'WLB_FOR_%s_KEY' % channel_code.upper())
        m.update(startday+endday+key)
        local_sign = m.hexdigest()
        if sign != local_sign:
            # logger.debug('正确的渠道校验参数%s'%local_sign)
            logger.error(u"渠道查询接口，sign参数校验失败")
            return False
        return True

    def get_user_info_for_coop(self, user_type, user_id, time=None):
        user_info = {
            'time': time,
            'uid': get_uid_for_coop(user_id),
            'uname': get_username_for_coop(user_id),
            'phone': get_phone_for_coop(user_id),
            'tid': get_tid_for_coop(user_id),
        }
        if user_type == self.VALIDATED_USER:
            user_info['time'] = get_validate_time_for_coop(user_id)
        elif user_type == self.BINDING_USER:
            user_info['time'] = get_binding_time_for_coop(user_id)
        elif user_type == self.INVESTED_USER:
            amount, total_amount, invested_time = get_first_investment_for_coop(user_id)
            user_info['investment'] = amount
            user_info['total_investment'] = total_amount
            user_info['time'] = invested_time

        if user_info['time']:
            user_info['time'] = timezone.localtime(user_info['time']).strftime('%Y-%m-%d %H:%M:%S')

        return user_info

    def get_all_user_info_for_coop(self, channel_code, user_type, start_day, end_day, sign, page):
        if not self.check_sign(channel_code, start_day, end_day, sign):
            raise ValueError('wrong signature.')

        coop_users = self.get_promo_user(channel_code, start_day, end_day)

        if user_type == self.VALIDATED_USER:
            def is_validated_user(user_id):
                try:
                    return WanglibaoUserProfile.objects.filter(user_id=user_id).get().id_is_valid
                except:
                    return False
            # logger.debug('user id %s'%[u.user_id for u in coop_users])
            coop_users = [u for u in coop_users if is_validated_user(u.user_id)]
        elif user_type == self.BINDING_USER:
            def is_binding_user(user_id):
                return Card.objects.filter(user_id=user_id).exists()
            coop_users = [u for u in coop_users if is_binding_user(u.user_id)]
        elif user_type == self.INVESTED_USER:
            def is_invested_user(user_id):
                return P2PRecord.objects.filter(user_id=user_id, catalog=u'申购').exists()
            coop_users = [u for u in coop_users if is_invested_user(u.user_id)]

        # 处理分页
        if page:
            page = int(page)
            start = page * self.PAGE_LENGTH
            end = start + self.PAGE_LENGTH
            coop_users = coop_users[start:end]

        user_info = []
        for coop_user in coop_users:
            try:
                user_info.append(self.get_user_info_for_coop(user_type, coop_user.user_id, coop_user.created_at))
            except Exception, e:
                logger.exception(e)
                logging.debug('get user %s error:%s' % (coop_user.user_id, e))

        return user_info

    def get(self, request, channel_code, user_type, start_day, end_day, sign, page=None):
        try:
            result = {
                'errorcode': 0,
                'errormsg': 'sucess',
                'info': self.get_all_user_info_for_coop(channel_code, int(user_type), start_day, end_day, sign, page)
            }
        except ValueError, e:
            result = {
                'errorcode': 2,
                'errormsg': 'sign error',
            }
        except Exception, e:
            logger.exception(e.message)
            result = {
                'errorcode': 1,
                'errormsg': 'api error'
            }
        finally:
            # logger.debug(result)
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))


###########################################希财网对接#####################################################################

def get_rate(product_id_or_instance):
    """
    获取产品收益率
    :param product_id_or_instance: p2p产品id或是实例
    :return:
    """
    if isinstance(product_id_or_instance, P2PProduct):
        if product_id_or_instance.activity and product_id_or_instance.activity.rule:
            return product_id_or_instance.activity.rule.rule_amount + \
                   decimal.Decimal(product_id_or_instance.expected_earning_rate)
        else:
            return product_id_or_instance.expected_earning_rate


def get_amortization_time(product_id_or_instance):
    """
    获取还款起始，结束时间
    :param product_id_or_instance:
    :return: datetime
    """
    try:
        amortizations = ProductAmortization.objects.filter(product_id=product_id_or_instance.id).order_by('term_date')
        return amortizations.first().term_date, amortizations.last().term_date
    except:
        return None, None


def get_p2p_info(mproduct):

    product_info = {'for_freshman': 1 if mproduct.category == '新手标' else 0, 'period': mproduct.period,
                    'rate': get_rate(mproduct), 'amount': mproduct.total_amount,
                    'ordered_amount': mproduct.ordered_amount,
                    'buyer': mproduct.equities.all().annotate(Count('user', distinct=True)).count(),
                    'start_time': mproduct.publish_time, 'end_time': get_amortization_time(mproduct)[1],
                    'state': mproduct.status, 'borrower': mproduct.borrower_name, 'guarant_mode': '本息担保',
                    'guarantor': mproduct.warrant_company,
                    'amortization_start_time': get_amortization_time(mproduct)[0], 'amortization_end_time': 0,
                    'borrower_guarant_type': '第三方担保', 'repayment_type': mproduct.pay_method, 'start_price': 100,
                    'id': mproduct.id}

    return product_info


def xicai_get_token():
    # 希财现在的过期时间 10天  864000秒
    url = settings.XICAI_TOKEN_URL
    client_id = settings.XICAI_CLIENT_ID
    client_secret = settings.XICAI_CLIENT_SECRET
    response = requests.post(url, data={'client_id': client_id, 'client_secret': client_secret})
    return response.json()['access_token']


def xicai_get_p2p_info(mproduct, access_token):
    """
    将我们的p2p信息转换后提供给西财网
    :param mproduct:
    :return:
    """
    p2p_info = get_p2p_info(mproduct)

    # 希财状态码：-1：已流标，0：筹款中，1.已满标，2.已开始还款，3.预发布，4.还款完成，5.逾期
    # 录标，录标完成，待审核的标均不推送给希财
    p2p_state_convert_table = {
        # u'录标': u'录标',
        # u'录标完成': u'录标完成',
        # u'待审核': u'待审核',
        u'正在招标': 0,
        u'满标待打款': 1,
        u'满标已打款': 1,
        u'满标待审核': 1,
        u'满标已审核': 1,
        u'还款中': 2,
        u'流标': -1,
        u'已完成': 4,
    }

    # 希财还款方式码：1.按月付息 到期还本 2.按季付息 到期还本 3.每月等额本息 4.到期本息
    pay_type_convert_table = {
        u'等额本息': 3,
        u'先息后本': 1,
        u'按月付息': 1,
        u'到期还本付息': 4,
        u'按季度付息': 2,
        u'日计息一次性还本付息': 4,
        u'日计息月付息到期还本': 1,
    }

    def format_time(time):
        if time:
            return time.strftime('%Y-%m-%d')

    period = mproduct.period if mproduct.pay_method.startswith(u"日计息") else mproduct.period * 30

    xicai_info = {
        'access_token': access_token,
        'product_name': mproduct.name,
        'isexp': p2p_info['for_freshman'],
        'life_cycle': period,
        'ev_rate': p2p_info['rate'],
        'amount': p2p_info['amount'],
        'invest_amount': p2p_info['ordered_amount'],
        'inverst_mans': mproduct.equities.all().annotate(Count('user', distinct=True)).count(),
        'underlying_start': format_time(p2p_info['start_time']),
        'underlying_end': format_time(p2p_info['end_time']),
        'link_website': settings.XICAI_LOAD_PAGE.format(p2p_id=mproduct.id),
        'product_state': p2p_state_convert_table.get(p2p_info['state']),
        'borrower': p2p_info['borrower'],
        'guarantors': p2p_info['guarantor'],
        'publish_time': format_time(p2p_info['start_time']),
        'repay_start_time': format_time(p2p_info['amortization_start_time']),
        'repay_end_time': format_time(p2p_info['amortization_end_time']),
        'borrow_type': 4,   # 都是第三方担保
        'pay_type': pay_type_convert_table.get(p2p_info['repayment_type']),
        'start_price': 100,
        'p2p_product_id': p2p_info['id']
    }

    if settings.ENV != settings.ENV_PRODUCTION:
        xicai_info['test'] = 1
    else:
        xicai_info['test'] = 0
    return xicai_info


def xicai_post_product_info(mproduct, access_token):
    p2p_info = xicai_get_p2p_info(mproduct, access_token)
    url = settings.XICAI_CREATE_P2P_URL
    ret = requests.post(url, data=p2p_info)
    return ret.text


def xicai_post_updated_product_info(mproduct, access_token):
    p2p_info = xicai_get_p2p_info(mproduct, access_token)
    updated_p2p_info = {}
    for k in ['access_token', 'invest_amount',
              'inverst_mans', 'underlying_end',
              'product_state', 'repay_start_time',
              'repay_end_time', 'p2p_product_id']:
        updated_p2p_info[k] = p2p_info[k]
    url = settings.XICAI_UPDATE_P2P_URL
    ret = requests.post(url, data=updated_p2p_info)
    return ret.text


def xicai_get_new_p2p():
    """
    获取新标给希财
    :return:
    """
    now = timezone.now()
    start_time = now - settings.XICAI_UPDATE_TIMEDELTA
    return P2PProduct.objects.filter(publish_time__gte=start_time).filter(publish_time__lt=now).all()


def xicai_get_updated_p2p():
    """
    获取有更新的标给希财
    :return:
    """
    start_time = timezone.now() - settings.XICAI_UPDATE_TIMEDELTA
    p2p_equity = P2PEquity.objects.filter(created_at__gte = start_time).all()
    return set([p.product for p in p2p_equity])


def xicai_send_data():
    """
    向西财网 post最新的标的信息
    :return:
    """
    access_token = xicai_get_token()
    # 更新新标数据
    for p2p_product in xicai_get_new_p2p():
        xicai_post_product_info(p2p_product, access_token)
    # 更新有变动的标的的数据
    for p2p_product in xicai_get_updated_p2p():
        xicai_post_updated_product_info(p2p_product, access_token)


def get_xicai_user_info(key, sign):
    """
    author: Zhoudong
    根据希财提供的sign 获取必须的用户信息.
    如, 手机号, 用户名, (邮箱, 等等)
    :return:
    """
    import base64
    # pip install pydes --allow-external pydes --allow-unverified pydes
    from pyDes import des, CBC, PAD_PKCS5
    k = des(key, CBC, key, pad=None, padmode=PAD_PKCS5)

    # # 加密
    # d = k.encrypt("phone=13811849325&name=zhoudong&pid=0&t=123456789")
    # print "Encrypted: %r" % base64.b64encode(d)

    # 解密
    d = base64.b64decode(sign)
    source = k.decrypt(d)
    arg_list = source.split('&')
    data = dict()

    for arg in arg_list:
        data[arg.split('=')[0]] = arg.split('=')[1]

    return data


class CsaiUserQuery(APIView):
    """
    author: Zhoudong
    希财专用用户信息查询接口
    """
    permission_classes = ()

    def check_sign(self):

        t = str(self.request.GET.get('t', None))
        token = self.request.GET.get('token', None)

        if t and token:
            from hashlib import md5
            sign = md5(md5(t).hexdigest() + settings.XICAI_CLIENT_SECRET).hexdigest()
            if token == sign:
                return True

    def get(self, request):

        if self.check_sign():

            page = int(self.request.GET.get('page', 1))
            page_size = int(self.request.GET.get('pagesize', 10))
            users_list = []
            ret = dict()

            start_date = self.request.GET.get('startdate', None)
            end_date = self.request.GET.get('enddate', None)

            if not start_date:
                start_date = '1970-01-01'
            start = str_to_float(start_date)
            if end_date:
                end = str_to_float(end_date)
            else:
                end = time.time()

            binds = Binding.objects.filter(
                (Q(btype=u'csai') | Q(btype=u'xicai')) & Q(created_at__gte=start) & Q(created_at__lte=end))

            users = [b.user for b in binds]
            ret['total'] = len(users)

            # 获取总页数, 和页数不对处理
            com_page = len(users) / page_size + 1
            if page > com_page:
                page = com_page
            if page < 1:
                page = 1

            # 获取到对应的页数的所有用户
            if len(users) / page_size >= page:
                users = users[(page - 1) * page_size: page * page_size]
            else:
                users = users[(page - 1) * page_size:]

            for user in users:
                user_dict = dict()
                user_dict['id'] = user.id
                user_dict['username'] = user.username
                user_dict['email'] = user.email
                user_dict['regtime'] = user.date_joined

                # 去用户详情表查
                user_profile = WanglibaoUserProfile.objects.get(user=user)
                user_dict['realname'] = user_profile.name
                user_dict['phone'] = user_profile.phone

                user_dict['totalmoney'] = \
                    P2PEquity.objects.filter(user=user).aggregate(Sum('equity'))['equity__sum'] or 0

                user_dict['ip'] = None
                user_dict['qq'] = None

                users_list.append(user_dict)

            ret['list'] = users_list
            ret['code'] = 0

        else:
            ret = {
                'code': 1,
                'msg': u"没有权限访问"
            }
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class CsaiInvestmentQuery(APIView):
    """
    author: Zhoudong
    希财专用投资查询接口
    """
    permission_classes = ()

    def check_sign(self):
        t = str(self.request.GET.get('t', None))
        token = self.request.GET.get('token', None)
        if t and token:
            from hashlib import md5
            sign = md5(md5(t).hexdigest() + settings.XICAI_CLIENT_SECRET).hexdigest()
            if token == sign:
                return True

    def get(self, request):

        if self.check_sign():

            page = int(self.request.GET.get('page', 1))
            page_size = int(self.request.GET.get('pagesize', 10))
            p2p_list = []
            ret = dict()

            start_date = self.request.GET.get('startdate', None)
            end_date = self.request.GET.get('enddate', None)

            if not start_date:
                start_date = '1970-01-01'
            start = str_to_float(start_date)
            if end_date:
                end = str_to_float(end_date)
            else:
                end = time.time()

            binds = Binding.objects.filter(
                (Q(btype=u'csai') | Q(btype=u'xicai')) & Q(created_at__gte=start) & Q(created_at__lte=end))
            users = [b.user for b in binds]
            p2ps = P2PEquity.objects.filter(user__in=users)

            ret['total'] = p2ps.count()

            # 获取总页数, 和页数不对处理
            com_page = len(p2ps) / page_size + 1

            if page > com_page:
                page = com_page
            if page < 1:
                page = 1

            # 获取到对应的页数的所有用户
            if len(p2ps) / page_size >= page:
                p2ps = p2ps[(page - 1) * page_size: page * page_size]
            else:
                p2ps = p2ps[(page - 1) * page_size:]

            for p2p in p2ps:
                p2p_dict = dict()
                p2p_dict['id'] = p2p.id
                p2p_dict['pid'] = p2p.product_id
                p2p_dict['username'] = p2p.user.username
                p2p_dict['datetime'] = p2p.created_at
                p2p_dict['money'] = p2p.equity
                period = p2p.product.period if not p2p.product.pay_method.startswith(u"日计息") \
                    else p2p.product.period/30.0
                p2p_dict['commission'] = p2p.equity * period * 0.012 / 12

                p2p_list.append(p2p_dict)

            ret['list'] = p2p_list
            ret['code'] = 0

        else:
            ret = {
                'code': 1,
                'msg': u"没有权限访问"
            }
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


if __name__ == '__main__':
    print xicai_get_updated_p2p()
    print xicai_get_new_p2p()
    xicai_send_data()


# 菜苗渠道
def caimiao_post_platform_info():
    """
    author: Zhoudong
    http请求方式: POST  平台基本数据
    http://121.40.31.143:86/api/JsonsFinancial/PlatformBasic/
    向菜苗推送我们的平台信息.
    :return:
    """
    url = settings.CAIMIAO_PlatformBasic_URL
    key = settings.CAIMIAO_SECRET

    post_data = dict()

    data = {
        'tits': u'网利宝',
        'provinces': u'北京市',
        'zones': u'朝阳区',
        'terms_scopes_mins': u'3个月',
        'terms_scopes_maxs': u'6个月',
        'aprs_mins': u'11%',
        'aprs_maxs': u'18%',
        'times_ups': u'2014-08-20',
        'registered_capitals': u'5000万',
        'telephones_services': u'4008588066',
        'types_projects': u'车贷20%, 房贷55%, 银行过桥10%, 供应链15%',
        'security_mode': u'融资性担保公司, 平台垫付',
        'legal_persons': u'杨华',
        'icps': u'京ICP备14014548号',
        'coms_names': u'北京网利科技有限公司',
        'coms_scales': u'120人',
        'coms_address': u'北京市朝阳区东三环北路乙2号1幢海南航空大厦A座7层',
        'coms_bewrites': u'',
        'qqs': u'',
        'websites': u'www.wanglibao.com'
    }

    # php md5('cmjr'.md5($key.json_encod(主数据)));
    sign = hashlib.md5('cmjr' + hashlib.md5(key + json.dumps(data)).hexdigest()).hexdigest()

    post_data.update(key=key)
    post_data.update(sign=sign)
    post_data.update(data=data)

    # 参数转成json 格式
    json_data = json.dumps(post_data)

    ret = requests.post(url, data=json_data)
    return ret.text


def caimiao_post_p2p_info():
    """
    author: Zhoudong
    http请求方式: POST  标的信息
    http://121.40.31.143:86/api/JsonsFinancial/ProdMain/
    :return:
    """

    url = settings.CAIMIAO_ProdMain_URL
    key = settings.CAIMIAO_SECRET

    post_data = dict()

    now = timezone.now()

    start_time = now - settings.XICAI_UPDATE_TIMEDELTA
    new_products = P2PProduct.objects.filter(Q(publish_time__gte=start_time) & Q(publish_time__lt=now))
    # 还需要把更新的标全部推送
    p2p_equity = P2PEquity.objects.filter(created_at__gte=start_time).all()
    wangli_products = set([p.product for p in p2p_equity])
    wangli_products.update(new_products)

    data = dict()
    data['tits'] = u"网利宝"
    data['prods'] = []

    for product in wangli_products:
        prod = dict()
        prod['prods_codes'] = product.pk
        prod['prods_tits'] = product.name
        prod['prods_type'] = product.category
        prod['borrower'] = product.borrower_name
        prod['moneys_mains'] = product.total_amount
        prod['aprs_mins'] = product.expected_earning_rate
        prod['aprs_maxs'] = product.excess_earning_rate
        period = product.period if product.pay_method.startswith(u"日计息") else product.period * 30
        prod['terms_scopes'] = period
        prod['prods_start'] = product.publish_time.strftime("%Y-%m-%d")
        prod['prods_end'] = product.soldout_time.strftime("%Y-%m-%d") if product.soldout_time else None

        data['prods'].append(prod)

    # php md5('cmjr'.md5($key.json_encod(主数据)));
    sign = hashlib.md5('cmjr' + hashlib.md5(key + json.dumps(data)).hexdigest()).hexdigest()

    post_data.update(key=key)
    post_data.update(sign=sign)
    post_data.update(data=data)

    # 参数转成json 格式
    json_data = json.dumps(post_data)

    ret = requests.post(url, data=json_data)

    return ret.text


def caimiao_post_volumes_info():
    """
    author: Zhoudong
    http请求方式: POST  成交量
    http://121.40.31.143:86/api/JsonsFinancial/Volumes/
    :return:
    """

    url = settings.CAIMIAO_DEAL_Volumes_URL
    key = settings.CAIMIAO_SECRET

    post_data = dict()

    now = timezone.now()
    start = now - timezone.timedelta(days=1)
    equities = P2PEquity.objects.filter(Q(created_at__gte=start) & Q(created_at__lt=now))

    data = dict()
    data['tits'] = u"网利宝"
    data['volumes_nows'] = equities.aggregate(Sum('equity'))['equity__sum'] or 0
    data['investors_number_now'] = equities.values_list('user', flat=True).distinct().count()
    data['volumes_all'] = P2PEquity.objects.all().aggregate(Sum('equity'))['equity__sum'] or 0
    data['times'] = timezone.localtime(now).strftime('%Y%m%d')

    # php md5('cmjr'.md5($key.json_encod(主数据)));
    sign = hashlib.md5('cmjr' + hashlib.md5(key + json.dumps(data)).hexdigest()).hexdigest()

    post_data.update(key=key)
    post_data.update(sign=sign)
    post_data.update(data=data)

    # 参数转成json 格式
    json_data = json.dumps(post_data)

    ret = requests.post(url, data=json_data)

    return ret.text


def caimiao_post_rating_info():
    """
    author: Zhoudong
    http请求方式: POST  网贷评级数据
    http://121.40.31.143:86/api/JsonsFinancial/Rating/
    :return:
    """

    url = settings.CAIMIAO_Rating_URL
    key = settings.CAIMIAO_SECRET

    post_data = dict()

    data = dict()
    data['tits'] = u"网利宝"
    data['site_registration_number'] = User.objects.count()
    data['risk_reserve_fund_sum'] = u'5000万'
    data['back_amount'] = \
        ProductAmortization.objects.all().aggregate(Sum('principal'))['principal__sum'] +\
        ProductAmortization.objects.all().aggregate(Sum('interest'))['interest__sum']

    now = timezone.now()
    end = now + timezone.timedelta(days=60)
    product_amortizations = ProductAmortization.objects.filter(Q(term_date__gte=now) & Q(term_date__lt=end))

    data['60days_back_amount'] = \
        product_amortizations.aggregate(Sum('principal'))['principal__sum'] +\
        product_amortizations.aggregate(Sum('interest'))['interest__sum']
    data['times'] = timezone.localtime(now).strftime('%Y%m%d')

    # php md5('cmjr'.md5($key.json_encod(主数据)));
    sign = hashlib.md5('cmjr' + hashlib.md5(key + json.dumps(data)).hexdigest()).hexdigest()

    post_data.update(key=key)
    post_data.update(sign=sign)
    post_data.update(data=data)

    # 参数转成json 格式
    json_data = json.dumps(post_data)

    ret = requests.post(url, data=json_data)

    return ret.text


# 众牛的API
class ZhongniuP2PQuery(APIView):
    """
    author: Zhoudong
    http请求方式: GET  获取请求当天发布并且当天结束的项目（防止漏掉秒杀标）及系统中所有未完成（预投标，投标中）的项目列表。
    http://xxxxxx.com/getList
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def check_sign(self):

        pwd = str(self.request.GET.get('pwd', None))
        if pwd and pwd == settings.ZHONGNIU_SECRET:
            return True

    def get(self, request):

        if self.check_sign():
            ret = dict()
            ret['list'] = []
            products = P2PProduct.objects.filter(
                Q(status=u'录标') | Q(status=u'录标完成') | Q(status=u'待审核') | Q(status=u'正在招标'))

            products = set(products)

            now = timezone.now()
            start = now - timezone.timedelta(days=1)
            end = now + timezone.timedelta(days=1)

            # 我们的秒杀标的规则是什么. 周期一天内的显示.
            sec_kill_products = P2PProduct.objects.filter(Q(publish_time__lt=now) & Q(publish_time__gte=start) &
                                                          Q(end_time__lt=end) & Q(end_time__gte=now))

            for p in sec_kill_products:
                if p.end_time - p.publish_time <= timezone.timedelta(days=1):
                    products.add(p)

            if len(products) > 0:
                ret['status'] = 0
                for product in products:
                    if product.status in [u'录标', u'录标完成', u'待审核']:
                        status = 0
                    elif product.status == u'正在招标':
                        status = 1
                    else:
                        status = 2
                    data = dict()
                    data['pid'] = product.pk
                    data['status'] = status
                    data['amounted'] = product.ordered_amount
                    data['progress'] = product.completion_rate
                    ret['list'].append(data)
            else:
                ret['status'] = 1

        else:
            ret = {
                'status': 2,
                'msg': u"没有权限访问"
            }
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class ZhongniuP2PDataQuery(APIView):
    """
    author: Zhoudong
    http请求方式: GET  获取请求指定pid的项目详情数据（请求中会附带pid参数）
    http://xxxxxx.com/getData/pid/123456
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def check_sign(self):

        pwd = str(self.request.GET.get('pwd', None))
        if pwd and pwd == settings.ZHONGNIU_SECRET:
            return True

    def get(self, request):

        ret = dict()

        pid = str(self.request.GET.get('pid', None))

        if self.check_sign():
            if pid:
                try:
                    product = P2PProduct.objects.get(pk=pid)
                except Exception, e:
                    ret['status'] = 2
                    ret['msg'] = u'%s' % e
                    return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))

            if product:
                ret['status'] = 0
                data = dict()
                data['pid'] = product.pk
                data['name'] = product.name
                # 根据不同环境对应不同的url
                if settings.ENV == 'debug':
                    base_url = 'http://127.0.0.1:8000'
                if settings.ENV == 'staging':
                    base_url = 'https://staging.wanglibao.com'
                if settings.ENV == 'production':
                    base_url = 'https://www.wanglibao.com'
                data['url'] = base_url + '/p2p/detail/' + str(product.pk)

                data['type'] = 2

                data['yield'] = product.expected_earning_rate
                data['duration'] = product.period

                if product.pay_method == u'等额本息':
                    pay_method = 3
                elif product.pay_method == u'按月付息':
                    pay_method = 1
                elif product.pay_method == u'到期还本付息':
                    pay_method = 4
                else:
                    pay_method = 9
                data['repaytype'] = pay_method

                data['guaranttype'] = 1

                data['threshold'] = 100

                if product.status in [u'录标', u'录标完成', u'待审核']:
                    status = 0
                elif product.status == u'正在招标':
                    status = 1
                else:
                    status = 2
                data['status'] = status

                data['amount'] = product.total_amount
                data['amounted'] = product.ordered_amount
                data['progress'] = "%.2f" % product.completion_rate

                # Attachment 重中的图片
                detail = list()
                detail.append({'title': product.name})
                detail.append({'content': product.usage})

                attachments = product.attachment_set.all()
                for attachment in attachments:
                    url = base_url + attachment.file.url
                    detail.append({'image': url})
                data['detail'] = detail

                data['startdate'] = product.publish_time.strftime("%Y-%m-%d")
                data['enddate'] = product.end_time.strftime("%Y-%m-%d")
                data['publishtime'] = product.publish_time.strftime("%Y-%m-%d %H:%M:%S")

                ret['data'] = data

            else:
                ret['status'] = 1

        else:
            ret = {
                'status': 2,
                'msg': u"没有权限访问"
            }
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


# 中金在线
def zhongjin_get_products():
    """
    author: Zhoudong
    :return: 返回所有需要处理的 p2p 产品
    """

    now = timezone.now()

    wangli_products = set()
    start_time = now - settings.ZHONGJIN_UPDATE_TIMEDELTA

    new_products = P2PProduct.objects.filter(Q(publish_time__gte=start_time) & Q(publish_time__lt=now))
    wangli_products.update(new_products)
    # 还需要把更新的标全部推送
    p2p_equity = P2PEquity.objects.filter(created_at__gte=start_time).all()
    updated_products = set([p.product for p in p2p_equity])
    wangli_products.update(updated_products)

    prods = []

    for product in wangli_products:
        prod = dict()
        if product in new_products:
            prod['method'] = 'add'
        else:
            if product.status in [u'录标', u'录标完成', u'待审核', u'正在招标']:
                prod['method'] = 'update'
            else:
                prod['method'] = 'down'

        prod['classId'] = 1
        if not prod['method'] == 'add':
            prod['productId'] = product.pk    # productId 不是我们的id, 是他们返回的用来修改对应的
        if prod['method'] == 'add':
            prod['productName'] = product.name
            prod['borrowMoney'] = product.total_amount
            prod['investmentMoney'] = 100
            period = product.period if product.pay_method.startswith(u"日计息")/30 else product.period
            prod['investmentPeriod'] = period

            prod['completeness'] = "%.2f" % product.completion_rate
            prod['stopTime'] = product.soldout_time.strftime("%Y-%m-%d") \
                if product.soldout_time else product.end_time.strftime("%Y-%m-%d")
            prod['riskPreference'] = 2
            prod['expectedYield'] = product.expected_earning_rate

            # 根据不同环境对应不同的url
            if settings.ENV == 'debug':
                prod['enterpriseId'] = settings.ZHONGJIN_TEST_ID
                base_url = 'http://127.0.0.1:8000'
            if settings.ENV == 'staging':
                prod['enterpriseId'] = settings.ZHONGJIN_TEST_ID
                base_url = 'https://staging.wanglibao.com'
            if settings.ENV == 'production':
                prod['enterpriseId'] = settings.ZHONGJIN_ID
                base_url = 'https://www.wanglibao.com'
            prod['linkProfiles'] = base_url + '/p2p/detail/' + str(product.pk)

        prod['dt'] = int(time.time())

        prods.append(prod)

    return prods


def zhongjin_get_sign(args_dict):
    """
    author: Zhoudong
    md5 加密方式: 待传参数 aid=1&bid=2&cid=3 那么加密串为：aid=1||bid=2||cid=32CF7AC2A27CC9B48C4EFCD7E356CD95F
    http://open.rong.cnfol.com/product.html
    根据参数获取对应的 sign, 然后拼成需要去请求的url
    :return:
    """
    if settings.ENV == settings.ENV_PRODUCTION:
        url = settings.ZHONGJIN_P2P_URL
        key = settings.ZHONGJIN_SECRET
    else:
        url = settings.ZHONGJIN_P2P_TEST_URL
        key = settings.ZHONGJIN_TEST_SECRET

    url += '?' + urlencode(args_dict)

    l = urlencode(args_dict).split('&')
    l.sort()

    md5_str = ''
    for i in l:
        md5_str += i + '||'

    md5_str = md5_str[0:-2] + key

    sign = hashlib.md5(md5_str).hexdigest()
    url += '&sign=' + sign

    return url


def zhongjin_post_p2p_info():
    """
    author: Zhoudong
    去请求对应的地址
    :return:
    """
    prods = zhongjin_get_products()
    for args_dict in prods:
        url = zhongjin_get_sign(args_dict)
        print url
        urllib2.urlopen(url)


def zhongjin_list_p2p():
    """
    author: Zhoudong
    查看所有数据
    :return:
    """
    args_dict = dict()
    args_dict['method'] = 'list'
    args_dict['dt'] = int(time.time())
    # 根据不同环境对应不同的url
    if settings.ENV == 'production':
        args_dict['enterpriseId'] = settings.ZHONGJIN_ID
    else:
        args_dict['enterpriseId'] = settings.ZHONGJIN_TEST_ID

    args_dict['classId'] = 1

    url = zhongjin_get_sign(args_dict)

    return url
