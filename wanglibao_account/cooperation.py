#!/usr/bin/env python
# encoding:utf-8
if __name__ == '__main__':
    import os
    import sys

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wanglibao.settings')

import hashlib
import datetime
import logging
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
import requests
from rest_framework import renderers
from rest_framework.views import APIView
from marketing.models import Channels, IntroducedBy, PromotionToken
from marketing.utils import set_promo_user
from wanglibao import settings
from wanglibao.settings import  YIRUITE_CALL_BACK_URL, \
        TIANMANG_CALL_BACK_URL, WLB_FOR_YIRUITE_KEY, YIRUITE_KEY, BENGBENG_KEY, \
    WLB_FOR_BENGBENG_KEY, BENGBENG_CALL_BACK_URL, BENGBENG_COOP_ID, JUXIANGYOU_COOP_ID, JUXIANGYOU_KEY, \
    JUXIANGYOU_CALL_BACK_URL, TINMANG_KEY, DOUWANWANG_CALL_BACK_URL
from wanglibao_account.models import Binding, IdVerification
from wanglibao_account.tasks import  yiruite_callback,  common_callback
from wanglibao_p2p.models import P2PEquity, P2PRecord, P2PProduct, ProductAmortization
from wanglibao_pay.models import Card
from wanglibao_profile.models import WanglibaoUserProfile

logger = logging.getLogger(__name__)

def get_uid_for_coop(user_id):
    """
    返回给渠道的用户ID
    :param user_id:
    :return:
    """
    m= hashlib.md5()
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
        binding_time  = Card.objects.filter(user_id=user_id).order_by('add_at').first().add_at
        return binding_time
    except Exception, e:
        return None


#######################第三方用户注册#####################

class CoopRegister(object):
    """
    第三方用户注册api
    """
    def __init__(self, request):
        #本渠道的名称
        self.c_code = None
        self.request = request
        #传递渠道邀请码时使用的变量名
        self.external_channel_key = settings.PROMO_TOKEN_QUERY_STRING
        self.internal_channel_key = 'channel_code'
        #传递渠道用户时使用的变量名
        self.external_channel_user_key = settings.PROMO_TOKEN_USER_KEY
        self.internal_channel_user_key = 'channel_user'
        #渠道提供给我们的秘钥
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
            #logger.debug('save to session %s:%s'%(self.internal_channel_key, channel_code))
        if channel_user:
            self.request.session[self.internal_channel_user_key] = channel_user
            #logger.debug('save to session %s:%s'%(self.internal_channel_user_key, channel_user))

    def clear_session(self):
        self.request.session.pop(self.internal_channel_key, None)
        self.request.session.pop(self.internal_channel_user_key, None)

    def save_to_introduceby(self, user, invite_code):
        """
        处理使用邀请码注册的用户
        """
        set_promo_user(self.request, user, invite_code)
        #try:
        #    channel = Channels.objects.filter(code=invite_code).get()
        #    introduced_by_record = IntroducedBy()
        #    introduced_by_record.channel = channel
        #    introduced_by_record.user = user
        #    introduced_by_record.save()
        #    logger.debug('save user %s introduced by channel to introducedby ' %user)
        #except:
        #    pass

        #try:
        #    user_promote_token = PromotionToken.objects.filter(token=invite_code).get()
        #    #使用user_id查询
        #    introduced_by_user = User.objects.get(pk=user_promote_token.pk)
        #    introduced_by_record = IntroducedBy()
        #    introduced_by_record.introduced_by = introduced_by_user
        #    introduced_by_record.user = user
        #    introduced_by_record.save()
        #    logger.debug('save user %s introduced by user to introducedby ' %user)
        #except:
        #    pass

    def save_to_binding(self, user):
        """
        处理从url获得的渠道参数
        :param user:
        :return:
        """
        if self.channel_user:
            binding = Binding()
            binding.user = user
            binding.btype = self.channel_name
            binding.bid = self.channel_user
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
        if not invite_code:
            invite_code = self.channel_code
        # logger.debug('get invite code %s'%(invite_code))
        if invite_code:
            #通过渠道注册
            for processor in self.processors:
                if processor.c_code == processor.channel_code:
                    processor.process_for_register(user, invite_code)
                    return
            #默认注册
            self.process_for_register(user, invite_code)

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
        channel_processor = self.get_user_channel_processor(user)
        # logger.debug('channel processor %s'%channel_processor)
        if channel_processor:
            channel_processor.validate_call_back(user)

    def process_for_binding_card(self, user):
        channel_processor = self.get_user_channel_processor(user)
        # logger.debug('channel processor %s'%channel_processor)
        if channel_processor:
            channel_processor.binding_card_call_back(user)

    def process_for_purchse(self, user):
        channel_processor = self.get_user_channel_processor(user)
        if channel_processor:
            channel_processor.purchase_call_back(user)

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
        yiruite_callback.apply_async(kwargs={'url': self.call_back_url, 'params': params})

class BengbengRegister(CoopRegister):
    def __init__(self, request):
        super(BengbengRegister, self).__init__(request)
        self.c_code = 'bengbeng'
        self.coop_id = BENGBENG_COOP_ID
        self.coop_key = BENGBENG_KEY
        self.call_back_url = BENGBENG_CALL_BACK_URL

    def binding_card_call_back(self, user):
        uid_for_coop = get_uid_for_coop(user.id)
        sign = hashlib.md5(self.coop_id + self.channel_user + uid_for_coop + self.coop_key).hexdigest()
        params = {
            'adID': self.coop_id,
            'annalID': self.channel_user,
            'idCode': uid_for_coop,
            'doukey': sign,
            'idName': get_username_for_coop(user.id)
        }
        common_callback.apply_async(
            kwargs={'url': self.call_back_url, 'params': params, 'channel':self.c_code})

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
            kwargs={'url': self.call_back_url, 'params': params, 'channel':self.c_code})

class DouwanRegister(CoopRegister):
    def __init__(self, request):
        super(DouwanRegister, self).__init__(request)
        self.c_code = 'douwanwang'
        self.call_back_url = DOUWANWANG_CALL_BACK_URL

    def douwan_callback(self, user, step):
        params = {
            'tid': get_tid_for_coop(user.id),
            step : get_uid_for_coop(user.id)
        }
        common_callback.apply_async(
            kwargs={'url': self.call_back_url, 'params': params, 'channel':self.c_code})

    def register_call_back(self, user):
        self.douwan_callback(user, 'step1')

    def validate_call_back(self, user):
        self.douwan_callback(user, 'step2')

    def binding_card_call_back(self, user):
        self.douwan_callback(user, 'step3')


#注册第三方通道
coop_processor_classes = [TianMangRegister, YiRuiTeRegister, BengbengRegister, JuxiangyouRegister, DouwanRegister]

#######################第三方用户查询#####################

class CoopQuery(APIView):
    """
    第三方用户查询api
    """
    permission_classes = ()
    channel = None

    #查询用户的类型
    REGISTERED_USER = 0
    VALIDATED_USER = 1
    BINDING_USER = 2
    INVESTED_USER = 3

    def get_promo_user(self, channel_code, startday, endday):
        """

        :param channel_code: like "tianmang"
        :param startday: 日期格式20050606
        :param endday:
        :return:
        """
        startday= datetime.datetime.strptime(startday, "%Y%m%d")
        endday = datetime.datetime.strptime(endday, "%Y%m%d")
        if startday > endday:
            endday, startday = startday, endday

        #daydelta = datetime.timedelta(days=1)
        daydelta = datetime.timedelta(hours=23, minutes=59, seconds=59, milliseconds=59)
        endday += daydelta
        promo_list = IntroducedBy.objects.filter(channel__code=channel_code, created_at__gte=startday, created_at__lte=endday)
        # logger.debug("promo user:%s"%[promo_user.user for promo_user in promo_list])
        return promo_list

    def check_sign(self, channel_code, startday, endday, sign):
        m = hashlib.md5()
        key = getattr(settings, 'WLB_FOR_%s_KEY'%channel_code.upper())
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

    def get_all_user_info_for_coop(self, channel_code, user_type, start_day, end_day, sign):
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

        user_info = []
        for coop_user in coop_users:
            try:
                user_info.append(self.get_user_info_for_coop(user_type, coop_user.user_id, coop_user.created_at))
            except Exception, e:
                logger.exception(e)
                logging.debug('get user %s error:%s'%(coop_user.user_id, e))

        return user_info

    def get(self, request, channel_code, user_type, start_day, end_day, sign):
        try:
            result = {
                'errorcode': 0,
                'errormsg': 'sucess',
                'info': self.get_all_user_info_for_coop(channel_code, int(user_type), start_day, end_day, sign)
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
        if product_id_or_instance.activity:
            return product_id_or_instance.activity.rule_amount + product_id_or_instance.expected_earning_rate
        else:
            return product_id_or_instance.expected_earning_rate

def get_amortization_time(product_id_or_instance):
    """
    获取还款起始，结束时间
    :param product_id_or_instance:
    :return: datetime
    """
    if isinstance(product_id_or_instance, P2PProduct):
        amortizations =  ProductAmortization.objects.filter(product_id = product_id_or_instance.id).order_by('term_date')
        return amortizations.first().term_date, amortizations.last().term_date

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
    #希财现在的过期时间在一个月左右
    url = settings.XICAI_TOKEN_URL
    client_id = settings.XICAI_CLIENT_ID
    client_secret = settings.XICAI_CLIENT_SECRET
    response = requests.post(url, data ={'client_id':client_id, 'client_secret': client_secret})
    return response.json()['access_token']


def xicai_get_p2p_info(mproduct, access_token):
    """
    将我们的p2p信息转换后提供给西财网
    :param mproduct:
    :return:
    """
    p2p_info = get_p2p_info(mproduct)

    #希财状态码：-1：已流标，0：筹款中，1.已满标，2.已开始还款，3.预发布，4.还款完成，5.逾期
    #录标，录标完成，待审核的标均不推送给希财
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

    #希财还款方式码：1.按月付息 到期还本 2.按季付息 到期还本 3.每月等额本息 4.到期本息
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
        'borrow_type': 4, #都是第三方担保
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
    now = datetime.datetime.now()
    start_time = now - settings.XICAI_UPDATE_TIMEDELTA
    return P2PProduct.objects.filter(publish_time__gte = start_time).filter(publish_time__lt = now).all()


def xicai_get_updated_p2p():
    """
    获取有更新的标给希财
    :return:
    """
    start_time = datetime.datetime.now() - settings.XICAI_UPDATE_TIMEDELTA
    p2p_equity = P2PEquity.objects.filter(created_at__gte = start_time).all()
    return set([p.product for p in p2p_equity])

def xicai_send_data():
    """
    向西财网 post最新的标的信息
    :return:
    """
    access_token = xicai_get_token()
    #更新新标数据
    for p2p_product in xicai_get_new_p2p():
        xicai_post_product_info(p2p_product, access_token)
    #更新有变动的标的的数据
    for p2p_product in xicai_get_updated_p2p():
        xicai_post_updated_product_info(p2p_product,access_token)


if __name__ == '__main__':
    print xicai_get_updated_p2p()
    print xicai_get_new_p2p()
    xicai_send_data()






























