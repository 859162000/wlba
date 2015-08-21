#!/usr/bin/env python
# encoding:utf-8
import json
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
from django.db.models import Sum, Q
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
     FUBA_COOP_ID, FUBA_KEY, FUBA_CHANNEL_CODE, FUBA_DEFAULT_TID, YUNDUAN_CALL_BACK_URL, WLB_FOR_YUNDUAN_KEY, \
     YUNDUAN_COOP_ID, YUNDUAN_KEY
from wanglibao_account.models import Binding, IdVerification
from wanglibao_account.tasks import common_callback, jinshan_callback
from wanglibao_p2p.models import P2PEquity, P2PRecord, P2PProduct, ProductAmortization
from wanglibao_pay.models import Card
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_redis.backend import redis_backend

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
            if record and record.name == 'shls':
                bid = request.DATA.get('tid', "").strip()
                bid_len = Binding._meta.get_field_by_name('bid')[0].max_length
                if bid and bid_len >= len(bid) > 0:
                    binding = Binding()
                    binding.user = user
                    binding.btype = record.name
                    binding.bid = bid
                    binding.save()
        except:
            pass


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
        channel_code  = self.get_channel_code_from_request()
        channel_user  = self.request.GET.get(self.external_channel_user_key, None)
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

    def process_for_register(self, user, invite_code):
        """
        用户可以在从渠道跳转后的注册页使用邀请码，优先考虑邀请码
        """
        promo_token = super(WaihuRegister, self).channel_code
        if promo_token:
            super(WaihuRegister, self).save_to_introduceby(user, invite_code)
            super(WaihuRegister, self).save_to_binding(user)
            super(WaihuRegister, self).clear_session()


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
        # 富爸爸需求，如果uid为空，uid设置为1316
        return self.request.session.get(self.internal_channel_user_key, FUBA_DEFAULT_TID)

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
                if earliest_settlement_time + datetime.timedelta(seconds=180) <= current_time:
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
        self.call_back_url = YUNDUAN_CALL_BACK_URL
        self.coop_id = YUNDUAN_COOP_ID
        self.coop_key = YUNDUAN_KEY

    def yunduan_call_back(self, user):
        # Binding.objects.get(user_id=user.id),使用get如果查询不到会抛异常
        binding = Binding.objects.filter(user_id=user.id).first()
        p2p_record = P2PRecord.objects.filter(user_id=user.id).last()
        if binding and p2p_record:
            order_id = p2p_record.id
            sig = hashlib.md5(str(order_id)+str(self.coop_key)).hexdigest()
            params = {
                'action': 'create',
                'order': order_id,
                'sig': sig,
                'planid': self.coop_id,
                'uid': binding.bid,
            }
            common_callback.apply_async(
                kwargs={'url': self.call_back_url, 'params': params, 'channel':self.c_code})

    def validate_call_back(self, user):
        self.yunduan_call_back(user)

    def purchase_call_back(self, user):
        # 判断是否是首次投资
        if P2PRecord.objects.filter(user_id=user.id, catalog=u'申购').count() == 1:
            self.yunduan_call_back(user)


# 注册第三方通道
coop_processor_classes = [TianMangRegister, YiRuiTeRegister, BengbengRegister,
                          JuxiangyouRegister, DouwanRegister, JinShanRegister,
                          ShiTouCunRegister, FUBARegister]


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
            return product_id_or_instance.activity.rule.rule_amount + product_id_or_instance.expected_earning_rate
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
    product_info = {
        'for_freshman': 0, #是否新手标
        'period': 0, #产品周期
        'rate': 0, #产品收益率
        'amount': 0, #募集金额
        'ordered_amount': 0, #已募集金额
        'buyer': 0, #投资人数
        'start_time': 0, #标的开始时间
        'end_time': 0, #标的结束时间
        'state': '', #产品状态
        'borrower': '', #借款人名称
        'guarant_mode': '本息担保', #担保方式
        'guarantor': '', #担保方名称
        'amortization_start_time': 0, #还款开始时间
        'amortization_end_time': 0, #还款结束时间
        'borrower_guarant_type': '第三方担保', #借款担保方式
        'repayment_type': '', #还款方式
        'start_price': 100, #起投金额
        'id': 0, #产品id
    }
    product_info['for_freshman'] = 1 if mproduct.category == '新手标' else 0
    product_info['period'] = mproduct.period
    product_info['rate'] = get_rate(mproduct)
    product_info['amount'] = mproduct.total_amount
    product_info['ordered_amount'] = mproduct.ordered_amount
    product_info['buyer'] = mproduct.bought_people_count
    product_info['start_time'] = mproduct.publish_time
    product_info['end_time'] = mproduct.end_time
    product_info['state'] = mproduct.status
    product_info['borrower'] = mproduct.borrower_name
    product_info['guarantor'] = mproduct.warrant_company
    product_info['amortization_start_time'], product_info['end_time'] = get_amortization_time(mproduct)
    product_info['repayment_type'] = mproduct.pay_method
    product_info['id'] = mproduct.id

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

    xicai_info = {
        'access_token': access_token,
        'product_name': '网利宝',
        'isexp': p2p_info['for_freshman'],
        'life_cycle': p2p_info['period'],
        'ev_rate': p2p_info['rate'],
        'amount': p2p_info['amount'],
        'invest_amount': p2p_info['ordered_amount'],
        'invest_mans': p2p_info['buyer'],
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
    return xicai_info


def xicai_post_product_info(mproduct, access_token):
    p2p_info = xicai_get_p2p_info(mproduct, access_token)
    url = settings.XICAI_CREATE_P2P_URL
    requests.post(url, data=p2p_info)


def xicai_post_updated_product_info(mproduct, access_token):
    p2p_info = xicai_get_p2p_info(mproduct, access_token)
    updated_p2p_info = {}
    for k in ['access_token', 'invest_amount',
              'invest_mans', 'underlying_end',
              'product_state', 'repay_start_time',
              'repay_end_time', 'p2p_product_id']:
        updated_p2p_info[k] = p2p_info[k]
    url = settings.XICAI_UPDATE_P2P_URL
    requests.post(url, data=updated_p2p_info)


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

                user_dict['totalmoney'] = P2PEquity.objects.filter(user=user).aggregate(sum=Sum('equity'))['sum']

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
    http请求方式: POST
    http://121.40.31.143:86/api/JsonsFinancial/PlatformBasic/
    向菜苗推送我们的平台信息.
    :return:
    """
    url = settings.CAIMIAO_PLATFORM_URL
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
    :return:
    """

    url = settings.CAIMIAO_P2P_URL
    key = settings.CAIMIAO_SECRET

    post_data = dict()

    now = timezone.now()

    start_time = now - settings.XICAI_UPDATE_TIMEDELTA
    wangli_products = P2PProduct.objects.filter(Q(publish_time__gte=start_time) & Q(publish_time__lt=now))

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
