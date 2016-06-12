#!/usr/bin/env python
# encoding:utf-8

import json
import copy
import hashlib
import logging
import StringIO
import traceback
from django.utils import timezone
from django.db.models import Sum
from django.conf import settings
from django.contrib.auth.models import User
from common.utils import save_to_callback_record, set_dont_enforce_csrf_checks, check_sign_for_coop
from common.tools import utc_to_local_timestamp, now, Aes, StrQuote
from common.tasks import common_callback
from marketing.utils import get_channel_record, get_user_channel_record, get_channel_record_related
from wanglibao_account.models import Binding
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_oauth2.models import OauthUser, Client, AccessToken
from wanglibao_margin.models import MarginRecord
from wanglibao_p2p.models import P2PRecord, UserAmortization, P2PEquity
from wanglibao_p2p.utils import get_user_p2p_total_asset
from .utils import get_bajinshe_base_data, get_renrenli_base_data, bisouyi_callback


logger = logging.getLogger('wanglibao_cooperation')


_LOCALS_VAR = locals()


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


def get_id_number_for_coop(user_id):
    try:
        id_number = WanglibaoUserProfile.objects.get(user_id=user_id).id_number
        return id_number[:6] + '***' + id_number[-4:]
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


class CoopProcessorBase(object):
    """
    第三方处理器基类
    """
    def __init__(self, *args, **kwargs):
        self.channel = None
        self.c_code = None
        self.coop_processors = None

    def get_channel_processor(self, channel_code):
        """
        返回该用户的渠道处理器
        """
        channel_processor = self.coop_processors.get(channel_code.lower())
        if channel_processor:
            channel_processor = _LOCALS_VAR.get(channel_processor, None)
        else:
            channel_processor = None
        return channel_processor


# ######################第三方用户注册#####################

class CoopRegister(object):
    """
    第三方用户注册api
    """
    def __init__(self, btype, bid=None, client_id=None, order_id=None, access_token=None, account=None):
        self.btype = btype
        self.bid = bid
        self.client_id = client_id
        self.order_id = order_id
        self.access_token = access_token
        self.account = account
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
            if self.account:
                binding.b_account = self.account
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

    def save_to_access_token(self, user):
        logger.info("user[%s] enter save_to_access_token with client_id[%s] access_token[%s]" % (user.id, self.client_id,
                                                                                                 self.access_token))
        if self.access_token and self.client_id:
            client = Client.objects.filter(client_id=self.client_id).first()
            if client:
                access_token = AccessToken()
                access_token.token = self.access_token
                access_token.client = client
                access_token.user = user
                access_token.save()
                logger.info("user[%s] save_to_access_token success")

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
        self.save_to_access_token(user)
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
                    channel_processor(self.btype, self.bid,
                                      self.client_id, self.order_id,
                                      self.access_token, self.account).process_for_register(user)
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


class RenRenLiRegister(CoopRegister):
    def __init__(self, *args, **kwargs):
        super(RenRenLiRegister, self).__init__(*args, **kwargs)

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


class BiSouYiRegister(CoopRegister):
    def __init__(self, *args, **kwargs):
        super(BiSouYiRegister, self).__init__(*args, **kwargs)


class WangLiBaoRegister(CoopRegister):
    def __init__(self, *args, **kwargs):
        super(WangLiBaoRegister, self).__init__(*args, **kwargs)

    def process_for_register(self, user):
        """
        用户可以在从渠道跳转后的注册页使用邀请码，优先考虑邀请码
        """
        self.save_to_oauthuser(user)
        self.save_to_access_token(user)


# 注册第三方通道
coop_register_processor = {
    'bajinshe': 'BaJinSheRegister',
    'renrenli': 'RenRenLiRegister',
    'bisouyi': 'BiSouYiRegister',
    'wanglibao': 'WangLiBaoRegister',
}


# ######################用户第三方回调#####################

class CoopCallback(object):
    """
    第三方用户数据回调api
    """
    def __init__(self, channel=None):
        self.c_code = None
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
        logger.info("%s enter amortization_push with user_amortization[%s]" % (self.channel.code, user_amo.id))

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
                    except:
                        # 创建内存文件对象
                        fp = StringIO.StringIO()
                        traceback.print_exc(file=fp)
                        message = fp.getvalue()
                        logger.info("%s raise error: %s" % (channel_processor.__name__, message))
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
                    # 创建内存文件对象
                    fp = StringIO.StringIO()
                    traceback.print_exc(file=fp)
                    message = fp.getvalue()
                    logger.info("%s raise error: %s" % (channel_processor.__name__, message))
            else:
                logger.info("coop callback not found processor matched for user[%s]" % user_id)
        else:
            logger.info("coop callback not found channel matched from db for user[%s]" % user_id)


class BaJinSheCallback(CoopCallback):
    """需要IP鉴权"""

    def __init__(self, *args, **kwargs):
        super(BaJinSheCallback, self).__init__(*args, **kwargs)
        self.c_code = 'bajinshe'
        self.coop_id = settings.BAJINSHE_COOP_ID
        self.coop_key = settings.BAJINSHE_COOP_KEY
        self.purchase_call_back_url = settings.BAJINSHE_PURCHASE_PUSH_URL
        self.register_call_back_url = settings.BAJINSHE_ACCOUNT_PUSH_URL
        self.transaction_call_back_url = settings.BAJINSHE_TRANSACTION_PUSH_URL

        self.headers = {
            'Content-Type': 'application/json'
        }

    def register_call_back(self, user_id, order_id, total_asset=0, p2p_margin=0, base_data=None):
        super(BaJinSheCallback, self).register_call_back(user_id, order_id)
        user = User.objects.get(pk=user_id)
        if order_id:
            order_id = '%s_0001' % order_id
        else:
            order_id = '%s_0001' % user_id

        if not base_data:
            data = get_bajinshe_base_data(order_id)
        else:
            data = base_data

        bid = get_tid_for_coop(user_id)
        if data and bid:
            pre_total_interest = UserAmortization.objects.filter(user=user,
                                                                 settled=True
                                                                 ).aggregate(Sum('interest'))['interest__sum'] or 0
            act_data = {
                'bingdingUid': bid,
                'usn': get_user_phone_for_coop(user_id),
                'sumIncome': float(pre_total_interest),
                'totalBalance': float(total_asset),
                'availableBalance': float(p2p_margin),
            }

            data['tran'] = [act_data]
            data = json.dumps(data)

            ret_parser = 'bajinshe_callback_ret_parser'
            call_back_record_data = {
                'user': user,
                'order_id': order_id,
                'description': u'账户推送',
                'request_url': self.register_call_back_url,
                'request_data': data,
                'request_headers': self.headers,
                'request_action': 1,
                'ret_parser': ret_parser,
            }

            save_to_callback_record(call_back_record_data, self.c_code)

            common_callback.apply_async(
                kwargs={'channel': self.c_code, 'url': self.register_call_back_url,
                        'params': data, 'headers': self.headers,
                        'order_id': order_id, 'ret_parser': ret_parser})

    def recharge_call_back(self, user_id, order_id):
        super(BaJinSheCallback, self).recharge_call_back(user_id, order_id)
        data = get_bajinshe_base_data(order_id)
        bid = get_tid_for_coop(user_id)
        if data and bid:
            margin_record = MarginRecord.objects.filter(user_id=user_id, order_id=order_id).first()
            if margin_record:
                user = User.objects.filter(pk=user_id).select_related('margin').first()
                act_data = {
                    'bingdingUid': bid,
                    'usn': get_user_phone_for_coop(user_id),
                    'businessName': u'充值',
                    'businessType': 0,
                    'businessBid': order_id,
                    'money': float(margin_record.amount),
                    'time': timezone.localtime(margin_record.create_time).strftime('%Y%m%d%H%M%S'),
                    'moneyType': 0,
                    'availableBalance': float(margin_record.margin_current),
                    'totalBalance': float(margin_record.margin_current),
                    'channel': 'bjs',
                }

                data['tran'] = [act_data]
                data = json.dumps(data)

                ret_parser = 'bajinshe_callback_ret_parser'
                call_back_record_data = {
                    'user': user,
                    'order_id': order_id,
                    'description': u'充值回调',
                    'request_url': self.transaction_call_back_url,
                    'request_data': data,
                    'request_headers': self.headers,
                    'request_action': 1,
                    'ret_parser': ret_parser,
                }

                save_to_callback_record(call_back_record_data, self.c_code)

                common_callback.apply_async(
                    kwargs={'channel': self.c_code, 'url': self.transaction_call_back_url,
                            'params': data, 'headers': self.headers,
                            'order_id': order_id, 'ret_parser': ret_parser})

                # 推送账户数据
                p2p_margin = user.margin.margin
                total_asset = get_user_p2p_total_asset(user)
                self.register_call_back(user_id, order_id, total_asset, p2p_margin)

    def purchase_call_back(self, user_id, order_id):
        super(BaJinSheCallback, self).purchase_call_back(user_id, order_id)
        base_data = get_bajinshe_base_data(order_id)
        data = copy.deepcopy(base_data)
        bid = get_tid_for_coop(user_id)
        if data and bid:
            margin_record = MarginRecord.objects.filter(user_id=user_id, order_id=order_id).first()
            if margin_record:
                user = User.objects.filter(pk=user_id).select_related('margin').first()
                act_data = {
                    'bingdingUid': bid,
                    'usn': get_user_phone_for_coop(user_id),
                    'businessName': u'投资',
                    'businessType': 3,
                    'businessBid': order_id,
                    'money': float(margin_record.amount),
                    'time': timezone.localtime(margin_record.create_time).strftime('%Y%m%d%H%M%S'),
                    'moneyType': 1,
                    'availableBalance': float(margin_record.margin_current),
                    'totalBalance': float(margin_record.margin_current),
                    'channel': 'bjs',
                }

                data['tran'] = [act_data]
                data = json.dumps(data)

                ret_parser = 'bajinshe_callback_ret_parser'
                call_back_record_data = {
                    'user': user,
                    'order_id': order_id,
                    'description': u'投资回调',
                    'request_url': self.transaction_call_back_url,
                    'request_data': data,
                    'request_headers': self.headers,
                    'request_action': 1,
                    'ret_parser': ret_parser,
                }

                save_to_callback_record(call_back_record_data, self.c_code)

                common_callback.apply_async(
                    kwargs={'channel': self.c_code, 'url': self.transaction_call_back_url,
                            'params': data, 'headers': self.headers,
                            'order_id': order_id, 'ret_parser': ret_parser})

                # 推送账户数据
                p2p_margin = user.margin.margin
                total_asset = get_user_p2p_total_asset(user)
                self.register_call_back(user_id, order_id, total_asset=total_asset, p2p_margin=p2p_margin)

    def get_amortize_data(self, **kwargs):
        user_amo = kwargs['user_amo']
        user_amos = kwargs['user_amos']
        equity = kwargs['equity']
        bid = kwargs['bid']
        user_phone = kwargs['user_phone']
        period = kwargs['period']
        period_type = kwargs['period_type']
        product = kwargs['product']
        profit_methods = kwargs['profit_methods']
        state = kwargs['state']

        act_data = {
            'investmentPid': equity.id,
            'bingdingUid': bid,
            'usn': user_phone,
            'money': float(equity.equity),
            'period': period,
            'periodType': period_type,
            'productPid': product.id,
            'productName': product.name,
            'productType': 2,
            'profitMethods': profit_methods,
            'apr': product.get_p2p_rate,
            'state': state,
            'purchases': timezone.localtime(equity.created_at).strftime('%Y%m%d%H%M%S'),
            'channel': 'bjs',
            'bearingDate': timezone.localtime(now()).strftime('%Y%m%d%H%M%S'),
        }

        reward_data_list = list()
        for user_amo in user_amos:
            income_state = 2 if user_amo.settled else 1
            reward_data = {
                'calendar': timezone.localtime(user_amo.term_date).strftime('%Y%m%d%H%M%S'),
                'income': float(user_amo.interest),
                'principal': float(user_amo.principal) + float(product.get_activity_earning(equity.equity)),
                'incomeState': income_state,
            }
            reward_data_list.append(reward_data)

        act_data['reward'] = reward_data_list

        return act_data

    def amortization_push(self, user_amo):
        super(BaJinSheCallback, self).amortization_push(user_amo)
        user_amos = UserAmortization.objects.filter(product=user_amo.product, user=user_amo.user)
        if user_amo.settled or user_amos.count() == user_amo.terms:
            if user_amo.settled:
                order_id = '%s_0005_%s' % (user_amo.user_id, user_amo.id)
            else:
                order_id = '%s_0006_%s' % (user_amo.user_id, user_amo.id)

            data = get_bajinshe_base_data(order_id)
            bid = get_tid_for_coop(user_amo.user_id)
            if data and bid:
                user = User.objects.filter(pk=user_amo.user_id).select_related('margin').first()
                product = user_amo.product
                period = product.period
                pay_method = product.pay_method
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

                act_data_list = list()
                equity = P2PEquity.objects.filter(user=user, product=product).first()
                user_phone = get_user_phone_for_coop(user_amo.user_id)
                get_amortize_arg = {
                    'product': product,
                    'equity': equity,
                    'bid': bid,
                    'user_phone': user_phone,
                    'period': period,
                    'period_type': period_type,
                    'profit_methods': profit_methods,
                    'user_amos': user_amos,
                }
                term_mark = list()
                if user_amo.settled:
                    get_amortize_arg['user_amo'] = user_amo
                    if user_amo.term == user_amo.terms:
                        get_amortize_arg['state'] = 1
                    else:
                        get_amortize_arg['state'] = 0
                    act_data = self.get_amortize_data(**get_amortize_arg)
                    act_data_list.append(act_data)
                else:
                    for user_amo in user_amos:
                        term_mark.append(str(user_amo.term))
                        if user_amo.term == 1:
                            get_amortize_arg['user_amo'] = user_amo
                            get_amortize_arg['state'] = 5
                            act_data = self.get_amortize_data(**get_amortize_arg)
                            act_data_list.append(act_data)

                data['tran'] = act_data_list
                data = json.dumps(data)

                ret_parser = 'bajinshe_callback_ret_parser'
                if user_amo.settled:
                    description = u'产品:%s %d期还款回调' % (product.id, user_amo.term)
                else:
                    term_mark = u','.join(term_mark)
                    description = u'产品:%s %s期满标回调' % (product.id, term_mark)

                call_back_record_data = {
                    'user': user,
                    'order_id': order_id,
                    'description': description,
                    'request_url': self.purchase_call_back_url,
                    'request_data': data,
                    'request_headers': self.headers,
                    'request_action': 1,
                    'ret_parser': ret_parser,
                }

                save_to_callback_record(call_back_record_data, self.c_code)

                common_callback.apply_async(
                    kwargs={'channel': self.c_code, 'url': self.purchase_call_back_url,
                            'params': data, 'headers': self.headers,
                            'order_id': order_id, 'ret_parser': ret_parser})

                # 推送账户数据
                p2p_margin = user.margin.margin
                total_asset = get_user_p2p_total_asset(user)
                self.register_call_back(user_amo.user_id, order_id, total_asset, p2p_margin)


class RenRenLiCallback(CoopCallback):
    """需要IP鉴权"""

    def __init__(self, *args, **kwargs):
        super(RenRenLiCallback, self).__init__(*args, **kwargs)
        self.c_code = 'renrenli'
        self.purchase_call_back_url = settings.RENRENLI_PURCHASE_PUSH_URL
        self.coop_account_name = settings.RENRENLI_ACCOUNT_NAME

    def get_purchase_data(self, p2p_record):
        bid = get_tid_for_coop(p2p_record.user_id)
        if bid:
            data = {
                'User_name': self.coop_account_name,
                'Order_no': p2p_record.order_id,
                'Pro_name': p2p_record.product.name,
                'Pro_id': p2p_record.product.id,
                'Invest_money': float(p2p_record.amount),
                'Rate': p2p_record.product.get_p2p_rate,
                'Invest_start_date': utc_to_local_timestamp(p2p_record.create_time),
                'Invest_end_date': 0,
                'Back_money': 0,
                'Back_last_date': 0,
                'Cust_key': bid,
                'Invest_full_scale_date': 0,
            }
        else:
            data = dict()

        return data

    def amortization_push(self, user_amo):
        super(RenRenLiCallback, self).amortization_push(user_amo)
        p2p_record = P2PRecord.objects.filter(product=user_amo.product,
                                              user_id=user_amo.user_id
                                              ).order_by('create_time').last()
        if p2p_record:
            if user_amo.settled:
                if p2p_record.amotized_amount:
                    amotized_amount = p2p_record.amotized_amount + user_amo.get_total_amount()
                else:
                    amotized_amount = user_amo.get_total_amount()

                P2PRecord.objects.filter(product=user_amo.product,
                                         user_id=user_amo.user_id
                                         ).update(back_last_date=user_amo.term_date,
                                                  amotized_amount=amotized_amount)
            else:
                if user_amo.term == user_amo.terms:
                    P2PRecord.objects.filter(product=user_amo.product,
                                             user_id=user_amo.user_id
                                             ).update(invest_end_time=user_amo.term_date)

    def purchase_call_back(self, user_id, order_id):
        super(RenRenLiCallback, self).purchase_call_back(user_id, order_id)
        p2p_record = P2PRecord.objects.filter(user_id=user_id,
                                              order_id=order_id,
                                              catalog=u'申购').select_related('product').first()
        if p2p_record:
            bid = get_tid_for_coop(p2p_record.user_id)
            data = get_renrenli_base_data(self.channel.code)
            if bid and data:
                act_data = self.get_purchase_data(p2p_record)
                if act_data:
                    user = User.objects.get(pk=p2p_record.user_id)
                    data['Data'] = json.dumps([act_data])

                    ret_parser = 'renrenli_callback_ret_parser'
                    call_back_record_data = {
                        'user': user,
                        'order_id': order_id,
                        'description': u'投资回调',
                        'request_url': self.purchase_call_back_url,
                        'request_data': data,
                        'request_action': 1,
                        'ret_parser': ret_parser,
                    }

                    save_to_callback_record(call_back_record_data, self.c_code)

                    common_callback.apply_async(
                        kwargs={'channel': self.c_code, 'url': self.purchase_call_back_url,
                                'params': data, 'order_id': order_id,
                                'ret_parser': ret_parser})
            else:
                logger.info("renrenli get_amotize_data failed with bid[%s] data[%s]" % (bid, data))


class BiSouYiCallback(CoopCallback):
    """需要IP鉴权"""

    def __init__(self, *args, **kwargs):
        super(BiSouYiCallback, self).__init__(*args, **kwargs)
        self.c_code = 'bisouyi'
        self.coop_id = settings.BAJINSHE_COOP_ID
        self.coop_key = settings.BAJINSHE_COOP_KEY
        self.register_call_back_url = settings.BAJINSHE_ACCOUNT_PUSH_URL

    def register_call_back(self, user_id, order_id=None, total_asset=0, p2p_margin=0, base_data=None):
        super(BiSouYiCallback, self).register_call_back(user_id, order_id)
        binding = Binding.objects.filter(user_id=user_id).select_related('channel').first()
        access_token = AccessToken.objects.filter(user_id=user_id).first()
        if access_token and binding and binding.b_account:
            order_id = order_id or '%s_0001' % user_id
            user = User.objects.get(pk=user_id)
            phone = get_user_phone_for_coop(user_id)
            account = binding.b_account
            access_token = access_token.token

            content_data = {
                'pcode': settings.BISOUYI_PCODE,
                'token': access_token,
                'yaccount': phone,
                'jaccount': account,
                'mobile': phone,
                'type': 1,
                'tstatus': 1,
            }

            url = settings.BISOUYI_OATUH_PUSH_URL
            ret_parser = 'bisouyi_callback_ret_parser'
            call_back_record_data = {
                'user': user,
                'description': u'授权推送',
            }
            bisouyi_callback(url, content_data, self.c_code, call_back_record_data,
                             async_callback=False, order_id=order_id, ret_parser=ret_parser)

    def purchase_call_back(self, user_id, order_id):
        super(BiSouYiCallback, self).purchase_call_back(user_id, order_id)
        p2p_record = P2PRecord.objects.filter(user_id=user_id, catalog=u'申购',
                                              order_id=order_id).select_related('product').first()
        if p2p_record:
            user = User.objects.get(pk=user_id)
            product = p2p_record.product
            pay_method = product.pay_method
            if pay_method in (u'等额本息', u'按月付息', u'到期还本付息'):
                unit = 2
                period = product.period * 30
            else:
                unit = 1
                period = product.period

            content_data = {
                'pcode': settings.BISOUYI_PCODE,
                'sn': p2p_record.order_id,
                'ocode': product.id,
                'yaccount': get_user_phone_for_coop(user_id),
                'idcard': get_id_number_for_coop(user_id)[:18],
                'name': product.name[:100],
                'amoney': float(p2p_record.amount),
                'aperiod': period,
                'unit': unit,
                'adate': timezone.localtime(p2p_record.create_time).strftime('%Y-%m-%d %H:%M:%S'),
                'rate': product.get_p2p_rate,
                'guarantee': pay_method,
                'sdate': '1970-01-01 00:00:00',
                'edate': '1970-01-01 00:00:00',
                'bankcard': get_user_phone_for_coop(user_id),
                'ptype': 1,
                'ostatus': 1,
                'pstatus': 1,
                'bstatus': 1,
            }

            ret_parser = 'bisouyi_callback_ret_parser'
            url = settings.BISOUYI_PURCHASE_PUSH_URL
            call_back_record_data = {
                'user': user,
                'description': u'投资推送',
            }
            bisouyi_callback(url, content_data, self.c_code, call_back_record_data,
                             async_callback=False, order_id=order_id, ret_parser=ret_parser)

            p2p_equity = P2PEquity.objects.filter(product=product, user_id=user_id).first()
            if p2p_equity:
                content_data = {
                    'pcode': settings.BISOUYI_PCODE,
                    'rlsn': p2p_equity.id,
                    'sn': p2p_record.order_id,
                    'ocode': product.id,
                    'yaccount': get_user_phone_for_coop(user_id),
                    'ostatus': 1,
                    'pstatus': 1,
                    'bstatus': 1,
                }

                order_id = str(order_id) + '_' + str(p2p_equity.id)
                url = settings.BISOUYI_ORDER_RELATION_PUSH_URL
                ret_parser = 'bisouyi_callback_ret_parser'
                call_back_record_data = {
                    'user': user,
                    'description': u'投资订单关联推送',
                }
                bisouyi_callback(url, content_data, self.c_code, call_back_record_data,
                                 order_id=order_id, ret_parser=ret_parser)

    def amortization_push(self, user_amo):
        super(BiSouYiCallback, self).amortization_push(user_amo)
        user_amos = UserAmortization.objects.filter(product=user_amo.product, user=user_amo.user)
        if user_amo.settled or user_amos.count() == user_amo.terms:
            product = user_amo.product
            user_id = user_amo.user_id
            p2p_equity = P2PEquity.objects.filter(product=user_amo.product, user_id=user_amo.user_id).first()
            if p2p_equity:
                user = User.objects.get(pk=user_amo.user_id)
                user_phone = get_user_phone_for_coop(user_amo.user_id)
                content_data = {}
                if user_amo.settled:
                    content_data = {
                        'pcode': settings.BISOUYI_PCODE,
                        'sn': p2p_equity.id,
                        'ocode': product.id,
                        'yaccount': get_user_phone_for_coop(user_id),
                        'bdate': timezone.localtime(user_amo.settlement_time).strftime('%Y-%m-%d %H:%M:%S'),
                        'bmoney': user_amo.get_total_amount + float(product.get_activity_earning(p2p_equity.equity)),
                        'ostatus': 1,
                        'pstatus': 1,
                    }

                    if user_amo.term == user_amo.terms:
                        content_data['bstatus'] = 4
                    else:
                        content_data['bstatus'] = 2
                else:
                    user_amo = user_amos.filter(term=1).first()
                    if user_amo:
                        last_user_amo = user_amos.filter(term=user_amo.terms).first()
                        if last_user_amo:
                            content_data = {
                                'pcode': settings.BISOUYI_PCODE,
                                'sn': p2p_equity.id,
                                'ocode': product.id,
                                'yaccount': user_phone,
                                'sdate': timezone.localtime(user_amo.created_time).strftime('%Y-%m-%d %H:%M:%S'),
                                'edate': timezone.localtime(last_user_amo.term_date).strftime('%Y-%m-%d %H:%M:%S'),
                                'ostatus': 1,
                                'pstatus': 1,
                                'bstatus': 2,
                            }

                if content_data:
                    if user_amo.settled:
                        order_id = '%s_0005_%s' % (user_amo.user_id, user_amo.id)
                        url = settings.BISOUYI_PURCHASE_REFUND_PUSH_URL
                        call_back_des = u'产品:%s %d期还款回调' % (product.id, user_amo.term)
                    else:
                        order_id = '%s_0006_%s' % (user_amo.user_id, user_amo.id)
                        url = settings.BISOUYI_ON_INTEREST_PUSH_URL
                        call_back_des = u'产品:%s 起息回调' % product.id

                    call_back_record_data = {
                        'user': user,
                        'description': call_back_des,
                    }

                    ret_parser = 'bisouyi_callback_ret_parser'
                    bisouyi_callback(url, content_data, self.c_code, call_back_record_data,
                                     order_id=order_id, ret_parser=ret_parser)

# 第三方回调通道
coop_callback_processor = {
    'bajinshe': 'BaJinSheCallback',
    'renrenli': 'RenRenLiCallback',
    'bisouyi': 'BiSouYiCallback',
}


class CoopLandProcessor(CoopProcessorBase):
    """
    渠道着陆处理
    """
    def __init__(self, request):
        super(CoopLandProcessor, self).__init__(request)
        self.request = request
        self.c_code = self.get_channel_code_from_request()

        # 传递渠道邀请码时使用的变量名
        self.external_channel_key = settings.PROMO_TOKEN_QUERY_STRING
        self.internal_channel_key = 'channel_code'

        self.get_from_data = dict()
        self.session_key_list = list()
        self.joined_sign_params = dict()
        self.internal_params_data = dict()

    def get_channel_code_from_request(self):
        return self.request.GET.get(self.external_channel_key, '')

    def get_appoint_data_from_request(self, get_from):
        if get_from == 'POST':
            appoint_data = self.request.POST
        elif get_from == 'GET':
            appoint_data = self.request.GET
        elif get_from == 'REQUEST':
            appoint_data = self.request.REQUEST
        elif get_from == 'BODY':
            appoint_data = json.loads(self.request.body.strip())
        else:
            appoint_data = self.request.META

        return appoint_data

    def get_params_value(self, params):
        if params.level == 2:
            params_parent = params.parent
            if params_parent in self.get_from_data:
                params_value = self.get_from_data[params_parent].get(params.external_name, None)
                if params_value:
                    return params_value
        else:
            get_from_list = params.get_from
            for get_from in get_from_list:
                if get_from in self.get_from_data:
                    params_value = self.get_from_data[get_from].get(params.external_name, None)
                    if params_value:
                        return params_value
                else:
                    appoint_data = self.get_appoint_data_from_request(get_from)
                    self.get_from_data[get_from] = appoint_data
                    if get_from == 'HEAD':
                        params_value = appoint_data.get('HTTP_%s' % params.external_name.upper(), None)
                    else:
                        params_value = appoint_data.get(params.external_name, None)

                    if params_value:
                        return params_value

        return params.default_value

    def process_params_decrypt(self, name, encrypt_str, encrypt_method):
        params_data = None
        try:
            if encrypt_method == 'json':
                params_data = json.loads(encrypt_str)
            elif encrypt_method == 'aes-128-ecb':
                ase = Aes()
                decrypt_text = ase.decrypt(settings.BISOUYI_AES_KEY, encrypt_str, mode_tag='ECB')
                params_data = json.loads(decrypt_text)
        except:
            logger.exception('channel[%s] params[%s] process_params_decrypt raise error: ' % (self.c_code, name))

        params_data_type = type(params_data)
        if params_data and params_data_type != 'dict':
            logger.info('channel[%s] params[%s] process_params_decrypt result: value[%s] type[%s]' %
                        (self.c_code, name, params_data, params_data_type))
            params_data = None

        return params_data

    def init_joined_sign_data(self, params, params_value):
        # 初始化签名数据
        if params.is_join_sign:
            # FixMe,此处只是顺应大部分渠道处理逻辑，如有特殊处理请重构
            if params.quote_url_decrypt and self.request.method == 'GET':
                quote = StrQuote()
                params_value = quote.quote_plus(params_value)

            internal_name = params.internal_name
            if internal_name == 'sign':
                self.joined_sign_params[internal_name] = params_value
            else:
                self.joined_sign_params[params.external_name] = params_value

    def process_level_one_params(self, params, params_value):
        if params.level == 1 and params.is_decrypt:
            params_name = params.name
            params_data = self.process_params_decrypt(params_name,
                                                      params_value,
                                                      params.decrypt_method)
            if params_data:
                self.get_from_data[params_name] = params_data

    def process_save_to_session(self):
        self.save_to_session(self.internal_channel_key, self.c_code)
        channel_params = self.channel.all_params.filter(is_abandoned=False).order_by('level', 'get_from')
        for params in channel_params:
            if params.is_save_session or params.level == 1 or params.is_join_sign:
                params_value = self.get_params_value(params)
                if params_value:
                    self.process_level_one_params(params, params_value)
                    self.init_joined_sign_data(params, params_value)

                    internal_name = params.internal_name
                    if params.is_save_session and internal_name:
                        self.save_to_session(internal_name, params_value)

    def process_csrf_checked(self):
        if self.channel.disable_csrf:
            sign_format = self.channel.sign_format
            sign = self.joined_sign_params.get('sign', None)
            if sign_format and sign:
                if check_sign_for_coop(sign, sign_format, self.joined_sign_params):
                    set_dont_enforce_csrf_checks(self.request)

    def save_to_session(self, key, value):
        self.request.session[key] = value
        self.session_key_list.append(key)

    def clear_session(self, session_key_list=None):
        session_key_list = session_key_list or self.session_key_list or self.request.session.keys()
        for session_key in session_key_list:
            self.request.session.pop(session_key, None)

    def process_for_session(self, session_act):
        """
        session_act ==> 0 保存参数到session
        session_act ==> 1 清除session参数
        """

        try:
            if self.c_code:
                if session_act == 0:
                    channel = get_channel_record_related(self.c_code)
                    if channel:
                        self.channel = channel
                        self.process_save_to_session()
                        self.process_csrf_checked()
                    else:
                        logger.info("process_for_session not found channel matched for channel_code[%s]" % self.c_code)
                elif session_act == 1:
                    self.clear_session()
        except:
            logger.exception("process_for_session raise error: ")

    def process_params_map(self):
        """
        处理所有第三方着陆，注册页跳转
        """
        channel_params = self.channel.all_params.filter(is_abandoned=False).order_by('level', 'get_from')
        for params in channel_params:
            params_value = self.get_params_value(params)
            if params_value:
                self.process_level_one_params(params, params_value)
                self.internal_params_data[params.internal_name] = params_value

    def process_for_request_params_map(self):
        """
        处理第三方着陆，注册页跳转
        """
        channel = get_channel_record_related(self.c_code)
        if channel:
            self.channel = channel
            try:
                self.process_params_map()
            except:
                logger.exception("channel[%s] process_for_land raise error: " % self.c_code)
        else:
            logger.info("process_for_land not found channel matched for channel_code[%s]" % self.c_code)

        return self.internal_params_data


# class BaJinSheLand(CoopLandProcessor):
#     def __init__(self, request):
#         super(BaJinSheLand, self).__init__(request)
#         self.external_channel_client_id_key = 'appid'
#         self.external_channel_phone_key = 'usn'
#         self.external_channel_sign_key = 'signature'
#         self.internal_channel_sign_key = 'sign'
#         self.external_channel_user_key = 'p_user_id'
#         self.external_channel_refresh_token_key = 'refresh_token'
#         self.external_channel_access_token_key = 'access_token'
#
#     def save_to_session(self):
#         super(BaJinSheLand, self).save_to_session()
#
#         if self.request.META.get('CONTENT_TYPE', '').lower().find('application/json') != -1:
#             req_data = json.loads(self.request.body.strip())
#         else:
#             req_data = self.request.REQUEST
#
#         channel_phone = req_data.get(self.external_channel_phone_key, None)
#         sign = req_data.get(self.external_channel_sign_key, None)
#         client_id = req_data.get(self.external_channel_client_id_key, None)
#         channel_user = req_data.get(self.external_channel_user_key, None)
#         refresh_token = req_data.get(self.external_channel_refresh_token_key, None)
#
#         if channel_user:
#             self.request.session[self.internal_channel_user_key] = channel_user
#
#         if channel_phone:
#             self.request.session[self.internal_channel_phone_key] = channel_phone
#
#         if sign:
#             self.request.session[self.internal_channel_sign_key] = sign
#
#         if client_id:
#             self.request.session[self.internal_channel_client_id_key] = client_id
#
#         if refresh_token:
#             self.request.session[self.internal_channel_refresh_token_key] = refresh_token
#
#     def clear_session(self):
#         super(BaJinSheLand, self).clear_session()
#         self.request.session.pop(self.internal_channel_phone_key, None)
#         self.request.session.pop(self.internal_channel_sign_key, None)
#         self.request.session.pop(self.internal_channel_refresh_token_key, None)
#         self.request.session.pop(self.internal_channel_client_id_key, None)
#
#
# class BiSouYiLand(CoopLandProcessor):
#     def __init__(self, request):
#         super(BiSouYiLand, self).__init__(request)
#         self.external_channel_client_id_key = 'cid'
#         self.external_channel_phone_key = 'mobile'
#         self.external_channel_sign_key = 'sign'
#         self.internal_channel_sign_key = 'sign'
#         self.channel_content_key = 'content'
#         self.external_channel_access_token_key = 'token'
#         self.external_channel_next_url_key = 'other'
#         self.external_channel_account_key = 'account'
#
#     @property
#     def channel_phone(self):
#         if self.request.META.get('CONTENT_TYPE', '').lower().find('application/json') != -1:
#             req_data = json.loads(self.request.body.strip())
#         else:
#             req_data = self.request.REQUEST
#
#         content = req_data.get(self.channel_content_key, None)
#         content = parse_bisouyi_content(content) if content else {}
#         return content.get(self.external_channel_phone_key, None)
#
#     @property
#     def channel_access_token(self):
#         if self.request.META.get('CONTENT_TYPE', '').lower().find('application/json') != -1:
#             req_data = json.loads(self.request.body.strip())
#         else:
#             req_data = self.request.REQUEST
#
#         content = req_data.get(self.channel_content_key, None)
#         content = parse_bisouyi_content(content) if content else {}
#         return content.get(self.external_channel_access_token_key, None)
#
#     def save_to_session(self):
#         super(BiSouYiLand, self).save_to_session()
#
#         if self.request.META.get('CONTENT_TYPE', '').lower().find('application/json') != -1:
#             req_data = json.loads(self.request.body.strip())
#         else:
#             req_data = self.request.REQUEST
#
#         content = req_data.get(self.channel_content_key, None)
#
#         if self.request.method == 'GET':
#             sign = req_data.get(self.external_channel_sign_key, None)
#             client_id = req_data.get(self.external_channel_client_id_key, None)
#         else:
#             sign = self.request.META.get('HTTP_%s' % self.external_channel_sign_key.upper(), None)
#             client_id = self.request.META.get('HTTP_%s' % self.external_channel_client_id_key.upper(), None)
#
#         if sign:
#             self.request.session[self.internal_channel_sign_key] = sign
#
#         if client_id:
#             self.request.session[self.internal_channel_client_id_key] = client_id
#
#         if content:
#             content = parse_bisouyi_content(content)
#             if content:
#                 phone = content.get(self.external_channel_phone_key, None)
#                 other = content.get(self.external_channel_next_url_key, None)
#                 account = content.get(self.external_channel_account_key, None)
#                 token = content.get(self.external_channel_access_token_key, None)
#
#                 if phone:
#                     self.request.session[self.internal_channel_phone_key] = phone
#
#                 if other:
#                     self.request.session[self.internal_channel_next_url_key] = other
#
#                 if account:
#                     self.request.session[self.internal_channel_account_key] = account
#
#                 if token:
#                     self.request.session[self.internal_channel_access_token_key] = token
#
#     def clear_session(self):
#         super(BiSouYiLand, self).clear_session()
#         self.request.session.pop(self.internal_channel_sign_key, None)
#         self.request.session.pop(self.internal_channel_client_id_key, None)
#         self.request.session.pop(self.internal_channel_phone_key, None)
#         self.request.session.pop(self.internal_channel_next_url_key, None)
#         self.request.session.pop(self.internal_channel_account_key, None)
#         self.request.session.pop(self.internal_channel_access_token_key, None)
#
#
# # 第三方着陆处理器
# coop_land_processor = {
#     'bajinshe': 'BaJinSheLand',
#     # 'renrenli': 'RenRenLiLand',
#     'bisouyi': 'BiSouYiLand',
# }
