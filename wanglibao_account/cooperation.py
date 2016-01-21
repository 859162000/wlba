#!/usr/bin/env python
# encoding:utf-8
import decimal
from wanglibao_account.utils import FileObject
import cStringIO
import json
import urllib2
from django.utils.http import urlencode
import pytz

from wanglibao_account.oauth2_utils import check_token, create_token
from wanglibao_account.utils import str_to_float

if __name__ == '__main__':
    import os
    import sys

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wanglibao.settings')

from wanglibao_reward.models import WanglibaoActivityReward
from experience_gold.models import ExperienceEvent
from weixin.models import WeixinAccounts
import qrcode
import hashlib
import datetime
import time
import logging
from django.db import transaction
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.db.models import Sum, Q, Count
from django.http import HttpResponse
from django.utils import timezone
from wanglibao_account import message as inside_message
from wanglibao_sms.tasks import send_messages
import requests
from rest_framework import renderers
from rest_framework.views import APIView
from marketing.models import Channels, IntroducedBy, PromotionToken, GiftOwnerInfo, GiftOwnerGlobalInfo
from marketing.utils import set_promo_user, get_channel_record, get_user_channel_record
from wanglibao import settings
from wanglibao_redpack import backends as redpack_backends
from misc.models import Misc
from wanglibao_reward.models import WanglibaoActivityReward as ActivityReward
from marketing.models import Reward
from wanglibao.settings import YIRUITE_CALL_BACK_URL, \
     TIANMANG_CALL_BACK_URL, WLB_FOR_YIRUITE_KEY, YIRUITE_KEY, BENGBENG_KEY, \
     WLB_FOR_BENGBENG_KEY, BENGBENG_CALL_BACK_URL, BENGBENG_COOP_ID, JUXIANGYOU_COOP_ID, JUXIANGYOU_KEY, \
     JUXIANGYOU_CALL_BACK_URL, TINMANG_KEY, DOUWANWANG_CALL_BACK_URL, JINSHAN_CALL_BACK_URL, WLB_FOR_JINSHAN_KEY, \
     WLB_FOR_SHLS_KEY, SHITOUCUN_CALL_BACK_URL, WLB_FOR_SHITOUCUN_KEY, FUBA_CALL_BACK_URL, WLB_FOR_FUBA_KEY, \
     FUBA_COOP_ID, FUBA_KEY, FUBA_CHANNEL_CODE, FUBA_DEFAULT_TID, FUBA_PERIOD, \
     WLB_FOR_YUNDUAN_KEY, YUNDUAN_CALL_BACK_URL, YUNDUAN_COOP_ID, WLB_FOR_YICHE_KEY, YICHE_COOP_ID, \
     YICHE_KEY, YICHE_CALL_BACK_URL, WLB_FOR_ZHITUI1_KEY, ZHITUI_COOP_ID, ZHITUI_CALL_BACK_URL, \
     WLB_FOR_ZGDX_KEY, ZGDX_CALL_BACK_URL, ZGDX_PARTNER_NO, ZGDX_SERVICE_CODE, ZGDX_CONTRACT_ID, \
     ZGDX_ACTIVITY_ID, ZGDX_KEY, ZGDX_IV, WLB_FOR_NJWH_KEY, ENV, ENV_PRODUCTION, WLB_FOR_FANLITOU_KEY, \
     WLB_FOR_XUNLEI9_KEY, XUNLEIVIP_CALL_BACK_URL, XUNLEIVIP_KEY, XUNLEIVIP_REGISTER_CALL_BACK_URL, \
     XUNLEIVIP_REGISTER_KEY, MAIMAI1_CHANNEL_CODE, MAIMAI_CALL_BACK_URL, YZCJ_CALL_BACK_URL, YZCJ_COOP_KEY,\
     XUNLEIVIP_LOGIN_URL
from wanglibao_account.models import Binding, IdVerification
from wanglibao_account.tasks import common_callback, jinshan_callback, yiche_callback, zgdx_callback, \
                                    xunleivip_callback
from wanglibao_p2p.models import P2PEquity, P2PRecord, P2PProduct, ProductAmortization, AutomaticPlan
from wanglibao_pay.models import Card, PayInfo
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_account.models import UserThreeOrder
from wanglibao_redis.backend import redis_backend
from dateutil.relativedelta import relativedelta
from wanglibao_account.utils import encrypt_mode_cbc, encodeBytes
from decimal import Decimal
from wanglibao_reward.models import WanglibaoUserGift
from user_agents import parse
import uuid
import urllib
from .utils import xunleivip_generate_sign
from wanglibao_sms.messages import sms_alert_unbanding_xunlei

logger = logging.getLogger('wanglibao_cooperation')


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
        channel = get_channel_record(self.channel_code)
        if channel:
            channel_name = channel.name
        else:
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
        channel_name = self.channel_name
        bid_len = Binding._meta.get_field_by_name('bid')[0].max_length
        if channel_name and channel_user and len(channel_user) <= bid_len:
            binding = Binding()
            binding.user = user
            binding.btype = channel_name
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

    def purchase_call_back(self, user, order_id):
        """
        用户购买后回调，一般用于用于用户首次投资之后回调第三方接口
        :param order_id:
        :param user:
        :return:
        """
        pass

    def recharge_call_back(self, user, order_id):
        """
        用户充值后回调，一般用于用户首次充值之后回调第三方接口
        :param order_id:
        :param user:
        :return:
        """
        pass

    def click_call_back(self):
        """
        用户点击投放页后回调第三方接口
        :param:
        :return:
        """
        pass

    def process_for_register(self, user, invite_code):
        """
        用户可以在从渠道跳转后的注册页使用邀请码，优先考虑邀请码
        """
        self.save_to_introduceby(user, invite_code)
        if user.wanglibaouserprofile.utype != '3':
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

    def weixin_redpack_distribute(self, user):
        phone = user.wanglibaouserprofile.phone
        logger.debug('通过weixin_redpack渠道注册,phone:%s' % (phone,))
        records = WanglibaoUserGift.objects.filter(valid=0, identity=phone)
        for record in records:
            try:
                redpack_backends.give_activity_redpack(user, record.rules.redpack, 'pc')
            except Exception, reason:
                logger.debug('Fail:注册的时候发送加息券失败, reason:%s' % (reason,))
            else:
                logger.debug('Success:发送红包完毕,user:%s, redpack:%s' % (self.request.user, record.rules.redpack,))
            record.user = user
            record.valid = 1
            record.save()

    def all_processors_for_user_register(self, user, invite_code):
        try:
            self.weixin_redpack_distribute(user)
        except Exception, reason:
            pass

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
        channel = get_user_channel_record(user.id)
        if channel:
            channel_code = channel.code
            for channel_processor in self.processors:
                if channel_processor.c_code == channel_code:
                    return channel_processor

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

    def process_for_purchase(self, user, order_id):
        try:
            channel_processor = self.get_user_channel_processor(user)
            if channel_processor:
                channel_processor.purchase_call_back(user, order_id)
        except:
            logger.exception('channel bind purchase process error for user %s'%(user.id))

    def process_for_recharge(self, user, order_id):
        try:
            channel_processor = self.get_user_channel_processor(user)
            if channel_processor:
                channel_processor.recharge_call_back(user, order_id)
        except:
            logger.exception('channel recharge process error for user %s'%(user.id))

    def process_for_click(self, channel_code):
        try:
            for processor in self.processors:
                if processor.c_code == processor.channel_code:
                    processor.click_call_back()
                    return
        except Exception, e:
            logger.exception('%s click process error' % channel_code)
            logger.info(e)

    def binding_for_after_register(self, user):
        """
        处理注册之后的第三方用户渠道绑定关系
        :param user:
        :return:
        """
        pass

    def process_after_binding(self, user):
        try:
            channel_processor = self.get_user_channel_processor(user)
            if channel_processor:
                channel_processor.binding_for_after_register(user)
                return
        except:
            logger.exception('process after binding error for user %s' % user.id)


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

    def clear_session(self):
        super(JinShanRegister, self).clear_session()
        self.request.session.pop(self.extra_key, None)

    def save_to_binding(self, user):
        """
        处理从url获得的渠道参数
        :param user:
        :return:
        """
        channel_user = self.channel_user
        channel_extra = self.channel_extra
        channel_name = self.channel_name
        bid_len = Binding._meta.get_field_by_name('bid')[0].max_length
        extra_len = Binding._meta.get_field_by_name('extra')[0].max_length
        if channel_name and channel_user and len(channel_user) <= bid_len and len(channel_extra) <= extra_len:
            binding = Binding()
            binding.user = user
            binding.btype = channel_name
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
            sign = hashlib.md5(str(bid) + offer_type + key).hexdigest()
            params = {
                'userid': bid,
                'offer_type': offer_type,
                'pass': sign,
                'extra': extra,
            }
            jinshan_callback.apply_async(
                kwargs={'url': self.call_back_url, 'params': params})

    # def register_call_back(self, user):
    #     self.jinshan_call_back(user, 'wangli_regist_none', 'ZSEt6lzsK1rigjcOXZhtA6KfbGoS')

    def validate_call_back(self, user):
        self.jinshan_call_back(user, 'wangli_regist_reward', 'Cp9AhO2o9BQTDhbUBnHxmY0X4Kbg')

    def purchase_call_back(self, user, order_id):
        p2p_record = P2PRecord.objects.filter(user_id=user.id, catalog=u'申购').order_by('create_time').first()

        # 判断是否首次投资
        if p2p_record and p2p_record.order_id == int(order_id):
            p2p_amount = int(p2p_record.amount)
            if p2p_amount >= 500:
                if p2p_amount <= 999:
                    self.jinshan_call_back(user, 'wangli_invest_reward', 'pA71ZhBf4DDeet7SLiLlGsT1qTYu')
                elif p2p_amount <= 1999:
                    self.jinshan_call_back(user, 'wangli_invest1000_reward', '4ss7mIRAjsqgOuLp5ezzDVp4Xu5x')
                else:
                    self.jinshan_call_back(user, 'wangli_invest2000_reward', 'uRfzjHGGpxfIZFZN9JbfYLPBGdGC')


class ShanghaiWaihuRegister(CoopRegister):
    def __init__(self, request):
        super(ShanghaiWaihuRegister, self).__init__(request)
        self.c_code = 'shls'

class NanjingWaihuRegister(CoopRegister):
    def __init__(self, request):
        super(NanjingWaihuRegister, self).__init__(request)
        self.c_code = 'njwh'


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

    def clear_session(self):
        super(ShiTouCunRegister, self).clear_session()
        self.request.session.pop(self.extra_key, None)

    def save_to_binding(self, user):
        """
        处理从url获得的渠道参数
        :param user:
        :return:
        """
        channel_user = self.channel_user
        channel_name = self.channel_name
        channel_extra = self.channel_extra
        bid_len = Binding._meta.get_field_by_name('bid')[0].max_length
        extra_len = Binding._meta.get_field_by_name('extra')[0].max_length
        if channel_name and channel_user and len(channel_user) <= bid_len and len(channel_extra) <= extra_len:
            binding = Binding()
            binding.user = user
            binding.btype = channel_name
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
                kwargs={'url': self.call_back_url, 'params': params, 'channel': self.c_code})

    def purchase_call_back(self, user, order_id):
        p2p_record = P2PRecord.objects.filter(user_id=user.id, catalog=u'申购').order_by('create_time').first()

        # 判断是否首次投资
        if p2p_record and p2p_record.order_id == int(order_id):
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

    def purchase_call_back(self, user, order_id):
        """
        投资回调
        :param order_id:
        """
        # Binding.objects.get(user_id=user.id),使用get如果查询不到会抛异常
        binding = Binding.objects.filter(user_id=user.id).first()
        p2p_record_set = P2PRecord.objects.filter(user_id=user.id, catalog=u'申购').order_by('create_time')
        if binding and p2p_record_set.exists():
            # 判断是否首次投资
            if p2p_record_set.first().order_id == order_id:
                p2p_record = p2p_record_set.first()
                goodmark = '1'
                order_act = u'首单'
            else:
                p2p_record = p2p_record_set.last()
                goodmark = '2'
                order_act = u'复投'

            # 如果结算时间过期了则不执行回调
            earliest_settlement_time = redis_backend()._get('%s_%s' % (self.c_code, binding.bid))
            if earliest_settlement_time:
                earliest_settlement_time = datetime.datetime.strptime(earliest_settlement_time, '%Y-%m-%d %H:%M:%S')
                current_time = datetime.datetime.now()
                # 如果上次访问的时间是在30天前则不更新访问时间
                if earliest_settlement_time + datetime.timedelta(days=int(FUBA_PERIOD)) <= current_time:
                    return

            order_id = p2p_record.id
            goodsprice = int(p2p_record.amount)
            # goodsname 提供固定值，固定值自定义，但不能为空
            goodsname = u"名称:网利宝,类型:产品标,周期:1月"
            sig = hashlib.md5(str(order_id)+str(self.coop_key)).hexdigest()
            status = u"%s【%s元：已付款】" % (order_act, goodsprice)
            params = {
                'action': 'create',
                'planid': self.coop_id,
                'order': order_id,
                'goodsmark': goodmark,
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
                    binding.extra = earliest_settlement_time
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

    def purchase_call_back(self, user, order_id):
        # 判断是否是首次投资
        binding = Binding.objects.filter(user_id=user.id).first()
        p2p_record = P2PRecord.objects.filter(user_id=user.id, catalog=u'申购').order_by('create_time').first()

        # 判断是否首次投资
        if binding and p2p_record and p2p_record.order_id == int(order_id):
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
        introduced_by = IntroducedBy.objects.filter(user_id=user.id).first()
        if introduced_by:
            url = self.call_back_url + '?method=AddPlatFormFinanceUser'
            mobile = '******'.join(get_phone_for_coop(user.id).split('***'))
            params = {
                'userId': get_uid_for_coop(user.id),
                'userName': mobile,
                'mobile': mobile,
                'companyId': 9,
                'regTime': introduced_by.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'regSource': 3,
            }
            self.yiche_call_back(url, params)

    def validate_call_back(self, user):
        introduced_by = IntroducedBy.objects.filter(user_id=user.id).first()
        if introduced_by:
            url = self.call_back_url + '?method=UpdatePlatFormFinanceUser'
            username = get_username_for_coop(user.id)
            params = {
                'userId': get_uid_for_coop(user.id),
                'realName': username,
                'companyId': 9,
            }
            self.yiche_call_back(url, params)

    def purchase_call_back(self, user, order_id):
        introduced_by = IntroducedBy.objects.filter(user_id=user.id).first()
        p2p_record = get_last_investment_for_coop(user.id)
        if introduced_by and p2p_record:
            url = self.call_back_url + '?method=AddPlatFormFinanceOrder'
            invest_time = p2p_record.create_time
            params = {
                'userId': get_uid_for_coop(user.id),
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

    def clear_session(self):
        super(ZhiTuiRegister, self).clear_session()
        self.request.session.pop(self.extra_key, None)

    def save_to_binding(self, user):
        """
        处理从url获得的渠道参数
        :param user:
        :return:
        """
        channel_user = self.channel_user
        channel_name = self.channel_name
        channel_extra = self.channel_extra
        bid_len = Binding._meta.get_field_by_name('bid')[0].max_length
        extra_len = Binding._meta.get_field_by_name('extra')[0].max_length
        if channel_name and channel_user and len(channel_user) <= bid_len and len(channel_extra) <= extra_len:
            binding = Binding()
            binding.user = user
            binding.btype = channel_name
            binding.bid = channel_user
            binding.extra = channel_extra
            binding.save()
            # logger.debug('save user %s to binding'%user)

    def purchase_call_back(self, user, order_id):
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

            ua_string = self.request.META.get('HTTP_USER_AGENT', '')
            user_agent = parse(ua_string)
            if user_agent.is_mobile:
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
                'o_date': timezone.localtime(invest_time).strftime('%Y%m%d%H%M%S'),
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
        self.coop_key = ZGDX_KEY
        self.iv = ZGDX_IV

    @property
    def channel_user(self):
        return self.request.session.get(self.internal_channel_user_key, '00000')

    def zgdx_call_back(self, user, plat_offer_id, order_id=None):
        if datetime.datetime.now().day >= 28:
            effect_type = '1'
        else:
            effect_type = '0'

        request_no_prefix = order_id or str(user.id) + timezone.now().strftime("%Y%m%d%H%M%S")
        request_no = str(request_no_prefix) + '_' + plat_offer_id
        phone_id = WanglibaoUserProfile.objects.get(user_id=user.id).phone
        code = {
            'request_no': request_no,
            'phone_id': phone_id,
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
        order = UserThreeOrder(user=user, order_on=channel_recode, request_no=request_no)
        order.save()

        # 异步回调
        zgdx_callback.apply_async(
            kwargs={'url': self.call_back_url, 'params': params, 'channel': self.c_code})

    def binding_card_call_back(self, user):
        logger.info("ZGDX-Enter recharge_call_back for zgdx: [%s]" % user.id)
        binding = Binding.objects.filter(user_id=user.id).first()
        # 判定是否首次绑卡
        if binding and binding.extra != '1':
            if ENV == ENV_PRODUCTION:
                plat_offer_id = '104369'
            else:
                plat_offer_id = '103050'
            self.zgdx_call_back(user, plat_offer_id)
            binding.extra = '1'
            binding.save()

    def purchase_call_back(self, user, order_id):
        logger.info("ZGDX-Enter purchase_call_back for zgdx: user[%s], order[%s]" % (user.id, order_id))
        # 判断是否是首次投资
        binding = Binding.objects.filter(user_id=user.id).first()
        p2p_record = P2PRecord.objects.filter(user_id=user.id, catalog=u'申购').order_by('create_time').first()

        # 判断是否首次投资
        if binding and p2p_record and p2p_record.order_id == int(order_id):
            p2p_amount = int(p2p_record.amount)
            if p2p_amount >= 1000:
                if ENV == ENV_PRODUCTION:
                    if 1000 <= p2p_amount < 2000:
                        plat_offer_id = '104371'
                    else:
                        plat_offer_id = '104372'
                else:
                    plat_offer_id = '103050'
                self.zgdx_call_back(user, plat_offer_id, order_id)


class RockFinanceRegister(CoopRegister):
    def __init__(self, request):
        super(RockFinanceRegister, self).__init__(request)
        self.c_code = 'dmw'
        self.invite_code = 'dmw'

    def purchase_call_back(self, user, order_id):
        key = 'activities'
        activity_config = Misc.objects.filter(key=key).first()
        if activity_config:
            activity = json.loads(activity_config.value)
            if type(activity) == dict:
                try:
                    rock_finance = activity['rock_finance']
                    is_open = rock_finance["is_open"]
                    amount = rock_finance["amount"]
                    p2p_amount = rock_finance["p2p_amount"]
                    start_time = rock_finance["start_time"]
                    end_time = rock_finance["end_time"]
                except KeyError, reason:
                    logger.debug(u"misc中activities配置错误，请检查,reason:%s" % reason)
                    raise Exception(u"misc中activities配置错误，请检查，reason:%s" % reason)
            else:
                raise Exception(u"misc中activities的配置参数，应是字典类型")
        else:
            raise Exception(u"misc中没有配置activities杂项")

        logger.debug(u"user:%s, order_id:%s, 运行开关:%s, 开放时间:%s, 结束时间:%s, 总票数:%s" % (user, order_id, is_open, start_time, end_time, amount))

        p2p_record = P2PRecord.objects.filter(user_id=user.id, catalog=u'申购').order_by('create_time').first()

        if p2p_record and p2p_record.order_id == int(order_id):
            # 1: 如果活动没有打开
            if is_open == "false":
                logger.debug(u'开关没打开')
                return

            # 2: 如果票数到800了，直接跳出
            counts = ActivityReward.objects.filter(activity='rock_finance').count()
            if counts >= amount:
                logger.debug(u'票已经发完了, %s' % (counts))
                return

            # 3 :如果时间已经过了, 直接跳出; 如果活动时间还没有开始，也直接跳出
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            if now < start_time or now > end_time:
                logger.debug("start_time:%s, end_time:%s, now:%s" % (start_time, end_time, now))
                return

            # 4: 如果投资额度不够，直接跳出
            if p2p_record.amount < p2p_amount:
                logger.debug(u"p2p_record.amount:%s, p2p_amount:%s" % (p2p_record.amount, p2p_amount))
                return

            reward = Reward.objects.filter(type='金融摇滚夜', is_used=False).first()
            if not reward:
                logger.debug(u"奖品没有了")
                return

            with transaction.atomic():
                reward = Reward.objects.select_for_update().filter(content=reward.content).first()
                try:
                    activity_reward = ActivityReward.objects.create(
                        activity='rock_finance',
                        order_id=order_id,
                        user=user,
                        p2p_amount=p2p_record.amount,
                        reward=reward,
                        has_sent=False, #当被扫码后， has_sent变成true
                        left_times=1,
                        join_times=1,
                    )
                except Exception, reason:
                    logger.debug(u"生成获奖记录报异常, reason:%s" % reason)
                    raise Exception(u"生成获奖记录异常")
                else:
                    #不知道为什么create的时候，会报错
                    m = Misc.objects.filter(key='weixin_qrcode_info').first()
                    original_id = None
                    if m and m.value:
                        info = json.loads(m.value)
                        original_id = info.get('fwh')
                        account = WeixinAccounts.getByOriginalId(original_id)
                    encoding_str = urllib.quote("https://www.wanglibao.com/api/check/qrcode/?owner_id=%s&activity=rock_finance&content=%s" % (user.id, reward.content))
                    qrcode_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_base&state=%s" % (account.app_id, encoding_str, original_id)
                    logger.debug("encoding_st:%s, qrcode_url:%s" % (encoding_str, qrcode_url))
                    img = qrcode.make(qrcode_url)
                    _img = img.tobytes()
                    img_handle = cStringIO.StringIO()
                    img.save(img_handle)
                    img_handle.seek(0)
                    _img = FileObject(img_handle, len(_img))
                    activity_reward.qrcode.save("rock_finance.png", _img, save=True)
                    activity_reward.save()
                    logger.debug("before save: activity_reward.qrcode:%s" % activity_reward.qrcode)
                    #将奖品通过站内信发出
                    inside_message.send_one.apply_async(kwargs={
                        "user_id": user.id,
                        "title": u"网利宝摇滚之夜门票",
                        "content": u"网利宝摇滚夜欢迎您的到来，点击<a href='https://www.wanglibao.com/rock/finance/qrcode/?user_id=%s'>获得入场二维码</a>查看，<br/> 感谢您对我们的支持与关注。<br/>网利宝" % user.id,
                        "mtype": "activity"
                    })
                    reward.is_used = True
                    reward.save()
                    logger.debug("after save:activity_reward.qrcode:%s" % activity_reward.qrcode)

                    logger.debug(u"user:%s, 站内信已经发出, 奖品内容:%s" % (user, reward.content))

class JuChengRegister(CoopRegister):
    def __init__(self, request):
        super(JuChengRegister, self).__init__(request)
        self.c_code = 'jcw'
        self.invite_code = 'jcw'

    @method_decorator(transaction.atomic)
    def purchase_call_back(self, user, order_id):
        p2p_record = P2PRecord.objects.filter(user_id=user.id, catalog=u'申购').order_by('create_time').first()
        SEND_SUCCESS = None
        ticket = 0

        # 判断是否首次投资
        if p2p_record and p2p_record.order_id == int(order_id):
            p2p_amount = int(p2p_record.amount)
            if p2p_amount>=500 and p2p_amount<1000 and False:
                try:
                    logger.debug(u"80门票，我要申请锁")
                    config = GiftOwnerGlobalInfo.objects.select_for_update().filter(description=u'jcw_ticket_80').first()
                except Exception, reason:
                    logger.debug(u"获取奖品信息全局配置表报异常,reason:%s" % (reason,))
                    raise
                if config and config.amount > 0:
                    logger.debug(u'80门票，我已经得到了锁')
                    logger.debug(u'80 ticket left：%s' % (config.amount,))
                    config.amount -= 1
                    ticket = 80
                    config.save()
                    logger.debug(u"用户 %s 获得80门票一张, 剩余：%s" % (user, config.amount))
                    SEND_SUCCESS = True

            if p2p_amount>=2000:
                try:
                    logger.debug(u"180门票，我要申请锁")
                    config = GiftOwnerGlobalInfo.objects.select_for_update().filter(description=u'jcw_ticket_188').first()
                except Exception, reason:
                    logger.debug(u"获取奖品信息全局配置表报异常,reason:%s" % (reason,))
                    raise
                if config and config.amount > 0:
                        logger.debug(u'180门票，我已经得到了锁')
                        config.amount -= 1
                        logger.debug(u"用户 %s 获得180门票一张, 剩余：%s" % (user, config.amount))
                        config.save()
                        ticket = 180
                        SEND_SUCCESS = True

            if SEND_SUCCESS:
                send_messages.apply_async(kwargs={
                    "phones": [user.wanglibaouserprofile.phone, ],
                    "messages": [u'【网利科技】您已成功获得%s元门票，请于演出当天到北京音乐厅一楼大厅票务兑换处领取，咨询电话:13581710219' % (ticket,), ]
                })
                inside_message.send_one.apply_async(kwargs={
                    "user_id": user.id,
                    "title": u"演出门票赠送",
                    "content": u'【网利科技】您已成功获得%s元门票，请于演出当天到北京音乐厅一楼大厅票务兑换处领取，咨询电话:13581710219' % (ticket,),
                    "mtype": "activity"
                })


class WeixinRedpackRegister(CoopRegister):
    def __init__(self, request):
        super(WeixinRedpackRegister, self).__init__(request)
        self.c_code = 'wrp'
        self.invite_code = 'wrp'
        self.order_id = request.POST.get("order_id", None)

    def register_call_back(self, user):
        phone = user.wanglibaouserprofile.phone
        logger.debug('通过weixin_redpack渠道注册,phone:%s' % (phone,))
        try:
            ex_event = ExperienceEvent.objects.filter(name=u'新手体验金', invalid=False).first()
            ActivityReward.objects.create(
                order_id=self.order_id,
                activity='weixin_experience_glod',
                experience=ex_event,
                user_id=user.id,
            )
        except Exception, reason:
            logger.debug("微信分享，生成体验金报异常; reason:%s" % (reason,))
        else:
            pass


class XunleiVipRegister(CoopRegister):
    def __init__(self, request):
        super(XunleiVipRegister, self).__init__(request)
        self.c_code = 'xunlei9'
        self.call_back_url = XUNLEIVIP_CALL_BACK_URL
        self.register_call_back_url = XUNLEIVIP_REGISTER_CALL_BACK_URL
        self.coop_key = XUNLEIVIP_KEY
        self.coop_register_key = XUNLEIVIP_REGISTER_KEY
        self.external_channel_user_key = 'xluserid'
        self.coop_time_key = 'time'
        self.coop_sign_key = 'sign'

    @property
    def channel_user(self):
        return self.request.session.get(self.internal_channel_user_key, '').strip()

    @property
    def channel_time(self):
        return self.request.session.get(self.coop_time_key, '').strip()

    @property
    def channel_sign(self):
        return self.request.session.get(self.coop_sign_key, '').strip()

    @property
    def is_xunlei_user(self):
        # 校验迅雷用户有效性
        data = {
            self.coop_time_key: self.channel_time,
            self.external_channel_user_key: self.channel_user,
        }

        if xunleivip_generate_sign(data, self.coop_register_key) == self.channel_sign:
            return True
        else:
            return False

    def save_to_session(self):
        super(XunleiVipRegister, self).save_to_session()
        coop_time = self.request.GET.get(self.coop_time_key, None)
        coop_sign = self.request.GET.get(self.coop_sign_key, None)
        if coop_time:
            self.request.session[self.coop_time_key] = coop_time

        if coop_sign:
            self.request.session[self.coop_sign_key] = coop_sign

    def clear_session(self):
        super(XunleiVipRegister, self).clear_session()
        self.request.session.pop(self.coop_time_key, None)
        self.request.session.pop(self.coop_sign_key, None)

    def save_to_binding(self, user):
        """
        处理从url获得的渠道参数
        :param user:
        :return:
        """

        channel_name = self.channel_name
        if self.is_xunlei_user:
            channel_user = self.channel_user
            bid_len = Binding._meta.get_field_by_name('bid')[0].max_length
            if channel_name and channel_user and len(channel_user) <= bid_len:
                binding = Binding()
                binding.user = user
                binding.btype = channel_name
                binding.bid = channel_user
                binding.save()
                # logger.debug('save user %s to binding'%user)
                return True

            logger.info("%s binding faild with user[%s], channel_user[%s]" %
                        (channel_name, user.id, channel_user))
        else:
            logger.info("%s binding faild with user[%s] not xunlei user, xluserid[%s] timestamp[%s] sgin[%s]" %
                        (channel_name, user.id, self.channel_user, self.channel_time, self.channel_sign))

    def binding_for_after_register(self, user):
        """
        用户可以在从渠道跳转后的注册页使用邀请码，优先考虑邀请码
        """
        # 处理渠道用户绑定状态
        channel = get_user_channel_record(user.id)
        if self.is_xunlei_user and channel and channel.code == self.c_code:
            binding = Binding.objects.filter(user_id=user.id).first()
            if not binding and self.save_to_binding(user):
                # 处理渠道用户注册回调
                self.register_call_back(user)

                # 处理渠道用户充值回调补发
                penny = Decimal(0.01).quantize(Decimal('.01'))
                pay_info = PayInfo.objects.filter(user=user, type='D', amount__gt=penny,
                                                  status=PayInfo.SUCCESS).order_by('create_time').first()
                if pay_info and int(pay_info.amount) >= 100:
                    self.recharge_call_back(user, pay_info.order_id)

                # 处理渠道用户投资回调补发
                p2p_record = P2PRecord.objects.filter(user_id=user.id, catalog=u'申购').order_by('create_time').first()
                if p2p_record and int(p2p_record.amount) >= 1000:
                    self.purchase_call_back(user, p2p_record.order_id)

        self.clear_session()

    def xunlei_call_back(self, user, tid, data, url, order_id):
        order_id = '%s_%s' % (order_id, data['act'])
        data['uid'] = tid
        data['orderid'] = order_id
        data['type'] = 'baijin'
        sign = xunleivip_generate_sign(data, self.coop_key)
        params = dict({'sign': sign}, **data)

        # 创建渠道订单记录
        channel_recode = get_user_channel_record(user.id)
        order = UserThreeOrder(user=user, order_on=channel_recode, request_no=order_id)
        order.save()

        # 异步回调
        xunleivip_callback.apply_async(
            kwargs={'url': url, 'params': params,
                    'channel': self.c_code, 'order_id': order_id})

    def register_call_back(self, user):
        # 判断用户是否绑定
        binding = Binding.objects.filter(user_id=user.id).first()
        if binding:
            data = {
                'coop': 'wanglibao',
                'xluserid': binding.bid,
                'regtime': int(time.mktime(user.date_joined.date().timetuple()))
            }

            sign = xunleivip_generate_sign(data, self.coop_register_key)
            params = dict({'sign': sign}, **data)

            # 异步回调
            common_callback.apply_async(
                kwargs={'url': self.register_call_back_url, 'params': params, 'channel': self.c_code})

    def recharge_call_back(self, user, order_id):
        logger.info("XunleiVip-Enter recharge_call_back for user[%s], order_id[%s]" % (user.id, order_id))
        # 判断用户是否首次充值
        penny = Decimal(0.01).quantize(Decimal('.01'))
        pay_info = PayInfo.objects.filter(user=user, type='D', amount__gt=penny,
                                          status=PayInfo.SUCCESS).order_by('create_time').first()

        if pay_info and pay_info.order_id == int(order_id):
            logger.info("XunleiVip-If amount for xunlei9: [%s], [%s]" % (order_id, pay_info.amount))
            # 判断充值金额是否大于100
            pay_amount = int(pay_info.amount)
            if pay_amount >= 100:
                # 判断用户是否绑定
                binding = Binding.objects.filter(user_id=user.id).first()
                if binding:
                    data = {
                        'sendtype': '1',
                        'num1': 7,
                        'act': 5171
                    }
                    self.xunlei_call_back(user, binding.bid, data,
                                          self.call_back_url, pay_info.order_id)
                else:
                    message_content = sms_alert_unbanding_xunlei(u"7天白金会员", XUNLEIVIP_LOGIN_URL)
                    inside_message.send_one.apply_async(kwargs={
                        "user_id": user.id,
                        "title": u"首次充值送7天迅雷白金会员",
                        "content": message_content,
                        "mtype": "activity"
                    })

    def purchase_call_back(self, user, order_id):
        logger.info("XunleiVip-Enter purchase_call_back for xunlei9: [%s], [%s]" % (user.id, order_id))
        # 判断是否首次投资
        p2p_record = P2PRecord.objects.filter(user_id=user.id, catalog=u'申购').order_by('create_time').first()
        if p2p_record and p2p_record.order_id == int(order_id):
            # 判断投资金额是否大于100
            pay_amount = int(p2p_record.amount)
            if pay_amount >= 1000:
                # 判断用户是否绑定
                binding = Binding.objects.filter(user_id=user.id).first()
                if binding:
                    data = {
                        'sendtype': '0',
                        'num1': 12,
                        'act': 5170
                    }
                    self.xunlei_call_back(user, binding.bid, data,
                                          self.call_back_url, p2p_record.order_id)
                else:
                    message_content = sms_alert_unbanding_xunlei(u"1年白金会员", XUNLEIVIP_LOGIN_URL)
                    inside_message.send_one.apply_async(kwargs={
                        "user_id": user.id,
                        "title": u"首次投资送1年迅雷白金会员",
                        "content": message_content,
                        "mtype": "activity"
                    })


class XunleiMobileRegister(XunleiVipRegister):
    def __init__(self, request):
        super(XunleiMobileRegister, self).__init__(request)
        self.c_code = 'mxunlei'


class MaimaiRegister(CoopRegister):
    def __init__(self, request):
        super(MaimaiRegister, self).__init__(request)
        self.c_code = MAIMAI1_CHANNEL_CODE
        self.call_back_url = MAIMAI_CALL_BACK_URL
        self.extra_key = 'mmtoken'

    def save_to_session(self):
        super(MaimaiRegister, self).save_to_session()
        channel_extra = self.request.GET.get(self.extra_key, None)
        if channel_extra:
            self.request.session[self.extra_key] = channel_extra
            # logger.debug('save to session %s:%s'%(self.extra_key, channel_extra))

    def clear_session(self):
        super(MaimaiRegister, self).clear_session()
        self.request.session.pop(self.extra_key, None)

    def register_call_back(self, user):
        introduced_by = IntroducedBy.objects.filter(user_id=user.id).first()
        mm_token = self.channel_extra
        if introduced_by:
            params = {'mmtoken': mm_token}
            # 异步回调
            common_callback.apply_async(
                kwargs={'url': self.call_back_url, 'params': params, 'channel': self.c_code})


class YZCJRegister(CoopRegister):
    def __init__(self, request):
        super(YZCJRegister, self).__init__(request)
        self.c_code = 'yzcj'
        self.coop_key = YZCJ_COOP_KEY
        self.call_back_url = YZCJ_CALL_BACK_URL

    def purchase_call_back(self, user, order_id):
        binding = Binding.objects.filter(user_id=user.id).first()
        p2p_record = P2PRecord.objects.filter(user_id=user.id, catalog=u'申购'
                                              ).select_related('product').order_by('create_time').first()

        # 判断是否已绑定并且首次投资
        if binding and p2p_record and p2p_record.order_id == int(order_id):
            # 判断投资金额是否大于1000
            pay_amount = int(p2p_record.amount)
            if pay_amount >= 1000:
                invest_time = p2p_record.create_time
                period = p2p_record.product.period
                pay_method = p2p_record.product.pay_method

                # 根据支付方式判定标周期的单位（天/月）,如果是单位为月则转换为天
                if pay_method in [u'等额本息', u'按月付息', u'到期还本付息']:
                    period = (invest_time + relativedelta(months=period) - invest_time).days

                sign = hashlib.md5(str(p2p_record.order_id) + str(binding.bid) +
                                   str(period) + str(pay_amount) + self.coop_key).hexdigest()

                params = {
                    'oid': p2p_record.order_id,
                    'tid': binding.bid,
                    'time': timezone.localtime(invest_time).strftime('%Y%m%d%H%M%S'),
                    'procuctId': p2p_record.product_id,
                    'interval': period,
                    'investment': pay_amount,
                    'phone': get_phone_for_coop(user.id),
                    'IdNum': '',
                    'sign': sign,
                }

                # 异步回调
                common_callback.apply_async(
                    kwargs={'url': self.call_back_url, 'params': params, 'channel': self.c_code})


# 注册第三方通道
coop_processor_classes = [TianMangRegister, YiRuiTeRegister, BengbengRegister,
                          JuxiangyouRegister, DouwanRegister, JinShanRegister,
                          ShiTouCunRegister, FUBARegister, YunDuanRegister,
                          YiCheRegister, ZhiTuiRegister, ShanghaiWaihuRegister,
                          ZGDXRegister, NanjingWaihuRegister, WeixinRedpackRegister,
                          XunleiVipRegister, JuChengRegister, MaimaiRegister,
                          YZCJRegister, RockFinanceRegister,]

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


class CoopInvestmentQuery(APIView):
    permission_classes = ()
    channel = None

    # 每一页用户数
    PAGE_LENGTH = 20

    def get_phone_for_coop(self, user_id):
        try:
            phone_number = WanglibaoUserProfile.objects.get(user_id=user_id).phone
            return phone_number
        except:
            return None

    def get_promo_user(self, channel_code, p2p_record):
        """
        :param channel_code: like "tianmang"
        :param startday: 日期格式20050606
        :param endday:
        :return:
        """

        promo_list = IntroducedBy.objects.filter(channel__code=channel_code)
        p2p_count_for_user = p2p_record.values('user').annotate(Count('user'))
        p2p_user_list = [p_info['user'] for p_info in p2p_count_for_user]

        promo_list = [p.user_id for p in promo_list if p.user_id in p2p_user_list]

        # logger.debug("promo user:%s"%[promo_user.user for promo_user in promo_list])
        return promo_list

    def check_sign(self, channel_code, p_id, sign):
        m = hashlib.md5()
        # key = getattr(settings, 'WLB_FOR_%s_KEY' % channel_code.upper())
        key = getattr(settings, 'WLB_FOR_FANLITOU_KEY')
        m.update(str(p_id)+key)
        local_sign = m.hexdigest()
        if sign != local_sign:
            # logger.debug('正确的渠道校验参数%s'%local_sign)
            logger.error(u"渠道查询接口，sign参数校验失败")
            return False
        return True

    def get_user_info_for_coop(self, user_id, p2p_record):
        user_info = {
            'uid': get_uid_for_coop(user_id),
            'uname': get_username_for_coop(user_id),
            'phone': self.get_phone_for_coop(user_id),
            'tid': get_tid_for_coop(user_id),
        }

        user_info_set = []
        p2p_record_set = p2p_record.filter(user_id=user_id)
        for _p2p_record in p2p_record_set:
            user_p2p_info = {
                'investment': _p2p_record.amount,
                'time': _p2p_record.create_time,
                'pid': _p2p_record.product_id
            }

            if user_p2p_info['time']:
                user_p2p_info['time'] = timezone.localtime(user_p2p_info['time']).strftime('%Y-%m-%d %H:%M:%S')

            user_info_set.append(dict(user_info, **user_p2p_info))

        return user_info_set

    def get_all_user_info_for_coop(self, channel_code, p_id, sign, page):
        if not self.check_sign(channel_code, p_id, sign):
            raise ValueError('wrong signature.')

        p2p_record = P2PRecord.objects.filter(product_id=p_id, catalog=u'申购').order_by('user' ,'create_time')

        coop_users = self.get_promo_user(channel_code, p2p_record)

        user_info = []
        for user_id in coop_users:
            try:
                user_info += self.get_user_info_for_coop(user_id, p2p_record)
            except Exception, e:
                logger.exception(e)
                logging.debug('get user %s error:%s' % (user_id, e))

        # 处理分页
        if page:
            page = int(page)
            start = page * self.PAGE_LENGTH
            end = start + self.PAGE_LENGTH
            user_info = user_info[start:end]

        return user_info

    def get(self, request, channel_code, p_id, sign, page=None):
        try:
            result = {
                'errorcode': 0,
                'errormsg': 'sucess',
                'info': self.get_all_user_info_for_coop(channel_code, p_id, sign, page)
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
                   Decimal(product_id_or_instance.expected_earning_rate)
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
            if not end_date:
                end_date = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()+8*60*60))
            channel = Channels.objects.get(name='xicai')
            channels = IntroducedBy.objects.filter(
                Q(channel=channel) & Q(created_at__gte=start_date) & Q(created_at__lte=end_date))

            users = [c.user for c in channels]
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
                # user_profile = WanglibaoUserProfile.objects.get(user=user)
                user_profile = user.wanglibaouserprofile
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

    url = settings.CAIMIAO_Volumes_URL
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

    url = settings.CAIMIAO_RATING_URL
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
            products = P2PProduct.objects.filter(status=u'正在招标')

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
                    base_url = ''
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

                    # 现在是招标前不往对方推送. 0状态不会被匹配.
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
        prod['wangli_id'] = product.pk
        if product in new_products:

            # 以下针对开发测试环境的手动数据处理对应id.
            redis = redis_backend()
            if not redis._get('wangli_id_'+str(product.pk)):
                prod['method'] = 'add'
            else:
                if product.status == u'正在招标':
                    prod['method'] = 'update'
                else:
                    prod['method'] = 'down'
        else:
            if product.status == u'正在招标':
                prod['method'] = 'update'
            else:
                prod['method'] = 'down'

        prod['classId'] = 1

        # 从redis 读对应他们的id
        if not prod['method'] == 'add':
            try:
                redis = redis_backend()
                prod['productId'] = int(redis._get('wangli_id_'+str(product.pk)))
            except Exception, e:
                print e
                prod['productId'] = -1

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
        base_url = ''
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
        ret = eval(urllib2.urlopen(url).read())

        # 把中金的产品 id 存到redis
        if ret['flag'] == '1000':
            zhongjin_pid = ret['msg']
            wangli_id = args_dict['wangli_id']
            redis = redis_backend()
            if not redis._get('wangli_id_'+str(wangli_id)):
                redis._set('wangli_id_'+str(wangli_id), zhongjin_pid)
                redis.redis.expire('wangli_id_'+str(wangli_id), 24*60*60*7)


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


# 金融加渠道
# 自动注册登录在 wanglibao_account/views.py JrjiaAutoRegisterView
class JrjiaCPSView(APIView):
    """
    接口示例：http://api.xxx.com/cps?src=jsrjia&time=14233469890
    """

    permission_classes = ()

    def get(self, request):
        """
        """
        source = self.request.GET.get('src', None)
        start = self.request.GET.get('time', None)
        ret = dict()
        data = []

        if source == 'jrjia' and int(start) > 0:
            timeArray = time.localtime(int(start))
            check_time = timezone.datetime(year=timeArray.tm_year,
                                           month=timeArray.tm_mon,
                                           day=timeArray.tm_mday,
                                           hour=timeArray.tm_hour,
                                           minute=timeArray.tm_min,
                                           second=timeArray.tm_sec).replace(tzinfo=pytz.UTC)
            jrjia_bindings = Binding.objects.filter(btype='jrjia')
            jrjia_users = [binding.user for binding in jrjia_bindings]
            equities = P2PEquity.objects.filter(user__in=jrjia_users, created_at__gte=check_time)

            for equity in equities:
                data_dic = dict()
                data_dic['reqId'] = Binding.objects.get(user=equity.user).bid
                data_dic['prodIdAct'] = str(equity.product.pk)
                data_dic['purchaseTime'] = int(time.mktime(equity.created_at.timetuple()))
                data_dic['investAmount'] = equity.equity
                data_dic['investDuration'] = equity.product.period
                data_dic['investDurationUnit'] = 1 if equity.product.pay_method.startswith(u"日计息") else 2
                data_dic['returnRate'] = equity.product.expected_earning_rate
                try:
                    data_dic['startDate'] = int(time.mktime(equity.product.make_loans_time.timetuple()))
                except Exception, e:
                    print 'get startDate error: {}'.format(e)
                    data_dic['startDate'] = ''

                data.append(data_dic)

            ret['data'] = data
            ret['result'] = 'ok'
            ret['errMsg'] = None
            return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))

        else:
            ret['result'] = 'error'
            ret['errMsg'] = u'参数错误'
            ret['data'] = data

            return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class JrjiaP2PStatusView(APIView):
    """
    author: Zhoudong
    http请求方式: GET  P2P标的的售卖进度
    http://api.xxx.com/pstatus?src=jrjia&prodId=123
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):

        source = self.request.GET.get('src', None)
        pid = self.request.GET.get('prodId', None)
        ret = dict()

        if source == u'jrjia' and int(pid) > 0:
            try:
                product = P2PProduct.objects.get(pk=pid)
            except Exception, e:
                ret['result'] = 'err'
                ret['errMsg'] = u'未找到该标： {}'.format(e)
                return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))

            if product:
                ret['result'] = 'ok'
                ret['errMsg'] = None
                data = dict()

                data['prodId'] = str(product.pk)
                data['totalAmount'] = product.total_amount
                data['soldAmount'] = product.ordered_amount
                data['userCount'] = len(product.equities.all().values('user').annotate(Count('user')))

                ret['data'] = data
        elif int(pid) <= 0:
            ret = {
                'result': 'err',
                'errMsg': u"标id错误"
            }
        else:
            ret = {
                'result': 'err',
                'errMsg': u"没有权限访问"
            }
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class JrjiaP2PInvestView(APIView):
    """
    author: Zhoudong
    http请求方式: GET  P2P标的的售卖进度
    http://api.xxx.com/pinvest?src=jrjia&prodId=123&time=1423469890
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):
        ret = dict()

        source = self.request.GET.get('src', None)
        pid = self.request.GET.get('prodId', None)
        start = self.request.GET.get('time', None)

        if source == u'jrjia' and int(pid) > 0 and int(start) > 0:
            timeArray = time.localtime(int(start))
            check_time = timezone.datetime(year=timeArray.tm_year,
                                           month=timeArray.tm_mon,
                                           day=timeArray.tm_mday,
                                           hour=timeArray.tm_hour,
                                           minute=timeArray.tm_min,
                                           second=timeArray.tm_sec).replace(tzinfo=pytz.UTC)
            try:
                data = []
                jrjia_bindings = Binding.objects.filter(btype='jrjia')
                jrjia_users = [binding.user for binding in jrjia_bindings]
                product = P2PProduct.objects.get(pk=pid)
                equities = P2PEquity.objects.filter(created_at__gte=check_time, user__in=jrjia_users)
                for equity in equities:
                    dic = dict()
                    dic['prodId'] = str(product.id)
                    dic['username'] = equity.user.wanglibaouserprofile.name
                    dic['investTime'] = (equity.created_at - datetime.datetime(1970, 1, 1).
                                         replace(tzinfo=timezone.utc)).total_seconds()
                    dic['investAmount'] = equity.equity
                    dic['reqId'] = Binding.objects.get(user=equity.user).bid
                    data.append(dic)

                ret['data'] = data
                ret['result'] = 'ok'
                ret['errMsg'] = None

            except Exception, e:
                ret['result'] = 'err'
                ret['errMsg'] = u'未找到该标： {}'.format(e)
                return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))

        elif int(pid) <= 0:
            ret = {
                'result': 'err',
                'errMsg': u"标id错误"
            }
        else:
            ret = {
                'result': 'err',
                'errMsg': u"没有权限访问"
            }
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class JrjiaReportView(APIView):
    """
    author: Zhoudong
    http请求方式: GET  该接口返回指定日期的数据日报，包括成交金额、成交笔数、参与人数和年化收益率等指标
    http://api.xxx.com/report?src=jrjia&date=20150825
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):
        ret = dict()

        source = self.request.GET.get('src', None)
        time_str = self.request.GET.get('date', None)

        if source == u'jrjia':
            try:
                data = dict()
                start_date = datetime.datetime.strptime(time_str, "%Y%m%d")

                time_zone = settings.TIME_ZONE
                local = pytz.timezone(time_zone)
                local_dt = local.localize(start_date, is_dst=None)
                start = local_dt.astimezone(pytz.utc)

                equities = P2PEquity.objects.filter(created_at__gt=start,
                                                    created_at__lte=(start + timezone.timedelta(days=1)))

                data['statDate'] = start_date.strftime("%Y-%m-%d")
                data['investAmount'] = equities.aggregate(Sum('equity'))['equity__sum']
                data['investCount'] = equities.count()
                data['investUser'] = equities.values_list('user', flat=True).distinct().count()
                products = P2PProduct.objects.filter(publish_time__gt=start,
                                                     publish_time__lte=(start + timezone.timedelta(days=1)))
                data['returnRate'] = round(products.aggregate(Sum('expected_earning_rate'))
                                           ['expected_earning_rate__sum'] / products.count(), 2)

                ret['data'] = data
                ret['result'] = 'ok'
                ret['errMsg'] = None

            except Exception, e:
                ret['result'] = 'err'
                ret['errMsg'] = u'数据错误： {}'.format(e)
                return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))

        else:
            ret = {
                'result': 'err',
                'errMsg': u"没有权限访问"
            }
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class JrjiaUsStatusView(APIView):
    """
    http请求方式: GET  返回指定时间以后的所有从”金融加”带来的用户的最终状态（状态包括：注册、实名认证、绑卡、充值）
                        按照注册、实名认证、绑卡、充值的顺序
    http://api.xxx.com/ustatus?src=jrjia&time=14233469890
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):
        ret = dict()

        source = self.request.GET.get('src', None)
        start = self.request.GET.get('time', None)

        if source == u'jrjia' and int(start) > 0:
            try:
                data = []

                # bindings = Binding.objects.filter(btype='jrjia', created_at__gt=int(start))
                bindings = Binding.objects.all()
                jrjia_users = set([b.user for b in bindings])

                # equities = P2PEquity.objects.filter(user__in=jrjia_users, equity__gt=100)
                deposits = PayInfo.objects.filter(user__in=jrjia_users, type=u'D')
                cards = Card.objects.filter(user__in=jrjia_users)
                identifies = WanglibaoUserProfile.objects.filter(user__in=jrjia_users, id_is_valid=True)

                # invested_users = set([equity.user for equity in equities])
                deposited_users = set([deposit.user for deposit in deposits])
                binding_users = set([card.user for card in cards])
                identify_users = set([identify.user for identify in identifies])

                for user in jrjia_users:
                    dic = dict()
                    dic['reqId'] = Binding.objects.get(user=user).bid
                    if user in deposited_users:
                        status = 4
                        action_datetime = PayInfo.objects.filter(user=user).first().create_time
                    elif user in binding_users:
                        status = 3
                        action_datetime = Card.objects.filter(user=user).last().add_at
                    elif user in identify_users:
                        status = 2
                        action_datetime = WanglibaoUserProfile.objects.get(user=user).id_valid_time

                    else:
                        status = 1
                        action_datetime = user.date_joined

                    action_time = (action_datetime - datetime.datetime(1970, 1, 1).
                                   replace(tzinfo=timezone.utc)).total_seconds()

                    dic['userStatus '] = status
                    dic['actionTime'] = action_time
                    dic['payAmount'] = Binding.objects.get(user=user).bid
                    try:
                        dic['userAccount'] = user.wanglibaouserprofile.phone
                    except Exception, e:
                        print 'user {} profile error: {}'.format(user.id, e)

                    data.append(dic)

                ret['data'] = data
                ret['result'] = 'ok'
                ret['errMsg'] = None

            except Exception, e:
                ret['result'] = 'err'
                ret['errMsg'] = u'数据错误： {}'.format(e)
                return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))

        else:
            ret = {
                'result': 'err',
                'errMsg': u"没有权限访问"
            }
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class ZOP2PListView(APIView):
    """
    """
    permission_classes = ()

    def check_sign(self):
        visit_key = str(self.request.GET.get('visit_key', None))
        sign = str(self.request.GET.get('sign', None))

        if visit_key and sign:
            full_path = self.request.get_full_path()
            full_path = urllib.unquote(full_path)
            # TODO 进行校验
            from hashlib import md5
            check_sign = md5(settings.ZO_SECRET + '&' + full_path.split('?')[1].split('&sign')[0]).hexdigest()
            if sign == check_sign.upper():
                return True

    def get(self, request):

        if self.check_sign():
            try:
                status = int(self.request.GET.get('status', None))
                time_from = self.request.GET.get('time_from', None)
                time_to = self.request.GET.get('time_to', None).strip()
                page_size = int(self.request.GET.get('page_size', 100))
                page_index = int(self.request.GET.get('page_index', 1))

                p2p_list = []
                ret = dict()

                # page = page_index

                p2p_status = []
                if status == 0:
                    p2p_status = [u'正在招标']
                if status == 1:
                    p2p_status = [u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'已完成']
                if status == 2:
                    p2p_status = [u'流标']

                time_zone = settings.TIME_ZONE
                local = pytz.timezone(time_zone)
                time_from2 = datetime.datetime.strptime(time_from, "%Y-%m-%d %H:%M:%S")
                time_to2 = datetime.datetime.strptime(time_to, "%Y-%m-%d %H:%M:%S")
                time_from3 = local.localize(time_from2, is_dst=None)
                time_to3 = local.localize(time_to2, is_dst=None)
                time_from4 = time_from3.astimezone(pytz.utc)
                time_to4 = time_to3.astimezone(pytz.utc)
                p2ps = P2PProduct.objects.filter(status__in=p2p_status,
                                                 publish_time__gt=time_from4,
                                                 publish_time__lte=time_to4)

                ret['total'] = p2ps.count()

                # 获取总页数, 和页数不对处理
                com_page = len(p2ps) / page_size + 1

                if page_index > com_page:
                    page = com_page
                elif page_index < 1:
                    page = 1
                else:
                    page = page_index

                # 获取到对应的页数的所有用户
                if p2ps.count() / page_size >= page:
                    p2ps = p2ps[(page - 1) * page_size: page * page_size]
                else:
                    p2ps = p2ps[(page - 1) * page_size:]

                for product in p2ps:

                    try:
                        p2p_dict = dict()
                        p2p_dict['id'] = product.id
                        p2p_dict['link'] = '/p2p/detail/{}'.format(product.id)
                        p2p_dict['title'] = product.name
                        p2p_dict['username'] = product.borrower_name
                        # 借款用户没有uid, 渠道说用用户名
                        p2p_dict['userd'] = product.borrower_name
                        p2p_dict['asset_type'] = u'抵押标'
                        p2p_dict['borrow_type'] = product.category
                        p2p_dict['product_type'] = u'散标'
                        p2p_dict['amount'] = product.total_amount
                        p2p_dict['interest'] = (product.expected_earning_rate/100)
                        p2p_dict['borrow_period'] = (str(product.period) + u'天') \
                            if product.pay_method.startswith(u'日计息') else (str(product.period) + u'个月')

                        if product.pay_method == u'等额本息':
                            pay_method = u'等额本息'
                        elif product.pay_method == u'按月付息':
                            pay_method = u'月付息到期还本'
                        elif product.pay_method == u'到期还本付息':
                            pay_method = product.pay_method
                        elif product.pay_method == u'日计息一次性还本付息':
                            pay_method = product.pay_method
                        elif product.pay_method == u'日计息月付息到期还本':
                            pay_method = u'月付息到期还本'
                        else:
                            pay_method = product.pay_method
                        p2p_dict['repay_type'] = pay_method
                        p2p_dict['percentage'] = product.completion_rate/100
                        p2p_dict['reward'] = 0
                        p2p_dict['guarantee'] = 0
                        p2p_dict['credit'] = ''
                        p2p_dict['verify_time'] = timezone.localtime(product.publish_time).strftime('%Y-%m-%d %H:%M:%S')
                        p2p_dict['reverify_time'] = timezone.localtime(product.soldout_time).strftime('%Y-%m-%d %H:%M:%S')
                        p2p_dict['invest_count'] = P2PEquity.objects.filter(product=product).count()
                        p2p_dict['borrow_detail'] = product.usage
                        p2p_dict['attribute1'] = ''
                        p2p_dict['attribute2'] = ''
                        p2p_dict['attribute3'] = ''

                        p2p_list.append(p2p_dict)

                    except Exception, e:
                        print 'product{} error: {}'.format(product.pk, e)

                ret['data'] = p2p_list
                ret['page_count'] = com_page
                ret['page_index'] = page_index
                ret['result_code'] = 1
                ret['result_msg'] = u'获取数据成功'
            except Exception, e:
                print e
                ret = {
                    'page_count': 1,
                    'page_index': 1,
                    'result_code': 0,
                    'result_msg': u"数据出错: {}".format(e)
                }
        else:
            ret = {
                'page_count': 1,
                'page_index': 1,
                'result_code': 0,
                'result_msg': u"没有权限访问"
            }
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class ZORecordView(APIView):
    """
    获取借款列表
    """
    permission_classes = ()

    def check_sign(self):
        visit_key = str(self.request.GET.get('visit_key', None))
        sign = str(self.request.GET.get('sign', None))

        if visit_key and sign:
            full_path = self.request.get_full_path()
            full_path = urllib.unquote(full_path)
            # TODO 进行校验
            from hashlib import md5
            check_sign = md5(settings.ZO_SECRET + '&' + full_path.split('?')[1].split('&sign')[0]).hexdigest()
            if sign == check_sign.upper():
                return True

    def get(self, request):

        if self.check_sign():
            pid = int(self.request.GET.get('id', -1))
            page_size = int(self.request.GET.get('page_size', 100))
            page = int(self.request.GET.get('page_index', 1))

            p2p_list = []
            ret = dict()

            try:
                product = P2PProduct.objects.get(pk=pid)
                equities = P2PEquity.objects.filter(product=product)
                # 获取总页数, 和页数不对处理
                com_page = len(equities) / page_size + 1

                if page > com_page:
                    page = com_page
                if page < 1:
                    page = 1

                # 获取到对应的页数的所有投资记录
                if equities.count() / page_size >= page:
                    equities = equities[(page - 1) * page_size: page * page_size]
                else:
                    equities = equities[(page - 1) * page_size:]

                for equity in equities:
                    p2p_dict = dict()

                    p2p_dict['id'] = product.id
                    p2p_dict['invest_id'] = equity.id
                    p2p_dict['link'] = '/p2p/detail/{}'.format(product.id)
                    # p2p_dict['title'] = product.name
                    p2p_dict['username'] = equity.user.wanglibaouserprofile.name
                    p2p_dict['userid'] = equity.user.pk
                    try:
                        may_auto = AutomaticPlan.objects.get(user=equity.user)
                        if may_auto.amounts_auto == equity.equity \
                                and may_auto.rate_min > product.expected_earning_rate \
                                and may_auto.is_used:
                            p2p_dict['type'] = u'自动'
                        else:
                            p2p_dict['type'] = u'手动'
                    except Exception, e:
                        print 'Except: {}'.format(e)
                        p2p_dict['type'] = u'手动'
                    p2p_dict['money'] = equity.equity
                    p2p_dict['account'] = equity.equity
                    p2p_dict['status'] = u'成功' if equity.equity else u'失败'
                    p2p_dict['add_time'] = timezone.localtime(equity.created_at).strftime('%Y-%m-%d %H:%M:%S')

                    p2p_list.append(p2p_dict)

                ret['data'] = p2p_list
                ret['page_count'] = com_page
                ret['page_index'] = page
                ret['result_code'] = 1
                ret['result_msg'] = u'获取数据成功'

            except Exception, e:
                ret = {
                    'page_count': 1,
                    'page_index': 1,
                    'result_code': 0,
                    'result_msg': u"数据出错: {}".format(e)
                }

        else:
            ret = {
                'page_count': 1,
                'page_index': 1,
                'result_code': 0,
                'result_msg': u"没有权限访问"
            }
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class ZOCountView(APIView):
    """
    数据验证
    """
    permission_classes = ()

    def check_sign(self):
        visit_key = str(self.request.GET.get('visit_key', None))
        sign = str(self.request.GET.get('sign', None))

        if visit_key and sign:
            full_path = self.request.get_full_path()
            full_path = urllib.unquote(full_path)
            # TODO 进行校验
            from hashlib import md5
            check_sign = md5(settings.ZO_SECRET + '&' + full_path.split('?')[1].split('&sign')[0]).hexdigest()
            if sign == check_sign.upper():
                return True

    def get(self, request):

        if self.check_sign():
            try:
                status = int(self.request.GET.get('status', None))
                time_from = self.request.GET.get('time_from', None)
                time_to = self.request.GET.get('time_to', None)

                ret = dict()
                data = []
                data_dic = dict()

                p2p_status = []
                if status == 0:
                    p2p_status = [u'正在招标']
                if status == 1:
                    p2p_status = [u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'已完成']
                if status == 2:
                    p2p_status = [u'流标']

                p2ps = P2PProduct.objects.filter(status__in=p2p_status,
                                                 publish_time__gt=time_from,
                                                 publish_time__lte=time_to)
                buyers = []
                investor_count = 0
                for product in p2ps:
                    equities = P2PEquity.objects.filter(product=product)
                    buyers.extend([equity.user for equity in equities])
                    investor_count += equities.count()

                data_dic['amount_total'] = p2ps.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
                data_dic['volume_count'] = p2ps.count()
                borrowers = [product.borrower_name for product in p2ps]
                data_dic['borrower_count'] = len(set(borrowers))
                data_dic['investor_count'] = investor_count
                data_dic['investment_num'] = len(set(buyers))
                data.append(data_dic)

                ret['result_code'] = 1
                ret['result_msg'] = u'获取数据成功'
                ret['data'] = data

            except Exception, e:
                ret = {
                    'result_code': 0,
                    'result_msg': u"数据出错: {}".format(e)
                }

        else:
            ret = {
                'result_code': 0,
                'result_msg': u"没有权限访问"
            }
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class MidaiSuccessView(APIView):
    """
    每日成交标的列表 或者 每日新增标的列表
    """
    permission_classes = ()

    def check_sign(self):
        username = str(self.request.GET.get('username', None))
        password = str(self.request.GET.get('password', None))

        if username == settings.MIDAI_USERNAME and password == settings.MIDAI_PASSWORD:
            return True

        return False

    def get(self, request):

        time_str = str(self.request.GET.get('date', None))
        time_zone = settings.TIME_ZONE
        local = pytz.timezone(time_zone)
        naive = datetime.datetime.strptime(time_str, "%Y%m%d")

        date = str(naive.year) + '-' + str(naive.month) + '-' + str(naive.day)

        if self.check_sign():
            try:
                local_dt = local.localize(naive, is_dst=None)
                start = local_dt.astimezone(pytz.utc)
                end = start + timezone.timedelta(days=1)

                ret = dict()
                loans = []
                data_dic = dict()

                products = P2PProduct.objects.filter(make_loans_time__gt=start,
                                                     make_loans_time__lte=end)

                for product in products:

                    data_dic['id'] = product.pk
                    data_dic['title'] = product.name
                    data_dic['desc'] = product.usage
                    data_dic['borrower'] = product.borrower_name
                    data_dic['amount'] = product.total_amount
                    data_dic['interest'] = product.expected_earning_rate
                    data_dic['bidnum'] = P2PEquity.objects.filter(product=product).count()
                    data_dic['time_0'] = product.publish_time
                    data_dic['time_1'] = product.soldout_time
                    data_dic['time_2'] = product.make_loans_time
                    data_dic['url'] = "http://{}/p2p/detail/{}".format(request.get_host(), product.id),
                    data_dic['months'] = product.period if not product.pay_method.startswith(u"日计息") else 0
                    data_dic['days'] = product.period if product.pay_method.startswith(u"日计息") else 0
                    if product.pay_method == u'等额本息':
                        pay_method = u'等额本息'
                    if product.pay_method == u'按月付息':
                        pay_method = u'先息后本'
                    if product.pay_method == u'到期还本付息':
                        pay_method = u'一次性还款'
                    if product.pay_method == u'日计息一次性还本付息':
                        pay_method = u'一次性还款'
                    if product.pay_method == u'日计息月付息到期还本':
                        pay_method = u'先息后本'
                    data_dic['repaytype'] = pay_method
                    data_dic['progress'] = product.completion_rate
                    data_dic['reward'] = ''
                    data_dic['type'] = u'diya'

                    loans.append(data_dic)

                ret['date'] = date
                ret['total'] = products.count()
                ret['loans'] = loans

            except Exception, e:
                print 'MidaiSuccessView exception: {}'.format(e)
                ret = {
                    'date': date,
                    'total': 0,
                    'loans': []
                }

        else:
            ret = {
                'date': date,
                'total': 0,
                'loans': []
            }
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class MidaiNewView(APIView):
    """
    每日成交标的列表 或者 每日新增标的列表
    """
    permission_classes = ()

    def check_sign(self):
        username = str(self.request.GET.get('username', None))
        password = str(self.request.GET.get('password', None))

        if username == settings.MIDAI_USERNAME and password == settings.MIDAI_PASSWORD:
            return True

        return False

    def get(self, request):

        time_str = str(self.request.GET.get('date', None))
        time_zone = settings.TIME_ZONE
        local = pytz.timezone(time_zone)
        naive = datetime.datetime.strptime(time_str, "%Y%m%d")

        date = str(naive.year) + '-' + str(naive.month) + '-' + str(naive.day)

        if self.check_sign():
            try:
                local_dt = local.localize(naive, is_dst=None)
                start = local_dt.astimezone(pytz.utc)
                end = start + timezone.timedelta(days=1)

                ret = dict()
                loans = []
                data_dic = dict()

                products = P2PProduct.objects.filter(status=u'正在招标',
                                                     publish_time__gt=start,
                                                     publish_time__lte=end)

                for product in products:

                    data_dic['id'] = product.pk
                    data_dic['title'] = product.name
                    data_dic['desc'] = product.usage
                    data_dic['borrower'] = product.borrower_name
                    data_dic['amount'] = product.total_amount
                    data_dic['interest'] = product.expected_earning_rate
                    data_dic['bidnum'] = P2PEquity.objects.filter(product=product).count()
                    data_dic['time_0'] = product.publish_time
                    data_dic['time_1'] = product.soldout_time
                    data_dic['time_2'] = product.make_loans_time
                    data_dic['url'] = "http://{}/p2p/detail/{}".format(request.get_host(), product.id),
                    data_dic['months'] = product.period if not product.pay_method.startswith(u"日计息") else 0
                    data_dic['days'] = product.period if product.pay_method.startswith(u"日计息") else 0
                    if product.pay_method == u'等额本息':
                        pay_method = u'等额本息'
                    if product.pay_method == u'按月付息':
                        pay_method = u'先息后本'
                    if product.pay_method == u'到期还本付息':
                        pay_method = u'一次性还款'
                    if product.pay_method == u'日计息一次性还本付息':
                        pay_method = u'一次性还款'
                    if product.pay_method == u'日计息月付息到期还本':
                        pay_method = u'先息后本'
                    data_dic['repaytype'] = pay_method
                    data_dic['progress'] = product.completion_rate
                    data_dic['reward'] = ''
                    data_dic['type'] = u'diya'

                    loans.append(data_dic)

                ret['date'] = date
                ret['total'] = products.count()
                ret['loans'] = loans

            except Exception, e:
                print 'MidaiSuccessView exception: {}'.format(e)
                ret = {
                    'date': date,
                    'total': 0,
                    'loans': []
                }

        else:
            ret = {
                'date': date,
                'total': 0,
                'loans': []
            }
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


def get_rongtu_borrow():
    """
    author: Zhoudong
    http请求方式: GET  返回正在招标但是没有投满的标
    :return:
    """
    ret = dict()
    ret['borrow'] = []
    try:
        products = P2PProduct.objects.filter(status=u'正在招标')
    except Exception, e:
        print 'Exception : {}'.format(e)
        return

    for product in products:
        data = dict()
        data['borrowid'] = product.pk
        data['name'] = product.name
        data['url'] = "https://www.wanglibao.com/p2p/detail/{}".format(product.id)
        data['isday'] = 1 if product.pay_method.startswith(u"日计息") else 0
        data['timelimit'] = 0 if product.pay_method.startswith(u"日计息") else product.period
        data['timelimitday'] = product.period if product.pay_method.startswith(u"日计息") else 0
        data['account'] = product.total_amount
        data['owner'] = product.borrower_name
        data['apr'] = product.expected_earning_rate
        data['award'] = 1 if product.activity else 0
        data['partaccount'] = str(round(product.activity.rule.rule_amount, 2)) if product.activity else ''
        data['funds'] = 0

        if product.pay_method in [u'等额本息']:
            pay_method = 0
        elif product.pay_method in [u'日计息一次性还本付息', u'到期还本付息']:
            pay_method = 1
        else:
            pay_method = 3
        data['repaymentType'] = pay_method
        data['type'] = 1
        data['addtime'] = time.mktime(time.strptime(
            product.publish_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))
        data['sumTender'] = product.completion_rate
        data['startmoney'] = float(100)
        data['tenderTimes'] = P2PEquity.objects.filter(product=product).count()

        ret['borrow'].append(data)

    return json.dumps(ret['borrow'])


def get_rongtu_list():
    """
    author: Zhoudong
    http请求方式: GET  30天内每天的平均年利率
    :return:
    """
    ret = dict()
    today = timezone.now()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    ret['apr_data'] = {}
    ret['count_data'] = {}
    ret['dcount_data'] = {}
    try:
        for i in range(29, -1, -1):
            check_date = today_start - timezone.timedelta(days=i)

            products = P2PProduct.objects.filter(publish_time__gte=check_date,
                                                 publish_time__lt=(check_date + timezone.timedelta(days=1)))

            try:
                avg_rate = round(products.aggregate(Sum('expected_earning_rate'))
                                 ['expected_earning_rate__sum'] / products.count(), 2) or 0
                if avg_rate <= 0:
                    avg_rate = round(P2PProduct.objects.all().aggregate(Sum('expected_earning_rate'))
                                     ['expected_earning_rate__sum'] / products.count(), 2) or 15
            except Exception, e:
                avg_rate = round(P2PProduct.objects.all().aggregate(Sum('expected_earning_rate'))
                                 ['expected_earning_rate__sum'] / P2PProduct.objects.count(), 2) or 15
                print 'avg_rate error: {}'.format(e)
                print avg_rate

            try:
                avg_amount = products.aggregate(Sum('total_amount'))['total_amount__sum'] / 10000 or 0
            except Exception, e:
                print 'avg_amount error: {}'.format(e)
                avg_amount = 0

            p2p_equities = P2PEquity.objects.filter(created_at__gte=check_date,
                                                    created_at__lt=(check_date + timezone.timedelta(days=1)))
            try:
                day_amount = (p2p_equities.aggregate(Sum('equity'))['equity__sum'] / 10000) or 0
            except Exception, e:
                print 'day_amount error: {}'.format(e)
                day_amount = 0
            # 需要返回的数据进行字符串处理
            # date_str += "'" + str(check_date).split()[0][5:] + "'" + ','
            date_str = str(check_date).split()[0][5:]

            ret['apr_data'].update({date_str: avg_rate})
            ret['count_data'].update({date_str: avg_amount})
            ret['dcount_data'].update({date_str: day_amount})

    except Exception, e:
        print 'apr_data error: {}'.format(e)

    try:
        time_delta = timezone.timedelta(days=365)
        products = P2PProduct.objects.filter(publish_time__gte=today-time_delta)

        day_count = products.filter(pay_method__contains=u'日计息')
        month_count = products.filter().exclude(pay_method__contains=u'日计息')

        p2p_1to3 = month_count.filter(period__gte=1, period__lte=3)
        p2p_4to6 = month_count.filter(period__gte=4, period__lte=6)
        p2p_7to12 = month_count.filter(period__gte=7, period__lte=12)
        p2p_gt_12 = month_count.filter(period__gt=12)

        amount_p2p_1to3 = (day_count.aggregate(Sum('total_amount'))['total_amount__sum'] +
                           p2p_1to3.aggregate(Sum('total_amount'))['total_amount__sum']) / 10000 or 0
        amount_p2p_4to6 = p2p_4to6.aggregate(Sum('total_amount'))['total_amount__sum'] / 10000 or 0
        amount_p2p_7to12 = p2p_7to12.aggregate(Sum('total_amount'))['total_amount__sum'] / 10000 or 0
        amount_p2p_gt_12 = p2p_gt_12.aggregate(Sum('total_amount'))['total_amount__sum'] / 10000 or 0

        ret['time_data'] = u"[u'1-3个月',{}],[u'4-6个月',{}],[u'7-12个月',{}],[u'12个月以上',{}]".format(
            amount_p2p_1to3, amount_p2p_4to6, amount_p2p_7to12, amount_p2p_gt_12)
    except Exception, e:
        print 'time_data error: {}'.format(e)
        ret['time_data'] = u"[u'1-3个月',?],[u'4-6个月',?],[u'7-12个月',?],[u'12个月以上',?]"

    try:
        # 平台交易总量
        ret['cj_data'] = P2PEquity.objects.all().aggregate(Sum('equity'))['equity__sum'] / 10000 or 0
        # 平台待还金额
        ret['dh_data'] = P2PProduct.objects.filter(status__in=[u'还款中']).aggregate(
            Sum('total_amount'))['total_amount__sum'] / 10000 or 0
        # 当天平均年利率
        today_products = P2PProduct.objects.filter(publish_time__gte=today_start,
                                                   publish_time__lt=today_start + timezone.timedelta(days=1))
        try:
            ret['avg_apr'] = round(today_products.aggregate(Sum('expected_earning_rate'))
                                   ['expected_earning_rate__sum'] / today_products.count(), 2) or 0
        except Exception, e:
            print 'avg_apr error: {}'.format(e)
            ret['avg_apr'] = round(P2PProduct.objects.all().aggregate(Sum('expected_earning_rate'))
                                   ['expected_earning_rate__sum'] / P2PProduct.objects.count(), 2) or 0
    except Exception, e:
        print 'error: {}'.format(e)

    return json.dumps(ret)


def rongtu_post_data():

    url = settings.RONGTU_URL_TEST
    if settings.ENV == settings.ENV_PRODUCTION:
        url = settings.RONGTU_URL

    dangan_id = settings.RONGTU_ID
    borrow = get_rongtu_borrow()
    arg_list = get_rongtu_list()

    args = dict()
    args.update(dangan_id=dangan_id, borrow=borrow, list=arg_list)

    ret = requests.post(url, data=args)
    print ret.text
    return ret.text


class Rong360TokenView(APIView):
    """
    get token from us.
    """
    permission_classes = ()

    def get(self, request):
        rong_ret = dict()
        ret = create_token(request)
        # {'state': True, 'data': token}
        if ret['state']:
            rong_ret = {'data': {'token': ret['data']}}
        return HttpResponse(renderers.JSONRenderer().render(rong_ret, 'application/json'))


class Rong360P2PListView(APIView):
    """
    """
    permission_classes = ()

    def check_token(self):
        token = str(self.request.GET.get('token', None))
        return check_token(token)

    def get(self, request):

        if self.check_token():
            try:
                time_str = self.request.GET.get('date', None)
                page_size = int(self.request.GET.get('page_size', 20))
                page_index = int(self.request.GET.get('page', 1))

                time_zone = settings.TIME_ZONE
                local = pytz.timezone(time_zone)
                naive = datetime.datetime.strptime(time_str, "%Y-%m-%d")

                local_dt = local.localize(naive, is_dst=None)
                start = local_dt.astimezone(pytz.utc)
                end = start + timezone.timedelta(days=1)

                p2p_list = []
                ret = dict()

                p2ps = P2PProduct.objects.filter(publish_time__gte=start,
                                                 publish_time__lt=end).exclude(status=u'流标')

                # 获取总页数, 和页数不对处理
                com_page = len(p2ps) / page_size + 1

                if page_index > com_page:
                    page = com_page
                elif page_index < 1:
                    page = 1
                else:
                    page = page_index

                # 获取到对应的页数的所有用户
                total = p2ps.count()
                total_amount = p2ps.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
                if total / page_size >= page:
                    p2ps = p2ps[(page - 1) * page_size: page * page_size]
                else:
                    p2ps = p2ps[(page - 1) * page_size:]

                for product in p2ps:

                    try:
                        p2p_dict = dict()
                        p2p_dict['projectId'] = str(product.id)
                        p2p_dict['title'] = product.name
                        p2p_dict['amount'] = Decimal(product.total_amount)
                        p2p_dict['schedule'] = str(Decimal(product.completion_rate).quantize(Decimal('0.00')))
                        p2p_dict['interestRate'] = str(product.expected_earning_rate) + '%'
                        p2p_dict['deadline'] = product.period
                        p2p_dict['deadlineUnit'] = u'天' if product.pay_method.startswith(u'日计息') else u'月'
                        p2p_dict['reward'] = 0
                        p2p_dict['type'] = u'抵押标'

                        pay_method = 6
                        if product.pay_method == u'等额本息':
                            pay_method = 6
                        if product.pay_method == u'按月付息':
                            pay_method = 5
                        if product.pay_method == u'到期还本付息':
                            pay_method = 1
                        if product.pay_method == u'日计息一次性还本付息':
                            pay_method = 1
                        if product.pay_method == u'日计息月付息到期还本':
                            pay_method = 5
                        p2p_dict['repaymentType'] = pay_method

                        p2p_dict['province'] = None
                        p2p_dict['city'] = None
                        p2p_dict['userName'] = product.borrower_name
                        p2p_dict['userAvatarUrl'] = None
                        p2p_dict['amountUsedDesc'] = product.usage
                        p2p_dict['revenue'] = None
                        p2p_dict['loanUrl'] = 'https://{}/p2p/detail/{}'.format(request.get_host(), product.id)
                        p2p_dict['successTime'] = timezone.localtime(product.soldout_time).\
                            strftime('%Y-%m-%d %H:%M:%S') if product.soldout_time else ''
                        p2p_dict['publishTime'] = timezone.localtime(product.publish_time).\
                            strftime('%Y-%m-%d %H:%M:%S') if product.publish_time else ''

                        subscribes = []
                        equities = P2PEquity.objects.filter(product=product)
                        for equity in equities:
                            data_dic = dict()
                            data_dic['subscribeUserName'] = str(equity.user.pk)
                            data_dic['amount'] = Decimal(equity.equity)
                            data_dic['validAmount'] = Decimal(equity.equity)
                            data_dic['addDate'] = equity.confirm_at or equity.created_at
                            data_dic['status'] = 1 if equity.confirm else 2

                            # 标识手动或自动投标 0:手动 1:自动
                            try:
                                may_auto = AutomaticPlan.objects.get(user=equity.user)
                                if may_auto.amounts_auto == equity.equity \
                                        and may_auto.rate_min > product.expected_earning_rate \
                                        and may_auto.is_used:
                                    data_dic['type'] = 1
                                else:
                                    data_dic['type'] = 0
                            except Exception, e:
                                print 'Except: {}'.format(e)
                                data_dic['type'] = 0

                            subscribes.append(data_dic)

                        p2p_dict['subscribes'] = subscribes

                        p2p_list.append(p2p_dict)

                    except Exception, e:
                        print 'product{} error: {}'.format(product.pk, e)

                ret['borrowList'] = p2p_list
                ret['totalPage'] = com_page
                ret['currentPage'] = page_index
                ret['totalCount'] = total
                ret['totalAmount'] = Decimal(total_amount)

                return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))
            except Exception, e:
                ret = {
                    'page_count': 1,
                    'page_index': 1,
                    'result_msg': e
                }
        else:
            ret = {
                'page_count': 1,
                'page_index': 1,
                'result_code': 0,
                'result_msg': u"没有权限访问"
            }
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class XiguaP2PListView(APIView):
    """
    """
    permission_classes = ()

    def get(self, request):

        data_list = []
        ret = dict()

        p2ps = P2PProduct.objects.filter(status=u'正在招标')

        ret['recordCount'] = p2ps.count()
        ret['apiCorp'] = u'网利宝'
        ret['transferTime'] = timezone.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for product in p2ps:

            try:
                p2p_dict = dict()
                p2p_dict['creditSeriesName'] = u'散标'
                p2p_dict['productName'] = product.name
                p2p_dict['productCode'] = str(product.id)
                p2p_dict['totalInvestment'] = Decimal(product.total_amount)
                p2p_dict['annualRevenueRate'] = product.expected_earning_rate/100
                p2p_dict['loanLifeType'] = u'天' if product.pay_method.startswith(u'日计息') else u'月'
                p2p_dict['loanLifePeriod'] = product.period
                p2p_dict['interestPaymentType'] = product.pay_method
                p2p_dict['guaranteeInsitutions'] = product.warrant_company.name
                p2p_dict['onlineState'] = u'在售'
                p2p_dict['scale'] = str(Decimal(product.completion_rate).quantize(Decimal('0.00')))
                p2p_dict['publishDate'] = timezone.localtime(product.publish_time).\
                    strftime('%Y-%m-%d %H:%M:%S') if product.publish_time else ''
                p2p_dict['fixedRepaymentDate'] = 0
                p2p_dict['rewardRate'] = 0
                p2p_dict['investTimes'] = P2PEquity.objects.filter(product=product).count()
                p2p_dict['productURL'] = 'https://{}/p2p/detail/{}'.format(request.get_host(), product.id)
                p2p_dict['isFirstBuy'] = True if product.category == u'新手标' else False

                data_list.append(p2p_dict)

            except Exception, e:
                print 'product{} error: {}'.format(product.pk, e)

            ret['dataList'] = data_list

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class XiguaP2PQueryView(APIView):
    """
    """
    permission_classes = ()

    def get(self, request):

        args = request.GET.get('queryProductIdList', None)
        args_list = args.split(',')

        data_list = []
        ret = dict()

        p2ps = P2PProduct.objects.filter(pk__in=args_list)

        ret['recordCount'] = p2ps.count()
        ret['apiCorp'] = u'网利宝'
        ret['transferTime'] = timezone.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for product in p2ps:

            try:
                p2p_dict = dict()
                p2p_dict['productCode'] = str(product.id)
                p2p_dict['onlineState'] = u'在售'
                p2p_dict['scale'] = Decimal(product.completion_rate).quantize(Decimal('0.00'))
                p2p_dict['productURL'] = 'https://{}/p2p/detail/{}'.format(request.get_host(), product.id)
                p2p_dict['establishmentDate'] = timezone.localtime(product.soldout_time).\
                    strftime('%Y-%m-%d %H:%M:%S') if product.soldout_time else ''

                data_list.append(p2p_dict)

            except Exception, e:
                print 'product{} error: {}'.format(product.pk, e)

            ret['dataList'] = data_list

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))
