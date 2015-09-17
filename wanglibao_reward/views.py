#-*- coding: utf-8 -*-
#########################################################################
# Author: Yihen Liu
# Created Time: 2015-09-09 13:23:07
# File Name: reward.py
# Description: 策划活动中的红包、奖品、加息券等用户奖励行为，独立在这个文件中
#########################################################################
from django.utils import timezone
from django.http.response import HttpResponse
from django.db.models import Count, Q
from datetime import datetime
from wanglibao_redpack.models import RedPackEvent
from wanglibao_redpack import backends as redpack_backends
import inspect
import time
import json
import logging
from wanglibao_account import message as inside_message
from marketing.models import IntroducedBy, Reward
from wanglibao_reward.models import WanglibaoActivityGift, WanglibaoUserGift, WanglibaoActivityGiftGlobalCfg
from wanglibao_redpack.models import RedPackEvent
from wanglibao_activity.models import Activity, ActivityRule
from wanglibao_p2p.models import P2PRecord
from django.views.generic import View
from django.http import HttpResponse, Http404

logger = logging.getLogger('wanglibao_reward')

def ajax_response_reward(request):
    activity = request.POST.get("activity", "")
    action = request.POST.get("action", "")
    util = WanglibaoReward(request, activity)
    if action == "IS_VALID_USER":
        year = request.POST.get("year", 1970)
        month = request.POST.get("month", 1)
        day = request.POST.get("day", 1)
        return util.is_register_in_activity_period(year, month, day)

    if action == 'IS_VALID_CHANNEL':
        return util.is_valid_channel()

    if action == 'ENTER_WEB_PAGE':
        pass

    if action == 'GET_REDPACK':
        pass

    if action == 'GET_REWARD':
        pass

class WanglibaoReward(object):

    def __init__(self, request):
        self.request = request
        self.activity = None
        self.global_cfg = None

    def is_register_in_activity_period(self, year=1970, month=1, day=1):
        """
            判断用户是不是在活动期间内注册的新用户
        """
        create_at = int(time.mktime(self.request.user.date_joined.date().timetuple()))  # 用户注册的时间戳
        activity_start = time.mktime(datetime(year, month, day).timetuple())  # 活动开始时间

        if activity_start > create_at:
            to_json_response = {
                'ret_code': 3000,
                'message': u'非活动期注册用户',
            }
        else:
            to_json_response = {
                'ret_code': 3001,
                'message': u'活动期注册用户',
            }
        logger.debug("user_id:%d, check invite_code flow,ret_code:%d, message:%s " %(self.request.user.id, to_json_response["ret_code"], to_json_response["message"]))
        return HttpResponse(json.dumps(to_json_response), content_type='application/json' )

    def is_login(self):
        """
            判断用户是不是已经登录
        """
        if not self.request.user.is_authenticated():
            to_json_response = {
                'ret_code': 4000,
                'message': u'用户没有登陆，请先登陆',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    def is_valid_channel(self):
        """
            优先使用WanglibaoActivityGift的渠道配置
        """
        channels = WanglibaoActivityGift.objects.filter(activity=self.activity).first()
        if not channels:
            channels = Activity.objects.filter(code=self.activity).first()
            if not channels:
                to_json_response = {
                    'ret_code': 3000,
                    'message': u'全渠道',
                }
                return HttpResponse(json.dumps(to_json_response), content_type='application/json' )
            else:
                channels = channels.channel.split(",")
        else:
            channels = channels.channel.split(",")

        record = IntroducedBy.objects.filter(user_id=self.request.user.id).first()

        if not record:
            to_json_response = {
                'ret_code': 3001,
                'message': u'非渠道用户',
            }
        else:
            if record.channel.name not in channels:
                to_json_response = {
                    'ret_code': 3002,
                    'message': u'渠道用户不是从对应的渠道过来',
                }
            else:
                to_json_response = {
                    'ret_code': 3003,
                    'message': u'渠道用户从对应的渠道过来',
                }

        logger.debug("user_id:%d, check invite_code flow,ret_code:%d, message:%s " %(self.request.user.id, to_json_response["ret_code"], to_json_response["message"]))
        return HttpResponse(json.dumps(to_json_response), content_type='application/json' )

    def get_activity_rewards(self):
        """
            获得奖品的种类
        """
        rewards = WanglibaoActivityGift.objects.filter(activity=self.activity).values("name", "code", "count")
        return rewards

    def get_total_rewards(self, name):
        """
            获得单个奖品在gift表中总共有多少（包括待发和已发）
        """
        record = WanglibaoUserGift.objects.filter(Q(valid=0)|Q(valid=1), activity=self.activity, name=name).aggregate(counts=Count("id"))
        return record["counts"] if record else 0

    def get_reward_max_index(self, name):
        """
            获得奖品最大下标（包括待发和已发和无效）
        """
        record = WanglibaoUserGift.objects.filter(activity=self.activity).aggregate(counts=Count("id"))
        return record["counts"] if record else 0

    def get_used_rewards(self, name):
        """
            获得单个奖品已发多少
        """
        record = WanglibaoUserGift.objects.filter(activity__code__extra=self.activity, name=name, valid=0).aggregate(counts=Count("id"))
        return record["counts"] if record else 0

    def has_distributed_reward(self):
        """
            判断是否已经给用户在gift表中生成奖品
        """
        record = WanglibaoUserGift.objects.filter(user=self.request.user, activity=self.activity).aggregate(counts=Count('id'))

        return record['counts'] if record else 0

    def gift_is_valid(self, index, rate):
        if index % ((100/rate)-1) == 0:
            return True

        return False

    def distribute_one_reward(self, name, counts):
        gift = WanglibaoUserGift.objects.create(
            user=self.request.user,
            rules=WanglibaoActivityGift.objects.filter(activity=self.activity, name=reward["name"]),
            activity=self.activity,
            index=self.get_reward_max_index()+1,
            name=name,
            valid=3,
        )
        has_send = self.get_used_rewards(name)
        if has_send < counts:
            if gift.rules.rate == 0:  # 0表示任意
                gift.valid = 0
                gift.save()
                return

            if self.gift_is_valid(gift.index, gift.rules.rate):
                gift.valid = 0
                gift.save()
            else:
                gift.valid = 1
                gift.save()
                #获得还有多少个奖品，每个奖品还有几个,还有多少次抽奖机会, 并将结果返回


    def distribute_rewards(self):
        """
            给用户预先在gift表中，将奖品生成
        """
        if not self.has_distributed_reward():
            rewards = self.get_activity_rewards()
            for reward in rewards:
                self.distribute_one_reward(reward["name"], reward["count"])

    def send_redpack(self):
        """
            发红包
        """
        try:
            dt = timezone.datetime.now()
            record = WanglibaoActivityGift.objects.filter(type=0, activity=self.activity)
            redpack_event = RedPackEvent.objects.filter(invalid=False, describe=record.code, give_start_at__lte=dt, give_end_at__gte=dt).first()
        except Exception, reason:
            logger.debug("send redpack Exception, msg:%s" % (reason,))
        else:
            gift = WanglibaoUserGift.objects.filter(type=0, rules=record, valid=0).first()
            gift.valid = 1
            gift.save()
        if redpack_event:
            redpack_backends.give_activity_redpack(self.request.user, redpack_event, 'pc')
        pass

    def send_reward(self):
        """
            发加息券,代金券等
        """
        gift_name = "None"
        now = timezone.now()
        reward = Reward.objects.filter(type=gift_name,
                                       is_used=False,
                                       end_time__gte=now).first()

        inside_message.send_one.apply_async(kwargs={
            "user_id": self.request.user.id,
            "title": reward.description,
            "content": reward.content,
            "mtype": "activity"
        })
        pass
    def ignore_request(self):
        """
            处理用户的不获奖行为
        """
        pass

class WeixinShareView(View):

    def __init__(self):
        self.activity = None
        self.global_cfg = None

    @property
    def current_function_name(self):
        return inspect.stack()[1][3]

    def exception_msg(self, reason, msg=u'None'):
        logger.exception("class:%s, function:%s, reason,%s, msg:%s" %(self.__class__.__name__, self.current_function_name, reason, msg))

    def error_msg(self, msg=u'None'):
        logger.error("class:%s, function:%s, msg:%s" %(self.__class__.__name__, self.current_function_name, msg))

    def debug_msg(self, msg=u'None'):
        logger.debug("class:%s, function:%s,  msg:%s" %(self.__class__.__name__, self.current_function_name, msg))

    def has_combine_redpack(self, product_id, activity):
        """
            判断是否已经生成了此次活动的组合红包
        """
        if not self.activity:
           self.get_activity_by_id(activity)
        try:
            combine_redpack = WanglibaoActivityGift.objects.filter(gift_id=product_id, activity=self.activity)
        except Exception, reason:
            self.exception_msg(reason, u'判断组合红包生成报异常')
        return True if combine_redpack else False

    def get_activity_by_id(self, activity_id):
        try:
            self.activity = Activity.objects.filter(code=activity_id).first()
        except Exception, reason:
            self.exception_msg(reason)


    def get_redpack_id(self, activity):
        """
            根据活动管理配置，获得对应的红包配置信息
        """
        self.get_activity_by_id(activity)
        if self.activity:
            if self.activity.is_stopped:
                self.debug_msg(u'活动已经暂停了')
                return None
            try:
                activity_rules = ActivityRule.objects.filter(activity=self.activity)
            except Exception, reason:
                self.exception_msg(reason, u'获取活动规则失败')
                return None

            try:
                return [rule.redpack for rule in activity_rules]
            except Exception, reason:
                self.exception_msg(reason, u'获取红包编号失败')
                return None
        else:
            return None

    def get_redpack_by_id(self, ids):
        """
            根据传入的id集合（list），获得红包的信息
        """
        if type(ids) is not list:
            return None
        try:
            return RedPackEvent.objects.filter(id__in=ids)
        except Exception, reason:
            self.exception_msg(reason, u'获得配置的红包失败')
            return None

    def generate_combine_redpack(self, product_id, activity):
        """
            生成此次活动的组合红包
        """
        redpack_type = {
        "direct": 0,
        "interest_coupon": 1,
        "percent": 2}
        if not self.global_cfg:
            if not self.get_global_cfg(activity):
                self.debug_msg(u'对应的全局红包活动配置没有配，请先配置')
                return None

        if not self.has_combine_redpack(product_id, activity):
            ids = self.get_redpack_id(activity)
            if ids:
                redpacks = self.get_redpack_by_id(ids)
            else:
                self.debug_msg(u"生成组合红包时错误")
                return None
            for redpack in redpacks:
                try:
                    activity_gift = WanglibaoActivityGift.objects.create(
                    cfg=self.global_cfg,
                    gift_id=product_id,
                    activity=self.activity,
                    redpack=redpack,
                    name=redpack.rtype,
                    total_count=redpack.value,  #这个地方很关键,优惠券个数
                    )
                    activity_gift.type = redpack_type[redpack.rtype]
                    activity_gift.save()
                except Exception, reason:
                    self.exception_msg(reason, '组合红包入库报错')

    def has_got_redpack(self, phone_num, openid, activity, product_id):
        """
            判断用户是否已经领完奖品了
        """
        if not self.activity:
            self.activity = self.get_activity_by_id(activity)
        try:
            user_gift = WanglibaoUserGift.objects.filter(rules__gift_id__exact=product_id, identity__in=(str(phone_num),str(openid)), activity=self.activity)
            return user_gift
        except Exception, reason:
            self.exception_msg(reason, u'判断用户领奖，数据库查询出错')
            return None

    def distribute_redpack(self, phone_num, openid, activity, product_id):
        """
            根据概率，分发奖品
        """
        pass

    def get_distribute_status(self, product_id):
        """
            获得用户领奖信息
        """
        try:
            gifts = WanglibaoUserGift.objects.filter(rules__gift_id__exact=product_id, activity=self.activity)
            return gifts
        except Exception, reason:
            self.exception_msg(reason, u'获取已领奖用户信息失败')
            return None

    def get_global_cfg(self, activity):
        """
            获得活动红包的全局配置信息
        """
        if not self.activity:
            self.get_activity_by_id(activity)

        try:
            self.global_cfg = WanglibaoActivityGiftGlobalCfg.objects.filter(activity=self.activity).get()
            return self.global_cfg
        except Exception, reason:
            self.exception_msg(reason, u'获取全局配置抛出异常')
            return None

    def is_valid_user_auth(self, product_id, activity):
        if not self.activity:
            self.get_activity_by_id(activity)

        if not self.global_cfg:
            self.get_global_cfg(activity)

        try:
            p2p_record = P2PRecord.objects.filter(order_id=product_id, amount__gte=self.global_cfg.amount)
            return p2p_record
        except Exception, reason:
            self.exception_msg(reason, u"判断用户投资额度抛异常")
            return None

    def get(self, request, **args):
        openid = args["openid"]
        phone_num = args["phone_num"]
        product_id = args["product_id"]
        activity = args["activity"]
        """if not self.is_valid_user_auth(product_id, activity):
            to_json_response = {
                'ret_code': 9000,
                'message': u'用户投资没有达到%s元;' %(self.global_cfg.amount),
            }
            self.debug_msg(to_json_response["message"])
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')
        """
        # 判断是否已经生成了组合红包,并生成组合红包
        if not self.has_combine_redpack(product_id, activity):
            self.generate_combine_redpack(product_id, activity)

        # 判断用户是否已经领取了红包
        if not self.has_got_redpack(phone_num, openid, activity, product_id):
            self.distribute_redpack(phone_num, openid, activity, product_id)
    #判断用户是否达到分享的标准，投资满1000
    #调用梅梅的接口，判断是否已经获取了用户的openid等信息
    # （1类红包看成是组合红包的特例）,
    # 分发用户红包
    # 获得组合红包的分发情况，返回给前端
        return HttpResponse(activity)
# vim: set noexpandtab ts=4 sts=4 sw=4 :

