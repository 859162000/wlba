#!/usr/bin/env python
# encoding:utf-8

if __name__ == '__main__':
    import os

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wanglibao.settings')

import hashlib
import logging
from django.utils import timezone
from django.db.models import Sum
from marketing.utils import get_channel_record, get_user_channel_record
from wanglibao_account.models import Binding
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_oauth2.models import OauthUser, Client
from wanglibao_rest.utils import get_current_utc_timestamp
from wanglibao_p2p.models import P2PRecord
from wanglibao_margin.models import MarginRecord
from wanglibao import settings
from .tasks import bajinshe_callback
from .utils import get_bajinshe_base_data


logger = logging.getLogger('wanglibao_cooperation')


def get_client(channel_code):
    try:
        client = Client.objects.get(channel__code=channel_code)
    except Client.DoesNotExist:
        client = None

    return client


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


def get_user_phone_for_coop(user_id):
    try:
        phone_number = WanglibaoUserProfile.objects.get(user_id=user_id).phone
        return phone_number
    except:
        return None


def get_tid_for_coop(user_id):
    try:
        return Binding.objects.filter(user_id=user_id).get().bid
    except:
        return None


_LOCALS_VAR = locals()


class CoopSessionProcessor(object):
    """
    第三方请求参数保存session
    """
    def __init__(self, request):
        self.request = request
        # 传递渠道邀请码时使用的变量名
        self.external_channel_key = settings.PROMO_TOKEN_QUERY_STRING
        self.internal_channel_key = 'channel_code'
        # 传递渠道用户时使用的变量名
        self.external_channel_user_key = settings.PROMO_TOKEN_USER_KEY
        self.internal_channel_user_key = 'channel_user'
        # 传递渠道oauth客户端ID时使用的变量名
        self.external_channel_client_id_key = settings.CLIENT_ID_QUERY_STRING
        self.internal_channel_client_id_key = 'client_id'

    def get_channel_code_from_request(self):
        return self.request.GET.get(self.external_channel_key, None)

    def save_to_session(self):
        channel_code = self.get_channel_code_from_request()
        channel_user = self.request.GET.get(self.external_channel_user_key, None)

        if channel_code:
            self.request.session[self.internal_channel_key] = channel_code

        if channel_user:
            self.request.session[self.internal_channel_user_key] = channel_user

    def clear_session(self):
        self.request.session.pop(self.internal_channel_key, None)
        self.request.session.pop(self.internal_channel_user_key, None)

    def get_channel_processor(self, channel_code):
        """
        返回该用户的渠道处理器
        """
        channel_processor = coop_session_processor.get(channel_code.lower())
        if channel_processor:
            channel_processor = _LOCALS_VAR.get(channel_processor, None)
        else:
            channel_processor = None
        return channel_processor

    def all_processors_for_session(self, session_act):
        """
        session_act ==> 0 保存参数到session
        session_act ==> 1 清除session参数
        """

        channel_code = self.get_channel_code_from_request()
        channel_processor = self.get_channel_processor(channel_code)
        if channel_processor:
            try:
                if session_act == 0:
                    channel_processor(self.request).save_to_session()
                elif session_act == 1:
                    channel_processor(self.request).clear_session()
            except Exception, e:
                logger.info("%s raise error: %s" % (channel_processor.__name__, e))
        else:
            logger.info("all_processors_for_user_register not found processor matched for channel_code[%s]" % channel_code)


class BaJinSheSession(CoopSessionProcessor):
    def __init__(self, request):
        super(BaJinSheSession, self).__init__(request)
        self.external_channel_client_id_key = 'appid'
        self.external_channel_phone_key = 'usn'
        self.internal_channel_phone_key = 'phone'
        self.external_channel_sign_key = 'signature'
        self.internal_channel_sign_key = 'sign'
        self.external_channel_user_key = 'p_user_id'

    def save_to_session(self):
        super(BaJinSheSession, self).save_to_session()
        channel_phone = self.request.REQUEST.get(self.external_channel_phone_key, None)
        sign = self.request.REQUEST.get(self.external_channel_sign_key, None)
        client_id = self.request.REQUEST.get(self.external_channel_client_id_key, None)

        if channel_phone:
            self.request.session[self.internal_channel_phone_key] = channel_phone

        if sign:
            self.request.session[self.internal_channel_sign_key] = sign

        if client_id:
            self.request.session[self.internal_channel_client_id_key] = client_id

    def clear_session(self):
        super(BaJinSheSession, self).clear_session()
        self.request.session.pop(self.internal_channel_phone_key, None)
        self.request.session.pop(self.internal_channel_sign_key, None)


# 注册第三方通道
coop_session_processor = {
    'bajinshe': 'BaJinSheSession',
    'renrenli': 'RenRenLiSession',
}


# ######################第三方用户注册#####################

class CoopRegister(object):
    """
    第三方用户注册api
    """
    def __init__(self, btype, bid=None, client_id=None, order_id=None):
        self.btype = btype
        self.bid = bid
        self.client_id = client_id
        self.order_id = order_id
        self.channel = get_channel_record(self.btype)

    def save_to_binding(self, user):
        """
        处理从url获得的渠道参数
        :param user:
        :return:
        """
        logger.info("user[%s] enter save_to_binding with btype[%s] bid[%s]" % (user.id, self.btype, self.bid))
        if self.channel:
            binding = Binding()
            binding.user = user
            binding.channel = self.channel
            if self.bid:
                binding.bid = self.bid
            binding.save()

    def save_to_oauthuser(self, user):
        logger.info("user[%s] enter save_to_oauthuser with client_id[%s]" % (user.id, self.client_id))
        if self.client_id:
            try:
                client = Client.objects.get(client_id=self.client_id)
                oauth_user = OauthUser()
                oauth_user.user = user
                oauth_user.client = client
                oauth_user.save()
            except Client.DoesNotExist:
                logger.info("user[%s] save to oauthuser failed with invalid client_id [%s]" % (user.id, self.client_id))

    def register_call_back(self, user):
        """
        用户注册成功后的回调
        :param user:
        :return:
        """
        CoopCallback(self.channel).process_all_callback(user.id, 'register', self.order_id)

    def process_for_register(self, user):
        """
        用户可以在从渠道跳转后的注册页使用邀请码，优先考虑邀请码
        """
        self.save_to_binding(user)
        self.save_to_oauthuser(user)
        self.register_call_back(user)

    def get_channel_processor(self, channel_code):
        """
        返回该用户的渠道处理器
        """
        channel_processor = coop_register_processor.get(channel_code.lower())
        if channel_processor:
            channel_processor = _LOCALS_VAR.get(channel_processor, None)
        else:
            channel_processor = None
        return channel_processor

    def all_processors_for_user_register(self, user):
        logger.info("user[%s] enter all_processors_for_user_register" % user.id)
        if self.channel:
            channel_processor = self.get_channel_processor(self.channel.code)
            if channel_processor:
                try:
                    channel_processor(self.btype, self.bid, self.client_id, self.order_id).process_for_register(user)
                except Exception, e:
                    logger.info("%s raise error: %s" % (channel_processor.__name__, e))
            else:
                logger.info("all_processors_for_user_register not found processor matched for user[%s]" % user.id)
        else:
            logger.info("all_processors_for_user_register not found channel matched from db with channel_code[%s]" % self.btype)


class BaJinSheRegister(CoopRegister):
    def __init__(self, *args, **kwargs):
        super(BaJinSheRegister, self).__init__(*args, **kwargs)

    def save_to_binding(self, user):
        """
        处理从url获得的渠道参数
        :param user:
        :return:
        """
        logger.info("user[%s] enter save_to_binding with btype[%s] bid[%s]" % (user.id, self.btype, self.bid))
        if self.channel:
            binding = Binding()
            binding.user = user
            binding.channel = self.channel
            binding.bid = get_uid_for_coop(user.id)
            binding.save()


# 注册第三方通道
coop_register_processor = {
    'bajinshe': 'BaJinSheRegister',
    'renrenli': 'RenRenLiRegister',
}


# ######################用户第三方回调#####################

class CoopCallback(object):
    """
    第三方用户数据回调api
    """
    def __init__(self, channel=None):
        self.channel = channel
        # 渠道提供给我们的秘钥
        self.coop_id = None
        self.coop_key = None
        self.call_back_url = None

    def register_call_back(self, user_id, order_id):
        """
        用户注册成功后的回调
        :param user:
        :return:
        """
        logger.info("%s enter register_call_back with user[%s] order_id[%s]" % (self.channel.code, user_id, order_id))

    def validate_call_back(self, user_id):
        """
        用户实名验证后的回调
        :param user:
        :return:
        """
        pass

    def binding_card_call_back(self, user_id):
        """
        用户绑定银行卡之后的回调
        :param user:
        :return:
        """
        pass

    def purchase_call_back(self, user_id, order_id):
        """
        用户购买后回调，一般用于用于用户首次投资之后回调第三方接口
        :param order_id:
        :param user:
        :return:
        """
        logger.info("%s enter purchase_call_back with user[%s] order_id[%s]" % (self.channel.code, user_id, order_id))

    def recharge_call_back(self, user_id, order_id):
        """
        用户充值后回调，一般用于用户首次充值之后回调第三方接口
        :param order_id:
        :param user:
        :return:
        """
        logger.info("%s enter recharge_call_back with user[%s] order_id[%s]" % (self.channel.code, user_id, order_id))

    def amortization_push(self, user_amo):
        """
        用户还款计划结算回调
        :param user_amo:
        :return:
        """
        logger.info("%s enter register_call_back with user_amortization[%s]" % (self.channel.code, user_amo.id))

    def get_channel_processor(self, channel_code):
        """
        返回该用户的渠道处理器
        """
        channel_processor = coop_callback_processor.get(channel_code.lower())
        if channel_processor:
            channel_processor = _LOCALS_VAR.get(channel_processor, None)
        else:
            channel_processor = None
        return channel_processor

    def process_amortize_callback(self, amortizations):
        logger.info("coop callback enter process_amortize_callback")
        for amo in amortizations:
            user_id = amo.user_id
            channel = get_user_channel_record(user_id)
            if channel:
                channel_processor = self.get_channel_processor(channel.code)
                if channel_processor:
                    try:
                        channel_processor(channel).amortization_push(amo)
                    except Exception, e:
                        logger.info("%s raise error: %s" % (channel_processor.__name__, e))
                else:
                    logger.info("coop callback not found processor matched for user[%s]" % user_id)
            else:
                logger.info("coop callback not found channel matched from db for user[%s]" % user_id)

    def process_all_callback(self, user_id, act, order_id=None):
        logger.info("coop callback enter process_all_callback with user[%s] act[%s] order_id[%s]" % (user_id, act, order_id))
        channel = get_user_channel_record(user_id)
        if channel:
            channel_processor = self.get_channel_processor(channel.code)
            if channel_processor:
                try:
                    call_back_processor = getattr(channel_processor(channel), '%s_call_back' % act.lower(), None)
                    call_back_processor(user_id, order_id)
                except Exception, e:
                    logger.info("%s raise error: %s" % (channel_processor.__name__, e))
            else:
                logger.info("coop callback not found processor matched for user[%s]" % user_id)
        else:
            logger.info("coop callback not found channel matched from db for user[%s]" % user_id)


class BaJinSheCallback(CoopCallback):
    def __init__(self, *args, **kwargs):
        super(BaJinSheCallback, self).__init__(*args, **kwargs)
        self.coop_id = settings.BAJINSHE_COOP_ID
        self.coop_key = settings.BAJINSHE_COOP_KEY
        self.purchase_call_back_url = settings.BAJINSHE_PURCHASE_PUSH_URL
        self.register_call_back_url = settings.BAJINSHE_ACCOUNT_PUSH_URL
        self.transaction_call_back_url = settings.BAJINSHE_TRANSACTION_PUSH_URL

    def register_call_back(self, user_id, order_id):
        super(BaJinSheCallback, self).register_call_back(user_id, order_id)
        utc_timestamp = get_current_utc_timestamp()
        query_id = '%s_%s' % (utc_timestamp, '0001')
        data = get_bajinshe_base_data(query_id)
        if data:
            act_data = {
                'bingdingUid': self.channel.bid,
                'usn': get_user_phone_for_coop(user_id),
                'sumIncome': 0,
                'totalBalance': 0,
                'availableBalance': 0,
            }
            data['tran'] = [act_data]
            # 异步回调
            bajinshe_callback.apply_async(
                kwargs={'data': data, 'url': self.purchase_call_back_url})

    def recharge_call_back(self, user_id, order_id):
        super(BaJinSheCallback, self).recharge_call_back(user_id, order_id)
        utc_timestamp = get_current_utc_timestamp()
        query_id = '%s_%s' % (utc_timestamp, '0002')
        data = get_bajinshe_base_data(query_id)
        if data:
            margin_record = MarginRecord.object(user_id=user_id, order_id=order_id).first()
            if margin_record:
                act_data = {
                    'bingdingUid': self.channel.bid,
                    'usn': get_user_phone_for_coop(user_id),
                    'businessName': margin_record.description,
                    'businessType': 0,
                    'businessBid': order_id,
                    'money': margin_record.amount,
                    'time': timezone.localtime(margin_record.create_time()).strftime('%Y%m%d%H%M%S'),
                    'moneyType': 0,
                    'availableBalance': margin_record.margin_current,
                }
                data['tran'] = [act_data]
                # 异步回调
                bajinshe_callback.apply_async(
                    kwargs={'data': data, 'url': self.transaction_call_back_url})

    def purchase_call_back(self, user_id, order_id):
        super(BaJinSheCallback, self).purchase_call_back(user_id, order_id)
        utc_timestamp = get_current_utc_timestamp()
        query_id = '%s_%s' % (utc_timestamp, '0003')
        data = get_bajinshe_base_data(query_id)
        if data:
            margin_record = MarginRecord.object(user_id=user_id, order_id=order_id).first()
            if margin_record:
                act_data = {
                    'bingdingUid': self.channel.bid,
                    'usn': get_user_phone_for_coop(user_id),
                    'businessName': margin_record.description,
                    'businessType': 3,
                    'businessBid': order_id,
                    'money': margin_record.amount,
                    'time': timezone.localtime(margin_record.create_time()).strftime('%Y%m%d%H%M%S'),
                    'moneyType': 1,
                    'availableBalance': margin_record.margin_current,
                }
                data['tran'] = [act_data]
                # 异步回调
                bajinshe_callback.apply_async(
                    kwargs={'data': data, 'url': self.transaction_call_back_url})

    def amortization_push(self, user_amo):
        super(BaJinSheCallback, self).amortization_push(user_amo)
        utc_timestamp = get_current_utc_timestamp()
        order_id = '%s_%s' % (utc_timestamp, '0005')
        data = get_bajinshe_base_data(order_id)
        if data:
            period = user_amo.product.period
            pay_method = user_amo.product.pay_method
            if pay_method in [u'等额本息', u'按月付息', u'到期还本付息']:
                period_type = 1
            else:
                period_type = 2

            if pay_method == u'等额本息':
                profit_methods = 3
            elif pay_method == u'按月付息':
                profit_methods = 1
            elif pay_method == u'到期还本付息':
                profit_methods = 2
            else:
                profit_methods = 11

            act_data = {
                'calendar': timezone.localtime(user_amo.settlement_time).strftime('%Y%m%d%H%M%S'),
                'income': user_amo.interest,
                'principal': user_amo.principal,
                'incomeState': 2,
                'investmentPid': user_amo.id,
                'bingdingUid': self.channel.bid,
                'usn': get_user_phone_for_coop(user_amo.user_id),
                'money': user_amo.equity_amount,
                'period': period,
                'periodType': period_type,
                'productPid': user_amo.product.id,
                'productName': user_amo.product.name,
                'productType': 2,
                'profitMethods': profit_methods,
                'apr': user_amo.product.expected_earning_rate,
                'state': 1,
                'purchases': timezone.localtime(user_amo.equity_confirm_at).strftime('%Y%m%d%H%M%S'),
            }
            data['tran'] = [act_data]
            # 异步回调
            bajinshe_callback.apply_async(
                kwargs={'data': data, 'url': self.purchase_call_back_url})

# 第三方回调通道
coop_callback_processor = {
    'bajinshe': 'BaJinSheCallback',
    'renrenli': 'RenRenLiCallback',
}
