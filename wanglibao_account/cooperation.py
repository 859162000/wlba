#!/usr/bin/env python
# encoding:utf-8
import hashlib
import datetime
import logging
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import renderers
from rest_framework.views import APIView
from marketing.models import Channels, IntroducedBy, PromotionToken
from marketing.utils import set_promo_user
from wanglibao import settings
from wanglibao.settings import  YIRUITE_CALL_BACK_URL, \
        TIANMANG_CALL_BACK_URL, WLB_FOR_YIRUITE_KEY, YIRUITE_KEY, BENGBENG_KEY, \
    WLB_FOR_BENGBENG_KEY, BENGBENG_CALL_BACK_URL, BENGBENG_COOP_ID, JUXIANGYOU_COOP_ID, JUXIANGYOU_KEY, \
    JUXIANGYOU_CALL_BACK_URL, TINMANG_KEY
from wanglibao_account.models import Binding, IdVerification
from wanglibao_account.tasks import  yiruite_callback,  common_callback
from wanglibao_p2p.models import P2PEquity, P2PRecord
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
    user_name = WanglibaoUserProfile.objects.get(user_id=int(user_id)).name
    return u'*' + user_name[1:]

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
        self.external_channel_user_key = None
        self.internal_channel_user_key = 'channel_user'
        #渠道提供给我们的秘钥
        self.coop_key = None
        #我们提供给渠道的秘钥
        self.key = None
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
            logger.debug('save user %s to binding'%user)
        else:
            logger.debug('failed to save user %s to binding'%user)

    def call_back(self, user):
        pass

    def process_for_register(self, user, invite_code):
        """
        用户可以在从渠道跳转后的注册页使用邀请码，优先考虑邀请码
        """
        self.save_to_introduceby(user, invite_code)
        self.save_to_binding(user)
        self.call_back(user)
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
        logger.debug('get invite code %s'%(invite_code))
        if invite_code:
            #通过渠道注册
            for processor in self.processors:
                if processor.c_code == processor.channel_code:
                    processor.process_for_register(user, invite_code)
                    return
            #默认注册
            self.process_for_register(user, invite_code)

class TianMangRegister(CoopRegister):
    def __init__(self, request):
        super(TianMangRegister, self).__init__(request)
        self.c_code = 'tianmang'
        self.external_channel_key = 'source'
        self.external_channel_user_key = 'sn'
        self.coop_key = TINMANG_KEY
        self.call_back_url = TIANMANG_CALL_BACK_URL

    @property
    def tianmang_sn(self):
        tianmang_sn = self.request.session.get('tianmang_sn', None)
        if tianmang_sn:
            return tianmang_sn

    def save_to_session(self):
        super(TianMangRegister, self).save_to_session()
        tianmang_sn = self.request.GET.get('tianmang_sn', None)
        if tianmang_sn:
            self.request.session['tianmang_sn'] = tianmang_sn

    def clear_session(self):
        super(TianMangRegister, self).clear_session()
        self.request.session.pop('tianmang_sn', None)

    def call_back(self, user):
        params={
            "oid": self.coop_key,
            "sn" : self.tianmang_sn,
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
        self.external_channel_key = 'from'
        self.external_channel_user_key = 'tid'
        self.coop_key = YIRUITE_KEY
        self.key = WLB_FOR_YIRUITE_KEY
        self.call_back_url = YIRUITE_CALL_BACK_URL

    def call_back(self, user):
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
        self.external_channel_user_key = 'bengbeng_id'
        self.coop_id = BENGBENG_COOP_ID
        self.coop_key = BENGBENG_KEY
        self.key = WLB_FOR_BENGBENG_KEY
        self.call_back_url = BENGBENG_CALL_BACK_URL

    def call_back(self, user):
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
        self.external_channel_user_key = 'jxy_id'
        self.coop_id = JUXIANGYOU_COOP_ID
        self.coop_key = JUXIANGYOU_KEY
        self.call_back_url = JUXIANGYOU_CALL_BACK_URL

    def call_back(self, user):
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


#注册第三方通道
coop_processor_classes = [TianMangRegister, YiRuiTeRegister, BengbengRegister]

#######################第三方用户查询#####################

class CoopQuery(APIView):
    """
    第三方用户查询api
    """
    channel = None
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
        logger.debug("promo user:%s"%[promo_user.user for promo_user in promo_list])
        return promo_list

    def check_sign(self, startday, endday, sign):
        if self.channel:
            m = hashlib.md5()
            key = getattr(settings, 'WLB_FOR_%s_KEY'%self.channel.upper())
            m.update(startday+endday+key)
            local_sign = m.hexdigest()
            if sign != local_sign:
                logger.debug('正确的渠道校验参数%s'%local_sign)
                logger.error(u"渠道查询接口，sign参数校验失败")
                return False
            return True

class TianmangQuery(CoopQuery):
    """
    根据天芒要求的格式返回信息
    """
    channel = 'tianmang'

    def get_phone_for_tianmang(self, user_id):
        phone_number = WanglibaoUserProfile.objects.get(user_id=user_id).phone
        return phone_number[:3] + '***' + phone_number[-2:]

class TianmangIDVerificationQuery(TianmangQuery):
    """天芒云 获取完成身份证认证用户"""
    permission_classes = ()
    def get(self, request, startday, endday):
        response_user_list = []
        try :
            tianmang_promo_list = self.get_promo_user(self.channel, startday, endday)
            for tianmang_promo_user in tianmang_promo_list:
                try:
                    if tianmang_promo_user.user.wanglibaouserprofile.id_is_valid:
                        #获取身份认证的时间
                        created_at = IdVerification.objects.get(\
                            id_number=tianmang_promo_user.user.wanglibaouserprofile.id_number).created_at

                        response_user ={
                            "time": timezone.localtime(created_at).strftime("%Y-%m-%d %H:%M:%S"),
                            "uid": get_uid_for_coop(tianmang_promo_user.user_id),
                            "uname": get_username_for_coop(tianmang_promo_user.user_id),
                            "phone": self.get_phone_for_tianmang(tianmang_promo_user.user_id),
                            #"status":tianmang_promo_user.user.wanglibaouserprofile.id_is_valid and 1 or 0,
                        }
                        response_user_list.append(response_user)
                except:
                    pass
        except:
            logger.error("TianmangIDVerificationListAPIView error")

        return HttpResponse(renderers.JSONRenderer().render(response_user_list, 'application/json'))


class TianmangRegisterQuery(TianmangQuery):
    """天芒云 获取注册完成用户"""
    permission_classes = ()
    def get(self, request, startday, endday):
        response_user_list = []
        try :
            tianmang_promo_list = self.get_promo_user(self.channel, startday, endday)
            for tianmang_promo_user in tianmang_promo_list:
                try:
                    response_user ={
                        "time": timezone.localtime(tianmang_promo_user.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                        "uid": get_uid_for_coop(tianmang_promo_user.user_id),
                        "uname": get_username_for_coop(tianmang_promo_user.user_id),
                        #"status":tianmang_promo_user.user.wanglibaouserprofile.phone_verified and 1 or 0,
                    }
                    response_user_list.append(response_user)
                except Exception, e:
                    logger.debug('%s'%e)
        except:
            logger.error("TianmangRegisterListAPIView error")

        return HttpResponse(renderers.JSONRenderer().render(response_user_list, 'application/json'))

class TianmangInvestQuery(TianmangQuery):
    """天芒云 投资成功及金额获取用户接口"""
    permission_classes = ()
    def get(self, request, startday, endday):
        response_user_list = []
        try :
            tianmang_promo_list = self.get_promo_user(self.channel, startday, endday)

            for tianmang_promo_user in tianmang_promo_list:
                try:
                    p2p_equities = P2PEquity.objects.filter(user=tianmang_promo_user.user).filter(product__status__in=[
                        u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
                        ])
                    income_all = 0
                    for equity in p2p_equities:
                        if equity.confirm:
                            income_all += equity.equity

                    if not income_all:
                        continue
                    response_user ={
                        "time": timezone.localtime(tianmang_promo_user.bought_at).strftime("%Y-%m-%d %H:%M:%S"),
                        "uid": get_uid_for_coop(tianmang_promo_user.user_id),
                        "uname": get_username_for_coop(tianmang_promo_user.user_id),
                        "investment": float(income_all),
                        #"status": 1 if income_all > 0 else 0
                    }
                    response_user_list.append(response_user)
                except:
                    pass
        except:
            logger.error("TianmangInvestListAPIView error")

        return HttpResponse(renderers.JSONRenderer().render(response_user_list, 'application/json'))

class TianmangInvestNotConfirmQuery(TianmangQuery):
    """天芒云 投资成功及金额获取用户接口"""
    permission_classes = ()
    def get(self, request, startday, endday):

        response_user_list = []
        try:
            tianmang_promo_list = self.get_promo_user(self.channel, startday, endday)

            for tianmang_promo_user in tianmang_promo_list:
                try:
                    total_equity = P2PEquity.objects.filter(user=tianmang_promo_user.user).filter(product__status__in=[
                        u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
                    ]).aggregate(total_equity=Sum('equity')).get('total_equity', 0)

                    if not total_equity:
                        continue
                    response_user ={
                        "time": timezone.localtime(tianmang_promo_user.bought_at).strftime("%Y-%m-%d %H:%M:%S"),
                        "uid": get_uid_for_coop(tianmang_promo_user.user_id),
                        "uname": get_username_for_coop(tianmang_promo_user.user_id),
                        "investment": float(total_equity),
                        #"status": 1 if income_all > 0 else 0
                    }
                    response_user_list.append(response_user)
                except:
                    pass
        except Exception, e:
            logger.error("TianmangInvestListNotConfirmAPIView error")
            logger.error(e)

        return HttpResponse(renderers.JSONRenderer().render(response_user_list, 'application/json'))

class TianmangCardBindQuery(TianmangQuery):
    """天芒云 批量查询通过天芒云渠道完成注册并成功绑定银行卡的用户列表接口"""
    permission_classes = ()
    def get(self, request, startday, endday):
        response_user_list = []
        try:
            tianmang_promo_list = self.get_promo_user(self.channel, startday, endday)
            for tianmang_promo_user in tianmang_promo_list:
                try:
                    add_at_list = Card.objects.filter(user=tianmang_promo_user.user).order_by('add_at')
                    if add_at_list.exists():
                        add_at = add_at_list[0].add_at
                        response_user = {
                            "time": timezone.localtime(add_at).strftime("%Y-%m-%d %H:%M:%S"),
                            "uid": get_uid_for_coop(tianmang_promo_user.user_id),
                            "uname": get_username_for_coop(tianmang_promo_user.user_id),
                        }
                        response_user_list.append(response_user)
                except:
                    pass
        except:
            logger.error("TianmangCardBindListAPIView error")

        return HttpResponse(renderers.JSONRenderer().render(response_user_list, 'application/json'))


class YiruiteQuery(CoopQuery):
    permission_classes = ()
    channel = 'yiruite'



    def get(self, request, startday, endday, sign):
        if not self.check_sign(startday, endday, sign):
            return HttpResponse(renderers.JSONRenderer().render(
                {"errorcode": 2, "errormsg": "sign error"}, 'application/json'))

        response_user_list = []
        try:
            yiruite_promo_list = self.get_promo_user(self.channel, startday, endday)
            for yiruite_promo_user in yiruite_promo_list:
                try:
                    # 易瑞特用户是否实名认证
                    is_valid = IdVerification.objects.get(\
                        id_number=yiruite_promo_user.user.wanglibaouserprofile.id_number).is_valid

                    # 易瑞特用户标识
                    tid_list = Binding.objects.filter(user=yiruite_promo_user.user)
                    tid = tid_list.first().bid
                except:
                    logger.debug('failed to get idverification or binding for user %s' %yiruite_promo_user.user)
                    continue

                try:
                    # 用户首次投资
                    p2p_record = P2PRecord.objects.filter(user=yiruite_promo_user.user, catalog=u'申购').order_by('create_time')
                    amount = p2p_record[0].amount
                    first_invest_time = timezone.localtime(p2p_record[0].create_time).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    amount = 0
                    first_invest_time = '0000-00-00 00:00:00'

                response_user = {
                    "UserName": yiruite_promo_user.user.username,
                    "RegisterTime": timezone.localtime(
                        yiruite_promo_user.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                    "IsValidateIdentity": is_valid,
                    "tid": tid,
                    "amount": amount,
                    "FirstInvestTime": first_invest_time,
                }
                response_user_list.append(response_user)
            result = {
                "errorcode": 0,
                "errormsg": "success",
                "info": response_user_list
            }
        except Exception, e:
            logger.error("YiruiteInfoListAPIView error")
            logger.error(e)
            result = {
                "errorcode": 1,
                "errormsg": "api error"
            }
        return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

class BengbengQuery(CoopQuery):
    permission_classes = ()
    channel = 'bengbeng'

    def get(self, request, startday, endday, sign):
        """
        返回所有注册用户
        """
        if not self.check_sign(startday, endday, sign):
            return HttpResponse(renderers.JSONRenderer().render(
                {"errorcode": 2, "errormsg": "sign error"}, 'application/json'))

        response_user_list = []
        try:
            yiruite_promo_list = self.get_promo_user(self.channel, startday, endday)
            for yiruite_promo_user in yiruite_promo_list:
                response_user = {
                    "UserName": yiruite_promo_user.user.username,
                    "RegisterTime": timezone.localtime(
                        yiruite_promo_user.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                }
                response_user_list.append(response_user)
            result = {
                "errorcode": 0,
                "errormsg": "success",
                "info": response_user_list
            }
        except Exception, e:
            logger.error("Bengbeng query error")
            logger.error(e)
            result = {
                "errorcode": 1,
                "errormsg": "api error"
            }
        return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

